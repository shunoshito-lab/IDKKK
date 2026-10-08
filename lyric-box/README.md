# Lyric Box

Testi sincronizzati con Spotify e animati in base al mood del brano, ispirati al COTODAMA Lyric Speaker. Un solo file HTML, senza build e senza dipendenze npm.

La ricerca dietro le scelte: [`../docs/ricerca-lyric-speaker.md`](../docs/ricerca-lyric-speaker.md).

## Avvio

Il login Spotify non funziona da `file://`, e Spotify non accetta più `localhost`. Servi la cartella su `127.0.0.1`:

```bash
npx http-server -a 127.0.0.1 -p 8137 .
# apri http://127.0.0.1:8137/lyric-box/
```

### Senza Spotify
- **Demo**: testo di prova originale, parte da solo. Puoi linkare un punto preciso e uno stile: `?demo&t=22&style=cloud`.
- **Manuale**: scrivi artista e titolo, la pagina scarica il testo da LRCLIB. Fai partire la canzone altrove e premi Spazio sul primo secondo; correggi lo sfasamento con ← →.

### Con Spotify
1. Crea un'app su https://developer.spotify.com/dashboard. Dal 2026, in Development Mode il proprietario deve avere Premium e l'app è limitata a 5 utenti.
2. Come Redirect URI aggiungi esattamente quello che la pagina mostra nel pannello, per esempio `http://127.0.0.1:8137/lyric-box/`.
3. Incolla il Client ID nel pannello e premi *Connetti Spotify*. Il flusso è Authorization Code + PKCE, senza client secret. Il refresh token resta nel `localStorage` di quel browser.
4. Fai partire una canzone su un qualsiasi dispositivo Spotify. La pagina fa polling di `currently-playing`.

## Comandi

| Tasto | Azione |
|---|---|
| Spazio | play/pausa (demo e modalità manuale) |
| ← → | offset del testo ±100 ms (con Shift ±500); viene salvato |
| [ ] | ±5 s (demo e modalità manuale) |
| S | cicla lo stile: auto → drift → kinetic → impact → cloud → crawl |
| H | nasconde l'HUD |
| F | schermo intero |
| Esc | pannello impostazioni |

## Come decide lo stile

1. **Ritornello**: righe di almeno 3 parole che compaiono più volte e formano blocchi consecutivi (l'indizio principale del metodo di Watanabe & Goto, ISMIR 2020).
2. **Energia per riga**: sillabe al secondo più un piccolo lessico IT/EN di arousal, smussata avanti e indietro lungo la canzone.
3. **Sezioni**: il testo viene spezzato ai confini del ritornello e alle pause oltre 3,5 s. Lo stile si sceglie per sezione:
   - strofa calma → `drift`
   - strofa energica → `kinetic`
   - valence negativa → `crawl`
   - ritornello → `impact`, oppure `cloud` se l'intera canzone è calma
4. **Interludi** più lunghi di 4,5 s → puntini con conto alla rovescia. Brano strumentale o testo assente → grafica geometrica.

Il lessico è volutamente minimo: è il punto più facile da migliorare, per esempio facendo stimare valence/arousal per riga a un LLM.

## Limiti noti
- Il timing per parola è **stimato** (per sillabe) quando la fonte dà solo le righe, cioè quasi sempre su LRCLIB. Le righe in formato enhanced LRC (`<mm:ss.xx>`) vengono usate così come sono.
- Niente analisi audio: lo stream di Spotify è protetto da DRM. Gli impulsi visivi seguono gli attacchi delle parole.
- Pensato per uso personale. I termini di Spotify vietano di sincronizzare registrazioni sonore con media visivi in prodotti: leggi la sezione 4 della ricerca.
