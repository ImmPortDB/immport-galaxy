/*
 * Initialize variables for parallelCoordinates display 
*/
var pCoordApp = pCoordApp || {};

pCoordApp.allPopulations = [];
pCoordApp.selectedPopulations = [];
pCoordApp.origData;
pCoordApp.flowData;
pCoordApp.headers = [];
pCoordApp.foreground;
pCoordApp.background;
pCoordApp.populations = [];
pCoordApp.allLines;
pCoordApp.lines = [];
pCoordApp.selectedLines = [];

var displayAll = function() {
    displayParallelPlot();
}

/*
 * Display the Population Legend
*/
var displayPopTable = function() {
    $('#popTable tbody').empty();
    pCoordApp.origData.map(function(d,index) {
        $('#popTable tbody')
            .append('<tr><td align="center">'
                   + '<input type="checkbox" '
                   + 'id="pop' + d.Population + '" '
                   + 'checked class="popSelect" value='
                   + index + '/></td><td>' + d.Population
                   + '</td><td><span style="background-color:'
                   + color_palette[index]
                   + '">&nbsp;&nbsp;&nbsp;</span></td>'
                   + '<td>' + d.Percentage + '</td></tr>');
    });

    $('#popSelectAll').click(function() {
        var checkAll = $("#popSelectAll").prop('checked');
        if (checkAll) {
            $(".popSelect").prop("checked", true);
			for (var i = 0; i < pCoordApp.allLines; i ++){
				pCoordApp.selectedLines.push(i);
				pCoordApp.lines.push(i);
			}
        } else {
            $(".popSelect").prop("checked", false);
 			pCoordApp.selectedLines = [];
			pCoordApp.lines = [];
       }

        pCoordApp.selectedPopulations = [];
        $('.popSelect').each(function() {
          if (this.checked) {
            pCoordApp.selectedPopulations.push(parseInt(this.value));
          }
        })
        displayTableGrid();
        if (checkAll) {
            displayParallelPlot();
        } else {
            updateParallelForeground();
        }
    });

    $('.popSelect').click(function() {
        if ($('.popSelect').length == $(".popSelect:checked").length) {
            $('#popSelectAll').prop("checked",true);
        } else {
            $('#popSelectAll').prop("checked",false);
        }

        pCoordApp.selectedPopulations = [];
        $('.popSelect').each(function() {
          if (this.checked) {
            pCoordApp.selectedPopulations.push(parseInt(this.value));
          }
        })
		pCoordApp.selectedLines = [];
		pCoordApp.lines = [];
		
		pCoordApp.origData.forEach(function(d,idx){
            if ($.inArray(pCoordApp.populations.indexOf(d.Population), pCoordApp.selectedPopulations) > -1) {
                pCoordApp.selectedLines.push(idx);
                pCoordApp.lines.push(idx);
            }
		});

        displayTableGrid();
        updateParallelForeground();
    });
};

var updatePopTable = function() {
    $('.popSelect').each(function() {
        var pop = parseInt(this.value);
		var selectedPops = pCoordApp.origData.map(function(d){
			if ($.inArray(d.idx, pCoordApp.selectedLines) > -1){
				return pCoordApp.populations.indexOf(d.Population);
			}
		});
        if ($.inArray(pop,selectedPops) > -1) {
            this.checked = true;
        } else {
            this.checked = false;
        }
    });
};


/*
 *
*/
var displayTableGrid = function() {
    $("#tableDiv").empty();
    var displayData = pCoordApp.origData.filter(function(d, index) {
        if ($.inArray(index,pCoordApp.selectedLines) > -1) {
          return d;
        }
    });
    var grid = d3.divgrid();
    grid.columns(pCoordApp.headers);
    d3.select("#tableDiv")
        .datum(displayData)
        .call(grid)
        .selectAll(".gridRow")
        .on({
          "mouseover": function(d) {
             var line = parseInt(d.idx);
             pCoordApp.selectedLines = [line];
             updateParallelForeground();
          },
          "mouseout": function() {
			  pCoordApp.selectedLines = [];
			  for (var i = 0, j = pCoordApp.lines.length; i < j; i++){
	              pCoordApp.selectedLines.push(pCoordApp.lines[i]);
			  }
              updateParallelForeground();
          }
        });
};


/*
 * Display The Main Plot
*/
var displayParallelPlot = function() {
    var margin = {top: 30, right: 10, bottom: 10, left: 10};

    $("#plotDiv").empty();
    var h = $("#chartDiv").height()/1.5;
    $("#plotDiv").height(h);
    var w = $("#plotDiv").width()
    width = w - margin.left - margin.right,
    height = h - margin.top - margin.bottom;
    var svg = d3.select("#plotDiv").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")")

    var x = d3.scale.ordinal().rangePoints([0, width], 1);
    var dragging = {};
    
    // Use this to scale line width to percentage population
    var pd = d3.extent(pCoordApp.origData, function(p) { return +p['Percentage'];});
    var popScale = d3.scale.linear().range([1,5]).domain(pd);

    var y = {};
    var line = d3.svg.line();
    var axis = d3.svg.axis().orient("left");

    var dimensions = d3.keys(pCoordApp.flowData[0]).filter(function(d) {
        return (y[d] = d3.scale.linear()
            .domain(d3.extent(pCoordApp.flowData,function(p) {
                return +p[d]; }
            ))
            .range([height, 0]));
    });
    x.domain(dimensions);

    function path(d) {
      return line(dimensions.map(function(p) { return [x(p), y[p](d[p])]; }));
    }

    function position(d) {
      var v = dragging[d];
      return v == null ? x(d) : v;
    }

    function transition(g) {
      return g.transition().duration(500);
    }

    function brush() {
      var actives = dimensions.filter(function(p)
                    { return !y[p].brush.empty(); });
      var extents = actives.map(function(p) { return y[p].brush.extent(); });
      var indices = pCoordApp.origData.filter(function(d) {
          var line = d.idx;
          var tf = actives.every(function(p,i) {
              return extents[i][0] <= pCoordApp.flowData[line][p] &&
                            pCoordApp.flowData[line][p] <= extents[i][1];
          })
          if (tf) {
              return line.toString();
          }
      });
      pCoordApp.selectedLines = indices.map(function(d) {
          return d.idx;
      });
      pCoordApp.lines = indices.map(function(d) {
          return d.idx;
      });

      updateParallelForeground();
      updatePopTable();
      displayTableGrid();
    }


    // Display paths in light gray color, to use as reference
    pCoordApp.background = svg.append("g")
       .attr("class", "background")
       .selectAll("path")
       .data(pCoordApp.flowData)
       .enter()
       .append("path")
       .attr("d", path);

    // Add foreground lines for focus, color by population.
    pCoordApp.foreground = svg.append("g")
        .attr("class", "foreground")
        .selectAll("path")
        .data(pCoordApp.origData)
        .enter()
        .append("path")
        .attr("d", path)
        .attr("stroke",function(d){
              var pop = pCoordApp.populations.indexOf(d.Population);
              return color_palette[pop];})
        //.attr("stroke-width", 2);
        // Use this if you want to scale the lines based on
        // population percentage
        .attr("stroke-width", function(d) {
               var pop = pCoordApp.populations.indexOf(d.Population);
               var w = popScale(pCoordApp.origData[pop]['Percentage']);
               w = parseInt(w);
               return w;
             });

    // Add a group element for each dimension.
    var g = svg.selectAll(".dimension")
        .data(dimensions)
        .enter().append("g")
        .attr("class", "dimension")
        .attr("transform", function(d) { return "translate(" + x(d) + ")"; })
         .call(d3.behavior.drag()
          .origin(function(d) { return {x: x(d)}; })
          .on("dragstart", function(d) {
            dragging[d] = x(d);
            pCoordApp.background.attr("visibility", "hidden");
          })
          .on("drag", function(d) {
            dragging[d] = Math.min(width, Math.max(0, d3.event.x));
            pCoordApp.foreground.attr("d", path);
            dimensions.sort(function(a, b) { return position(a) - position(b); });
            x.domain(dimensions);
            g.attr("transform", function(d) { return "translate(" + position(d) + ")"; })
          })
          .on("dragend", function(d) {
            delete dragging[d];
            transition(d3.select(this)).attr("transform", "translate(" + x(d) + ")");
            transition(pCoordApp.foreground).attr("d", path);
            pCoordApp.background
                .attr("d", path)
              .transition()
                .delay(500)
                .duration(0)
                .attr("visibility", null);
          }));
       

    // Add an axis and title.
    g.append("g")
        .attr("class", "axis")
        .each(function(d) { d3.select(this).call(axis.scale(y[d])); })
        .append("text")
        .style("text-anchor", "middle")
        .attr("y", -9)
        .text(function(d) { return d; });

    // Add and store a brush for each axis.
    g.append("g")
        .attr("class", "brush")
        .each(function(d) { d3.select(this).call(y[d].brush = d3.svg.brush().y(y[d]).on("brush", brush)); })
        .selectAll("rect")
        .attr("x", -8)
        .attr("width", 16);

    // Control line opacity.
    $('#pcline_opacity').on('change', (function() {
      var val = $(this).val();
      $('#plotDiv .foreground path').css('stroke-opacity', val.toString());
      $('#pcopacity').html((Math.round(val*10000)/100) + "%");
    }));
};

var updateParallelForeground = function() {
   pCoordApp.foreground[0].map(function(d) {
       var ln = parseInt(d['__data__']['idx']);
       
       if ($.inArray(ln, pCoordApp.selectedLines) < 0){
             d.style.display = "none";
           } else {
             d.style.display = null;
           }
   });
};

/*
 * Retrieve the data, then call display functions
*/
var displayParallelCoordinates = function() {
    var inputFile = "flow.mfi_pop";
    d3.tsv(inputFile, function(error, data) {
        if (error) {
            alert("Problem Retrieving Data");
            return;
        }
   
        pCoordApp.origData = $.extend(true,[],data);
        pCoordApp.headers = Object.keys(pCoordApp.origData[0]);
        pCoordApp.origData.forEach(function(d,idx) {
            d.idx = idx;
			pCoordApp.selectedLines.push(idx);
			pCoordApp.lines.push(idx);
            if (!pCoordApp.populations.includes(d.Population)){
                pCoordApp.populations.push(d.Population);
            }
        })
        /* 
         * For the plot use only the MFI information
         * for each populations. Store in flowData
        */
        pCoordApp.flowData = $.extend(true,[],data);
        pCoordApp.flowData.forEach(function(d, idx) {
            delete d['Population'];delete d['Count']; delete d['Percentage']
            pCoordApp.allPopulations.push(idx);
            pCoordApp.selectedPopulations.push(idx);
            pCoordApp.selectedLines.push(idx);
            pCoordApp.lines.push(idx);
        });

        pCoordApp.allLines = pCoordApp.flowData.length;
        displayPopTable();
        displayTableGrid();
        displayParallelPlot();
    
        $("#resetPCoordDisplay").on("click",function() {
            for (var i = 0; i < pCoordApp.allLines; i++) {
                pCoordApp.allPopulations.push(i);
                pCoordApp.selectedPopulations.push(i);
                pCoordApp.selectedLines.push(i);
                pCoordApp.lines.push(i);
            }
            $("#popSelectAll").prop('checked',true);
            $(".popSelect").prop("checked",true);

            var opcty = ".8";
            $('#plotDiv .foreground path').css('stroke-opacity', opcty);
            $('#pcopacity').html("80%");
            $('#pcline_opacity').val(0.8);

            displayPopTable();
            displayTableGrid();
            displayParallelPlot();
        });

        $(window).on('resize',function() {
            waitForFinalEvent(function() {
                displayAll();
            },500,"resizeParallelCoordinates");
        });
    });
}
