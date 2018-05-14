/**
 * Created by Mauriel on 5/10/2018.
 */
$(document).ready(function () {
    $('.datepicker').datepicker({
        format: 'yyyy-mm-dd',
        startDate: '0d'
    });

    $("#id_had_storm").change(function() {
        var val = parseInt($(this).val());
        if (val == 2) {
            $("#storm-additional").collapse('show');
        }
        else {
            $("#storm-additional").collapse('hide');
        }
    });

    $(".bug-count").change(function() {
        var items = $(this).closest(".mdl-card").find(".bug-count");
        var count = 0;
        // for (var i = 0; i < items.length; i++) {
        //     var val = $(items[i]).val();
        //     if (val) {
        //         count += parseInt(val);
        //     }
        // }

        items.each(function () {
            var val = $(this).val();
            if (val) {
                count += parseInt(val);
            }
        });

        var total = parseInt($(this).closest(".mdl-card").find(".bug-total-count").val(count));
    });

    $(".bug-total-count").change(function() {
        var items = $(this).closest(".mdl-card").find(".bug-count");
        $(items).val("");
    });
});