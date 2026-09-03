// `hexo generate` on Hexo 3.9 under Node 18 writes every file as 0 bytes: the
// route streams render fine (checked: 60 KB post pages, 46 KB CSS through the
// API) but the write step loses the data. Render each route here and write it
// with plain fs instead. Same output, minus the broken pipe.
const fs = require('fs'), path = require('path');
const Hexo = require(process.cwd() + '/node_modules/hexo');
const hexo = new Hexo(process.cwd(), { silent: true });
const slurp = (s) => new Promise((res, rej) => { const ch = []; s.on('data', c => ch.push(Buffer.isBuffer(c) ? c : Buffer.from(String(c)))).on('end', () => res(Buffer.concat(ch))).on('error', rej); });
(async () => {
  await hexo.init(); await hexo.load();
  const out = path.join(process.cwd(), 'public');
  fs.rmSync(out, { recursive: true, force: true });
  let n = 0, empty = [];
  for (const r of hexo.route.list()) {
    const buf = await slurp(hexo.route.get(r));
    const f = path.join(out, r);
    fs.mkdirSync(path.dirname(f), { recursive: true });
    fs.writeFileSync(f, buf);
    n++; if (buf.length === 0) empty.push(r);
  }
  console.log(`  written ${n} files; empty: ${empty.length}${empty.length ? ' -> ' + empty.slice(0, 5).join(', ') : ''}`);
  process.exit(0);
})().catch(e => { console.error(e); process.exit(1); });
