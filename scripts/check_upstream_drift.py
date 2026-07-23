#!/usr/bin/env python3
"""Validate the tutorial's pinned upstream baseline without network access."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SOURCE_URL_RE = re.compile(
    r"https://github\.com/HKUDS/nanobot/"
    r"(?P<kind>blob|tree)/(?P<revision>[^/\s)#?]+)"
    r"(?:/(?P<path>[A-Za-z0-9._/-]+))?"
)
FULL_SHA_RE = re.compile(r"[0-9a-f]{40}")
AUDITED_SOURCE_RE = re.compile(r"(?P<kind>blob|tree):(?P<path>.*)")
BASELINE_RELATIVE_PATH = Path("scripts/upstream-baseline.json")


class BaselineError(ValueError):
    """Raised when the machine-readable audit baseline is inconsistent."""


@dataclass(frozen=True, order=True)
class Finding:
    """One actionable drift finding."""

    rule_id: str
    path: str
    line: int
    message: str


@dataclass(frozen=True)
class Document:
    """One text document included in the published tutorial scan."""

    path: str
    text: str


@dataclass(frozen=True)
class ScanResult:
    """Deterministic result and counters used by both CLI and tests."""

    baseline: dict[str, Any]
    findings: tuple[Finding, ...]
    scanned_files: int
    source_references: int
    unique_source_references: int
    command_counts: dict[str, int]

    @property
    def ok(self) -> bool:
        return not self.findings


def load_baseline(path: Path) -> dict[str, Any]:
    """Load and validate one baseline JSON document."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BaselineError(f"cannot load baseline {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise BaselineError("baseline root must be a JSON object")
    validate_baseline(payload)
    return payload


def validate_baseline(baseline: dict[str, Any]) -> None:
    """Reject malformed SHAs, source inventories, modules, and regex rules."""

    if baseline.get("schema_version") != 1:
        raise BaselineError("schema_version must be 1")

    upstream = baseline.get("upstream")
    if not isinstance(upstream, dict) or set(upstream) != {"stable", "main"}:
        raise BaselineError("upstream must contain exactly stable and main")

    seen_shas: set[str] = set()
    audited_by_revision: dict[str, set[str]] = {}
    for revision, entry in upstream.items():
        if not isinstance(entry, dict):
            raise BaselineError(f"upstream.{revision} must be an object")
        version = entry.get("version")
        sha = entry.get("sha")
        sources = entry.get("audited_sources")
        if not isinstance(version, str) or not version.strip():
            raise BaselineError(f"upstream.{revision}.version must be non-empty")
        if not isinstance(sha, str) or FULL_SHA_RE.fullmatch(sha) is None:
            raise BaselineError(f"upstream.{revision}.sha must be a full lowercase SHA")
        if sha in seen_shas:
            raise BaselineError("stable and main SHAs must differ")
        seen_shas.add(sha)
        if not isinstance(sources, list) or not sources:
            raise BaselineError(f"upstream.{revision}.audited_sources must be non-empty")

        audited: set[str] = set()
        for source in sources:
            if not isinstance(source, str):
                raise BaselineError(f"upstream.{revision} source entries must be strings")
            match = AUDITED_SOURCE_RE.fullmatch(source)
            if match is None:
                raise BaselineError(f"invalid audited source: {source!r}")
            source_path = match.group("path")
            if source_path.startswith("/") or ".." in Path(source_path).parts:
                raise BaselineError(f"unsafe audited source path: {source!r}")
            if source in audited:
                raise BaselineError(f"duplicate audited source: {source!r}")
            audited.add(source)
        audited_by_revision[revision] = audited

    modules = baseline.get("key_modules")
    if not isinstance(modules, list) or not modules:
        raise BaselineError("key_modules must be a non-empty list")
    module_ids: set[str] = set()
    for module in modules:
        if not isinstance(module, dict):
            raise BaselineError("key_modules entries must be objects")
        module_id = module.get("id")
        revision = module.get("revision")
        kind = module.get("kind")
        path = module.get("path")
        if not isinstance(module_id, str) or not module_id:
            raise BaselineError("key module id must be non-empty")
        if module_id in module_ids:
            raise BaselineError(f"duplicate key module id: {module_id}")
        module_ids.add(module_id)
        if revision not in upstream or kind not in {"blob", "tree"} or not isinstance(path, str):
            raise BaselineError(f"invalid key module: {module_id}")
        if f"{kind}:{path}" not in audited_by_revision[revision]:
            raise BaselineError(f"key module is not in audited_sources: {module_id}")

    command_assertions = baseline.get("command_assertions")
    if not isinstance(command_assertions, dict):
        raise BaselineError("command_assertions must be an object")
    required = command_assertions.get("required")
    forbidden = command_assertions.get("forbidden")
    if not isinstance(required, list) or not required:
        raise BaselineError("command_assertions.required must be non-empty")
    if not isinstance(forbidden, list) or not forbidden:
        raise BaselineError("command_assertions.forbidden must be non-empty")

    for rule in required:
        _validate_regex_rule(rule, "required command")
        minimum = rule.get("minimum_occurrences")
        if not isinstance(minimum, int) or isinstance(minimum, bool) or minimum < 1:
            raise BaselineError(f"required command {rule.get('id')} has invalid minimum")
    for rule in forbidden:
        _validate_regex_rule(rule, "forbidden command", require_reason=True)

    legacy_rules = baseline.get("legacy_path_assertions")
    if not isinstance(legacy_rules, list) or not legacy_rules:
        raise BaselineError("legacy_path_assertions must be non-empty")
    for rule in legacy_rules:
        _validate_regex_rule(rule, "legacy path", require_reason=True)

    tools_rule = baseline.get("tools_bootstrap_assertion")
    if not isinstance(tools_rule, dict):
        raise BaselineError("tools_bootstrap_assertion must be an object")
    patterns = tools_rule.get("positive_patterns")
    markers = tools_rule.get("negative_markers")
    if not isinstance(patterns, list) or not patterns:
        raise BaselineError("TOOLS Bootstrap positive_patterns must be non-empty")
    if not isinstance(markers, list) or not markers or not all(
        isinstance(marker, str) and marker for marker in markers
    ):
        raise BaselineError("TOOLS Bootstrap negative_markers must be non-empty strings")
    for pattern in patterns:
        if not isinstance(pattern, str):
            raise BaselineError("TOOLS Bootstrap patterns must be strings")
        _compile_pattern(pattern, "TOOLS Bootstrap")


def _validate_regex_rule(
    rule: Any,
    category: str,
    *,
    require_reason: bool = False,
) -> None:
    if not isinstance(rule, dict):
        raise BaselineError(f"{category} rules must be objects")
    rule_id = rule.get("id")
    pattern = rule.get("pattern")
    if not isinstance(rule_id, str) or not rule_id:
        raise BaselineError(f"{category} rule id must be non-empty")
    if not isinstance(pattern, str) or not pattern:
        raise BaselineError(f"{category} pattern must be non-empty: {rule_id}")
    if require_reason and (not isinstance(rule.get("reason"), str) or not rule["reason"]):
        raise BaselineError(f"{category} reason must be non-empty: {rule_id}")
    _compile_pattern(pattern, rule_id)


def _compile_pattern(pattern: str, rule_id: str, *, ignore_case: bool = False) -> re.Pattern[str]:
    flags = re.IGNORECASE if ignore_case else 0
    try:
        return re.compile(pattern, flags)
    except re.error as exc:
        raise BaselineError(f"invalid regex for {rule_id}: {exc}") from exc


def collect_documents(root: Path) -> tuple[Document, ...]:
    """Read only published docs and contributor-facing root files."""

    paths: set[Path] = set()
    for relative in ("README.md", "CONTRIBUTING.md", "mkdocs.yml"):
        candidate = root / relative
        if candidate.is_file():
            paths.add(candidate)

    docs_root = root / "docs"
    if docs_root.is_dir():
        for candidate in docs_root.rglob("*.md"):
            relative = candidate.relative_to(root)
            if relative.parts[:2] == ("docs", "superpowers"):
                continue
            paths.add(candidate)

    documents: list[Document] = []
    for path in sorted(paths, key=lambda item: item.relative_to(root).as_posix()):
        documents.append(
            Document(
                path=path.relative_to(root).as_posix(),
                text=path.read_text(encoding="utf-8"),
            )
        )
    return tuple(documents)


def scan_repository(root: Path, baseline: dict[str, Any]) -> ScanResult:
    """Scan pinned links and regression assertions using only local files."""

    validate_baseline(baseline)
    documents = collect_documents(root)
    findings: list[Finding] = []
    upstream = baseline["upstream"]
    revision_by_sha = {
        entry["sha"]: revision for revision, entry in upstream.items()
    }
    audited_by_revision = {
        revision: set(entry["audited_sources"])
        for revision, entry in upstream.items()
    }

    seen_sources: set[tuple[str, str, str]] = set()
    source_references = 0
    for document in documents:
        for match in SOURCE_URL_RE.finditer(document.text):
            source_references += 1
            kind = match.group("kind")
            sha = match.group("revision")
            source_path = match.group("path") or ""
            revision = revision_by_sha.get(sha)
            line = _line_number(document.text, match.start())
            if revision is None:
                findings.append(
                    Finding(
                        "source-unpinned",
                        document.path,
                        line,
                        f"nanobot source URL must use an audited full SHA, found {sha!r}",
                    )
                )
                continue
            source_key = f"{kind}:{source_path}"
            if source_key not in audited_by_revision[revision]:
                findings.append(
                    Finding(
                        "source-path-unreviewed",
                        document.path,
                        line,
                        f"{revision} source target is not in the audited inventory: {source_key}",
                    )
                )
                continue
            seen_sources.add((revision, kind, source_path))

    for module in baseline["key_modules"]:
        key = (module["revision"], module["kind"], module["path"])
        if key not in seen_sources:
            findings.append(
                Finding(
                    "key-module-reference-missing",
                    BASELINE_RELATIVE_PATH.as_posix(),
                    1,
                    f"required source reference is missing: {module['id']}",
                )
            )

    command_counts: dict[str, int] = {}
    for rule in baseline["command_assertions"]["required"]:
        pattern = _compile_pattern(rule["pattern"], rule["id"])
        count = sum(
            1
            for document in documents
            for _match in pattern.finditer(document.text)
        )
        command_counts[rule["id"]] = count
        minimum = rule["minimum_occurrences"]
        if count < minimum:
            findings.append(
                Finding(
                    "required-command-missing",
                    BASELINE_RELATIVE_PATH.as_posix(),
                    1,
                    f"{rule['id']} appears {count} time(s), expected at least {minimum}",
                )
            )

    _scan_forbidden_rules(
        documents,
        baseline["command_assertions"]["forbidden"],
        "forbidden-command",
        findings,
    )
    _scan_forbidden_rules(
        documents,
        baseline["legacy_path_assertions"],
        "legacy-path",
        findings,
    )
    _scan_tools_bootstrap(documents, baseline["tools_bootstrap_assertion"], findings)

    return ScanResult(
        baseline=baseline,
        findings=tuple(sorted(set(findings))),
        scanned_files=len(documents),
        source_references=source_references,
        unique_source_references=len(seen_sources),
        command_counts=command_counts,
    )


def _scan_forbidden_rules(
    documents: tuple[Document, ...],
    rules: list[dict[str, Any]],
    category: str,
    findings: list[Finding],
) -> None:
    for rule in rules:
        pattern = _compile_pattern(rule["pattern"], rule["id"])
        for document in documents:
            for match in pattern.finditer(document.text):
                findings.append(
                    Finding(
                        category,
                        document.path,
                        _line_number(document.text, match.start()),
                        f"{rule['id']}: {rule['reason']}",
                    )
                )


def _scan_tools_bootstrap(
    documents: tuple[Document, ...],
    rule: dict[str, Any],
    findings: list[Finding],
) -> None:
    markers = tuple(rule["negative_markers"])
    reported: set[tuple[str, int]] = set()
    patterns = [
        _compile_pattern(pattern, "tools-bootstrap", ignore_case=True)
        for pattern in rule["positive_patterns"]
    ]
    for document in documents:
        for pattern in patterns:
            for match in pattern.finditer(document.text):
                line = _line_number(document.text, match.start())
                line_text = _line_text(document.text, match.start())
                if any(marker in line_text for marker in markers):
                    continue
                location = (document.path, line)
                if location in reported:
                    continue
                reported.add(location)
                findings.append(
                    Finding(
                        "tools-bootstrap-claim",
                        document.path,
                        line,
                        "TOOLS.md must not be described as an automatic Bootstrap file",
                    )
                )


def _line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _line_text(text: str, offset: int) -> str:
    start = text.rfind("\n", 0, offset) + 1
    end = text.find("\n", offset)
    return text[start:] if end == -1 else text[start:end]


def render_report(result: ScanResult) -> str:
    """Render a deterministic Markdown report suitable for CI logs."""

    stable = result.baseline["upstream"]["stable"]
    main = result.baseline["upstream"]["main"]
    status = "PASS" if result.ok else "FAIL"
    required_rules = result.baseline["command_assertions"]["required"]
    lines = [
        "# nanobot 上游漂移检查报告",
        "",
        f"- 结果：**{status}**",
        "- 执行模式：完全离线（0 次网络、模型或 Channel 调用）",
        f"- 稳定版：{stable['version']} @ {stable['sha']}",
        f"- main 对照：{main['version']} @ {main['sha']}",
        f"- 扫描文件：{result.scanned_files}",
        f"- 固定源码链接：{result.source_references} 处，"
        f"{result.unique_source_references} 个已审计目标",
        f"- 关键模块断言：{len(result.baseline['key_modules'])}",
        f"- 禁用命令断言：{len(result.baseline['command_assertions']['forbidden'])}",
        f"- 旧路径断言：{len(result.baseline['legacy_path_assertions'])}",
        f"- 发现项：{len(result.findings)}",
        "",
        "## 命令断言",
        "",
        "| 断言 | 实际 | 最低要求 |",
        "|---|---:|---:|",
    ]
    for rule in required_rules:
        lines.append(
            f"| {rule['id']} | {result.command_counts[rule['id']]} | "
            f"{rule['minimum_occurrences']} |"
        )

    lines.extend(["", "## 发现", ""])
    if not result.findings:
        lines.append("- 未发现上游基线漂移或已修复模式回归。")
    else:
        lines.extend(
            [
                "| 规则 | 位置 | 说明 |",
                "|---|---|---|",
            ]
        )
        for finding in result.findings:
            location = f"{finding.path}:{finding.line}" if finding.line else finding.path
            message = finding.message.replace("|", "\\|")
            lines.append(f"| {finding.rule_id} | {location} | {message} |")
    return "\n".join(lines) + "\n"


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check nanobot tutorial upstream drift without network access."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root (default: inferred from this script)",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        help="baseline JSON path (default: <root>/scripts/upstream-baseline.json)",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="print a Markdown maintenance report",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    root = args.root.resolve()
    baseline_path = (
        args.baseline.resolve()
        if args.baseline is not None
        else root / BASELINE_RELATIVE_PATH
    )
    try:
        baseline = load_baseline(baseline_path)
        result = scan_repository(root, baseline)
    except (BaselineError, OSError, UnicodeError) as exc:
        print(f"upstream drift check: ERROR: {exc}", file=sys.stderr)
        return 2

    if args.report:
        print(render_report(result), end="")
    elif result.ok:
        print(
            "upstream drift check: PASS "
            f"({result.scanned_files} files, {result.source_references} source links)"
        )
    else:
        print(render_report(result), end="", file=sys.stderr)
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
