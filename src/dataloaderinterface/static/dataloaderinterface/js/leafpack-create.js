/**
 * Created by Mauriel on 5/10/2018.
 */
$(document).ready(function () {
    $('.datepicker').datepicker({
        format: 'yyyy-mm-dd',
        startDate: '0d'
    });

    $("#id_had_storm").change(function () {
        var val = parseInt($(this).val());
        var collapse = $("#storm-additional");
        if (val == 2) {
            var items = collapse.find("[data-name]");
            items.each(function () {
                $(this).attr("name", $(this).attr("data-name"));
                $(this).removeAttr("data-name");
            });
            $("#storm-additional").collapse('show');
        }
        else {
            var items = collapse.find("[name]");
            items.each(function () {
                $(this).attr("data-name", $(this).attr("name"));
                $(this).removeAttr("name");
            });
            $("#storm-additional").collapse('hide');
        }
    });

    $(".bug-count").change(function() {
        var items = $(this).closest(".mdl-card").find(".bug-count");
        var count = 0;
        var total = $(this).closest(".mdl-card").find(".bug-total-count");

        items.each(function () {
            var val = $(this).val();
            if (val) {
                count += parseInt(val);
            }
        });

        total.val(Math.max(total.val(), count));
    });

    $(".bug-total-count").change(function() {
        var items = $(this).closest(".mdl-card").find(".bug-count");
        var count = 0;
        var total = $(this).closest(".mdl-card").find(".bug-total-count");

        items.each(function () {
            var val = $(this).val();
            if (val) {
                count += parseInt(val);
            }
        });

        if (count > total.val()) {
            $(items).val("");
        }
    });
});