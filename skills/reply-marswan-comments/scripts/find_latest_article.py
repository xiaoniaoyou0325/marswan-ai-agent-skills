#!/usr/bin/env python3
"""Locate the newest published WeChat Markdown article."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


DEFAULT_OUTPUT = Path("E:/公众号：火星来信Marswan/output")
TITLE_PATTERN = re.compile(r"^title:\s*(.+?)\s*$", re.MULTILINE)


def normalize_root(raw_root: str | None) -> Path:
    if raw_root:
        root = Path(raw_root).expanduser()
    else:
        cwd_output = Path.cwd() / "output"
        root = cwd_output if cwd_output.is_dir() else DEFAULT_OUTPUT
    nested_output = root / "output"
    return nested_output if nested_output.is_dir() else root


def is_published_wechat_draft(path: Path) -> bool:
    name = path.name
    included = "公众号" in name and ("发布稿" in name or "终稿" in name)
    excluded = any(word in name for word in ("初稿", "质检", "发布配置", "截图指南"))
    return included and not excluded


def read_title(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""
    match = TITLE_PATTERN.search(text[:4000])
    return match.group(1).strip().strip("\"'") if match else ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", help="Project root or output directory")
    args = parser.parse_args()

    root = normalize_root(args.root)
    if not root.is_dir():
        print(json.dumps({"found": False, "root": str(root)}, ensure_ascii=False))
        return 1

    candidates = [path for path in root.rglob("*.md") if is_published_wechat_draft(path)]
    if not candidates:
        print(json.dumps({"found": False, "root": str(root)}, ensure_ascii=False))
        return 1

    latest = max(candidates, key=lambda path: path.stat().st_mtime)
    result = {
        "found": True,
        "path": str(latest.resolve()),
        "title": read_title(latest),
        "modified_at": latest.stat().st_mtime,
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
