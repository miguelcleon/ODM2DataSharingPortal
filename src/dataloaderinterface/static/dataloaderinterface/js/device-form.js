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

function requestFilteredOptions(serviceUrl, data, callback) {
    $.ajax({ url: serviceUrl, data: data })
        .done(callback)
        .fail(function(xhr, error) {
            console.log(error);
        })
        .always(function(xhr) {
            console.log(xhr.status+": "+xhr.responseText);
        });
}

function filterSelectOptions(select, values) {
    select.children('option').each(function(index, element) {
        if (values.indexOf(element.value) === -1 && element.value !== '') {
            $(element).attr('disabled', 'disabled');
        } else {
            $(element).removeAttr('disabled');
        }
    });

    if (values.indexOf(select.val()) === -1) {
        select.val('');
    }

    selectSoloOptions(select);
    initializeSelect(select);
}


function clearSelectFilter(select) {
    select.children('option').removeAttr('disabled');
    initializeSelect(select);
}


function bindResultEvents(resultForm) {
    var equipmentModelSelect = resultForm.find('[name$="equipment_model"]');

    // Delete button
    resultForm.find('span.remove-result').on('click', function() {
        $(this).parents('.result-form').remove();
    });

    // equipment model selection
    equipmentModelSelect.on('change', function() {
        var parentForm = $(this).parents('.result-form');
        var unitSelect = parentForm.find('[name$="unit"]');
        var variableSelect = parentForm.find('[name$="variable"]');

        var modelId = $(this).val();
        if (!modelId) {
            clearSelectFilter(variableSelect.add(unitSelect));
            return;
        }

        requestFilteredOptions(
            $('#model-variables-api').val(),
            {
                equipment_model_id: modelId,
                csrfmiddlewaretoken: $('form').find('[name="csrfmiddlewaretoken"]').val()
            },
            function filterEquipmentModelOutput(equipmentModel) {
                var variables = equipmentModel.output_variables.map(function(variable) { return variable.variable_id + '' });
                var units = equipmentModel.output_units.map(function(unit) { return unit.unit_id + '' });
                filterSelectOptions(variableSelect, variables);
                filterSelectOptions(unitSelect, units);
            }
        );
    });

    equipmentModelSelect.trigger('change');

}

function initializeSelect(select) {
    select.select2({
        theme: "bootstrap",
        containerCssClass : "input-sm",
        dropdownAutoWidth: true,
        width: 'auto'
    });
}

function selectSoloOptions(select) {
    select.each(function() {
        var selectElement = $(this);
        var options = selectElement.children('[value!=""]:not([disabled])');
        if (options.length === 1) {
            selectElement.val(options.get(0).value);
        }
    });
}

function addResult() {
    var newIndex = $('div#formset div.result-form').length;
    $('input[name="form-TOTAL_FORMS"]').val(newIndex + 1);

    var newResultForm = $($('div#results-template').html().replace(new RegExp('__prefix__', 'g'), newIndex));
    $('.formset-container').append(newResultForm);

    bindResultEvents(newResultForm);
    selectSoloOptions(newResultForm.find('select'));
    initializeSelect(newResultForm.find('select.form-control'));
}

$(document).ready(function() {
    var form = $('form');
    selectSoloOptions(form.find('select'));
    initializeSelect(form.find('select.form-control'));

    $('div.form-field.has-error .form-control').on('change keypress', function() {
        var fieldElement = $(this).parents('div.form-field');
        if (fieldElement.hasClass('has-error')) {
            fieldElement.removeClass('has-error');
        }
    });

    $('button.new-result-button').on('click', addResult);
    bindResultEvents($('form .result-form'));

    $(document).on("keypress", ":input:not(textarea):not([type=submit])", function(event) {
        if (event.keyCode == 13) {
            event.preventDefault();
        }
    });
});
