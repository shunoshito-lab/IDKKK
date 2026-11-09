/* Estrae da Simple Icons (CC0-1.0) solo i tracciati che servono e li scrive
   in launcher/icons.js. Uso:  npm pack simple-icons && tar xzf simple-icons-*.tgz
                               node make-icons.js package/icons            */
const fs = require('fs'), path = require('path');
const dir = process.argv[2];
const want = ['netflix','youtube','appletv','twitch','spotify','dazn','youtubemusic','now','paramountplus','crunchyroll'];
const out = {};
for (const s of want) {
  const svg = fs.readFileSync(path.join(dir, s + '.svg'), 'utf8');
  const m = svg.match(/<path d="([^"]+)"/);
  if (!m) throw new Error('tracciato non trovato: ' + s);
  out[s] = m[1];
}
fs.writeFileSync('launcher/icons.js',
  '/* Tracciati da Simple Icons 16.37.0 — https://simpleicons.org — licenza CC0-1.0.\n' +
  '   I marchi restano dei rispettivi proprietari; qui indicano il servizio che il riquadro apre.\n' +
  '   Generato da make-icons.js: non modificare a mano. */\n' +
  'window.SI = ' + JSON.stringify(out) + ';\n');
console.log('icons.js:', Object.keys(out).length, 'icone,', fs.statSync('launcher/icons.js').size, 'byte');
