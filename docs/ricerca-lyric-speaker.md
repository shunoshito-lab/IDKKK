# Lyric Speaker × Spotify: ricerca

Come funziona il COTODAMA Lyric Speaker, che linguaggio di design usa, cosa permette davvero Spotify nel 2026 e come si fanno animazioni di testo fluide sul web. Alla fine c'è l'architettura del prototipo in [`lyric-box/`](../lyric-box/).

Data della ricerca: 8 ottobre 2026. Le fonti sono in fondo. Dove una cosa è una mia deduzione e non un fatto documentato, lo scrivo.

---

## 0. In breve

- **Cotodama non ha mai pubblicato l'algoritmo.** Il prodotto è documentato solo a livello di marketing, recensioni e qualche intervista. Il funzionamento si può ricostruire abbastanza bene: testi sincronizzati con licenza (SyncPower/PetitLyrics), analisi del *testo* (non dell'audio) fatta con tecnologia dell'istituto di ricerca giapponese AIST per stimarne l'"impressione" (il mood) e trovare il ritornello, poi un "expression engine" che sceglie font e famiglia di motion.
- **Spotify non ti dà i testi.** Non esiste un endpoint lyrics pubblico. Dal 27/11/2024 le app nuove non hanno nemmeno `audio-features` e `audio-analysis` (quindi niente beat, sezioni, energy, valence). Da febbraio 2026 la Development Mode richiede che il proprietario dell'app abbia Premium e limita l'app a 5 utenti. Spotify ti dice solo **cosa** suona e **a che punto** (`/me/player/currently-playing`).
- **I testi sincronizzati si prendono da LRCLIB** (gratis, senza chiave, CORS aperto). Musixmatch è la via commerciale, a pagamento. Il timing parola per parola è raro: nella pratica va stimato.
- **L'audio di Spotify nel browser non si può analizzare** (DRM/EME: un `AnalyserNode` riceve silenzio). Il ritmo lo ricavi dai timestamp dei testi: le parole tendono a cadere sul beat.
- **Animazioni fluide** = un solo loop `requestAnimationFrame`, solo `transform`/`opacity` (e con cautela `filter`), molle fisiche invece di durate fisse, smoothing indipendente dal frame rate, clock della canzone estrapolato localmente e corretto gradualmente.

---

## 1. Cos'è il Lyric Speaker e come è fatto

### Azienda e prodotti

- **COTODAMA** nasce a Tokyo nel 2016 come società collegata all'agenzia creativa **SIX inc.** Il CEO, Jin Saito, è anche direttore creativo di SIX. Il nome viene da *kotodama*, "lo spirito che abita le parole" ([BCN+R](https://www.bcnretail.com/market/detail/20210731_237104.html), [Hypebeast](https://hypebeast.com/2025/8/pauly-cotodama-lyric-speaker-collaboration-interview)).
- Modelli: Lyric Speaker originale (circa 2017–2018, display trasparente, intorno a $4.500), **Canvas** (2019), **Box** (2022, intorno a $1.000, cassa in acrilico) e una lunga serie di collaborazioni con artisti e brand: Pauly, Dr.Woo, Geoff McFetridge, mastermind JAPAN, Yohji Yamamoto, Mika Ninagawa, HERALBONY (2026) ([sito ufficiale](https://cotodama-speaker.com/), [Forbes 2018](https://www.forbes.com/sites/bradmoon/2018/02/13/cotodama-lyric-speaker-review-4500-for-a-wireless-speaker-thats-a-multimedia-art-installation/), [Forbes 2022](https://www.forbes.com/sites/bradmoon/2022/07/07/review-cotodama-lyric-speaker-box-wi-fi-speaker/)).
- La parte acustica è progettata da **Tom's Lab**. Abbey Road Red (l'incubatore di Abbey Road Studios) ha dato consulenza sul suono ([sito](https://cotodama-speaker.com/), [BCN+R](https://www.bcnretail.com/market/detail/20210731_237104.html)).
- Saito racconta che hanno costruito **prima il software, poi l'hardware** ([BCN+R](https://www.bcnretail.com/market/detail/20210731_237104.html)). Lo stesso motore gira anche fuori dallo speaker: in **rekordbox lyric** di Pioneer DJ (2018) e nelle scenografie di concerti ([Pioneer DJ](https://www.pioneerdj.com/ja-jp/news/2018/rekordbox-lyric-japan/)).

### La pipeline (ricostruita)

```
brano in riproduzione (Wi-Fi: app/streaming)
        │
        ▼
testo sincronizzato con licenza ─── SyncPower / PetitLyrics (milioni di brani, royalty agli autori)
        │
        ▼
analisi del TESTO (tecnologia AIST)
  ├─ stima dell'"impression space" (che sensazione dà il testo)
  └─ rilevamento del ritornello dal testo (ISMIR 2020)
        │
        ▼
"expression engine" / Lyric Sync Technology
  └─ sceglie font + famiglia di motion + intensità, per sezione
        │
        ▼
rendering sul display (trasparente nel modello originale)
  └─ niente testo o brano strumentale → grafica geometrica a tempo
```

Cosa dicono le fonti, punto per punto:

1. **Testi.** Lo speaker non trascrive l'audio: cerca il brano in un database online. Quello di **SyncPower (PetitLyrics)** era dato a più di 2 milioni di brani nel 2018. Oggi il sito ufficiale dichiara più di 15 milioni di brani in più di 40 lingue, con royalty pagate agli autori tramite le società di gestione dei diritti ([Forbes 2018](https://www.forbes.com/sites/bradmoon/2018/02/13/cotodama-lyric-speaker-review-4500-for-a-wireless-speaker-thats-a-multimedia-art-installation/), [sito](https://cotodama-speaker.com/)).
2. **Mood.** Il motore "stima l'*impression space* a partire dal testo" e sceglie motion e font di conseguenza. Il sito parla di "collaborazione tecnica con AIST". La stampa giapponese cita esplicitamente la tecnologia di **stima dell'impressione dei testi** di AIST ([sito](https://cotodama-speaker.com/), [PHILE WEB 2022](https://www.phileweb.com/sp/news/d-av/202208/22/56202.html)). Le prime recensioni parlano anche di tempo e mood della canzone ([Display Daily](https://displaydaily.com/introducing-the-cotodama-lyric-speaker/)).
3. **Ritornello.** Dal modello Box in poi lo speaker rileva il ritornello **dal testo** e cambia motion. Questo deriva dal paper di Kento Watanabe e Masataka Goto (AIST), *A Chorus-Section Detection Method for Lyrics Text*, ISMIR 2020 ([paper](https://program.ismir2020.net/poster_3-04.html)). Come funziona:
   - è un sequence labeling (una rete neurale) sulle righe del testo, che sfrutta soprattutto **le ripetizioni** e indizi linguistici;
   - i dati di addestramento li hanno generati facendo girare un rilevatore di ritornelli *audio* su canzoni con testi allineati, e proiettando gli intervalli sulle righe;
   - un modello addestrato su testi giapponesi funziona sorprendentemente bene anche sull'inglese: **gli schemi di ripetizione non dipendono dalla lingua**;
   - la versione estesa è uscita su IEICE Transactions nel 2023 ([PDF](https://staff.aist.go.jp/m.goto/PAPER/TIEICE202309watanabe.pdf)).
4. **Mappatura.** Testo calmo → motion calma. Testo che dà energia → motion dinamica. **Ritornello → motion più potente** ([PHILE WEB 2026](https://www.phileweb.com/news/d-av/202608/05/65718.html), [mikeshouts](https://mikeshouts.com/cotodama-lyric-speaker-analyzes-songs-mood-and-displays-lyrics/)). Una ballata ha font "morbidi" e movimenti dolci, un pezzo rock ha lettering pesante e aggressivo.
5. **Fallback.** Per gli strumentali, o se il testo manca, lo speaker mostra **grafiche astratte che si muovono a ritmo** ([Digital Trends](https://www.digitaltrends.com/home-theater/cotodama-lyric-review/)).
6. **Origine accademica.** La valutazione intermedia del progetto JST ACCEL di Goto (2016–2020) cita, tra i risultati, uno speaker che mostra i testi sincronizzati con la musica ([JST](https://www.jst.go.jp/kisoken/accel/evaluation/mid-term/mid-term_h28_2.pdf)). Lo stesso gruppo ha creato **TextAlive** (vedi §3).

**Cosa non si sa:** quanti template di motion esistono, come vengono parametrizzati, come si combina il mood con il tempo del brano. Nessuna fonte lo documenta. Tutto quello che scrivo sotto su questi punti è una ricostruzione.

---

## 2. Il linguaggio di design

Questi sono i "tipi di design" che usa, ricavati da recensioni, comunicati e interviste.

### 2.1 La parola come oggetto d'arte
Saito collega il prodotto alla tradizione giapponese di apprezzare le parole in sé: lo *shodō* (la calligrafia) e i *kakejiku* (i rotoli appesi con una frase che ami). Il manifesto è: "uno strumento che amplifica le parole dei testi per fartici fare il bagno dentro" ([BCN+R](https://www.bcnretail.com/market/detail/20210731_237104.html)). Ne seguono alcune scelte:
- la tipografia è la protagonista, non un sottotitolo;
- niente UI, niente box: solo testo e spazio negativo;
- poco testo alla volta.

### 2.2 Il display trasparente
Nel modello originale il testo galleggia su un pannello LCD trasparente retroilluminato, davanti alla stanza. Rende di più con poca luce ([Forbes 2018](https://www.forbes.com/sites/bradmoon/2018/02/13/cotodama-lyric-speaker-review-4500-for-a-wireless-speaker-thats-a-multimedia-art-installation/)). **Sul web:** sfondo scuro e vivo (non nero piatto), vignettatura, nessun contenitore attorno alle parole, grana leggera.

### 2.3 Famiglie di motion osservate
Dalle recensioni ([Forbes Canvas 2019](https://www.forbes.com/sites/bradmoon/2019/04/19/cotodama-lyric-speaker-canvas-review-music-words-art/), [Digital Trends](https://www.digitaltrends.com/home-theater/cotodama-lyric-review/)):
- **word cloud**: le parole si accumulano sullo schermo (bello, ma difficile da cantare);
- **testo che attraversa lo schermo in diagonale**;
- **crawl**: scorrimento continuo che esce dallo schermo;
- **drift**: lettere che fluttuano piano, nelle ballate;
- secondo una recensione, il pop e il rock "rendono meglio" perché i cantanti stanno più sul beat e i tempi sono moderati. Indizio importante: **il timing delle parole È il ritmo visivo**.

Natalie titolava un evento con Sukima Switch: "tecnologia capace di esprimere anche *l'interlinea e i paragrafi*" ([Natalie](https://natalie.mu/music/news/308060)). In altre parole, la struttura del testo (strofe, pause) è usata come materiale compositivo.

### 2.4 La tipografia è curata, non scelta a caso
- Il Box del 2022 usa il font **Role**, progettato con **Matthew Carter** come designer principale ([PHILE WEB 2022](https://www.phileweb.com/sp/news/d-av/202208/22/56202.html)).
- Le collaborazioni aggiungono **font scritti a mano**: la modalità "Pauly Font" usa la grafia dell'artista (2025, [Hypebeast](https://hypebeast.com/2025/8/pauly-cotodama-lyric-speaker-collaboration-interview)), il modello HERALBONY (2026) quella di Shota Matsuda ([PHILE WEB 2026](https://www.phileweb.com/news/d-av/202608/05/65718.html)).
- Il risultato è un sistema a "modalità" in cui il font fa parte dell'identità del preset.

### 2.5 Personalizzazione limitata e sensata
In rekordbox lyric puoi cambiare tonalità di colore e tipo di grafica, font, colore e trasparenza dello sfondo ([Pioneer DJ](https://www.pioneerdj.com/ja-jp/news/2018/rekordbox-lyric-japan/)). Il motore decide, l'utente rifinisce.

### 2.6 Base teorica: kinetic typography ed emozioni
Non è roba di Cotodama, ma è la letteratura su cui poggia questo tipo di design:
- **Lee, Forlizzi, Hudson (CMU)**, *The Kinetic Typography Engine* (UIST 2002) e *Using kinetic typography to convey emotion…* (DIS 2006) ([progetto](https://www.cs.cmu.edu/~johnny/kt)).
- Uno studio coreano su effetti di kinetic typography predefiniti ha trovato che dimensione, trasparenza, direzione, ampiezza del movimento, velocità e accelerazione influenzano l'**energia** percepita, mentre trasparenza, direzione, regolarità e velocità influenzano il **mood** ([KoreaScience](https://koreascience.kr/article/JAKO201409864556113.do)).
- AIST/Kyoto hanno lavorato sulla **traiettoria d'impressione** di un brano: valori di valence/arousal frase per frase, calcolati da testo e audio sul piano V-A di Russell (fonte trovata via ricerca, paper IPSJ "歌詞と音響特徴量を用いた楽曲の印象軌跡推定").

Da qui la tabella che uso nel prototipo:

| Impressione | Dimensione | Movimento | Molla | Font | Effetti |
|---|---|---|---|---|---|
| Calma, arousal basso | media | poco, lento, verso l'alto | morbida, ζ≈1 | serif leggero (Fraunces 300) | blur→fuoco, glow sulle note tenute |
| Dinamica, arousal medio/alto | grande | pop-in per parola | rimbalzante, ζ≈0,55 | grotesk nero (Inter Tight 800) | stagger, rotazioni piccole che si azzerano |
| Ritornello | enorme, una parola alla volta | slam + camera shake | dura, ζ≈0,57 | condensed (Anton) | flash dello sfondo, riga intera piccola sotto |
| Ritornello di un pezzo calmo | mista | le parole si posano e restano | rimbalzante | serif corsivo + grotesk | word cloud che si attenua con l'età |
| Valence negativa | grande, inclinato | scorrimento continuo | — (damping) | grotesk light spaziato | ticker diagonale |

---

## 3. TextAlive: il "fratello aperto" del Lyric Speaker

Stesso gruppo di AIST (Masataka Goto, Jun Kato). **TextAlive** (2015) è un editor di video di kinetic typography sincronizzati con la musica. La **TextAlive App API** (CHI 2023, honorable mention) è un'API JavaScript per fare "lyric app" web: dà il timing **di ogni carattere**, più beat, accordi e sezioni, per i brani registrati sulla piattaforma (soprattutto vocaloid e J-pop) ([GitHub](https://github.com/TextAliveJp/textalive-app-api), [paper](https://dl.acm.org/doi/full/10.1145/3544548.3580931)).

**Perché ti interessa:** è l'unico posto dove trovi gratis timing per carattere più analisi musicale, quindi è ottimo per studiare animazioni per-glifo. Non copre però il catalogo Spotify.

---

## 4. Spotify nel 2026: cosa puoi e non puoi fare

| Cosa | Stato |
|---|---|
| Endpoint per i testi | **Non esiste.** Lo staff di Spotify lo ha detto più volte ([community](https://community.spotify.com/t5/Spotify-for-Developers/API-to-get-Track-s-Lyrics/td-p/5981895)). I testi nel client vengono da Musixmatch, con licenza. |
| `audio-features`, `audio-analysis` (beat, sezioni, energy, valence) | **Bloccati per le app create dopo il 27/11/2024** ([TechCrunch](https://techcrunch.com/2024/11/27/spotify-cuts-developer-access-to-several-of-its-recommendation-features)) |
| Development Mode (da febbraio 2026) | Il proprietario dell'app deve avere **Premium**. Max **5 utenti** per app. Alcuni endpoint rimossi (batch fetch, browse, top track degli artisti, ecc.). `limit` della search ridotto a 10 ([blog Spotify](https://developer.spotify.com/blog/2026-02-06-update-on-developer-access-and-platform-security), [migration guide](https://developer.spotify.com/documentation/web-api/tutorials/february-2026-migration-guide), [TechCrunch](https://techcrunch.com/2026/02/06/spotify-changes-developer-mode-api-to-require-premium-accounts-limits-test-users/)). Da luglio 2026 il limite è di 25 Client ID per sviluppatore, con quota condivisa. |
| Extended Quota | Dal maggio 2025 solo per organizzazioni registrate con almeno 250k utenti attivi mensili. Per te: no. |
| OAuth | **Solo Authorization Code + PKCE.** L'implicit grant è morto il 27/11/2025. Niente redirect su `localhost`: usa **`http://127.0.0.1:PORTA`** oppure https ([blog](https://developer.spotify.com/blog/2025-02-12-increasing-the-security-requirements-for-integrating-with-spotify), [redirect URI](https://developer.spotify.com/documentation/web-api/concepts/redirect_uri)) |
| `GET /me/player/currently-playing` | **Disponibile.** Scope `user-read-currently-playing`. Restituisce `progress_ms`, `is_playing`, `timestamp`, `item.duration_ms`, `album.images`, `external_ids.isrc` ([reference](https://developer.spotify.com/documentation/web-api/reference/get-the-users-currently-playing-track)) |
| Web Playback SDK | Serve Premium. L'audio passa per EME/DRM: **un `AnalyserNode` riceve silenzio**, quindi niente FFT ([Web Playback SDK](https://developer.spotify.com/documentation/web-playback-sdk), [EME](https://web.dev/articles/eme-basics)) |
| Termini d'uso | La reference di Spotify dice che la piattaforma non può essere usata per "sincronizzare registrazioni sonore con media visivi" né per integrazioni commerciali di streaming. **Un progetto personale da 5 utenti è una cosa, un prodotto è un'altra.** Cotodama ha accordi e licenze, tu no. Non è consulenza legale, ma non farci un business senza parlarne con qualcuno che lo è. |
| API non ufficiali (cookie `sp_dc` per prendere i testi Musixmatch da Spotify) | Esistono ([esempio](https://github.com/akashrchandran/spotify-lyrics-api)), ma lo dicono loro stessi: violano i ToS. Sconsigliate. |

### Fonti di testi sincronizzati

| Fonte | Sync | Costo | Note |
|---|---|---|---|
| **LRCLIB** ([lrclib.net](https://lrclib.net), [repo](https://github.com/tranxuanthang/lrclib)) | per riga, a volte per parola | gratis, senza chiave | `GET /api/get?track_name&artist_name&album_name&duration` (tolleranza ±2 s) e `GET /api/search`. **CORS `*`**, quindi funziona direttamente dal browser. Il mio test del 08/10/2026 ha trovato nella risposta i campi `syncedLyrics` (LRC), `plainLyrics`, `instrumental`, `duration`, **`hasWordSync`** e **`lyricsfile`** (YAML con `start_ms`/`end_ms` per riga). Su 6 hit pop cercati, nessuno aveva `hasWordSync: true`. |
| **Musixmatch** | per riga; "richsync" per parola | a pagamento | La via legale per un prodotto vero. Prezzi su contratto ([docs](https://docs.musixmatch.com/lyrics-api)) |
| **AMLL TTML DB** | per parola (TTML) | community | Testi word-timed fatti a mano dalla community di AMLL |
| **TextAlive** | per carattere | gratis | Solo i brani registrati sulla piattaforma |

**Matching:** pulisci il titolo (" - Remastered 2011", "(feat. …)", " - Live"), usa il primo artista, passa la `duration` e, se il get fallisce, cerca e scegli il risultato con la durata più vicina. L'ISRC (`external_ids.isrc`) è utile se la fonte lo supporta.

---

## 5. Sincronizzazione: il clock

Spotify ti dà la posizione solo quando fai polling. Tra un poll e l'altro la stimi tu.

1. **Polling** ogni ~1 s mentre suona, ~2–2,5 s in pausa. Accelera vicino alla fine del brano per agganciare subito il pezzo successivo. Rispetta `Retry-After` sui 429. Fermati quando la tab è nascosta.
2. **Estrapolazione**: `pos = progress_ms + rtt/2 + (performance.now() − ricevuto)`.
3. **Slew, non jump**: se la differenza è piccola (sotto ~900 ms) la assorbi in modo esponenziale in qualche centinaio di ms. Così il riempimento delle parole non scatta.
4. **Seek detection**: differenza grande, oppure passaggio play/pausa → resetti la scena. AMLL usa una tolleranza di jitter di 150 ms, una drift slack del 50% e un gap massimo di cui fidarsi di 800 ms (codice di `seek-detector.ts`).
5. **Offset manuale** (←/→): gli LRC della community sono spesso sfasati di 100–300 ms. Serve una manopola.
6. **Timing stimato per parola** (quando hai solo le righe): distribuisci la durata della riga per peso sillabico, aggiungendo un po' di "hold" sulle parole prima della punteggiatura. Limita lo span cantato: nelle ballate la riga successiva arriva molto dopo che hai finito di cantare quella attuale.

---

## 6. Animazioni web fluide: teoria e pratica

### 6.1 La pipeline del browser
Per ogni frame il browser fa: style → layout → paint → composite.
- **Anima solo `transform` e `opacity`**: girano sul compositor senza rifare layout e paint. Oggi anche `filter` e `clip-path` sono accettabili, con moderazione ([Motion](https://motion.dev/docs/feature-comparison)).
- **Non animare** `top`/`left`/`width`/`font-size`/`font-weight`/`letter-spacing`: causano layout a ogni frame. Per far "respirare" un font variabile conviene `scale` più il cambio di peso a scatti, oppure passare a canvas/WebGL.
- **Misura il testo una volta sola**, quando la riga entra in scena, mai dentro il loop. Se devi misurare tanto testo senza reflow c'è **Pretext** (Cheng Lou, marzo 2026, MIT, ~15 KB): misura via canvas e fa il layout come aritmetica ([LogRocket](https://blog.logrocket.com/pretext-laying-out-ui-without-css/)).
- `will-change: transform` solo sugli elementi che animano davvero: ogni layer costa memoria GPU.
- `blur()` grandi, `backdrop-filter` a tutto schermo e `text-shadow` animati costano paint. Il glow lo faccio con `drop-shadow` solo sulle parole tenute a lungo. **Misurato sul prototipo** (Chromium headless, rendering software): con il blur sulle parole a tutto schermo del ritornello si scende da 60 a 30 fps di mediana; senza blur si torna a 60. Sulle parole giganti usa solo scala e opacità.
- Uno **sfondo a bassa frequenza** (gradienti) si può renderizzare a 1/3 della risoluzione e scalare via CSS: non si nota e costa un nono.

### 6.2 Un solo loop, tempo vero
- Un solo `requestAnimationFrame` per tutto. `dt` limitato a ~50 ms, così dopo un freeze non salta tutto.
- **Tutto si calcola dal tempo della canzone**, non contando i frame: il riempimento della parola è `(t − start)/(end − start)`. A 30, 60 o 144 Hz il risultato è identico.
- **Smoothing indipendente dal frame rate.** `x += (target − x)·0.1` è sbagliato: dipende dagli fps. Quello giusto è
  `x = target + (x − target)·exp(−λ·dt)`
  ([Freya Holmér, "Lerp smoothing is broken"](https://acegikmo.substack.com/p/lerp-smoothing-is-broken)). Valori di λ tra 1 e 25 coprono tutto, da "pigro" a "scattante".

### 6.3 Molle invece di durate
Una molla ha massa *m*, rigidità *k* e smorzamento *c*. Il numero che conta è il **rapporto di smorzamento**:

```
ζ = c / (2·√(k·m))      ζ<1 rimbalza · ζ=1 critico (il più veloce senza overshoot) · ζ>1 pigro
```

Le molle si interrompono bene: se cambi target a metà, la velocità si conserva e non ci sono "scatti". Le durate fisse non lo fanno. Integrazione: Euler semi-implicito a sotto-passi fissi (1/240 s), stabile anche con molle rigide a frame rate bassi.

**Lezioni dal codice di AMLL** (Apple Music-like Lyrics, l'open source più curato in materia; letto dalla source map di `@applemusic-like-lyrics/core@0.6.0`):
- Posizione verticale delle righe: `m 0.9, c 15, k 90` (ζ≈0,83). Scala: `m 2, c 25, k 100` (ζ≈0,88). X: `m 1, c 10, k 100` (ζ=0,5).
- **Molla adattiva al ritmo**: in riproduzione normale l'intervallo tra una riga e la precedente (100–800 ms) viene mappato in modo inverso, con esponente 0,2, su una stiffness di 170–220, con `damping = 2.2·√k`. Nota che con *m*=1 questo dà **ζ = 1,1 costante**: cambia la velocità, mai il carattere (nessun overshoot). Righe ravvicinate scorrono più veloci. In seek e interludi usa una molla lenta (k 90, c 15).
- **Enfasi delle parole lunghe**: per ogni carattere, scala `1 + 0.1·amount`, piccolo spostamento verso l'alto, cascata tra i caratteri e glow. `amount` cresce con la durata (`du/2000`, cubico sotto 1 e radice sopra, ×0,6, max 1,2). Sull'ultima parola della riga l'effetto è più forte.
- **Riempimento**: `mask-image` a gradiente lineare con una zona di sfumatura, fatto scorrere col progresso. Io uso la variante `background-clip: text` con `--p`.
- **Sfondo**: mesh gradient a patch di Hermite bicubiche (l'approccio di Apple Music, [Moving Parts](https://movingparts.io/gradient-meshes)), con palette estratta dalla copertina (k-means/octree).
- Licenza **AGPL-3.0**: studialo, non copiarlo dentro un prodotto chiuso.

### 6.4 Strumenti

| Strumento | Quando |
|---|---|
| **CSS + molle tue** (come nel prototipo) | Zero dipendenze, controllo totale, perfetto per poche decine di elementi |
| **GSAP 3.13+** ([blog](https://gsap.com/blog/3-13/), [Webflow](https://webflow.com/blog/gsap-becomes-free)) | Dal 2025 è **gratis, anche per uso commerciale, con tutti i plugin**. `SplitText` riscritto: metà del peso, accessibile, con masking. Timeline potentissime. |
| **Motion** ([motion.dev](https://motion.dev/docs/feature-comparison)) | Motore ibrido: usa la Web Animations API (accelerata dall'hardware) quando può e compila le molle in `linear()` |
| **CSS `linear()`** ([Chrome](https://developer.chrome.com/docs/css-ui/css-linear-easing-function), [Josh Comeau](https://joshwcomeau.com/animation/linear-timing-function)) | Molle e rimbalzi in puro CSS, campionati. Chrome/Edge 113, Firefox 112, Safari 17.2 |
| **View Transitions API** | Cambi di "modalità" e di schermata con crossfade gratis |
| **PixiJS / three.js + troika-three-text** ([npm](https://npmjs.com/package/troika-three-text)) | Centinaia di parole, effetti per glifo in vertex shader (testo SDF), particelle. È il passo successivo se il DOM non basta. |
| **AMLL** | Riferimento per lo stile Apple Music, con React/Vue binding |

### 6.5 Ritmo senza audio
Non puoi analizzare l'audio di Spotify, quindi:
- ogni **inizio di parola** diventa un piccolo impulso (flash dello sfondo, kick alla camera);
- l'**energia** di una riga = sillabe/secondo più un lessico di arousal;
- il **ritornello** si rileva dalla ripetizione delle righe (l'indizio principale del paper ISMIR 2020).

Il risultato sembra "a tempo" perché i cantanti cadono sul beat.

### 6.6 Accessibilità e buone maniere
- `prefers-reduced-motion`: niente shake, blur e rotazioni, solo molle critiche.
- Tab nascosta: stop al polling e al rendering. Al ritorno, risincronizzazione.
- Contrasto: sfondo scurito (la luminosità dei colori della palette è limitata a ≤0,36), testo quasi bianco.

---

## 7. Architettura del prototipo (`lyric-box/index.html`)

```
Spotify (PKCE) ──poll 1s──▶ clock (estrapola + slew + seek detect)
      │ item cambiato                          │ t (ms)
      ▼                                        ▼
LRCLIB get/search ─▶ parse LRC/eLRC ─▶ timing parole ─▶ expression engine
copertina ─▶ k-means palette               (ritornello, energia/valence per riga,
                                             sezioni, stile per sezione)
                                               │
                     ┌─────────────────────────┴───────────────────────┐
                     ▼                                                 ▼
          stili DOM con molle                              sfondo WebGL a 1/3 di risoluzione
   drift · kinetic · impact · cloud · crawl                (blob di palette + domain warp)
                     │                                     + layer geometrico (strumentali)
                     └──── word onset ─▶ pulse/shake ──────────────────┘
```

Per lanciarlo vedi [`lyric-box/README.md`](../lyric-box/README.md).

### Cosa manca (roadmap sensata)
1. **Mood migliore**: sostituire il mini-lessico con un LLM che dia valence/arousal per riga e il ritornello (con cache per brano). È la versione 2026 della stima d'impressione di AIST.
2. **Timing vero per parola**: leggere il `lyricsfile` di LRCLIB quando `hasWordSync` è true, poi Musixmatch richsync se diventi serio.
3. **Font per modalità**: font scritti a mano (alla Pauly) come preset caricabili.
4. **Canvas/WebGL per il testo** (troika o Pixi) quando vuoi effetti per glifo su tante parole.
5. **Microfono** (`getUserMedia`) come sorgente di beat opzionale, visto che l'audio dello stream non è accessibile.

---

## Fonti

**Cotodama**
- Sito ufficiale: https://cotodama-speaker.com/
- BCN+R, intervista a Jin Saito (2021): https://www.bcnretail.com/market/detail/20210731_237104.html
- Forbes, Lyric Speaker (2018): https://www.forbes.com/sites/bradmoon/2018/02/13/cotodama-lyric-speaker-review-4500-for-a-wireless-speaker-thats-a-multimedia-art-installation/
- Forbes, Canvas (2019): https://www.forbes.com/sites/bradmoon/2019/04/19/cotodama-lyric-speaker-canvas-review-music-words-art/
- Forbes, Box (2022): https://www.forbes.com/sites/bradmoon/2022/07/07/review-cotodama-lyric-speaker-box-wi-fi-speaker/
- Digital Trends, hands-on: https://www.digitaltrends.com/home-theater/cotodama-lyric-review/
- Display Daily: https://displaydaily.com/introducing-the-cotodama-lyric-speaker/
- mikeshouts: https://mikeshouts.com/cotodama-lyric-speaker-analyzes-songs-mood-and-displays-lyrics/
- Hypebeast, collaborazione Pauly (2025): https://hypebeast.com/2025/8/pauly-cotodama-lyric-speaker-collaboration-interview
- PHILE WEB, Box/Role di Matthew Carter (2022): https://www.phileweb.com/sp/news/d-av/202208/22/56202.html
- PHILE WEB, HERALBONY (2026): https://www.phileweb.com/news/d-av/202608/05/65718.html
- Pioneer DJ, rekordbox lyric (2018): https://www.pioneerdj.com/ja-jp/news/2018/rekordbox-lyric-japan/
- Natalie, evento con Sukima Switch: https://natalie.mu/music/news/308060

**Ricerca (AIST e kinetic typography)**
- Watanabe & Goto, ISMIR 2020: https://program.ismir2020.net/poster_3-04.html · PDF: https://program.ismir2020.net/static/final_papers/88.pdf
- Versione IEICE 2023: https://staff.aist.go.jp/m.goto/PAPER/TIEICE202309watanabe.pdf
- JST ACCEL, valutazione intermedia: https://www.jst.go.jp/kisoken/accel/evaluation/mid-term/mid-term_h28_2.pdf
- TextAlive App API: https://github.com/TextAliveJp/textalive-app-api · Lyric App Framework (CHI 2023): https://dl.acm.org/doi/full/10.1145/3544548.3580931
- CMU Kinetic Typography: https://www.cs.cmu.edu/~johnny/kt
- Effetti di kinetic typography ed emozioni: https://koreascience.kr/article/JAKO201409864556113.do

**Spotify e testi**
- Spotify, Developer Mode febbraio 2026: https://developer.spotify.com/blog/2026-02-06-update-on-developer-access-and-platform-security
- Migration guide febbraio 2026: https://developer.spotify.com/documentation/web-api/tutorials/february-2026-migration-guide
- TechCrunch 2026: https://techcrunch.com/2026/02/06/spotify-changes-developer-mode-api-to-require-premium-accounts-limits-test-users/
- TechCrunch 2024 (audio features): https://techcrunch.com/2024/11/27/spotify-cuts-developer-access-to-several-of-its-recommendation-features
- OAuth/PKCE: https://developer.spotify.com/blog/2025-02-12-increasing-the-security-requirements-for-integrating-with-spotify · https://developer.spotify.com/documentation/web-api/concepts/redirect_uri
- Currently playing: https://developer.spotify.com/documentation/web-api/reference/get-the-users-currently-playing-track
- Web Playback SDK: https://developer.spotify.com/documentation/web-playback-sdk
- Community, nessuna API per i testi: https://community.spotify.com/t5/Spotify-for-Developers/API-to-get-Track-s-Lyrics/td-p/5981895
- LRCLIB: https://lrclib.net · https://github.com/tranxuanthang/lrclib
- Musixmatch Lyrics API: https://docs.musixmatch.com/lyrics-api
- EME: https://web.dev/articles/eme-basics

**Animazione**
- AMLL: https://github.com/amll-dev/applemusic-like-lyrics · Gradient meshes: https://movingparts.io/gradient-meshes
- Freya Holmér, Lerp smoothing is broken: https://acegikmo.substack.com/p/lerp-smoothing-is-broken
- CSS `linear()`: https://developer.chrome.com/docs/css-ui/css-linear-easing-function · https://joshwcomeau.com/animation/linear-timing-function
- Motion: https://motion.dev/docs/feature-comparison
- GSAP 3.13: https://gsap.com/blog/3-13/ · https://webflow.com/blog/gsap-becomes-free · SplitText: https://gsap.com/docs/v3/Plugins/SplitText/
- troika-three-text: https://npmjs.com/package/troika-three-text
- Pretext: https://blog.logrocket.com/pretext-laying-out-ui-without-css/
