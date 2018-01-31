/**
 * hydroshare-settings-modal.js
 * @description Determines how the hydroshare settings modal is presented in 'site_details.html'.
 */

$(() => {
    setTimeout(() => {

        console.log("Loading hydroshare-settings-modal.js");

        const dialog = $('#hydroshare-settings-dialog')[0];
        const showDialogButton = $('#show-hydroshare-settings-dialog')[0];
        const hydroshareSettingsForm = $('#hydroshare-settings-form')[0];
        const scheduledCB = $('input#id_schedule_type_0')[0];
        const manualCB = $('input#id_schedule_type_1')[0];
        const updateFreqSelect = $('select#id_update_freq')[0];

        if (!dialog.showModal) {
            console.log("registering dialog");
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

        // dialog.showModal();

        $(manualCB).change(onCBChange);
        $(scheduledCB).change(onCBChange);
        function onCBChange(e) {
            const shouldHide = $(scheduledCB).closest(`label[for=id_schedule_type_0]`).hasClass('is-checked');
            $(updateFreqSelect).attr('hidden', shouldHide);
        }


        function submitForm() {
            const inputField = $(hydroshareSettingsForm).find('input[type=submit]')[0];

            let method = '';
            if (inputField.id === 'create-resource') {
                method = 'create';
            } else if (inputField.id === 'update-resource') {
                method = 'update';
            }

            let url = `${hydroshareSettingsForm.baseURI}hsr/${method}/`;
            let serializedForm = $(hydroshareSettingsForm).serialize();
            let progressSpinner = $(hydroshareSettingsForm).find('#hydroshare-progress-spinner');

            progressSpinner.addClass('is-active');

            $.post(url, serializedForm)
                .done(data => {
                    console.log(data);
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
                    } else {
                        console.error(xhr.responseText);
                    }
                })
                .always(() => {
                    progressSpinner.removeClass('is-active');
                })
        }
    }, 0);



});