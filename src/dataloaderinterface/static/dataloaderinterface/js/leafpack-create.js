/**
 * Created by Mauriel on 5/10/2018.
 */
$(document).ready(function () {
    // var datepicker = $.fn.datepicker.noConflict(); // return $.fn.datepicker to previously assigned value
    // $.fn.bootstrapDP = datepicker;                 // give $().bootstrapDP the bootstrap-datepicker functionality
    // $.fn.bootstrapDP.defaults.format = "mm/dd/yyyy";
    $('.datepicker').datepicker({
        format: 'yyyy-mm-dd',
        startDate: '0d'
    });
});