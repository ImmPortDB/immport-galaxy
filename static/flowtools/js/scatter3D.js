var preprocessScatterData3D = function(text) {
    data = d3.tsv.parseRows(text).map(function(row) {
        return row.map(function(value) {
            if (isNaN(value)) {
                return value;
            }
            return +value;
        });
    });

    scatterData3D['columnHeadings'] = data.shift();
    scatterData3D['columnHeadings'].pop();
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

    scatterData3D['popCol'] = popCol;
    scatterData3D['populations'] = d3.set(p).values();
    scatterData3D['populations'] = scatterData3D['populations']
                                   .map(function(value,index) {
                                     return parseInt(value);
                                   });

    scatterData3D['percent'] = scatterData3D['populations']
                         .map(function(value,index) {
                                     return Math.floor(populations[value] * 10000.0 / data.length) / 100.0;
                                         });

    scatterData3D['data'] = data;
    scatterData3D['m1'] = 0;
    scatterData3D['m2'] = 1;
    scatterData3D['m3'] = 2;
    scatterData3D['view'] = 1;
};

var processScatterData3D = function() {
    var min = d3.min(scatterData3D['data'], function(array) {
      return d3.min(array);
    });
    var max = d3.max(scatterData3D['data'], function(array) {
      return d3.max(array);
    });
    scatterData3D['min'] = 0;
    scatterData3D['max'] = max;

    var col1 = scatterData3D['data'].map(function(value,index) {
               return value[scatterData3D['m1']];});
    var col2 = scatterData3D['data'].map(function(value,index) {
               return value[scatterData3D['m2']];});
    var col3 = scatterData3D['data'].map(function(value,index) {
               return value[scatterData3D['m3']];});
    var pop = scatterData3D['data'].map(function(value,index) {
               return value[scatterData3D['popCol']];});

    var xData = [];
    var yData = [];
    var zData = [];
    var popData = [];
    for (var i = 0; i < col1.length; i++) {
        if (scatterData3D['populations'].indexOf(pop[i]) >= 0) {
            xData.push(col1[i]);
            yData.push(col2[i]);
            zData.push(col3[i]);
            popData.push(pop[i]);
        }
    }

    scatterData3D['popColors'] = popData.map(function(value,index) {
        return color_palette[value];
    });
    scatterData3D['xData'] = xData;
    scatterData3D['yData'] = yData;
    scatterData3D['zData'] = zData;
    scatterData3D['popData'] = popData;
    return scatterData3D;
};


var displayScatterToolbar3D = function() {
    $("#xAxisMarker3D").select2();
    $("#yAxisMarker3D").select2();
    $("#zAxisMarker3D").select2();
    $("#view3D").select2();

    scatterData3D['columnHeadings'].map(function(value,index) {
        $('#xAxisMarker3D')
            .append($("<option></option>")
            .attr("value",index)
            .text(value));

        $('#yAxisMarker3D')
            .append($("<option></option>")
            .attr("value",index)
            .text(value));

        $('#zAxisMarker3D')
            .append($("<option></option>")
            .attr("value",index)
            .text(value));
    });

    $('#xAxisMarker3D').select2("val",0);
    $('#yAxisMarker3D').select2("val",1);
    $('#zAxisMarker3D').select2("val",2);

    $("#xAxisMarker3D").on("change",function(e) {
        var m1 = $("#xAxisMarker3D").select2("val");
        scatterData3D['m1'] = m1;
        scatterDataMFI['m1'] = m1;
    });
    $("#yAxisMarker3D").on("change",function(e) {
        var m2 = $("#yAxisMarker3D").select2("val");
        scatterData3D['m2'] = m2;
        scatterDataMFI['m2'] = m2;
    });
    $("#zAxisMarker3D").on("change",function(e) {
        var m3 = $("#zAxisMarker3D").select2("val");
        scatterData3D['m3'] = m3;
        scatterDataMFI['m3'] = m3;
    });

    $("#view3D").on("change",function(e) {
        var view = $("#view3D").select2("val");
        scatterData3D['view'] = view;
    });


    $("#updateDisplay3D").on("click",function() {
        scatterData3D['populations'] = [];
        scatterDataMFI['populations'] = [];
        $('.pop3D').each(function() {
            if (this.checked) {
                scatterData3D['populations'].push(parseInt(this.value));
                scatterDataMFI['populations'].push(parseInt(this.value));
            }
        });
        processScatterData3D();
        processScatterDataMFI3D();
        displayScatterPlot3D();
    });
};

var displayScatterPopulation3D = function() {
    scatterData3D['populations'].map(function(value,index) {
        $('#populationTable3D tr')
            .last()
            .after('<tr><td align="center"><input type="checkbox" checked class="pop3D" value=' + value + '/></td><td>' + value + '<td><span style="background-color:' + color_palette[value] + '">&nbsp;&nbsp;&nbsp</span></td></td><td>' + scatterData3D['percent'][value - 1] + '<td></tr>');
    });

    $('#selectall3D').click(function() {
        var checkAll = $("#selectall3D").prop('checked');
        if (checkAll) {
            $(".pop3D").prop("checked", true);
        } else {
            $(".pop3D").prop("checked", false);
        }
    });
    $('.pop3D').click(function() {
        if ($('.pop3D').length == $(".pop3D:checked").length) {
            $('#selectall3D').prop("checked",true);
        } else {
            $('#selectall3D').prop("checked",false);
        }
    });

};

var displayScatterPlot3D = function() {
    $("#scatterPlotDiv3D").empty();
    //var iframe = window.parent.document.getElementById('galaxy_main')
    //var iframeHeight = iframe.clientHeight - 200;
    //var iframeWidth = iframe.clientWidth;
    var h = $(window).height() - 200;
    $("#scatterPlotDiv3D").height(h);
    var w = $("#scatterPlotDiv3D").width();


    var xtitle = scatterData3D['columnHeadings'][scatterData3D['m1']];
    var ytitle = scatterData3D['columnHeadings'][scatterData3D['m2']];
    var ztitle = scatterData3D['columnHeadings'][scatterData3D['m3']];
    var view = scatterData3D['view']
    
    var traces = [];
    if ( view == 1 || view == 2 ){
        var trace1 = {
            x: scatterData3D['xData'],
            y: scatterData3D['yData'],
            z: scatterData3D['zData'],
            mode: 'markers',
            opacity: .75,
            hoverinfo: "none",
            marker: { size: 2, color: scatterData3D['popColors'] },
            type: 'scatter3d'
       }
       traces.push(trace1);
    };

    if ( view == 1 || view == 3) {
        var trace2 =
          {
            x: scatterDataMFI['xData'],
            y: scatterDataMFI['yData'],
            z: scatterDataMFI['zData'],
            mode: 'markers',
            opacity: 1.0,
            hoverinfo: "x+y+z",
            marker: { symbol: "circle-open", size: 8, color: scatterDataMFI['popColors'] },
            type: 'scatter3d'
          };
        traces.push(trace2);
    }

    var layout = {
        title: '',
        showlegend: false,
        scene: {
            aspectratio: {
                x: 1,
                y: 1,
                z: 1
            },
            camera: {
                center: {
                    x: 0,
                    y: 0,
                    z: 0
                },
                eye: {
                    x: 1.25,
                    y: 1.25,
                    z: 1.25 
                },
                up: {
                    x: 0,
                    y: 0,
                    z: 1
                }
            },
            xaxis: { type: 'linear',
                     title: xtitle,
                     range: [0,scatterData3D['max']],
                     zeroline: false },
            yaxis: { type: 'linear',
                     title: ytitle,
                     range: [0,scatterData3D['max']],
                     zeroline: false },
            zaxis: { type: 'linear',
                     title: ztitle,
                     range: [0,scatterData3D['max']],
                     zeroline: false }
        }
    };

    Plotly.newPlot('scatterPlotDiv3D',traces,layout);
};
