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

function bindResultEvents(resultForm) {
    var equipmentModelSelect = resultForm.find('[name$="equipment_model"]');

    // Delete button
    resultForm.find('span.remove-result').on('click', function() {
        var forms = $('input[name="form-TOTAL_FORMS"]');
        $(this).parents('.result-form').remove();
        forms.val(forms.val() - 1);
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

    equipmentModelSelect.trigger('change', [true]);

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
    $('button.new-result-button').on('click', addResult);
    bindResultEvents($('form .result-form'));
});
