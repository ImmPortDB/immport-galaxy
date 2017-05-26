define(['plugin/charts/forms/default'], function(config_default) {

return $.extend(true, {}, config_default, {
    title       : '',
    category    : '',
    library     : 'jqPlot',
    tag         : 'div',
    zoomable    : true,
    keywords    : 'medium',
    settings    : {
        separator_grid  : {
            title       : 'Grids',
            type        : 'separator'
        },
        x_axis_grid : {
            title       : 'Axis grid',
            info        : 'Would you like to show grid lines for the X axis?',
            type        : 'select',
            display     : 'radiobutton',
            init        : 'false',
            data        : [
                {
                    label   : 'On',
                    value   : 'true'
                },
                {
                    label   : 'Off',
                    value   : 'false'
                }
            ]
        },
        y_axis_grid : {
            title       : 'Axis grid',
            info        : 'Would you like to show grid lines for the Y axis?',
            type        : 'select',
            display     : 'radiobutton',
            init        : 'true',
            data        : [
                {
                    label   : 'On',
                    value   : 'true'
                },
                {
                    label   : 'Off',
                    value   : 'false'
                }
            ]
        }
    }
});

});