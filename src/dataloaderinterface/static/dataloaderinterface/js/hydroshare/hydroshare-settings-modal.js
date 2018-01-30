/**
 * hydroshare-settings-modal.js
 * @description Determines how the hydroshare settings modal is presented in 'site_details.html'.
 */

$(() => {
    const dialog = document.querySelector('#hydroshare-settings-dialog');
    const showDialogButton = document.querySelector('#show-hydroshare-settings-dialog');
    const hydroshareSettingsForm = document.querySelector('#hydroshare-settings-form');
    const scheduledCB = document.querySelector('input#id_schedule_type_0');
    const manualCB = document.querySelector('input#id_schedule_type_1');
    const updateFreqSelect = document.querySelector('select#id_update_freq');

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

    manualCB.addEventListener('change', onCBChange);
    scheduledCB.addEventListener('change', onCBChange);
    function onCBChange(e) {
        const shouldHide = $(scheduledCB).closest(`label[for=id_schedule_type_0]`).hasClass('is-checked');
        $(updateFreqSelect).attr('hidden', shouldHide);
    }


    function submitForm() {
        let url = `${hydroshareSettingsForm.baseURI}hydroshare_settings/`;
        let serializedForm = $(hydroshareSettingsForm).serialize();
        let progressSpinner = $(hydroshareSettingsForm).find('#hydroshare-form-spinner');

        progressSpinner.addClass('is-active');

        $.post(url, serializedForm)
            .done(data => {
                if (data.redirect)
                    window.location.href = data.redirect;
                else
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