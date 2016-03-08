var preprocessScatterData2D = function(text) {
    var data = d3.tsv.parseRows(text).map(function(row) {
        return row.map(function(value) {
            if (isNaN(value)) {
                return value;
            }
            return +value;
        });
    });

    scatterData2D['columnHeadings'] = data.shift();
    scatterData2D['columnHeadings'].pop();
    var popCol = data[0].length - 1;
    var p = data.map(function(value,index) {
        return parseInt(value[popCol]);
    });

    var populations = {};
    for (var i = 0; i < p.length; i++) {
        if (populations[p[i]] === undefined) {
            populations[p[i]] = 1;
        } else {
            populations[p[i]] = populations[p[i]] + 1;
        }
    }

    scatterData2D['popCol'] = popCol;
    scatterData2D['populations'] = d3.set(p).values();
    scatterData2D['populations'] = scatterData2D['populations']
                                   .map(function(value,index) {
                                     return parseInt(value);
                                   });

    scatterData2D['percent'] = scatterData2D['populations']
                         .map(function(value,index) {
                                     return Math.floor(populations[value] * 10000.0 / data.length) / 100.0;
                                         });

    scatterData2D['data'] = data;
    scatterData2D['m1'] = 0;
    scatterData2D['m2'] = 1;
    scatterData2D['view'] = 1;
};

var processScatterData2D = function() {
    var min = d3.min(scatterData2D['data'], function(array) {
      return d3.min(array);
    });
    var max = d3.max(scatterData2D['data'], function(array) {
      return d3.max(array);
    });
    scatterData2D['min'] = 0;
    scatterData2D['max'] = max;

    var col1 = scatterData2D['data'].map(function(value,index) {
               return value[scatterData2D['m1']];});
    var col2 = scatterData2D['data'].map(function(value,index) {
               return value[scatterData2D['m2']];});
    var pop = scatterData2D['data'].map(function(value,index) {
               return value[scatterData2D['popCol']];});

    var xData = [];
    var yData = [];
    var popData = [];
    for (var i = 0; i < col1.length; i++) {
        if (scatterData2D['populations'].indexOf(pop[i]) >= 0) {
            xData.push(col1[i]);
            yData.push(col2[i]);
            popData.push(pop[i]);
        }
    }

    scatterData2D['popColors'] = popData.map(function(value,index) {
        return color_palette[value];
    });
    scatterData2D['xData'] = xData;
    scatterData2D['yData'] = yData;
    scatterData2D['popData'] = popData;
    return scatterData2D;
};


var displayScatterToolbar2D = function() {
    $("#xAxisMarker2D").select2();
    $("#yAxisMarker2D").select2();
    $("#view2D").select2();

    scatterData2D['columnHeadings'].map(function(value,index) {
        $('#xAxisMarker2D')
            .append($("<option></option>")
            .attr("value",index)
            .text(value));

        $('#yAxisMarker2D')
            .append($("<option></option>")
            .attr("value",index)
            .text(value));

    });

    $('#xAxisMarker2D').select2("val",0);
    $('#yAxisMarker2D').select2("val",1);

    $("#xAxisMarker2D").on("change",function(e) {
        var m1 = $("#xAxisMarker2D").select2("val");
        scatterData2D['m1'] = m1;
        scatterDataMFI['m1'] = m1;
    });
    $("#yAxisMarker2D").on("change",function(e) {
        var m2 = $("#yAxisMarker2D").select2("val");
        scatterData2D['m2'] = m2;
        scatterDataMFI['m2'] = m2;
    });
    $("#view2D").on("change",function(e) {
        var view = $("#view2D").select2("val");
        scatterData2D['view'] = view;
    });

    $("#updateDisplay2D").on("click",function() {
        scatterData2D['populations'] = [];
        scatterDataMFI['populations'] = [];
        $('.pop2D').each(function() {
            if (this.checked) {
                scatterData2D['populations'].push(parseInt(this.value));
                scatterDataMFI['populations'].push(parseInt(this.value));
            }
        });
        processScatterData2D();
        processScatterDataMFI2D();
        displayScatterPlot2D();
    });
};

var displayScatterPopulation2D = function() {
    scatterData2D['populations'].map(function(value,index) {
        $('#populationTable2D tr')
            .last()
            .after('<tr><td align="center"><input type="checkbox" checked class="pop2D" value=' + value + '/></td><td>' + value + '<td><span style="background-color:' + color_palette[value] + '">&nbsp;&nbsp;&nbsp</span></td></td><td>' + scatterData2D['percent'][value - 1] + '<td></tr>');
    });

    $('#selectall2D').click(function() {
        var checkAll = $("#selectall2D").prop('checked');
        if (checkAll) {
            $(".pop2D").prop("checked", true);
        } else {
            $(".pop2D").prop("checked", false);
        }
    });
    $('.pop2D').click(function() {
        if ($('.pop2D').length == $(".pop2D:checked").length) {
            $('#selectall2D').prop("checked",true);
        } else {
            $('#selectall2D').prop("checked",false);
        }
    });

};

var displayScatterPlot2D = function() {
    $("#scatterPlotDiv2D").empty();
    //var iframe = window.parent.document.getElementById('galaxy_main')
    //var iframeHeight = iframe.clientHeight - 200;
    //var iframeWidth = iframe.clientWidth;
    var h = $(window).height() - 200;
    $("#scatterPlotDiv2D").height(h);
    var w = $("#scatterPlotDiv2D").width();


    var xtitle = scatterData2D['columnHeadings'][scatterData2D['m1']];
    var ytitle = scatterData2D['columnHeadings'][scatterData2D['m2']];
    var view = scatterData2D['view']

    var traces = [];
    if ( view == 1 || view == 2) {
        var trace1 = 
          {
            x: scatterData2D['xData'],
            y: scatterData2D['yData'],
            mode: 'markers',
            opacity: .75,
            hoverinfo: "none",
            marker: { size: 2, color: scatterData2D['popColors'] },
            type: 'scatter'
          };
          traces.push(trace1);
    }

    if ( view == 1 || view == 3) {
        var trace2 = 
          {
            x: scatterDataMFI['xData'],
            y: scatterDataMFI['yData'],
            mode: 'markers',
            opacity: 1.0,
            hoverinfo: "x+y",
            marker: { symbol: 128, size: 8, color: scatterDataMFI['popColors'] },
            type: 'scatter'
          };
        traces.push(trace2);
    }

    var layout = {
        title: '',
        showlegend: false,
        xaxis: {
            range: [0,scatterData2D['max']],
            title: xtitle
        },
        yaxis: {
            range: [0,scatterData2D['max']],
            title: ytitle
        },
    };

    Plotly.newPlot('scatterPlotDiv2D',traces,layout);
};