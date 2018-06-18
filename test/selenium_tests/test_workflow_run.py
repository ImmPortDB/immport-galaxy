import yaml
from base import rules_test_data
from base.populators import load_data_dict
from base.workflow_fixtures import (
    WORKFLOW_SIMPLE_CAT_TWICE,
    WORKFLOW_WITH_DYNAMIC_OUTPUT_COLLECTION,
    WORKFLOW_WITH_OLD_TOOL_VERSION,
    WORKFLOW_WITH_RULES_1,
)

from .framework import (
    managed_history,
    selenium_test,
    SeleniumTestCase,
    UsesHistoryItemAssertions,
)


class WorkflowRunTestCase(SeleniumTestCase, UsesHistoryItemAssertions):

    ensure_registered = True

    @selenium_test
    @managed_history
    def test_simple_execution(self):
        self.perform_upload(self.get_filename("1.fasta"))
        self.wait_for_history()
        self.open_in_workflow_run(WORKFLOW_SIMPLE_CAT_TWICE)
        self.screenshot("workflow_run_simple_ready")
        self.workflow_run_submit()
        self.sleep_for(self.wait_types.UX_TRANSITION)
        self.screenshot("workflow_run_simple_submitted")
        self.history_panel_wait_for_hid_ok(2, allowed_force_refreshes=1)
        self.history_panel_click_item_title(hid=2, wait=True)
        self.assert_item_summary_includes(2, "2 sequences")
        self.screenshot("workflow_run_simple_complete")

    @selenium_test
    def test_execution_with_tool_upgrade(self):
        name = self.workflow_upload_yaml_with_random_name(WORKFLOW_WITH_OLD_TOOL_VERSION, exact_tools=True)
        self.workflow_run_with_name(name)
        self.sleep_for(self.wait_types.UX_TRANSITION)
        # Check that this tool form contains a warning about different versions.
        self.assert_warning_message(contains="different versions")
        self.screenshot("workflow_run_tool_upgrade")

    @selenium_test
    @managed_history
    def test_execution_with_multiple_inputs(self):
        history_id, inputs = self.workflow_run_setup_inputs(WORKFLOW_WITH_DYNAMIC_OUTPUT_COLLECTION)
        self.open_in_workflow_run(WORKFLOW_WITH_DYNAMIC_OUTPUT_COLLECTION)
        self.workflow_run_specify_inputs(inputs)
        self.screenshot("workflow_run_two_inputs")
        self.workflow_run_submit()

        self.history_panel_wait_for_hid_ok(7, allowed_force_refreshes=1)
        content = self.dataset_populator.get_history_dataset_content(history_id, hid=7)
        self.assertEqual("10.0\n30.0\n20.0\n40.0\n", content)

    @selenium_test
    @managed_history
    def test_execution_with_rules(self):
        history_id, inputs = self.workflow_run_setup_inputs(WORKFLOW_WITH_RULES_1)
        self.open_in_workflow_run(WORKFLOW_WITH_RULES_1)
        self.workflow_run_specify_inputs(inputs)
        self.screenshot("workflow_run_rules")
        self.workflow_run_submit()
        self.history_panel_wait_for_hid_ok(6, allowed_force_refreshes=1)
        output_content = self.dataset_populator.get_history_collection_details(history_id, hid=6)
        rules_test_data.check_example_2(output_content, self.dataset_populator)

    def open_in_workflow_run(self, yaml_content):
        name = self.workflow_upload_yaml_with_random_name(yaml_content)
        self.workflow_run_with_name(name)

    def workflow_run_setup_inputs(self, content):
        history_id = self.current_history_id()
        test_data = yaml.safe_load(content)["test_data"]
        inputs, _, _ = load_data_dict(history_id, test_data, self.dataset_populator, self.dataset_collection_populator)
        self.dataset_populator.wait_for_history(history_id)
        return history_id, inputs

    def workflow_run_specify_inputs(self, inputs):
        workflow_run = self.components.workflow_run
        for label, value in inputs.items():
            input_div_element = workflow_run.input_div(label=label).wait_for_visible()
            self.select2_set_value(input_div_element, "%d: " % value["hid"])

    def workflow_run_with_name(self, name):
        self.workflow_index_open()
        self.workflow_index_search_for(name)
        self.workflow_index_click_option("Run")
