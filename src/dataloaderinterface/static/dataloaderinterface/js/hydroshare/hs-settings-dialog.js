/**
* hs-settings-dialog.js
* @description Initializes the hydroshare settings modal for presentation on 'site_details.html'.
*/

function initializeHydroShareSettingsDialog() {

    const dialog = $('dialog#hydroshare-settings-dialog')[0];
    const showDialogButton = $('#show-hydroshare-settings-dialog')[0];
    const hydroshareSettingsForm = $('#hydroshare-settings-form')[0];
    const scheduledCB = $('input#id_schedule_type_0')[0];
    const manualCB = $('input#id_schedule_type_1')[0];
    const updateFreqSelect = $('select#id_update_freq')[0];

    if (!showDialogButton) {
        // If showDialogButton is undefined, return immediately and do not register dialog.
        // This most likely happens when the hydroshare resource was not found because
        // the user deleted the resource in hydroshare.org.
        return;
    }

    if (!dialog.showModal) {
        dialogPolyfill.registerDialog(dialog);
    }

    showDialogButton.addEventListener('click', () => {
        dialog.showModal();
        $('label[for="id_enabled"]').removeClass('is-focused');
        toggleUpdateFreqSelect(!!$(manualCB).attr('checked'))
    });

    dialog.querySelector('.close').addEventListener('click', () => {
        dialog.close();
    });

    hydroshareSettingsForm.addEventListener('submit', (e) => {
         e.preventDefault();
         submitForm();
    });

    $(manualCB).change(toggleUpdateFreqSelect);
    $(scheduledCB).change(toggleUpdateFreqSelect);

    /**
     * toggleUpdateFreqSelect
     * @description: Shows the "update frequency" select element when the selected update type is "scheduled".
     * Otherwise hides the "update frequency" select element when the selected upate type is "manual".
     */
    function toggleUpdateFreqSelect(e) {
        const hide = typeof e === 'boolean' ? e : e.target.value.toLowerCase() == 'manual';
        $(updateFreqSelect).attr('hidden', hide);
    }

    function submitForm() {
        let submitButton = $(hydroshareSettingsForm).find('input[type=submit]');
        $(submitButton).prop('disabled', true);

        let cancelButton = $(hydroshareSettingsForm).find('button.close');
        $(cancelButton).prop('disabled', true);

        let inputField = $(hydroshareSettingsForm).find('input[type=submit]')[0];

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
            }).fail((xhr) => {
                let errors = xhr.responseJSON;
                if (errors) {
                    console.error(xhr.responseJSON);
                    for (let [errorName, errorList] of Object.entries(errors)) {
                        if (Array.isArray(errorList)) {
                            let fieldContainer = $(`#id_${errorName}`);
                            let errorContainer = $(fieldContainer).find('ul.errorlist');

                            if (errorContainer.length) {
                                $(errorContainer).html('');
                            } else {
                                $(fieldContainer).prepend(`<ul class="errorlist"></ul>`);
                                errorContainer = $(fieldContainer).find('ul.errorlist');
                            }

                            for (let err of errorList) {
                                $(errorContainer).append(`<li>${err}</li>`);
                            }
                        }
                    }
                } else {
                    console.error(xhr.responseText);
                }
            }).always(() => {
                progressSpinner.removeClass('is-active');
                $(submitButton).prop('disabled', false);
            });

        componentHandler.upgradeElement(progressSpinner[0]); // upgradeElement to fix issue where spinner doesn't render
    }
}
