'use strict';

$(() => {
   const hydroshareSettingsForm = document.querySelector('#hydroshare-settings-form');
   const updateNowButton = $('#update-now-button');

   updateNowButton.click((e) => {
       console.log('clicked');
       const url = `${hydroshareSettingsForm[0].baseURI}hydroshare_settings/`;
       const serializedForm = $(hydroshareSettingsForm).serialize();
       $.post(url, `${serializedForm}&update_resource=true`)
      .done((data) => {
         console.log("DATA: ", data);
      })
      .fail((xhr) => {
          console.error("ERROR: ", xhr.responseJSON);
      })
      .always();
   });

   $(hydroshareSettingsForm).submit((e) => {
       e.preventDefault();
       const url = `${hydroshareSettingsForm[0].baseURI}hydroshare_settings/`;
       console.log(url);
       // const serializedForm = `${updateResourceForm.serialize()}&update_resource=true`;
       const serializedForm = hydroshareSettingsForm.serialize();
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