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

    var infoWindow = new google.maps.InfoWindow({
        content: ''
    });

    markerData.forEach(function(site) {
        var marker = new google.maps.Marker({
            position: { lat: site.latitude, lng: site.longitude },
            map: map
        });

        marker.addListener('click', function() {
            var infoContent = createInfoWindowContent(site);
            infoWindow.setContent(infoContent);
            infoWindow.open(marker.get('map'), marker);
        });

        $('.site[data-site=' + site.id + '] .view-on-map').on('click', { 'site-data': site, 'marker': marker, 'info-window': infoWindow }, function(event) {
            var data = event.data['site-data'];
            map.setCenter({ lat: data.latitude, lng: data.longitude });
            map.setZoom(16);

            var infoContent = createInfoWindowContent(data);
            event.data['info-window'].setContent(infoContent);
            event.data['info-window'].open(marker.get('map'), marker);
        });
    });
}

function createInfoWindowContent(siteInfo) {
    var contentElement = $('<div></div>').append($('#site-marker-content').html());
    var fields = contentElement.find('.site-field');
    fields.each(function(index, element) {
        var field = $(element).data('field');
        $(element).find('.site-data').text(siteInfo[field]);
    });
    contentElement.find('.site-link a').attr('href', siteInfo.detail_link);

    return $('<div></div>').append(contentElement.html()).html();
}

$(document).ready(function() {
    $('nav .menu-sites-list').addClass('active');

});