import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const out = path.dirname(fileURLToPath(import.meta.url));

const formats = [
  ['01_smm-1080x1350',1080,1350,72,72,936,1206,6,'SMM 4:5','6–8 слоёв'],
  ['02_smm-1080x1080',1080,1080,72,72,936,936,6,'SMM 1:1','5–7 слоёв'],
  ['03_smm-1080x1920',1080,1920,72,108,936,1704,6,'SMM 9:16','6–8 слоёв'],
  ['04_urbanads-1080x450',1080,450,45,20,990,410,6,'UrbanAds horizontal','4–5 слоёв'],
  ['05_urbanads-1706x184',1706,184,71,0,1564,184,12,'UrbanAds stretch','3–4 слоя'],
  ['06_urbanads-940x1524',940,1524,70,99,800,1326,6,'UrbanAds vertical','6–8 слоёв'],
  ['07_urbanads-720x720',720,720,30,45,660,630,6,'UrbanAds pop-up','5–6 слоёв'],
  ['08_maps-1280x256',1280,256,16,16,1248,224,10,'Maps route banner','3–4 слоя'],
  ['09_route-card-1200x400',1200,400,48,32,1104,336,8,'Geo card banner','4–5 слоёв'],
  ['10_rsya-300x600',300,600,18,24,264,552,4,'РСЯ 300×600','4–5 слоёв'],
  ['11_rsya-300x250',300,250,16,16,268,218,4,'РСЯ 300×250','3–4 слоя'],
  ['12_rsya-320x100',320,100,10,8,300,84,4,'РСЯ 320×100','2–3 слоя'],
  ['13_rsya-970x250',970,250,36,18,898,214,10,'РСЯ 970×250','3–4 слоя'],
  ['14_rsya-160x600',160,600,12,24,136,552,2,'РСЯ 160×600','3–4 слоя'],
  ['15_rsya-300x300',300,300,16,16,268,268,4,'РСЯ 300×300','4–5 слоёв'],
  ['16_rsya-1000x120',1000,120,30,10,940,100,10,'РСЯ 1000×120','2–3 слоя'],
];

const esc = value => value.replaceAll('&','&amp;').replaceAll('<','&lt;');

for (const [name,w,h,sx,sy,sw,sh,cols,label,density] of formats) {
  const small = Math.max(8, Math.min(22, h * 0.035, w * 0.035));
  const carX = w * (h / w < .3 ? .60 : .42);
  const carY = h * (h / w < .3 ? .38 : .54);
  const carW = w * (h / w < .3 ? .34 : .52);
  const carH = Math.min(h * .32, carW * .35);
  const moduleX = sx + sw * .04;
  const moduleY = sy + sh * .18;
  const moduleW = sw * (h / w < .3 ? .47 : .60);
  const headlineLines = h / w < .3
    ? ['РОБОТАКСИ В МОСКВЕ']
    : w / h < .4
      ? ['МОСКВА', 'ВИДИТ', 'БОЛЬШЕ']
      : ['МОСКВА ВИДИТ', 'БОЛЬШЕ'];
  const maxChars = Math.max(...headlineLines.map(line => line.length));
  const titleSize = Math.max(8, Math.min(46, h * 0.075, moduleW * .88 / (maxChars * .58)));
  const moduleH = Math.min(sh * .38, titleSize * (headlineLines.length + 1.15));
  const headline = headlineLines.map((line,index) =>
    `<text x="${moduleX + moduleW*.05}" y="${moduleY + titleSize*(1.05+index)}" fill="#F7F3EA" font-family="Arial, sans-serif" font-size="${titleSize}" font-weight="800">${line}</text>`
  ).join('');
  const underlineY = moduleY + titleSize * (headlineLines.length + .28);
  const colLines = Array.from({length: cols - 1}, (_,i) => {
    const x = sx + sw * (i + 1) / cols;
    return `<line x1="${x}" y1="${sy}" x2="${x}" y2="${sy+sh}"/>`;
  }).join('');
  const gridId = `grid-${w}-${h}`;
  const svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">
  <defs>
    <pattern id="${gridId}" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="#FFFFFF" stroke-opacity=".055" stroke-width="1"/></pattern>
    <linearGradient id="accent" x1="0" x2="1"><stop stop-color="#FF3B30"/><stop offset=".55" stop-color="#FFD60A"/><stop offset="1" stop-color="#50E06E"/></linearGradient>
    <filter id="shadow"><feDropShadow dx="0" dy="12" stdDeviation="18" flood-opacity=".35"/></filter>
  </defs>
  <rect width="${w}" height="${h}" fill="#101214"/>
  <rect width="${w}" height="${h}" fill="url(#${gridId})"/>
  <rect x="${sx}" y="${sy}" width="${sw}" height="${sh}" rx="${Math.min(28,h*.06)}" fill="none" stroke="#56D7FF" stroke-width="3" stroke-dasharray="12 10"/>
  <g stroke="#56D7FF" stroke-opacity=".20" stroke-width="1">${colLines}</g>
  <rect x="${moduleX}" y="${moduleY}" width="${moduleW}" height="${moduleH}" rx="${Math.min(22,h*.04)}" fill="#191D21" stroke="#FFFFFF" stroke-opacity=".10"/>
  ${headline}
  <rect x="${moduleX + moduleW*.05}" y="${underlineY}" width="${moduleW*.42}" height="${Math.max(3,h*.008)}" rx="4" fill="#FF3B30"/>
  <g filter="url(#shadow)">
    <path d="M${carX} ${carY+carH*.65} C${carX+carW*.10} ${carY+carH*.10}, ${carX+carW*.64} ${carY}, ${carX+carW*.92} ${carY+carH*.46} L${carX+carW} ${carY+carH*.72} L${carX+carW*.94} ${carY+carH} L${carX+carW*.08} ${carY+carH} Z" fill="#F4F4F2"/>
    <path d="M${carX+carW*.55} ${carY+carH*.12} h${carW*.18} l${carW*.05} ${carH*.15} h-${carW*.28}z" fill="#111417"/>
    <rect x="${carX+carW*.45}" y="${carY+carH*.79}" width="${carW*.45}" height="${Math.max(5,carH*.08)}" rx="6" fill="url(#accent)"/>
    <circle cx="${carX+carW*.22}" cy="${carY+carH}" r="${Math.max(6,carH*.17)}" fill="#171A1D" stroke="#71777D" stroke-width="3"/>
    <circle cx="${carX+carW*.82}" cy="${carY+carH}" r="${Math.max(6,carH*.17)}" fill="#171A1D" stroke="#71777D" stroke-width="3"/>
  </g>
  <path d="M${sx+sw*.05} ${sy+sh*.86} C${sx+sw*.28} ${sy+sh*.72}, ${sx+sw*.62} ${sy+sh*.94}, ${sx+sw*.94} ${sy+sh*.77}" fill="none" stroke="#56D7FF" stroke-width="${Math.max(2,h*.007)}" stroke-linecap="round"/>
  <circle cx="${sx+sw*.94}" cy="${sy+sh*.77}" r="${Math.max(4,h*.012)}" fill="#FF3B30"/>
  <text x="${sx}" y="${Math.max(small+4,sy-small*.35)}" fill="#56D7FF" font-family="Arial, sans-serif" font-size="${small}" font-weight="700">SAFE AREA ${sw}×${sh}</text>
  <text x="${sx}" y="${Math.min(h-small*.55,sy+sh+small*1.45)}" fill="#F7F3EA" font-family="Arial, sans-serif" font-size="${small}" font-weight="700">${esc(label)} · ${w}×${h} · ${esc(density)}</text>
</svg>`;
  fs.writeFileSync(path.join(out, `${name}.svg`), svg);
}

console.log(`Generated ${formats.length} guides in ${out}`);
