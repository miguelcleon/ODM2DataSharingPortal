(function () {
    'use strict';

    try {
        const disconnectForm = $('#disconnect-hs-form');
        const hsDialog = document.querySelector('#hs-dialog');

        let shouldDisconnectHSAccount = false;

        disconnectForm.submit((e) => {
            if (!shouldDisconnectHSAccount) {
                e.preventDefault();
                hsDialog.removeAttribute('hidden');
                hsDialog.showModal();
            }
        });


        if (!hsDialog.showModal) {
            dialogPolyfill.registerDialog(hsDialog);
        }

        hsDialog.querySelector('.close').addEventListener('click', () => {
            hsDialog.close();
            hsDialog.setAttribute('hidden', '');
            shouldDisconnectHSAccount = false;
        });

        hsDialog.querySelector('#continue').addEventListener('click', () => {
            hsDialog.close();
            hsDialog.setAttribute('hidden', '');
            shouldDisconnectHSAccount = true;
            disconnectForm.submit();
        });
    } catch (e) {
        // ignore error :D
    }


}());