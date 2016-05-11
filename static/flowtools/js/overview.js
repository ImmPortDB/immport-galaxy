var scatterData2D = {};
var scatterData3D = {};
var scatterData3DMFI = {};
var scatterDataMFI = {};
var tableContent;
var newNames = {};

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

var updateOverviewPlotDisplay = function(data) {
    $('#overviewPlotDiv').empty();
    $('#overviewPlotDiv').html(data);
};

var displayMFI = function() {
    var url = "flow.mfi_pop";
    d3.tsv(url, function(error, data){
        if (error){
            alert("Problem retrieving data");
            return;
        }
        function handleSubmit(method, url, d, successCallBack, errorCallBack) {
            var output = {data : mfiTableData};
            successCallBack(output);   
        };

        $('#mfiDiv').empty();
        var mfiTableData = $.extend(true,[],data);
        mfiTableData.forEach(function(d){
            d.Comment = d.Population;
            newNames[parseInt(d.Population)] = d.Comment;
        })
        var mfiHdgs = Object.keys(mfiTableData[0]);
        //var mfiData = mfiTableData.filter(function(d){return d});
        tableContent = $.extend(true, [], mfiTableData);
        var mfiTableHeadings = [];
        var mfiTargets = [];
        var mfiEditorData =[];
        mfiHdgs.forEach(function(d,i) {
            mfiTableHeadings.push({"data": d, "title": d});
            mfiEditorData.push({"label" : d, "name" : d});
        });
        
        var mfiTableHTML = '<table id="mfitable" class="dtable display compact" cellspacing="0" width="100%"/>';

        var popcol = mfiHdgs.length - 2;
        for (var i=0; i<popcol;i++){
            mfiTargets.push(i);
        }
        $('#mfiDiv').html(mfiTableHTML);
        var editor = new $.fn.dataTable.Editor( {
            ajax: handleSubmit,
            table: '#mfitable',
            fields: mfiEditorData,
            idSrc: 'Population'
        });
        
        $('#mfitable').on( 'click', 'tbody td:last-child', function (e) {
            editor.bubble( this );
        });
        var mfiTable = $('#mfitable').DataTable({
            columns: mfiTableHeadings,
            data: mfiTableData,
            order: [[ popcol, "asc" ]],
            pageLength: 25, 
            dom: '<"top"Bi>t<"bottom"lp><"clear">',
            columnDefs: [{ 
                targets: mfiTargets,
                className: "dt-body-right"
            }],
            buttons: [
                'copy', 'pdfHtml5','csvHtml5', 'colvis'
            ],
            colReorder: true,
            select: true
        });
        editor.on( 'preSubmit', function(e, object, action){
            var data = object.data;
            var key = Object.keys(data)[0];
            var count = object.data[key]['Comment'];
            mfiTableData.forEach(function(d){
                if (d.Population === key) {
                    d.Comment = count;
                    newNames[parseInt(d.Population)] = count;
                }
            });
            tableContent = $.extend(true, [], mfiTableData);
        });
    });
};

var displayOverviewPlot = function() {
    var url = "flow.overview";
    $.ajax({
       url: url,
       dataType: "text",
       success: function(data) {
                  updateOverviewPlotDisplay(data);
                }
    });
};

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
                   displayScatterPopulation2D(newNames);
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
                   displayScatterPopulation3D(newNames);
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
           displayScatterPopulation3DMFI(newNames);
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
