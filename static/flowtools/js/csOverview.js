//var url = "./data/csOverview.tsv";
var url = "./csOverview.tsv";

var waitForFinalEvent = (function () {
  var timers = {};
  return function (callback, ms, uniqueId) {
    if (!uniqueId) {
      uniqueId = "Don't call this twice without a uniqueId";
    }
    if (timers[uniqueId]) {
      clearTimeout (timers[uniqueId]);
    }
    timers[uniqueId] = setTimeout(callback, ms);
  };
})();

var preprocess = function(text){
    var crossSampleData = d3.tsv.parseRows(text).map(function(row) {
        return row.map(function(value) {
            if (isNaN(value)) {
                return value;
            }
            return +value;
        })
    })
    return crossSampleData;
};

var updatePopPropDisplay = function(data) {
    $('#propDiv').empty();
    var table = $("<table/>");
    $.each(data, function(rowIndex,r) {
        var row = $("<tr/>");
        $.each(r,function(colIndex,c) {
			if (colIndex >= 1){
				row.append($("<t"+(rowIndex ==0 ? "h" : "d")+" align='right'/>").text(c));
			}
		});
        table.append(row);

    });
    $('#propDiv').html(table);
};

var displayPopulationLegend = function(plotconfig) {
    plotconfig.allPopulations.map(function(value,index) {
        $(plotconfig.table)
			.last()
 			.after('<tr><td align="center"><input type="checkbox" checked class=' + plotconfig.popSelect + 
				   ' value=' + value + '/></td><td>' + value + '</td><td><span style="background-color:' +
				   color_palette[value] + '">&nbsp;&nbsp;&nbsp;</span></td></tr>');
    });

    $(plotconfig.popSelectAll).click(function() {
        var checkAll = $(plotconfig.popSelectAll).prop('checked');
        if (checkAll) {
            $(plotconfig.popSelectj).prop("checked", true);
        } else {
            $(plotconfig.popSelectj).prop("checked", false);
        }
    });

    $(plotconfig.popSelectj).click(function() {
        if ($(plotconfig.popSelectj).length == $(plotconfig.popSelectCheck).length) {
            $(plotconfig.popSelectAll).prop("checked",true);
        } else {
            $(plotconfig.popSelectAll).prop("checked",false);
        }
    });
};

var displayProp = function() {
    $.ajax({
        url: url,
        dataType: "text",
        success: function(text) {
            data = d3.tsv.parseRows(text).map(function(row) {
                return row.map(function(value) {
                    return value;
                });
            });
            updatePopPropDisplay(data);
        }
    });
};

var displayStackedAreaPlot = function() {
    $.ajax({
        url: url,
        dataType: "text",
        success: function(text) {
			var configAreaplot = {
				displaybutton : '#updateDisplayA',
				popSelectj : '.popSelectA',
				plotdivj : '#plotDivA',
				csdata : preprocess(text),
				plotdiv : 'plotDivA',
				type : "areaplot",
				table : '#popTableA tr',
				popSelect : "popSelectA",
				allPopulations : [],
				selectedPopulations : [],
				popSelectAll : '#popSelectAllA',
				popSelectCheck : '.popSelectA:checked',
			}
            displayToolbar(configAreaplot);
        }
    })
};

var displayStackedBarplot = function() {
    $.ajax({
        url: url,
        dataType: "text",
        success: function(text) {
			var configBarplot = {
				displaybutton : "#updateDisplayB",
				popSelectj : '.popSelectB',
				plotdivj : "#plotDivB",
				csdata : preprocess(text),
				plotdiv : 'plotDivB',
				type : "barplot",
				table : '#popTableB tr',
				popSelect : "popSelectB",
				allPopulations : [],
				selectedPopulations : [],
				popSelectAll : '#popSelectAllB',
				popSelectCheck: ".popSelectB:checked",
				checkAll : ""
			}
            displayToolbar(configBarplot);
        }
    })
};

