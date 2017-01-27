$(document).ready(function () {
    var dialog = document.querySelector('#data-table-dialog');
    if (!dialog.showModal) {
        dialogPolyfill.registerDialog(dialog);
    }

    $(".table-trigger").click(function(){
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
    var sitePosition = { lat: latitude, lng: longitude };

    var map = new google.maps.Map(document.getElementById('map'), {
        center: sitePosition,
        scrollwheel: false,
        zoom: defaultZoomLevel,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    });

    var marker = new google.maps.Marker({
        position: sitePosition,
        map: map
    });
}

function plotValues(result_id, values) {
    var plotBox = $('div.plot_box[data-result-id="' + result_id + '"] div.graph-container');

    var margin = {top: 0, right: 0, bottom: 0, left: 0};
    var width = plotBox.width() - margin.left - margin.right;
    var height = plotBox.height() - margin.top - margin.bottom;

    var xAxis = d3.scaleTime().range([0, width]);
    var yAxis = d3.scaleLinear().range([height, 0]);

    xAxis.domain(d3.extent(values, function (d) {
        return d.index;
    }));
    yAxis.domain(d3.extent(values, function (d) {
        return parseFloat(d.value);
    }));

    var line = d3.line()
        .x(function(d) {
            return xAxis(d.index);
        })
        .y(function(d) {
            return yAxis(d.value);
        });
    var svg = d3.select(plotBox.get(0)).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    svg.append("path").data([values]).attr("class", "line").attr("d", line);
}

function drawSparklinePlots(tableData) {
    $('div.graph-container').empty();
    for (var index = 0; index < tableData.length; index++) {
        plotValues(tableData[index]['id'], tableData[index]['data']);
    }
}

function initializeTable(table) {
    return table.dataTable({
        info: false,
        ordering: true,
        paging: false,
        searching: false,
        scrollY: '700',
        scrollCollapse: true
    });
}

$(document).ready(function() {
    $('nav .menu-sites-list').addClass('active');
    
    var resizeTimer;
    var tablesData = [];
    var plotBoxes = $('div.plot_box');

    var tables = initializeTable($('table.data-values'));

    for (var index = 0; index < tables.length; index++) {
        var table = $(tables.get(index));
        tablesData[index] = {
            table: table,
            id: table.data('result-id'),
            data: tables.api().table(index).data().map(function(data, index) {
                return { index: index, value: data[1] }
            })
        }
    }
    tables.api().destroy();

    $(window).on('resize', function(event) {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(function() {
          drawSparklinePlots(tablesData);
      }, 500);
    });

    drawSparklinePlots(tablesData);
    plotBoxes.first().trigger('click');
});
