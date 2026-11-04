# Home — launcher webOS (com.shun.launcher)

TV di riferimento: **LG 50UT73006LA, webOS 25, senza root.** Niente exploit,
niente Homebrew: solo Developer Mode ufficiale.

## Cosa c'è

```
launcher/
  index.html        la Home intera: nessuna dipendenza esterna
  webOSTV.js        libreria LG (Apache 2.0) — senza, window.webOS non esiste
  appinfo.json      id com.shun.launcher, 1920x1080, type web
  icon.png          80x80
  largeIcon.png     130x130
build.sh            pacchetto (+ install e launch se passi il device)
dist/*.ipk          il pacchetto pronto
```

## Setup, una volta sola

1. `npm i -g @webos-tools/cli`
2. Sulla TV: LG Content Store → app **Developer Mode** → login account LG →
   **Dev Mode Status ON** → riavvia la TV.
3. Riapri Developer Mode: ti mostra **IP** e **passphrase**. Poi:
   ```
   ares-setup-device
   ```
   `add` → nome `tv`, host = l'IP, port `9922`, user `prisoner`,
   auth type `password`, e come password la **passphrase**.
   Verifica con `ares-device -i --device tv`.

> La Dev Mode scade dopo ~50 ore: si rinnova dall'app con *Extend*.
> Se la TV smette di rispondere, quasi sempre è quella, non il codice.

## Installare

```
./build.sh tv
```

Il pacchetto è già in `dist/`, verificato: struttura corretta, nessun warning.

## Comandi sul telecomando

| Tasto | Effetto |
|---|---|
| Frecce | muovi tra i tile |
| OK | apri |
| Rosso / Verde / Giallo / Blu (403–406) | Coppia / Amici / Stress-free / Tutti |
| 1 – 4 | le stesse modalità, da tastiera |
| 0 | cicla i livelli grafici a mano |

Modalità e livello grafico restano salvati tra un avvio e l'altro.

## I tre livelli grafici — e perché

Misurato in rasterizzazione software (proxy onesto del SoC di una UT7300):

| livello | FPS | cosa fa |
|---|---|---|
| **glass** (default) | ~40 | vetro traslucido "cotto", 4 blob animati |
| **full** (opt-in) | **~11** | glass + `backdrop-filter` vero |
| **static** (fallback) | ~61 | blob fermi, pannelli più opachi |

Il collo di bottiglia non è un singolo effetto: è `backdrop-filter` **sopra uno
sfondo in movimento**, insieme a `mix-blend-mode`. Quella coppia impedisce alla
GPU di promuovere i layer, quindi ogni frame rifà il blur dell'intera area.

La Home quindi **non usa blur per frame**. I pannelli sono traslucidi (alpha
0.46): i blob si vedono comunque passare sotto, quindi il movimento resta —
cade solo la rifrazione, che era la parte costosa. Luce, profondità e anello
di focus sono gradienti e ombre dipinti *una volta*.

Regole rispettate in tutto il file, verificate dai test:
- si anima **solo `transform` e `opacity`** (il compositor, mai il layout)
- il focus accende un anello pre-disegnato via `opacity` — transizionare
  `box-shadow` voleva dire ripitturare il tile a ogni freccia = input lag
- la sfocatura dei blob è *dentro* il radial-gradient, non in un `filter`

All'avvio la Home misura gli FPS reali: parte da `glass`, prova `full` solo se
la TV è comoda e torna indietro se non regge. Col tasto `0` decidi tu.

## Come apre i siti

Tre tentativi in cascata, con guardia di 2,5s perché un tile non resti mai morto:

1. app nativa webOS (`youtube.leanback.v4` per YouTube)
2. browser della TV (`com.webos.app.browser`)
3. l'URL dentro la Home stessa

**Da verificare sulla TV:** webOS limita il lancio di altre app dalle app di
terze parti. Se i passi 1 e 2 vengono negati, si cade sul 3 — che funziona, ma
i siti con DRM dentro la nostra webview possono essere zoppi. Lo sapremo al
primo `ares-launch`; il piano B è tenere i tile sul browser di sistema.

## Da sistemare

- `RADIO_CARDUCCI_URL` in cima a `index.html` è un segnaposto: serve l'URL vero.

## Modificare i contenuti

Tutto in cima allo `<script>` di `index.html`: `SITES` (nome, sottotitolo,
colore, glifo, url, appId) e `MODES` (etichetta, tasto colorato, colore,
elenco tile). La griglia è a 3 colonne e si adatta al numero di tile.
