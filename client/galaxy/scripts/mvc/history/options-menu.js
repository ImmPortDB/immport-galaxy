import * as _ from "underscore";
import _l from "utils/localization";
import PopupMenu from "mvc/ui/popup-menu";
import historyCopyDialog from "mvc/history/copy-dialog";
import Webhooks from "mvc/webhooks";

/* global $ */
/* global Galaxy */

// ============================================================================
var menu = [
    {
        html: _l("History Lists"),
        header: true
    },
    {
        html: _l("Saved Histories"),
        href: "histories/list",
        target: "_top"
    },
    {
        html: _l("Histories Shared with Me"),
        href: "histories/list_shared",
        target: "_top"
    },
    {
        html: _l("Current History"),
        header: true,
        anon: true
    },
    {
        html: _l("Create New"),
        func: function() {
            if (Galaxy && Galaxy.currHistoryPanel) {
                Galaxy.currHistoryPanel.createNewHistory();
            }
        }
    },
    {
        html: _l("Copy History"),
        func: function() {
            historyCopyDialog(Galaxy.currHistoryPanel.model).done(() => {
                Galaxy.currHistoryPanel.loadCurrentHistory();
            });
        }
    },
    {
        html: _l("Share or Publish"),
        href: "history/sharing"
    },
    {
        html: _l("Show Structure"),
        anon: true,
        func: function() {
            if (Galaxy && Galaxy.currHistoryPanel && Galaxy.router) {
                Galaxy.router.push(`/histories/show_structure`);
            }
        }
    },
    {
        html: _l("Extract Workflow"),
        href: "workflow/build_from_current_history"
    },
    {
        html: _l("Delete"),
        anon: true,
        func: function() {
            if (Galaxy && Galaxy.currHistoryPanel && confirm(_l("Really delete the current history?"))) {
                Galaxy.currHistoryPanel.model._delete().done(() => {
                    Galaxy.currHistoryPanel.loadCurrentHistory();
                });
            }
        }
    },
    {
        html: _l("Delete Permanently"),
        purge: true,
        anon: true,
        func: function() {
            if (
                Galaxy &&
                Galaxy.currHistoryPanel &&
                confirm(_l("Really delete the current history permanently? This cannot be undone."))
            ) {
                Galaxy.currHistoryPanel.model.purge().done(() => {
                    Galaxy.currHistoryPanel.loadCurrentHistory();
                });
            }
        }
    },

    {
        html: _l("Dataset Actions"),
        header: true,
        anon: true
    },
    {
        html: _l("Copy Datasets"),
        href: "dataset/copy_datasets"
    },
    {
        html: _l("Dataset Security"),
        func: function() {
            if (Galaxy && Galaxy.currHistoryPanel && Galaxy.router) {
                Galaxy.router.push(`/histories/permissions?id=${Galaxy.currHistoryPanel.model.id}`);
            }
        }
    },
    {
        html: _l("Resume Paused Jobs"),
        href: "history/resume_paused_jobs?current=True",
        anon: true
    },
    {
        html: _l("Collapse Expanded Datasets"),
        func: function() {
            if (Galaxy && Galaxy.currHistoryPanel) {
                Galaxy.currHistoryPanel.collapseAll();
            }
        }
    },
    {
        html: _l("Unhide Hidden Datasets"),
        anon: true,
        func: function() {
            // TODO: Deprecate this functionality and replace with group dataset selector and action combination
            if (Galaxy && Galaxy.currHistoryPanel && confirm(_l("Really unhide all hidden datasets?"))) {
                $.post(`${Galaxy.root}history/adjust_hidden`, { user_action: "unhide" }, () => {
                    Galaxy.currHistoryPanel.loadCurrentHistory();
                });
            }
        }
    },
    {
        html: _l("Delete Hidden Datasets"),
        anon: true,
        func: function() {
            // TODO: Deprecate this functionality and replace with group dataset selector and action combination
            if (Galaxy && Galaxy.currHistoryPanel && confirm(_l("Really delete all hidden datasets?"))) {
                $.post(`${Galaxy.root}history/adjust_hidden`, { user_action: "delete" }, () => {
                    Galaxy.currHistoryPanel.loadCurrentHistory();
                });
            }
        }
    },
    {
        html: _l("Purge Deleted Datasets"),
        confirm: _l("Really delete all deleted datasets permanently? This cannot be undone."),
        href: "history/purge_deleted_datasets",
        purge: true,
        anon: true
    },

    {
        html: _l("Downloads"),
        header: true
    },
    {
        html: _l("Export Tool Citations"),
        anon: true,
        func: function() {
            if (Galaxy && Galaxy.currHistoryPanel && Galaxy.router) {
                Galaxy.router.push(`/histories/citations?id=${Galaxy.currHistoryPanel.model.id}`);
            }
        }
    },
    {
        html: _l("Export History to File"),
        href: "history/export_archive?preview=True",
        anon: true
    },

    {
        html: _l("Other Actions"),
        header: true
    },
    {
        html: _l("Import from File"),
        href: "histories/import",
        target: "_top"
    }
];

// Webhooks
Webhooks.load({
    type: "history-menu",
    async: false, // (hypothetically) slows down the performance
    callback: function(webhooks) {
        var webhooks_menu = [];

        webhooks.each(model => {
            var webhook = model.toJSON();
            if (webhook.activate) {
                webhooks_menu.push({
                    html: _l(webhook.config.title),
                    // func: function() {},
                    anon: true
                });
            }
        });

        if (webhooks_menu.length > 0) {
            webhooks_menu.unshift({
                html: _l("Webhooks"),
                header: true
            });
            $.merge(menu, webhooks_menu);
        }
    }
});

function buildMenu(isAnon, purgeAllowed, urlRoot) {
    return _.clone(menu).filter(menuOption => {
        if (isAnon && !menuOption.anon) {
            return false;
        }
        if (!purgeAllowed && menuOption.purge) {
            return false;
        }

        //TODO:?? hard-coded galaxy_main
        if (menuOption.href) {
            menuOption.href = urlRoot + menuOption.href;
            menuOption.target = menuOption.target || "galaxy_main";
        }

        if (menuOption.confirm) {
            menuOption.func = () => {
                if (confirm(menuOption.confirm)) {
                    /* galaxy_main is a global here: TODO: Fix it! */
                    galaxy_main.location = menuOption.href;
                }
            };
        }
        return true;
    });
}

var create = ($button, options) => {
    options = options || {};
    var isAnon = options.anonymous === undefined ? true : options.anonymous;
    var purgeAllowed = options.purgeAllowed || false;
    var menu = buildMenu(isAnon, purgeAllowed, Galaxy.root);
    //console.debug( 'menu:', menu );
    return new PopupMenu($button, menu);
};

// ============================================================================
export default create;
