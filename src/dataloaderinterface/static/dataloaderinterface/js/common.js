// (function() {
//     'use strict';
//
// }());


function updateSitePosition() {

}

function updateSiteElevation() {

}

function initMap() {
    var defaultZoomLevel = 5;
    var defaultPosition = { latitude: -37.0902, longitude: 95.7129 };

    var map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: defaultPosition.latitude, lng: defaultPosition.longitude },
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
            map.setZoom(10)
        }, undefined, { timeout: 5000 });
    }

    map.addListener('click', function(event) {
        var elevationUrl = [
            'https://maps.googleapis.com/maps/api/elevation/json?locations=',
            marker.position, '&key=AIzaSyAiUxiuZaPEPtB4EhAquguz7kNzYU7bnnc'
        ].join('');

        marker.setPosition(event.latLng);
        map.panTo(marker.position);
        $.ajax({
            url: elevationUrl
        }).done(function(data) {
            updateSiteElevation()
        })
    });

}