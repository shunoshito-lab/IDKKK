# LB–1: il linguaggio di design di Lyric Box

Lyric Box v2 ("LB–1, screen & manual") unisce due riferimenti: il COTODAMA Lyric Speaker per come si guarda la musica, e Teenage Engineering per come si toccano i controlli. Questo documento spiega da dove viene ogni scelta. La ricerca di base è in [`ricerca-lyric-speaker.md`](ricerca-lyric-speaker.md).

Metodo: due ricercatori (TE, Cotodama), tre direzioni di design in competizione ("l'oggetto", "la galleria", "lo schermo e il manuale"), due giudici indipendenti (un design director e un ingegnere UX) e una sintesi in una spec unica. Hanno vinto "schermo e manuale" con entrambi i giudici. Poi c'è stata una revisione avversaria del codice.

---

## 1. Cosa rende "premium" il Lyric Speaker

Dalle recensioni e dalle pagine ufficiali:

- **Monocromo.** "There's no color" (GeekDad, Box 2022); "all grayscale" (Alphr). Alterna nero su bianco e bianco su nero, come un LCD trasparente: i pixel bianchi lasciano passare la retroilluminazione lattea, quelli neri sono opachi.
- **Toglie, non aggiunge.** Niente comandi di volume o di traccia, niente logo. GeekDad lo definisce "minimalist to the extreme". Cotodama ha rifiutato immagini e video degli utenti per tenere il focus su parole e musica (Gizmodo JP).
- **Il cambio brano è un piccolo rito.** Per una frazione di secondo compare il titolo, poi le parole.
- **La tipografia è un sistema curato.** Il Box usa **Role** (superfamiglia Morisawa guidata da Matthew Carter: Serif, Sans, Slab e Soft in tagli Text, Display e Banner). Fonte: PHILE WEB 2022 e un rivenditore; Cotodama parla solo di "una varietà di font".
- **Motion legata al mood:** calma per testi calmi, dinamica per testi energici, la più forte per il ritornello (sito ufficiale).

**In LB–1:** a riposo si vedono solo il testo, un fondo appena tinto e la grana. Il colore della copertina diventa una tinta a bassa saturazione, non un poster. C'è un tema scuro e uno "carta" (l'acrilico retroilluminato). Al cambio brano compare una card con il titolo, che sparisce quando arriva la prima riga.

## 2. Cosa è davvero Teenage Engineering (e cosa no)

Dal CSS e dai font del sito teenage.engineering (letti l'8/10/2026) e dalla guida utente dell'OP–1 field:

- **Il "look TE" che si vede in giro (monospace, `#ff6600`, maiuscole spaziate) è un'imitazione.** Il sito usa due tagli custom di Linotype Univers ("Univers TE20 Thin" e "TE40 Light"), solo ai pesi 100 e 300, in minuscolo, con tracking leggermente negativo.
- **Token reali:**

  | Token | Valore |
  |---|---|
  | arancione | `#f05a24` |
  | giallo | `#fab413` |
  | blu | `#0071bb` |
  | verde | `#006837` |
  | rosso | `#b81d13` |
  | nero | `#0f0e12` |
  | bianco | `#f5f5f5` |
  | grigi | da `#e5e5e5` a `#272727` |

  L'interfaccia del sito è quasi monocroma.
- **Griglia:** un artboard di 980 unità che scala con la larghezza dello schermo. Margini 45, gutter 10, hairline 1 unità. Sotto i 768 px i rapporti raddoppiano.
- **"Giocoso ma preciso":** il colore ha un significato. Sull'OP–1 il colore di un encoder corrisponde a quello del parametro sullo schermo. Le sezioni dei manuali sono numerate `((n))`. Le unità sono sempre esatte.
- **Gli schermi sono finestre scure dentro l'hardware**, con numeri da LCD o a segmenti (TP–7: display monocromo 64×32; EP–133: display "super segment").

**In LB–1:**

| TE | LB–1 |
|---|---|
| Univers TE20/TE40 | **Archivo** variabile (Google Fonts): pesi 100–900, larghezze 62–125, un solo file per tutti gli stili e per la UI |
| Display a matrice di punti | **Doto**: un subset di 16 glifi per le sole cifre |
| Colore = significato | arancione = tempo, blu = sync, giallo = modo, grigio = vista. Nient'altro è colorato |
| Schermo dentro l'hardware | la barra in basso ha una finestra scura sempre nera, anche in tema carta |
| `((n))` nei manuali | il menu ha quattro sezioni: ((1)) sorgente, ((2)) modo, ((3)) vista, ((4)) tasti |
| Bobina motorizzata del TP–7 | l'icona del tempo è una bobina che gira con la canzone e si ferma in pausa. Fa anche da indicatore di caricamento e da grafica per gli strumentali |
| Minuscolo, frasi brevi | tutto il testo dell'app è in italiano minuscolo, con frasi che finiscono col punto. Titoli e testi delle canzoni restano come sono |

Per i testi delle canzoni, il serif è **Fraunces 300** (fissato a SOFT 50, WONK 0) e fa la voce calma di Cotodama. Il resto lo copre Archivo:
- larghezza 100 per **kinetic**;
- larghezza 62 in maiuscolo per **impact**, al posto di Anton;
- larghezza 125, peso light e spaziato per **crawl**.

## 3. Regole del sistema

1. **Le parole sono lo schermo, i controlli sono l'hardware.** A riposo l'interfaccia visibile è zero. La barra sale solo quando muovi il mouse, tocchi o premi un tasto, e riscende dopo 2,5 s. Il tasto H la fissa o la spegne del tutto.
2. **Monocromo prima di tutto.** L'inchiostro è `#f5f5f5` su `#0f0e12`, mai bianco puro su nero puro.
3. **Un gesto per volta.** Niente blur, tilt o rotazione della camera. Le molle sono criticamente smorzate, tranne il ritornello: è l'unico punto con un rimbalzo (ζ ≈ 0,69).
4. **Leggibilità:**
   - testo cantato almeno 15:1 di contrasto su qualsiasi tinta;
   - testo non ancora cantato almeno 3,6:1;
   - testo piccolo almeno 4,5:1;
   - nessuna parola entra nella fascia della barra.
5. **Si comporta come uno strumento.** Ogni comando risponde sul posto entro 220 ms: il valore cambiato si gonfia una volta e si accende del colore della sua famiglia. I toast restano solo per gli errori.

## 4. Scelte prese contro la spec (e perché)

- **Tema scuro di default.** "Auto" (che segue il sistema operativo) resta un'opzione. La spec diceva sia "auto di default" sia "la polarità cambia solo per scelta dell'utente": ho tenuto la seconda, che è anche quella di Cotodama.
- **I due punti dell'ora in Archivo.** Quelli di Doto, a quella dimensione, sembravano un "‡".
- **Grana con fusione normale.** Con la fusione overlay su un livello a tutto schermo il framerate a 1080p si dimezzava (misurato: 30 → 60 fps in rendering software).
- **Uscita anticipata in kinetic.** La riga esce 240 ms prima dell'arrivo della successiva, così due frasi non condividono mai lo schermo. Prima si sovrapponevano per circa 170 ms; ora la nuova compare quando la vecchia è già sotto il 30%.
- **`data-lb-theme` invece di `data-theme`.** Il secondo è riservato al visualizzatore degli artifact.

## 5. Revisione avversaria

Quattro revisori indipendenti hanno lavorato su quattro aspetti: macchina a stati con Spotify e LRCLIB simulati via rete, aderenza alla spec, accessibilità e input, QA visivo. Ogni loro lista è passata da uno scettico che doveva riprodurre il problema o scartarlo: 36 problemi confermati, 1 scartato. Tutti sono stati corretti e ri-verificati con gli stessi script di riproduzione. I più importanti:

- **Spazio riapriva il menu dopo aver avviato una sorgente.** Il focus tornava al pulsante della barra; ora avviare una sorgente è un cambio di contesto.
- **La barra "spenta" chiudeva fuori gli utenti touch**, anche dopo il reload. Ora un tocco o un click la riporta su per un momento, mentre il passaggio del mouse resta ignorato (modalità proiettore).
- **Il tap che rivela la barra poteva premere il controllo sotto il dito** se durava più di 170 ms. Ora il suo click viene sempre assorbito.
- **Spotify fermo (204) lasciava il testo congelato con la bobina disegnata sopra.** Ora le righe escono e la barra si svuota; alla ripresa torna tutto, compresa la card di stato.
- **Un token revocato portava a uno schermo morto e silenzioso.** Ora l'app esce dall'account, apre il menu e lo dice. Un token che arriva dopo la disconnessione viene scartato.
- **Al cambio brano non c'era dissolvenza**: le righe sparivano subito. Ora la vecchia riga sfuma mentre la card dice "cerco.".
- **Contrasto della card agganciata in basso:** era 2,5:1 in carta, ora è 5,2:1.
- **`[` e `]` non funzionavano sulle tastiere italiane** (servono AltGr). Ora funzionano, e tenere premuto T non fa più lampeggiare il tema.
- **Telefono:** parole di cloud e crawl più larghe dello schermo, il titolo della barra ridotto a una lettera, intestazioni del menu coperte dall'header.

## 6. Prestazioni misurate

Chromium headless con rendering software (SwiftShader), quindi senza GPU. Valori mediana / 95° percentile in ms per frame:

| Stile | 1280×720 | 1920×1080 |
|---|---|---|
| drift | 16,7 / 16,7 | 16,7 / 16,8 |
| kinetic | 16,7 / 16,8 | 16,7 / 16,7 |
| impact | 16,7 / 16,8 | 16,7 / 16,7 |
| cloud | 16,7 / 16,7 | 16,7 / 16,8 |
| crawl | 16,7 / 16,7 | 16,7 / 16,8 |

Per ogni frame si scrivono solo `transform` e `opacity`. Lo sfondo è renderizzato a un terzo della risoluzione. Il canvas della bobina è grande quanto la bobina.

## Fonti principali

- teenage.engineering: home page, bundle CSS (`root.*.css`: token, artboard 980, scala tipografica), file dei font `TE20T`/`TE40L` (tabella dei nomi), [OP–1 field user guide (PDF)](https://assets.teenage.engineering/_img/69f248938d433104c4dd1846_original.pdf), pagine [TP–7](https://teenage.engineering/products/tp-7), [OB–4](https://teenage.engineering/products/ob-4), [EP–133](https://teenage.engineering/products/ep-133), [guida EP–133 sullo schermo](https://teenage.engineering/guides/ep-133/screen)
- Cotodama: [sito](https://cotodama-speaker.com/), [our story](https://cotodama-speaker.com/pages/our-story), [FAQ](https://cotodama-speaker.com/pages/faq), [collaborazione con Pauly](https://cotodama-speaker.com/pages/pauly-x-cotodama-speaker)
- Recensioni: [GeekDad](https://geekdad.com/2022/03/geekdad-review-cotodama-lyric-speaker-box/), [Alphr](https://www.alphr.com/speakers/1007952/cotodama-lyric-speaker-review-never-forget-the-lyrics-for-a-price/), [Gizmodo JP](https://www.gizmodo.jp/article/lyric-speaker-canvas/), [moov.ooo](https://moov.ooo/article/587730eb62fd2623a8c2fbea), [Sound & Vision](https://www.soundandvision.com/content/wireless-speaker-visualizes-lyrics-real-time), [audioXpress](https://audioxpress.com/news/cotodama-lyric-speaker-is-world-s-first-lyric-visualizing-speaker), [Display Daily](https://displaydaily.com/introducing-the-cotodama-lyric-speaker/)
- Font: [Archivo](https://fonts.google.com/specimen/Archivo), [Fraunces](https://fonts.google.com/specimen/Fraunces), [Doto](https://fonts.google.com/specimen/Doto) su Google Fonts
