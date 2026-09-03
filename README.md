# The Tao of Jason — source

Hexo source for [belyenochi.github.io](https://belyenochi.github.io/).
Hexo 8, NexT 8 (scheme Muse).

The original sources were lost. Everything under `source/` was rebuilt from the
generated HTML of the deployed site — see [`tools/hexo-recover/`](tools/hexo-recover/)
for how, and for the verification that the rebuild renders back to the same
articles.

## Layout

```
_config.yml              site config
_config.next.yml         NexT theme config (Hexo 5+ location; the theme lives in node_modules)
source/_posts/           25 posts, 2018-07 .. 2021-08
source/images/           106 images referenced by the posts
source/about/            the about page
source/tags/ source/categories/   index pages NexT needs for those menu items
scaffolds/post.md        `hexo new post` template
tools/hexo-recover/      the recovery and verification scripts, the per-post report,
                         and the NexT 5 config that was reconstructed along the way
```

## Working on it

```sh
npm install
npx hexo server            # http://localhost:4000
npx hexo new "标题"        # -> source/_posts/标题.md
npx hexo generate          # -> public/
npx hexo deploy            # pushes public/ to belyenochi.github.io (master)
```

Nothing here depends on an old runtime; it builds on the current Node.

## What was carried over from the old site, and where it now lives

| old site (NexT 5.1.4) | now |
|---|---|
| menu 首页/分类/归档/标签/关于/搜索 | `_config.next.yml` → `menu`, search is `local_search` |
| four social links | `_config.next.yml` → `social` |
| avatar `/images/avatar.jpg` | `_config.next.yml` → `avatar.url` |
| every index entry cut at ~150 chars with a read-more button | `hexo-auto-excerpt` (`excerpt_length: 150` in `_config.yml`) + `read_more_btn` |
| busuanzi visitor counter | `_config.next.yml` → `busuanzi_count` |
| `/YYYY/MM/DD/slug/` URLs | `_config.yml` → `permalink`, unchanged so inbound links keep working |
| highlight.js code blocks with line numbers | `_config.yml` → `syntax_highlighter`/`highlight` |
| `lang=zh-Hans` | `language: zh-CN` (NexT 8's name for the same file) |

## Not in this repository

Three posts that exist in the deployed HTML are kept out of `source/_posts/` on
purpose and are ignored by git (`_private/`). One was removed from the live site
by hand in 2025; the other two were never meant as blog posts. Republishing any
of them is a decision, not a side effect of a rebuild.
