'use strict';

const resource_template_url = `${window.location.href}hsr/update/`;
const hydroshareContainer = $('#hydroshare-settings-container');

// makes a GET request to fetch HTML for hydroshare settings modal
$(hydroshareContainer).load(resource_template_url, () => {
    const updateNowButton = $('button#update-now-button');
    const hydroshareSettingsForm = $('#hydroshare-settings-form');
    const hydroshareError = $('p#hydroshare-error');

    initializeHydroShareSettingsDialog(); // called from `hydroshare-settings-modal.js`
    initializeHydroShareDeleteDialog(); // called from `hydroshare-delete-resource.js`

    $(updateNowButton).click((e) => {
        $(updateNowButton).prop('disabled', true);
        $('p#hydroshare-error').text('');
        console.log(hydroshareError);
        const url = `${hydroshareSettingsForm[0].baseURI}hsr/update/`;
        const serializedForm = $(hydroshareSettingsForm).serialize();

        let progressSpinner = $('#hydroshare-progress-spinner');
        progressSpinner.addClass('is-active');

        // make POST request to upload site data files to hydroshare resource.
        $.post(url, `${serializedForm}&update_files=true`)
            .done((data) => {
                console.log(data);
                if (data.redirect) {
                    window.location.href = data.redirect;
                }
            })
            .fail((xhr) => {
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    $(hydroshareError).text(xhr.responseJSON.error);
                } else {
                    console.error("ERROR: ", xhr);
                    $(hydroshareError).text(xhr.statusText);
                }

            })
            .always(() => {
                progressSpinner.removeClass('is-active');
                $(updateNowButton).prop('disabled', false);
            });
    });
});
