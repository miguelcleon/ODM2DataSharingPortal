// (function() {
//     'use strict';
//
// }());

function updateSitePosition(map, position) {
    map.panTo(position);
    $('input[name="latitude"]').val(Math.round(position.lat() * 100000) / 100000).trigger('keypress');
    $('input[name="longitude"]').val(Math.round(position.lng() * 100000) / 100000).trigger('keypress');
}

function updateSiteElevation(position) {
    var elevator = new google.maps.ElevationService();
     elevator.getElevationForLocations({'locations':[position]}, function(results, status) {
          if (status == google.maps.ElevationStatus.OK && results[0]) {
              $('input[name="elevation_m"]').val(Math.round(results[0].elevation)).trigger('keypress');
          }
     });
}

function initMap() {
    const DEFAULT_ZOOM = 4;
    const DEFAULT_SPECIFIC_ZOOM = 10;
    const DEFAULT_LATITUDE = 37.0902;
    const DEFAULT_LONGITUDE = -95.7129;
    var mapPosition = { lat: parseFloat($('input[name="latitude"]').val()), lng: parseFloat($('input[name="longitude"]').val()) };
    var isCompletePosition = mapPosition.lat && mapPosition.lng;
    var mapZoom = parseInt($('input[name="zoom-level"]').val());

    var map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: mapPosition.lat || DEFAULT_LATITUDE, lng: mapPosition.lng || DEFAULT_LONGITUDE },
        zoom: mapZoom || DEFAULT_ZOOM,
        mapTypeId: google.maps.MapTypeId.HYBRID,
        gestureHandling: 'greedy',
        draggableCursor: 'pointer',
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


output_variables = {};

filter_structure = {
    'sensor_manufacturer': {sub_filters: ['sensor_model']},
    'sensor_model': {sub_filters: ['variable', 'sensor_manufacturer']},
    'variable': {sub_filters: ['unit', 'sampled_medium', 'sensor_model']},
    'unit': {sub_filters: ['variable']},
    'sampled_medium': {sub_filters: ['variable']}
};

function clear_filters() {
    var form = $('div#result-dialog .result-form');
    for (var filter_name in filter_structure) {
        if (!filter_structure.hasOwnProperty(filter_name)) {
            continue;
        }

        var select = form.find('select[name$="' + filter_name + '"]');
        var filter = filter_structure[filter_name];

        if (filter.filtered_set) {
            filter.filtered_set.length = 0;
        }
        filter.filtered_by = undefined;

        select.val('');
        select.trigger('change');
    }

}

function apply_filter(filter_name, values, parent_filter_name) {
    var filter = filter_structure[filter_name];
    var parent_filter = filter_structure[parent_filter_name];
    var has_selected_values = !(values.length === 1 && values[0] === '');
    var filtered_set = parent_filter && parent_filter.filtered_set || output_variables;

    if (has_selected_values) {
        filtered_set = filtered_set.filter(function(output) {
            if (!output.hasOwnProperty(filter_name)) {
                return false;
            }
            return values.indexOf(output[filter_name] && output[filter_name].toString()) >= 0;
        });
    }

    var is_initial_set = output_variables.every(function(item){return filtered_set.indexOf(item) >= 0;});
    filter.filtered_by = (is_initial_set)? undefined: parent_filter_name;
    filter.filtered_set = filtered_set;

    for (var index = 0; index < filter.sub_filters.length; index++) {
        var sub_filter_name = filter.sub_filters[index];

        if (sub_filter_name === parent_filter_name) {
            continue;
        }

        var sub_filter_values = filter.filtered_set.reduce(function(filter_values, output) {
            var value = output[sub_filter_name] && output[sub_filter_name].toString();
            if (filter_values.indexOf(value) < 0) {
                filter_values.push(value);
            }
            return filter_values;
        }, []);

        updateFilterUI(sub_filter_name, sub_filter_values);
        apply_filter(sub_filter_name, sub_filter_values, filter_name);
    }
}

function updateFilterUI(sub_filter, sub_filter_values) {
    var select = $('div#result-dialog .result-form select[name$="' + sub_filter + '"]');
    filterSelectOptions(select, sub_filter_values);
}

function bindResultEvents(form) {
    var filters = Object.keys(filter_structure);
    var output_variable_select = $('div#result-dialog .result-form input[name$="output_variable"]');

    $.ajax({
        url: $('#output-variables-api').val(),
        data: {csrfmiddlewaretoken: $('form').find('[name="csrfmiddlewaretoken"]').val()}
    }).fail(function(xhr, error) {
        console.log(error);
    }).done(function(data) {
        output_variables = data;
    }).always(function(response, status, xhr) {
        console.log(status + ": " + xhr.responseText);
    });

    for (var index = 0; index < filters.length; index++) {
        var filter = filter_structure[filters[index]];
        var select = form.find('[name$="' + filters[index] + '"]');

        (function(i, filter, select) {
            select.on('change', function(event, automatic_trigger) {
                if (automatic_trigger) {
                    return;
                }

                output_variable_select.val('');
                apply_filter(filters[i], [$(this).val()], filter.filtered_by);

                if (filter.filtered_set.length === 1) {
                    output_variable_select.val(filter.filtered_set[0].pk);
                }
            });
        })(index, filter, select);
    }
}


function defaultTableMessage() {
    $("tr.no-sensors-row").toggleClass("hidden", !!$("tr.result-form:not(.deleted-row)").length);
}


function initializeResultsForm() {
    var form = $('div#result-dialog .result-form');
    bindResultEvents(form);
    selectSoloOptions(form.find('select'));
    initializeSelect(form.find('select.form-control'));
    
    $('div#result-dialog').on('show.bs.modal', function(event) {
        var dialog = $(this);
        var fieldsParents = form.find('select').parents('div.form-field');

        if (fieldsParents.hasClass('has-error')) {
            fieldsParents.find('.errorlist').remove();
            fieldsParents.removeClass('has-error');
        }

        if (event.relatedTarget && event.relatedTarget.id === 'new-result-button') {
            clear_filters();
            form.find('input[name="id"]').val('');
            form.find('input[name="output_variable"]').val('');

            dialog.find('#result-dialog-title').text("Add Sensor");
            dialog.find('#add-sensor-button').show();
            dialog.find('#edit-sensor-button').hide();
            $('#result-dialog-uuid').parent().hide();


        } else {
            var row = dialog.data('row');
            $('#result-dialog-title').text("Update Sensor");
            dialog.find('#add-sensor-button').hide();
            dialog.find('#edit-sensor-button').show();
            $('#result-dialog-uuid').text(row['result_uuid']).parent().show();
        }
    });

    $('div#result-dialog button#add-sensor-button').on('click', function() {
        var new_sensor_api = $('#sensor-registration-api').val();

        make_sensor_api_request(new_sensor_api).done(function(data, message, xhr) {
            var form = $('div#result-dialog div.result-form');

            if (xhr.status === 201) {
                // valid
                var newRow = $($('#sensor-row').html());
                form.find('[name="id"]').val(data['id']);

                updateRowData(newRow);
                bindResultEditEvent(newRow);
                bindResultDeleteEvent(newRow);

                $('div.results-table table').append(newRow);
                defaultTableMessage();

                $('#result-dialog').modal('toggle');

            } else if (xhr.status === 206) {
                // not valid
                for (var fieldName in data) {
                    var element = form.find('[name*="' + fieldName + '"]');
                    var field = element.parents('.form-field');
                    field.addClass('has-error');

                    form.find('div.form-field.has-error .form-control').on('change keypress', function(event, isTriggered) {
                        if (isTriggered) {  // http://i.imgur.com/avHnbUZ.gif
                            return;
                        }

                        var fieldElement = $(this).parents('div.form-field');
                        if (fieldElement.hasClass('has-error')) {
                            fieldElement.find('.errorlist').remove();
                            fieldElement.removeClass('has-error');
                        }
                    });
                }
            }
        });
    });

    $('div#result-dialog button#edit-sensor-button').on('click', function() {
        var edit_sensor_api = $('#sensor-edit-api').val();

        make_sensor_api_request(edit_sensor_api).done(function(data, message, xhr) {
            var form = $('div#result-dialog div.result-form');

            if (xhr.status === 201) {
                // valid
                var newRow = $($('#sensor-row').html());
                form.find('[name="id"]').val(data['id']);

                updateRowData(newRow);
                bindResultEditEvent(newRow);
                bindResultDeleteEvent(newRow);

                $('div.results-table table').append(newRow);
                defaultTableMessage();

                $('#result-dialog').modal('toggle');

            } else if (xhr.status === 206) {
                // not valid
                for (var fieldName in data) {
                    var element = form.find('[name*="' + fieldName + '"]');
                    var field = element.parents('.form-field');
                    field.addClass('has-error');

                    form.find('div.form-field.has-error .form-control').on('change keypress', function(event, isTriggered) {
                        if (isTriggered) {  // http://i.imgur.com/avHnbUZ.gif
                            return;
                        }

                        var fieldElement = $(this).parents('div.form-field');
                        if (fieldElement.hasClass('has-error')) {
                            fieldElement.find('.errorlist').remove();
                            fieldElement.removeClass('has-error');
                        }
                    });
                }
            }
        });

        // var dialog = $('#result-dialog');
        // var row = dialog.data('row');
        // updateRowData(row);
        // dialog.modal('toggle');
    });

    defaultTableMessage();
    notifyInputStatus();
}

function validateResultForm() {
    var prefixText = '-__prefix__-';
    var data = $('#result-dialog div.result-form input, #result-dialog div.result-form select').toArray().reduce(function(dict, field) {
        var fieldName = field.name.substring(field.name.indexOf(prefixText) + prefixText.length, field.name.length);
        dict[fieldName] = field.value;
        return dict;
    }, {});
    
    return $.ajax({
        url: $('#result-validation-api').val(),
        type: 'post',
        data: $.extend({ csrfmiddlewaretoken: $('form input[name="csrfmiddlewaretoken"]').val() }, data)
    });
}


function make_sensor_api_request(api_url) {
    var output_data = $('#result-dialog div.result-form input, #result-dialog div.result-form select').toArray().reduce(function(dict, field) {
        dict[field.name] = field.value;
        return dict;
    }, {});

    return $.ajax({
        url: api_url,
        type: 'post',
        data: $.extend({ csrfmiddlewaretoken: $('form input[name="csrfmiddlewaretoken"]').val() }, output_data)
    });
}


function fillFormData(row) {
    var rowData = row.data();
    var form = $('div#result-dialog div.result-form');

    for (var field_name in filter_structure) {
        if (!filter_structure.hasOwnProperty(field_name)) {
            continue;
        }

        var formSelect = form.find('.form-control[name="' + field_name + '"]');
        formSelect.val(rowData[field_name]);
        formSelect.trigger('change');
    }

    form.find('input[name="id"]').val(rowData['id']);
    form.find('input[name="output_variable"]').val(rowData['sensor_output']);

    $('#result-dialog').data('row', row);
}

function updateRowData(row) {
    var fields = $('div#result-dialog div.result-form input, div#result-dialog div.result-form select');

    for (var index = 0; index < fields.length; index++) {
        var field = $(fields.get(index));
        var fieldName = field.attr('name');
        var value = field.val();
        row.data(fieldName, value);

        if (field.hasClass('form-control')) {
            var selectedOption = field.find('option:selected');
            var dataColumn = row.find('td[data-field="' + fieldName + '"]');
            dataColumn.find('.field-text').text(selectedOption.text());
        }
    }
}


function bindResultEditEvent(row) {
    row.find('td[data-behaviour="edit"] button').on('click', function(event) {
        var rowElement = $(this).parents('tr');
        var result_uuid = rowElement.data('result_uuid');

        clear_filters();
        fillFormData(rowElement);

        $('#result-dialog').modal('toggle');
    });
}

function bindResultDeleteEvent(row) {
    row.find('td[data-behaviour="delete"] button').on('click', function(event) {
        var sensor = $(this).parents('tr');
        $('#confirm-delete').data('to-delete', sensor).modal('toggle');
    });
}

function initializeResultsTable() {
    var rows = $('div.results-table tbody tr');
    bindResultEditEvent(rows);
    bindResultDeleteEvent(rows);
}

function notifyInputStatus() {
    if (!$("#id_notify").prop("checked")) {
        $("#id_hours_threshold").removeAttr("name");
        $("#id_hours_threshold").removeAttr("required");
    }
    else {
        $("#id_hours_threshold").attr("name", "hours_threshold");
        $("#id_hours_threshold").attr("required", true);
    }
}

$(document).ready(function() {
    $('nav .menu-register-site').addClass('active');

    initializeResultsForm();
    initializeResultsTable();

    $('#btn-confirm-delete').on('click', function(event) {
        var dialog = $('#confirm-delete');

        // dialog.data('to-delete').addClass('deleted-row').find('input[name*="DELETE"]').prop('checked', true);
        dialog.modal('toggle');
        defaultTableMessage();
    });

    $("#id_notify").change(function() {
        $("div[data-field='hours_threshold']").toggleClass("hidden", !this.checked);
        notifyInputStatus();
    });
});
