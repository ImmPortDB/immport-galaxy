/**
 *  This class contains backbone wrappers for basic ui elements such as Images, Labels, Buttons, Input fields etc.
 */
import Select from "mvc/ui/ui-select-default";
import Slider from "mvc/ui/ui-slider";
import Options from "mvc/ui/ui-options";
import Drilldown from "mvc/ui/ui-drilldown";
import Buttons from "mvc/ui/ui-buttons";
import Modal from "mvc/ui/ui-modal";

/** Label wrapper */
export var Label = Backbone.View.extend({
    tagName: "label",
    initialize: function(options) {
        this.model = (options && options.model) || new Backbone.Model(options);
        this.tagName = options.tagName || this.tagName;
        this.setElement($(`<${this.tagName}/>`));
        this.listenTo(this.model, "change", this.render, this);
        this.render();
    },
    title: function(new_title) {
        this.model.set("title", new_title);
    },
    value: function() {
        return this.model.get("title");
    },
    render: function() {
        this.$el
            .removeClass()
            .addClass("ui-label")
            .addClass(this.model.get("cls"))
            .html(this.model.get("title"));
        return this;
    }
});

/** Displays messages used e.g. in the tool form */
export var Message = Backbone.View.extend({
    initialize: function(options) {
        this.model =
            (options && options.model) ||
            new Backbone.Model({
                message: null,
                status: "info",
                cls: "",
                persistent: false,
                fade: true
            }).set(options);
        this.listenTo(this.model, "change", this.render, this);
        if (options && options.active_tab) {
            this.active_tab = options.active_tab;
        }
        this.render();
    },
    update: function(options) {
        this.model.set(options);
    },
    render: function() {
        this.$el
            .removeClass()
            .addClass("ui-message")
            .addClass(this.model.get("cls"));
        var status = this.model.get("status");
        if (this.model.get("large")) {
            this.$el.addClass(
                `${(status == "success" && "done") || (status == "danger" && "error") || status}messagelarge`
            );
        } else {
            this.$el.addClass("alert").addClass(`alert-${status}`);
        }
        if (this.model.get("message")) {
            this.$el.html(this.messageForDisplay());
            this.$el[this.model.get("fade") ? "fadeIn" : "show"]();
            this.timeout && window.clearTimeout(this.timeout);
            if (!this.model.get("persistent")) {
                var self = this;
                this.timeout = window.setTimeout(() => {
                    self.model.set("message", "");
                }, 3000);
            }
        } else {
            this.$el.fadeOut();
        }
        return this;
    },
    messageForDisplay: function() {
        return _.escape(this.model.get("message"));
    }
});

export var UnescapedMessage = Message.extend({
    messageForDisplay: function() {
        return this.model.get("message");
    }
});

/** Renders an input element used e.g. in the tool form */
export var Input = Backbone.View.extend({
    initialize: function(options) {
        this.model =
            (options && options.model) ||
            new Backbone.Model({
                type: "text",
                placeholder: "",
                disabled: false,
                readonly: false,
                visible: true,
                cls: "",
                area: false,
                color: null,
                style: null
            }).set(options);
        this.tagName = this.model.get("area") ? "textarea" : "input";
        this.setElement($(`<${this.tagName}/>`));
        this.listenTo(this.model, "change", this.render, this);
        this.render();
    },
    events: {
        input: "_onchange"
    },
    value: function(new_val) {
        new_val !== undefined && this.model.set("value", typeof new_val === "string" ? new_val : "");
        return this.model.get("value");
    },
    render: function() {
        var self = this;
        this.$el
            .removeClass()
            .addClass(`ui-${this.tagName}`)
            .addClass(this.model.get("cls"))
            .addClass(this.model.get("style"))
            .attr("id", this.model.id)
            .attr("type", this.model.get("type"))
            .attr("placeholder", this.model.get("placeholder"))
            .css("color", this.model.get("color") || "")
            .css("border-color", this.model.get("color") || "");
        var datalist = this.model.get("datalist");
        if ($.isArray(datalist) && datalist.length > 0) {
            this.$el.autocomplete({
                source: function(request, response) {
                    response(self.model.get("datalist"));
                },
                change: function() {
                    self._onchange();
                }
            });
        }
        if (this.model.get("value") !== this.$el.val()) {
            this.$el.val(this.model.get("value"));
        }
        _.each(["readonly", "disabled"], attr_name => {
            self.model.get(attr_name) ? self.$el.attr(attr_name, true) : self.$el.removeAttr(attr_name);
        });
        this.$el[this.model.get("visible") ? "show" : "hide"]();
        return this;
    },
    _onchange: function() {
        this.value(this.$el.val());
        this.model.get("onchange") && this.model.get("onchange")(this.model.get("value"));
    }
});

/** Creates a hidden element input field used e.g. in the tool form */
export var Hidden = Backbone.View.extend({
    initialize: function(options) {
        this.model = (options && options.model) || new Backbone.Model(options);
        this.setElement(
            $("<div/>")
                .append((this.$info = $("<div/>")))
                .append((this.$hidden = $("<div/>")))
        );
        this.listenTo(this.model, "change", this.render, this);
        this.render();
    },
    value: function(new_val) {
        new_val !== undefined && this.model.set("value", new_val);
        return this.model.get("value");
    },
    render: function() {
        this.$el.attr("id", this.model.id);
        this.$hidden.val(this.model.get("value"));
        this.model.get("info") ? this.$info.show().text(this.model.get("info")) : this.$info.hide();
        return this;
    }
});

/** Creates an input element which switches between select and text field */
export var TextSelect = Backbone.View.extend({
    initialize: function(options) {
        this.select = options.select;
        this.model = this.select.model;
        this.text = new Input({
            onchange: this.model.get("onchange")
        });
        this.on("change", () => {
            if (this.model.get("onchange")) {
                this.model.get("onchange")(this.value());
            }
        });
        this.setElement(
            $("<div/>")
                .append(this.select.$el)
                .append(this.text.$el)
        );
        this.update(this.model.get("data"));
    },
    wait: function() {
        this.select.wait();
    },
    unwait: function() {
        this.select.unwait();
    },
    value: function(new_val) {
        var element = this.textmode ? this.text : this.select;
        return element.value(new_val);
    },
    update: function(options) {
        var v = this.value();
        this.textmode = !$.isArray(options) || options.length === 0;
        this.text.$el[this.textmode ? "show" : "hide"]();
        this.select.$el[this.textmode ? "hide" : "show"]();
        this.select.update(options);
        this.value(v);
    }
});

/** Creates a upload element input field */
export var Upload = Backbone.View.extend({
    initialize: function(options) {
        var self = this;
        this.model = (options && options.model) || new Backbone.Model(options);
        this.setElement(
            $("<div/>")
                .append((this.$info = $("<div/>")))
                .append(
                    (this.$file = $("<input/>")
                        .attr("type", "file")
                        .addClass("ui-margin-bottom"))
                )
                .append(
                    (this.$text = $("<textarea/>")
                        .addClass("ui-textarea")
                        .attr("disabled", true))
                )
                .append((this.$wait = $("<i/>").addClass("fa fa-spinner fa-spin")))
        );
        this.listenTo(this.model, "change", this.render, this);
        this.$file.on("change", e => {
            self._readFile(e);
        });
        this.render();
    },
    value: function(new_val) {
        new_val !== undefined && this.model.set("value", new_val);
        return this.model.get("value");
    },
    render: function() {
        this.$el.attr("id", this.model.id);
        this.model.get("info") ? this.$info.show().text(this.model.get("info")) : this.$info.hide();
        this.model.get("value") ? this.$text.text(this.model.get("value")).show() : this.$text.hide();
        this.model.get("wait") ? this.$wait.show() : this.$wait.hide();
        return this;
    },
    _readFile: function(e) {
        var self = this;
        var file = e.target.files && e.target.files[0];
        if (file) {
            var reader = new FileReader();
            reader.onload = function() {
                self.model.set({ wait: false, value: this.result });
            };
            this.model.set({ wait: true, value: null });
            reader.readAsText(file);
        }
    }
});

/* Make more Ui stuff directly available at this namespace (for backwards
 * compatibility).  We should eliminate this practice, though, and just require
 * what we need where we need it, allowing for better package optimization.
 */

export let Button = Buttons.ButtonDefault;
export let ButtonIcon = Buttons.ButtonIcon;
export let ButtonCheck = Buttons.ButtonCheck;
export let ButtonMenu = Buttons.ButtonMenu;
export let ButtonLink = Buttons.ButtonLink;
export let Checkbox = Options.Checkbox;
export let RadioButton = Options.RadioButton;
export let Radio = Options.Radio;
export { Select, Slider, Drilldown };

export default {
    Button: Buttons.ButtonDefault,
    ButtonIcon: Buttons.ButtonIcon,
    ButtonCheck: Buttons.ButtonCheck,
    ButtonMenu: Buttons.ButtonMenu,
    ButtonLink: Buttons.ButtonLink,
    Input: Input,
    Label: Label,
    Message: Message,
    UnescapedMessage: UnescapedMessage,
    Upload: Upload,
    Modal: Modal,
    RadioButton: Options.RadioButton,
    Checkbox: Options.Checkbox,
    Radio: Options.Radio,
    Select: Select,
    TextSelect: TextSelect,
    Hidden: Hidden,
    Slider: Slider,
    Drilldown: Drilldown
};
