#!/usr/bin/env python3
"""Manda alle lampadine Tapo il colore dominante di una sorgente video.

    python3 ambilight.py --source demo   --out print        # prova a secco
    python3 ambilight.py --source screen --out print
    python3 ambilight.py --source hdmi --device 0 --out tapo --hosts 192.168.1.50

Credenziali: variabili d'ambiente TAPO_USER e TAPO_PASS (l'account TP-Link
usato nell'app Tapo). Non si passano da riga di comando, cosi' non finiscono
nella cronologia della shell.

Lo stadio di lettura e quello di scrittura dipendono dall'hardware e NON sono
stati provati qui: non c'erano ne' uno schermo ne' una lampadina. Il motore
del colore invece e' coperto dai test in test_color.py.
"""

import argparse, os, sys, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from color import dominant, Smoother, Gate


# --------------------------------------------------------------------------
# sorgenti
# --------------------------------------------------------------------------
def src_demo():
    """Scene finte, per vedere girare la catena senza hardware."""
    scenes = [((18, 24, 40), (40, 90, 220)), ((10, 10, 12), (230, 40, 30)),
              ((20, 30, 20), (40, 190, 70)), ((130, 132, 129), (140, 140, 138))]
    i = 0
    while True:
        bg, fg = scenes[(i // 40) % len(scenes)]
        f = np.zeros((360, 640, 3), np.uint8)
        f[:, :] = bg
        f[90:270, 140:500] = fg
        i += 1
        yield f
        time.sleep(1 / 30)


def src_screen():
    """Cattura lo schermo della macchina su cui gira questo script."""
    try:
        import mss
    except ImportError:
        sys.exit("serve mss:  pip install mss")
    with mss.mss() as sct:
        mon = sct.monitors[1]
        while True:
            img = np.asarray(sct.grab(mon))      # BGRA
            yield img[:, :, [2, 1, 0]]
            time.sleep(1 / 30)


def src_hdmi(index):
    """Scheda di acquisizione HDMI vista come webcam."""
    try:
        import cv2
    except ImportError:
        sys.exit("serve opencv:  pip install opencv-python")
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        sys.exit("nessun dispositivo di acquisizione all'indice %d" % index)
    try:
        while True:
            ok, f = cap.read()
            if not ok:
                time.sleep(0.1); continue
            yield f[:, :, ::-1]                   # BGR -> RGB
    finally:
        cap.release()


# --------------------------------------------------------------------------
# uscite
# --------------------------------------------------------------------------
class PrintOut:
    """Prova a secco: stampa cosa manderebbe, senza toccare la rete."""
    def send(self, rgb):
        r, g, b = rgb
        print("\033[48;2;%d;%d;%dm    \033[0m  rgb(%3d,%3d,%3d)" % (r, g, b, r, g, b),
              flush=True)


class TapoOut:
    """python-kasa >= 0.7, protocollo locale: niente giro dal cloud.

    NON PROVATO: qui non c'era nessuna lampadina. Se l'API della tua versione
    di python-kasa differisce, il punto da adattare e' solo set().
    """
    def __init__(self, hosts):
        try:
            from kasa import Discover          # noqa: F401
        except ImportError:
            sys.exit("serve python-kasa:  pip install python-kasa")
        self.user = os.environ.get("TAPO_USER")
        self.pw = os.environ.get("TAPO_PASS")
        if not self.user or not self.pw:
            sys.exit("imposta TAPO_USER e TAPO_PASS nell'ambiente")
        self.hosts = hosts
        self.devs = []
        import asyncio
        self.loop = asyncio.new_event_loop()
        self.loop.run_until_complete(self._connect())

    async def _connect(self):
        from kasa import Discover
        for h in self.hosts:
            d = await Discover.discover_single(h, username=self.user, password=self.pw)
            await d.update()
            self.devs.append(d)
            print("collegata: %s (%s)" % (d.alias, h))

    def _light(self, d):
        mods = getattr(d, "modules", {})
        return mods.get("Light") or mods.get("light") or d

    async def _set(self, rgb):
        import colorsys, asyncio
        r, g, b = [x / 255 for x in rgb]
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        hsv = (int(h * 360), int(s * 100), max(1, int(v * 100)))
        await asyncio.gather(*[self._light(d).set_hsv(*hsv) for d in self.devs],
                             return_exceptions=True)

    def send(self, rgb):
        self.loop.run_until_complete(self._set(rgb))


# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", choices=["demo", "screen", "hdmi"], default="demo")
    ap.add_argument("--device", type=int, default=0, help="indice acquisizione HDMI")
    ap.add_argument("--out", choices=["print", "tapo"], default="print")
    ap.add_argument("--hosts", nargs="*", default=[], help="IP delle lampadine Tapo")
    ap.add_argument("--hz", type=float, default=4.0, help="invii al secondo, al massimo")
    ap.add_argument("--alpha", type=float, default=0.12, help="0 lentissimo, 1 immediato")
    a = ap.parse_args()

    frames = {"demo": src_demo, "screen": src_screen,
              "hdmi": lambda: src_hdmi(a.device)}[a.source]()
    out = PrintOut() if a.out == "print" else TapoOut(a.hosts)
    smooth = Smoother(alpha=a.alpha)
    gate = Gate(min_interval=1.0 / a.hz)

    print("sorgente %s -> %s   (ctrl-c per fermare)" % (a.source, a.out))
    try:
        for f in frames:
            rgb = smooth.push(dominant(f))
            if gate.allow(rgb, time.monotonic()):
                out.send(rgb)
    except KeyboardInterrupt:
        print("\nfermato")


if __name__ == "__main__":
    main()
