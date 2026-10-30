"""Master catalog integrity only; these are not 62 completed features."""
import csv
from pathlib import Path
from collections import Counter


def test_menu_and_action_inventory_has_no_false_release_claims():
    source = Path(__file__).resolve().parents[2] / "docs/UX/action-registry.csv"
    with source.open(newline="", encoding="utf-8") as stream:
        actions = list(csv.DictReader(stream))
    assert len(actions) == 414
    assert len({action["action_id"] for action in actions}) == 414
    groups = Counter(action["submenu"][0] for action in actions)
    assert set(groups) == set("ABCDEFGHIJ")
    menus = {action["submenu"] for action in actions}
    assert len(menus) == 62
    assert all(
        "PRODUCTION" not in action["status"]
        and "DONE" not in action["status"]
        for action in actions
    )
    partial = {action["action_id"] for action in actions
               if "POC_GENERIC_TASK_ONLY" in action["status"]}
    assert partial == {"A2-01", "A2-02", "A2-03"}
