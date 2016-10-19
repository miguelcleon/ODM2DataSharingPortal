// (function() {
//     'use strict';
//
// }());

function updateSitePosition(map, position) {
    map.panTo(position);
    $('input[name="latitude"]').val(position.lat);
    $('input[name="longitude"]').val(position.lng);
}

function updateSiteElevation(position) {
    var elevator = new google.maps.ElevationService();
     elevator.getElevationForLocations({'locations':[position]}, function(results, status) {
          if (status == google.maps.ElevationStatus.OK && results[0]) {
              $('input[name="elevation_m"]').val(results[0].elevation);
          }
     });
}

function initMap() {
    var defaultZoomLevel = 4;
    var defaultPosition = { lat: 37.0902, lng: -95.7129 };
    var mapTip = $('<div class="map-info"><span class="map-tip">Click on the map to update coordinates and elevation data</span></div>');

    var map = new google.maps.Map(document.getElementById('map'), {
        center: defaultPosition,
        zoom: defaultZoomLevel,
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
        position: undefined,
        map: map
    });

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function getLocation(position){
            map.setCenter({ lat: position.coords.latitude, lng: position.coords.longitude });
            map.setZoom(10);
        }, undefined, { timeout: 5000 });
    }

    map.controls[google.maps.ControlPosition.TOP_CENTER].push(mapTip.get(0));

    map.addListener('click', function(event) {
        marker.setPosition(event.latLng);
        updateSitePosition(map, event.latLng);
        updateSiteElevation(event.latLng);
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

    $('button.new-result-button').on('click', addResult);
    bindDeleteResult($('form .result-form'));

    //$('.form-field.required-field input, .form-field.required-field select').attr('required', true);

    $(document).on("keypress", ":input:not(textarea):not([type=submit])", function(event) {
        if (event.keyCode == 13) {
            event.preventDefault();
        }
    });
});
