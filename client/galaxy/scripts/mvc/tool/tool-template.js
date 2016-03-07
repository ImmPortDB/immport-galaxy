// dependencies
define([], function() {

// tool form templates
return {
    help: function( options ) {
        var $tmpl = $( '<div/>' ).addClass( 'ui-form-help' ).append( options.help );
        $tmpl.find( 'a' ).attr( 'target', '_blank' );
        return $tmpl;
    },

    success: function(response) {
        // check
        if (!response.jobs || !response.jobs.length) {
            return this.error(response);
        }

        // number of jobs
        var njobs = response.jobs.length;

        // job count info text
        var njobs_text = '';
        if (njobs == 1) {
            njobs_text = '1 job has';
        } else {
            njobs_text = njobs + ' jobs have';
        }

        // create template string
        var tmpl =  '<div class="donemessagelarge">' +
                        '<p>' + njobs_text + ' been successfully added to the queue - resulting in the following datasets:</p>';
        for (var i in response.outputs) {
            tmpl +=     '<p style="padding: 10px 20px;"><b>' + response.outputs[i].hid + ': ' + response.outputs[i].name + '</b></p>';
        }
        tmpl +=         '<p>You can check the status of queued jobs and view the resulting data by refreshing the History pane. When the job has been run the status will change from \'running\' to \'finished\' if completed successfully or \'error\' if problems were encountered.</p>' +
                    '</div>';

        // return success message element
        return tmpl;
    },

    error: function(response) {
        return  '<div>' +
                    '<p>' +
                        'The server could not complete the request. Please contact the Galaxy Team if this error persists.' +
                    '</p>' +
                    '<textarea class="ui-textarea" disabled style="color: black; height: 300px !important;">' +
                        JSON.stringify(response, undefined, 4) +
                    '</textarea>' +
                '</div>';
    },

    requirements: function(options) {
        var requirements_message = 'This tool requires ';
        for (var i in options.requirements) {
            var req = options.requirements[i];
            requirements_message += req.name;
            if (req.version) {
                requirements_message += ' (Version ' + req.version + ')';
            }
            if (i < options.requirements.length - 2) {
                requirements_message += ', ';
            }
            if (i == options.requirements.length - 2) {
                requirements_message += ' and ';
            }
        }
        return requirements_message + '. Click <a target="_blank" href="https://wiki.galaxyproject.org/Tools/Requirements">here</a> for more information.';
    }
};

});