/*
 * Initialize variables for parallelCoordinates display 
*/
var pcApp = pcApp || {};

pcApp.allSamples = [];
pcApp.selectedSamples = [];
pcApp.origData;
pcApp.flowData;
pcApp.headers = [];
pcApp.foreground;
pcApp.background;

var displayAll = function() {
    displayParallelPlot();
}

/*
 * Display the Population Legend
*/
var displaySmpTable = function() {
    $('#popTablePC tbody').empty();
    pcApp.origData.map(function(d) {
        $('#popTablePC tbody')
            .append('<tr><td align="center">'
                   + '<input type="checkbox" id="' + d.SampleName + '" '
                   + 'checked class="popSelectPC" value='
                   + d.SampleNumber + '/></td><td>' + d.SampleName
                   + '</td><td><span style="background-color:'
                   + color_palette[d.SampleNumber]
                   + '">&nbsp;&nbsp;&nbsp;</span></td></tr>');
    });

    $('#popSelectAllPC').click(function() {
        var checkAll = $("#popSelectAllPC").prop('checked');
        if (checkAll) {
            $(".popSelectPC").prop("checked", true);
        } else {
            $(".popSelectPC").prop("checked", false);
        }

        pcApp.selectedSamples = [];
        $('.popSelectPC').each(function() {
          if (this.checked) {
            pcApp.selectedSamples.push(parseInt(this.value));
          }
        })
        displayTableGrid();
        if (checkAll) {
            displayParallelPlot();
        } else {
            updateParallelForeground();
        }
    });

    $('.popSelectPC').click(function() {
        if ($('.popSelectPC').length == $(".popSelectPC:checked").length) {
            $('#popSelectAllPC').prop("checked",true);
        } else {
            $('#popSelectAllPC').prop("checked",false);
        }

        pcApp.selectedSamples = [];
        $('.popSelectPC').each(function() {
          if (this.checked) {
             pcApp.selectedSamples.push(parseInt(this.value));
          }
        })
        displayTableGrid();
        updateParallelForeground();
    });
};

var updateSmpTable = function() {
    $('.popSelectPC').each(function() {
        var smp = parseInt(this.value);
        if ($.inArray(smp,pcApp.selectedSamples) > -1) {
            this.checked = true;
        } else {
            this.checked = false;
        }
    })
}


var displayTableGrid = function() {
    $("#tableDivPC").empty();
    var displayData = pcApp.origData.filter(function(d) {
        var smp = parseInt(d.SampleNumber);
        if ($.inArray(smp,pcApp.selectedSamples) > -1) {
          return d;
        }
    });
    var grid = d3.divgrid();
    grid.columns(pcApp.headers);
    d3.select("#tableDivPC")
        .datum(displayData)
        .call(grid)
        .selectAll(".gridRow")
        .on({
          "mouseover": function(d) {
             var smp = parseInt(d.SampleNumber);
             pcApp.selectedSamples = [ smp ];
             updateParallelForeground();
          },
          "mouseout": function() {
              pcApp.selectedSamples = [];
              $('.popSelectPC').each(function() {
                  if (this.checked) {
                     pcApp.selectedSamples.push(parseInt(this.value));
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

    $("#plotDivPC").empty();
    var h = $("#chartDivPC").height() * 0.6;
    $("#plotDivPC").height(h);
    var w = $("#plotDivPC").width()
    width = w - margin.left - margin.right,
    height = h - margin.top - margin.bottom;
    var svg = d3.select("#plotDivPC").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")")

    var x = d3.scale.ordinal().rangePoints([0, width], 1);
    var y = {};
	var dragging = {};
    var line = d3.svg.line();
    var axis = d3.svg.axis().orient("left");

    var dimensions = d3.keys(pcApp.flowData[0]).filter(function(d) {
        return (y[d] = d3.scale.linear()
            .domain(d3.extent(pcApp.flowData,function(p) {
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
      var selectedSamples = pcApp.origData.filter(function(d) {
          var smp = parseInt(d.SampleNumber);
          var tf = actives.every(function(p,i) {
              return extents[i][0] <= pcApp.flowData[smp][p] &&
                            pcApp.flowData[smp][p] <= extents[i][1];

          })
          if (tf) {
              return smp.toString();
          }
      });
      pcApp.selectedSamples = selectedSamples.map(function(d) {
          return parseInt(d.SampleNumber);
      });

      updateParallelForeground();
      updateSmpTable()
      displayTableGrid();
    }

    // Display paths in light gray color, to use as reference
    pcApp.background = svg.append("g")
       .attr("class", "background")
       .selectAll("path")
       .data(pcApp.flowData)
       .enter()
       .append("path")
       .attr("d", path);

    // Add foreground lines for focus, color by population.
    pcApp.foreground = svg.append("g")
        .attr("class", "foreground")
        .selectAll("path")
        .data(pcApp.origData)
        .enter()
        .append("path")
        .attr("d", function(d) {
			var smp = d.SampleNumber;
            return path(pcApp.flowData[smp]);
		})
        .attr("stroke",function(d){
			var smp = d.SampleNumber;
            return color_palette[smp];})
        .attr("stroke-width", 1);

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
            pcApp.background.attr("visibility", "hidden");
          })
          .on("drag", function(d) {
            dragging[d] = Math.min(width, Math.max(0, d3.event.x));
            pcApp.foreground.attr("d", path);
            dimensions.sort(function(a, b) { return position(a) - position(b); });
            x.domain(dimensions);
            g.attr("transform", function(d) { return "translate(" + position(d) + ")"; })
          })
          .on("dragend", function(d) {
            delete dragging[d];
            transition(d3.select(this)).attr("transform", "translate(" + x(d) + ")");
            transition(pcApp.foreground).attr("d", path);
            pcApp.background
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
    $('#PCline_opacity').on('change', (function() {
      var val = $(this).val();
      $('#plotDivPC .foreground path').css('stroke-opacity', val.toString());
      $('#pc_opacity').html((Math.round(val*10000)/100) + "%");
    }));
};

var updateParallelForeground = function() {
   pcApp.foreground[0].map(function(d) {
       var smp = parseInt(d['__data__']['SampleNumber'])
       if ($.inArray(smp,pcApp.selectedSamples) < 0) {
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
    var inputFile = "./csOverview.tsv";
    d3.tsv(inputFile, function(error, data) {
         if (error) {
            alert("Problem Retrieving Data");
            return;
        }
   
        pcApp.origData = $.extend(true,[],data);
        pcApp.headers = Object.keys(pcApp.origData[0]);
        pcApp.headers.splice(pcApp.headers.indexOf("FileID"), 1);
        
        pcApp.origData.forEach(function(d,idx){
            d.SampleNumber = idx;
			delete d.FileID;
        })
		
        /* 
         * For the plot use only the MFI information
         * for each populations. Store in flowData
        */
        pcApp.flowData = $.extend(true,[],data);
        pcApp.flowData.forEach(function(d, index) {
            delete d['FileID'];
            delete d['SampleName']; 
        } )
        
        for (var i = 0; i < pcApp.flowData.length; i++) {
            pcApp.allSamples.push(i);
            pcApp.selectedSamples.push(i);
        }

        displaySmpTable();
        displayTableGrid();
        displayParallelPlot();
    
        $("#resetPCDisplay").on("click",function() {
            for (var i = 0; i < pcApp.flowData.length; i++) {
                pcApp.allSamples.push(i);
                pcApp.selectedSamples.push(i);
            }
            $("#smpSelectAllPC").prop('checked',true);
            $(".smpSelectPC").prop("checked",true);

            var opcty = ".8";
            $('#plotDivPC .foreground path').css('stroke-opacity', opcty);
            $('#pc_opacity').html("80%");
            $('#PCline_opacity').val(0.8);
            
            displaySmpTable();
            displayTableGrid();
            displayParallelPlot();
        });

        $(window).on('resize',function() {
            waitForFinalEvent(function() {
                displayAll();
            },500,"resizePC");
        });
    });
}
