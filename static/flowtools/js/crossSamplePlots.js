var displayToolbar = function(plotconfig){
    $(plotconfig.displaybutton).on("click",function() {
      plotconfig.selectedPopulations = [];
      $(plotconfig.popSelectj).each(function() {
        if (this.checked) {
          plotconfig.selectedPopulations.push(parseInt(this.value));
        }
      })
      updatePlot(plotconfig);
    });
    displayPlot(plotconfig);
};

var displayPlot = function(plotconfig) {
	$(plotconfig.plotdivj).empty();
	var h = $(window).height() - 200;
	$(plotconfig.plotdivj).height(h);

    for (var i = 2; i < plotconfig.csdata[0].length; i++) {
        plotconfig.allPopulations.push(i - 1);
        plotconfig.selectedPopulations.push(i - 1);
    }

    $(window).on('resize',function() {
        waitForFinalEvent(function() {
            updatePlot(plotconfig);
        },500,"resizePlot");
    })

    displayPopulationLegend(plotconfig);
    updatePlot(plotconfig);
};

var updatePlot = function(plotconfig) {
	$(plotconfig.plotdivj).empty();
	var h = $(window).height() - 200;
	$(plotconfig.plotdivj).height(h);

    var traces = [];
	var tmptraces = [];
	var x_values = [];
	for (var i = 1; i < plotconfig.csdata.length; i++) {
		x_values.push(String(plotconfig.csdata[i][1]));
	}

    var totals = []
    for (var k = 1; k < plotconfig.csdata.length; k++){
        totals[k] = 0;
        for (var m = 2; m < plotconfig.csdata[0].length; m++){
            for (var n = 0; n < plotconfig.selectedPopulations.length; n++){
                if (plotconfig.csdata[0][m] === plotconfig.selectedPopulations[n]) {
                    totals[k] += plotconfig.csdata[k][m];
                }
            }
        }
    }

	for (var i = 0; i < plotconfig.selectedPopulations.length; i++) {
		pop = plotconfig.selectedPopulations[i];
		var popName = "Pop " + pop;
		var y_values = [];

		for (var j = 1; j < plotconfig.csdata.length; j++) {
		    var newvalue = (plotconfig.csdata[j][pop + 1] / totals[j]) * 100;
 			y_values.push(newvalue)
		}

		var obj
		 
		if (plotconfig.type === "areaplot"){
			obj = { 
				x: x_values,
				y: y_values,
		        hoverinfo: "none",
		        name: popName,
		        type: 'area',
				fill: 'tonexty', 
		        marker: { color: color_palette[pop]}
	       };
		}
		if (plotconfig.type === "barplot"){
			obj = { 
				x: x_values,
				y: y_values,
		        hoverinfo: "none",
		        name: popName,
		        type: 'bar',
		        marker: { color: color_palette[pop]}
	       };
		}
		tmptraces.push(obj)
	}

    var layout;
	if (plotconfig.type === "barplot"){
		layout = {
	       	title: '',
			barmode: 'stack',
	       	showlegend: false
	    };
		traces = tmptraces;
	}
	if (plotconfig.type === "areaplot"){
		function stacked(trcs) {
		    for(var i=1; i<trcs.length; i++) {
		        for(var j=0; j<(Math.min(trcs[i]['y'].length, trcs[i-1]['y'].length)); j++) {
		            trcs[i]['y'][j] += trcs[i-1]['y'][j];
		        }
		    }
		    return trcs;
		}

		layout = {
	       	title: '',
	       	showlegend: false
	    };
		traces = stacked(tmptraces);
	}
    Plotly.newPlot(plotconfig.plotdiv,traces,layout,{displayModeBar: false});	
	
};
