var preprocessScatterDataMFI = function(text) {
    data = d3.tsv.parseRows(text).map(function(row) {
        return row.map(function(value) {
            if (isNaN(value)) {
                return value;
            }
            return +value;
        });
    });

    // Get the Headings Row, then remove the Count, Percentage and
    // Population headings
    scatterDataMFI['columnHeadings'] = data.shift();
    scatterDataMFI['columnHeadings'].pop();
    scatterDataMFI['columnHeadings'].pop();
    scatterDataMFI['columnHeadings'].pop();

    var popCol = data[0].length -1;
    var pop = data.map(function(value,index) {
        return parseInt(value[popCol]);
    });

    var perCol = data[0].length -2;
    var per = data.map(function(value,index) {
        return parseFloat(value[perCol]);
    });

    var countCol = data[0].length -3;
    var count = data.map(function(value,index) {
        return parseInt(value[countCol]);
    });

    scatterDataMFI['popCol'] = popCol;
    scatterDataMFI['populations'] = pop;
    scatterDataMFI['percent'] = per;
    scatterDataMFI['counts'] = count;

    var l = data[0].length;
    scatterDataMFI['data'] = data.map(function(row) {
        return row.splice(0,countCol);
    });
    scatterDataMFI['poplist'] = pop;
    scatterDataMFI['m1'] = 0;
    scatterDataMFI['m2'] = 1;
    scatterDataMFI['m3'] = 2;

};

var processScatterDataMFI2D = function() {
    var col1 = scatterDataMFI['data'].map(function(value,index) {
               return value[scatterDataMFI['m1']];});
    var col2 = scatterDataMFI['data'].map(function(value,index) {
               return value[scatterDataMFI['m2']];});
    //var pop = scatterDataMFI['data'].map(function(value,index) {
    //           return value[scatterDataMFI['popCol']];});
    var pop = scatterDataMFI['poplist']

    var xData = [];
    var yData = [];
    var popData = [];
    for (var i = 0; i < col1.length; i++) {
        if (scatterDataMFI['populations'].indexOf(pop[i]) >= 0) {
            xData.push(col1[i]);
            yData.push(col2[i]);
            popData.push(pop[i]);
        }
    }

    scatterDataMFI['popColors'] = popData.map(function(value,index) {
        return color_palette[value];
    });
    scatterDataMFI['xData'] = xData;
    scatterDataMFI['yData'] = yData;
    scatterDataMFI['popData'] = popData;
    return scatterDataMFI;
};

var processScatterDataMFI3D = function() {
    var col1 = scatterDataMFI['data'].map(function(value,index) {
               return value[scatterDataMFI['m1']];});
    var col2 = scatterDataMFI['data'].map(function(value,index) {
               return value[scatterDataMFI['m2']];});
    var col3 = scatterDataMFI['data'].map(function(value,index) {
               return value[scatterDataMFI['m3']];});
    var pop = scatterDataMFI['poplist'];

    var xData = [];
    var yData = [];
    var zData = [];
    var popData = [];
    for (var i = 0; i < col1.length; i++) {
        if (scatterDataMFI['populations'].indexOf(pop[i]) >= 0) {
            xData.push(col1[i]);
            yData.push(col2[i]);
            zData.push(col3[i]);
            popData.push(pop[i]);
        }
    }

    scatterDataMFI['popColors'] = popData.map(function(value,index) {
        return color_palette[value];
    });
    scatterDataMFI['xData'] = xData;
    scatterDataMFI['yData'] = yData;
    scatterDataMFI['zData'] = zData;
    scatterDataMFI['popData'] = popData;
    return scatterDataMFI;
};
