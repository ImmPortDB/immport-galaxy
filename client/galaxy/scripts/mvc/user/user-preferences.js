import _l from "utils/localization";
/** User Preferences view */
import Form from "mvc/form/form-view";
import Ui from "mvc/ui/ui-misc";
import QueryStringParsing from "utils/query-string-parsing";
/** Contains descriptive dictionaries describing user forms */
var Model = Backbone.Model.extend({
    initialize: function(options) {
        options = options || {};
        options.user_id = options.user_id || Galaxy.user.id;
        this.set({
            user_id: options.user_id,
            information: {
                title: _l("Manage information"),
                description: "Edit your email, addresses and custom parameters or change your username.",
                url: `api/users/${options.user_id}/information/inputs`,
                icon: "fa-user",
                redirect: "user"
            },
            password: {
                title: _l("Change password"),
                description: _l("Allows you to change your login credentials."),
                icon: "fa-unlock-alt",
                url: `api/users/${options.user_id}/password/inputs`,
                submit_title: "Save password",
                redirect: "user"
            },
            communication: {
                title: _l("Change communication settings"),
                description: _l("Enable or disable the communication feature to chat with other users."),
                url: `api/users/${options.user_id}/communication/inputs`,
                icon: "fa-comments-o",
                redirect: "user"
            },
            permissions: {
                title: _l("Set dataset permissions for new histories"),
                description:
                    "Grant others default access to newly created histories. Changes made here will only affect histories created after these settings have been stored.",
                url: `api/users/${options.user_id}/permissions/inputs`,
                icon: "fa-users",
                submit_title: "Save permissions",
                redirect: "user"
            },
            api_key: {
                title: _l("Manage API key"),
                description: _l("Access your current API key or create a new one."),
                url: `api/users/${options.user_id}/api_key/inputs`,
                icon: "fa-key",
                submit_title: "Create a new key",
                submit_icon: "fa-check"
            },
            toolbox_filters: {
                title: _l("Manage Toolbox filters"),
                description: _l("Customize your Toolbox by displaying or omitting sets of Tools."),
                url: `api/users/${options.user_id}/toolbox_filters/inputs`,
                icon: "fa-filter",
                submit_title: "Save filters",
                redirect: "user"
            },
            openids: {
                title: _l("Manage OpenIDs"),
                description: _l("Associate OpenIDs with your account."),
                icon: "fa-openid",
                onclick: function() {
                    window.location.href = `${Galaxy.root}openids/list`;
                }
            },
            custom_builds: {
                title: _l("Manage custom builds"),
                description: _l("Add or remove custom builds using history datasets."),
                icon: "fa-cubes",
                onclick: function() {
                    window.location.href = `${Galaxy.root}custom_builds`;
                }
            },
            logout: {
                title: _l("Sign out"),
                description: _l("Click here to sign out of all sessions."),
                icon: "fa-sign-out",
                onclick: function() {
                    Galaxy.modal.show({
                        title: _l("Sign out"),
                        body: "Do you want to continue and sign out of all active sessions?",
                        buttons: {
                            Cancel: function() {
                                Galaxy.modal.hide();
                            },
                            "Sign out": function() {
                                window.location.href = `${Galaxy.root}user/logout?session_csrf_token=${
                                    Galaxy.session_csrf_token
                                }`;
                            }
                        }
                    });
                }
            }
        });
    }
});

/** View of the main user preference panel with links to individual user forms */
var View = Backbone.View.extend({
    title: _l("User Preferences"),
    active_tab: "user",
    initialize: function() {
        this.model = new Model();
        this.setElement("<div/>");
        this.render();
    },

    render: function() {
        var self = this;
        var config = Galaxy.config;
        $.getJSON(`${Galaxy.root}api/users/${Galaxy.user.id}`, data => {
            self.$preferences = $("<div/>")
                .addClass("ui-panel")
                .append($("<h2/>").append("User preferences"))
                .append($("<p/>").append(`You are logged in as <strong>${_.escape(data.email)}</strong>.`))
                .append((self.$table = $("<table/>").addClass("ui-panel-table")));
            var message = QueryStringParsing.get("message");
            var status = QueryStringParsing.get("status");
            if (message && status) {
                self.$preferences.prepend(new Ui.Message({ message: message, status: status }).$el);
            }
            if (!config.use_remote_user) {
                self._addLink("information");
                self._addLink("password");
            }
            if (config.enable_communication_server) {
                self._addLink("communication");
            }
            self._addLink("custom_builds");
            self._addLink("permissions");
            self._addLink("api_key");
            if (config.has_user_tool_filters) {
                self._addLink("toolbox_filters");
            }
            if (config.enable_openid && !config.use_remote_user) {
                self._addLink("openids");
            }
            if (Galaxy.session_csrf_token) {
                self._addLink("logout");
            }
            self.$preferences.append(self._templateFooter(data));
            self.$el.empty().append(self.$preferences);
        });
    },

    _addLink: function(action) {
        var options = this.model.get(action);
        var $row = $(this._templateLink(options));
        var $a = $row.find("a");
        if (options.onclick) {
            $a.on("click", () => {
                options.onclick();
            });
        } else {
            $a.attr("href", `${Galaxy.root}user/${action}`);
        }
        this.$table.append($row);
    },

    _templateLink: function(options) {
        return `<tr><td><div class="ui-panel-icon fa ${
            options.icon
        }"></td><td><a class="ui-panel-anchor" href="javascript:void(0)">${
            options.title
        }</a><div class="ui-form-info">${options.description}</div></td></tr>`;
    },

    _templateFooter: function(options) {
        return `<p class="ui-panel-footer">You are using <strong>${
            options.nice_total_disk_usage
        }</strong> of disk space in this Galaxy instance. ${
            Galaxy.config.enable_quotas ? `Your disk quota is: <strong>${options.quota}</strong>. ` : ""
        }Is your usage more than expected? See the <a href="https://galaxyproject.org/learn/managing-datasets/" target="_blank">documentation</a> for tips on how to find all of the data in your account.</p>`;
    }
});

export default {
    View: View,
    Model: Model
};
