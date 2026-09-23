"""P0-A tests: uniform plural dispatch, and one stage-state source.

Two defects this file pins down, both named in the handoff:

1. The batch runner read only the SINGULAR `dispatch` for every stage except
   INPUT_SYNC. A per-TM result that carries the plural `dispatchableRoles` with
   `dispatch: None` therefore collapsed to "no unique role" and the stage ended
   early — the "empty dispatch" the handoff forbids. The plural list must be the
   authority at every stage.
2. Stage order and the CORRECTION_STRATEGY alias were declared twice, in
   `ate_ptc_batch_runner.STAGE_ORDER` and `ate_ptc_runner.STAGE_ALIASES`, while
   `team/ptc/ptc_stage_registry.json` is supposed to be the only state source.

Run:  python -m unittest test_ptc_dispatch_plural_and_stage_source -v
      (from the scripts directory)
"""
import importlib.util
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


batch = load("batch_plural", "ate_ptc_batch_runner.py")
single = load("single_plural", "ate_ptc_runner.py")


def item(tm, state, dispatch=None, roles=None):
    result = {"state": state, "dispatch": dispatch, "reason": state}
    if roles is not None:
        result["dispatchableRoles"] = roles
    return {"tm": tm, "trial": f"C:/trial/{tm.lower()}", "result": result}


class DispatchRoleNormalisation(unittest.TestCase):
    def test_dispatch_roles_prefers_the_plural_list_and_falls_back_to_the_singular(self):
        self.assertEqual(single.dispatch_roles({"dispatchableRoles": ["a", "b"], "dispatch": None}), ["a", "b"])
        self.assertEqual(single.dispatch_roles({"dispatch": "only"}), ["only"])
        self.assertEqual(single.dispatch_roles({}), [])
        self.assertEqual(single.dispatch_roles({"dispatch": None}), [])
        self.assertEqual(single.dispatch_roles({"dispatch": "x", "dispatchableRoles": ["a", "b"]}), ["a", "b"])

    def test_dispatch_roles_keeps_order_and_drops_blanks_and_repeats(self):
        self.assertEqual(
            single.dispatch_roles({"dispatchableRoles": ["b", "a", "b", None, "", "a"]}),
            ["b", "a"],
        )


class PluralDispatchAtEveryStage(unittest.TestCase):
    def test_a_second_stage_with_plural_only_roles_is_dispatched_not_blocked(self):
        result = batch.aggregate([
            item("TM106", "STRATEGY", None, roles=["test-strategy-architect"]),
            item("TM108", "STRATEGY", None, roles=["test-strategy-architect"]),
        ])
        self.assertEqual(result["state"], "STRATEGY")
        self.assertEqual(result["dispatch"], "test-strategy-architect")
        self.assertEqual(result["targetTms"], ["TM106", "TM108"])
        self.assertEqual(result["dispatchableRoles"], ["test-strategy-architect"])

    def test_the_plural_list_is_produced_for_an_ordinary_singular_result_too(self):
        result = batch.aggregate([
            item("TM106", "METHOD", "test-method-expert"),
            item("TM108", "METHOD", "test-method-expert"),
        ])
        self.assertEqual(result["dispatch"], "test-method-expert")
        self.assertEqual(result["dispatchableRoles"], ["test-method-expert"])

    def test_two_distinct_roles_at_one_stage_are_both_reported(self):
        result = batch.aggregate([
            item("TM106", "STRATEGY", None, roles=["test-strategy-architect"]),
            item("TM108", "STRATEGY", None, roles=["rule-reviewer"]),
        ])
        self.assertEqual(result["state"], "STRATEGY")
        self.assertIsNone(result["dispatch"], "no single role is unique, so the singular field stays empty")
        self.assertEqual(result["dispatchableRoles"], ["rule-reviewer", "test-strategy-architect"])
        self.assertEqual(sorted(result["targetTms"]), ["TM106", "TM108"])

    def test_a_stage_that_names_no_role_at_all_is_blocked_with_a_reason(self):
        result = batch.aggregate([item("TM106", "STRATEGY")])
        self.assertEqual(result["state"], "BLOCKED")
        self.assertIn("无法确定唯一的处理角色", result["reason"])

    def test_a_non_source_stage_must_not_emit_an_auto_dispatch_list(self):
        # `captain_delivery_entry.advance_batch()` returns this dict straight to
        # the plugin hook, whose continuation path dispatches every entry in
        # `dispatches`. Emitting that key outside INPUT_SYNC would silently start
        # non-source specialists, which is a production behaviour change and not
        # part of P0-A.
        result = batch.aggregate([item("TM106", "STRATEGY", None, roles=["test-strategy-architect"])])
        self.assertNotIn("dispatches", result)


class SingleStageStateSource(unittest.TestCase):
    def test_stage_order_comes_from_the_registry_state_machine(self):
        order = single.stage_order()
        registry, error = single.load_stage_registry()
        self.assertIsNone(error)
        states = registry["stateMachine"]
        self.assertEqual([order[state] for state in states], list(range(len(states))))

    def test_the_correction_alias_ranks_with_the_stage_it_returns_to(self):
        order = single.stage_order()
        self.assertEqual(order["CORRECTION_STRATEGY"], order["STRATEGY"])
        self.assertEqual(single.canonical_stage("CORRECTION_STRATEGY"), "STRATEGY")
        self.assertEqual(single.canonical_stage("METHOD"), "METHOD")

    def test_stage_order_accepts_an_explicit_registry(self):
        fake = {"stateMachine": ["A", "B", "COMPLETE"], "stages": {"A": {}, "B": {}}}
        self.assertEqual(single.stage_order(fake), {"A": 0, "B": 1, "COMPLETE": 2})

    def test_only_one_module_declares_the_alias_and_none_declares_a_rank_table(self):
        alias_declared_in, order_declared_in = [], []
        for path in sorted(HERE.glob("*.py")):
            text = path.read_text(encoding="utf-8")
            if re.search(r"^\s*STAGE_ALIASES\s*=", text, re.M):
                alias_declared_in.append(path.name)
            if re.search(r"^\s*STAGE_ORDER\s*=", text, re.M):
                order_declared_in.append(path.name)
        self.assertEqual(alias_declared_in, ["ate_ptc_runner.py"],
                         "the correction alias must have exactly one declaration")
        self.assertEqual(order_declared_in, [],
                         "stage ranks must be derived from the registry, not restated as a table")


if __name__ == "__main__":
    unittest.main()
