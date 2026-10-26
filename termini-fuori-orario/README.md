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
- `assets/img/bot.png` — sprite del buttafuori
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

## Intro

"Nuova partita" apre il protagonista allo specchio del livello −1 che pensa ad alta voce (circa 50 s, sottotitoli sincronizzati, musica abbassata). Clic, Esc o Spazio per saltare.

## Da fare

- Il flow field resta un flood fill su tutta la griglia (circa 216k celle). Va spostato in un Web Worker, oppure va limitata la ricerca a un raggio.
- Poster, cartelli e graffiti sono texture canvas generate a runtime (decine di canvas). Si possono cachare o mettere in un atlas.
- `index.html` è ancora un unico modulo di circa 2300 righe. Va diviso in moduli.
