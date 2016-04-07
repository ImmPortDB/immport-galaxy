/*
 * Initialize variables for parallelCoordinates display 
*/
var pCoordApp = pCoordApp || {};

pCoordApp.allPopulations = [];
pCoordApp.selectedPopulations = [];
pCoordApp.origData;
pCoordApp.flowData;

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
                   + d.Population + '/></td><td>' + d.Population
                   + '</td><td><span style="background-color:'
                   + color_palette[d.Population]
                   + '">&nbsp;&nbsp;&nbsp;</span></td>'
                   + '<td>' + d.Percentage + '</td></tr>');
    });

    $('#popSelectAll').click(function() {
        var checkAll = $("#popSelectAll").prop('checked');
        if (checkAll) {
            $(".popSelect").prop("checked", true);
        } else {
            $(".popSelect").prop("checked", false);
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
        displayTableGrid();
        updateParallelForeground();
    });
};

var updatePopTable = function() {
    $('.popSelect').each(function() {
        var pop = parseInt(this.value);
        if ($.inArray(pop,pCoordApp.selectedPopulations) > -1) {
            this.checked = true;
        } else {
            this.checked = false;
        }
    })
}

/*
 *
*/
var displayTableGrid = function() {
    $("#tableDiv").empty();
    var displayData = pCoordApp.origData.filter(function(d) {
        var pop = parseInt(d['Population'])
        if ($.inArray(pop,pCoordApp.selectedPopulations) > -1) {
          return d;
        }
    });
    var grid = d3.divgrid();
    d3.select("#tableDiv")
        .datum(displayData)
        .call(grid)
        .selectAll(".gridRow")
        .on({
          "mouseover": function(d) {
             var pop = parseInt(d['Population']);
             pCoordApp.selectedPopulations = [ pop ];
             updateParallelForeground();
          },
          "mouseout": function() {
              pCoordApp.selectedPopulations = [];
              $('.popSelect').each(function() {
                  if (this.checked) {
                     pCoordApp.selectedPopulations.push(parseInt(this.value));
                  }
              })
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

    // Use this to scale line width to percentage population
    var pd = d3.extent(pCoordApp.origData, function(p) { return +p['Percentage'];});
    var popScale = d3.scale.linear().range([1,5]).domain(pd);

    var y = {};
    var line = d3.svg.line();
    var axis = d3.svg.axis().orient("left");
    var background;
    var foreground;

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

    function brush() {
      var actives = dimensions.filter(function(p)
                    { return !y[p].brush.empty(); });
      var extents = actives.map(function(p) { return y[p].brush.extent(); });
      var selectedPopulations = pCoordApp.origData.filter(function(d) {
          var pop = parseInt(d['Population']);
          var tf = actives.every(function(p,i) {
              return extents[i][0] <= pCoordApp.flowData[pop-1][p] &&
                            pCoordApp.flowData[pop-1][p] <= extents[i][1];

          })
          if (tf) {
              return pop;
          }
      });
      pCoordApp.selectedPopulations = selectedPopulations.map(function(d) {
          return parseInt(d['Population']);
      });

      updateParallelForeground();
      updatePopTable()
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
        .attr("d", function(d,i) {var pop = parseInt(d['Population']);
              return path(pCoordApp.flowData[pop -1 ]);})
        .attr("stroke",function(d){var pop = parseInt(d['Population']);
              return color_palette[pop];})
        //.attr("stroke-width", 2);
        // Use this if you want to scale the lines based on
        // population percentage
        .attr("stroke-width", function(d,i) {
               var pop = parseInt(d['Population']);
               var w = popScale(pCoordApp.origData[pop -1]['Percentage']);
               w = parseInt(w);
               return w;
             });

    // Add a group element for each dimension.
    var g = svg.selectAll(".dimension")
        .data(dimensions)
        .enter().append("g")
        .attr("class", "dimension")
        .attr("transform", function(d) { return "translate(" + x(d) + ")"; });

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
};

var updateParallelForeground = function() {
   pCoordApp.foreground[0].map(function(d) {
       var pop = parseInt(d['__data__']['Population'])
       if ($.inArray(pop,pCoordApp.selectedPopulations) < 0) {
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
        /* 
         * For the plot use only the MFI information
         * for each populations. Store in flowData
        */
        pCoordApp.flowData = $.extend(true,[],data);
        pCoordApp.flowData.forEach(function(d) {
            delete d['Population'];delete d['Count']; delete d['Percentage']} )
        for (var i = 0; i < pCoordApp.flowData.length; i++) {
            pCoordApp.allPopulations.push(i + 1);
            pCoordApp.selectedPopulations.push(i + 1);
        }

        displayPopTable();
        displayTableGrid();
        displayParallelPlot();
    
        $("#resetPCoordDisplay").on("click",function() {
            for (var i = 0; i < pCoordApp.flowData.length; i++) {
                pCoordApp.allPopulations.push(i + 1);
                pCoordApp.selectedPopulations.push(i + 1);
            }
            $("#popSelectAll").prop('checked',true);
            $(".popSelect").prop("checked",true);
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
