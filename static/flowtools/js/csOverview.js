var url = "./csOverview.tsv";
var pctablecontent;
var newSmpNames= {};
var newPopNames = {};
var configBarplot = {};
var configAreaplot = {};

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

var displayPopulationLegend = function(plotconfig) {
    $(plotconfig.table).empty();
    plotconfig.allPopulations.map(function(value,index) {
        $(plotconfig.table)
			.append('<tr><td align="center">' 
			+ '<input type="checkbox" checked class=' + plotconfig.popSelect 
			+ ' value=' + value + '/></td><td title="' + newPopNames[value] + '">' 
			+ newPopNames[value] + '</td><td><span style="background-color:' 
			+ color_palette[value] + '">&nbsp;&nbsp;&nbsp;</span></td></tr>');
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
    
    $(plotconfig.popSelectj).each(function() {
        var selectedpopn = parseInt(this.value);
        if ($.inArray(selectedpopn,plotconfig.selectedPopulations) > -1) {
            this.checked = true;
        } else {
            this.checked = false;
        }
    });    
};

var displayProp = function() {
    d3.text(url, function(error, data){
        if (error){
            alert("Problem retrieving data");
            return;
        }
        var propHeadings = data.split("\n")[0].split("\t");
        propHeadings.unshift("Comment");
        data = d3.tsv.parse(data);
        function propHandle(method, url, d, successCallBack, errorCallBack) {
            var output = {data : propTableData};
            successCallBack(output);   
        };

        function popHandle(method, url, d, successCallBack, errorCallBack) {
            var output = {data : popTableData};
            successCallBack(output);   
        };

        var fileID = [];
        var sampleNames = [];
        var popTableData = [];
        var propTableData = $.extend(true,[],data);
        propTableData.forEach(function(d){
            d.Comment = d.SampleName;
            newSmpNames[d.SampleName] = d.Comment;
            fileID.push(d.FileID);
            sampleNames.push(d.SampleName);
        })
        var propTableHeadings = [];
        var propTargets = [];
        var popTableHeadings = [];
        var propEditorData = [];
        var popEditorData = [];
        var smpcol = 2;
        for (var i = 3, j = propHeadings.length; i < j; i++){
            propTargets.push(i);
        }
        propHeadings.forEach(function(d){
            propTableHeadings.push({"data":d, "title":d});
            propEditorData.push({"label":d,"name":d});
            if (d != 'Comment' && d != 'SampleName' && d != "FileID"){
                newPopNames[d] = d.toString();
                popTableHeadings.push({"data":d, "title":d});
                popEditorData.push({"label":d,"name":d});
            }
        });        
        popTableData.push(newPopNames);
        pctablecontent = $.extend(true,[],propTableData);

        $('#propDiv').empty();
        var propHTML = '<table id="proptable" class="dtable display compact nowrap" cellspacing="0" width="100%"/>';
        $('#propDiv').html(propHTML);
        var smpEditor = new $.fn.dataTable.Editor( {
            ajax: propHandle,
            table: '#proptable',
            fields: propEditorData,
            idSrc: 'SampleName'
        });
        
        $('#proptable').on( 'click', 'tbody td:first-child', function (e) {
            smpEditor.bubble( this );
        });
        var propTable = $('#proptable').DataTable({
            columns: propTableHeadings,
            data: propTableData,
            order: [[ smpcol, "asc" ]],
            pageLength: 10, 
            scrollX: true,
            scrollCollapse: true,
            dom: '<"top"Bi>t<"bottom"lp><"clear">',
            columnDefs: [{ 
                targets: propTargets,
                className: "dt-body-right",
                render: function(data, type, row){
                        return parseFloat(data).toFixed(2) + '%';
                }
              },
              {
                targets: [smpcol - 1, smpcol, smpcol + 1],
                className: "dt-body-left",
              }
            ],
            buttons: [
                'copy', 'pdfHtml5','csvHtml5', 'colvis'
            ],
            colReorder: {
                fixedColumnsLeft:1
            },
            select: true
        });
        
        // Add titles to File ID and Sample Name
        $('#proptable tr').each(function(i,d){
            if (i > 0) {
                $(this).find('td').each(function(j,e){
                    if (j == 1 ) {
                        $(this).prop('title', fileID[i - 1] );
                    }
                    if (j == 2) {
                        $(this).prop('title', sampleNames[i - 1]);
                    }
                });
            }
        });
        
        
        // Add a table below to rename pops
        // Might want to change that some other time?
        var popHTML = '<table id="popnamestable" class="popt dtable display nowrap compact" cellspacing="0" width="100%"/>';
        $('#popnamesDiv').html(popHTML);
        var popEditor = new $.fn.dataTable.Editor( {
            ajax: popHandle,
            table: '#popnamestable',
            fields: popEditorData,
            idSrc: '1'
        });
        
        $('#popnamestable').on( 'click', 'tbody td', function (e) {
            popEditor.bubble( this );
        });
        var popTable = $('#popnamestable').DataTable({
            columns: popTableHeadings,
            dom: 't',
            select: true,
            data: popTableData
        });
              
        smpEditor.on( 'preSubmit', function(e, object, action){
            var data = object.data;
            var key = Object.keys(data)[0];
            var count = object.data[key]['Comment'];
            
            propTableData.forEach(function(d){
                if (d.SampleName === key) {
                    d.Comment = count;
                    newSmpNames[d.SampleName] = count;
                }
            });
            pctablecontent = $.extend(true, [], propTableData);
        });
        popEditor.on( 'preSubmit', function(e, object, action){
            var data = object.data;
            var key = Object.keys(data['1'])[0];
            var count = object.data['1'][key];
            popTableData[0][key] = count;
            newPopNames[key] = count;
        });
    });
};

var displayStackedAreaPlot = function() {
    $.ajax({
        url: url,
        dataType: "text",
        success: function(text) {
			configAreaplot = {
				displaybutton : '#updateDisplayA',
				popSelectj : '.popSelectA',
				plotdivj : '#plotDivA',
				csdata : preprocess(text),
				plotdiv : 'plotDivA',
				type : "areaplot",
				table : '#popTableA tbody',
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
			configBarplot = {
				displaybutton : "#updateDisplayB",
				popSelectj : '.popSelectB',
				plotdivj : "#plotDivB",
				csdata : preprocess(text),
				plotdiv : 'plotDivB',
				type : "barplot",
				table : '#popTableB tbody',
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

