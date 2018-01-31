'use strict';

$(() => {
    // console.log("Loading hydroshare-resource-update.js");
    const resource_template_url = `${window.location.href}hsr/update/`;
    const hydroshareContainer = $('#hydroshare-settings-container');
    let updateNowButton = $('button#update-now-button');
    let hydroshareSettingsForm = $('#hydroshare-settings-form');

    console.log(updateNowButton);

    $.get(resource_template_url)
        .done(data => {
            // console.log(data);
            // console.log('template loaded.');
            $(hydroshareContainer).html(data);
            hydroshareSettingsForm = $('#hydroshare-settings-form');
            $('button#update-now-button').click((e) => {
                const url = `${hydroshareSettingsForm[0].baseURI}hsr/update/`;
                const serializedForm = $(hydroshareSettingsForm).serialize();

                let progressSpinner = $('#hydroshare-progress-spinner');
                progressSpinner.addClass('is-active');

                $.post(url, `${serializedForm}&update_files=true`)
                    .done((data) => {
                        console.log(data);
                        if (data.redirect) {
                            window.location.href = data.redirect;
                        }
                    })
                    .fail((xhr) => {
                        console.error("ERROR: ", xhr.responseJSON);
                    })
                    .always(() => {
                        progressSpinner.removeClass('is-active');
                    });
            });
        })
        .fail(xhr => {
            if (xhr.responseJSON)
                console.error(xhr.responseJSON);
            else
                console.error(xhr.responseText);
        });

    $(hydroshareSettingsForm).submit((e) => {
        e.preventDefault();
        // const url = `${hydroshareSettingsForm[0].baseURI}hydroshare_resource/`;
        // console.log(url);
        // const serializedForm = `${updateResourceForm.serialize()}&update_resource=true`;
        // const serializedForm = hydroshareSettingsForm.serialize();
        //  const csrftoken = serializedForm.split(/=/).splice(1, 1).pop();
        //  console.log(csrftoken);
        // $.post(url, {
        //     csrfmiddlewaretoken: csrftoken,
        //     update_resource: true
        // })
        // .done((data) => {
        //    console.log("DATA: ", data);
        // })
        // .fail((xhr) => {
        //     console.error("ERROR: ", xhr.responseJSON);
        // })
        // .always();
    });


});