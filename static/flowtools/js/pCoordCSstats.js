var allPopulationsPC = []
var selectedPopulationsPC = []
var csdataPC;

var preprocessPC = function(text){
    csdataPC = d3.tsv.parseRows(text).map(function(row) {
        return row.map(function(value) {
            if (isNaN(value)) {
                return value;
            }
            return +value;
        })
    })
}

var displaytoolbarPC = function(){
    $("#updateDisplayPC").on("click",function() {
      selectedPopulationsPC = [];
      $('.popSelectPC').each(function() {
        if (this.checked) {
          selectedPopulationsPC.push(parseInt(this.value));
        }
      })
      updateCrossSamplepCoord();
    });
    displayCrossSamplepCoord(csdataPC);
}

var displayPopulationLegendPC = function() {
    allPopulationsPC.map(function(value,index) {
        $('#popTablePC tr')
            .last()
            .after('<tr><td align="center"><input type="checkbox" checked class="popSelectPC" value='
                   + value + '/></td><td>' + value + '</td><td><span style="background-color:' +
                   color_palette[value] + '">&nbsp;&nbsp;&nbsp;</span></td></tr>');
    });

    $('#popSelectAllPC').click(function() {
        var checkAllPC = $("#popSelectAllPC").prop('checked');
        if (checkAllPC) {
            $(".popSelectPC").prop("checked", true);
        } else {
            $(".popSelectPC").prop("checked", false);
        }
    });

    $('.popSelectPC').click(function() {
        if ($('.popSelectPC').length == $(".popSelectPC:checked").length) {
            $('#popSelectAllPC').prop("checked",true);
        } else {
            $('#popSelectAllPC').prop("checked",false);
        }
    });
}

var displayCrossSamplepCoord = function(csdataPC) {
	$("#plotDivPC").empty();
	var h = $(window).height() - 200;
	$("#plotDivPC").height(h);

    for (var i = 2; i < csdataPC[0].length; i++) {
        allPopulationsPC.push(i - 1);
        selectedPopulationsPC.push(i - 1);
    }

    $(window).on('resize',function() {
        waitForFinalEvent(function() {
            updateCrossSamplepCoord();
        },500,"resizeCrossSampleStacked");
    })

    displayPopulationLegendPC();
    updateCrossSamplepCoord();
}

var updateCrossSamplepCoord = function() {
	$("#plotDivPC").empty();
	var h = $(window).height() - 200;
	$("#plotDivPC").height(h);

    var traces = [];
	var x_values = [];
	for ( var i = 1; i < csdataPC.length; i++ ) {
		x_values.push(String(csdataPC[i][1]));
	}

    var totals = []
    for (var k = 1; k < csdataPC.length; k++){
        totals[k] = 0;
        for (var m = 2; m < csdataPC[0].length; m++){
            for (var n = 0; n < selectedPopulationsPC.length; n++){
                if (csdataPC[0][m] === selectedPopulationsPC[n]) {
                    totals[k] += csdataPC[k][m];
                }
            }
        }
    }

	for (var i = 0; i < selectedPopulationsPC.length; i++) {
		pop = selectedPopulationsPC[i]
		var popName = "Pop " + pop;
		var y_values = []

		for (var j = 1; j < csdataPC.length; j++) {
		    var newvalue = (csdataPC[j][pop + 1] / totals[j]) * 100;
 			y_values.push(newvalue)
		}

		var obj = { x: x_values,
			        y: y_values,
			        hoverinfo: "none",
			        name: popName,
			        type: 'bar',
			        marker: { color: color_palette[pop]}
			       } 
		traces.push(obj)
	}

    var layout = {
       	barmode: 'stack',
       	title: '',
       	showlegend: false
    };

    Plotly.newPlot('plotDivPC',traces,layout,{displayModeBar: false});	
}
