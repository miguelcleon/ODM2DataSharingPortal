/**
 * Created by Juan on 11/28/2016.
 */

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

$(document).ready(function() {
    var form = $('form');
    selectSoloOptions(form.find('select'));
    initializeSelect(form.find('select.form-control'));
    
    $('div.form-field.has-error .form-control').on('change keypress', function() {
        var fieldElement = $(this).parents('div.form-field');
        if (fieldElement.hasClass('has-error')) {
            fieldElement.find('.errorlist').remove();
            fieldElement.removeClass('has-error');
        }
    });

    $(document).on("keypress", ":input:not(textarea):not([type=submit])", function(event) {
        if (event.keyCode == 13) {
            event.preventDefault();
        }
    });
});
