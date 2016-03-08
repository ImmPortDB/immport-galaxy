var color_palette = [
    '#000000', // Black 0
    '#FF0000', // Red 1
    '#FFFF00', // Yellow 2
    '#008000', // Dark Green 3
    '#0000FF', // Blue 4
    '#FFA500', // Orange 5
    '#8A2BE2', // BlueViolet 6
    '#808000', // Olive 7
    '#00FFFF', // Cyan 8
    '#FF00FF', // Magenta 9
    '#00FF00', // Green 10
    '#000080', // Navy Blue 11
    '#F08080', // Light Coral 12
    '#800080', // Purple 13
    '#F0E68C', // Khaki 14
    '#8FBC8F', // Dark Sea Green 15
    '#2F4F4F', // Dark Slate Grey 16
    '#008080', // Teal 17
    '#9932CC', // Dark Orchid 18
    '#FF7F50', // Coral 19
    '#FFD700', // Gold 20
    '#008B8B', // Cyan 4 21
    '#800000', // Maroon 22
    '#5F9EA0', // Cadet Blue 23
    '#FFC0CB', // Pink 24
    '#545454', // Grey 25
    '#7FFFD4', // Aquamarine 26
    '#ADD8E6', // Light Blue 27
    '#DB7093', // Medium Violet Red 28
    '#CD853F', // Tan 3 29
    '#4169E1', // Royal Blue 30
    '#708090', // Slate Grey 31
    '#4682B4', // Steel Blue 32
    '#D8BFD8', // Thistle 33
    '#F5DEB3', // Wheat 34
    '#9ACD32', // Yellow Green 35
    '#BDB76B', // Dark Khaki 36
    '#8B008B', // Magenta 4 37
    '#556B2F', // Dark Olive Green 38
    '#00CED1', // Dark Turquoise 39
    '#FF1493' // Deep Pink
]



var displayPlotToolbar = function(toolbarDiv,populationDiv,scatterPlot) {
    scatterPlot['columnHeadings'].map(function(value,index) {
        $('#xAxisMarker')
            .append($("<option></option>")
            .attr("value",index)
            .text(value));

        $('#yAxisMarker')
            .append($("<option></option>")
            .attr("value",index)
            .text(value));
    });

    $('#xAxisMarker').select2("val",0);
    $('#yAxisMarker').select2("val",1);

    scatterPlot['populations'].map(function(value,index) {
        $('#populationTable tr')
            .last()
            .after('<tr><td align="center"><input type="checkbox" checked class="pop" value=' + value + '/></td><td>' + value + '<td><span style="background-color:' + color_palette[value] + '">&nbsp;&nbsp;&nbsp</span></td></td><td>' + scatterPlot['percent'][value - 1] + '<td></tr>');
    }); 
            
    return;
};

var processScatterPlotData = function(scatterPlot) {
    var min = d3.min(scatterPlot['data'], function(array) {
      return d3.min(array);
    });
    var max = d3.max(scatterPlot['data'], function(array) {
      return d3.max(array);
    });
    scatterPlot['min'] = 0;
    scatterPlot['max'] = max;

    var col1 = scatterPlot['data'].map(function(value,index) { 
               return value[scatterPlot['m1']];});
    var col2 = scatterPlot['data'].map(function(value,index) {
               return value[scatterPlot['m2']];});
    var pop = scatterPlot['data'].map(function(value,index) {
               return value[scatterPlot['popCol']];});

    var scatterData = []
    for (var i = 0; i < col1.length; i++) {
        if (scatterPlot['populations'].indexOf(pop[i]) >= 0) {
            obj = { "col1": col1[i], "col2": col2[i], "pop": pop[i] };
            scatterData.push(obj);
        }
    }
    scatterPlot['scatterData'] = scatterData;

    return scatterPlot;
};

var displayScatterPlot = function(element,scatterPlot) {
    var h = $(window).height() - 200;
    $(element).empty(); 
    $(element).height(h);
    var margin = { top: 20, right: 100, bottom: 20, left: 100 }
    var svgWidth = $(element).width();
    var svgHeight = $(element).height();
    var plotWidth = svgWidth - margin.left - margin.right;
    var plotHeight = svgHeight - margin.top - margin.bottom;

    // setup x
    var xValue = function(d) { return d.col1;}, // data -> value
        xScale = d3.scale.linear().range([0, plotWidth]), // value -> display
        xMap = function(d) { return xScale(xValue(d));}, // data -> display
        xAxis = d3.svg.axis().scale(xScale).orient("bottom");

    // setup y
    var yValue = function(d) { return d.col2;}, // data -> value
        yScale = d3.scale.linear().range([plotHeight, 0]), // value -> display
        yMap = function(d) { return yScale(yValue(d));}, // data -> display
        yAxis = d3.svg.axis().scale(yScale).orient("left");

    // don't want dots overlapping axis, so add in buffer to data domain
      xScale.domain([0, scatterPlot['max']]);
      yScale.domain([0, scatterPlot['max']]);

    /* Initialize SVG */
    var svg = d3.select(element).append("svg")
                .attr("width", svgWidth)
                .attr("height", svgHeight)
                .append("g")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // x-axis
    svg.append("g")
          .attr("class", "x axis")
          .attr("transform", "translate(0," + plotHeight + ")")
          .call(xAxis);
          //.append("text")
          //.attr("class", "label")
          //.attr("x", plotWidth)
          //.attr("y", -6)
          //.style("text-anchor", "end")
          //.text("Marker 1");

    // y-axis
    svg.append("g")
          .attr("class", "y axis")
          .call(yAxis);
          //.append("text")
          //.attr("class", "label")
          //.attr("transform", "rotate(-90)")
          //.attr("y", 6)
          //.attr("dy", ".71em")
          //.style("text-anchor", "end")
          //.text("Marker 2");

    svg.selectAll("circle")
          .data(scatterPlot['scatterData'])
          .enter()
          .append("circle")
          .attr("cx",xMap)
          .attr("cy",yMap)
          .attr("r",function(d) { return 2; })
          .attr("fill",function(d) { return color_palette[d.pop];});

    return;
}
