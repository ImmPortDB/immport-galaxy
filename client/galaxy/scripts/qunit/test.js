// Load all qunit tests into a single bundle.
//var testsContext = require.context(".", true, /_tests$/);
//testsContext.keys().forEach(testsContext);

import gab from "qunit/tests/galaxy_app_base_tests";
import ml from "qunit/tests/metrics_logger_tests";
// form_tests seems to need to come before something - maybe multiple things
import form from "qunit/tests/form_tests";
import l from "qunit/tests/list_of_pairs_collection_creator_tests";
import upd from "qunit/tests/upload_dialog_tests";
import we from "qunit/tests/workflow_editor_tests";
import mast from "qunit/tests/masthead_tests";
import graph from "qunit/tests/graph_tests";
import jd from "qunit/tests/job_dag_tests";
import hc from "qunit/tests/history_contents_model_tests";
import hda from "qunit/tests/hda_base_tests";
import modal from "qunit/tests/modal_tests";
import page from "qunit/tests/page_tests";
import popover from "qunit/tests/popover_tests";
import utils from "qunit/tests/utils_tests";
import ui from "qunit/tests/ui_tests";
