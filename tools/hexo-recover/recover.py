#!/usr/bin/env python3
"""Rebuild a Hexo (NexT theme) source tree from the generated site in .deploy_git.

Why this exists: the markdown sources of belyenochi.github.io were lost; the only
complete record is the generated HTML, 77 deploys of it, in the .deploy_git that
the 2022-03-08 backup happened to include. Generic HTML->Markdown converters
mangle exactly the parts that matter here -- NexT renders code as a
<table> with a line-number gutter, and headings carry an anchor <a> -- so the
conversion is written against NexT's actual markup rather than HTML in general.

Input : a .deploy_git checkout (or any Hexo `public/` folder)
Output: a Hexo project skeleton: _config.yml, source/_posts/*.md, source/images,
        source/about/index.md, themes/next/_config.yml, plus _private/ for posts
        that must not go back online without a human decision.

Usage: recover.py <deploy_git_dir> <out_dir>
"""
import html
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag

# Posts that exist in the generated site but must NOT be republished silently.
# Each entry says why, because the reason is the decision, not the slug.
PRIVATE = {
    "2021/05/19/love": "the author deleted this from the live site by hand on 2025-04-07",
    "2021/08/29/8.22": "a work weekly report, not a blog post",
    "2021/08/31/中间件平台开发流程规范": "empty body (2 characters); a stray draft",
    "2021/08/27/2021-目标": "the author asked for it to come down (2026-09-03)",
}

POST_DIR = re.compile(r"^\d{4}/\d{2}/\d{2}/[^/]+$")


# --------------------------------------------------------------------------- #
# HTML -> Markdown, written for NexT's markup
# --------------------------------------------------------------------------- #
class Converter:
    """Depth-first walk producing Markdown. Block elements return text that
    already ends with the right number of newlines; inline elements return
    text with no trailing newline. Keeping that contract is what stops the
    output from growing stray blank lines."""

    def __init__(self):
        self.warnings = []

    # -- entry -------------------------------------------------------------
    def convert(self, node) -> str:
        out = "".join(self.block(c) for c in node.children)
        out = re.sub(r"\n{3,}", "\n\n", out)
        return out.strip() + "\n"

    # -- blocks ------------------------------------------------------------
    def block(self, n) -> str:
        if isinstance(n, NavigableString):
            # Bare text at block level: hexo-renderer-marked emits this when a
            # heading is followed by text without a blank line in the source.
            # It is a paragraph in every sense but the tag, so close it as one;
            # otherwise it glues onto the previous heading in the output.
            t = self.guard_line_start(self.text(n).strip())
            return t + "\n\n" if t else ""
        if not isinstance(n, Tag):
            return ""
        name = n.name
        if name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(name[1])
            return "#" * level + " " + self.inline_children(n).strip() + "\n\n"
        if name == "p":
            body = self.guard_line_start(self.inline_children(n).strip())
            return body + "\n\n" if body else ""
        if name == "figure" and "highlight" in n.get("class", []):
            return self.code_figure(n)
        if name == "pre":
            # A bare <pre><code> with no highlight figure around it is what
            # marked emits for an INDENTED code block; Hexo only runs the
            # highlighter on fenced ones. Re-emit it indented so the re-render
            # is a bare <pre> too, not a highlight table.
            code = html.unescape(n.get_text()).rstrip("\n")
            return "\n".join("    " + ln if ln else "" for ln in code.split("\n")) + "\n\n"
        if name in ("ul", "ol"):
            return self.list(n, ordered=(name == "ol"), depth=0) + "\n"
        if name == "blockquote":
            inner = "".join(self.block(c) for c in n.children).strip()
            return "\n".join("> " + ln if ln else ">" for ln in inner.split("\n")) + "\n\n"
        if name == "table":
            return self.table(n)
        if name == "hr":
            return "---\n\n"
        if name == "div":
            # NexT wraps nothing meaningful in divs inside post-body except the
            # table container; recurse transparently.
            return "".join(self.block(c) for c in n.children)
        if name in ("img",):
            return self.img(n) + "\n\n"
        if name == "br":
            return "\n"
        if name in ("script", "style"):
            return ""
        # Inline element at block level (NexT sometimes emits bare <strong>):
        t = self.inline(n).strip()
        return t + "\n\n" if t else ""

    def code_figure(self, fig) -> str:
        lang = ""
        for c in fig.get("class", []):
            if c != "highlight":
                lang = c
        if lang == "plain":
            lang = ""
        caption = fig.find("figcaption")
        cap = caption.get_text(" ", strip=True) if caption else ""
        code_td = fig.select_one("td.code")
        if code_td is None:
            # Old NexT / no gutter: a single <pre>
            pre = fig.find("pre")
            code = pre.get_text() if pre else fig.get_text()
        else:
            lines = code_td.select("span.line")
            if lines:
                code = "\n".join(self.raw_text(ln) for ln in lines)
            else:
                code = code_td.get_text()
        code = code.rstrip("\n")
        fence = "```"
        while fence in code:
            fence += "`"
        head = fence + lang
        if cap:
            head += " " + cap
        return f"{head}\n{code}\n{fence}\n\n"

    def raw_text(self, node) -> str:
        # Code must not be Markdown-escaped; only entity-decoded.
        return html.unescape(node.get_text())

    def list(self, lst, ordered, depth) -> str:
        """Each <li> becomes one or more lines. Inline runs are joined into the
        first line; block children (headings, nested lists, code, paragraphs
        after the first) go on their own lines, indented under the marker, so
        marked re-parses them as blocks inside the item. biji-os-01 has twenty
        <li><h5> -- a heading glued onto the item text on one line is just text
        with hashes in it, which is what the first version of this produced."""
        out = []
        i = 0
        for li in lst.find_all("li", recursive=False):
            i += 1
            marker = f"{i}. " if ordered else "- "
            pad = " " * len(marker)
            blocks = []          # list of markdown chunks, in order
            inline_run = []
            def flush():
                s = " ".join(x.strip() for x in inline_run if x.strip())
                if s:
                    blocks.append(s)
                inline_run.clear()
            for c in li.children:
                if isinstance(c, Tag) and c.name in ("ul", "ol"):
                    flush()
                    blocks.append(self.list(c, ordered=(c.name == "ol"), depth=0).rstrip("\n"))
                elif isinstance(c, Tag) and c.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
                    flush()
                    blocks.append("#" * int(c.name[1]) + " " + self.inline_children(c).strip())
                elif isinstance(c, Tag) and c.name == "figure":
                    flush()
                    blocks.append(self.code_figure(c).rstrip("\n"))
                elif isinstance(c, Tag) and c.name in ("pre",):
                    flush()
                    blocks.append(self.block(c).rstrip("\n"))
                elif isinstance(c, Tag) and c.name in ("p", "div"):
                    flush()
                    blocks.append(self.inline_children(c).strip())
                elif isinstance(c, Tag) and c.name == "br":
                    inline_run.append("  \n")
                else:
                    inline_run.append(self.inline(c) if isinstance(c, Tag) else self.text(c))
            flush()
            if not blocks:
                blocks = [""]
            first, rest = blocks[0], blocks[1:]
            # A <br> inside the item yields "  \n"; the continuation must be
            # indented under the marker or it ends the list -- jsys_06 came out
            # as five one-item lists instead of one four-item list.
            first_lines = first.split("\n")
            lines = [marker + first_lines[0]] + [pad + ln if ln.strip() else "" for ln in first_lines[1:]]
            for b in rest:
                lines.extend(pad + ln if ln else "" for ln in b.split("\n"))
            out.append("\n".join(lines))
        body = "\n".join(out)
        return self.indent(body, depth) + "\n" if depth else body + "\n"

    def indent(self, s, depth) -> str:
        pad = "  " * depth
        return "\n".join(pad + ln if ln else ln for ln in s.split("\n"))

    def table(self, t) -> str:
        rows = []
        for tr in t.find_all("tr"):
            cells = [self.inline_children(td).strip().replace("|", "\\|").replace("\n", " ")
                     for td in tr.find_all(["th", "td"])]
            rows.append(cells)
        if not rows:
            return ""
        width = max(len(r) for r in rows)
        rows = [r + [""] * (width - len(r)) for r in rows]
        head, body = rows[0], rows[1:]
        lines = ["| " + " | ".join(head) + " |", "|" + "---|" * width]
        lines += ["| " + " | ".join(r) + " |" for r in body]
        return "\n".join(lines) + "\n\n"

    # -- inline ------------------------------------------------------------
    def inline_children(self, n) -> str:
        return "".join(self.inline(c) if isinstance(c, Tag) else self.text(c) for c in n.children)

    def inline(self, n) -> str:
        name = n.name
        cls = n.get("class", [])
        if name == "a":
            if "headerlink" in cls:          # NexT heading anchor: drop it
                return ""
            href = n.get("href", "")
            txt = self.inline_children(n)
            if not txt.strip():
                return ""
            if href.startswith("/tags/") or href.startswith("/categories/"):
                return txt
            return f"[{txt}]({href})"
        if name == "img":
            return self.img(n)
        if name in ("strong", "b"):
            return self.emphasis(n, "**", "strong")
        if name in ("em", "i"):
            if any(c.startswith("fa") for c in cls):  # icon fonts
                return ""
            return self.emphasis(n, "*", "em")
        if name in ("del", "s"):
            return "~~" + self.inline_children(n).strip() + "~~"
        if name == "code":
            t = html.unescape(n.get_text())
            fence = "`" * (max([len(m) for m in re.findall(r"`+", t)] + [0]) + 1)
            return f"{fence}{t}{fence}"
        if name == "br":
            return "  \n"
        if name == "span" and "line" in cls:
            return self.raw_text(n)
        if name in ("sup", "sub", "kbd", "mark"):
            return f"<{name}>{self.inline_children(n)}</{name}>"
        if name in ("figure", "pre", "ul", "ol", "table", "blockquote", "div", "p"):
            # block inside inline context (e.g. inside <li>) -- caller handles
            return self.block(n)
        return self.inline_children(n)

    _PUNCT_START = re.compile(r"^[\\\[\](){}<>\"'!?.,:;#*_~`|-]")

    def emphasis(self, n, marks: str, tag: str) -> str:
        """`**text**` -- unless the text begins with punctuation and the run is
        glued to a word on the left, e.g. 为何物**[本篇]**. CommonMark then says
        the opening `**` is not left-flanking and refuses to open emphasis;
        the old marked did not care, the current one follows the spec and
        printed the asterisks literally in parser_00. An HTML tag says the
        same thing in both and keeps the text byte-identical."""
        inner = self.inline_children(n).strip()
        if not inner:
            return ""
        prev = n.previous_sibling
        glued_left = isinstance(prev, NavigableString) and str(prev)[-1:].strip() != "" \
            and not self._PUNCT_START.match(str(prev)[-1:])
        if glued_left and self._PUNCT_START.match(inner):
            return f"<{tag}>{inner}</{tag}>"
        return f"{marks}{inner}{marks}"

    def img(self, n) -> str:
        src = n.get("data-src") or n.get("src", "")
        # Three of the originals have spaces in the file name
        # (/images/jsys_05/stored program.jpg). A bare space ends the URL in
        # Markdown and the image renders as literal text.
        src = src.replace(" ", "%20")
        alt = n.get("alt", "") or n.get("title", "")
        return f"![{alt}]({src})"

    # Characters that are literal in the rendered HTML but would be markup in
    # Markdown. Everything else stays as-is: over-escaping makes the source
    # unpleasant to edit, which is the whole point of recovering it.
    # No `~` here: the marked that hexo-renderer-marked 1.x ships does not treat
    # `\~` as an escape and prints the backslash. A single `~` is inert anyway.
    _INLINE_ESC = re.compile(r"([*_`\\\[\]])")
    _LINE_START_ESC = re.compile(r"^(\s*)(#{1,6}|[>+-]|\d+\.)(\s)", re.M)

    def text(self, s) -> str:
        t = html.unescape(str(s))
        t = re.sub(r"[ \t\r\f\v]+", " ", t)
        t = t.replace("\n", " ")
        t = self._INLINE_ESC.sub(r"\\\1", t)
        # `~` cannot be backslash-escaped in old marked (prints the backslash)
        # and two of them in one paragraph are a strikethrough in new marked
        # (suibi-00: "呀~周末 ... blog~"). The entity renders as ~ in both.
        return t.replace("~", "&#126;")

    def guard_line_start(self, t: str) -> str:
        """Escape a leading heading/list marker. Only for text that will sit at
        the start of a paragraph line: inside a heading "1. 前言" cannot be a
        list, and escaping it there put a literal backslash into two posts."""
        return self._LINE_START_ESC.sub(r"\1\\\2\3", t, count=1)


# --------------------------------------------------------------------------- #
# Post extraction
# --------------------------------------------------------------------------- #
def parse_post(path: Path, rel: str):
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "lxml")
    title_el = soup.select_one(".post-title")
    title = title_el.get_text(" ", strip=True) if title_el else ""
    date = None
    upd = None
    for t in soup.select(".post-meta time"):
        dt = t.get("datetime")
        if not dt:
            continue
        item = t.find_parent(class_="post-meta-item")
        txt = item.get_text(" ", strip=True) if item else t.get_text()
        if "更新" in txt or "Edited" in txt or "updated" in txt.lower():
            upd = dt
        elif date is None:
            date = dt
    if date is None:
        date = rel[:10].replace("/", "-") + "T00:00:00+08:00"
    cats = [a.get_text(strip=True) for a in soup.select(".post-meta .post-category a, .post-meta a[href^='/categories/']")]
    cats = list(dict.fromkeys(c for c in cats if c))
    tags = [a.get_text(strip=True).lstrip("#").strip() for a in soup.select(".post-tags a")]
    tags = list(dict.fromkeys(t for t in tags if t))
    body = soup.select_one(".post-body")
    if body is None:
        raise RuntimeError(f"{rel}: no .post-body")
    conv = Converter()
    md = conv.convert(body)
    plain = re.sub(r"\s+", " ", body.get_text(" ")).strip()
    return {
        "slug": rel.split("/")[-1], "path": rel, "title": title, "date": date,
        "updated": upd, "categories": cats, "tags": tags, "markdown": md,
        "plain_len": len(plain), "plain": plain, "warnings": conv.warnings,
    }


def excerpt_boundaries(deploy: Path):
    """Map post path -> excerpt plain text, from the paginated index pages.
    A post that shows a '阅读全文' button had a <!-- more --> tag; the excerpt
    text tells us where."""
    out = {}
    pages = [deploy / "index.html"] + sorted(deploy.glob("page/*/index.html"))
    for pg in pages:
        if not pg.exists():
            continue
        soup = BeautifulSoup(pg.read_text(encoding="utf-8"), "lxml")
        for art in soup.select("article"):
            link = art.select_one(".post-title-link, .post-title a")
            if not link:
                continue
            href = link.get("href", "").strip("/")
            more = art.select_one("a.btn[href*='#more']")
            body = art.select_one(".post-body")
            if more and body:
                for b in body.select("a.btn"):
                    b.decompose()
                out[href] = re.sub(r"\s+", " ", body.get_text(" ")).strip()
    return out


def insert_more(md: str, excerpt_plain: str) -> str:
    """Put <!-- more --> after the paragraph whose cumulative plain text first
    covers the excerpt. Approximate by construction; good enough that a
    re-render shows the same fold."""
    if not excerpt_plain:
        return md
    target = len(excerpt_plain)
    blocks = md.split("\n\n")
    acc = 0
    for i, b in enumerate(blocks):
        acc += len(re.sub(r"\s+", " ", re.sub(r"[#*`>\[\]()!|-]", "", b)).strip())
        if acc >= target * 0.9:
            return "\n\n".join(blocks[: i + 1]) + "\n\n<!-- more -->\n\n" + "\n\n".join(blocks[i + 1:])
    return md


def yaml_str(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def write_post(post, dest: Path):
    fm = [f"title: {yaml_str(post['title'] or post['slug'])}",
          f"date: {post['date'][:19].replace('T', ' ')}"]
    if post["updated"]:
        fm.append(f"updated: {post['updated'][:19].replace('T', ' ')}")
    if post["categories"]:
        fm.append("categories:")
        fm += [f"  - {yaml_str(c)}" for c in post["categories"]]
    if post["tags"]:
        fm.append("tags:")
        fm += [f"  - {yaml_str(t)}" for t in post["tags"]]
    dest.write_text("---\n" + "\n".join(fm) + "\n---\n\n" + post["markdown"], encoding="utf-8")


# --------------------------------------------------------------------------- #
# Site-level config, read off the generated chrome
# --------------------------------------------------------------------------- #
def site_facts(deploy: Path):
    soup = BeautifulSoup((deploy / "index.html").read_text(encoding="utf-8"), "lxml")
    g = lambda sel, attr=None: (lambda e: (e.get(attr) if attr else e.get_text(strip=True)) if e else "")(soup.select_one(sel))
    facts = {
        "title": g(".site-title") or g("title"),
        "subtitle": g(".site-subtitle"),
        "author": g(".site-author-name"),
        "description": g(".site-description"),
        "avatar": g(".site-author-image", "src"),
        "lang": soup.html.get("lang", "zh-CN") if soup.html else "zh-CN",
        "generator": g("meta[name=generator]", "content"),
        "menu": [], "social": {}, "scheme": "Muse", "next_version": "",
    }
    for li in soup.select(".menu-item a"):
        facts["menu"].append((li.get_text(" ", strip=True), li.get("href", "")))
    for a in soup.select(".links-of-author a, .social-link, .links-of-author-item a"):
        facts["social"][a.get_text(" ", strip=True) or a.get("title", "")] = a.get("href", "")
    m = re.search(r"NexT\.(\w+) v([\d.]+)", soup.get_text())
    if m:
        facts["scheme"], facts["next_version"] = m.group(1), m.group(2)
    return facts


def write_site_config(out: Path, facts, url):
    menu = "\n".join(f"  {name}: {href}" for name, href in facts["menu"]) or "  home: /"
    social = "\n".join(f"  {k}: {v}" for k, v in facts["social"].items()) or "  # none found in the generated site"
    (out / "_config.yml").write_text(f"""# Rebuilt from the generated site, not recovered: the original _config.yml was
# lost with the source tree. Every value here was read off the deployed HTML
# (site chrome, permalinks, generator meta), so what is NOT visible in HTML --
# plugin options, deploy credentials -- is a guess marked as such.
title: {facts['title']}
subtitle: '{facts['subtitle']}'
description: '{facts['description']}'
author: {facts['author']}
language: {facts['lang']}
timezone: Asia/Shanghai

url: {url}
root: /
# The deployed URLs are /YYYY/MM/DD/slug/ -- this permalink reproduces them.
permalink: :year/:month/:day/:title/
permalink_defaults:

source_dir: source
public_dir: public
new_post_name: :title.md
default_layout: post
titlecase: false
external_link:
  enable: true
render_drafts: false
post_asset_folder: false
relative_link: false
future: true
highlight:
  enable: true
  line_number: true
  auto_detect: false

index_generator:
  path: ''
  per_page: 10
  order_by: -date
per_page: 10
pagination_dir: page

theme: next

# GUESS: the site was deployed to the github.io repo's master branch (that is
# where the generated files are). Fill in before running `hexo deploy`.
deploy:
  type: git
  repo: git@github.com:Belyenochi/belyenochi.github.io.git
  branch: master

# The generated pages include a local search index (search.xml), so this
# plugin was installed.
search:
  path: search.xml
  field: post
""", encoding="utf-8")


def write_theme_config(out: Path, facts):
    tdir = out / "themes" / "next"
    tdir.mkdir(parents=True, exist_ok=True)
    menu_keys = {"首页": "home", "分类": "categories", "归档": "archives", "标签": "tags", "关于": "about", "搜索": "search"}
    menu = []
    for name, href in facts["menu"]:
        key = menu_keys.get(name, name.lower())
        menu.append(f"  {key}: {href}" if key != "search" else "  #search: /search/ || search  # rendered by local_search, not a page")
    social = "\n".join(f"  {k}: {v}" for k, v in facts["social"].items()) or "  # none recoverable from HTML"
    (tdir / "_config.yml").write_text(f"""# Rebuilt for NexT {facts['next_version'] or '5.x'}, scheme {facts['scheme']} -- both read from the
# footer of the deployed pages. The theme's own _config.yml was not in the
# backup. Only settings that leave a visible trace in HTML are set here; the
# rest is the theme default.
scheme: {facts['scheme']}
language: {facts['lang']}

menu:
{chr(10).join(menu)}

menu_icons:
  enable: true

avatar: {facts['avatar']}

social:
{social}

local_search:
  enable: true
  trigger: auto
  top_n_per_article: 1

# The index pages of the deployed site show a "阅读全文 »" button on every
# post while no post page has an <a id="more"> anchor, which is exactly what
# this option produces. length is the theme default; the measured excerpts
# on the original index agree with it.
auto_excerpt:
  enable: true
  length: 150
# Every read-more button on the original index links to <post>/#more; in
# post.swig that suffix is emitted only when this is on.
scroll_to_more: true

# Top level, not under codeblock: that nesting is NexT 7. In 5.x the stylus
# variables for the code gutter ($highlight-gutter) are derived from this key,
# and with it missing main.css fails to compile at highlight.styl:79.
highlight_theme: normal

post_meta:
  item_text: true
  created_at: true
  updated_at: true
  categories: true

footer:
  powered: true
  theme:
    enable: true
    version: true
""", encoding="utf-8")


def write_about(deploy: Path, out: Path):
    src = deploy / "about" / "index.html"
    if not src.exists():
        return False
    soup = BeautifulSoup(src.read_text(encoding="utf-8"), "lxml")
    body = soup.select_one(".post-body")
    if body is None:
        return False
    md = Converter().convert(body)
    t = soup.select_one(".post-title")
    title = t.get_text(strip=True) if t else "关于"
    d = out / "source" / "about"
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.md").write_text(f"---\ntitle: {yaml_str(title)}\ndate: 2018-07-16 00:00:00\n---\n\n{md}", encoding="utf-8")
    return True


# --------------------------------------------------------------------------- #
def main(deploy_dir, out_dir):
    deploy, out = Path(deploy_dir), Path(out_dir)
    (out / "source" / "_posts").mkdir(parents=True, exist_ok=True)
    (out / "_private").mkdir(exist_ok=True)
    (out / "scaffolds").mkdir(exist_ok=True)

    posts = []
    for idx in sorted(deploy.glob("[0-9][0-9][0-9][0-9]/[0-9][0-9]/[0-9][0-9]/*/index.html")):
        rel = str(idx.parent.relative_to(deploy))
        if not POST_DIR.match(rel):
            continue
        posts.append(parse_post(idx, rel))

    # No <!-- more --> is inserted, deliberately. The original post pages carry
    # no <a id="more"> anchor, so the sources never had the tag; the index
    # excerpts came from NexT's auto_excerpt (theme config), which is turned on
    # in write_theme_config. An earlier version of this script inserted the tag
    # and every post gained one anchor the original did not have.
    report = {"public": [], "private": [], "images": 0, "about": False}
    used_slugs = set()
    for p in posts:
        p["has_more"] = False
        slug = p["slug"]
        if slug in used_slugs:
            slug = p["date"][:10] + "-" + slug
        used_slugs.add(slug)
        if p["path"] in PRIVATE:
            dest = out / "_private" / f"{slug}.md"
            write_post(p, dest)
            report["private"].append({"path": p["path"], "title": p["title"], "why": PRIVATE[p["path"]], "file": str(dest)})
        else:
            dest = out / "source" / "_posts" / f"{slug}.md"
            write_post(p, dest)
            report["public"].append({"path": p["path"], "title": p["title"], "date": p["date"], "chars": p["plain_len"],
                                     "categories": p["categories"], "tags": p["tags"], "code_blocks": p["markdown"].count("\n```") // 2,
                                     "more": p["has_more"], "file": dest.name})

    # images: everything the posts reference lives under /images
    img_src = deploy / "images"
    if img_src.exists():
        dst = out / "source" / "images"
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(img_src, dst)
        report["images"] = sum(1 for _ in dst.rglob("*") if _.is_file())

    facts = site_facts(deploy)
    write_site_config(out, facts, "https://belyenochi.github.io")
    write_theme_config(out, facts)
    report["about"] = write_about(deploy, out)
    report["site"] = facts

    (out / "scaffolds" / "post.md").write_text("---\ntitle: {{ title }}\ndate: {{ date }}\ncategories:\ntags:\n---\n", encoding="utf-8")
    (out / ".gitignore").write_text("node_modules/\npublic/\ndb.json\n.deploy_git/\n_private/\n", encoding="utf-8")
    (out / "RECOVERY-REPORT.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    r = main(sys.argv[1], sys.argv[2])
    print(f"public posts : {len(r['public'])}")
    print(f"private posts: {len(r['private'])}")
    print(f"images       : {r['images']}")
    print(f"about page   : {r['about']}")
    print(f"site         : {r['site']['title']} / {r['site']['author']} / NexT {r['site']['next_version']} {r['site']['scheme']} / menu {[m[0] for m in r['site']['menu']]}")
