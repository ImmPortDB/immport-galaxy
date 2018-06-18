import yaml
from base import rules_test_data

from galaxy.util import rules_dsl


def test_rules():
    for test_case in yaml.safe_load(rules_test_data.RULES_DSL_SPEC_STR):
        rule_set = rules_dsl.RuleSet(test_case)
        if "initial" in test_case:
            initial = test_case["initial"]
            final_data, final_sources = rule_set.apply(initial["data"], initial["sources"])
            expected_final = test_case["final"]
            for final_row, expected_final_row in zip(final_data, expected_final["data"]):
                msg = "%s != %s" % (final_row, expected_final_row)
                assert len(final_row) == len(expected_final_row), msg
                for final_val, expected_final_val in zip(final_row, expected_final_row):
                    assert final_val == expected_final_val, msg
        elif "error" in test_case:
            assert rule_set.has_errors, "rule [%s] does not contain errors" % test_case
        else:
            raise Exception("Problem with test case definition [%s]." % test_case)
