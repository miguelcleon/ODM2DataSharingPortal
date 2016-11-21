// (function() {
//     'use strict';
//
// }());

function updateSitePosition(map, position) {
    map.panTo(position);
    $('input[name="latitude"]').val(Math.round(position.lat() * 100000) / 100000);
    $('input[name="longitude"]').val(Math.round(position.lng() * 100000) / 100000);
}

function updateSiteElevation(position) {
    var elevator = new google.maps.ElevationService();
     elevator.getElevationForLocations({'locations':[position]}, function(results, status) {
          if (status == google.maps.ElevationStatus.OK && results[0]) {
              $('input[name="elevation_m"]').val(Math.round(results[0].elevation));
          }
     });
}

function initMap() {
    const DEFAULT_ZOOM = 4;
    const DEFAULT_SPECIFIC_ZOOM = 10;
    const DEFAULT_LATITUDE = 37.0902;
    const DEFAULT_LONGITUDE = -95.7129;
    var mapTip = $('<div class="map-info"><span class="map-tip">Click on the map to update coordinates and elevation data</span></div>');
    var mapPosition = { lat: parseFloat($('input[name="latitude"]').val()), lng: parseFloat($('input[name="longitude"]').val()) };
    var isCompletePosition = mapPosition.lat && mapPosition.lng;
    var mapZoom = parseInt($('input[name="zoom-level"]').val());

    var map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: mapPosition.lat || DEFAULT_LATITUDE, lng: mapPosition.lng || DEFAULT_LONGITUDE },
        zoom: mapZoom || DEFAULT_ZOOM,
        mapTypeId: google.maps.MapTypeId.TERRAIN,
        draggableCursor: 'pointer',
        disableDefaultUI: true,
        zoomControl: true,
        zoomControlOptions: {
          position: google.maps.ControlPosition.LEFT_BOTTOM
        },
        scaleControl: true
    });

    var marker = new google.maps.Marker({
        position: (mapPosition.lat && mapPosition.lng)? mapPosition: undefined,
        map: map
    });

    if (navigator.geolocation && !isCompletePosition) {
        navigator.geolocation.getCurrentPosition(function getLocation(locatedPosition) {
            map.setCenter({ lat: locatedPosition.coords.latitude, lng: locatedPosition.coords.longitude });
            map.setZoom(DEFAULT_SPECIFIC_ZOOM);
        }, undefined, { timeout: 5000 });
    }

    map.controls[google.maps.ControlPosition.TOP_CENTER].push(mapTip.get(0));

    map.addListener('click', function(event) {
        marker.setPosition(event.latLng);
        updateSitePosition(map, event.latLng);
        updateSiteElevation(event.latLng);
    });
    
    map.addListener('zoom_changed', function() {
        $('input[name="zoom-level"]').val(map.getZoom());
    });

    $('input[name="latitude"], input[name="longitude"]').on('change', function() {
        var coordinates = {
            lat: parseFloat($('input[name="latitude"]').val()),
            lng: parseFloat($('input[name="longitude"]').val())
        };

        if (!coordinates.lat || !coordinates.lng) {
            return;
        }

        map.panTo(coordinates);
        marker.setPosition(coordinates);
    });
}

function bindDeleteResult(resultForm) {
    resultForm.find('span.remove-result').on('click', function() {
        $(this).parents('.result-form').remove();
    });
}

function initializeSelects(form) {
    form.find('select.form-control').select2({
        theme: "bootstrap",
        containerCssClass : "input-sm",
        dropdownAutoWidth: true,
        width: 'auto'
    });
}

function selectSoloOptions(form) {
    form.find('select').each(function() {
        var select = $(this);
        var options = select.children('[value!=""]');
        if (options.length === 1) {
            select.val(options.get(0).value);
            // select.attr('readonly', true);
        }
    });
}

function addResult() {
    var newIndex = $('div#formset div.result-form').length;
    $('input[name="form-TOTAL_FORMS"]').val(newIndex + 1);

    var newResultForm = $($('div#results-template').html().replace(new RegExp('__prefix__', 'g'), newIndex));
    $('.formset-container').append(newResultForm);

    bindDeleteResult(newResultForm);
    selectSoloOptions(newResultForm);
    initializeSelects(newResultForm);
}

function fillAffiliationFields(data) {
    if (data && data.error) {
        console.log(data.error);
    }

    $('input[name="person_first_name"]').val(data && data.person && data.person.person_first_name || '');
    $('input[name="person_last_name"]').val(data && data.person && data.person.person_last_name || '');
    $('input[name="organization_code"]').val(data && data.organization && data.organization.organization_code || '');
    $('input[name="organization_name"]').val(data && data.organization && data.organization.organization_name || '');
    $('select[name="organization_type"]').val(data && data.organization && data.organization.organization_type || '').trigger('change');
    $('input[name="primary_phone"]').val(data && data.primary_phone || '');
    $('input[name="primary_email"]').val(data && data.primary_email || '');
    $('input[name="affiliation_start_date"]').val(data && data.affiliation_start_date || '');
}

function bindAffiliationChange() {
    var affiliationSelect = $('select[name="affiliation"]');
    var newPersonFields = $('div.new-person-fields input, div.new-person-fields select');
    var newPersonButton = $('button.new-affiliation-button');

    $('<option value="new">Add New Person</option>').insertAfter(affiliationSelect.children().first());

    affiliationSelect.on('change', function() {
        if ($(this).val() == "new") {
            fillAffiliationFields({ person: {
                person_first_name: $('input[name="user_first_name"]').val(),
                person_last_name: $('input[name="user_last_name"]').val()
            }});
            newPersonFields.removeAttr('disabled');
            newPersonButton.show();
            return;
        } else if (!newPersonFields.attr('disabled')) {
            newPersonFields.attr('disabled', true);
            newPersonButton.hide();
        }

        $.ajax({
            url: $('#affiliation-api').val(),
            data: {
                affiliation_id: $(this).val(),
                csrfmiddlewaretoken: $('form input[name="csrfmiddlewaretoken"]').val()
            }
        }).done(function(data) {
            fillAffiliationFields(data);
        }).fail(function(errors) {
            console.log(errors);
            fillAffiliationFields()
        });
    });
    affiliationSelect.trigger('change');
}

function bindNewPersonButton() {
    $('button.new-affiliation-button').on('click', function() {
        var data = $('div.new-person-fields input, div.new-person-fields select').toArray().reduce(function(dict, field) {
            dict[field.name] = field.value;
            return dict;
        }, {});

        $.ajax({
            url: $('#affiliation-api').val(),
            type: 'post',
            data: $.extend({
                csrfmiddlewaretoken: $('form input[name="csrfmiddlewaretoken"]').val()
            }, data)
        }).done(function(data) {
            var newOption = $('<option value="' + data.affiliation_id + '">' +
                data.person.person_first_name + ' ' + data.person.person_last_name +
                ' (' + data.organization.organization_name + ')' + '</option>');
            $('select[name="affiliation"]').append(newOption).val(data.affiliation_id).trigger('change');
        }).fail(function(errors) {
            console.log(errors);
        });
    });
}

$(document).ready(function() {
    var form = $('form');
    selectSoloOptions(form);
    initializeSelects(form);
    bindAffiliationChange();
    bindNewPersonButton();

    $('div.form-field.has-error .form-control').on('change keypress', function() {
        var fieldElement = $(this).parents('div.form-field');
        if (fieldElement.hasClass('has-error')) {
            fieldElement.removeClass('has-error');
        }
    });

    $('button.new-result-button').on('click', addResult);
    bindDeleteResult($('form .result-form'));

    $('div.form-field div.input-group.date').datepicker({
        todayBtn: "linked",
        autoclose: true,
        todayHighlight: true,
        format: 'yyyy-mm-dd',
        maxViewMode: 2
    });

    $(document).on("keypress", ":input:not(textarea):not([type=submit])", function(event) {
        if (event.keyCode == 13) {
            event.preventDefault();
        }
    });
});
