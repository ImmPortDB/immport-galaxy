# -*- coding: utf-8 -*-

import json

from requests import delete, put

from base import api  # noqa: I100,I202
from base.populators import (  # noqa: I100
    DatasetCollectionPopulator,
    DatasetPopulator,
    LibraryPopulator,
    skip_without_tool,
    TestsDatasets,
)


# TODO: Test anonymous access.
class HistoryContentsApiTestCase(api.ApiTestCase, TestsDatasets):

    def setUp(self):
        super(HistoryContentsApiTestCase, self).setUp()
        self.history_id = self._new_history()
        self.dataset_populator = DatasetPopulator(self.galaxy_interactor)
        self.dataset_collection_populator = DatasetCollectionPopulator(self.galaxy_interactor)
        self.library_populator = LibraryPopulator(self.galaxy_interactor)

    def test_index_hda_summary(self):
        hda1 = self._new_dataset(self.history_id)
        contents_response = self._get("histories/%s/contents" % self.history_id)
        hda_summary = self.__check_for_hda(contents_response, hda1)
        assert "display_types" not in hda_summary  # Quick summary, not full details

    def test_index_hda_all_details(self):
        hda1 = self._new_dataset(self.history_id)
        contents_response = self._get("histories/%s/contents?details=all" % self.history_id)
        hda_details = self.__check_for_hda(contents_response, hda1)
        self.__assert_hda_has_full_details(hda_details)

    def test_index_hda_detail_by_id(self):
        hda1 = self._new_dataset(self.history_id)
        contents_response = self._get("histories/%s/contents?details=%s" % (self.history_id, hda1["id"]))
        hda_details = self.__check_for_hda(contents_response, hda1)
        self.__assert_hda_has_full_details(hda_details)

    def test_show_hda(self):
        hda1 = self._new_dataset(self.history_id)
        show_response = self.__show(hda1)
        self._assert_status_code_is(show_response, 200)
        self.__assert_matches_hda(hda1, show_response.json())

    def test_hda_copy(self):
        hda1 = self._new_dataset(self.history_id)
        create_data = dict(
            source='hda',
            content=hda1["id"],
        )
        second_history_id = self._new_history()
        assert self.__count_contents(second_history_id) == 0
        create_response = self._post("histories/%s/contents" % second_history_id, create_data)
        self._assert_status_code_is(create_response, 200)
        assert self.__count_contents(second_history_id) == 1

    def test_library_copy(self):
        ld = self.library_populator.new_library_dataset("lda_test_library")
        create_data = dict(
            source='library',
            content=ld["id"],
        )
        assert self.__count_contents(self.history_id) == 0
        create_response = self._post("histories/%s/contents" % self.history_id, create_data)
        self._assert_status_code_is(create_response, 200)
        assert self.__count_contents(self.history_id) == 1

    def test_update(self):
        hda1 = self._wait_for_new_hda()
        assert str(hda1["deleted"]).lower() == "false"
        update_response = self._raw_update(hda1["id"], dict(deleted=True))
        self._assert_status_code_is(update_response, 200)
        show_response = self.__show(hda1)
        assert str(show_response.json()["deleted"]).lower() == "true"

        update_response = self._raw_update(hda1["id"], dict(name="Updated Name"))
        assert self.__show(hda1).json()["name"] == "Updated Name"

        update_response = self._raw_update(hda1["id"], dict(name="Updated Name"))
        assert self.__show(hda1).json()["name"] == "Updated Name"

        unicode_name = u'ржевский сапоги'
        update_response = self._raw_update(hda1["id"], dict(name=unicode_name))
        updated_hda = self.__show(hda1).json()
        assert updated_hda["name"] == unicode_name, updated_hda

        quoted_name = '"Mooo"'
        update_response = self._raw_update(hda1["id"], dict(name=quoted_name))
        updated_hda = self.__show(hda1).json()
        assert updated_hda["name"] == quoted_name, quoted_name

    def test_update_type_failures(self):
        hda1 = self._wait_for_new_hda()
        update_response = self._raw_update(hda1["id"], dict(deleted='not valid'))
        self._assert_status_code_is(update_response, 400)

    def _wait_for_new_hda(self):
        hda1 = self._new_dataset(self.history_id)
        self._wait_for_history(self.history_id)
        return hda1

    def _raw_update(self, item_id, data):
        update_url = self._api_url("histories/%s/contents/%s" % (self.history_id, item_id), use_key=True)
        update_response = put(update_url, json=data)
        return update_response

    def test_delete(self):
        hda1 = self._new_dataset(self.history_id)
        self._wait_for_history(self.history_id)
        assert str(self.__show(hda1).json()["deleted"]).lower() == "false"
        delete_response = self._delete("histories/%s/contents/%s" % (self.history_id, hda1["id"]))
        assert delete_response.status_code < 300  # Something in the 200s :).
        assert str(self.__show(hda1).json()["deleted"]).lower() == "true"

    def test_purge(self):
        hda1 = self._new_dataset(self.history_id)
        self._wait_for_history(self.history_id)
        assert str(self.__show(hda1).json()["deleted"]).lower() == "false"
        assert str(self.__show(hda1).json()["purged"]).lower() == "false"
        data = {'purge': True}
        delete_response = self._delete("histories/%s/contents/%s" % (self.history_id, hda1["id"]), data=data)
        assert delete_response.status_code < 300  # Something in the 200s :).
        assert str(self.__show(hda1).json()["deleted"]).lower() == "true"
        assert str(self.__show(hda1).json()["purged"]).lower() == "true"

    def test_dataset_collection_creation_on_contents(self):
        payload = self.dataset_collection_populator.create_pair_payload(
            self.history_id,
            type="dataset_collection"
        )
        endpoint = "histories/%s/contents" % self.history_id
        self._check_pair_creation(endpoint, payload)

    def test_dataset_collection_creation_on_typed_contents(self):
        payload = self.dataset_collection_populator.create_pair_payload(
            self.history_id,
        )
        endpoint = "histories/%s/contents/dataset_collections" % self.history_id
        self._check_pair_creation(endpoint, payload)

    def _check_pair_creation(self, endpoint, payload):
        pre_collection_count = self.__count_contents(type="dataset_collection")
        pre_dataset_count = self.__count_contents(type="dataset")
        pre_combined_count = self.__count_contents(type="dataset,dataset_collection")

        dataset_collection_response = self._post(endpoint, payload)

        dataset_collection = self.__check_create_collection_response(dataset_collection_response)

        post_collection_count = self.__count_contents(type="dataset_collection")
        post_dataset_count = self.__count_contents(type="dataset")
        post_combined_count = self.__count_contents(type="dataset,dataset_collection")

        # Test filtering types with index.
        assert pre_collection_count == 0
        assert post_collection_count == 1
        assert post_combined_count == pre_dataset_count + 1
        assert post_combined_count == pre_combined_count + 1
        assert pre_dataset_count == post_dataset_count

        # Test show dataset colleciton.
        collection_url = "histories/%s/contents/dataset_collections/%s" % (self.history_id, dataset_collection["id"])
        show_response = self._get(collection_url)
        self._assert_status_code_is(show_response, 200)
        dataset_collection = show_response.json()
        self._assert_has_keys(dataset_collection, "url", "name", "deleted")

        assert not dataset_collection["deleted"]

        delete_response = delete(self._api_url(collection_url, use_key=True))
        self._assert_status_code_is(delete_response, 200)

        show_response = self._get(collection_url)
        dataset_collection = show_response.json()
        assert dataset_collection["deleted"]

    @skip_without_tool("collection_creates_list")
    def test_jobs_summary_simple_hdca(self):
        create_response = self.dataset_collection_populator.create_list_in_history(self.history_id, contents=["a\nb\nc\nd", "e\nf\ng\nh"])
        hdca_id = create_response.json()["id"]
        run = self.dataset_populator.run_collection_creates_list(self.history_id, hdca_id)
        collections = run['output_collections']
        collection = collections[0]
        jobs_summary_url = "histories/%s/contents/dataset_collections/%s/jobs_summary" % (self.history_id, collection["id"])
        jobs_summary_response = self._get(jobs_summary_url)
        self._assert_status_code_is(jobs_summary_response, 200)
        jobs_summary = jobs_summary_response.json()
        self._assert_has_keys(jobs_summary, "populated_state", "states")

    @skip_without_tool("cat1")
    def test_jobs_summary_implicit_hdca(self):
        create_response = self.dataset_collection_populator.create_pair_in_history(self.history_id, contents=["123", "456"])
        hdca_id = create_response.json()["id"]
        inputs = {
            "input1": {'batch': True, 'values': [{'src': 'hdca', 'id': hdca_id}]},
        }
        run = self.dataset_populator.run_tool("cat1", inputs=inputs, history_id=self.history_id)
        self.dataset_populator.wait_for_history_jobs(self.history_id)
        collections = run['implicit_collections']
        collection = collections[0]
        jobs_summary_url = "histories/%s/contents/dataset_collections/%s/jobs_summary" % (self.history_id, collection["id"])
        jobs_summary_response = self._get(jobs_summary_url)
        self._assert_status_code_is(jobs_summary_response, 200)
        jobs_summary = jobs_summary_response.json()
        self._assert_has_keys(jobs_summary, "populated_state", "states")
        states = jobs_summary["states"]
        assert states.get("ok") == 2, states

    def test_dataset_collection_hide_originals(self):
        payload = self.dataset_collection_populator.create_pair_payload(
            self.history_id,
            type="dataset_collection"
        )

        payload["hide_source_items"] = True
        dataset_collection_response = self._post("histories/%s/contents" % self.history_id, payload)
        self.__check_create_collection_response(dataset_collection_response)

        contents_response = self._get("histories/%s/contents" % self.history_id)
        datasets = [d for d in contents_response.json() if d["history_content_type"] == "dataset" and d["hid"] in [1, 2]]
        # Assert two datasets in source were hidden.
        assert len(datasets) == 2
        assert not datasets[0]["visible"]
        assert not datasets[1]["visible"]

    def test_update_dataset_collection(self):
        payload = self.dataset_collection_populator.create_pair_payload(
            self.history_id,
            type="dataset_collection"
        )
        dataset_collection_response = self._post("histories/%s/contents" % self.history_id, payload)
        self._assert_status_code_is(dataset_collection_response, 200)
        hdca = dataset_collection_response.json()
        update_url = self._api_url("histories/%s/contents/dataset_collections/%s" % (self.history_id, hdca["id"]), use_key=True)
        # Awkward json.dumps required here because of https://trello.com/c/CQwmCeG6
        body = json.dumps(dict(name="newnameforpair"))
        update_response = put(update_url, data=body)
        self._assert_status_code_is(update_response, 200)
        show_response = self.__show(hdca)
        assert str(show_response.json()["name"]) == "newnameforpair"

    def test_hdca_copy(self):
        hdca = self.dataset_collection_populator.create_pair_in_history(self.history_id).json()
        hdca_id = hdca["id"]
        second_history_id = self._new_history()
        create_data = dict(
            source='hdca',
            content=hdca_id,
        )
        assert len(self._get("histories/%s/contents/dataset_collections" % second_history_id).json()) == 0
        create_response = self._post("histories/%s/contents/dataset_collections" % second_history_id, create_data)
        self.__check_create_collection_response(create_response)
        contents = self._get("histories/%s/contents/dataset_collections" % second_history_id).json()
        assert len(contents) == 1
        new_forward, _ = self.__get_paired_response_elements(contents[0])
        self._assert_has_keys(new_forward, "history_id")
        assert new_forward["history_id"] == self.history_id

    def test_hdca_copy_and_elements(self):
        hdca = self.dataset_collection_populator.create_pair_in_history(self.history_id).json()
        hdca_id = hdca["id"]
        second_history_id = self._new_history()
        create_data = dict(
            source='hdca',
            content=hdca_id,
            copy_elements=True,
        )
        assert len(self._get("histories/%s/contents/dataset_collections" % second_history_id).json()) == 0
        create_response = self._post("histories/%s/contents/dataset_collections" % second_history_id, create_data)
        self.__check_create_collection_response(create_response)

        contents = self._get("histories/%s/contents/dataset_collections" % second_history_id).json()
        assert len(contents) == 1
        new_forward, _ = self.__get_paired_response_elements(contents[0])
        self._assert_has_keys(new_forward, "history_id")
        assert new_forward["history_id"] == second_history_id

    def __get_paired_response_elements(self, contents):
        hdca = self.__show(contents).json()
        self._assert_has_keys(hdca, "name", "deleted", "visible", "elements")
        elements = hdca["elements"]
        assert len(elements) == 2
        element0 = elements[0]
        element1 = elements[1]
        self._assert_has_keys(element0, "object")
        self._assert_has_keys(element1, "object")

        return element0["object"], element1["object"]

    def test_hdca_from_library_datasets(self):
        ld = self.library_populator.new_library_dataset("el1")
        ldda_id = ld["ldda_id"]
        element_identifiers = [{"name": "el1", "src": "ldda", "id": ldda_id}]
        create_data = dict(
            history_id=self.history_id,
            type="dataset_collection",
            name="Test From Library",
            element_identifiers=json.dumps(element_identifiers),
            collection_type="list",
        )
        create_response = self._post("histories/%s/contents/dataset_collections" % self.history_id, create_data)
        hdca = self.__check_create_collection_response(create_response)
        elements = hdca["elements"]
        assert len(elements) == 1
        hda = elements[0]["object"]
        assert hda["hda_ldda"] == "hda"
        assert hda["history_content_type"] == "dataset"
        assert hda["copied_from_ldda_id"] == ldda_id

    def test_hdca_from_inaccessible_library_datasets(self):
        library, library_dataset = self.library_populator.new_library_dataset_in_private_library("HDCACreateInaccesibleLibrary")
        ldda_id = library_dataset["id"]
        element_identifiers = [{"name": "el1", "src": "ldda", "id": ldda_id}]
        create_data = dict(
            history_id=self.history_id,
            type="dataset_collection",
            name="Test From Library",
            element_identifiers=json.dumps(element_identifiers),
            collection_type="list",
        )
        with self._different_user():
            second_history_id = self._new_history()
            create_response = self._post("histories/%s/contents/dataset_collections" % second_history_id, create_data)
            # TODO: This should be 403 and a proper JSON response.
            self._assert_status_code_is(create_response, 400)

    def __check_create_collection_response(self, response):
        self._assert_status_code_is(response, 200)
        dataset_collection = response.json()
        self._assert_has_keys(dataset_collection, "url", "name", "deleted", "visible", "elements")
        return dataset_collection

    def __show(self, contents):
        show_response = self._get("histories/%s/contents/%ss/%s" % (self.history_id, contents["history_content_type"], contents["id"]))
        return show_response

    def __count_contents(self, history_id=None, **kwds):
        if history_id is None:
            history_id = self.history_id
        contents_response = self._get("histories/%s/contents" % history_id, kwds)
        return len(contents_response.json())

    def __assert_hda_has_full_details(self, hda_details):
        self._assert_has_keys(hda_details, "display_types", "display_apps")

    def __check_for_hda(self, contents_response, hda):
        self._assert_status_code_is(contents_response, 200)
        contents = contents_response.json()
        assert len(contents) == 1
        hda_summary = contents[0]
        self.__assert_matches_hda(hda, hda_summary)
        return hda_summary

    def __assert_matches_hda(self, input_hda, query_hda):
        self._assert_has_keys(query_hda, "id", "name")
        assert input_hda["name"] == query_hda["name"]
        assert input_hda["id"] == query_hda["id"]
