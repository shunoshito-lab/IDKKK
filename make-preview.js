/* Genera preview.html da launcher/index.html: stessa UI, dentro una cornice
   16:9 invece che a schermo intero. Un solo sorgente, niente copie da tenere
   allineate a mano. */
const fs = require('fs');
const src = fs.readFileSync('launcher/index.html', 'utf8');

const head = src.slice(src.indexOf('<title>'), src.indexOf('</head>'));
const body = src.slice(src.indexOf('<body>') + 6, src.indexOf('</body>'))
                .replace(/<script src="webOSTV\.js"><\/script>\s*/, '')
                .replace(/<script src="icons\.js"><\/script>/,
                         '<script>' + fs.readFileSync('launcher/icons.js', 'utf8') + '</script>');

const chrome = `
<meta name="claude:viewport-fit-sides" content="cover">
<style>
/* --- solo per l'anteprima: la TV dentro una cornice, non a schermo intero --- */
html,body{height:auto;overflow:visible;background:#04050a}
body{font-family:var(--ui);color:var(--ink);
  padding-left:max(16px,env(safe-area-inset-left,0px));
  padding-right:max(16px,env(safe-area-inset-right,0px));
  padding-block:clamp(16px,3.5vw,40px);
  display:flex;flex-direction:column;align-items:center;gap:clamp(12px,2vw,20px)}
.wrap{width:100%;max-width:1360px;display:flex;flex-direction:column;
  gap:clamp(10px,1.6vw,16px);min-width:0}
.bar{display:flex;align-items:baseline;justify-content:space-between;
  gap:12px;flex-wrap:wrap}
.bar h2{font-family:var(--display);font-size:clamp(17px,2.4vw,24px);font-weight:700;
  letter-spacing:-.02em;color:var(--ink)}
.bar p{font-size:clamp(12px,1.5vw,14px);color:var(--ink-3)}
.tv{position:relative;width:100%;aspect-ratio:16/9;max-width:100%;
  border-radius:clamp(8px,1.1vw,16px);overflow:hidden;
  border:1px solid rgba(255,255,255,.1);
  box-shadow:0 30px 70px -30px rgba(0,0,0,.9),0 0 0 1px rgba(255,255,255,.04)}
.tv #stage{position:absolute;inset:0}
/* sul telefono la cornice diventa verticale e la Home si ridispone da sola */
@media (max-width:640px){ .tv{aspect-ratio:9/15} }
.legend{display:flex;flex-wrap:wrap;gap:clamp(8px,1.4vw,14px);
  font-size:clamp(11px,1.4vw,13px);color:var(--ink-3);min-width:0}
.legend b{color:var(--ink-2);font-weight:500}
.legend kbd{font-family:var(--ui);font-size:.92em;color:var(--ink-2);
  border:1px solid var(--pane-line);border-radius:5px;padding:1px 6px;
  background:rgba(255,255,255,.05)}
.note{font-size:clamp(11px,1.4vw,13px);color:var(--ink-3);line-height:1.5;
  max-width:62ch}
</style>`;

const page = `<!DOCTYPE html>
<html lang="it" data-perf="glass">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
${head}
${chrome}
</head>
<body>
<div class="wrap">
  <div class="bar">
    <h2>Home</h2>
    <p>anteprima &middot; la stessa pagina che gira sulla TV</p>
  </div>
  <div class="tv">
${body}
  </div>
  <div class="legend">
    <span><b>Frecce</b> <kbd>&larr;</kbd><kbd>&uarr;</kbd><kbd>&darr;</kbd><kbd>&rarr;</kbd> muovi</span>
    <span><b>Invio</b> apri</span>
    <span><b>1&ndash;4</b> cambia modalit&agrave;</span>
    <span><b>M</b> suono</span>
    <span><b>L</b> radio &middot; <b>N</b> stazione</span>
    <span>oppure tocca i riquadri</span>
  </div>
  <p class="note">Sul telecomando le quattro modalit&agrave; stanno sui tasti colorati.
  Qui meteo e uscite della settimana sono esempi: l&rsquo;anteprima non pu&ograve; chiamare
  servizi esterni n&eacute; aprire le app. Sulla TV arrivano da Open-Meteo e TVMaze,
  con le locandine, e i riquadri aprono le app vere. Anche la radio lofi suona solo sulla TV:
  qui l&rsquo;audio esterno &egrave; bloccato.</p>
</div>
</body>
</html>`;

fs.writeFileSync('preview.html', page);
console.log('preview.html: ' + page.length + ' byte');

/* Il tennis in anteprima: stessa pagina, senza PeerJS e QR. Dentro
   l'anteprima WebRTC e' bloccato, quindi il gioco parte da solo in modalita'
   telecomando: si gioca con Invio o cliccando. */
const t = fs.readFileSync('launcher/tennis.html', 'utf8')
  .replace(/<script src="lib\/qrcode\.js"><\/script>\s*/, '')
  .replace(/<script src="lib\/peerjs\.min\.js"><\/script>\s*/, '');
fs.writeFileSync('preview-tennis.html', t);
console.log('preview-tennis.html: ' + t.length + ' byte');
