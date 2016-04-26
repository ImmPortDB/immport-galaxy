var displayPopulationLegend = function() {
    allPopulations.map(function(value,index) {
        $('#popTable tr')
            .last()
            .after('<tr><td align="center"><input type="checkbox" checked class="popSelect" value='
                   + value + '/></td><td>' + value + '</td><td><span style="background-color:' +
                   color_palette[value] + '">&nbsp;&nbsp;&nbsp;</span></td></tr>');
    });

    $('#popSelectAll').click(function() {
        var checkAll = $("#popSelectAll").prop('checked');
        if (checkAll) {
            $(".popSelect").prop("checked", true);
        } else {
            $(".popSelect").prop("checked", false);
        }
    });

    $('.popSelect').click(function() {
        if ($('.popSelect').length == $(".popSelect:checked").length) {
            $('#popSelectAll').prop("checked",true);
        } else {
            $('#popSelectAll').prop("checked",false);
        }
    });
}