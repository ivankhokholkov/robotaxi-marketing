// Зеркалирование сайта autonomy.yandex.ru целиком (страницы меню).
// Качает HTML страниц, CDN-ассеты (yastatic.net, avatars.mds), корневые /static/...,
// переписывает CDN-ссылки на корневые локальные /assets/..., глушит Метрику.
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname, join, extname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = fileURLToPath(new URL('../', import.meta.url));
const ORIGIN = 'https://autonomy.yandex.ru';
const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36';

const PAGES = [
  '/', '/products/robotaxi', '/products/truck', '/products/robot',
  '/story', '/mission', '/blog', '/media', '/contacts',
];

const CDN_HOSTS = ['yastatic.net', 'avatars.mds.yandex.net'];
const CDN_RE = new RegExp(`https://(?:${CDN_HOSTS.map(h => h.replace(/\./g, '\\.')).join('|')})/[^\\s"'\`)\\\\<>]+`, 'g');
// корневые пути к файлам с расширением: /static/..., /favicon.ico, /manifest.json
const LOCAL_RE = /["'`(](\/(?:static|fonts|images|icons)\/[^"'`)\\\s]+?\.[a-z0-9]{2,5}|\/favicon[^"'`)\\\s]*|\/manifest[^"'`)\\\s]*\.json)["'`)]/gi;
// в __NEXT_DATA__ пути лежат без префикса: "images/home/hero/pic.webp" -> /static/images/...
const REL_RE = /["'`]((?:images|videos|fonts|icons)\/[^"'`\\\s]+?\.[a-z0-9]{2,5})["'`]/gi;
// srcset и прочие места, где путь не обёрнут кавычками
const BARE_RE = /\/static\/(?:images|videos|fonts|icons|favicon)\/[^"'`)\\\s,]+?\.[a-z0-9]{2,5}/gi;

const EXT_BY_TYPE = {
  'image/jpeg': '.jpg', 'image/png': '.png', 'image/webp': '.webp',
  'image/gif': '.gif', 'image/svg+xml': '.svg', 'image/avif': '.avif',
  'video/mp4': '.mp4', 'font/woff2': '.woff2', 'font/woff': '.woff',
  'text/css': '.css', 'application/javascript': '.js', 'text/javascript': '.js',
};

const UNWANTED = /https:\/\/mc\.yandex\.ru/g; // Метрика — глушим

async function get(url) {
  const res = await fetch(url, { headers: { 'User-Agent': UA, Referer: ORIGIN + '/' } });
  if (!res.ok) throw new Error(String(res.status));
  return { ct: res.headers.get('content-type') || '', buf: Buffer.from(await res.arrayBuffer()) };
}

function cdnLocalPath(url, ct) {
  const u = new URL(url);
  // имя файла на диске — раскодированное: чанк pages/blog/[slug]-*.js приходит как %5Bslug%5D
  let p = decodeURIComponent(u.pathname).replace(/^\/+/, '');
  if (u.search) p += '_' + Buffer.from(u.search).toString('hex').slice(0, 8);
  if (!extname(p)) p += EXT_BY_TYPE[(ct || '').split(';')[0].trim()] || '.bin';
  return '/assets/' + u.hostname + '/' + p;
}

function isText(ct) { return /css|javascript|json|svg|html/.test(ct); }

async function save(relPath, data) {
  const abs = join(ROOT, relPath.replace(/^\//, ''));
  await mkdir(dirname(abs), { recursive: true });
  await writeFile(abs, data);
}

const cdnMap = new Map();   // cdn url -> локальный корневой путь
const cdnQueue = [];
const cdnSeen = new Set();
const localPaths = new Set(); // /static/... найденные пути
const failed = [];

function harvest(text) {
  for (const raw of text.match(CDN_RE) || []) {
    const url = raw.replace(/[.,;]+$/, '');
    if (!cdnSeen.has(url)) { cdnSeen.add(url); cdnQueue.push(url); }
  }
  let m;
  LOCAL_RE.lastIndex = 0;
  while ((m = LOCAL_RE.exec(text))) localPaths.add(m[1]);
  REL_RE.lastIndex = 0;
  while ((m = REL_RE.exec(text))) localPaths.add('/static/' + m[1]);
  BARE_RE.lastIndex = 0;
  while ((m = BARE_RE.exec(text))) localPaths.add(m[0]);
}

function rewrite(text) {
  return text
    .replace(CDN_RE, (m) => {
      const clean = m.replace(/[.,;]+$/, '');
      const local = cdnMap.get(clean);
      return local ? local + m.slice(clean.length) : m;
    })
    .replace(/https:\/\/mc\.yandex\.ru\/metrika\//g, '/static/_noop/metrika/')
    .replace(UNWANTED, '/static/_noop');
}

// 1. Страницы: стартовый список плюс обход внутренних ссылок (статьи блога и т.п.)
const MAX_PAGES = 80;
const pageBodies = new Map();
const pageQueue = [...PAGES];
const pageSeen = new Set(PAGES);

while (pageQueue.length && pageBodies.size < MAX_PAGES) {
  const p = pageQueue.shift();
  try {
    const { buf } = await get(ORIGIN + p);
    const html = buf.toString('utf8');
    pageBodies.set(p, html);
    harvest(html);
    // внутренние ссылки без расширения — это страницы, а не файлы
    for (const m of html.matchAll(/href="(\/[^"#?]*)"/g)) {
      const href = m[1].replace(/\/$/, '') || '/';
      if (extname(href)) continue;
      if (href.startsWith('/static')) continue;
      if (pageSeen.has(href)) continue;
      pageSeen.add(href);
      pageQueue.push(href);
    }
  } catch (e) { failed.push(`page ${p} — ${e.message}`); }
}

// 2. CDN-ассеты (текстовые пополняют очередь)
const cdnBodies = new Map();
while (cdnQueue.length) {
  const batch = cdnQueue.splice(0, 6);
  await Promise.all(batch.map(async (url) => {
    try {
      const { ct, buf } = await get(url);
      const local = cdnLocalPath(url, ct);
      cdnMap.set(url, local);
      cdnBodies.set(url, { local, buf, text: isText(ct) });
      if (isText(ct)) harvest(buf.toString('utf8'));
    } catch (e) { failed.push(`cdn ${url} — ${e.message}`); }
  }));
}

// 3. Запись CDN-ассетов с переписанными ссылками
for (const [, { local, buf, text }] of cdnBodies) {
  await save(local, text ? rewrite(buf.toString('utf8')) : buf);
}

// 4. Запись страниц: / -> index.html, /products/truck -> products/truck/index.html
for (const [p, html] of pageBodies) {
  const rel = p === '/' ? 'index.html' : p.replace(/^\//, '') + '/index.html';
  // на проде страница живёт без слеша в конце, локально — со слешем,
  // поэтому относительные src="static/..." делаем корневыми
  await save(rel, rewrite(html).replace(/(["'(])static\//g, '$1/static/'));
}

// 5. Корневые /static/... — кладём по тому же пути, что на проде
const staticList = [...localPaths];
let staticOk = 0;
for (let i = 0; i < staticList.length; i += 6) {
  await Promise.all(staticList.slice(i, i + 6).map(async (p) => {
    try { const { buf } = await get(ORIGIN + p); await save(p, buf); staticOk++; }
    catch (e) { failed.push(`static ${p} — ${e.message}`); }
  }));
}

// 5б. JSON-данные Next.js — нужны для переходов между страницами без перезагрузки
const buildId = [...pageBodies.values()][0]?.match(/"buildId":"([^"]+)"/)?.[1];
let dataOk = 0;
if (buildId) {
  const list = [...pageBodies.keys()];
  for (let i = 0; i < list.length; i += 6) {
    await Promise.all(list.slice(i, i + 6).map(async (p) => {
      const slug = p === '/' ? 'index' : p.replace(/^\//, '');
      const rel = `/_next/data/${buildId}/${slug}.json`;
      try { const { buf } = await get(ORIGIN + rel); await save(rel, rewrite(buf.toString('utf8'))); dataOk++; }
      catch (e) { failed.push(`data ${slug} — ${e.message}`); }
    }));
  }
}

// 6. Заглушки Метрики
for (const f of ['watch.js', 'tag.js', 'tag_phono.js']) {
  await save('/static/_noop/metrika/' + f, '/* Метрика Яндекса отключена в копии */\n');
}

console.log(JSON.stringify({
  pages: pageBodies.size, cdn: cdnBodies.size, static: staticOk, data: dataOk, failed,
}, null, 2));
