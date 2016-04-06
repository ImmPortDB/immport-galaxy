var allPopulationsB = []
var selectedPopulationsB = []
var csdataB;

var preprocessB = function(text){
    csdataB = d3.tsv.parseRows(text).map(function(row) {
        return row.map(function(value) {
            if (isNaN(value)) {
                return value;
            }
            return +value;
        })
    })
}


var displaytoolbarB = function(){
    $("#updateDisplayB").on("click",function() {
      selectedPopulationsB = [];
      $('.popSelectB').each(function() {
        if (this.checked) {
          selectedPopulationsB.push(parseInt(this.value));
        }
      })
      updateCrossSampleStackedB(csdataB);
    });
    displayCrossSampleStackedB(csdataB);
}

var displayPopulationLegendB = function() {
    allPopulationsB.map(function(value,index) {
        $('#popTableB tr')
            .last()
            .after('<tr><td align="center"><input type="checkbox" checked class="popSelectB" value='
                   + value + '/></td><td>' + value + '</td><td><span style="background-color:' +
                   color_palette[value] + '">&nbsp;&nbsp;&nbsp;</span></td></tr>');
    });

    $('#popSelectAllB').click(function() {
        var checkAll = $("#popSelectAllB").prop('checked');
        if (checkAll) {
            $(".popSelectB").prop("checked", true);
        } else {
            $(".popSelectB").prop("checked", false);
        }
    });

    $('.popSelectB').click(function() {
        if ($('.popSelectB').length == $(".popSelectB:checked").length) {
            $('#popSelectAllB').prop("checked",true);
        } else {
            $('#popSelectAllB').prop("checked",false);
        }
    });
}

var displayCrossSampleStackedB = function(csdataB) {
	$("#plotDivB").empty();
	var h = $(window).height() - 200;
	$("#plotDivB").height(h);

    for (var i = 2; i < csdataB[0].length; i++) {
        allPopulationsB.push(i - 1);
        selectedPopulationsB.push(i - 1);
    }

    $(window).on('resize',function() {
        waitForFinalEvent(function() {
            updateCrossSampleStackedB(csdataB);
        },500,"resizeCrossSampleStackedB");
    })

    displayPopulationLegendB();
    updateCrossSampleStackedB(csdataB);
}

var updateCrossSampleStackedB = function(csdataB) {
	$("#plotDivB").empty();
	var h = $(window).height() - 200;
	$("#plotDivB").height(h);

    var tracesB = [];
	var x_values = [];
	for ( var i = 1; i < csdataB.length; i++ ) {
		x_values.push(String(csdataB[i][1]));
	}

    var totals = []
    for (var k = 1; k < csdataB.length; k++){
        totals[k] = 0;
        for (var m = 2; m < csdataB[0].length; m++){
            for (var n = 0; n < selectedPopulationsB.length; n++){
                if (csdataB[0][m] === selectedPopulationsB[n]) {
                    totals[k] += csdataB[k][m];
                }
            }
        }
    }

	for (var i = 0; i < selectedPopulationsB.length; i++) {
		pop = selectedPopulationsB[i]
		var popName = "Pop " + pop;
		var y_values = []

		for (var j = 1; j < csdataB.length; j++) {
		    var newvalue = (csdataB[j][pop + 1] / totals[j]) * 100;
 			y_values.push(newvalue)
		}

		var obj = { x: x_values,
			        y: y_values,
			        hoverinfo: "none",
			        name: popName,
			        type: 'bar',
			        marker: { color: color_palette[pop]}
			       } 
		tracesB.push(obj)
	}

    var layoutB = {
       	barmode: 'stack',
       	title: '',
       	showlegend: false
    };

    Plotly.newPlot('plotDivB',tracesB,layoutB,{displayModeBar: false});	
}
