import _l from "utils/localization";
// dependencies
import Utils from "utils/utils";
import Ui from "mvc/ui/ui-misc";
import GenomespaceBrowser from "mvc/tool/tool-genomespace";
/**
 * GenomeSpace file selector
 */
var View = Backbone.View.extend({
    // initialize
    initialize: function(options) {
        // link this
        var self = this;
        this.options = options;

        // create insert new list element button
        this.browse_button = new Ui.ButtonIcon({
            title: _l("Browse"),
            icon: "fa fa-sign-in",
            tooltip: _l("Browse GenomeSpace"),
            onclick: function() {
                self.browseGenomeSpace(options);
            }
        });

        // create genomespace filepath textbox
        this.filename_textbox = new Ui.Input();

        // create elements
        this.setElement(this._template(options));
        this.$(".ui-gs-browse-button").append(this.browse_button.$el);
        this.$(".ui-gs-filename-textbox").append(this.filename_textbox.$el);
    },

    /** Browse GenomeSpace */
    browseGenomeSpace: function(options) {
        var self = this;
        GenomespaceBrowser.openFileBrowser({
            successCallback: function(data) {
                self.value(data.destination);
            }
        });
    },

    /** Main Template */
    _template: function(options) {
        return (
            '<div class="ui-gs-select-file">' +
            '<div class="ui-gs-browse-field">' +
            '<span class="ui-gs-browse-button" />' +
            '<span class="ui-gs-filename-textbox" />' +
            "</div>" +
            "</div>"
        );
    },

    /** Return/Set currently selected genomespace filename */
    value: function(new_value) {
        // check if new_value is defined
        if (new_value !== undefined) {
            this._setValue(new_value);
        } else {
            return this._getValue();
        }
    },

    // get value
    _getValue: function() {
        return this.filename_textbox.value();
    },

    // set value
    _setValue: function(new_value) {
        if (new_value) {
            this.filename_textbox.value(new_value);
        }
        this.options.onchange && this.options.onchange(new_value);
    }
});

export default {
    View: View
};
