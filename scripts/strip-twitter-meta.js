/* Remove the twitter:* meta tags from every rendered page.
 *
 * Hexo's open_graph helper always emits <meta name="twitter:card">
 * (options.twitter_card || 'summary'), and the only switch NexT offers is
 * open_graph.enable, which would also drop og:title / og:description and with
 * them the link previews in chat apps. This keeps Open Graph and removes just
 * the Twitter-specific lines, at the author's request. */
'use strict';

hexo.extend.filter.register('after_render:html', (html) =>
  html.replace(/^[ \t]*<meta name="twitter:[^"]*"[^>]*>\s*\r?\n?/gm, ''));
