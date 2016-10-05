// (function() {
//     'use strict';
//
// }());

function updateSitePosition(map, position) {
    map.panTo(position);
    $('input[name="latitude"]').val(position.lat);
    $('input[name="longitude"]').val(position.lng);
}

function updateSiteElevation(position) {
    var elevator = new google.maps.ElevationService();
     elevator.getElevationForLocations({'locations':[position]}, function(results, status) {
          if (status == google.maps.ElevationStatus.OK && results[0]) {
              $('input[name="elevation_m"]').val(results[0].elevation);
          }
     });
}

function initMap() {
    var defaultZoomLevel = 4;
    var defaultPosition = { lat: 37.0902, lng: -95.7129 };

    var map = new google.maps.Map(document.getElementById('map'), {
        center: defaultPosition,
        zoom: defaultZoomLevel,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    });

    var marker = new google.maps.Marker({
        position: undefined,
        map: map
    });

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function getLocation(position){
            map.setCenter({ lat: position.coords.latitude, lng: position.coords.longitude });
            map.setZoom(10);
        }, undefined, { timeout: 5000 });
    }

    map.addListener('click', function(event) {
        marker.setPosition(event.latLng);
        updateSitePosition(map, event.latLng);
        updateSiteElevation(event.latLng);
    });

    $('input[name="latitude"], input[name="longitude"]').on('change', function() {
        var input = $(this);
        var value = parseFloat(input.val());
        if (!value) {
            return;
        }

        var markerPosition = {
            lat: input.prop('name') === 'latitude'? parseFloat(value): marker.getPosition().lat(),
            lng: input.prop('name') === 'longitude'? parseFloat(value): marker.getPosition().lng()
        };

        map.panTo(markerPosition);
        marker.setPosition(markerPosition);
    });
}


function addResult() {
    var newIndex = $('div#formset div.result-form').length;
    $('input[name="form-TOTAL_FORMS"]').val(newIndex + 1);

    var newResultForm = $($('div#results-template').html().replace(new RegExp('__prefix__', 'g'), newIndex));
    newResultForm.insertBefore($('.formset-container .add-result-container'));

    newResultForm.find('span.remove-result').on('click', function() {
        $(this).parents('div.result-form').remove();
    });
}


$(document).ready(function() {
    $('button.new-result-button').on('click', addResult);

    $(document).on("keypress", ":input:not(textarea):not([type=submit])", function(event) {
        if (event.keyCode == 13) {
            event.preventDefault();
        }
    });
});

