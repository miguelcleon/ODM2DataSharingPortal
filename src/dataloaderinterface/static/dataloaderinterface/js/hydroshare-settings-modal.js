/**
 * hydroshare-settings-modal.js
 * @description Determines how the hydroshare settings modal is presented in 'site_details.html'.
 */

$(() => {
    const dialog = document.querySelector('#hydroshare-settings-dialog');
    const showDialogButton = document.querySelector('#show-hydroshare-settings-dialog');
    const hydroshareSettingsForm = document.querySelector('#hydroshare-settings-form');

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

    hydroshareSettingsForm.addEventListener('submit', (e) => {
         e.preventDefault();
         submitForm();
    });

    setTimeout(() => {
        dialog.showModal();
    }, 0);

    function submitForm() {
        let url = `${hydroshareSettingsForm.baseURI}/hydroshare_settings`;
        let serialized = $('#hydroshare-settings-form').serialize();
        $.post(url, serialized)
            .done(data => {
               console.log('Data from request: ', data);
            })
            .fail((xhr) => {
                let errors = xhr && xhr.responseJSON ? xhr.responseJSON : null;
                if (errors) {
                    console.error(errors);
                    for (let err in errors) {
                        let errList = errors[err];
                        if (Array.isArray((errList))) {
                            let htmlInsertList = '';
                            for (let err of errList) { htmlInsertList += `<li>${err}</li>` }
                            let inputField = $(`#id_${err}`);
                            inputField.after(`<ul class="errorlist">${htmlInsertList}</ul>`);
                        }
                    }
                }
            });

    }



});