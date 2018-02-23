'use strict';

function initializeHydroShareDeleteDialog() {
    const deleteForm = $('#hs-delete-form');
    const deleteFormDialog = $('#hydroshare-delete-dialog')[0];
    const showDeleteDialogBtn = $('button#show-hydroshare-delete-dialog');
    const deleteResourceCB = $('label[for="id_delete_external_resource"]');

    if (!deleteFormDialog.showModal) {
        dialogPolyfill.registerDialog(deleteFormDialog);
    }

    $(showDeleteDialogBtn).click(() => {
       deleteFormDialog.showModal();
       $('label[for="id_delete_external_resource"]').removeClass('is-focused');
    });

    deleteFormDialog.querySelector('.close').addEventListener('click', () => {
        deleteFormDialog.close();
    });

    deleteForm.submit((e) => {
        const submitButton = $(deleteFormDialog).find('input[type=submit]');
        submitButton[0].setAttribute('disabled', '');
        $(submitButton[0]).removeClass('mdl-color--red-400');
        $(submitButton[0]).addClass('mdl-color--grey');

        const spinner = $(deleteFormDialog).find('.mdl-js-spinner')[0];
        $(spinner).addClass('is-active');
        componentHandler.upgradeElement(spinner);

    });

    deleteResourceCB.change(() => {
        let warningList = $('div#checkbox-warning-list');
        let isChecked = $(deleteResourceCB[0]).hasClass('is-checked');
        $(warningList).prop('hidden', !isChecked);
    });


}