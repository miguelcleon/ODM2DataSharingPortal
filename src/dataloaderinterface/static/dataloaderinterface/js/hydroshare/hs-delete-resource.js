'use strict';

function initializeHydroShareDeleteDialog() {
    const deleteFormDialog = $('#hydroshare-delete-dialog')[0];
    const stopSharingButton = $('button#show-hydroshare-delete-dialog');

    if (!deleteFormDialog.showModal) {
        dialogPolyfill.registerDialog(deleteFormDialog);
    }

    $(stopSharingButton).click(() => {
       deleteFormDialog.showModal();
    });

    deleteFormDialog.querySelector('.close').addEventListener('click', () => {
        deleteFormDialog.close();
    });

}