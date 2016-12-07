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


// function checkSelectsIntegrity(resultForm) {
//     var equipmentModelSelect = resultForm.find('[name$="equipment_model"]');
//     var variableSelect = resultForm.find('[name$="variable"]');
//     var unitSelect = resultForm.find('[name$="unit"]');
//
// }


function applyInstrumentOutputFilter(equipmentModelSelect) {
    var resultForm = equipmentModelSelect.parents('.result-form');
    var variableSelect = resultForm.find('[name$="variable"]');
    var unitSelect = resultForm.find('[name$="unit"]');

    var outputVariables = equipmentModelSelect
        .find('option[value=' + equipmentModelSelect.val() + ']')
        .data('output-variables');

    filterSelectOptions(variableSelect, Object.keys(outputVariables.variables));
    filterSelectOptions(unitSelect, Object.keys(outputVariables.units));

    variableSelect.data('filters-applied', false);
    unitSelect.data('filters-applied', false);

    if (variableSelect.val()) {
        variableSelect.trigger('change');
    } else if (unitSelect.val()) {
        unitSelect.trigger('change');
    }
}

function bindResultEvents(resultForm) {
    var equipmentModelSelect = resultForm.find('[name$="equipment_model"]');
    var variableSelect = resultForm.find('[name$="variable"]');
    var unitSelect = resultForm.find('[name$="unit"]');


    // delete button
    resultForm.find('span.remove-result').on('click', function() {
        var forms = $('input[name="form-TOTAL_FORMS"]');
        $(this).parents('.result-form').remove();
        forms.val(forms.val() - 1);
    });

    // equipment model selection
    equipmentModelSelect.on('change', function() {
        var resultForm = $(this).parents('.result-form');

        // clear filter if no model was selected.
        var modelId = $(this).val();
        if (!modelId) {
            clearSelectFilter(resultForm.find('[name$="variable"]').add(resultForm.find('[name$="unit"]')));
            return;
        }

        var selectedOption = equipmentModelSelect.find('option[value=' + modelId + ']');
        // just apply filter if there's a cached map of output variables.
        if (selectedOption.data('output-variables')) {
            applyInstrumentOutputFilter(equipmentModelSelect);
            return;
        }

        // request output variables
        requestFilteredOptions(
            $('#model-variables-api').val(),
            { equipment_model_id: modelId, csrfmiddlewaretoken: $('form').find('[name="csrfmiddlewaretoken"]').val() },
            function(data) {
                var variablesMap = data.reduce(function(map, outputVariable) {
                    var units = map[outputVariable.variable] || [];
                    units.push(outputVariable.instrument_raw_output_unit.toString());
                    map[outputVariable.variable] = units;
                    return map;
                }, {});

                var unitsMap = data.reduce(function(map, outputUnit) {
                    var variables = map[outputUnit.instrument_raw_output_unit] || [];
                    variables.push(outputUnit.variable.toString());
                    map[outputUnit.instrument_raw_output_unit] = variables;
                    return map;
                }, {});

                selectedOption.data('output-variables', { variables: variablesMap, units: unitsMap });
                applyInstrumentOutputFilter(equipmentModelSelect);
            }
        );
    });
    equipmentModelSelect.trigger('change', [true]);


    variableSelect.on('change', function() {
        var resultForm = $(this).parents('.result-form');
        var modelId = equipmentModelSelect.val();
        var variableId = $(this).val();

        if ($(this).data('filters-applied') || !modelId) {
            return;
        }

        if (!variableId) {
            resultForm.find('[name$="equipment_model"]').trigger('change', [true]);
            return;
        }

        var outputVariableData = equipmentModelSelect.find('option[value=' + modelId + ']').data('output-variables');
        unitSelect.data('filters-applied', true);

        filterSelectOptions(unitSelect, outputVariableData.variables[variableId]);
    });
    variableSelect.trigger('change', [true]);


    unitSelect.on('change', function() {
        var resultForm = $(this).parents('.result-form');
        var modelId = equipmentModelSelect.val();
        var unitId = $(this).val();

        if ($(this).data('filters-applied') || !modelId) {
            return;
        }

        if (!unitId) {
            resultForm.find('[name$="equipment_model"]').trigger('change', [true]);
            return;
        }

        var outputVariableData = equipmentModelSelect.find('option[value=' + modelId + ']').data('output-variables');
        variableSelect.data('filters-applied', true);

        filterSelectOptions(variableSelect, outputVariableData.units[unitId]);
    });
    unitSelect.trigger('change', [true]);
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
