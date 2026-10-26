# Termini Fuori Orario

Gioco 3D in browser (three.js 0.160.0 da CDN). `index.html` contiene tutto il codice; gli asset sono file separati.

## Avvio

Va servito via HTTP: il gioco carica la musica e gli sprite con `fetch`, quindi da `file://` non parte.

```
cd termini-fuori-orario
python3 -m http.server 8000
```

Poi apri http://localhost:8000

## Struttura

- `index.html` — gioco
- `assets/music/track1-4.mp3` — colonna sonora
- `assets/sfx/bot-voice.mp3` — voce del buttafuori
- `assets/models/man.json` — Salvino, il buttafuori: omino low-poly senza volto, occhi rossi
- `assets/img/bot-pixel.png` — immagine pixelata per jumpscare e riflesso del finale
- `assets/models/chain.json`, `oldpc.json`, `phone.json` — catene sulle uscite, PC accanto al quadro, telefono del protagonista
  (ogni `.json` è un GLB in base64: la versione pubblicata su claude.ai serve solo certi tipi di file; licenze in `assets/models/licenses/`)
- `assets/img/sky-city.jpg` — skybox città di notte (ridotta da 8192 a 2048 px)
- `assets/sfx/heartbeat.mp3` (paura), `bam.mp3` (presa), `studia.mp3` (codice sbagliato, distorto); `bot-voice.mp3` è distorta
- `assets/img/protagonist.png` — protagonista (disegnato via codice), usato nell'intro e nello specchio del finale
- `assets/sfx/intro-voice.mp3` — monologo dell'intro: voce sintetica Piper (`it_IT-riccardo`), deformata con ffmpeg

## Modifiche rispetto alla versione originale

- **Peso**: 3.9 MB di base64 inline → 154 KB di HTML più gli asset in file separati, cacheabili dal browser.
- **Memoria audio**: prima tutte e 4 le tracce venivano decodificate in RAM all'avvio (circa 180 MB di PCM). Ora ne sta una in RAM, più la successiva decodificata mentre suona.
- **Pathfinding dei fantasmi**: `Map` sostituita con un array tipizzato per i collegamenti tra livelli. Il calcolo del flow field passa da circa 8 ms a circa 6 ms (misurato in headless, mediana).
- **Audio**: ogni goccia e ogni passo creavano un `GainNode` collegato per sempre al reverb, che si accumulava nel tempo. Ora ci sono bus fissi, e un solo panner per perdita invece di uno per goccia.
- **Luci**: le 12 più forti vengono ricalcolate 10 volte al secondo, non più ordinate ~300 candidati ogni frame.
- **Mobile**: aggiunto `viewport`, senza il quale il layout restava a 980px di larghezza.
- **Testo**: aggiunto `<meta charset="utf-8">`; prima le scritte uscivano come `â¿`, `Â·`.
- **CSS**: il selettore `html[data-ps="3"] html[data-ps="3"] #keys` era scritto male e non si applicava mai. Ora i comandi spariscono in modalità camcorder come previsto dall'autore.
- **Rimosso**: la schermata di vittoria `winGame()` (non era raggiungibile) e `window.__dbg`, che esponeva lo stato interno al giocatore.

## Crediti

Modelli da Sketchfab, modificati:

- "Proportional Low Poly Man" di Robin Butler — CC BY 4.0 — https://sketchfab.com/3d-models/proportional-low-poly-man-free-download-0bfd0e2b49a348a4b64b20cc8196e3b3
- "Old PC Low Poly Set - Pack" di diopieretti3d — CC BY 4.0 — https://sketchfab.com/3d-models/old-pc-low-poly-set-pack-7eab0a9519e74bd5b1f9f480b2ddca8b
- "Low Poly Mobile Phone" di k. — CC BY 4.0 — https://sketchfab.com/3d-models/low-poly-mobile-phone-4ff99cf17b164e7b9790638c5d2ef4ce
- "City Rooftop Night Skybox" di Luis Vidal — CC BY 4.0 — https://sketchfab.com/3d-models/city-rooftop-night-skybox-cce0e8aaa10f45ccb234e1aa2a3d5753
- "ChainPack" di DarkWalf88 — CC BY-NC-SA 4.0 (niente uso commerciale) — https://sketchfab.com/3d-models/chainpack-eb6db9a6085b48809dd68bd6b6d7f438

Musica ed effetti sonori (brani C418/Key/OST, Phasmophobia, Spider-Man 2, meme) sono di terzi: solo uso personale.

## Intro

"Nuova partita" apre il protagonista allo specchio del livello −1 che pensa ad alta voce (circa 50 s, sottotitoli sincronizzati, musica abbassata). Clic, Esc o Spazio per saltare.

## Da fare

- Il flow field resta un flood fill su tutta la griglia (circa 216k celle). Va spostato in un Web Worker, oppure va limitata la ricerca a un raggio.
- Poster, cartelli e graffiti sono texture canvas generate a runtime (decine di canvas). Si possono cachare o mettere in un atlas.
- `index.html` è ancora un unico modulo di circa 2300 righe. Va diviso in moduli.
