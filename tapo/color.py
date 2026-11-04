"""Estrazione del colore dominante da un fotogramma.

La media semplice dei pixel non funziona: una scena meta' rossa e meta' ciano
dara' grigio, cioe' esattamente il colore che non vuoi mandare a una lampadina.
Qui si ragiona per tinta: si pesano i pixel per quanto sono vividi e luminosi,
si fa un istogramma delle tinte, si prende la piu' votata e si media solo
quella. Le scene scure o grigie ricadono su un bianco caldo invece di
restituire un colore inventato.
"""

import numpy as np

HUE_BINS = 24


def _hsv(rgb):
    """rgb float 0..1, shape (N,3) -> (hue 0..1, sat 0..1, val 0..1)."""
    mx = rgb.max(axis=1)
    mn = rgb.min(axis=1)
    d = mx - mn
    val = mx
    sat = np.where(mx > 1e-6, d / np.maximum(mx, 1e-6), 0.0)

    r, g, b = rgb[:, 0], rgb[:, 1], rgb[:, 2]
    hue = np.zeros_like(mx)
    safe = d > 1e-6
    # ramo per canale massimo, formula standard
    ir = safe & (mx == r)
    ig = safe & (mx == g) & ~ir
    ib = safe & (mx == b) & ~ir & ~ig
    hue[ir] = ((g[ir] - b[ir]) / d[ir]) % 6.0
    hue[ig] = ((b[ig] - r[ig]) / d[ig]) + 2.0
    hue[ib] = ((r[ib] - g[ib]) / d[ib]) + 4.0
    hue = hue / 6.0
    return hue, sat, val


def dominant(frame, sample=90, min_weight=0.015, saturate=1.18, floor=0.12):
    """frame: array HxWx3 uint8. Ritorna (r,g,b) interi 0..255.

    sample      lato massimo del sottocampionamento: 90 basta e tiene il costo
                costante qualunque sia la risoluzione della sorgente
    min_weight  sotto questa quantita' di colore vivido la scena e' considerata
                grigia e si ricade sul bianco caldo
    saturate    piccola spinta di saturazione: le lampadine smorzano
    floor       luminosita' minima, per non spegnere la luce sulle scene nere
    """
    a = np.asarray(frame)
    if a.ndim != 3 or a.shape[2] < 3:
        raise ValueError("serve un fotogramma HxWx3")
    a = a[:, :, :3]

    # sottocampionamento a passo: niente interpolazione, costo prevedibile
    h, w = a.shape[:2]
    step = max(1, int(max(h, w) / sample))
    small = a[::step, ::step].reshape(-1, 3).astype(np.float32) / 255.0

    hue, sat, val = _hsv(small)
    # i pixel scuri e slavati non devono decidere il colore della stanza
    weight = (sat ** 1.25) * (val ** 0.75)

    total = float(weight.mean())
    if total < min_weight:
        # scena grigia, nera o slavata: bianco caldo proporzionato alla luce
        lum = float(val.mean())
        k = max(floor, min(1.0, lum * 1.15))
        return (int(255 * k), int(214 * k), int(170 * k))

    bins = np.minimum((hue * HUE_BINS).astype(np.int32), HUE_BINS - 1)
    hist = np.bincount(bins, weights=weight, minlength=HUE_BINS)

    top = int(hist.argmax())
    # la tinta vincente piu' le due adiacenti: un rosso a cavallo di due
    # caselle non deve perdere contro un blu tutto dentro una
    keep = {(top - 1) % HUE_BINS, top, (top + 1) % HUE_BINS}
    mask = np.isin(bins, list(keep))

    wm = weight[mask]
    if wm.sum() <= 1e-6:
        mask = np.ones_like(bins, dtype=bool)
        wm = weight
    rgb = np.average(small[mask], axis=0, weights=wm)

    # riporta in HSV per ritoccare saturazione e luminosita'
    hh, ss, vv = _hsv(rgb.reshape(1, 3))
    ss = float(min(1.0, ss[0] * saturate))
    vv = float(max(floor, vv[0]))
    return _to_rgb(float(hh[0]), ss, vv)


def _to_rgb(h, s, v):
    i = int(h * 6.0) % 6
    f = h * 6.0 - int(h * 6.0)
    p, q, t = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    r, g, b = [(v, t, p), (q, v, p), (p, v, t),
               (p, q, v), (t, p, v), (v, p, q)][i]
    return (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))


class Smoother:
    """Media esponenziale, con stacco rapido sui cambi di scena.

    Senza questo la luce sfarfalla a ogni taglio di montaggio; con una media
    troppo lenta invece resta indietro di secondi quando la scena cambia
    davvero. La soglia distingue i due casi.
    """

    def __init__(self, alpha=0.12, cut=120.0, cut_alpha=0.55):
        self.alpha, self.cut, self.cut_alpha = alpha, cut, cut_alpha
        self.cur = None

    def push(self, rgb):
        rgb = np.asarray(rgb, dtype=np.float32)
        if self.cur is None:
            self.cur = rgb
        else:
            dist = float(np.linalg.norm(rgb - self.cur))
            a = self.cut_alpha if dist > self.cut else self.alpha
            self.cur = self.cur + (rgb - self.cur) * a
        return tuple(int(round(x)) for x in self.cur)


class Gate:
    """Lascia passare un aggiornamento solo se e' passato abbastanza tempo e
    il colore e' cambiato abbastanza. Le Tapo si comandano via rete: inondarle
    le fa ritardare e basta."""

    def __init__(self, min_interval=0.25, min_delta=10.0):
        self.min_interval, self.min_delta = min_interval, min_delta
        self.last_t, self.last = 0.0, None

    def allow(self, rgb, now):
        if now - self.last_t < self.min_interval:
            return False
        if self.last is not None:
            d = sum((a - b) ** 2 for a, b in zip(rgb, self.last)) ** 0.5
            if d < self.min_delta:
                return False
        self.last_t, self.last = now, rgb
        return True
