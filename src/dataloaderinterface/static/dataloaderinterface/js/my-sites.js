/**
 * Created by Juan on 1/24/2017.
 */

function initMap() {
    const DEFAULT_ZOOM = 5;
    const DEFAULT_LATITUDE = 37.0902;
    const DEFAULT_LONGITUDE = -95.7129;
    const DEFAULT_POSITION = { lat: DEFAULT_LATITUDE, lng: DEFAULT_LONGITUDE };

    var markerData = JSON.parse(document.getElementById('sites-data').innerHTML);
    var map = new google.maps.Map(document.getElementById('map'), {
        center: DEFAULT_POSITION,
        zoom: DEFAULT_ZOOM,
        scrollwheel: false,
        disableDefaultUI: true,
        zoomControl: true,
        zoomControlOptions: {
          position: google.maps.ControlPosition.LEFT_BOTTOM
        },
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        scaleControl: true
    });

    markerData.forEach(function(site) {
        var marker = new google.maps.Marker({
            position: { lat: site.latitude, lng: site.longitude },
            map: map
        });

        marker.addListener('click', function() {
            // TODO: whatever happens when you click on a marker.
        })
    });
}
