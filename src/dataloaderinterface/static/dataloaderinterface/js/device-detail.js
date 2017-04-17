$(document).ready(function () {
    var dialog = document.querySelector('#data-table-dialog');
    if (!dialog.showModal) {
        dialogPolyfill.registerDialog(dialog);
    }

    $(".table-trigger").click(function () {
        var box = $(this).parents('.plot_box');
        var id = box.data('result-id');
        var tables = $('table.data-values');
        tables.hide();

        tables.filter('[data-result-id="' + id + '"]').show();
        $(dialog).find('.mdl-dialog__title').text(box.data('variable-name') + ' (' + box.data('variable-code') + ')');

        dialog.showModal();
    });

    dialog.querySelector('.dialog-close').addEventListener('click', function () {
        dialog.close();
    });
});

function initMap() {
    var defaultZoomLevel = 18;
    var latitude = parseFloat($('#site-latitude').val());
    var longitude = parseFloat($('#site-longitude').val());
    var sitePosition = {lat: latitude, lng: longitude};

    var map = new google.maps.Map(document.getElementById('map'), {
        center: sitePosition,
        scrollwheel: false,
        zoom: defaultZoomLevel,
        mapTypeId: google.maps.MapTypeId.SATELLITE
    });

    var marker = new google.maps.Marker({
        position: sitePosition,
        map: map
    });
}

function plotValues(result_id, values) {
    var plotBox = $('div.plot_box[data-result-id="' + result_id + '"] div.graph-container');

    var margin = {top: 5, right: 1, bottom: 5, left: 1};
    var width = plotBox.width() - margin.left - margin.right;
    var height = plotBox.height() - margin.top - margin.bottom;

    var xAxis = d3.scaleTime().range([0, width]);
    var yAxis = d3.scaleLinear().range([height, 0]);

    xAxis.domain(d3.extent(values, function (d) {
        return d.index;
    }));
    yAxis.domain(d3.extent(values, function (d) {
        return d.value;
    }));

    var line = d3.line()
        .x(function (d) {
            return xAxis(d.index);
        })
        .y(function (d) {
            return yAxis(d.value);
        });
    var svg = d3.select(plotBox.get(0)).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    svg.append("path").data([values]).attr("class", "line").attr("d", line);
}

function drawSparklinePlots(timeSeriesData) {
    $('div.graph-container').empty();
    for (var index = 0; index < timeSeriesData.length; index++) {
        var timeSeries = timeSeriesData[index];
        var dataValues = timeSeries['values'];
        if (dataValues.length === 0) {
            continue;
        }

        $('.plot_box[data-result-id=' + timeSeries.id + ' ]').find('.latest-value').text(dataValues[dataValues.length - 1].value);

        plotValues(timeSeries['id'], timeSeries['values']);
    }
}

function fillValueTables(tables, data) {
    for (var index = 0; index < data.length; index++) {
        var result = data[index];
        var table = tables.filter('[data-result-id=' + result.id + ' ]');
        var rows = result['values'].map(function (dataValue) {
            return $("<tr><td class='mdl-data-table__cell--non-numeric'>" + dataValue.timestamp + "</td><td class='mdl-data-table__cell--non-numeric'>" + dataValue.timestamp_utc_offset + "</td><td>" + dataValue.value + "</td></tr>");
        });
        table.append(rows);
    }
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

    deleteButton.addEventListener('click', function() {
      deleteDialog.showModal();
    });

    deleteDialog.querySelector('.dialog-close').addEventListener('click', function() {
      deleteDialog.close();
    });

    deleteDialog.querySelector('.confirm-delete').addEventListener('click', function() {
      deleteDialog.close();
    });
}

$(document).ready(function () {
    $('nav .menu-sites-list').addClass('active');

    var resizeTimer;
    var timeSeriesData = JSON.parse(document.getElementById('sensors-data').innerHTML);
    fillValueTables($('table.data-values'), timeSeriesData);
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

    $(window).on('resize', function (event) {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function () {
            drawSparklinePlots(timeSeriesData);
        }, 500);
    });

    drawSparklinePlots(timeSeriesData);
});
