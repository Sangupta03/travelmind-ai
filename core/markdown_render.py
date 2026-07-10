"""
Renders LLM-generated markdown (the AI reasoning text) to HTML for display.

Gemini's markdown output doesn't reliably include a blank line before a
list starts (e.g. "Header:\n* item"), but the `markdown` library requires
one to recognize a list at all — without this fix, list markers show up
as literal "*" characters in a single unbroken paragraph instead of a
rendered list.
"""
import re

import markdown as _markdown

_LIST_ITEM_RE = re.compile(r"^\s*([*\-+]|\d+\.)\s+")


def _ensure_blank_line_before_lists(text: str) -> str:
    lines = text.split("\n")
    fixed = []
    for line in lines:
        if _LIST_ITEM_RE.match(line):
            prev = fixed[-1] if fixed else ""
            if prev.strip() != "" and not _LIST_ITEM_RE.match(prev):
                fixed.append("")
        fixed.append(line)
    return "\n".join(fixed)


def render_ai_reasoning(text: str) -> str:
    if not text:
        return ""
    prepared = _ensure_blank_line_before_lists(text)
    return _markdown.markdown(prepared, extensions=["extra", "sane_lists"])
