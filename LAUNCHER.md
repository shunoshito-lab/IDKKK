# Home — launcher webOS (com.shun.launcher)

TV di riferimento: **LG 50UT73006LA, webOS 25, senza root.** Niente exploit,
niente Homebrew: solo Developer Mode ufficiale.

## Cosa c'è

```
launcher/
  index.html        la Home intera: nessuna dipendenza oltre ai font Google
  icons.js          le icone da Simple Icons (CC0), generate da make-icons.js
  logos/            i tuoi file logo, opzionali
  tennis.html       il gioco
  lib/              PeerJS e generatore QR, entrambi MIT
controller/         la pagina della racchetta, da servire in HTTPS
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
| 0 | sfondo animato / fermo |
| Indietro | torna al primo riquadro |
| M | suono acceso / spento |
| *(nel Tennis)* OK | colpisci |
| *(nel Tennis)* ◀ ▶ | mira, tenuti premuti |
| *(nel Tennis)* Indietro | torna alla Home |

Modalità, livello grafico e suono restano salvati tra un avvio e l'altro.
Dopo 4 minuti fermi resta lo sfondo con l'ora; un tasto qualsiasi sveglia, e
quel primo tasto non muove il focus.

## Suoni

Sintetizzati al volo con Web Audio: nessun file nel pacchetto, nessun ritardo
di caricamento, nessun diritto di terzi. Quattro segnali — spostamento, bordo
della griglia, cambio modalità, apertura — a volume basso. Si spengono con
`M` e la scelta resta salvata.

## Loghi

Metti i file in `launcher/logos/` e aggiungi `logo:"logos/nome.png"` alla
voce corrispondente in `SITES`. Dove non c'è un file resta il segno
disegnato, quindi puoi farne anche solo qualcuno. I file entrano nel
pacchetto da soli.

Nel pacchetto non ci sono marchi di terzi: i segni disegnati sono forme
originali.

## Resa

Regola di tutto il file: si animano **solo `transform` e `opacity`**. Ombre,
bordi di luce e alone sono disegnati una volta e si accendono in dissolvenza;
l'alone ai bordi sono due strati che si scambiano. Nessun `backdrop-filter`.

Se all'avvio la TV sta sotto i 26 fotogrammi al secondo, lo sfondo si ferma
da solo. Il tasto `0` lo decide a mano.

### Sui numeri di FPS

Le misure sono state fatte in rasterizzazione software su una macchina
condivisa, e **cinque misure della stessa identica configurazione hanno dato
da 21 a 41 FPS**. A quel livello di rumore i confronti fini non dicono nulla:
un benchmark per-livello dava "più veloce" a configurazioni con *più* roba
accesa, che è impossibile.

Reggeva solo il confronto grosso, ripetuto sei volte per parte, tra la
prima versione col vetro traslucido (`glass`) e quella con il blur vero (`full`):

```
glass  [22, 22, 23, 24, 24, 37]   mediana 24
full   [12, 13, 13, 13, 13, 14]   mediana 13
```

Il peggior `glass` batteva il miglior `full`. È da lì che viene la scelta di
non usare mai il blur per frame; l'impianto attuale non lo prevede proprio.
**Il numero vero si misura sulla TV**, dove la GPU è dedicata e stabile.

## Impianto

Da tv box: in alto lo **scaffale**, sotto i **riquadri** 16:9 delle app.

Il riquadro a fuoco si solleva, prende un bordo di luce e mostra il nome; col
puntatore del Magic Remote si inclina verso la mano. Lo scaffale racconta
l'app a fuoco: nome, una riga di descrizione e, quando ci sono, le **uscite
della settimana** con le locandine. Per le app senza uscite mostra il
riquadro in grande. Dalla seconda riga in giù lo scaffale esce e le righe
scorrono; **Indietro** riporta in cima.

Il fuoco si sposta subito; lo scaffale si aggiorna 130 ms dopo, così tenendo
premuta una freccia non si ricostruisce a ogni passo.

La navigazione è **spaziale**: sceglie il vicino guardando le posizioni reali
dei riquadri, quindi regge qualunque numero di app e l'ultima riga incompleta.

Su uno schermo verticale (l'anteprima sul telefono) la stessa pagina passa a
3 colonne e lo scaffale va in colonna.

## App

21 app, definite in `APPS` in cima allo script; le quattro modalità ne
scelgono un sottoinsieme e l'ordine in `MODES`.

**Icone.** Dieci arrivano da [Simple Icons](https://simpleicons.org)
(licenza CC0), estratte da `make-icons.js` in `launcher/icons.js`. I servizi
che nella raccolta non ci sono (Prime Video, Disney+, RaiPlay, Infinity,
Pluto TV) hanno il nome scritto sul loro colore. Un tuo file in `logos/`
vince su tutto: basta `logo:"logos/nome.png"` nella voce.

**Come si aprono.** In ordine: l'identificativo letto dalla TV, quelli
scritti in `ids`, il browser della TV sull'indirizzo `url`, e infine
l'indirizzo dentro la Home. Guardia a 3 secondi; se non c'è nemmeno un
indirizzo (ingressi HDMI, TV dal vivo) compare un avviso.

| identificativo | stato |
|---|---|
| `netflix`, `amazon` (Prime Video), `youtube.leanback.v4`, `com.apple.appletv`, `com.disney.disneyplus-prod` | confermati da fonti esterne |
| `spotify-beehive`, `tv.twitch.tv.starshot.lg`, `dazn`, `com.webos.app.livetv`, `com.webos.app.hdmi1/2`, `com.webos.app.browser` | plausibili, **non confermati** |
| RaiPlay, Infinity, Pluto TV, NOW, Paramount+, Crunchyroll, YouTube Music | nessuno: si aprono nel browser, salvo riconoscimento |

All'avvio la Home chiede alla TV l'elenco delle app installate
(`listLaunchPoints`) e riconosce le sue dal nome: se la TV lo concede, gli
identificativi diventano quelli veri di questa TV e la tabella non conta
più. Se lo nega — probabile per un'app di terze parti — restano quelli
scritti. **Da verificare sulla TV:** webOS può anche negare a un'app di terze
parti il lancio delle altre; in quel caso tutto ripiega sul browser.

Le app che non hai installato o a cui non sei abbonato si tolgono dall'elenco
della modalità in `MODES`.

## Uscite della settimana

[TVMaze](https://www.tvmaze.com/api): gratuita, senza chiave. Si leggono gli
ultimi 5 giorni di uscite in streaming (1,7 MB di JSON), si tengono solo i
servizi presenti in `APPS` e ogni serie una volta sola; il risultato ridotto
(circa 8 KB) resta in memoria 12 ore. Lo scaffale si riempie man mano che i
giorni arrivano. In una prova su cinque giorni: 8 serie per Netflix, 8 per
Prime Video, 3 per Apple TV, 5 per Paramount+.

Sono le uscite mondiali del servizio, non il catalogo italiano: qualche
titolo potrebbe non esserci in Italia. Le locandine non portano dentro l'app
al titolo: l'apertura è sempre quella dell'app.

## Meteo

Open-Meteo: gratuito, senza chiave, senza registrazione. La città si cambia
con la costante `PLACE` in cima allo `<script>`. Se la rete non risponde resta
un valore d'esempio invece di un buco nel layout.

## Anteprima

`node make-preview.js` genera `preview.html` dalla stessa sorgente: identica
UI dentro una cornice 16:9 invece che a schermo intero. Un solo file da
mantenere.

## Tennis

Tennis in stile Wii: ci si muove da soli, si sceglie solo **quando** colpire.
In anticipo tiri incrociato, in ritardo lungolinea; il telefono aggiunge forza
e mira. Troppa forza o troppo angolo e la palla esce. Si gioca contro la CPU,
vince chi arriva a 3 game, con vantaggi e parità veri.

**Col telefono:** sulla TV compare un QR; lo inquadri, tocchi "Attiva la
racchetta" e fai uno swing. Telefono e TV sulla stessa Wi-Fi. Il telefono
vibra quando colpisci, ti dice com'è venuto il colpo e mostra il punteggio.
Sensibilità regolabile (delicato / normale / sensibile) e opzione mancino.

**Col telecomando:** OK colpisce, ◀ ▶ tenuti premuti mirano. Funziona sempre,
anche se il telefono non si collega o se ne va.

### Come parlano telefono e TV

La TV non può aprire un server, quindi non si trovano da soli. **PeerJS**
(MIT) usa un servizio pubblico gratuito solo per presentarli; poi telefono e
TV si parlano diretti in WebRTC sulla rete di casa. Il telefono batte ogni
2 secondi: dopo 6 secondi di silenzio — anche per il blocco schermo, che
nessun evento di chiusura segnala — la TV torna al telecomando.

La pagina del telefono (`controller/`) deve stare in **HTTPS**, altrimenti il
browser del telefono non dà accesso ai sensori. Va servita da GitHub Pages:
`CONTROLLER_URL` in cima a `tennis.html` punta a
`https://shunoshito-lab.github.io/IDKKK/controller/`.

### Verificato

Partita col telecomando, con numeri casuali a seme fisso così l'esito è
ripetibile: punteggio con parità e vantaggi, cambio di servizio, fine
partita, scambio di 21 colpi.

Telefono↔TV, con un server PeerJS locale e due pagine vere collegate in
WebRTC (21 controlli): QR, collegamento, tocco per i sensori, uno swing = un
colpo, forza e direzione lette, anti-doppio, nessun colpo fantasma col
telefono tenuto in mano, servizio dal telefono, vibrazione, punteggio sul
telefono, mancino, ritorno al telecomando in ~6 s quando il telefono sparisce.
Dal gesto alla TV ~155 ms, di cui ~144 sono la durata del gesto simulato.

Due cose trovate dai test e corrette: un secondo swing durante l'annuncio
faceva ripartire la partita da capo; e la TV non si accorgeva del telefono
sparito, da cui il battito.

**Non verificati:** WebRTC sul browser di webOS 25 e i sensori di un
telefono vero. Se uno dei due manca, resta il telecomando.

## Da sistemare

- `PLACE` è impostato su Roma: va messa la città giusta per il meteo.
- I font arrivano da Google Fonts, quindi al primo avvio serve rete. Se la TV
  è spesso offline vanno incorporati nel pacchetto come `@font-face` base64.

## Modificare i contenuti

Tutto in cima allo `<script>` di `index.html`: `APPS` e `MODES`.
