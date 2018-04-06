var markers = [];
var filters = {
    organizations: {
        key: 'organization',
        label: 'Organizations',
        icon: 'business',   // From https://material.io/icons/
        values: {},
        values_sortable: []
    },
    siteTypes: {
        key: 'type',
        icon: 'layers',
        label: 'Site Types',
        values: {},
        values_sortable: []
    }
};

function initMap() {
    const DEFAULT_ZOOM = 5;
    const DEFAULT_SPECIFIC_ZOOM = 12;
    const DEFAULT_LATITUDE = 40.0902;
    const DEFAULT_LONGITUDE = -95.7129;
    const DEFAULT_POSITION = { lat: DEFAULT_LATITUDE, lng: DEFAULT_LONGITUDE };
    var ZOOM_LEVEL = sessionStorage && parseInt(sessionStorage.getItem('CURRENT_ZOOM')) || DEFAULT_ZOOM;
    var temp = sessionStorage.getItem('CURRENT_CENTER');
    var MAP_CENTER = DEFAULT_POSITION;

    if(sessionStorage.getItem('CURRENT_CENTER')) {
        MAP_CENTER = getLatLngFromString(temp);
    } else if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function getLocation(locatedPosition) {
            map.setCenter({ lat: locatedPosition.coords.latitude, lng: locatedPosition.coords.longitude });
            map.setZoom(DEFAULT_SPECIFIC_ZOOM);
        }, undefined, { timeout: 5000 });
    }

    var markerData = JSON.parse(document.getElementById('sites-data').innerHTML);

    var map = new google.maps.Map(document.getElementById('map'), {
        center: MAP_CENTER,
        zoom: ZOOM_LEVEL,
        gestureHandling: 'greedy',
        zoomControl: true,
        zoomControlOptions: {
            position: google.maps.ControlPosition.LEFT_BOTTOM
        },
        mapTypeId: google.maps.MapTypeId.HYBRID,
        scaleControl: true
    });

    var infoWindow = new google.maps.InfoWindow({
        content: ''
    });

    map.addListener('zoom_changed', function(){
        var CURRENT_ZOOM = map.getZoom();
        sessionStorage.setItem('CURRENT_ZOOM', CURRENT_ZOOM);
    });

    map.addListener('center_changed', function(){
        var CURRENT_CENTER = map.getCenter();
        sessionStorage.setItem('CURRENT_CENTER', CURRENT_CENTER);
    });

    markerData.forEach(function(site) {
        var marker = new google.maps.Marker({
            position: { lat: site.latitude, lng: site.longitude },
            map: map,
        });

        for (var f in filters) {
            marker[filters[f].key] = site[filters[f].key];
        }

        marker.addListener('click', function() {
            var contentElement = $('<div></div>').append($('#site-marker-content').html());
            var fields = contentElement.find('.site-field');
            fields.each(function(index, element) {
                var field = $(element).data('field');
                $(element).find('.site-data').text(site[field]);
            });
            contentElement.find('.site-link a').attr('href', site.detail_link);

            var infoContent = $('<div></div>').append(contentElement.html()).html();
            infoWindow.setContent(infoContent);
            infoWindow.open(marker.get('map'), marker);
        });

        markers.push(marker);
    });
}

$(document).ready(function () {
    $('nav .menu-browse-sites').addClass('active');
    resizeContent();

    var markerData = JSON.parse(document.getElementById('sites-data').innerHTML);

    markerData.forEach(function (site) {
        for (var f in filters) {
            if (filters[f].values[site[filters[f].key]])
                filters[f].values[site[filters[f].key]] += 1;
            else
                filters[f].values[site[filters[f].key]] = 1;
        }
    });

    // Move the items to an array so we can sort them
    for (var f in filters) {
        for (var val in filters[f].values) {
            filters[f].values_sortable.push([val, filters[f].values[val]]);
        }
    }

    // Sort the arrays
    for (var f in filters) {
        filters[f].values_sortable.sort(function (a, b) {
            return b[1] - a[1];
        });
    }

    // Append filter headers
    for (var f in filters) {
        $("#filters").append('<div class="filter-header">\
                    <table class="mdl-data-table mdl-js-data-table mdl-data-table--selectable mdl-shadow--2dp full-width">\
                        <tr>\
                            <td class="mdl-data-table__cell--non-numeric">\
                                <a data-toggle="collapse" href="#collapse-' + filters[f].key + '" role="button" aria-expanded="true"\
                                   aria-controls="collapse-' + f.key + '" style="text-decoration: none; color: #222;">\
                                    <h6><i class="material-icons mdl-shadow--2dp">' + filters[f].icon + '</i> ' + filters[f].label + '<i class="material-icons pull-right">keyboard_arrow_down</i></h6>\
                                </a>\
                            </td>\
                        </tr>\
                    </table>\
                </div>\
                <div id="collapse-' + filters[f].key + '" class="show filter-body" data-facet="' + filters[f].key + '">\
                    <table class="mdl-data-table mdl-js-data-table mdl-data-table--selectable mdl-shadow--2dp full-width">\
                        <tbody>\
                            <tr class="td-filter">\
                                <td class="mdl-data-table__cell--non-numeric">\
                                    <div class="input-group">\
                                        <span class="input-group-addon" id="basic-addon1"><i class="material-icons">search</i></span>\
                                        <input type="text" class="form-control input-filter" placeholder="Search ' + filters[f].label + '...">\
                                    </div>\
                                </td>\
                            </tr>\
                        </tbody>\
                    </table>\
                </div>'
        );

        // Append filter items
        for (var item = 0; item < filters[f].values_sortable.length; item++) {
            $("#collapse-" + filters[f].key + " > table tbody").append(' <tr>\
                <td class="mdl-data-table__cell--non-numeric">\
                    <label class="mdl-checkbox mdl-js-checkbox mdl-js-ripple-effect" for="chk-' + filters[f].key + '-' + filters[f].values_sortable[item][0] + '">\
                        <input type="checkbox" id="chk-' + filters[f].key + '-' + filters[f].values_sortable[item][0] + '" \
                        class="mdl-checkbox__input chk-filter" data-value="'+ filters[f].values_sortable[item][0] + '">\
                        <span class="mdl-checkbox__label">' + filters[f].values_sortable[item][0] + '</span>\
                    </label>\
                    <span class="badge badge-info">' + filters[f].values_sortable[item][1] + '</span>\
                </td>\
            </tr>');
        }
    }

    // Bind search events
    $(".input-filter").keyup(function() {
        var items = $(this).closest("tbody").find("tr:not(.td-filter)");
        var searchStr = $(this).val().trim().toUpperCase();

        if (searchStr.length > 0) {
            items.hide();

            var results = items.filter(function () {
                return $(this).find('label').text().trim().toUpperCase().indexOf(searchStr) >= 0;
            });

            results.show();
        }
        else {
            items.show();
        }
    });

    $("#btnClearFilters").click(function() {
        // document.querySelector('.chk-filter').parentElement.MaterialCheckbox.uncheck();
        var items = $(".chk-filter");
        for (var i = 0; i < items.length; i++) {
            $(items[i]).parent()[0].MaterialCheckbox.uncheck();
        }
        for (var i = 0; i < markers.length; i++) {
            markers[i].setVisible(true);
        }
    });

    $(".chk-filter").change(onFilterChange);
});

function onFilterChange() {
    var checkedItems = getCurrentFilters();
    // If nothing selected, display all
    if (!checkedItems.length) {
        for (var i = 0; i < markers.length; i++) {
            markers[i].setVisible(true);
        }
    }
    else {
        for (var i = 0; i < markers.length; i++) {
            var visible = false;    // Starts as false by default
            for (var j = 0; j < checkedItems.length; j++) {
                if (checkedItems[j][1].indexOf(markers[i][checkedItems[j][0]]) >= 0) {
                    visible = true; // Display if included in some filter
                    continue;
                }
            }
            markers[i].setVisible(visible);
        }
    }
}

// Returns an object listing currently checked filter items
function getCurrentFilters() {
    var filters = $(".filter-body");
    var results = [];

    for (var i = 0; i < filters.length; i++) {
        var items = [];
        var checked = $(filters[i]).find(".chk-filter:checked");

        for (var j = 0; j < checked.length; j++) {
            items.push($(checked[j]).attr("data-value"));
        }

        if (items && items.length > 0) {
            var facet = $(filters[i]).attr("data-facet");
            results.push([facet, items]);
        }
    }

    return results;
}

$(window).resize(resizeContent);

function resizeContent() {
    $("#wrapper").css("height", "calc(100% - 81px)");
    $(".map-container").css("height", $("#wrapper").height() - $("#title-row").height());
    $("#filters-row").css("height", $("#wrapper").height() - $("#title-row").height());
}

function getLatLngFromString(location) {
    var latlang = location.replace(/[()]/g,'');
    var latlng = latlang.split(',');
    var locate = new google.maps.LatLng(parseFloat(latlng[0]) , parseFloat(latlng[1]));
    return locate;
}