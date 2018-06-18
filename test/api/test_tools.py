# Test tools API.
import json
import os

from base import api
from base import rules_test_data
from base.populators import (
    DatasetCollectionPopulator,
    DatasetPopulator,
    LibraryPopulator,
    load_data_dict,
    skip_without_tool,
)


class ToolsTestCase(api.ApiTestCase):

    def setUp(self):
        super(ToolsTestCase, self).setUp()
        self.dataset_populator = DatasetPopulator(self.galaxy_interactor)
        self.dataset_collection_populator = DatasetCollectionPopulator(self.galaxy_interactor)

    def test_index(self):
        tool_ids = self.__tool_ids()
        assert "upload1" in tool_ids

    def test_no_panel_index(self):
        index = self._get("tools", data=dict(in_panel="false"))
        tools_index = index.json()
        # No need to flatten out sections, with in_panel=False, only tools are
        # returned.
        tool_ids = [_["id"] for _ in tools_index]
        assert "upload1" in tool_ids

    @skip_without_tool("cat1")
    def test_show_repeat(self):
        tool_info = self._show_valid_tool("cat1")
        parameters = tool_info["inputs"]
        assert len(parameters) == 2, "Expected two inputs - got [%s]" % parameters
        assert parameters[0]["name"] == "input1"
        assert parameters[1]["name"] == "queries"

        repeat_info = parameters[1]
        self._assert_has_keys(repeat_info, "min", "max", "title", "help")
        repeat_params = repeat_info["inputs"]
        assert len(repeat_params) == 1
        assert repeat_params[0]["name"] == "input2"

    @skip_without_tool("random_lines1")
    def test_show_conditional(self):
        tool_info = self._show_valid_tool("random_lines1")

        cond_info = tool_info["inputs"][2]
        self._assert_has_keys(cond_info, "cases", "test_param")
        self._assert_has_keys(cond_info["test_param"], 'name', 'type', 'label', 'help')

        cases = cond_info["cases"]
        assert len(cases) == 2
        case1 = cases[0]
        self._assert_has_keys(case1, "value", "inputs")
        assert case1["value"] == "no_seed"
        assert len(case1["inputs"]) == 0

        case2 = cases[1]
        self._assert_has_keys(case2, "value", "inputs")
        case2_inputs = case2["inputs"]
        assert len(case2_inputs) == 1
        self._assert_has_keys(case2_inputs[0], 'name', 'type', 'label', 'help', 'argument')
        assert case2_inputs[0]["name"] == "seed"

    @skip_without_tool("multi_data_param")
    def test_show_multi_data(self):
        tool_info = self._show_valid_tool("multi_data_param")

        f1_info, f2_info = tool_info["inputs"][0], tool_info["inputs"][1]
        self._assert_has_keys(f1_info, "min", "max")
        assert f1_info["min"] == 1
        assert f1_info["max"] == 1235

        self._assert_has_keys(f2_info, "min", "max")
        assert f2_info["min"] is None
        assert f2_info["max"] is None

    @skip_without_tool("test_data_source")
    def test_data_source_ok_request(self):
        with self.dataset_populator.test_history() as history_id:
            payload = self.dataset_populator.run_tool_payload(
                tool_id="test_data_source",
                inputs={
                    "URL": "https://raw.githubusercontent.com/galaxyproject/galaxy/dev/test-data/1.bed",
                    "URL_method": "get",
                    "data_type": "bed",
                },
                history_id=history_id,
            )
            create_response = self._post("tools", data=payload)
            self._assert_status_code_is(create_response, 200)
            create_object = create_response.json()
            self._assert_has_keys(create_object, "outputs")
            assert len(create_object["outputs"]) == 1
            output = create_object["outputs"][0]
            self.dataset_populator.wait_for_history(history_id, assert_ok=True)
            output_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output)
            assert output_content.startswith("chr1\t147962192\t147962580")

            output_details = self.dataset_populator.get_history_dataset_details(history_id, dataset=output)
            assert output_details["file_ext"] == "bed"

    @skip_without_tool("test_data_source")
    def test_data_sources_block_file_parameters(self):
        with self.dataset_populator.test_history() as history_id:
            payload = self.dataset_populator.run_tool_payload(
                tool_id="test_data_source",
                inputs={
                    "URL": "file://%s" % os.path.join(os.getcwd(), "README.rst"),
                    "URL_method": "get",
                    "data_type": "bed",
                },
                history_id=history_id,
            )
            create_response = self._post("tools", data=payload)
            self._assert_status_code_is(create_response, 200)
            create_object = create_response.json()
            self._assert_has_keys(create_object, "outputs")
            assert len(create_object["outputs"]) == 1
            output = create_object["outputs"][0]
            self.dataset_populator.wait_for_history(history_id, assert_ok=False)

            output_details = self.dataset_populator.get_history_dataset_details(history_id, dataset=output, wait=False)
            assert output_details["state"] == "error", output_details
            assert "has not sent back a URL parameter" in output_details["misc_info"], output_details

    def _show_valid_tool(self, tool_id):
        tool_show_response = self._get("tools/%s" % tool_id, data=dict(io_details=True))
        self._assert_status_code_is(tool_show_response, 200)
        tool_info = tool_show_response.json()
        self._assert_has_keys(tool_info, "inputs", "outputs", "panel_section_id")
        return tool_info

    @skip_without_tool("composite_output")
    def test_test_data_filepath_security(self):
        test_data_response = self._get("tools/%s/test_data_path?filename=../CONTRIBUTORS.md" % "composite_output", admin=True)
        assert test_data_response.status_code == 404, test_data_response.json()

    @skip_without_tool("composite_output")
    def test_test_data_admin_security(self):
        test_data_response = self._get("tools/%s/test_data_path?filename=../CONTRIBUTORS.md" % "composite_output")
        assert test_data_response.status_code == 403, test_data_response.json()

    @skip_without_tool("composite_output")
    def test_test_data_composite_output(self):
        test_data_response = self._get("tools/%s/test_data" % "composite_output")
        assert test_data_response.status_code == 200
        test_data = test_data_response.json()
        assert len(test_data) == 1
        test_case = test_data[0]
        self._assert_has_keys(test_case, "inputs", "outputs", "output_collections", "required_files")
        assert len(test_case["inputs"]) == 1, test_case
        # input0 = next(iter(test_case["inputs"].values()))

    @skip_without_tool("collection_two_paired")
    def test_test_data_collection_two_paired(self):
        test_data_response = self._get("tools/%s/test_data" % "collection_two_paired")
        assert test_data_response.status_code == 200
        test_data = test_data_response.json()
        assert len(test_data) == 2
        test_case = test_data[0]
        self._assert_has_keys(test_case, "inputs", "outputs", "output_collections", "required_files")
        assert len(test_case["inputs"]) == 3, test_case

    @skip_without_tool("collection_nested_test")
    def test_test_data_collection_nested(self):
        test_data_response = self._get("tools/%s/test_data" % "collection_nested_test")
        assert test_data_response.status_code == 200
        test_data = test_data_response.json()
        assert len(test_data) == 2
        test_case = test_data[0]
        self._assert_has_keys(test_case, "inputs", "outputs", "output_collections", "required_files")
        assert len(test_case["inputs"]) == 1, test_case

    @skip_without_tool("simple_constructs_y")
    def test_test_data_yaml_tools(self):
        test_data_response = self._get("tools/%s/test_data" % "simple_constructs_y")
        assert test_data_response.status_code == 200
        test_data = test_data_response.json()
        assert len(test_data) == 3

    def test_unzip_collection(self):
        with self.dataset_populator.test_history() as history_id:
            hdca_id = self.__build_pair(history_id, ["123", "456"])
            inputs = {
                "input": {"src": "hdca", "id": hdca_id},
            }
            self.dataset_populator.wait_for_history(history_id, assert_ok=True)
            response = self._run("__UNZIP_COLLECTION__", history_id, inputs, assert_ok=True)
            outputs = response["outputs"]
            self.assertEquals(len(outputs), 2)
            output_forward = outputs[0]
            output_reverse = outputs[1]
            output_forward_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output_forward)
            output_reverse_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output_reverse)
            assert output_forward_content.strip() == "123"
            assert output_reverse_content.strip() == "456"

            output_forward = self.dataset_populator.get_history_dataset_details(history_id, dataset=output_forward)
            output_reverse = self.dataset_populator.get_history_dataset_details(history_id, dataset=output_reverse)

            assert output_forward["history_id"] == history_id
            assert output_reverse["history_id"] == history_id

    def test_unzip_nested(self):
        with self.dataset_populator.test_history() as history_id:
            hdca_list_id = self.__build_nested_list(history_id)
            inputs = {
                "input": {
                    'batch': True,
                    'values': [{'src': 'hdca', 'map_over_type': 'paired', 'id': hdca_list_id}],
                }
            }
            self.dataset_populator.wait_for_history(history_id, assert_ok=True)
            response = self._run("__UNZIP_COLLECTION__", history_id, inputs, assert_ok=True)
            implicit_collections = response["implicit_collections"]
            self.assertEquals(len(implicit_collections), 2)
            unzipped_hdca = self.dataset_populator.get_history_collection_details(history_id, hid=implicit_collections[0]["hid"])
            assert unzipped_hdca["elements"][0]["element_type"] == "hda", unzipped_hdca

    def test_zip_inputs(self):
        with self.dataset_populator.test_history() as history_id:
            hda1 = dataset_to_param(self.dataset_populator.new_dataset(history_id, content='1\t2\t3'))
            hda2 = dataset_to_param(self.dataset_populator.new_dataset(history_id, content='4\t5\t6'))
            inputs = {
                "input_forward": hda1,
                "input_reverse": hda2,
            }
            self.dataset_populator.wait_for_history(history_id, assert_ok=True)
            response = self._run("__ZIP_COLLECTION__", history_id, inputs, assert_ok=True)
            output_collections = response["output_collections"]
            self.assertEquals(len(output_collections), 1)
            self.dataset_populator.wait_for_job(response["jobs"][0]["id"], assert_ok=True)
            zipped_hdca = self.dataset_populator.get_history_collection_details(history_id, hid=output_collections[0]["hid"])
            assert zipped_hdca["collection_type"] == "paired"

    def test_zip_list_inputs(self):
        with self.dataset_populator.test_history() as history_id:
            hdca1_id = self.dataset_collection_populator.create_list_in_history(history_id, contents=["a\nb\nc\nd", "e\nf\ng\nh"]).json()["id"]
            hdca2_id = self.dataset_collection_populator.create_list_in_history(history_id, contents=["1\n2\n3\n4", "5\n6\n7\n8"]).json()["id"]
            inputs = {
                "input_forward": {'batch': True, 'values': [{"src": "hdca", "id": hdca1_id}]},
                "input_reverse": {'batch': True, 'values': [{"src": "hdca", "id": hdca2_id}]},
            }
            self.dataset_populator.wait_for_history(history_id, assert_ok=True)
            response = self._run("__ZIP_COLLECTION__", history_id, inputs, assert_ok=True)
            implicit_collections = response["implicit_collections"]
            self.assertEquals(len(implicit_collections), 1)
            self.dataset_populator.wait_for_job(response["jobs"][0]["id"], assert_ok=True)
            zipped_hdca = self.dataset_populator.get_history_collection_details(history_id, hid=implicit_collections[0]["hid"])
            assert zipped_hdca["collection_type"] == "list:paired"

    def test_filter_failed(self):
        with self.dataset_populator.test_history() as history_id:
            ok_hdca_id = self.dataset_collection_populator.create_list_in_history(history_id, contents=["0", "1", "0", "1"]).json()["id"]
            response = self.dataset_populator.run_exit_code_from_file(history_id, ok_hdca_id)

            mixed_implicit_collections = response["implicit_collections"]
            self.assertEquals(len(mixed_implicit_collections), 1)
            mixed_hdca_hid = mixed_implicit_collections[0]["hid"]
            mixed_hdca = self.dataset_populator.get_history_collection_details(history_id, hid=mixed_hdca_hid, wait=False)

            def get_state(dce):
                return dce["object"]["state"]

            mixed_states = [get_state(_) for _ in mixed_hdca["elements"]]
            assert mixed_states == [u"ok", u"error", u"ok", u"error"], mixed_states
            inputs = {
                "input": {"src": "hdca", "id": mixed_hdca["id"]},
            }
            response = self._run("__FILTER_FAILED_DATASETS__", history_id, inputs, assert_ok=False).json()
            self.dataset_populator.wait_for_history(history_id, assert_ok=False)
            filter_output_collections = response["output_collections"]
            self.assertEquals(len(filter_output_collections), 1)
            filtered_hid = filter_output_collections[0]["hid"]
            filtered_hdca = self.dataset_populator.get_history_collection_details(history_id, hid=filtered_hid, wait=False)
            filtered_states = [get_state(_) for _ in filtered_hdca["elements"]]
            assert filtered_states == [u"ok", u"ok"], filtered_states

    def _apply_rules_and_check(self, example):
        with self.dataset_populator.test_history() as history_id:
            inputs, _, _ = load_data_dict(history_id, {"input": example["test_data"]}, self.dataset_populator, self.dataset_collection_populator)
            hdca = inputs["input"]
            inputs = {
                "input": {"src": "hdca", "id": hdca["id"]},
                "rules": example["rules"]
            }
            self.dataset_populator.wait_for_history(history_id)
            response = self._run("__APPLY_RULES__", history_id, inputs, assert_ok=True)
            output_collections = response["output_collections"]
            self.assertEquals(len(output_collections), 1)
            output_hid = output_collections[0]["hid"]
            output_hdca = self.dataset_populator.get_history_collection_details(history_id, hid=output_hid, wait=False)
            example["check"](output_hdca, self.dataset_populator)

    def test_apply_rules_1(self):
        self._apply_rules_and_check(rules_test_data.EXAMPLE_1)

    def test_apply_rules_2(self):
        self._apply_rules_and_check(rules_test_data.EXAMPLE_2)

    def test_apply_rules_3(self):
        self._apply_rules_and_check(rules_test_data.EXAMPLE_3)

    @skip_without_tool("multi_select")
    def test_multi_select_as_list(self):
        with self.dataset_populator.test_history() as history_id:
            inputs = {
                "select_ex": ["--ex1", "ex2"],
            }
            response = self._run("multi_select", history_id, inputs, assert_ok=True)
            output = response["outputs"][0]
            output1_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output)

            assert output1_content == "--ex1,ex2"

    @skip_without_tool("multi_select")
    def test_multi_select_optional(self):
        with self.dataset_populator.test_history() as history_id:
            inputs = {
                "select_ex": ["--ex1"],
                "select_optional": None,
            }
            response = self._run("multi_select", history_id, inputs, assert_ok=True)
            output = response["outputs"]
            output1_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output[0])
            output2_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output[1])
            assert output1_content.strip() == "--ex1"
            assert output2_content.strip() == "None", output2_content

    @skip_without_tool("library_data")
    def test_library_data_param(self):
        with self.dataset_populator.test_history() as history_id:
            ld = LibraryPopulator(self.galaxy_interactor).new_library_dataset("lda_test_library")
            inputs = {
                "library_dataset": ld["ldda_id"],
                "library_dataset_multiple": [ld["ldda_id"], ld["ldda_id"]]
            }
            response = self._run("library_data", history_id, inputs, assert_ok=True)
            output = response["outputs"]
            output_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output[0])
            assert output_content == "TestData\n", output_content
            output_multiple_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output[1])
            assert output_multiple_content == "TestData\nTestData\n", output_multiple_content

    @skip_without_tool("multi_data_param")
    def test_multidata_param(self):
        with self.dataset_populator.test_history() as history_id:
            hda1 = dataset_to_param(self.dataset_populator.new_dataset(history_id, content='1\t2\t3'))
            hda2 = dataset_to_param(self.dataset_populator.new_dataset(history_id, content='4\t5\t6'))
            inputs = {
                "f1": {'batch': False, 'values': [hda1, hda2]},
                "f2": {'batch': False, 'values': [hda2, hda1]},
            }
            response = self._run("multi_data_param", history_id, inputs, assert_ok=True)
            output1 = response["outputs"][0]
            output2 = response["outputs"][1]
            output1_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output1)
            output2_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output2)
            assert output1_content == "1\t2\t3\n4\t5\t6\n", output1_content
            assert output2_content == "4\t5\t6\n1\t2\t3\n", output2_content

    @skip_without_tool("cat1")
    def test_run_cat1(self):
        with self.dataset_populator.test_history() as history_id:
            # Run simple non-upload tool with an input data parameter.
            history_id = self.dataset_populator.new_history()
            new_dataset = self.dataset_populator.new_dataset(history_id, content='Cat1Test')
            inputs = dict(
                input1=dataset_to_param(new_dataset),
            )
            outputs = self._cat1_outputs(history_id, inputs=inputs)
            self.assertEquals(len(outputs), 1)
            output1 = outputs[0]
            output1_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output1)
            self.assertEqual(output1_content.strip(), "Cat1Test")

    @skip_without_tool("cat1")
    def test_run_cat1_use_cached_job(self):
        with self.dataset_populator.test_history() as history_id:
            # Run simple non-upload tool with an input data parameter.
            new_dataset = self.dataset_populator.new_dataset(history_id, content='Cat1Test')
            inputs = dict(
                input1=dataset_to_param(new_dataset),
            )
            outputs_one = self._run_cat1(history_id, inputs=inputs, assert_ok=True, wait_for_job=True)
            outputs_two = self._run_cat1(history_id, inputs=inputs, use_cached_job=False, assert_ok=True, wait_for_job=True)
            outputs_three = self._run_cat1(history_id, inputs=inputs, use_cached_job=True, assert_ok=True, wait_for_job=True)
            dataset_details = []
            for output in [outputs_one, outputs_two, outputs_three]:
                output_id = output['outputs'][0]['id']
                dataset_details.append(self._get("datasets/%s" % output_id).json())
            filenames = [dd['file_name'] for dd in dataset_details]
            assert len(filenames) == 3, filenames
            assert len(set(filenames)) <= 2, filenames

    @skip_without_tool("cat1")
    def test_run_cat1_listified_param(self):
        # Run simple non-upload tool with an input data parameter.
        history_id = self.dataset_populator.new_history()
        new_dataset = self.dataset_populator.new_dataset(history_id, content='Cat1Testlistified')
        inputs = dict(
            input1=[dataset_to_param(new_dataset)],
        )
        outputs = self._cat1_outputs(history_id, inputs=inputs)
        self.assertEquals(len(outputs), 1)
        output1 = outputs[0]
        output1_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output1)
        self.assertEqual(output1_content.strip(), "Cat1Testlistified")

    @skip_without_tool("multiple_versions")
    def test_run_by_versions(self):
        for version in ["0.1", "0.2"]:
            # Run simple non-upload tool with an input data parameter.
            history_id = self.dataset_populator.new_history()
            inputs = dict()
            outputs = self._run_and_get_outputs(tool_id="multiple_versions", history_id=history_id, inputs=inputs, tool_version=version)
            self.assertEquals(len(outputs), 1)
            output1 = outputs[0]
            output1_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output1)
            self.assertEqual(output1_content.strip(), "Version " + version)

    @skip_without_tool("cat1")
    def test_run_cat1_single_meta_wrapper(self):
        # Wrap input in a no-op meta parameter wrapper like Sam is planning to
        # use for all UI API submissions.
        history_id = self.dataset_populator.new_history()
        new_dataset = self.dataset_populator.new_dataset(history_id, content='123')
        inputs = dict(
            input1={'batch': False, 'values': [dataset_to_param(new_dataset)]},
        )
        outputs = self._cat1_outputs(history_id, inputs=inputs)
        self.assertEquals(len(outputs), 1)
        output1 = outputs[0]
        output1_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output1)
        self.assertEqual(output1_content.strip(), "123")

    @skip_without_tool("validation_default")
    def test_validation(self):
        history_id = self.dataset_populator.new_history()
        inputs = {
            'select_param': "\" ; echo \"moo",
        }
        response = self._run("validation_default", history_id, inputs)
        self._assert_status_code_is(response, 400)

    @skip_without_tool("validation_empty_dataset")
    def test_validation_empty_dataset(self):
        history_id = self.dataset_populator.new_history()
        inputs = {
        }
        outputs = self._run_and_get_outputs('empty_output', history_id, inputs)
        empty_dataset = outputs[0]
        inputs = {
            'input1': dataset_to_param(empty_dataset),
        }
        self.dataset_populator.wait_for_history(history_id, assert_ok=True)
        response = self._run("validation_empty_dataset", history_id, inputs)
        self._assert_status_code_is(response, 400)

    @skip_without_tool("validation_repeat")
    def test_validation_in_repeat(self):
        history_id = self.dataset_populator.new_history()
        inputs = {
            'r1_0|text': "123",
            'r2_0|text': "",
        }
        response = self._run("validation_repeat", history_id, inputs)
        self._assert_status_code_is(response, 400)

    @skip_without_tool("multi_select")
    def test_select_legal_values(self):
        history_id = self.dataset_populator.new_history()
        inputs = {
            'select_ex': 'not_option',
        }
        response = self._run("multi_select", history_id, inputs)
        self._assert_status_code_is(response, 400)

    @skip_without_tool("column_param")
    def test_column_legal_values(self):
        history_id = self.dataset_populator.new_history()
        new_dataset1 = self.dataset_populator.new_dataset(history_id, content='#col1\tcol2')
        inputs = {
            'input1': {"src": "hda", "id": new_dataset1["id"]},
            'col': "' ; echo 'moo",
        }
        response = self._run("column_param", history_id, inputs)
        # This needs to either fail at submit time or at job prepare time, but we have
        # to make sure the job doesn't run.
        if response.status_code == 200:
            job = response.json()["jobs"][0]
            final_job_state = self.dataset_populator.wait_for_job(job["id"])
            assert final_job_state == "error"

    @skip_without_tool("collection_paired_test")
    def test_collection_parameter(self):
        history_id = self.dataset_populator.new_history()
        hdca_id = self.__build_pair(history_id, ["123", "456"])
        inputs = {
            "f1": {"src": "hdca", "id": hdca_id},
        }
        output = self._run("collection_paired_test", history_id, inputs, assert_ok=True)
        assert len(output['jobs']) == 1
        assert len(output['implicit_collections']) == 0
        assert len(output['outputs']) == 1
        contents = self.dataset_populator.get_history_dataset_content(history_id, hid=4)
        assert contents.strip() == "123\n456", contents

    @skip_without_tool("collection_creates_pair")
    def test_paired_collection_output(self):
        history_id = self.dataset_populator.new_history()
        new_dataset1 = self.dataset_populator.new_dataset(history_id, content='123\n456\n789\n0ab')
        inputs = {
            "input1": {"src": "hda", "id": new_dataset1["id"]},
        }
        # TODO: shouldn't need this wait
        self.dataset_populator.wait_for_history(history_id, assert_ok=True)
        create = self._run("collection_creates_pair", history_id, inputs, assert_ok=True)
        output_collection = self._assert_one_job_one_collection_run(create)
        element0, element1 = self._assert_elements_are(output_collection, "forward", "reverse")
        self.dataset_populator.wait_for_history(history_id, assert_ok=True)
        self._verify_element(history_id, element0, contents="123\n789\n", file_ext="txt", visible=False)
        self._verify_element(history_id, element1, contents="456\n0ab\n", file_ext="txt", visible=False)

    @skip_without_tool("collection_creates_list")
    def test_list_collection_output(self):
        with self.dataset_populator.test_history() as history_id:
            create_response = self.dataset_collection_populator.create_list_in_history(history_id, contents=["a\nb\nc\nd", "e\nf\ng\nh"])
            hdca_id = create_response.json()["id"]
            create = self.dataset_populator.run_collection_creates_list(history_id, hdca_id)
            output_collection = self._assert_one_job_one_collection_run(create)
            element0, element1 = self._assert_elements_are(output_collection, "data1", "data2")
            self.dataset_populator.wait_for_history(history_id, assert_ok=True)
            self._verify_element(history_id, element0, contents="identifier is data1\n", file_ext="txt")
            self._verify_element(history_id, element1, contents="identifier is data2\n", file_ext="txt")

    @skip_without_tool("collection_creates_list_2")
    def test_list_collection_output_format_source(self):
        # test using format_source with a tool
        history_id = self.dataset_populator.new_history()
        new_dataset1 = self.dataset_populator.new_dataset(history_id, content='#col1\tcol2')
        create_response = self.dataset_collection_populator.create_list_in_history(history_id, contents=["a\tb\nc\td", "e\tf\ng\th"])
        hdca_id = create_response.json()["id"]
        inputs = {
            "header": {"src": "hda", "id": new_dataset1["id"]},
            "input_collect": {"src": "hdca", "id": hdca_id},
        }
        # TODO: real problem here - shouldn't have to have this wait.
        self.dataset_populator.wait_for_history(history_id, assert_ok=True)
        create = self._run("collection_creates_list_2", history_id, inputs, assert_ok=True)
        output_collection = self._assert_one_job_one_collection_run(create)
        element0, element1 = self._assert_elements_are(output_collection, "data1", "data2")
        self.dataset_populator.wait_for_history(history_id, assert_ok=True)
        self._verify_element(history_id, element0, contents="#col1\tcol2\na\tb\nc\td\n", file_ext="txt")
        self._verify_element(history_id, element1, contents="#col1\tcol2\ne\tf\ng\th\n", file_ext="txt")

    @skip_without_tool("collection_split_on_column")
    def test_dynamic_list_output(self):
        history_id = self.dataset_populator.new_history()
        new_dataset1 = self.dataset_populator.new_dataset(history_id, content='samp1\t1\nsamp1\t3\nsamp2\t2\nsamp2\t4\n')
        inputs = {
            'input1': dataset_to_param(new_dataset1),
        }
        self.dataset_populator.wait_for_history(history_id, assert_ok=True)
        create = self._run("collection_split_on_column", history_id, inputs, assert_ok=True)

        output_collection = self._assert_one_job_one_collection_run(create)
        self._assert_has_keys(output_collection, "id", "name", "elements", "populated")
        assert not output_collection["populated"]
        assert len(output_collection["elements"]) == 0
        self.assertEquals(output_collection["name"], "Table split on first column")
        self.dataset_populator.wait_for_job(create["jobs"][0]["id"], assert_ok=True)

        get_collection_response = self._get("dataset_collections/%s" % output_collection["id"], data={"instance_type": "history"})
        self._assert_status_code_is(get_collection_response, 200)

        output_collection = get_collection_response.json()
        self._assert_has_keys(output_collection, "id", "name", "elements", "populated")
        assert output_collection["populated"]
        self.assertEquals(output_collection["name"], "Table split on first column")

        assert len(output_collection["elements"]) == 2
        output_element_0 = output_collection["elements"][0]
        assert output_element_0["element_index"] == 0
        assert output_element_0["element_identifier"] == "samp1"
        output_element_hda_0 = output_element_0["object"]
        assert output_element_hda_0["metadata_column_types"] is not None

    @skip_without_tool("cat1")
    def test_run_cat1_with_two_inputs(self):
        # Run tool with an multiple data parameter and grouping (repeat)
        history_id = self.dataset_populator.new_history()
        new_dataset1 = self.dataset_populator.new_dataset(history_id, content='Cat1Test')
        new_dataset2 = self.dataset_populator.new_dataset(history_id, content='Cat2Test')
        inputs = {
            'input1': dataset_to_param(new_dataset1),
            'queries_0|input2': dataset_to_param(new_dataset2)
        }
        outputs = self._cat1_outputs(history_id, inputs=inputs)
        self.assertEquals(len(outputs), 1)
        output1 = outputs[0]
        output1_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output1)
        self.assertEqual(output1_content.strip(), "Cat1Test\nCat2Test")

    @skip_without_tool("cat1")
    def test_multirun_cat1(self):
        history_id, datasets = self._prepare_cat1_multirun()
        inputs = {
            "input1": {
                'batch': True,
                'values': datasets,
            },
        }
        self._check_cat1_multirun(history_id, inputs)

    def _prepare_cat1_multirun(self):
        history_id = self.dataset_populator.new_history()
        new_dataset1 = self.dataset_populator.new_dataset(history_id, content='123')
        new_dataset2 = self.dataset_populator.new_dataset(history_id, content='456')
        return history_id, [dataset_to_param(new_dataset1), dataset_to_param(new_dataset2)]

    def _check_cat1_multirun(self, history_id, inputs):
        outputs = self._cat1_outputs(history_id, inputs=inputs)
        self.assertEquals(len(outputs), 2)
        output1 = outputs[0]
        output2 = outputs[1]
        output1_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output1)
        output2_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output2)
        self.assertEquals(output1_content.strip(), "123")
        self.assertEquals(output2_content.strip(), "456")

    @skip_without_tool("random_lines1")
    def test_multirun_non_data_parameter(self):
        history_id = self.dataset_populator.new_history()
        new_dataset1 = self.dataset_populator.new_dataset(history_id, content='123\n456\n789')
        inputs = {
            'input': dataset_to_param(new_dataset1),
            'num_lines': {'batch': True, 'values': [1, 2, 3]}
        }
        outputs = self._run_and_get_outputs('random_lines1', history_id, inputs)
        # Assert we have three outputs with 1, 2, and 3 lines respectively.
        assert len(outputs) == 3
        outputs_contents = [self.dataset_populator.get_history_dataset_content(history_id, dataset=o).strip() for o in outputs]
        assert sorted(len(c.split("\n")) for c in outputs_contents) == [1, 2, 3]

    @skip_without_tool("cat1")
    def test_multirun_in_repeat(self):
        history_id, common_dataset, repeat_datasets = self._setup_repeat_multirun()
        inputs = {
            "input1": common_dataset,
            'queries_0|input2': {'batch': True, 'values': repeat_datasets},
        }
        self._check_repeat_multirun(history_id, inputs)

    @skip_without_tool("cat1")
    def test_multirun_in_repeat_mismatch(self):
        history_id, common_dataset, repeat_datasets = self._setup_repeat_multirun()
        inputs = {
            "input1": {'batch': False, 'values': [common_dataset]},
            'queries_0|input2': {'batch': True, 'values': repeat_datasets},
        }
        self._check_repeat_multirun(history_id, inputs)

    @skip_without_tool("cat1")
    def test_multirun_on_multiple_inputs(self):
        history_id, first_two, second_two = self._setup_two_multiruns()
        inputs = {
            "input1": {'batch': True, 'values': first_two},
            'queries_0|input2': {'batch': True, 'values': second_two},
        }
        outputs = self._cat1_outputs(history_id, inputs=inputs)
        self.assertEquals(len(outputs), 2)
        outputs_contents = [self.dataset_populator.get_history_dataset_content(history_id, dataset=o).strip() for o in outputs]
        assert "123\n789" in outputs_contents
        assert "456\n0ab" in outputs_contents

    @skip_without_tool("cat1")
    def test_multirun_on_multiple_inputs_unlinked(self):
        history_id, first_two, second_two = self._setup_two_multiruns()
        inputs = {
            "input1": {'batch': True, 'linked': False, 'values': first_two},
            'queries_0|input2': {'batch': True, 'linked': False, 'values': second_two},
        }
        outputs = self._cat1_outputs(history_id, inputs=inputs)
        outputs_contents = [self.dataset_populator.get_history_dataset_content(history_id, dataset=o).strip() for o in outputs]
        self.assertEquals(len(outputs), 4)
        assert "123\n789" in outputs_contents
        assert "456\n0ab" in outputs_contents
        assert "123\n0ab" in outputs_contents
        assert "456\n789" in outputs_contents

    def _assert_one_job_one_collection_run(self, create):
        jobs = create['jobs']
        implicit_collections = create['implicit_collections']
        collections = create['output_collections']

        self.assertEquals(len(jobs), 1)
        self.assertEquals(len(implicit_collections), 0)
        self.assertEquals(len(collections), 1)

        output_collection = collections[0]
        return output_collection

    def _assert_elements_are(self, collection, *args):
        elements = collection["elements"]
        self.assertEquals(len(elements), len(args))
        for index, element in enumerate(elements):
            arg = args[index]
            self.assertEquals(arg, element["element_identifier"])
        return elements

    def _verify_element(self, history_id, element, **props):
        object_id = element["object"]["id"]

        if "contents" in props:
            expected_contents = props["contents"]

            contents = self.dataset_populator.get_history_dataset_content(history_id, dataset_id=object_id)
            self.assertEquals(contents, expected_contents)

            del props["contents"]

        if props:
            details = self.dataset_populator.get_history_dataset_details(history_id, dataset_id=object_id)
            for key, value in props.items():
                self.assertEquals(details[key], value)

    def _setup_repeat_multirun(self):
        history_id = self.dataset_populator.new_history()
        new_dataset1 = self.dataset_populator.new_dataset(history_id, content='123')
        new_dataset2 = self.dataset_populator.new_dataset(history_id, content='456')
        common_dataset = self.dataset_populator.new_dataset(history_id, content='Common')
        return (
            history_id,
            dataset_to_param(common_dataset),
            [dataset_to_param(new_dataset1), dataset_to_param(new_dataset2)]
        )

    def _check_repeat_multirun(self, history_id, inputs):
        outputs = self._cat1_outputs(history_id, inputs=inputs)
        self.assertEquals(len(outputs), 2)
        output1 = outputs[0]
        output2 = outputs[1]
        output1_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output1)
        output2_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output2)
        self.assertEquals(output1_content.strip(), "Common\n123")
        self.assertEquals(output2_content.strip(), "Common\n456")

    def _setup_two_multiruns(self):
        history_id = self.dataset_populator.new_history()
        new_dataset1 = self.dataset_populator.new_dataset(history_id, content='123')
        new_dataset2 = self.dataset_populator.new_dataset(history_id, content='456')
        new_dataset3 = self.dataset_populator.new_dataset(history_id, content='789')
        new_dataset4 = self.dataset_populator.new_dataset(history_id, content='0ab')
        return (
            history_id,
            [dataset_to_param(new_dataset1), dataset_to_param(new_dataset2)],
            [dataset_to_param(new_dataset3), dataset_to_param(new_dataset4)]
        )

    @skip_without_tool("cat1")
    def test_map_over_collection(self):
        history_id = self.dataset_populator.new_history()
        hdca_id = self.__build_pair(history_id, ["123", "456"])
        inputs = {
            "input1": {'batch': True, 'values': [{'src': 'hdca', 'id': hdca_id}]},
        }
        self._run_and_check_simple_collection_mapping(history_id, inputs)

    @skip_without_tool("cat1")
    def test_map_over_empty_collection(self):
        with self.dataset_populator.test_history() as history_id:
            hdca_id = self.dataset_collection_populator.create_list_in_history(history_id, contents=[]).json()['id']
            inputs = {
                "input1": {'batch': True, 'values': [{'src': 'hdca', 'id': hdca_id}]},
            }
            create = self._run_cat1(history_id, inputs=inputs, assert_ok=True)
            outputs = create['outputs']
            jobs = create['jobs']
            implicit_collections = create['implicit_collections']
            self.assertEquals(len(jobs), 0)
            self.assertEquals(len(outputs), 0)
            self.assertEquals(len(implicit_collections), 1)

            empty_output = implicit_collections[0]
            assert empty_output["name"] == "Concatenate datasets on collection 1", empty_output

    @skip_without_tool("output_action_change_format")
    def test_map_over_with_output_format_actions(self):
        for use_action in ["do", "dont"]:
            history_id = self.dataset_populator.new_history()
            hdca_id = self.__build_pair(history_id, ["123", "456"])
            inputs = {
                "input_cond|dispatch": use_action,
                "input_cond|input": {'batch': True, 'values': [{'src': 'hdca', 'id': hdca_id}]},
            }
            create = self._run('output_action_change_format', history_id, inputs).json()
            outputs = create['outputs']
            jobs = create['jobs']
            implicit_collections = create['implicit_collections']
            self.assertEquals(len(jobs), 2)
            self.assertEquals(len(outputs), 2)
            self.assertEquals(len(implicit_collections), 1)
            output1 = outputs[0]
            output2 = outputs[1]
            output1_details = self.dataset_populator.get_history_dataset_details(history_id, dataset=output1)
            output2_details = self.dataset_populator.get_history_dataset_details(history_id, dataset=output2)
            assert output1_details["file_ext"] == "txt" if (use_action == "do") else "data"
            assert output2_details["file_ext"] == "txt" if (use_action == "do") else "data"

    @skip_without_tool("output_action_change_format_paired")
    def test_map_over_with_nested_paired_output_format_actions(self):
        history_id = self.dataset_populator.new_history()
        hdca_id = self.__build_nested_list(history_id)
        inputs = {
            "input": {'batch': True, 'values': [dict(map_over_type='paired', src="hdca", id=hdca_id)]}
        }
        create = self._run('output_action_change_format_paired', history_id, inputs).json()
        outputs = create['outputs']
        jobs = create['jobs']
        implicit_collections = create['implicit_collections']
        self.assertEquals(len(jobs), 2)
        self.assertEquals(len(outputs), 2)
        self.assertEquals(len(implicit_collections), 1)
        for output in outputs:
            assert output["file_ext"] == "txt"

    @skip_without_tool("output_filter_with_input")
    def test_map_over_with_output_filter_no_filtering(self):
        with self.dataset_populator.test_history() as history_id:
            hdca_id = self.dataset_collection_populator.create_list_in_history(history_id).json()["id"]
            inputs = {
                "input_1": {'batch': True, 'values': [{'src': 'hdca', 'id': hdca_id}]},
                "produce_out_1": "true",
                "filter_text_1": "foo",
            }
            create = self._run('output_filter_with_input', history_id, inputs).json()
            jobs = create['jobs']
            implicit_collections = create['implicit_collections']
            self.assertEquals(len(jobs), 3)
            self.assertEquals(len(implicit_collections), 3)
            self._check_implicit_collection_populated(create)

    @skip_without_tool("output_filter_with_input")
    def test_map_over_with_output_filter_one_filtered(self):
        with self.dataset_populator.test_history() as history_id:
            hdca_id = self.dataset_collection_populator.create_list_in_history(history_id).json()["id"]
            inputs = {
                "input_1": {'batch': True, 'values': [{'src': 'hdca', 'id': hdca_id}]},
                "produce_out_1": "true",
                "filter_text_1": "bar",
            }
            create = self._run('output_filter_with_input', history_id, inputs).json()
            jobs = create['jobs']
            implicit_collections = create['implicit_collections']
            self.assertEquals(len(jobs), 3)
            self.assertEquals(len(implicit_collections), 2)
            self._check_implicit_collection_populated(create)

    @skip_without_tool("Cut1")
    def test_map_over_with_complex_output_actions(self):
        history_id = self.dataset_populator.new_history()
        hdca_id = self._bed_list(history_id)
        inputs = {
            "columnList": "c1,c2,c3,c4,c5",
            "delimiter": "T",
            "input": {'batch': True, 'values': [{'src': 'hdca', 'id': hdca_id}]},
        }
        create = self._run('Cut1', history_id, inputs).json()
        outputs = create['outputs']
        jobs = create['jobs']
        implicit_collections = create['implicit_collections']
        self.assertEquals(len(jobs), 2)
        self.assertEquals(len(outputs), 2)
        self.assertEquals(len(implicit_collections), 1)
        output1 = outputs[0]
        output2 = outputs[1]
        output1_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output1)
        output2_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output2)
        assert output1_content.startswith("chr1")
        assert output2_content.startswith("chr1")

    @skip_without_tool("collection_creates_dynamic_list_of_pairs")
    def test_map_over_with_discovered_output_collection_elements(self):
        with self.dataset_populator.test_history() as history_id:
            hdca_id = self.dataset_collection_populator.create_list_in_history(history_id).json()["id"]
            inputs = {
                "input": {"batch": True, "values": [{"src": "hdca", "id": hdca_id}]}
            }
            create = self._run('collection_creates_dynamic_list_of_pairs', history_id, inputs).json()
            implicit_collections = create['implicit_collections']
            self.assertEquals(len(implicit_collections), 1)
            self.assertEquals(implicit_collections[0]['collection_type'], 'list:list:paired')
            self.assertEquals(implicit_collections[0]['elements'][0]['object']['element_count'], None)
            self.dataset_populator.wait_for_job(create["jobs"][0]["id"], assert_ok=True)
            hdca = self._get("histories/%s/contents/dataset_collections/%s" % (history_id, implicit_collections[0]['id'])).json()
            self.assertEquals(hdca['elements'][0]['object']['elements'][0]['object']['elements'][0]['element_identifier'], 'forward')

    def _bed_list(self, history_id):
        bed1_contents = open(self.get_filename("1.bed"), "r").read()
        bed2_contents = open(self.get_filename("2.bed"), "r").read()
        contents = [bed1_contents, bed2_contents]
        hdca = self.dataset_collection_populator.create_list_in_history(history_id, contents=contents).json()
        return hdca["id"]

    def _run_and_check_simple_collection_mapping(self, history_id, inputs):
        create = self._run_cat1(history_id, inputs=inputs, assert_ok=True)
        outputs = create['outputs']
        jobs = create['jobs']
        implicit_collections = create['implicit_collections']
        self.assertEquals(len(jobs), 2)
        self.assertEquals(len(outputs), 2)
        self.assertEquals(len(implicit_collections), 1)
        output1 = outputs[0]
        output2 = outputs[1]
        output1_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output1)
        output2_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output2)
        self.assertEquals(output1_content.strip(), "123")
        self.assertEquals(output2_content.strip(), "456")

    @skip_without_tool("identifier_single")
    def test_identifier_in_map(self):
        history_id = self.dataset_populator.new_history()
        hdca_id = self.__build_pair(history_id, ["123", "456"])
        inputs = {
            "input1": {'batch': True, 'values': [{'src': 'hdca', 'id': hdca_id}]},
        }
        create_response = self._run("identifier_single", history_id, inputs)
        self._assert_status_code_is(create_response, 200)
        create = create_response.json()
        outputs = create['outputs']
        jobs = create['jobs']
        implicit_collections = create['implicit_collections']
        self.assertEquals(len(jobs), 2)
        self.assertEquals(len(outputs), 2)
        self.assertEquals(len(implicit_collections), 1)
        output1 = outputs[0]
        output2 = outputs[1]
        output1_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output1)
        output2_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output2)
        self.assertEquals(output1_content.strip(), "forward")
        self.assertEquals(output2_content.strip(), "reverse")

    @skip_without_tool("identifier_single")
    def test_identifier_outside_map(self):
        history_id = self.dataset_populator.new_history()
        new_dataset1 = self.dataset_populator.new_dataset(history_id, content='123', name="Plain HDA")
        inputs = {
            "input1": {'src': 'hda', 'id': new_dataset1["id"]},
        }
        create_response = self._run("identifier_single", history_id, inputs)
        self._assert_status_code_is(create_response, 200)
        create = create_response.json()
        outputs = create['outputs']
        jobs = create['jobs']
        implicit_collections = create['implicit_collections']
        self.assertEquals(len(jobs), 1)
        self.assertEquals(len(outputs), 1)
        self.assertEquals(len(implicit_collections), 0)
        output1 = outputs[0]
        output1_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output1)
        self.assertEquals(output1_content.strip(), "Plain HDA")

    @skip_without_tool("identifier_multiple")
    def test_identifier_in_multiple_reduce(self):
        history_id = self.dataset_populator.new_history()
        hdca_id = self.__build_pair(history_id, ["123", "456"])
        inputs = {
            "input1": {'src': 'hdca', 'id': hdca_id},
        }
        create_response = self._run("identifier_multiple", history_id, inputs)
        self._assert_status_code_is(create_response, 200)
        create = create_response.json()
        outputs = create['outputs']
        jobs = create['jobs']
        implicit_collections = create['implicit_collections']
        self.assertEquals(len(jobs), 1)
        self.assertEquals(len(outputs), 1)
        self.assertEquals(len(implicit_collections), 0)
        output1 = outputs[0]
        output1_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output1)
        self.assertEquals(output1_content.strip(), "forward\nreverse")

    @skip_without_tool("identifier_multiple_in_conditional")
    def test_identifier_multiple_reduce_in_conditional(self):
        history_id = self.dataset_populator.new_history()
        hdca_id = self.__build_pair(history_id, ["123", "456"])
        inputs = {
            "outer_cond|inner_cond|input1": {'src': 'hdca', 'id': hdca_id},
        }
        create_response = self._run("identifier_multiple_in_conditional", history_id, inputs)
        self._assert_status_code_is(create_response, 200)
        create = create_response.json()
        outputs = create['outputs']
        jobs = create['jobs']
        implicit_collections = create['implicit_collections']
        self.assertEquals(len(jobs), 1)
        self.assertEquals(len(outputs), 1)
        self.assertEquals(len(implicit_collections), 0)
        output1 = outputs[0]
        output1_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output1)
        self.assertEquals(output1_content.strip(), "forward\nreverse")

    @skip_without_tool("identifier_multiple_in_repeat")
    def test_identifier_multiple_reduce_in_repeat(self):
        history_id = self.dataset_populator.new_history()
        hdca_id = self.__build_pair(history_id, ["123", "456"])
        inputs = {
            "the_repeat_0|the_data|input1": {'src': 'hdca', 'id': hdca_id},
        }
        create_response = self._run("identifier_multiple_in_repeat", history_id, inputs)
        self._assert_status_code_is(create_response, 200)
        create = create_response.json()
        outputs = create['outputs']
        jobs = create['jobs']
        implicit_collections = create['implicit_collections']
        self.assertEquals(len(jobs), 1)
        self.assertEquals(len(outputs), 1)
        self.assertEquals(len(implicit_collections), 0)
        output1 = outputs[0]
        output1_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output1)
        self.assertEquals(output1_content.strip(), "forward\nreverse")

    @skip_without_tool("identifier_multiple_in_conditional")
    def test_identifier_multiple_in_conditional(self):
        history_id = self.dataset_populator.new_history()
        new_dataset1 = self.dataset_populator.new_dataset(history_id, content='123', name="Normal HDA1")
        inputs = {
            "outer_cond|inner_cond|input1": {'src': 'hda', 'id': new_dataset1["id"]},
        }
        create_response = self._run("identifier_multiple_in_conditional", history_id, inputs)
        self._assert_status_code_is(create_response, 200)
        create = create_response.json()
        outputs = create['outputs']
        jobs = create['jobs']
        implicit_collections = create['implicit_collections']
        self.assertEquals(len(jobs), 1)
        self.assertEquals(len(outputs), 1)
        self.assertEquals(len(implicit_collections), 0)
        output1 = outputs[0]
        output1_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output1)
        self.assertEquals(output1_content.strip(), "Normal HDA1")

    @skip_without_tool("identifier_multiple")
    def test_identifier_with_multiple_normal_datasets(self):
        history_id = self.dataset_populator.new_history()
        new_dataset1 = self.dataset_populator.new_dataset(history_id, content='123', name="Normal HDA1")
        new_dataset2 = self.dataset_populator.new_dataset(history_id, content='456', name="Normal HDA2")
        inputs = {
            "input1": [
                {'src': 'hda', 'id': new_dataset1["id"]},
                {'src': 'hda', 'id': new_dataset2["id"]}
            ]
        }
        create_response = self._run("identifier_multiple", history_id, inputs)
        self._assert_status_code_is(create_response, 200)
        create = create_response.json()
        outputs = create['outputs']
        jobs = create['jobs']
        implicit_collections = create['implicit_collections']
        self.assertEquals(len(jobs), 1)
        self.assertEquals(len(outputs), 1)
        self.assertEquals(len(implicit_collections), 0)
        output1 = outputs[0]
        output1_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output1)
        self.assertEquals(output1_content.strip(), "Normal HDA1\nNormal HDA2")

    @skip_without_tool("identifier_collection")
    def test_identifier_with_data_collection(self):
        history_id = self.dataset_populator.new_history()

        element_identifiers = self.dataset_collection_populator.list_identifiers(history_id)

        payload = dict(
            instance_type="history",
            history_id=history_id,
            element_identifiers=json.dumps(element_identifiers),
            collection_type="list",
        )

        create_response = self._post("dataset_collections", payload)
        dataset_collection = create_response.json()

        inputs = {
            "input1": {'src': 'hdca', 'id': dataset_collection['id']},
        }

        self.dataset_populator.wait_for_history(history_id, assert_ok=True)
        create_response = self._run("identifier_collection", history_id, inputs)
        self._assert_status_code_is(create_response, 200)
        create = create_response.json()
        outputs = create['outputs']
        jobs = create['jobs']
        self.assertEquals(len(jobs), 1)
        self.assertEquals(len(outputs), 1)
        output1 = outputs[0]
        output1_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output1)
        self.assertEquals(output1_content.strip(), '\n'.join([d['name'] for d in element_identifiers]))

    @skip_without_tool("identifier_in_actions")
    def test_identifier_in_actions(self):
        history_id = self.dataset_populator.new_history()

        element_identifiers = self.dataset_collection_populator.list_identifiers(history_id, contents=["1\t2"])

        payload = dict(
            instance_type="history",
            history_id=history_id,
            element_identifiers=json.dumps(element_identifiers),
            collection_type="list",
        )

        create_response = self._post("dataset_collections", payload)
        dataset_collection = create_response.json()

        inputs = {
            "input": {'batch': True, 'values': [{'src': 'hdca', 'id': dataset_collection['id']}]},
        }

        self.dataset_populator.wait_for_history(history_id, assert_ok=True)
        create_response = self._run("identifier_in_actions", history_id, inputs)
        self._assert_status_code_is(create_response, 200)
        create = create_response.json()
        outputs = create['outputs']
        output1 = outputs[0]

        output_details = self.dataset_populator.get_history_dataset_details(history_id, dataset=output1)
        assert output_details["metadata_column_names"][1] == "data1", output_details

    @skip_without_tool("cat1")
    def test_map_over_nested_collections(self):
        history_id = self.dataset_populator.new_history()
        hdca_id = self.__build_nested_list(history_id)
        inputs = {
            "input1": {'batch': True, 'values': [dict(src="hdca", id=hdca_id)]},
        }
        self._check_simple_cat1_over_nested_collections(history_id, inputs)

    @skip_without_tool("collection_paired_structured_like")
    def test_paired_input_map_over_nested_collections(self):
        history_id = self.dataset_populator.new_history()
        hdca_id = self.__build_nested_list(history_id)
        inputs = {
            "input1": {'batch': True, 'values': [dict(map_over_type='paired', src="hdca", id=hdca_id)]},
        }
        self.dataset_populator.wait_for_history(history_id, assert_ok=True)
        create = self._run("collection_paired_structured_like", history_id, inputs, assert_ok=True)
        jobs = create['jobs']
        implicit_collections = create['implicit_collections']
        self.assertEquals(len(jobs), 2)
        self.assertEquals(len(implicit_collections), 1)
        implicit_collection = implicit_collections[0]
        assert implicit_collection["collection_type"] == "list:paired", implicit_collection["collection_type"]
        outer_elements = implicit_collection["elements"]
        assert len(outer_elements) == 2

    @skip_without_tool("collection_paired_conditional_structured_like")
    def test_paired_input_conditional_map_over_nested_collections(self):
        history_id = self.dataset_populator.new_history()
        hdca_id = self.__build_nested_list(history_id)
        inputs = {
            "cond|cond_param": "paired",
            "cond|input1": {'batch': True, 'values': [dict(map_over_type='paired', src="hdca", id=hdca_id)]},
        }
        self.dataset_populator.wait_for_history(history_id, assert_ok=True)
        create = self._run("collection_paired_conditional_structured_like", history_id, inputs, assert_ok=True)
        jobs = create['jobs']
        implicit_collections = create['implicit_collections']
        self.assertEquals(len(jobs), 2)
        self.assertEquals(len(implicit_collections), 1)
        implicit_collection = implicit_collections[0]
        assert implicit_collection["collection_type"] == "list:paired", implicit_collection["collection_type"]
        outer_elements = implicit_collection["elements"]
        assert len(outer_elements) == 2

    def _check_simple_cat1_over_nested_collections(self, history_id, inputs):
        create = self._run_cat1(history_id, inputs=inputs, assert_ok=True)
        outputs = create['outputs']
        jobs = create['jobs']
        implicit_collections = create['implicit_collections']
        self.assertEquals(len(jobs), 4)
        self.assertEquals(len(outputs), 4)
        self.assertEquals(len(implicit_collections), 1)
        implicit_collection = implicit_collections[0]
        self._assert_has_keys(implicit_collection, "collection_type", "elements")
        assert implicit_collection["collection_type"] == "list:paired"
        assert len(implicit_collection["elements"]) == 2
        first_element, second_element = implicit_collection["elements"]
        assert first_element["element_identifier"] == "test0"
        assert second_element["element_identifier"] == "test1"

        first_object = first_element["object"]
        assert first_object["collection_type"] == "paired"
        assert len(first_object["elements"]) == 2
        first_object_forward_element = first_object["elements"][0]
        self.assertEquals(outputs[0]["id"], first_object_forward_element["object"]["id"])

    @skip_without_tool("cat1")
    def test_map_over_two_collections(self):
        history_id = self.dataset_populator.new_history()
        hdca1_id = self.__build_pair(history_id, ["123", "456"])
        hdca2_id = self.__build_pair(history_id, ["789", "0ab"])
        inputs = {
            "input1": {'batch': True, 'values': [{'src': 'hdca', 'id': hdca1_id}]},
            "queries_0|input2": {'batch': True, 'values': [{'src': 'hdca', 'id': hdca2_id}]},
        }
        self._check_map_cat1_over_two_collections(history_id, inputs)

    def _check_map_cat1_over_two_collections(self, history_id, inputs):
        response = self._run_cat1(history_id, inputs)
        self._assert_status_code_is(response, 200)
        response_object = response.json()
        outputs = response_object['outputs']
        self.assertEquals(len(outputs), 2)
        output1 = outputs[0]
        output2 = outputs[1]
        self.dataset_populator.wait_for_history(history_id)
        output1_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output1)
        output2_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output2)
        self.assertEquals(output1_content.strip(), "123\n789")
        self.assertEquals(output2_content.strip(), "456\n0ab")

        self.assertEquals(len(response_object['jobs']), 2)
        self.assertEquals(len(response_object['implicit_collections']), 1)

    @skip_without_tool("cat1")
    def test_map_over_two_collections_unlinked(self):
        history_id = self.dataset_populator.new_history()
        hdca1_id = self.__build_pair(history_id, ["123", "456"])
        hdca2_id = self.__build_pair(history_id, ["789", "0ab"])
        inputs = {
            "input1": {'batch': True, 'linked': False, 'values': [{'src': 'hdca', 'id': hdca1_id}]},
            "queries_0|input2": {'batch': True, 'linked': False, 'values': [{'src': 'hdca', 'id': hdca2_id}]},
        }
        response = self._run_cat1(history_id, inputs)
        self._assert_status_code_is(response, 200)
        response_object = response.json()
        outputs = response_object['outputs']
        self.assertEquals(len(outputs), 4)

        self.assertEquals(len(response_object['jobs']), 4)
        implicit_collections = response_object['implicit_collections']
        self.assertEquals(len(implicit_collections), 1)
        implicit_collection = implicit_collections[0]
        self.assertEquals(implicit_collection["collection_type"], "paired:paired")

        outer_elements = implicit_collection["elements"]
        assert len(outer_elements) == 2
        element0, element1 = outer_elements
        assert element0["element_identifier"] == "forward"
        assert element1["element_identifier"] == "reverse"

        elements0 = element0["object"]["elements"]
        elements1 = element1["object"]["elements"]

        assert len(elements0) == 2
        assert len(elements1) == 2

        element00, element01 = elements0
        assert element00["element_identifier"] == "forward"
        assert element01["element_identifier"] == "reverse"

        element10, element11 = elements1
        assert element10["element_identifier"] == "forward"
        assert element11["element_identifier"] == "reverse"

        expected_contents_list = [
            (element00, "123\n789\n"),
            (element01, "123\n0ab\n"),
            (element10, "456\n789\n"),
            (element11, "456\n0ab\n"),
        ]
        for (element, expected_contents) in expected_contents_list:
            dataset_id = element["object"]["id"]
            contents = self.dataset_populator.get_history_dataset_content(history_id, dataset_id=dataset_id)
            self.assertEquals(expected_contents, contents)

    @skip_without_tool("cat1")
    def test_map_over_collected_and_individual_datasets(self):
        history_id = self.dataset_populator.new_history()
        hdca1_id = self.__build_pair(history_id, ["123", "456"])
        new_dataset1 = self.dataset_populator.new_dataset(history_id, content='789')
        new_dataset2 = self.dataset_populator.new_dataset(history_id, content='0ab')

        inputs = {
            "input1": {'batch': True, 'values': [{'src': 'hdca', 'id': hdca1_id}]},
            "queries_0|input2": {'batch': True, 'values': [dataset_to_param(new_dataset1), dataset_to_param(new_dataset2)]},
        }
        response = self._run_cat1(history_id, inputs)
        self._assert_status_code_is(response, 200)
        response_object = response.json()
        outputs = response_object['outputs']
        self.assertEquals(len(outputs), 2)

        self.assertEquals(len(response_object['jobs']), 2)
        self.assertEquals(len(response_object['implicit_collections']), 1)

    @skip_without_tool("identifier_source")
    def test_default_identifier_source_map_over(self):
        history_id = self.dataset_populator.new_history()
        input_a_hdca_id = self.dataset_collection_populator.create_list_in_history(history_id, contents=[("A", "A content")]).json()['id']
        input_b_hdca_id = self.dataset_collection_populator.create_list_in_history(history_id, contents=[("B", "B content")]).json()['id']
        inputs = {
            "inputA": {'batch': True, 'values': [dict(src="hdca", id=input_a_hdca_id)]},
            "inputB": {'batch': True, 'values': [dict(src="hdca", id=input_b_hdca_id)]},
        }
        self.dataset_populator.wait_for_history(history_id, assert_ok=True)
        create = self._run("identifier_source", history_id, inputs, assert_ok=True)
        assert create['implicit_collections'][0]['elements'][0]['element_identifier'] == 'B'
        assert create['implicit_collections'][1]['elements'][0]['element_identifier'] == 'A'

    @skip_without_tool("collection_creates_pair")
    def test_map_over_collection_output(self):
        history_id = self.dataset_populator.new_history()
        create_response = self.dataset_collection_populator.create_list_in_history(history_id, contents=["a\nb\nc\nd", "e\nf\ng\nh"])
        hdca_id = create_response.json()["id"]
        inputs = {
            "input1": {'batch': True, 'values': [dict(src="hdca", id=hdca_id)]},
        }
        self.dataset_populator.wait_for_history(history_id, assert_ok=True)
        create = self._run("collection_creates_pair", history_id, inputs, assert_ok=True)
        jobs = create['jobs']
        implicit_collections = create['implicit_collections']
        self.assertEquals(len(jobs), 2)
        self.assertEquals(len(implicit_collections), 1)
        implicit_collection = implicit_collections[0]
        assert implicit_collection["collection_type"] == "list:paired", implicit_collection
        outer_elements = implicit_collection["elements"]
        assert len(outer_elements) == 2
        element0, element1 = outer_elements
        assert element0["element_identifier"] == "data1"
        assert element1["element_identifier"] == "data2"

        pair0, pair1 = element0["object"], element1["object"]
        pair00, pair01 = pair0["elements"]
        pair10, pair11 = pair1["elements"]

        for pair in pair0, pair1:
            assert "collection_type" in pair, pair
            assert pair["collection_type"] == "paired", pair

        pair_ids = []
        for pair_element in pair00, pair01, pair10, pair11:
            assert "object" in pair_element
            pair_ids.append(pair_element["object"]["id"])

        self.dataset_populator.wait_for_history(history_id, assert_ok=True)
        expected_contents = [
            "a\nc\n",
            "b\nd\n",
            "e\ng\n",
            "f\nh\n",
        ]
        for i in range(4):
            contents = self.dataset_populator.get_history_dataset_content(history_id, dataset_id=pair_ids[i])
            self.assertEquals(expected_contents[i], contents)

    @skip_without_tool("cat1")
    def test_cannot_map_over_incompatible_collections(self):
        history_id = self.dataset_populator.new_history()
        hdca1_id = self.__build_pair(history_id, ["123", "456"])
        hdca2_id = self.dataset_collection_populator.create_list_in_history(history_id).json()["id"]
        inputs = {
            "input1": {
                'batch': True,
                'values': [{'src': 'hdca', 'id': hdca1_id}],
            },
            "queries_0|input2": {
                'batch': True,
                'values': [{'src': 'hdca', 'id': hdca2_id}],
            },
        }
        run_response = self._run_cat1(history_id, inputs)
        # TODO: Fix this error checking once switch over to new API decorator
        # on server.
        assert run_response.status_code >= 400

    @skip_without_tool("__FILTER_FROM_FILE__")
    def test_map_over_collection_structured_like(self):
        with self.dataset_populator.test_history() as history_id:
            hdca_id = self.dataset_collection_populator.create_list_in_history(history_id, contents=[("A", "A"), ("B", "B")]).json()['id']
            self.dataset_populator.wait_for_history(history_id, assert_ok=True)
            inputs = {
                "input": {'values': [dict(src="hdca", id=hdca_id)]},
                "how|filter_source": {'batch': True, 'values': [dict(src="hdca", id=hdca_id)]}
            }
            self._run("__FILTER_FROM_FILE__", history_id, inputs, assert_ok=True)
            self.dataset_populator.wait_for_history(history_id, assert_ok=True)
            history_contents = self.dataset_populator._get_contents_request(history_id).json()
            # We should have a final collection count of 3 (2 nested collections, plus the input collection)
            new_collections = len([c for c in history_contents if c['history_content_type'] == 'dataset_collection']) - 1
            assert new_collections == 2, "Expected to generate 4 new, filtered collections, but got %d collections" % new_collections
            filtered_collection = history_contents[7]
            assert filtered_collection['collection_type'] == 'list:list', filtered_collection
            collection_details = self.dataset_populator.get_history_collection_details(history_id, hid=filtered_collection['hid'])
            assert collection_details['element_count'] == 2
            first_collection_level = collection_details['elements'][0]
            assert first_collection_level['element_type'] == 'dataset_collection'
            second_collection_level = first_collection_level['object']
            assert second_collection_level['collection_type'] == 'list'
            assert second_collection_level['elements'][0]['element_type'] == 'hda'

    @skip_without_tool("collection_type_source")
    def test_map_over_collection_type_source(self):
        with self.dataset_populator.test_history() as history_id:
            hdca_id = self.dataset_collection_populator.create_list_in_history(history_id, contents=[("A", "A"), ("B", "B")]).json()['id']
            self.dataset_populator.wait_for_history(history_id, assert_ok=True)
            inputs = {
                "input_collect": {'values': [dict(src="hdca", id=hdca_id)]},
                "header": {'batch': True, 'values': [dict(src="hdca", id=hdca_id)]}
            }
            self._run("collection_type_source", history_id, inputs, assert_ok=True, wait_for_job=True)
            collection_details = self.dataset_populator.get_history_collection_details(history_id, hid=4)
            assert collection_details['elements'][0]['object']['elements'][0]['element_type'] == 'hda'

    @skip_without_tool("multi_data_param")
    def test_reduce_collections_legacy(self):
        history_id = self.dataset_populator.new_history()
        hdca1_id = self.__build_pair(history_id, ["123", "456"])
        hdca2_id = self.dataset_collection_populator.create_list_in_history(history_id).json()["id"]
        inputs = {
            "f1": "__collection_reduce__|%s" % hdca1_id,
            "f2": "__collection_reduce__|%s" % hdca2_id,
        }
        self._check_simple_reduce_job(history_id, inputs)

    @skip_without_tool("multi_data_param")
    def test_reduce_collections(self):
        history_id = self.dataset_populator.new_history()
        hdca1_id = self.__build_pair(history_id, ["123", "456"])
        hdca2_id = self.dataset_collection_populator.create_list_in_history(history_id).json()["id"]
        inputs = {
            "f1": {'src': 'hdca', 'id': hdca1_id},
            "f2": {'src': 'hdca', 'id': hdca2_id},
        }
        self._check_simple_reduce_job(history_id, inputs)

    @skip_without_tool("multi_data_repeat")
    def test_reduce_collections_in_repeat(self):
        history_id = self.dataset_populator.new_history()
        hdca1_id = self.__build_pair(history_id, ["123", "456"])
        inputs = {
            "outer_repeat_0|f1": {'src': 'hdca', 'id': hdca1_id},
        }
        create = self._run("multi_data_repeat", history_id, inputs, assert_ok=True)
        outputs = create['outputs']
        jobs = create['jobs']
        self.assertEquals(len(jobs), 1)
        self.assertEquals(len(outputs), 1)
        output1 = outputs[0]
        output1_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output1)
        assert output1_content.strip() == "123\n456", output1_content

    @skip_without_tool("multi_data_repeat")
    def test_reduce_collections_in_repeat_legacy(self):
        history_id = self.dataset_populator.new_history()
        hdca1_id = self.__build_pair(history_id, ["123", "456"])
        inputs = {
            "outer_repeat_0|f1": "__collection_reduce__|%s" % hdca1_id,
        }
        create = self._run("multi_data_repeat", history_id, inputs, assert_ok=True)
        outputs = create['outputs']
        jobs = create['jobs']
        self.assertEquals(len(jobs), 1)
        self.assertEquals(len(outputs), 1)
        output1 = outputs[0]
        output1_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output1)
        assert output1_content.strip() == "123\n456", output1_content

    @skip_without_tool("multi_data_param")
    def test_reduce_multiple_lists_on_multi_data(self):
        history_id = self.dataset_populator.new_history()
        hdca1_id = self.__build_pair(history_id, ["123", "456"])
        hdca2_id = self.dataset_collection_populator.create_list_in_history(history_id).json()["id"]
        inputs = {
            "f1": [{'src': 'hdca', 'id': hdca1_id}, {'src': 'hdca', 'id': hdca2_id}],
            "f2": [{'src': 'hdca', 'id': hdca1_id}],
        }
        create = self._run("multi_data_param", history_id, inputs, assert_ok=True)
        outputs = create['outputs']
        jobs = create['jobs']
        self.assertEquals(len(jobs), 1)
        self.assertEquals(len(outputs), 2)
        output1, output2 = outputs
        output1_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output1)
        output2_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output2)
        self.assertEquals(output1_content.strip(), "123\n456\nTestData123\nTestData123\nTestData123")
        self.assertEquals(output2_content.strip(), "123\n456")

    def _check_simple_reduce_job(self, history_id, inputs):
        create = self._run("multi_data_param", history_id, inputs, assert_ok=True)
        outputs = create['outputs']
        jobs = create['jobs']
        self.assertEquals(len(jobs), 1)
        self.assertEquals(len(outputs), 2)
        output1, output2 = outputs
        output1_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output1)
        output2_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output2)
        assert output1_content.strip() == "123\n456"
        assert len(output2_content.strip().split("\n")) == 3, output2_content

    @skip_without_tool("collection_paired_test")
    def test_subcollection_mapping(self):
        history_id = self.dataset_populator.new_history()
        hdca_list_id = self.__build_nested_list(history_id)
        inputs = {
            "f1": {
                'batch': True,
                'values': [{'src': 'hdca', 'map_over_type': 'paired', 'id': hdca_list_id}],
            }
        }
        self._check_simple_subcollection_mapping(history_id, inputs)

    def _check_simple_subcollection_mapping(self, history_id, inputs):
        # Following wait not really needed - just getting so many database
        # locked errors with sqlite.
        self.dataset_populator.wait_for_history(history_id, assert_ok=True)
        outputs = self._run_and_get_outputs("collection_paired_test", history_id, inputs)
        assert len(outputs), 2
        output1 = outputs[0]
        output2 = outputs[1]
        output1_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output1)
        output2_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output2)
        assert output1_content.strip() == "123\n456", output1_content
        assert output2_content.strip() == "789\n0ab", output2_content

    @skip_without_tool("collection_mixed_param")
    def test_combined_mapping_and_subcollection_mapping(self):
        history_id = self.dataset_populator.new_history()
        nested_list_id = self.__build_nested_list(history_id)
        create_response = self.dataset_collection_populator.create_list_in_history(history_id, contents=["xxx", "yyy"])
        list_id = create_response.json()["id"]
        inputs = {
            "f1": {
                'batch': True,
                'values': [{'src': 'hdca', 'map_over_type': 'paired', 'id': nested_list_id}],
            },
            "f2": {
                'batch': True,
                'values': [{'src': 'hdca', 'id': list_id}],
            },
        }
        self._check_combined_mapping_and_subcollection_mapping(history_id, inputs)

    def _check_combined_mapping_and_subcollection_mapping(self, history_id, inputs):
        self.dataset_populator.wait_for_history(history_id, assert_ok=True)
        outputs = self._run_and_get_outputs("collection_mixed_param", history_id, inputs)
        assert len(outputs), 2
        output1 = outputs[0]
        output2 = outputs[1]
        output1_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output1)
        output2_content = self.dataset_populator.get_history_dataset_content(history_id, dataset=output2)
        assert output1_content.strip() == "123\n456\nxxx", output1_content
        assert output2_content.strip() == "789\n0ab\nyyy", output2_content

    def _check_implicit_collection_populated(self, run_response):
        implicit_collections = run_response["implicit_collections"]
        assert implicit_collections
        for implicit_collection in implicit_collections:
            assert implicit_collection["populated_state"] == "ok"

    def _cat1_outputs(self, history_id, inputs):
        return self._run_outputs(self._run_cat1(history_id, inputs))

    def _run_and_get_outputs(self, tool_id, history_id, inputs, tool_version=None):
        return self._run_outputs(self._run(tool_id, history_id, inputs, tool_version=tool_version))

    def _run_outputs(self, create_response):
        self._assert_status_code_is(create_response, 200)
        return create_response.json()['outputs']

    def _run_cat1(self, history_id, inputs, assert_ok=False, **kwargs):
        return self._run('cat1', history_id, inputs, assert_ok=assert_ok, **kwargs)

    def _run(self, tool_id, history_id, inputs, assert_ok=False, tool_version=None, use_cached_job=False, wait_for_job=False):
        payload = self.dataset_populator.run_tool_payload(
            tool_id=tool_id,
            inputs=inputs,
            history_id=history_id,
        )
        if tool_version is not None:
            payload["tool_version"] = tool_version
        if use_cached_job:
            payload['use_cached_job'] = True
        create_response = self._post("tools", data=payload)
        if wait_for_job:
            self.dataset_populator.wait_for_job(job_id=create_response.json()['jobs'][0]['id'])
        if assert_ok:
            self._assert_status_code_is(create_response, 200)
            create = create_response.json()
            self._assert_has_keys(create, 'outputs')
            return create
        else:
            return create_response

    def __tool_ids(self):
        index = self._get("tools")
        tools_index = index.json()
        # In panels by default, so flatten out sections...
        tools = []
        for tool_or_section in tools_index:
            if "elems" in tool_or_section:
                tools.extend(tool_or_section["elems"])
            else:
                tools.append(tool_or_section)

        tool_ids = [_["id"] for _ in tools]
        return tool_ids

    def __build_nested_list(self, history_id):
        hdca1_id = self.__build_pair(history_id, ["123", "456"])
        hdca2_id = self.__build_pair(history_id, ["789", "0ab"])

        response = self.dataset_collection_populator.create_list_from_pairs(history_id, [hdca1_id, hdca2_id])
        self._assert_status_code_is(response, 200)
        hdca_list_id = response.json()["id"]
        return hdca_list_id

    def __build_pair(self, history_id, contents):
        create_response = self.dataset_collection_populator.create_pair_in_history(history_id, contents=contents)
        hdca_id = create_response.json()["id"]
        return hdca_id


def dataset_to_param(dataset):
    return dict(
        src='hda',
        id=dataset['id']
    )
