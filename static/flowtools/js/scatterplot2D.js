var displayToolbar2D = function(toolbarDiv,populationDiv,scatterData2D) {
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

    scatterData2D['populations'].map(function(value,index) {
        $('#populationTable2D tr')
            .last()
            .after('<tr><td align="center"><input type="checkbox" checked class="pop2D" value=' + value + '/></td><td>' + value + '<td><span style="background-color:' + color_palette[value] + '">&nbsp;&nbsp;&nbsp</span></td></td><td>' + scatterData2D['percent'][value - 1] + '<td></tr>');
    }); 
            
    return;
};

var processScatterData2D = function(scatterData2D) {
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

    var scatterDataTemp = []
    for (var i = 0; i < col1.length; i++) {
        if (scatterData2D['populations'].indexOf(pop[i]) >= 0) {
            obj = { "col1": col1[i], "col2": col2[i], "pop": pop[i] };
            scatterDataTemp.push(obj);
        }
    }
    scatterData2D['scatterData'] = scatterDataTemp;

    return scatterData2D;
};

var displayScatterPlot2D = function(element,scatterData2D) {
    var iframe = window.parent.document.getElementById('galaxy_main')
    var iframeHeight = iframe.clientHeight; 
    var iframeWidth = iframe.clientWidth; 
    console.log($(window).width(),$(window).height());
    console.log(iframeWidth,iframeHeight);
    var h = iframeHeight - 200;
    $(element).empty(); 
    $(element).height(iframeHeight - 200);
    var margin = { top: 20, right: 50, bottom: 20, left: 50 }
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
    xScale.domain([0, scatterData2D['max']]);
    yScale.domain([0, scatterData2D['max']]);

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
          .data(scatterData2D['scatterData'])
          .enter()
          .append("circle")
          .attr("cx",xMap)
          .attr("cy",yMap)
          .attr("r",function(d) { return 2; })
          .attr("fill",function(d) { return color_palette[d.pop];});

    return;
}
