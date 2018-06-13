/**
 * Created by Mauriel on 6/5/2018.
 */

function defaultExperimentsMessage() {
    $("tr.no-experiments-row").toggleClass("hidden", !!$("tr.leafpack-form:not(.deleted-row)").length);
}

$(document).ready(function() {
    $(".btn-delete-experiment").click(function () {
        var experiment = $(this).parents('tr');
        $('#confirm-delete-experiment').data('to-delete', experiment).modal('show');
    });

    $("#btn-confirm-delete-experiment").click(function () {
        var dialog = $('#confirm-delete-experiment');
        var row = dialog.data('to-delete');
        $("#btn-confirm-delete-experiment").prop("disabled", true).text("DELETING EXPERIMENT...");

        $.ajax({
            url: $('#leafpack-delete-api').val(),
            type: 'post',
            data: {
                csrfmiddlewaretoken: $('fieldset.form-fieldset input[name="csrfmiddlewaretoken"]').val(),
                id: row.data('id')
            }
        }).done(function (data, message, xhr) {
            if (xhr.status === 202) {
                // Valid
                row.remove();
                snackbarMsg('Leafpack has been deleted!');

            } else if (xhr.status === 206) {
                // Invalid
                snackbarMsg('Leafpack could not be deleted!');
            }
        }).fail(function (xhr, error) {
            console.log(error);
        }).always(function (response, status, xhr) {
            $("#btn-confirm-delete-experiment").prop("disabled", false).text("DELETE");
            defaultExperimentsMessage();
            dialog.modal('hide');
        });
    });
});