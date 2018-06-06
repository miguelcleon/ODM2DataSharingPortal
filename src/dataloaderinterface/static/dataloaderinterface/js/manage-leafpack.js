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
        dialog.data('to-delete').addClass('deleted-row').find('input[name*="DELETE"]').prop('checked', true);
        defaultExperimentsMessage();
        dialog.modal('hide');
    });

    defaultExperimentsMessage();
});