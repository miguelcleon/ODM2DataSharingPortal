function initMap() {
    const DEFAULT_ZOOM = 6;
    const DEFAULT_LATITUDE = 37.0902;
    const DEFAULT_LONGITUDE = -95.7129;
    const DEFAULT_POSITION = { lat: DEFAULT_LATITUDE, lng: DEFAULT_LONGITUDE };

    var markerData = JSON.parse(document.getElementById('sites-data').innerHTML);
    var map = new google.maps.Map(document.getElementById('map'), {
        center: DEFAULT_POSITION,
        zoom: DEFAULT_ZOOM,
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
            var contentElement = $('<div></div>').append($('#site-marker-content').html());
            var fields = contentElement.find('.site-field');
            fields.each(function(index, element) {
                var field = $(element).data('field');
                $(element).find('.site-data').text(site[field]);
            });
            contentElement.find('.site-link a').attr('href', site.detail_link);
            
            var infoContent = $('<div></div>').append(contentElement.html()).html();
            infoWindow.setContent(infoContent);
            infoWindow.open(marker.get('map'), marker);
        })
    });
}

$(document).ready(function () {
    $("#wrapper").css("height", "calc(100% - 81px)");
    $(".map-container").css("height", $("#wrapper").height());
    $("body").css("overflow", "hidden")
});

$( window ).resize(function() {
  $(".map-container").css("height", $("#wrapper").height());
    $("body").css("overflow", "hidden")
});
