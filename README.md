# The Tao of Jason — source

Hexo source for [belyenochi.github.io](https://belyenochi.github.io/).

The original sources were lost. Everything under `source/` was rebuilt from the
generated HTML of the deployed site — see [`tools/hexo-recover/`](tools/hexo-recover/)
for how, and for the verification that the rebuild renders back to the same
articles (25 posts, every structural element identical, body text identical
once whitespace is normalised).

## Layout

```
_config.yml              site config, reconstructed from the deployed pages
source/_posts/           25 posts, 2018-07 .. 2021-08
source/images/           106 images referenced by the posts
source/about/index.md    the about page
themes/next/_config.yml  NexT theme config, reconstructed; the theme itself is not tracked
scaffolds/
tools/hexo-recover/      the recovery and verification scripts, plus the per-post report
hexo-recover-generate.js renders every route through the Hexo API (see below)
```

## Building

The site was published with Hexo 3.9 and NexT v5.1.4 (scheme Muse). That
toolchain still builds it, with two caveats that `package.json` already handles:

```sh
git clone --depth 1 --branch v5.1.4 https://github.com/iissnan/hexo-theme-next themes/next
# keep our themes/next/_config.yml; the clone does not overwrite it because the
# directory already exists with only that file -- if git refuses, clone to a temp
# dir and copy everything except _config.yml in.
npm install
npx -y -p node@18 -c 'node hexo-recover-generate.js'   # writes public/
```

Why not plain `hexo generate`: Hexo 3.9 does not start on Node 24 (`util.isDate`
was removed), and on Node 18 it renders every route correctly but writes each
file as 0 bytes. The small script renders through the same API and writes with
`fs`. It exists to verify the recovery; a blog that is going to be maintained
again should move to a current Hexo and NexT — the Markdown does not depend on
the old versions.

## Not in this repository

Three posts that exist in the deployed HTML are kept out of `source/_posts/` on
purpose and are ignored by git (`_private/`). One was removed from the live site
by hand in 2025; the other two were never meant as blog posts. Republishing any
of them is a decision, not a side effect of a rebuild.
