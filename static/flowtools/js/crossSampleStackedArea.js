var allPopulationsA = []
var selectedPopulationsA = []
var csdataA;

var preprocessA = function(text){
    csdataA = d3.tsv.parseRows(text).map(function(row) {
        return row.map(function(value) {
            if (isNaN(value)) {
                return value;
            }
            return +value;
        })
    })
}

var displaytoolbarA = function(){
    $("#updateDisplayA").on("click",function() {
      selectedPopulationsA = [];
      $('.popSelectA').each(function() {
        if (this.checked) {
          selectedPopulationsA.push(parseInt(this.value));
        }
      })
      updateCrossSampleStackedA();
    });
    displayCrossSampleStackedA(csdataA);
}

var displayPopulationLegendA = function() {
    allPopulationsA.map(function(value,index) {
        $('#popTableA tr')
            .last()
            .after('<tr><td align="center"><input type="checkbox" checked class="popSelectA" value='
                   + value + '/></td><td>' + value + '</td><td><span style="background-color:' +
                   color_palette[value] + '">&nbsp;&nbsp;&nbsp;</span></td></tr>');
    });

    $('#popSelectAllA').click(function() {
        var checkAllA = $("#popSelectAllA").prop('checked');
        if (checkAllA) {
            $(".popSelectA").prop("checked", true);
        } else {
            $(".popSelectA").prop("checked", false);
        }
    });

    $('.popSelectA').click(function() {
        if ($('.popSelectA').length == $(".popSelectA:checked").length) {
            $('#popSelectAllA').prop("checked",true);
        } else {
            $('#popSelectAllA').prop("checked",false);
        }
    });
}

var displayCrossSampleStackedA = function(csdataA) {
    for (var i = 2; i < csdataA[0].length; i++) {
        allPopulationsA.push(i - 1);
        selectedPopulationsA.push(i - 1);
    }

    $(window).on('resize',function() {
        waitForFinalEvent(function() {
            updateCrossSampleStackedA();
        },500,"resizeCrossSampleStackedA");
    })

    displayPopulationLegendA();
    updateCrossSampleStackedA();
}

var updateCrossSampleStackedA = function() {
    $("#plotDivA").empty();
    var h = $(window).height() - 200;
    $("#plotDivA").height(h);

    var tracesA = [];
    var x_values = [];
    for ( var i = 1; i < csdataA.length; i++ ) {
        x_values.push(String(csdataA[i][1]));
    }

    var totals = []
    for (var k = 1; k < csdataA.length; k++){
        totals[k] = 0;
        for (var m = 2; m < csdataA[0].length; m++){
            for (var n = 0; n < selectedPopulationsA.length; n++){
                if (csdataA[0][m] === selectedPopulationsA[n]) {
                    totals[k] += csdataA[k][m];
                }
            }
        }
    }

    for (var i = 0; i < selectedPopulationsA.length; i++) {
        pop = selectedPopulationsA[i]
        var popName = "Pop " + pop;
        var y_values = []
       
        for (var j = 1; j < csdataA.length; j++) {
            var newvalue = (csdataA[j][pop + 1] / totals[j]) * 100;
             y_values.push(newvalue)
        }

        var obj = { x: x_values,
                    y: y_values,
                    hoverinfo: "none",
                    name: popName,
                    type: 'area',
                    fill: 'tonexty',
                    marker: { color: color_palette[pop]}
                   } 
        tracesA.push(obj)
    }

    function stackedArea(traces) {
        for(var i=1; i<traces.length; i++) {
            for(var j=0; j<(Math.min(traces[i]['y'].length, traces[i-1]['y'].length)); j++) {
                traces[i]['y'][j] += traces[i-1]['y'][j];
            }
        }
        return traces;
    }
    
    var layoutA = {
           title: '',
           showlegend: false
    };

    Plotly.newPlot('plotDivA',stackedArea(tracesA),layoutA,{displayModeBar: false});    
}
