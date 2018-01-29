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

    // setTimeout(() => { dialog.showModal(); }, 0);

    function submitForm() {
        let url = `${hydroshareSettingsForm.baseURI}hydroshare_settings/`;
        let serializedForm = $(hydroshareSettingsForm).serialize();
        let progressSpinner = $(hydroshareSettingsForm).find('#hydroshare-form-spinner');

        progressSpinner.addClass('is-active');

        $.post(url, serializedForm)
            .done(data => {
                console.log(data);
                dialog.close();
            })
            .fail((xhr) => {
                let errJSON = xhr && xhr.responseJSON ? xhr.responseJSON : null;
                if (errJSON) {
                    console.error(errJSON);
                    for (let err in errJSON) {
                        let errList = errJSON[err];
                        if (Array.isArray((errList))) {
                            let htmlInsertList = '';
                            for (let err of errList) { htmlInsertList += `<li>${err}</li>` }
                            let inputField = $(`#id_${err}`);
                            inputField.after(`<ul class="errorlist">${htmlInsertList}</ul>`);
                        }
                    }
                }
            })
            .always(() => {
                progressSpinner.removeClass('is-active');
            })
    }



});