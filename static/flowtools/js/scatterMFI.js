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
        if (scatterDataMFI['selectedPopulations'].indexOf(pop[i]) >= 0) {
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

var processScatterData3DMFI = function() {
    var min = d3.min(scatterData3DMFI['data'], function(array) {
      return d3.min(array);
    });
    var max = d3.max(scatterData3DMFI['data'], function(array) {
      return d3.max(array);
    });
    scatterData3DMFI['min'] = 0;
    scatterData3DMFI['max'] = max;

    var col1 = scatterData3DMFI['data'].map(function(value,index) {
               return value[scatterData3DMFI['m1']];});
    var col2 = scatterData3DMFI['data'].map(function(value,index) {
               return value[scatterData3DMFI['m2']];});
    var col3 = scatterData3DMFI['data'].map(function(value,index) {
               return value[scatterData3DMFI['m3']];});
    var pop = scatterData3DMFI['poplist'];

    var xData = [];
    var yData = [];
    var zData = [];
    var popData = [];
    for (var i = 0; i < col1.length; i++) {
        if (scatterData3DMFI['selectedPopulations'].indexOf(pop[i]) >= 0) {
            xData.push(col1[i]);
            yData.push(col2[i]);
            zData.push(col3[i]);
            popData.push(pop[i]);
        }
    }

    scatterData3DMFI['popColors'] = popData.map(function(value,index) {
        return color_palette[value];
    });
    scatterData3DMFI['xData'] = xData;
    scatterData3DMFI['yData'] = yData;
    scatterData3DMFI['zData'] = zData;
    scatterData3DMFI['popData'] = popData;
    return scatterData3DMFI;
};


