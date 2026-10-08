# Lyric Box

Testi sincronizzati con Spotify e animati in base al mood del brano. Il modo di guardare viene dal COTODAMA Lyric Speaker, il modo di toccare da Teenage Engineering. Un solo file HTML, senza build e senza dipendenze npm.

- Ricerca: [`../docs/ricerca-lyric-speaker.md`](../docs/ricerca-lyric-speaker.md)
- Linguaggio di design (LB–1): [`../docs/design-lb1.md`](../docs/design-lb1.md)

## Avvio

Il login Spotify non funziona da `file://`, e Spotify non accetta più `localhost`. Servi la cartella su `127.0.0.1`:

```bash
npx http-server -a 127.0.0.1 -p 8137 .
# apri http://127.0.0.1:8137/lyric-box/
```

Al primo avvio si apre il menu. Da lì scegli la sorgente:

- **demo**: un testo di prova scritto per l'app, parte da solo. Puoi linkare un punto preciso e uno stile: `?demo&t=22&style=cloud`.
- **lrclib**: scrivi artista e titolo, la pagina scarica il testo. Fai partire la canzone altrove, poi premi Spazio sul primo secondo e correggi lo sfasamento con ← →.
- **spotify**:
  1. Crea un'app su https://developer.spotify.com/dashboard. Dal 2026, in Development Mode, il proprietario deve avere Premium e l'app è limitata a 5 utenti.
  2. Come Redirect URI aggiungi esattamente quello mostrato nel menu, per esempio `http://127.0.0.1:8137/lyric-box/`. Il tasto `copia` lo copia per te.
  3. Incolla il Client ID e premi *connetti spotify*. Il flusso è Authorization Code + PKCE, senza client secret.

## Come si usa

A riposo vedi solo le parole. Muovi il mouse, tocca lo schermo o premi un tasto e sale la barra:

```
[copertina  titolo · artista]   [ ▸ modo 01 drift auto │ ● sync ±0 ms │ ◎ 1:23 (−2:41) ]   [menu]
```

Nella barra il colore ha sempre lo stesso significato: **arancione** = tempo, **blu** = sync, **giallo** = modo, **grigio** = vista.

| Tasto | Azione |
|---|---|
| Spazio | play / pausa (demo e lrclib; con Spotify si comanda da Spotify) |
| [ ] | −5 s / +5 s (demo e lrclib) |
| ← → | sync del testo ±100 ms (Shift ±500); con la rotella sopra il segmento sync, ±100 a scatto |
| S | modo successivo |
| 1–5 / 0 | modo fisso (01 drift, 02 kinetic, 03 impact, 04 cloud, 05 crawl) / torna ad auto |
| H | barra: auto / fissa / spenta |
| T | tema: scuro / carta / auto |
| F | schermo intero |
| Esc | menu |

Sul telefono un tocco mostra o nasconde la barra. Toccare lo schermo della barra apre il menu su ((2)) modo. Lì trovi sync (tieni premuto ± per passi da 500 ms), trasporto, modi e tema.

## Come sceglie il modo

1. **Ritornello**: righe di almeno 3 parole che si ripetono e formano blocchi. È l'indizio principale del metodo di Watanabe & Goto (ISMIR 2020).
2. **Energia per riga**: sillabe al secondo più un piccolo lessico italiano e inglese di arousal, smussata lungo la canzone.
3. **Sezioni**: il testo viene spezzato ai confini del ritornello e alle pause oltre 3,5 s.
   - strofa calma → `01 drift`
   - strofa energica → `02 kinetic`
   - valence negativa → `05 crawl`
   - ritornello → `03 impact`, oppure `04 cloud` se tutta la canzone è calma
4. **Interludi** tra 4,5 e 12 s: tre puntini che si riempiono. Pause più lunghe, strumentali, testo assente o fine brano: una bobina con l'arco di avanzamento arancione.

## Limiti noti

- Il timing per parola è **stimato** (per sillabe) quando la fonte dà solo le righe, cioè quasi sempre con LRCLIB. Le righe in enhanced LRC (`<mm:ss.xx>`) si usano così come sono.
- Niente analisi audio: lo stream di Spotify è protetto da DRM. Gli impulsi visivi seguono gli attacchi delle parole e si attivano solo nei brani energici.
- Pensato per uso personale. I termini di Spotify vietano di sincronizzare registrazioni sonore con media visivi in un prodotto (vedi la sezione 4 della ricerca).
