"""Teaching snapshot for build/05-skills-and-beyond.md."""

from __future__ import annotations

import re
import sys
from pathlib import Path


class SkillsLoader:
    def __init__(self, workspace: Path, builtin_dir: Path | None = None):
        self.workspace_skills = workspace / "skills"
        self.builtin_skills = builtin_dir

    def list_skills(self) -> list[dict]:
        skills = []
        if self.workspace_skills.exists():
            for directory in self.workspace_skills.iterdir():
                skill_file = directory / "SKILL.md"
                if directory.is_dir() and skill_file.exists():
                    skills.append(
                        {
                            "name": directory.name,
                            "path": str(skill_file),
                            "description": self._get_description(skill_file),
                        }
                    )
        if self.builtin_skills and self.builtin_skills.exists():
            existing = {skill["name"] for skill in skills}
            for directory in self.builtin_skills.iterdir():
                skill_file = directory / "SKILL.md"
                if directory.is_dir() and skill_file.exists() and directory.name not in existing:
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


def main():
    workspace = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else Path("~/.mini-agent/workspace").expanduser()
    loader = SkillsLoader(workspace)
    summary = loader.build_skills_summary()
    if summary:
        print(summary)
    else:
        print(f"No skills found under {workspace / 'skills'}")


if __name__ == "__main__":
    main()
