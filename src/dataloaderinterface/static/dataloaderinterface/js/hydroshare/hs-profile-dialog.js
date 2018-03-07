/*
* hs-profile-dialog.js
* This script is loaded into the browser at /account/.
*
* This script allows a user to authorize/deathorize EnviroDIY to perform actions on the users HydroShare account in
* the users behalf.
* */
(function () {
    'use strict';

    try {
        const disconnectForm = $('#disconnect-hs-form');
        const dialog = document.querySelector('#hs-dialog');

        let shouldDisconnectHSAccount = false;

        disconnectForm.submit((e) => {
            if (!shouldDisconnectHSAccount) {
                e.preventDefault();
                dialog.removeAttribute('hidden');
                dialog.showModal();
            }
        });

        if (!dialog.showModal) {
            dialogPolyfill.registerDialog(dialog);
        }

        dialog.querySelector('.close').addEventListener('click', () => {
            dialog.close();
            dialog.setAttribute('hidden', '');
            shouldDisconnectHSAccount = false;
        });

        dialog.querySelector('#continue').addEventListener('click', () => {
            dialog.close();
            dialog.setAttribute('hidden', '');
            shouldDisconnectHSAccount = true;
            disconnectForm.submit();
        });
    } catch (e) {
        // ignore error :-D
    }


}());