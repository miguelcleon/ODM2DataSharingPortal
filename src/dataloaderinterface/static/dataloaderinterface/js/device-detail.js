const EXTENT_HOURS = 72;
const GAP_HOURS = 6;
const STALE_DATA_CUTOFF = new Date(new Date() - 1000 * 60 * 60 * EXTENT_HOURS);

function initMap() {
    var defaultZoomLevel = 18;
    var latitude = parseFloat($('#site-latitude').val());
    var longitude = parseFloat($('#site-longitude').val());
    var sitePosition = {lat: latitude, lng: longitude};

    var map = new google.maps.Map(document.getElementById('map'), {
        center: sitePosition,
        gestureHandling: 'greedy',
        zoom: defaultZoomLevel,
        mapTypeId: google.maps.MapTypeId.SATELLITE
    });

    var marker = new google.maps.Marker({
        position: sitePosition,
        map: map
    });
}

// Makes all site cards have the same height.
function fixViewPort() {
    var cards = $('.plot_box');

    var maxHeight = 0;
    for (var i = 0; i < cards.length; i++) {
        maxHeight = Math.max($(cards[i]).height(), maxHeight);
    }

    // set to new max height
    for (var i = 0; i < cards.length; i++) {
        $(cards[i]).height(maxHeight);
    }
}

function bindDeleteDialogEvents() {
    var deleteDialog = document.querySelector('#site-delete-dialog');
    var deleteButton = document.querySelector('#btn-delete-site');

    if (!deleteButton) {
        return;
    }

    if (!deleteDialog.showModal) {
        dialogPolyfill.registerDialog(deleteDialog);
    }

    deleteButton.addEventListener('click', function () {
        deleteDialog.showModal();
    });

    deleteDialog.querySelector('.dialog-close').addEventListener('click', function () {
        deleteDialog.close();
    });

    deleteDialog.querySelector('.confirm-delete').addEventListener('click', function () {
        deleteDialog.close();
    });
}

// Returns the most recent 72 hours since the last reading
function getRecentData(timeSeriesData) {
    var lastRead = Math.max.apply(Math, timeSeriesData.map(function(value){
        return new Date(value.DateTime);
    }));

    var dataTimeOffset = new Date(lastRead - 1000 * 60 * 60 * EXTENT_HOURS);
    return timeSeriesData.filter(function (value) {
        return (new Date(value.DateTime)) >= dataTimeOffset;
    });
}

function fillValueTable(table, data) {
    var rows = data.map(function (dataValue) {
        return "<tr><td class='mdl-data-table__cell--non-numeric'>" + dataValue.DateTime + "</td><td class='mdl-data-table__cell--non-numeric'>" + dataValue.TimeOffset + "</td><td>" + dataValue.Value + "</td></tr>";
    });
    table.append($(rows.join('')));
}

function drawSparklineOnResize(seriesInfo, seriesData) {
    var resizeTimer;
    window.addEventListener('resize', function (event) {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function () {
            drawSparklinePlot(seriesInfo, seriesData);
        }, 500);
    });
}

function drawSparklinePlot(seriesInfo, seriesData) {
    var card = $('div.plot_box[data-result-id="' + seriesInfo['resultId'] + '"]');
    var plotBox = card.find(".graph-container");
    var $lastObservation = card.find(".last-observation");

    plotBox.empty();

    var margin = {top: 5, right: 1, bottom: 5, left: 1};
    var width = plotBox.width() - margin.left - margin.right;
    var height = plotBox.height() - margin.top - margin.bottom;

    if (seriesData.length === 0) {
        card.find(".table-trigger").toggleClass("disabled", true);
        card.find(".download-trigger").toggleClass("disabled", true);

        // Append message when there is no data
        d3.select(plotBox.get(0)).append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("text")
                .text("No data exist for this variable.")
                .attr("font-size", "12px")
                .attr("fill", "#AAA")
                .attr("text-anchor", "left")
                .attr("transform", "translate(" + (margin.left + 10) + "," + (margin.top + 20) + ")");
        return;
    }

    card.find(".last-obs-container").css("visibility", "visible");

    $('.plot_box[data-result-id=' + seriesInfo['resultId'] + ' ]').find('.latest-value').text(seriesData[seriesData.length - 1].Value);

    var lastRead = Math.max.apply(Math, seriesData.map(function(value){
        return new Date(value.DateTime);
    }));

    $lastObservation.text(formatDate(lastRead));

    var dataTimeOffset = new Date(lastRead - 1000 * 60 * 60 * EXTENT_HOURS);

    var xAxis = d3.scaleTime().range([0, width]);
    var yAxis = d3.scaleLinear().range([height, 0]);

    xAxis.domain([dataTimeOffset, lastRead]);
    yAxis.domain(d3.extent(seriesData, function(d) {
        return parseInt(d.Value);
    }));

    var line = d3.line()
        .x(function(d) {
            var date = new Date(d.DateTime);
            return xAxis(date);
        })
        .y(function(d) {
            return yAxis(d.Value);
        });

    var svg = d3.select(plotBox.get(0)).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("class", function() {
            if (lastRead <= STALE_DATA_CUTOFF) {
                return "stale";
            }

            return "not-stale";
        })
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // Rendering the paths
    var gapOffset;  // The minimum date required before being considered a gap.
    var previousDate;
    var start = 0;  // Latest start detected after a gap. Initially set to the start of the list.
    var paths = [];

    for (var i = 0; i < seriesData.length; i++) {
        var currentDate = new Date(seriesData[i].DateTime);

        if (previousDate) {
            gapOffset = new Date(currentDate - 1000 * 60 * 60 * GAP_HOURS);
        }

        if (previousDate && previousDate < gapOffset) {
            paths.push(seriesData.slice(start, i - 1));
            start = i;
        }
        previousDate = currentDate;
    }

    if (start > 0) {
        paths.push(seriesData.slice(start, seriesData.length));
    }
    else {
        paths.push(seriesData); // No gaps were detected. Just plot the entire original data.
    }

    // Plot all paths separately to display gaps between them.
    for (var i = 0; i < paths.length; i++) {
        svg.append("path")
            .data([paths[i]])
            .attr("class", "line").attr("d", line)
            .attr("stroke", "steelblue");
    }
}

function getTimeSeriesData(sensorInfo) {
    Papa.parse(sensorInfo['csvPath'], {
        download: true,
        header: true,
        worker: true,
        comments: "#",
        skipEmptyLines: true,
        complete: function (result) {
            if (result.data) {
                var recentValues = getRecentData(result.data);
                fillValueTable($('table.data-values[data-result-id=' + sensorInfo['resultId'] + ']'), result.data);
                drawSparklineOnResize(sensorInfo, recentValues);
                drawSparklinePlot(sensorInfo, recentValues);
            }
        }
    });
}

$(document).ready(function () {
    var dialog = document.querySelector('#data-table-dialog');
    if (!dialog.showModal) {
        dialogPolyfill.registerDialog(dialog);
    }

    $("#btn-follow").on("click", function () {
        $(".follow-status").toggleClass("following");
        var tooltip = $(".mdl-tooltip[data-mdl-for='btn-follow']");
        if (tooltip.text().trim() == "Follow") {
            tooltip.text("Unfollow");
        }
        else {
            tooltip.text("Follow");
        }
    });

    $(".table-trigger").click(function () {
        var box = $(this).parents('.plot_box');
        var id = box.data('result-id');
        var tables = $('table.data-values');
        tables.hide();

        tables.filter('[data-result-id="' + id + '"]').show();
        var title = box.data('variable-name') + ' (' + box.data('variable-code') + ')';
        $(dialog).find('.mdl-dialog__title').text(title);
        $(dialog).find('.mdl-dialog__title').attr("title", title);

        dialog.showModal();
    });

    dialog.querySelector('.dialog-close').addEventListener('click', function () {
        dialog.close();
    });

    $('nav .menu-sites-list').addClass('active');


    var sensors = document.querySelectorAll('.device-data .plot_box');
    for (var index = 0; index < sensors.length; index++) {
        var sensorInfo = sensors[index].dataset;
        getTimeSeriesData(sensorInfo);
    }

    bindDeleteDialogEvents();

    // Executes when page loads
    fixViewPort();

    // Executes each time window size changes
    $(window).resize(
        ResponsiveBootstrapToolkit.changed(function () {
            $('.plot_box').height("initial");   // Reset height
            fixViewPort();
        })
    );
});

function formatDate(date) {
    date = new Date(date);

    var options = {
        year: "numeric", month: "short",
        day: "numeric", hour: "2-digit", minute: "2-digit"
    };

    return date.toLocaleTimeString("en-us", options);
}
