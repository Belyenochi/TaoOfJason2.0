#!/usr/bin/env python3
"""Compare a regenerated Hexo site against the original generated site, post by
post. This is the evidence that the recovered Markdown is faithful: not "the
converter ran without errors" but "rendering the recovered sources back through
Hexo + NexT produces the same article body".

Usage: verify.py <original_public_dir> <regenerated_public_dir>

Three measures per post:
  ratio      difflib similarity of the visible body text (gutter line numbers
             and read-more buttons removed, whitespace collapsed)
  nospace    whether the text is identical once all spaces are removed --
             the remaining differences are spaces around inline elements,
             which Markdown cannot always reproduce and which do not render
  struct     count of each structural tag; <p> is excluded because bare text
             nodes in the original become paragraphs in Markdown and that is
             not a content difference
"""
import difflib
import html
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

TAGS = ["h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li", "table", "img", "a",
        "figure.highlight", "pre", "code", "strong", "em", "blockquote"]


def body(p):
    return BeautifulSoup(Path(p).read_text(encoding="utf-8"), "lxml").select_one(".post-body")


def text_of(el):
    for b in el.select("a.btn"):
        b.decompose()
    for g in el.select("td.gutter"):
        g.decompose()
    return re.sub(r"\s+", " ", html.unescape(el.get_text(" "))).strip()


def struct(el):
    return {k: len(el.select(k)) for k in TAGS}


def main(orig, new):
    orig, new = Path(orig), Path(new)
    rows, bad_struct = [], []
    for page in sorted(new.glob("[0-9]*/[0-9]*/[0-9]*/*/index.html")):
        rel = page.parent.relative_to(new)
        old = orig / rel / "index.html"
        if not old.exists():
            rows.append((str(rel), None, False, "not in original"))
            continue
        eo, en = body(old), body(page)
        if eo is None or en is None:
            rows.append((str(rel), None, False, "no .post-body"))
            continue
        a, b = text_of(eo), text_of(en)
        r = difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()
        rows.append((str(rel), r, a.replace(" ", "") == b.replace(" ", ""), ""))
        sa, sb = struct(eo), struct(en)
        d = {k: (sa[k], sb[k]) for k in sa if sa[k] != sb[k]}
        if d:
            bad_struct.append((str(rel), d))

    scored = [r for r in rows if r[1] is not None]
    print(f"{'post':<44} {'ratio':>7}  nospace")
    for rel, r, same, note in sorted(rows, key=lambda x: (x[1] is None, x[1] or 0)):
        print(f"{rel:<44} {('%.4f' % r) if r is not None else '   -   ':>7}  {'yes' if same else 'NO '}  {note}")
    print()
    print(f"posts compared     : {len(scored)}")
    print(f"text identical     : {sum(1 for r in scored if r[1] == 1.0)}")
    print(f"identical no-space : {sum(1 for r in scored if r[2])}")
    print(f"mean ratio         : {sum(r[1] for r in scored) / max(1, len(scored)):.4f}")
    print(f"structure diffs    : {len(bad_struct)}")
    for rel, d in bad_struct:
        print(f"  {rel}: {d}")
    return 0 if all(r[2] for r in scored) and not bad_struct else 1


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1], sys.argv[2]))
