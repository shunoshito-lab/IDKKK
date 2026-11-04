# Ambilight per la striscia Tapo

Manda alla striscia dietro la TV il colore dominante di quello che sta passando.

## La tua striscia

**Tapo L900**, IP `192.168.1.10`, hardware 1.0, firmware 1.4.3.

La L900 è una striscia LED **a colore unico**: tutta la striscia prende lo
stesso colore, non ha zone. Per una luce d'atmosfera che segue la scena va
bene, ed è il caso per cui è scritto il motore (un solo colore dominante).

Python-kasa la supporta ufficialmente (L900-5 e L900-10, hardware 1.0 EU) ed
espone esattamente le chiamate usate qui: verificato su python-kasa 0.12.0.
Il loro elenco però è provato su un firmware più vecchio del tuo, quindi:

**Primo comando da lanciare, prima di tutto il resto:**

```bash
export TAPO_USER='email account Tapo' TAPO_PASS='password'
python3 ambilight.py --probe --hosts 192.168.1.10
```

La striscia fa rosso, verde, blu e torna com'era. Se lo fa, tutta la catena
fino alla luce funziona. Se dice che non risponde:

1. **Autorizza il controllo locale.** I firmware recenti di TP-Link lo
   bloccano finché non lo permetti: nell'app Tapo cerca, nel profilo, la voce
   sui servizi o la compatibilità **di terze parti** e attivala. Il nome
   esatto cambia fra versioni dell'app.
2. **Fissa l'IP.** Nel router Vodafone riserva `192.168.1.10` alla striscia
   (prenotazione DHCP), altrimenti dopo un riavvio può cambiare indirizzo.
3. Il computer che fa girare lo script deve stare sulla stessa rete.

**Lascia spenta la "Transizione graduale" nell'app.** La morbidezza la fa già
lo script; con la transizione della striscia accesa i cambi di scena
arriverebbero in ritardo.

Per non ripetere l'IP: `export TAPO_HOSTS=192.168.1.10`.

## Quello che non si può fare, e perché

**Un'app webOS non può vedere cosa c'è sullo schermo della TV.** Non esiste
un'API di cattura per le app di terze parti, e i contenuti protetti non sono
leggibili neanche dove la cattura esiste. Quindi il programma deve girare da
qualche altra parte e guardare il video *prima* che arrivi alla TV.

**Una striscia Tapo non è una strip da ambilight.** Si comanda via rete, una
chiamata per volta: realisticamente 3–5 aggiornamenti al secondo, non 60. Il risultato è
una luce d'atmosfera che segue le scene, non un ambilight che insegue ogni
fotogramma. Chi vuole la seconda cosa compra la strip.

## Come si mette in mezzo

| sorgente | cosa serve | cosa segue |
|---|---|---|
| `--source hdmi` | acquisitore HDMI (~20–40 €) tra la sorgente e la TV | **tutto** quello che passa dall'HDMI |
| `--source screen` | niente | solo ciò che riproduci da quel computer |
| `--source demo` | niente | scene finte, per provare la catena |

Con l'acquisitore HDMI resti comunque molto sotto i 200 € della strip.

## Uso

```bash
pip install numpy            # il motore
pip install mss              # per --source screen
pip install opencv-python    # per --source hdmi
pip install python-kasa      # per --out tapo

python3 ambilight.py --source demo --out print       # prova a secco, a colori
export TAPO_USER='...' TAPO_PASS='...'               # account dell'app Tapo
python3 ambilight.py --source hdmi --out tapo --hosts 192.168.1.10
```

Le credenziali stanno nell'ambiente, non sulla riga di comando: così non
finiscono nella cronologia della shell.

`--hz` limita gli invii al secondo (4 di default), `--alpha` la reattività
(0 lentissimo, 1 immediato).

## Il motore del colore

La media dei pixel non funziona: una scena metà rossa e metà ciano dà
**grigio**, cioè esattamente il colore che non vuoi mandare a una lampadina.

Qui si ragiona per tinta. Ogni pixel vota con un peso pari a quanto è vivido
e luminoso (`saturazione^1.25 · luminosità^0.75`), così il fondale nero di una
scena notturna non vince contro la fiammata rossa che la illumina. Si fa un
istogramma di 24 tinte, si prende la più votata con le due adiacenti — un
rosso a cavallo di due caselle non deve perdere contro un blu tutto dentro una
— e si media solo quella.

Le scene grigie o nere ricadono su un bianco caldo proporzionato alla
luminosità, invece di restituire un colore inventato, e non spengono mai del
tutto la luce.

Poi `Smoother` smorza: media esponenziale lenta sulle derive, stacco rapido
sopra una soglia, così i tagli di montaggio si vedono subito ma la luce non
sfarfalla. `Gate` limita gli invii per tempo e per differenza di colore:
inondare le Tapo le fa solo ritardare.

Costo: 1,1 ms per fotogramma anche in 4K, perché il sottocampionamento è a
passo fisso e il lavoro non dipende dalla risoluzione della sorgente.

## Cosa è verificato e cosa no

`python3 test_color.py` — 11 test sul motore, tutti verdi:

```
scena blu -> blu                       poco rosso su fondo nero -> rosso
rosso|ciano resta vivido               scena grigia -> bianco caldo
scena nera -> luce tenue               1080p e 360p danno lo stesso colore
cambio scena: segue subito             deriva piccola: resta ferma
100 fotogrammi in 1 s -> 3 invii       4K in 1,1 ms
```

Verificato anche: l'interfaccia di python-kasa 0.12.0 corrisponde a quella
usata (`Discover.discover_single` con credenziali, modulo `Light`,
`set_hsv`), e se la striscia non risponde `--probe` dice cosa controllare
invece di mostrare un errore Python.

**Non verificati:** la cattura (`mss`, `opencv`) e l'invio vero alla tua
striscia. Da qui la tua rete di casa non si raggiunge: è quello che
`--probe` serve a controllare in cinque secondi.
