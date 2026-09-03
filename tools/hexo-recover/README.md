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

## Rendering with Hexo 3.9 on a current Node

Hexo 3.9 does not run on Node 24 (`util.isDate` was removed), and on Node 18
`hexo generate` renders every route correctly but writes every file as 0 bytes.
`hexo-recover-generate.js` in the output directory renders each route through
the Hexo API and writes it with plain `fs`. Run it as:

```
cd <out> && npx -y -p node@18.20.8 -c 'node hexo-recover-generate.js'
```

Dependencies that had to be pinned for NexT 5 (`package.json` records them):
`hexo-renderer-swig` (NexT 5 templates are swig; without the renderer pages
are empty with no error) and `stylus@0.54.5` (newer stylus fails on
`highlight.styl`).

This toolchain is for verification. A blog that is going to be maintained again
should move to a current Hexo and NexT; the recovered Markdown does not depend
on the old versions.

## Things learned from the HTML that were not in any config

- `auto_excerpt: enable, length 150` -- the index shows "阅读全文 »" on every
  post while no post page has an `<a id="more">` anchor.
- `scroll_to_more: true` -- every read-more link ends in `#more`.
- `highlight_theme` must be top-level in NexT 5 (nesting it under `codeblock`
  is NexT 7 and breaks the stylus build).
- Three image files have spaces in their names; the Markdown links use `%20`.
