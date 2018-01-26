$(function() {
   const dialog = document.querySelector('#hydroshare-settings-dialog');
   const showDialogButton = document.querySelector('#show-hydroshare-settings-dialog');

    if (!dialog.showModal) {
        console.log("Registering modal");
        dialogPolyfill.registerDialog(dialog);
    }

    showDialogButton.addEventListener('click', () => {
        dialog.showModal();
    });

    dialog.querySelector('.close').addEventListener('click', () => {
        dialog.close();
    });

    setTimeout(() => {
        dialog.showModal();
    }, 0);

});