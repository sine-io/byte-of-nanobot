"""Teaching snapshot for hero/05-skills-and-beyond.md."""

from __future__ import annotations

import os
import re
import sys
import tempfile
from pathlib import Path

_temporary_workspace = None


def select_workspace() -> Path:
    """Use an explicit teaching directory or create a private temporary one."""
    global _temporary_workspace
    configured = os.environ.get("NANOBOT_HERO_WORKSPACE")
    if configured:
        return Path(configured).expanduser().resolve()
    _temporary_workspace = tempfile.TemporaryDirectory(prefix="nanobot-hero-")
    return Path(_temporary_workspace.name).resolve()


DEFAULT_WORKSPACE = select_workspace()


class SkillsLoader:
    def __init__(self, workspace: Path, builtin_dir: Path | None = None):
        self.workspace = workspace.resolve()
        self.workspace_skills = self.workspace / "skills"
        self.builtin_skills = builtin_dir.resolve() if builtin_dir else None

    @staticmethod
    def _safe_skill_file(root: Path, directory: Path) -> Path | None:
        """Reject SKILL.md symlinks that escape their declared skill root."""
        skill_file = (directory / "SKILL.md").resolve(strict=False)
        if skill_file != root and root not in skill_file.parents:
            return None
        return skill_file if directory.is_dir() and skill_file.is_file() else None

    def list_skills(self) -> list[dict]:
        skills = []
        workspace_skills = self.workspace_skills.resolve(strict=False)
        workspace_skills_is_safe = (
            workspace_skills == self.workspace or self.workspace in workspace_skills.parents
        )
        if workspace_skills_is_safe and workspace_skills.exists():
            for directory in sorted(workspace_skills.iterdir()):
                skill_file = self._safe_skill_file(workspace_skills, directory)
                if skill_file:
                    skills.append(
                        {
                            "name": directory.name,
                            "path": str(skill_file),
                            "description": self._get_description(skill_file),
                        }
                    )
        if self.builtin_skills and self.builtin_skills.exists():
            existing = {skill["name"] for skill in skills}
            for directory in sorted(self.builtin_skills.iterdir()):
                skill_file = self._safe_skill_file(self.builtin_skills, directory)
                if skill_file and directory.name not in existing:
                    skills.append(
                        {
                            "name": directory.name,
                            "path": str(skill_file),
                            "description": self._get_description(skill_file),
                        }
                    )
        return skills

    def build_skills_summary(self) -> str:
        skills = self.list_skills()
        if not skills:
            return ""
        lines = ["<skills>"]
        for skill in skills:
            lines.append("  <skill>")
            lines.append(f"    <name>{skill['name']}</name>")
            lines.append(f"    <description>{skill['description']}</description>")
            lines.append(f"    <location>{skill['path']}</location>")
            lines.append("  </skill>")
        lines.append("</skills>")
        return "\n".join(lines)

    def _get_description(self, path: Path) -> str:
        content = path.read_text(encoding="utf-8")
        if content.startswith("---"):
            match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
            if match:
                for line in match.group(1).split("\n"):
                    if line.startswith("description:"):
                        return line.split(":", 1)[1].strip().strip("\"'")
        return path.parent.name


def print_safety_warning(explicit_workspace: bool) -> None:
    scope = "你显式指定的目录" if explicit_workspace else "系统临时教学目录"
    print(
        f"[安全提示] 这是教学加载器，不是生产沙箱；它只读取{scope}下的 SKILL.md，"
        "但没有提供完整的依赖验证或执行隔离。"
    )


def main():
    argument_workspace = len(sys.argv) > 1
    explicit_workspace = argument_workspace or bool(os.environ.get("NANOBOT_HERO_WORKSPACE"))
    workspace = Path(sys.argv[1]).expanduser().resolve() if argument_workspace else DEFAULT_WORKSPACE
    print_safety_warning(explicit_workspace)
    loader = SkillsLoader(workspace)
    summary = loader.build_skills_summary()
    if summary:
        print(summary)
    else:
        print(f"No skills found under {workspace / 'skills'}")


if __name__ == "__main__":
    main()
