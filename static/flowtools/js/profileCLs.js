var cl_table = './CLprofiles.txt';
var scores_table = './scores.txt';

var displayCLTable = function(){

    d3.text(cl_table, function(error, data){
        if (error){
            alert("Problem retrieving data");
            return;
        }
        var clHdgs = data.split("\n")[0].split("\t");
        data = d3.tsv.parse(data);

        var clHTML = '<table id="cltable" class="display compact" cellspacing="0" width="100%"/>';
        $('#clprofiles').html(clHTML);

        var clTableData = $.extend(true, [], data)
        var clHeadings = [];
        
        clHdgs.forEach(function(d,i){
            clHeadings.push({"data" : d, "title" : d});
        });
        
        var clTable = $('#cltable').DataTable({
            columns: clHeadings,
            dom: '<"top"Bi>t<"bottom"lp><"clear">',
            pageLength: 25, 
            order: [[ 0, "asc" ]],
            data: clTableData,
            buttons: [
                'copy', 'pdfHtml5','csvHtml5'
            ],
            columnDefs: [
              {
                targets: [0,2,3],
                className: "smallcols"
              },
              {
                targets: 4,
                className: "dt-body-left"
              },
              {
                targets: [5,6],
                className: "firstcol"
            }]
        });
    });
};

var displayScoresTable = function(){

    d3.text(scores_table, function(error, data){
        if (error){
            alert("Problem retrieving data");
            return;
        }
        var scoreHdgs = data.split("\n")[0].split("\t");
        data = d3.tsv.parse(data);

        var scoreHTML = '<table id="scoretable" class="display compact" cellspacing="0" width="100%"/>';
        $('#scores').html(scoreHTML);

        var scoreTableData = $.extend(true, [], data)
        var scoreHeadings = [];
        
        scoreHdgs.forEach(function(d,i){
            scoreHeadings.push({"data" : d, "title" : d});
        });
        
        var scoreTable = $('#scoretable').DataTable({
            columns: scoreHeadings,
            pageLength: 25, 
            order: [[ 0, "asc" ]],
            dom: '<"top"Bi>t<"bottom"lp><"clear">',
            data: scoreTableData,
            buttons: [
                'copy', 'pdfHtml5','csvHtml5'
            ],
        });
    });
};

