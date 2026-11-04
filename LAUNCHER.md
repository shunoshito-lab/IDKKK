# Home — launcher webOS (com.shun.launcher)

TV di riferimento: **LG 50UT73006LA, webOS 25, senza root.** Niente exploit,
niente Homebrew: solo Developer Mode ufficiale.

## Cosa c'è

```
launcher/
  index.html        la Home intera: nessuna dipendenza oltre ai font Google
  webOSTV.js        libreria LG (Apache 2.0) — senza, window.webOS non esiste
  appinfo.json      id com.shun.launcher, 1920x1080, type web
  icon.png          80x80
  largeIcon.png     130x130
build.sh            pacchetto (+ install e launch se passi il device)
make-preview.js     genera preview.html dalla stessa sorgente
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

| livello | cosa fa |
|---|---|
| **glass** (default) | vetro traslucido "cotto", orbe + nastri + polvere animati |
| **full** (opt-in) | glass + `backdrop-filter` vero |
| **static** (fallback) | tutto fermo, pannelli più opachi |

Il collo di bottiglia non è un singolo effetto: è `backdrop-filter` **sopra uno
sfondo in movimento**, insieme a `mix-blend-mode`. Quella coppia impedisce alla
GPU di promuovere i layer, quindi ogni frame rifà il blur dell'intera area.

La Home quindi **non usa blur per frame**. I pannelli sono traslucidi: gli orbe
si vedono comunque passare sotto, quindi il movimento resta — cade solo la
rifrazione, che era la parte costosa. Luce, profondità e anello di focus sono
gradienti e ombre dipinti *una volta*.

Regole rispettate in tutto il file, verificate dai test:
- si anima **solo `transform` e `opacity`**: mai il layout, mai un'ombra
- il focus accende un anello pre-disegnato via `opacity`. Transizionare
  `box-shadow` significava ripitturare il tile a ogni freccia premuta
- stessa cosa per l'alone ai bordi: due strati che si incrociano in opacity,
  invece di interpolare un'ombra grande quanto lo schermo
- la sfocatura degli orbe è *dentro* il radial-gradient, non in un `filter`;
  i nastri sfumano con un gradiente ellittico invece che con una `mask-image`,
  che costava un passaggio di composizione per frame

### Sui numeri di FPS

Le misure sono state fatte in rasterizzazione software su una macchina
condivisa, e **cinque misure della stessa identica configurazione hanno dato
da 21 a 41 FPS**. A quel livello di rumore i confronti fini non dicono nulla:
un benchmark per-livello dava "più veloce" a configurazioni con *più* roba
accesa, che è impossibile.

Regge solo il confronto grosso, ripetuto sei volte per parte:

```
glass  [22, 22, 23, 24, 24, 37]   mediana 24
full   [12, 13, 13, 13, 13, 14]   mediana 13
```

Il peggior `glass` batte il miglior `full`. È su questo che si fonda la
scelta di togliere il blur dal percorso per frame — non su una cifra precisa.
**Il numero vero si misura sulla TV**, dove la GPU è dedicata e stabile:
all'avvio la Home misura gli FPS reali, parte da `glass`, prova `full` solo se
la TV è comoda e torna indietro se non regge. Col tasto `0` decidi tu.

## Griglia

Una regola sola riempie sempre la griglia, senza celle vuote né righe
fantasma: colonne = metà dei tile arrotondata per eccesso, due righe; con un
numero dispari il primo tile occupa due colonne e i conti tornano lo stesso.
La gerarchia viene dalla riga superiore, più alta, non da un buco.

```
4 tile -> 2x2     5 -> primo largo + 4     6 -> 3x2     7 -> primo largo + 6
```

La navigazione è **spaziale**: sceglie il vicino guardando le posizioni reali
degli elementi, preferendo quelli allineati e usando un cono stretto solo
quando non ce ne sono. Il layout può cambiare forma senza toccare i tasti.

## Meteo

Open-Meteo: gratuito, senza chiave, senza registrazione. La città si cambia
con la costante `PLACE` in cima allo `<script>`. Se la rete non risponde resta
un valore d'esempio invece di un buco nel layout.

## Anteprima

`node make-preview.js` genera `preview.html` dalla stessa sorgente: identica
UI dentro una cornice 16:9 invece che a schermo intero. Un solo file da
mantenere.

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
- `PLACE` è impostato su Roma: va messa la città giusta per il meteo.
- I font arrivano da Google Fonts, quindi al primo avvio serve rete. Se la TV
  è spesso offline vanno incorporati nel pacchetto come `@font-face` base64.

## Modificare i contenuti

Tutto in cima allo `<script>` di `index.html`: `SITES` (nome, sottotitolo,
colore, glifo, url, appId) e `MODES` (etichetta, tasto colorato, colore,
elenco tile). La griglia è a 3 colonne e si adatta al numero di tile.
