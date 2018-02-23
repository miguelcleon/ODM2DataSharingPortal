

$(() => {
    // console.log("Loading hs-create-resource.js");
   const template_url = `${window.location.href}hsr/create/`;
   const hydroshareContainer = $('#hydroshare-settings-container');

   console.log(window.location.href);

   $.get(template_url)
       .done(data => {
           $(hydroshareContainer).html(data);

           // called from `hydroshare-resource-modal.js`
           initializeHydroShareSettingsDialog();
       })
       .fail(xhr => {
           if (xhr.responseJSON)
               console.error(xhr.responseJSON);
           else
               console.error(xhr.responseText);
       })
});