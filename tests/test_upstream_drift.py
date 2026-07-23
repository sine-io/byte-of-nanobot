"""Offline regression tests for the upstream drift checker."""

from __future__ import annotations

import copy
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPOSITORY_ROOT / "scripts" / "check_upstream_drift.py"
BASELINE_PATH = REPOSITORY_ROOT / "scripts" / "upstream-baseline.json"

SPEC = importlib.util.spec_from_file_location("upstream_drift_checker", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load drift checker: {SCRIPT_PATH}")
DRIFT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = DRIFT
SPEC.loader.exec_module(DRIFT)

STABLE_SHA = "1" * 40
MAIN_SHA = "2" * 40
STABLE_PATH = "nanobot/agent/runner.py"
MAIN_PATH = "nanobot/agent/model_runtime.py"


def minimal_baseline() -> dict:
    return {
        "schema_version": 1,
        "upstream": {
            "stable": {
                "version": "v-test",
                "sha": STABLE_SHA,
                "audited_sources": [f"blob:{STABLE_PATH}"],
            },
            "main": {
                "version": "main@test",
                "sha": MAIN_SHA,
                "audited_sources": [f"blob:{MAIN_PATH}"],
            },
        },
        "key_modules": [
            {
                "id": "stable-runner",
                "revision": "stable",
                "kind": "blob",
                "path": STABLE_PATH,
            },
            {
                "id": "main-runtime",
                "revision": "main",
                "kind": "blob",
                "path": MAIN_PATH,
            },
        ],
        "command_assertions": {
            "required": [
                {
                    "id": "status",
                    "pattern": r"\bnanobot\s+status\b",
                    "minimum_occurrences": 1,
                }
            ],
            "forbidden": [
                {
                    "id": "agent-verbose",
                    "pattern": (
                        r"\bnanobot\s+agent\s+(?:--verbose|-v)"
                        r"(?=\s|[^A-Za-z0-9_-]|$)"
                    ),
                    "reason": "use the stable diagnostic command",
                },
                {
                    "id": "legacy-log-env",
                    "pattern": r"\bNANOBOT_LOG_LEVEL\b",
                    "reason": "use supported logging controls",
                }
            ],
        },
        "legacy_path_assertions": [
            {
                "id": "old-requirements",
                "pattern": r"\brequirements-docs\.txt\b",
                "reason": "use requirements.txt",
            }
        ],
        "tools_bootstrap_assertion": {
            "positive_patterns": [
                r"BOOTSTRAP_FILES\s*=\s*\[[^\]]*TOOLS\.md",
                r"(?:Bootstrap|启动配置文件)[^\n]{0,180}TOOLS\.md",
                r"TOOLS\.md[^\n]{0,120}自动加载",
            ],
            "negative_markers": ["不是", "不从", "误述"],
        },
    }


def valid_document(extra: str = "") -> str:
    return (
        "# Fixture\n\n"
        f"[stable](https://github.com/HKUDS/nanobot/blob/{STABLE_SHA}/{STABLE_PATH})\n"
        f"[main](https://github.com/HKUDS/nanobot/blob/{MAIN_SHA}/{MAIN_PATH})\n\n"
        "nanobot status\n\n"
        "TOOLS.md 不是自动加载的 Bootstrap 文件。\n"
        f"{extra}"
    )


def scan_fixture(text: str, baseline: dict | None = None):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        docs = root / "docs"
        docs.mkdir()
        (docs / "fixture.md").write_text(text, encoding="utf-8")
        return DRIFT.scan_repository(root, baseline or minimal_baseline())


class UpstreamDriftTests(unittest.TestCase):
    def test_repository_baseline_passes_without_network(self):
        baseline = DRIFT.load_baseline(BASELINE_PATH)

        result = DRIFT.scan_repository(REPOSITORY_ROOT, baseline)
        expected_sources = sum(
            len(entry["audited_sources"])
            for entry in baseline["upstream"].values()
        )

        self.assertTrue(result.ok, DRIFT.render_report(result))
        self.assertEqual(result.unique_source_references, expected_sources)
        self.assertGreaterEqual(result.source_references, 64)
        self.assertGreaterEqual(len(baseline["key_modules"]), 22)

    def test_report_records_baselines_counts_and_offline_boundary(self):
        result = scan_fixture(valid_document())

        report = DRIFT.render_report(result)

        self.assertTrue(result.ok)
        self.assertIn("**PASS**", report)
        self.assertIn(STABLE_SHA, report)
        self.assertIn(MAIN_SHA, report)
        self.assertIn("完全离线", report)
        self.assertIn("| status | 1 | 1 |", report)

    def test_unpinned_revision_is_rejected(self):
        text = valid_document().replace(
            f"blob/{STABLE_SHA}/{STABLE_PATH}",
            f"blob/main/{STABLE_PATH}",
        )

        result = scan_fixture(text)

        self.assertIn("source-unpinned", {finding.rule_id for finding in result.findings})

    def test_unreviewed_source_path_is_rejected(self):
        text = valid_document().replace(STABLE_PATH, "nanobot/agent/missing.py")

        result = scan_fixture(text)

        self.assertIn(
            "source-path-unreviewed",
            {finding.rule_id for finding in result.findings},
        )

    def test_required_forbidden_and_legacy_assertions_are_enforced(self):
        text = valid_document(
            "\nnanobot agent --verbose\nnanobot agent -v\n"
            "export NANOBOT_LOG_LEVEL=DEBUG\n"
            "python -m pip install -r requirements-docs.txt\n"
        ).replace("nanobot status", "status command removed")

        result = scan_fixture(text)
        messages = "\n".join(finding.message for finding in result.findings)

        self.assertIn("required-command-missing", {item.rule_id for item in result.findings})
        self.assertIn("forbidden-command", {item.rule_id for item in result.findings})
        self.assertIn("legacy-path", {item.rule_id for item in result.findings})
        self.assertIn("agent-verbose", messages)
        self.assertIn("legacy-log-env", messages)
        self.assertIn("old-requirements", messages)

    def test_every_recorded_legacy_path_pattern_detects_its_fixture(self):
        samples = {
            "legacy-requirements": "python -m pip install -r requirements-docs.txt",
            "legacy-hero-directory": "[Hero](build/README.md)",
            "legacy-appendix-path": "[help](appendix-troubleshooting.md)",
            "legacy-example-directory": "python examples/ch01-mini-agent.py",
            "legacy-history-file": "read HISTORY.md before the next turn",
        }
        recorded = DRIFT.load_baseline(BASELINE_PATH)["legacy_path_assertions"]
        self.assertEqual({rule["id"] for rule in recorded}, set(samples))

        for rule in recorded:
            with self.subTest(rule=rule["id"]):
                baseline = minimal_baseline()
                baseline["legacy_path_assertions"] = [copy.deepcopy(rule)]
                result = scan_fixture(
                    valid_document(f"\n{samples[rule['id']]}\n"),
                    baseline,
                )
                self.assertTrue(
                    any(rule["id"] in finding.message for finding in result.findings),
                    DRIFT.render_report(result),
                )

    def test_tools_bootstrap_claim_is_rejected_but_correction_is_allowed(self):
        positive = valid_document(
            "\nBootstrap 文件包括 AGENTS.md、SOUL.md、USER.md 和 TOOLS.md。\n"
        )
        code_positive = valid_document(
            '\nBOOTSTRAP_FILES = ["AGENTS.md", "SOUL.md", "TOOLS.md"]\n'
        )
        negative = valid_document(
            "\nTOOLS.md 不是自动加载的 Bootstrap 文件，这条误述不能回归。\n"
        )

        positive_result = scan_fixture(positive)
        code_positive_result = scan_fixture(code_positive)
        negative_result = scan_fixture(negative)

        self.assertIn(
            "tools-bootstrap-claim",
            {finding.rule_id for finding in positive_result.findings},
        )
        self.assertIn(
            "tools-bootstrap-claim",
            {finding.rule_id for finding in code_positive_result.findings},
        )
        self.assertTrue(negative_result.ok, DRIFT.render_report(negative_result))

    def test_malformed_sha_is_rejected_before_scanning(self):
        baseline = copy.deepcopy(minimal_baseline())
        baseline["upstream"]["main"]["sha"] = "b189a376"

        with self.assertRaises(DRIFT.BaselineError):
            DRIFT.validate_baseline(baseline)


if __name__ == "__main__":
    unittest.main()
