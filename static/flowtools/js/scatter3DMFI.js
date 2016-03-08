var preprocessScatterData3DMFI = function(text) {
    data = d3.tsv.parseRows(text).map(function(row) {
        return row.map(function(value) {
            if (isNaN(value)) {
                return value;
            }
            return +value;
        });
    });

    // Get the Headings Row, then remove the Count, Percentage and
    // Population headings
    scatterData3DMFI['columnHeadings'] = data.shift();
    scatterData3DMFI['columnHeadings'].pop();
    scatterData3DMFI['columnHeadings'].pop();
    scatterData3DMFI['columnHeadings'].pop();

    var popCol = data[0].length -1;
    var pop = data.map(function(value,index) {
        return parseInt(value[popCol]);
    });

    var perCol = data[0].length -2;
    var per = data.map(function(value,index) {
        return parseFloat(value[perCol]);
    });

    var countCol = data[0].length -3;
    var count = data.map(function(value,index) {
        return parseInt(value[countCol]);
    });

    scatterData3DMFI['popCol'] = popCol;
    scatterData3DMFI['populations'] = pop;
    scatterData3DMFI['percent'] = per;
    scatterData3DMFI['counts'] = count;

    var l = data[0].length;
    scatterData3DMFI['data'] = data.map(function(row) {
        return row.splice(0,countCol);
    });
    scatterData3DMFI['poplist'] = pop;

    scatterData3DMFI['m1'] = 0;
    scatterData3DMFI['m2'] = 1;
    scatterData3DMFI['m3'] = 2;
};

var processScatterData3DMFI = function() {
    var min = d3.min(scatterData3DMFI['data'], function(array) {
      return d3.min(array);
    });
    var max = d3.max(scatterData3DMFI['data'], function(array) {
      return d3.max(array);
    });
    scatterData3DMFI['min'] = 0;
    scatterData3DMFI['max'] = max;

    console.log("MAX: ",max);

    var col1 = scatterData3DMFI['data'].map(function(value,index) {
               return value[scatterData3DMFI['m1']];});
    var col2 = scatterData3DMFI['data'].map(function(value,index) {
               return value[scatterData3DMFI['m2']];});
    var col3 = scatterData3DMFI['data'].map(function(value,index) {
               return value[scatterData3DMFI['m3']];});
    var pop = scatterData3DMFI['poplist'];

    var xData = [];
    var yData = [];
    var zData = [];
    var popData = [];
    for (var i = 0; i < col1.length; i++) {
        if (scatterData3DMFI['populations'].indexOf(pop[i]) >= 0) {
            xData.push(col1[i]);
            yData.push(col2[i]);
            zData.push(col3[i]);
            popData.push(pop[i]);
        }
    }

    scatterData3DMFI['popColors'] = popData.map(function(value,index) {
        return color_palette[value];
    });
    scatterData3DMFI['xData'] = xData;
    scatterData3DMFI['yData'] = yData;
    scatterData3DMFI['zData'] = zData;
    scatterData3DMFI['popData'] = popData;
    return scatterData3DMFI;
};


var displayScatterToolbar3DMFI = function() {
    $("#xAxisMarker3DMFI").select2();
    $("#yAxisMarker3DMFI").select2();
    $("#zAxisMarker3DMFI").select2();

    scatterData3DMFI['columnHeadings'].map(function(value,index) {
        $('#xAxisMarker3DMFI')
            .append($("<option></option>")
            .attr("value",index)
            .text(value));

        $('#yAxisMarker3DMFI')
            .append($("<option></option>")
            .attr("value",index)
            .text(value));

        $('#zAxisMarker3DMFI')
            .append($("<option></option>")
            .attr("value",index)
            .text(value));
    });

    $('#xAxisMarker3DMFI').select2("val",0);
    $('#yAxisMarker3DMFI').select2("val",1);
    $('#zAxisMarker3DMFI').select2("val",2);

    $("#xAxisMarker3DMFI").on("change",function(e) {
        var m1 = $("#xAxisMarker3DMFI").select2("val");
        scatterData3DMFI['m1'] = m1;
    });
    $("#yAxisMarker3DMFI").on("change",function(e) {
        var m2 = $("#yAxisMarker3DMFI").select2("val");
        scatterData3DMFI['m2'] = m2;
    });
    $("#zAxisMarker3DMFI").on("change",function(e) {
        var m3 = $("#zAxisMarker3DMFI").select2("val");
        scatterData3DMFI['m3'] = m3;
    });

    $("#updateDisplay3DMFI").on("click",function() {
        scatterData3DMFI['populations'] = [];
        $('.pop3DMFI').each(function() {
            if (this.checked) {
                scatterData3DMFI['populations'].push(parseInt(this.value));
            }
        });
        processScatterData3DMFI();
        displayScatterPlot3DMFI();
    });
};

var displayScatterPopulation3DMFI = function() {
    scatterData3DMFI['populations'].map(function(value,index) {
        $('#populationTable3DMFI tr')
            .last()
            .after('<tr><td align="center"><input type="checkbox" checked class="pop3DMFI" value=' + value + '/></td><td>' + value + '<td><span style="background-color:' + color_palette[value] + '">&nbsp;&nbsp;&nbsp</span></td></td><td>' + scatterData3DMFI['percent'][value - 1] + '<td></tr>');
    });

    $('#selectall3DMFI').click(function() {
        var checkAll = $("#selectall3DMFI").prop('checked');
        if (checkAll) {
            $(".pop3DMFI").prop("checked", true);
        } else {
            $(".pop3DMFI").prop("checked", false);
        }
    });
    $('.pop3DMFI').click(function() {
        if ($('.pop3DMFI').length == $(".pop3DMFI:checked").length) {
            $('#selectall3DMFI').prop("checked",true);
        } else {
            $('#selectall3DMFI').prop("checked",false);
        }
    });

};

var displayScatterPlot3DMFI = function() {
    $("#scatterPlotDiv3DMFI").empty();
    //var iframe = window.parent.document.getElementById('galaxy_main')
    //var iframeHeight = iframe.clientHeight - 200;
    //var iframeWidth = iframe.clientWidth;
    var h = $(window).height() - 200;
    $("#scatterPlotDiv3DMFI").height(h);
    var w = $("#scatterPlotDiv3DMFI").width();


    var xtitle = scatterData3DMFI['columnHeadings'][scatterData3DMFI['m1']];
    var ytitle = scatterData3DMFI['columnHeadings'][scatterData3DMFI['m2']];
    var ztitle = scatterData3DMFI['columnHeadings'][scatterData3DMFI['m3']];

    var data = [
      {
        x: scatterData3DMFI['xData'],
        y: scatterData3DMFI['yData'],
        z: scatterData3DMFI['zData'],
        mode: 'markers',
        marker: { size: 8, color: scatterData3DMFI['popColors'] },
        type: 'scatter3d'
      }
    ];

    var layout = {
        title: '',
        //width: w,
        //height: h,
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
                     range: [0,scatterData3DMFI['max']],
                     zeroline: false },
            yaxis: { type: 'linear',
                     title: ytitle,
                     range: [0,scatterData3DMFI['max']],
                     zeroline: false },
            zaxis: { type: 'linear',
                     title: ztitle,
                     range: [0,scatterData3DMFI['max']],
                     zeroline: false }
        }
    };

    Plotly.newPlot('scatterPlotDiv3DMFI',data,layout);
};
