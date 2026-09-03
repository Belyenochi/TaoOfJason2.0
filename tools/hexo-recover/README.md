# hexo-recover

Rebuilds the Markdown sources of a Hexo + NexT 5 blog from its generated HTML.

Written for belyenochi.github.io, whose sources were lost. The 2022-03-08
backup in `Belyenochi/TaoOfJason` turned out to hold no Markdown at all, but it
did hold `.deploy_git` -- 77 deploys of generated HTML, more complete than the
live site -- and that is the input here.

## What it does

`recover.py <deploy_git> <out>` reads every `YYYY/MM/DD/slug/index.html` and
writes a Hexo project:

| output | source of truth |
|---|---|
| `source/_posts/*.md` | `.post-body` converted to Markdown; title, date, categories, tags from `.post-meta` and `.post-tags` |
| `source/images/` | copied from the site's `/images` |
| `source/about/index.md` | the `/about/` page |
| `_config.yml` | site chrome: title, author, language, permalink shape, search index presence |
| `themes/next/_config.yml` | scheme and version from the footer, menu, social links, avatar, `auto_excerpt`, `scroll_to_more`, `highlight_theme` -- each one inferred from something visible in the HTML |
| `_private/*.md` | posts that exist in the HTML but must not be republished without a decision: see `PRIVATE` in the script, each entry carries its reason |
| `RECOVERY-REPORT.json` | per-post inventory |

The converter is specific to NexT's markup on purpose. Generic HTML-to-Markdown
tools mangle the two things that matter most here: code blocks are rendered as a
`<table>` with a line-number gutter, and every heading carries an anchor `<a>`.
It also escapes only the characters that would change meaning (`*`, `_`, `` ` ``,
`\`, `[`, `]`, and heading/list markers at the start of a paragraph), because
over-escaped Markdown is unpleasant to keep editing, which is the whole point.

## How it was verified

Not by reading the output. The recovered sources were rendered back through the
same toolchain the site used -- Hexo 3.9.0, NexT v5.1.4, `hexo-renderer-marked`
1.x -- and each article body was compared with the original:

```
verify.py <original_public_dir> <regenerated_public_dir>
```

Result for the 25 public posts: mean text similarity 0.9999; 24 of 25 identical
once spaces are removed; every structural tag count (headings, lists, tables,
images, links, code blocks, emphasis) identical in all 25. The `<p>` count is
excluded: bare text nodes in the original become paragraphs in Markdown, which
is not a content difference.

The same check was then run against the site as rebuilt with **Hexo 8.1.2 +
NexT 8.29.0** (the toolchain this repository now uses): 24 of 25 bodies
identical once spaces are removed, structure counts identical in 24 of 25. The
one difference was `**[本篇]**` glued to a word, which the old marked accepted
and CommonMark does not; the converter now emits `<strong>` for that shape.

### The old toolchain, for the record

The first verification used the versions the site was actually published with,
Hexo 3.9.0 and NexT v5.1.4 from `iissnan/hexo-theme-next`. Getting that to run
on a current machine took three workarounds, kept here in case anyone needs to
reproduce the original bytes:

- Hexo 3.9 does not start on Node 24 (`util.isDate` was removed); use Node 18.
- On Node 18 `hexo generate` renders every route correctly but writes every file
  as 0 bytes. Render through the Hexo API and write with `fs` instead
  (a 30-line script; it lived in the output dir as `hexo-recover-generate.js`).
- NexT 5 templates are swig, so `hexo-renderer-swig` is required -- without it
  pages are empty with no error -- and stylus must be `0.54.5`.

`next5_config.yml` alongside this file is the NexT 5 theme config as
reconstructed from the HTML; `_config.next.yml` at the repo root is its NexT 8
translation.

## Things learned from the HTML that were not in any config

- `auto_excerpt: enable, length 150` -- the index shows "阅读全文 »" on every
  post while no post page has an `<a id="more">` anchor.
- `scroll_to_more: true` -- every read-more link ends in `#more`.
- `highlight_theme` must be top-level in NexT 5 (nesting it under `codeblock`
  is NexT 7 and breaks the stylus build).
- Three image files have spaces in their names; the Markdown links use `%20`.
