'use strict';

$(function () {
    // Add event handler on each toggle that submits it's parent form when the toggle is clicked
    function addSwitchClickHandlers() {
        const switches = $('form#hydroshare-udpate-form').find('input.mdl-switch__input');
        if (switches) {
            switches.each(function() {
                $(this).on('click', function(ev) {
                    const parentForm = ev.target.closest('form');
                    submitWait(parentForm);
                });
            });
        }
    }

    // Delay form submition to allow animation to complete on mdl toggle switch
    function submitWait(form) {
        setTimeout(function() {
            form.submit();
        }, 250);
    }

    addSwitchClickHandlers();
});
