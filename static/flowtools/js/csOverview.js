//var url = "csOverview.tsv";
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

/*
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
}
*/


var updatePopPropDisplay = function(data) {
    $('#propDiv').empty();
    var table = $("<table/>");
    $.each(data, function(rowIndex,r) {
        var row = $("<tr/>");
        $.each(r,function(colIndex,c) {
            row.append($("<t"+(rowIndex ==0 ? "h" : "d")+" align='right'/>").text(c));
        });
        table.append(row);

    });
    $('#propDiv').html(table);
}

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
}

var displaystackedA = function() {
    $.ajax({
        url: url,
        dataType: "text",
        success: function(textA) {
//           objA = preprocess(text);
            preprocessA(textA)
            displaytoolbarA();
        }
    })
}

var displaystackedB = function() {
    $.ajax({
        url: url,
        dataType: "text",
        success: function(textB) {
//           objB = preprocess(text);
            preprocessB(textB)
            displaytoolbarB();
        }
    })
}
var displaypCoord = function() {
    $.ajax({
        url: url,
        dataType: "text",
        success: function(text) {
//           objPC = preprocess(text);
            preprocessPC(text)
            displaytoolbarPC();
        }
    })
}


