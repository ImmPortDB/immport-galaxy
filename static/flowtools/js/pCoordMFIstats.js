/*
 * Initialize variables for parallelCoordinates display 
*/
var pcAppMFI = pcAppMFI || {};

pcAppMFI.origData;
pcAppMFI.flowData;
pcAppMFI.background;
pcAppMFI.foreground;
pcAppMFI.selectedLines = [];
pcAppMFI.selectedPopulations = [];
pcAppMFI.selectedSamples = [];
pcAppMFI.populations = [];
pcAppMFI.samples = [];
pcAppMFI.lines = [];
pcAppMFI.allLines;
pcAppMFI.headers = [];

var displayAllm = function() {
    displayParallelPlotm();
};

/*
 * Display the Population Legend
*/
var displayPopTablem = function() {
    $('#popTablePCm tbody').empty();
    pcAppMFI.populations.map(function(d, index) {
        $('#popTablePCm tbody')
            .append('<tr><td align="center">'
                   + '<input type="checkbox" '
                   + 'id="'+ d + '" '
                   + 'checked class="popSelectPCm" value='
                   + index + '/></td><td>' + d
                   + '</td><td><span style="background-color:'
                   + color_palette[index]
                   + '">&nbsp;&nbsp;&nbsp;</span></td></tr>');
    });

    $('#popSelectAllPCm').click(function() {
        var checkAll = $("#popSelectAllPCm").prop('checked');
        if (checkAll) {
            $(".popSelectPCm").prop("checked", true);
			for (var i = 0; i < pcAppMFI.allLines; i ++){
				pcAppMFI.selectedLines.push(i);
				pcAppMFI.lines.push(i);
			}
        } else {
            $(".popSelectPCm").prop("checked", false);
			pcAppMFI.selectedLines = [];
			pcAppMFI.lines = [];
        }

        pcAppMFI.selectedPopulations = [];
        $('.popSelectPCm').each(function() {
          if (this.checked) {
            pcAppMFI.selectedPopulations.push(parseInt(this.value));
          }
        });
		
        displayTableGridm();
        if (checkAll) {
            displayParallelPlotm();
        } else {
            updateParallelForegroundidx();
        }
    });

    $('.popSelectPCm').click(function() {
        if ($('.popSelectPCm').length == $(".popSelectPCm:checked").length) {
            $('#popSelectAllPCm').prop("checked",true);
        } else {
            $('#popSelectAllPCm').prop("checked",false);
        }
		
		pcAppMFI.selectedPopulations = [];
		$('.popSelectPCm').each(function() {
            if (this.checked) {
		        pcAppMFI.selectedPopulations.push(parseInt(this.value));
            }
        });
			
		pcAppMFI.selectedLines = [];
		pcAppMFI.lines = [];
		
		pcAppMFI.origData.forEach(function(d,idx){
            if ($.inArray(pcAppMFI.populations.indexOf(d.Population), pcAppMFI.selectedPopulations) > -1) {
                if ($.inArray(pcAppMFI.samples.indexOf(d.SampleName), pcAppMFI.selectedSamples) > -1){
                    pcAppMFI.selectedLines.push(idx);
                    pcAppMFI.lines.push(idx);
                }
            }

		});

        displayTableGridm();
        updateParallelForegroundidx();
    });
};

var updatePopTableidx = function() {
    $('.popSelectPCm').each(function() {
        var pop = parseInt(this.value);
		var selectedPops = pcAppMFI.origData.map(function(d){
			if ($.inArray(d.idx, pcAppMFI.selectedLines) > -1){
				return pcAppMFI.populations.indexOf(d.Population);
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
* Display Sample Legend
*/
var displaySmpTablem = function(){
    $('#smpTablePCm tbody').empty();
    pcAppMFI.samples.map(function(d, index) {
        $('#smpTablePCm tbody')
            .append('<tr><td>' + d 
                   + '</td><td align="center">'
                   + '<input type="checkbox" '
                   + 'id="' + d + '" '
                   + 'checked class="smpSelectPCm" value='
                   + index + '></td></tr>');
    });

    $('#smpSelectAllPCm').click(function() {
        var checkAll = $("#smpSelectAllPCm").prop('checked');
        if (checkAll) {
            $(".smpSelectPCm").prop("checked", true);
			for (var i = 0; i < pcAppMFI.allLines; i ++){
				pcAppMFI.selectedLines.push(i);
				pcAppMFI.lines.push(i);
			}
        } else {
            $(".smpSelectPCm").prop("checked", false);
			pcAppMFI.selectedLines = [];
			pcAppMFI.lines = [];
        }

        pcAppMFI.selectedSamples = [];
        $('.smpSelectPCm').each(function() {
            if (this.checked) {
                pcAppMFI.selectedSamples.push(parseInt(this.value));
            }
        });

        displayTableGridm();
        if (checkAll) {
            displayParallelPlotm();
        } else {
            updateParallelForegroundidx();
        }
    });

    $('.smpSelectPCm').click(function() {
        if ($('.smpSelectPCm').length == $(".smpSelectPCm:checked").length) {
            $('#smpSelectAllPCm').prop("checked",true);
        } else {
            $('#smpSelectAllPCm').prop("checked",false);
        }

        pcAppMFI.selectedSamples = [];
		$('.smpSelectPCm').each(function() {
            if (this.checked) {
                pcAppMFI.selectedSamples.push(parseInt(this.value));
            }
        });

		pcAppMFI.selectedLines = [];
		pcAppMFI.lines = [];

		pcAppMFI.origData.forEach(function(d,idx){
            if ($.inArray(pcAppMFI.populations.indexOf(d.Population), pcAppMFI.selectedPopulations) > -1) {
                if ($.inArray(pcAppMFI.samples.indexOf(d.SampleName), pcAppMFI.selectedSamples) > -1){
                    pcAppMFI.selectedLines.push(idx);
                    pcAppMFI.lines.push(idx);
                }
            }

		});

        displayTableGridm();
        updateParallelForegroundidx();
    });
};

var updateSmpTableidx = function() {
    $('.smpSelectPCm').each(function() {
        var smp = parseInt(this.value);
		var selectedSamples = pcAppMFI.origData.map(function(d){
			if ($.inArray(d.idx, pcAppMFI.selectedLines) > -1){
				return pcAppMFI.samples.indexOf(d.SampleName);
			}
		});
        if ($.inArray(smp,selectedSamples) > -1) {
            this.checked = true;
        } else {
            this.checked = false;
        }
    });
};
      
/*
 * Display Data table
*/

var displayTableGridm = function() {
	$("#tableDivPCm").empty();
    var displayData = pcAppMFI.origData.filter(function(d, index) {
        if ($.inArray(index,pcAppMFI.selectedLines) > -1){
            return d;
        }
    });

    var grid = d3.divgrid();
    grid.columns(pcAppMFI.headers);
    d3.select("#tableDivPCm")
      .datum(displayData)
      .call(grid)
      .selectAll(".gridRow")
      .on({
          "mouseover": function(d) {
             var line = parseInt(d.idx);

             pcAppMFI.selectedLines = [line];
             updateParallelForegroundidx();
          },
          "mouseout": function() {
			  pcAppMFI.selectedLines = [];
			  for (var i = 0, j = pcAppMFI.lines.length; i < j; i++){
	              pcAppMFI.selectedLines.push(pcAppMFI.lines[i]);
			  }
              updateParallelForegroundidx();
          }
      });
};    

/*
* Update Parallel Foreground
*/
var updateParallelForegroundidx = function() {
   pcAppMFI.foreground[0].map(function(d) {
       var ln = parseInt(d['__data__']['idx']);
       
       if ($.inArray(ln,pcAppMFI.selectedLines) < 0){
             d.style.display = "none";
           } else {
             d.style.display = null;
           }
   });
};

/*
 * Display The Main Plot
*/
var displayParallelPlotm = function() {
    var margin = {top: 30, right: 10, bottom: 10, left: 10};

    $("#plotDivPCm").empty();
    var h = $("#chartDivPCm").height() * 0.6;
    $("#plotDivPCm").height(h);
    var w = $("#plotDivPCm").width()
    width = w - margin.left - margin.right,
    height = h - margin.top - margin.bottom;
    var svg = d3.select("#plotDivPCm").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")")

    var x = d3.scale.ordinal().rangePoints([0, width], 1);
    var y = {};
    var line = d3.svg.line();
    var axis = d3.svg.axis().orient("left");
    var dragging = {};
    
    var dimensions = d3.keys(pcAppMFI.flowData[0]).filter(function(d) {
        return (y[d] = d3.scale.linear()
            .domain(d3.extent(pcAppMFI.flowData,function(p) {
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

      var indices = pcAppMFI.origData.filter(function(d) {
          var line = parseInt(d.idx)
          var tf = actives.every(function(p,i) {
              return extents[i][0] <= pcAppMFI.flowData[line][p] &&
                            pcAppMFI.flowData[line][p] <= extents[i][1];
          })
          if (tf) {
              return line.toString();
          }
      });

      pcAppMFI.selectedLines = indices.map(function(d) {
          return parseInt(d.idx);
      });
      pcAppMFI.lines = indices.map(function(d) {
          return parseInt(d.idx);
      });
      updateParallelForegroundidx();
      updatePopTableidx();
      updateSmpTableidx();
      displayTableGridm();
    }

    // Display paths in light gray color, to use as reference
    pcAppMFI.background = svg.append("g")
       .attr("class", "background")
       .selectAll("path")
       .data(pcAppMFI.flowData)
       .enter()
       .append("path")
       .attr("d", path);

    // Add foreground lines for focus, color by population.
    pcAppMFI.foreground = svg.append("g")
        .attr("class", "foreground")
        .selectAll("path")
        .data(pcAppMFI.origData)
        .enter()
        .append("path")
        .attr("d", path)
        .attr("stroke",function(d){
			  var pop = pcAppMFI.populations.indexOf(d.Population);
              return color_palette[pop];})
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
            pcAppMFI.background.attr("visibility", "hidden");
          })
          .on("drag", function(d) {
            dragging[d] = Math.min(width, Math.max(0, d3.event.x));
            pcAppMFI.foreground.attr("d", path);
            dimensions.sort(function(a, b) { return position(a) - position(b); });
            x.domain(dimensions);
            g.attr("transform", function(d) { return "translate(" + position(d) + ")"; })
          })
          .on("dragend", function(d) {
            delete dragging[d];
            transition(d3.select(this)).attr("transform", "translate(" + x(d) + ")");
            transition(pcAppMFI.foreground).attr("d", path);
            pcAppMFI.background
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
    $('#PCmline_opacity').on('change', (function() {
      var val = $(this).val();
      $('#plotDivPCm .foreground path').css('stroke-opacity', val.toString());
      $('#pcm_opacity').html((Math.round(val*10000)/100) + "%");
    }));
};


/*
 * Retrieve the data, then call display functions
*/
var displayParallelCoordinatesMFI = function() {
    var inputFile = "./csAllMFIs.tsv";
    d3.tsv(inputFile, function(error, data) {
        if (error) {
            alert("Problem Retrieving Data");
            return;
        }
   
        pcAppMFI.origData = $.extend(true,[],data);
        pcAppMFI.headers = Object.keys(pcAppMFI.origData[0]);
        pcAppMFI.origData.forEach(function(d,idx) {
            d.idx = idx;
			pcAppMFI.selectedLines.push(idx);
			pcAppMFI.lines.push(idx);
            if (!pcAppMFI.populations.includes(d.Population)){
                pcAppMFI.populations.push(d.Population);
            }
            if (!pcAppMFI.samples.includes(d.SampleName)){
                pcAppMFI.samples.push(d.SampleName);
            }
        })
		pcAppMFI.allLines = pcAppMFI.origData.length;

		var allPops = pcAppMFI.populations.length;
		var allSamples = pcAppMFI.samples.length;
        for (var i = 0; i < allPops; i++) {
            pcAppMFI.selectedPopulations.push(i);
        }
        for (var i = 0; i < allSamples; i++) {
            pcAppMFI.selectedSamples.push(i);
        }
		
        /* 
         * For the plot use only the MFI information
         * for each populations. Store in flowData
        */
        pcAppMFI.flowData = $.extend(true,[],data);
        pcAppMFI.flowData.forEach(function(d) {
            delete d['Population'];delete d['SampleName']; delete d['Percentage']; 
        })
 
        displayPopTablem();
        displaySmpTablem();
        displayTableGridm();
        displayParallelPlotm();
    
        $("#resetDisplayMFIpop").on("click",function() {
            for (var i = 0; i < allPops; i++) {
                pcAppMFI.selectedPopulations.push(i);
            }
            for (var i = 0; i < allSamples; i++) {
                pcAppMFI.selectedSamples.push(i);
            }
            for (var i = 0; i < pcAppMFI.allLines; i++) {
                pcAppMFI.selectedLines.push(i);
				pcAppMFI.lines.push(i);
            }

            $("#popSelectAllPCm").prop('checked',true);
            $(".popSelectPCm").prop("checked",true);
            $("#smpSelectAllPCm").prop('checked',true);
            $(".smpSelectPCm").prop("checked",true);

            var opcty = ".8"
            $('#plotDivPCm .foreground path').css('stroke-opacity', opcty);
            $('#pcm_opacity').html("80%");
            $('#PCmline_opacity').val(0.8);

            displayPopTablem();
            displaySmpTablem();
            displayTableGridm();
            displayParallelPlotm();
        });

        $(window).on('resize',function() {
            waitForFinalEvent(function() {
                displayAllm();
            },500,"resizePCm");
        });
    });
}
