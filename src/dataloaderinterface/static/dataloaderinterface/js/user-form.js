/**
 * Created by Juan on 12/12/2016.
 */


function cleanOrganizationForm() {
    $('.organization-fields input, .organization-fields select').val('');
}

$(document).ready(function() {
    var organizationForm = $('.organization-fields');
    var organizationSelect = $('form').find('[name="organization"]');
    initializeSelect(organizationForm.find('[name="organization_type"]'));

    $('<option value="new">Add New Organization</option>').insertAfter(organizationSelect.children().first());
    organizationSelect.on('change', function() {
        if ($(this).val() == 'new') {
            cleanOrganizationForm();
            $('#organization-dialog').modal('toggle');
        }
    });

    $('#new-organization-button').on('click', function() {
        var data = $('.organization-fields input, .organization-fields select').toArray().reduce(function(dict, field) {
            dict[field.name] = field.value;
            return dict;
        }, {});
        
        $.ajax({
            url: $('#new-organization-api').val(),
            type: 'post',
            data: $.extend({
                csrfmiddlewaretoken: $('form input[name="csrfmiddlewaretoken"]').val()
            }, data)
        }).done(function(data) {
            var newOption = $('<option value="' + data.organization_id + '">' +
                data.organization_name + '</option>');
            $('select[name="organization"]').append(newOption).val(data.organization_id);
            $('#organization-dialog').modal('toggle');
        }).fail(function(data) {
            if (!data.responseJSON || data.status != 400) {
                console.log(data);
                return;
            }

            var form = $('.organization-fields');
            for (var fieldName in data.responseJSON) {
                var element = form.find('[name="' + fieldName + '"]');
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
        });
    });
});
