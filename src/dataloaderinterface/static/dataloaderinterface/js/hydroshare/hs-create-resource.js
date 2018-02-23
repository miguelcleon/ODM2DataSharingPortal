

$(() => {
   const template_url = `${window.location.href}hsr/create/`;
   const hydroshareContainer = $('#hydroshare-settings-container');

   $.get(template_url)
       .done(data => {
           $(hydroshareContainer).html(data);
           initializeHydroShareSettingsDialog(); // called from `hydroshare-resource-modal.js`
       })
       .fail(xhr => {
           if (xhr.responseJSON)
               console.error(xhr.responseJSON);
           else
               console.error(xhr.responseText);
       })
});