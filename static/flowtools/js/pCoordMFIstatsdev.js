/*
 * Initialize variables for parallelCoordinates display 
*/
var pCoordAppMFI = pCoordAppMFI || {};

pCoordAppMFI.allPopulations = [];
pCoordAppMFI.selectedPopulations = [];
pCoordAppMFI.allSamples = [];
pCoordAppMFI.selectedSamples = [];
pCoordAppMFI.origData;
pCoordAppMFI.flowData;
pCoordAppMFI.tblData;
pCoordAppMFI.populations = [];
pCoordAppMFI.samples = [];
pCoordAppMFI.background;
pCoordAppMFI.foreground;

var displayAllm = function() {
    displayParallelPlotm();
}

/*
 * Display the Population Legend
*/
var displayPopTablem = function() {
    $('#popTablePCm tbody').empty();
    pCoordAppMFI.populations.map(function(d) {
        $('#popTablePCm tbody')
            .append('<tr><td align="center">'
                   + '<input type="checkbox" '
                   + 'id="'+ d + '" '
                   + 'checked class="popSelectPCm" value='
                   + d + '/></td><td>' + d
                   + '</td><td><span style="background-color:'
                   + color_palette[d]
                   + '">&nbsp;&nbsp;&nbsp;</span></td></tr>');
    });

    $('#popSelectAllPCm').click(function() {
        var checkAll = $("#popSelectAllPCm").prop('checked');
        if (checkAll) {
            $(".popSelectPCm").prop("checked", true);
        } else {
            $(".popSelectPCm").prop("checked", false);
        }

        pCoordAppMFI.selectedPopulations = [];
        $('.popSelectPCm').each(function() {
          if (this.checked) {
            pCoordAppMFI.selectedPopulations.push(parseInt(this.value));
          }
        })
        displayTableGridm();
        if (checkAll) {
            displayParallelPlotm();
        } else {
            updateParallelForegroundm();
        }
    });

    $('.popSelectPCm').click(function() {
        if ($('.popSelectPCm').length == $(".popSelectPCm:checked").length) {
            $('#popSelectAllPCm').prop("checked",true);
        } else {
            $('#popSelectAllPCm').prop("checked",false);
        }

        pCoordAppMFI.selectedPopulations = [];
        $('.popSelectPCm').each(function() {
          if (this.checked) {
            pCoordAppMFI.selectedPopulations.push(parseInt(this.value));
          }
        })
        displayTableGridm();
        updateParallelForegroundm();
    });
};

var updatePopTablem = function() {
    $('.popSelectPCm').each(function() {
        var pop = parseInt(this.value);
        if ($.inArray(pop,pCoordAppMFI.selectedPopulations) > -1) {
            this.checked = true;
        } else {
            this.checked = false;
        }
    })
}

/*
* Display Sample Legend
*/
var displaySmpTablem = function(){
    $('#smpTablePCm tbody').empty();
    pCoordAppMFI.samples.map(function(d) {
        $('#smpTablePCm tbody')
            .append('<tr><td>' + d 
                   + '</td><td align="center">'
                   + '<input type="checkbox" '
                   + 'id="' + d + '" '
                   + 'checked class="smpSelectPCm" value='
                   + d + '/></td></tr>');
    });

    $('#smpSelectAllPCm').click(function() {
        var checkAll = $("#smpSelectAllPCm").prop('checked');
        if (checkAll) {
            $(".smpSelectPCm").prop("checked", true);
        } else {
            $(".smpSelectPCm").prop("checked", false);
        }

        pCoordAppMFI.selectedSamples = [];
        $('.smpSelectPCm').each(function() {
          if (this.checked) {
            pCoordAppMFI.selectedSamples.push(parseInt(this.value));
          }
        })
        displayTableGridm();
        if (checkAll) {
            displayParallelPlotm();
        } else {
            updateParallelForegroundm();
        }
    });

    $('.smpSelectPCm').click(function() {
        if ($('.smpSelectPCm').length == $(".smpSelectPCm:checked").length) {
            $('#smpSelectAllPCm').prop("checked",true);
        } else {
            $('#smpSelectAllPCm').prop("checked",false);
        }

        pCoordAppMFI.selectedSamples = [];
        $('.smpSelectPCm').each(function() {
          if (this.checked) {
            pCoordAppMFI.selectedSamples.push(parseInt(this.value));
          }
        })
        displayTableGridm();
        updateParallelForegroundm();
    });
};

var updateSmpTablem = function() {
    $('.smpSelectPCm').each(function() {
        var smp = parseInt(this.value);
        if ($.inArray(smp,pCoordAppMFI.selectedSamples) > -1) {
            this.checked = true;
        } else {
            this.checked = false;
        }
    })
}
      
/*
 * Display Data table
*/
var displayTableGridm = function() {
    $("#tableDivPCm").empty();
    var displayData = pCoordAppMFI.tblData.filter(function(d) {
        var pop = parseInt(d['Population']);
        var smp = pCoordAppMFI.samples.indexOf(d.SampleName);
        if ($.inArray(pop,pCoordAppMFI.selectedPopulations) > -1 && $.inArray(smp, pCoordAppMFI.selectedSamples) > -1) {
          return d;
        }
    });
    
    var grid = d3.divgrid();
    d3.select("#tableDivPCm")
        .datum(displayData)
        .call(grid)
        .selectAll(".gridRow")
        .on({
          "mouseover": function(d) {
             var pop = parseInt(d['Population']);
             var smp = pCoordAppMFI.samples.indexOf(d.SampleName);
             pCoordAppMFI.selectedPopulations = [ pop ];
             pCoordAppMFI.selectedSamples = [smp];
             updateParallelForegroundm();
          },
          "mouseout": function() {
              pCoordAppMFI.selectedPopulations = [];
              pCoordAppMFI.selectedSamples = [];
              $('.popSelectPCm').each(function() {
                  if (this.checked) {
                     pCoordAppMFI.selectedPopulations.push(parseInt(this.value));
                  }
              })
              $('.smpSelectPCm').each(function() {
                  if (this.checked) {
                     pCoordAppMFI.selectedSamples.push(parseInt(this.value));
                  }
              })
              updateParallelForegroundm();
          }
        });
};


/*
 * Display The Main Plot
*/
var displayParallelPlotm = function() {
    var margin = {top: 30, right: 10, bottom: 10, left: 10};

    $("#plotDivPCm").empty();
    var h = $("#chartDivPCm").height()/1.5;
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
    
    var dimensions = d3.keys(pCoordAppMFI.flowData[0]).filter(function(d) {
        return (y[d] = d3.scale.linear()
            .domain(d3.extent(pCoordAppMFI.flowData,function(p) {
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

      var selectedPopulations = pCoordAppMFI.origData.filter(function(d) {
          var pop = parseInt(d.idx)
          var tf = actives.every(function(p,i) {
              return extents[i][0] <= pCoordAppMFI.flowData[pop-1][p] &&
                            pCoordAppMFI.flowData[pop-1][p] <= extents[i][1];
          })
          if (tf) {
              return pop;
          }
      });
      pCoordAppMFI.selectedPopulations = selectedPopulations.map(function(d) {
          return parseInt(d['Population']);
      });

      var selectedSamples = pCoordApp.origData.filter(function(d) {
          var smp = pCoordAppMFI.samples.indexOf(d.SampleNumber);
          var tf = actives.every(function(p,i) {
              return extents[i][0] <= pCoordApp.flowData[smp][p] &&
                            pCoordApp.flowData[smp][p] <= extents[i][1];

          })
          if (tf) {
              return smp;
          }
      });
      pCoordApp.selectedSamples = selectedSamples.map(function(d) {
          return parseInt(d.SampleNumber);
      });


      updateParallelForegroundm();
      updatePopTablem();
      updateSmpTablem();
      displayTableGridm();
    }


    // Display paths in light gray color, to use as reference
    pCoordAppMFI.background = svg.append("g")
       .attr("class", "background")
       .selectAll("path")
       .data(pCoordAppMFI.flowData)
       .enter()
       .append("path")
       .attr("d", path);

    // Add foreground lines for focus, color by population.
    pCoordAppMFI.foreground = svg.append("g")
        .attr("class", "foreground")
        .selectAll("path")
        .data(pCoordAppMFI.origData)
        .enter()
        .append("path")
        .attr("d", function(d,i) {var pop = parseInt(d['Population']);
              return path(pCoordAppMFI.flowData[pop -1 ]);})
        .attr("stroke",function(d){var pop = parseInt(d['Population']);
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
            pCoordAppMFI.background.attr("visibility", "hidden");
          })
          .on("drag", function(d) {
            dragging[d] = Math.min(width, Math.max(0, d3.event.x));
            pCoordAppMFI.foreground.attr("d", path);
            dimensions.sort(function(a, b) { return position(a) - position(b); });
            x.domain(dimensions);
            g.attr("transform", function(d) { return "translate(" + position(d) + ")"; })
          })
          .on("dragend", function(d) {
            delete dragging[d];
            transition(d3.select(this)).attr("transform", "translate(" + x(d) + ")");
            transition(pCoordAppMFI.foreground).attr("d", path);
            pCoordAppMFI.background
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

var updateParallelForegroundm = function() {
   pCoordAppMFI.foreground[0].map(function(d) {
       var pop = parseInt(d['__data__']['Population']);
       var smp = pCoordAppMFI.samples.indexOf(d['__data__']['SampleName']);
       
       if ($.inArray(pop,pCoordAppMFI.selectedPopulations) < 0 && $.inArray(smp,pCoordAppMFI.selectedSamples) < 0) {
         d.style.display = "none";
       } else {
         d.style.display = null;
       }
   });
};

/*
 * Retrieve the data, then call display functions
*/
var displayParallelCoordinatesMFI = function() {
    var inputFile = "pcoord_multiple_file.tsv";
    d3.tsv(inputFile, function(error, data) {
        if (error) {
            alert("Problem Retrieving Data");
            return;
        }
   
        pCoordAppMFI.tblData = $.extend(true,[],data);

        pCoordAppMFI.origData = $.extend(true,[],data);
        pCoordAppMFI.origData.forEach(function(d,idx) {
            d.idx = idx;
            if (!pCoordAppMFI.populations.includes(d.Population)){
                pCoordAppMFI.populations.push(d.Population)
            }
            if (!pCoordAppMFI.samples.includes(d.SampleName)){
                pCoordAppMFI.samples.push(d.SampleName)
            }
        })

        for (var i = 0; i < pCoordAppMFI.populations.length; i++) {
            pCoordAppMFI.allPopulations.push(i);
            pCoordAppMFI.selectedPopulations.push(i);
        }
        for (var i = 0; i < pCoordAppMFI.samples.length; i++) {
            pCoordAppMFI.allSamples.push(i);
            pCoordAppMFI.selectedSamples.push(i);
        }
        
        /* 
         * For the plot use only the MFI information
         * for each populations. Store in flowData
        */
        pCoordAppMFI.flowData = $.extend(true,[],data);
        pCoordAppMFI.flowData.forEach(function(d) {
            delete d['Population'];delete d['SampleName']; delete d['Percentage']; 
        })
 

        displayPopTablem();
        displaySmpTablem();
        displayTableGridm();
        displayParallelPlotm();
    
        $("#resetDisplayMFIpop").on("click",function() {
            for (var i = 0; i < pCoordAppMFI.populations.length; i++) {
                pCoordAppMFI.allPopulations.push(i);
                pCoordAppMFI.selectedPopulations.push(i);
            }
            for (var i = 0; i < pCoordAppMFI.samples.length; i++) {
                pCoordAppMFI.allSamples.push(i);
                pCoordAppMFI.selectedSamples.push(i);
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
