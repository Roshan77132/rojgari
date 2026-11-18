import re

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()

# "- item", "* item", "• item", "1. item", "1) item"
_BULLET = re.compile(r"^\s*(?:[-*\u2022]|\d+[.)])\s+(.*)$")


def _render_lines(lines):
    out, bullets, para = [], [], []

    def flush():
        if bullets:
            out.append("<ul>" + "".join("<li>%s</li>" % b for b in bullets) + "</ul>")
            bullets.clear()
        if para:
            out.append("<p>%s</p>" % "<br>".join(para))
            para.clear()

    for line in lines:
        m = _BULLET.match(line)
        if m:
            if para:
                flush()
            bullets.append(escape(m.group(1).strip()))
        else:
            if bullets:
                flush()
            para.append(escape(line))
    flush()
    return "".join(out)


@register.filter
def rich_text(value):
    """Plain text -> headings, paragraphs and bullet lists (HTML-escaped)."""
    if not value:
        return ""
    html = []
    for block in re.split(r"\n\s*\n", str(value).strip()):
        lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
        if not lines:
            continue
        first = lines[0]
        is_heading = (
            len(lines) > 1
            and len(first) <= 45
            and not _BULLET.match(first)
            and not first.endswith((".", ",", ";"))
        )
        if is_heading:
            html.append("<h3>%s</h3>" % escape(first.rstrip(":").strip()))
            lines = lines[1:]
        html.append(_render_lines(lines))
    return mark_safe("".join(html))