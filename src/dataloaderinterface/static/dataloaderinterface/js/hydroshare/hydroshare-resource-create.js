

$(() => {
    // console.log("Loading hydroshare-resource-create.js");
   const template_url = `${window.location.href}hsr/create/`;
   const hydroshareContainer = $('#hydroshare-settings-container');

   console.log(window.location.href);

   $.get(template_url)
       .done(data => {
           // console.log(data);
           $(hydroshareContainer).html(data);
       })
       .fail(xhr => {
           if (xhr.responseJSON)
               console.error(xhr.responseJSON);
           else
               console.error(xhr.responseText);
       })
});