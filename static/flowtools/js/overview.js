var scatterData2D = {};
var scatterData3D = {};
var scatterData3DMFI = {};
var scatterDataMFI = {};

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


var updateMFIDisplay = function(data) {
    $('#mfiDiv').empty();
    var table = $("<table/>");
    $.each(data, function(rowIndex,r) {
        var row = $("<tr/>");
        $.each(r,function(colIndex,c) {
            row.append($("<t"+(rowIndex ==0 ? "h" : "d")+" align='right'/>").text(c));
        });
        table.append(row);

    });
    $('#mfiDiv').html(table);
}

var updateOverviewPlotDisplay = function(data) {
    $('#overviewPlotDiv').empty();
    $('#overviewPlotDiv').html(data);
}

var displayMFI = function() {
    var url = "flow.mfi_pop";
    $.ajax({
       url: url,
       dataType: "text",
       success: function(text) {
           data = d3.tsv.parseRows(text).map(function(row) {
                   return row.map(function(value) {
                       return value;
                   });
            });

            updateMFIDisplay(data);
       }
    });
}

var displayOverviewPlot = function() {
    var url = "flow.overview";
    $.ajax({
       url: url,
       dataType: "text",
       success: function(data) {
                  updateOverviewPlotDisplay(data);
                }
    });
}

var displayScatter2D = function() {
    var url = "flow.sample";
    $.ajax({
        url: url,
        dataType: "text",
        success: function(text) {
            var mfi_url = "flow.mfi_pop";
            $.ajax({
                url: mfi_url,
                dataType: "text",
                success: function(mfi_text) {
                   preprocessScatterDataMFI(mfi_text);
                   preprocessScatterData2D(text);
                   displayScatterToolbar2D();
                   displayScatterPopulation2D();
                   processScatterData2D();
                   processScatterDataMFI2D();
                   displayScatterPlot2D();
                   $(window).on('resize',function() {
                       waitForFinalEvent(function() {
                           processScatterData2D();
                           displayScatterPlot2D();
                       },500,"resize2D");
                   });
               }
            });
        }
    });
}

var displayScatter3D = function() {
    var url = "flow.sample";
    $.ajax({
       url: url,
       dataType: "text",
       success: function(text) {
            var mfi_url = "flow.mfi_pop";
            $.ajax({
                url: mfi_url,
                dataType: "text",
                success: function(mfi_text) {
                   preprocessScatterDataMFI(mfi_text);
                   preprocessScatterData3D(text);
                   displayScatterToolbar3D();
                   displayScatterPopulation3D();
                   processScatterData3D();
                   processScatterDataMFI3D();
                   displayScatterPlot3D();
                   $(window).on('resize',function() {
                       waitForFinalEvent(function() {
                           processScatterData3D();
                           displayScatterPlot3D();
                       },500,"resize3D");
                   });
               }
           });
       }
    });
}


var displayScatter3DMFI = function() {
    var url = "flow.mfi_pop";
    $.ajax({
       url: url,
       dataType: "text",
       success: function(text) {
           preprocessScatterData3DMFI(text);
           displayScatterToolbar3DMFI();
           displayScatterPopulation3DMFI();
           processScatterData3DMFI();
           displayScatterPlot3DMFI();
           $(window).on('resize',function() {
               waitForFinalEvent(function() {
                   processScatterData3DMFI();
                   displayScatterPlot3DMFI();
               },500,"resize3DMFI");
           });
       }
    });
}
