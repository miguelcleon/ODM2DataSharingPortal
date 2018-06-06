function updateSitePosition(map, position) {
    map.panTo(position);
    $('input[name="latitude"]').val(Math.round(position.lat() * 100000) / 100000).trigger('keypress');
    $('input[name="longitude"]').val(Math.round(position.lng() * 100000) / 100000).trigger('keypress');
}

function updateSiteElevation(position) {
    var elevator = new google.maps.ElevationService();
    elevator.getElevationForLocations({'locations': [position]}, function (results, status) {
        if (status == google.maps.ElevationStatus.OK && results[0]) {
            $('input[name="elevation_m"]').val(Math.round(results[0].elevation)).trigger('keypress');
        }
    });
}

function initMap() {
    const DEFAULT_ZOOM = 4;
    const DEFAULT_SPECIFIC_ZOOM = 10;
    const DEFAULT_LATITUDE = 37.0902;
    const DEFAULT_LONGITUDE = -95.7129;
    var mapPosition = { lat: parseFloat($('input[name="latitude"]').val()), lng: parseFloat($('input[name="longitude"]').val()) };
    var isCompletePosition = mapPosition.lat && mapPosition.lng;
    var mapZoom = parseInt($('input[name="zoom-level"]').val());

    var map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: mapPosition.lat || DEFAULT_LATITUDE, lng: mapPosition.lng || DEFAULT_LONGITUDE },
        zoom: mapZoom || DEFAULT_ZOOM,
        mapTypeId: google.maps.MapTypeId.HYBRID,
        gestureHandling: 'greedy',
        draggableCursor: 'pointer',
        zoomControl: true,
        zoomControlOptions: {
          position: google.maps.ControlPosition.LEFT_BOTTOM
        },
        scaleControl: true
    });

    var marker = new google.maps.Marker({
        position: (mapPosition.lat && mapPosition.lng)? mapPosition: undefined,
        map: map
    });

    if (navigator.geolocation && !isCompletePosition) {
        navigator.geolocation.getCurrentPosition(function getLocation(locatedPosition) {
            map.setCenter({ lat: locatedPosition.coords.latitude, lng: locatedPosition.coords.longitude });
            map.setZoom(DEFAULT_SPECIFIC_ZOOM);
        }, undefined, { timeout: 5000 });
    }

    map.addListener('click', function(event) {
        marker.setPosition(event.latLng);
        updateSitePosition(map, event.latLng);
        updateSiteElevation(event.latLng);
    });
    
    map.addListener('zoom_changed', function() {
        $('input[name="zoom-level"]').val(map.getZoom());
    });

    $('input[name="latitude"], input[name="longitude"]').on('change', function() {
        var coordinates = {
            lat: parseFloat($('input[name="latitude"]').val()),
            lng: parseFloat($('input[name="longitude"]').val())
        };

        if (!coordinates.lat || !coordinates.lng) {
            return;
        }

        map.panTo(coordinates);
        marker.setPosition(coordinates);
    });
}

function notifyInputStatus() {
    if (!$("#id_notify").prop("checked")) {
        $("#id_hours_threshold").removeAttr("name");
        $("#id_hours_threshold").removeAttr("required");
    }
    else {
        $("#id_hours_threshold").attr("name", "hours_threshold");
        $("#id_hours_threshold").attr("required", true);
    }
}

$(document).ready(function() {
    $('nav .menu-register-site').addClass('active');

    $("#id_notify").change(function() {
        $("div[data-field='hours_threshold']").toggleClass("hidden", !this.checked);
        notifyInputStatus();
    });
});
