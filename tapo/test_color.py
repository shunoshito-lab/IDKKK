import os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from color import dominant, Smoother, Gate

def frame(h=360, w=640): return np.zeros((h,w,3), np.uint8)
def hue_of(rgb):
    r,g,b=[x/255 for x in rgb]; mx,mn=max(r,g,b),min(r,g,b); d=mx-mn
    if d<1e-6: return None
    if mx==r: hh=((g-b)/d)%6
    elif mx==g: hh=(b-r)/d+2
    else: hh=(r-g)/d+4
    return hh*60
def name(rgb):
    h=hue_of(rgb)
    if h is None: return "grigio"
    for lo,hi,n in [(0,20,"rosso"),(20,45,"arancio"),(45,70,"giallo"),(70,165,"verde"),
                    (165,200,"ciano"),(200,255,"blu"),(255,290,"viola"),(290,340,"magenta"),(340,361,"rosso")]:
        if lo<=h<hi: return n
    return "?"
def sat(rgb):
    mx,mn=max(rgb),min(rgb)
    return 0 if mx==0 else (mx-mn)/mx

ok=lambda c,m: print(("  OK  " if c else " FAIL ")+m)

# 1) scena prevalentemente blu
f=frame(); f[:,:]=(18,24,40); f[80:280,120:520]=(40,90,220)
r=dominant(f); ok(name(r)=="blu", "scena blu -> "+name(r)+" "+str(r))

# 2) scena scura con una piccola fiammata rossa: i pixel scuri non devono vincere
f=frame(); f[:,:]=(8,8,10); f[150:210,280:360]=(230,40,30)
r=dominant(f); ok(name(r)=="rosso", "poco rosso su fondo nero -> "+name(r)+" "+str(r))

# 3) il caso che rompe la media semplice: meta' rosso, meta' ciano
f=frame(); f[:,:320]=(220,30,30); f[:,320:]=(30,220,220)
r=dominant(f)
ok(sat(r)>0.55, "rosso|ciano: resta un colore vivido, non grigio -> "+name(r)+" sat "+str(round(sat(r),2))+" "+str(r))
naive=tuple(int(x) for x in np.asarray(f).reshape(-1,3).mean(axis=0))
print("        (la media semplice darebbe "+str(naive)+", sat "+str(round(sat(naive),2))+")")

# 4) scena grigia -> bianco caldo, non un colore inventato
f=frame(); f[:,:]=(130,132,129)
r=dominant(f); ok(r[0]>=r[1]>=r[2] and sat(r)<0.4, "scena grigia -> bianco caldo "+str(r))

# 5) scena nera: la luce non si spegne del tutto
f=frame(); r=dominant(f)
ok(max(r)>=25, "scena nera -> luce tenue, non spenta "+str(r))

# 6) verde
f=frame(); f[:,:]=(20,30,20); f[60:300,80:560]=(40,190,70)
r=dominant(f); ok(name(r)=="verde", "scena verde -> "+name(r)+" "+str(r))

# 7) il risultato non dipende dalla risoluzione della sorgente
a=frame(1080,1920); a[:,:]=(18,24,40); a[200:800,300:1500]=(40,90,220)
b=frame(360,640);   b[:,:]=(18,24,40); b[66:266,100:500]=(40,90,220)
ra,rb=dominant(a),dominant(b)
d=sum((x-y)**2 for x,y in zip(ra,rb))**.5
ok(d<26, "1080p e 360p danno lo stesso colore (scarto "+str(round(d,1))+") "+str(ra)+" "+str(rb))

# 8) costo costante: 4K non deve costare piu' di 360p
import time
big=np.random.randint(0,255,(2160,3840,3),dtype=np.uint8)
t=time.perf_counter(); [dominant(big) for _ in range(5)]; tb=(time.perf_counter()-t)/5
print("        4K: %.1f ms per fotogramma (%.0f fps teorici)"%(tb*1000, 1/tb))

# 9) lo smorzatore: stacco rapido sui tagli, lento sulle derive
s=Smoother()
for _ in range(40): s.push((30,40,200))
before=s.push((30,40,200))
after=s.push((220,40,30))
jump=sum((a-b)**2 for a,b in zip(after,before))**.5
ok(jump>60, "cambio di scena: la luce segue subito (salto "+str(round(jump,1))+")")
s2=Smoother(); [s2.push((100,100,100)) for _ in range(40)]
prev=s2.push((100,100,100)); small=s2.push((108,100,100))
ok(sum((a-b)**2 for a,b in zip(small,prev))**.5 < 4, "deriva piccola: la luce resta ferma")

# 10) il cancello limita gli invii alla lampadina
g=Gate(min_interval=0.25, min_delta=10)
sent=sum(1 for i in range(100) if g.allow((30+i,40,200), i*0.01))
ok(sent<=5, "100 fotogrammi in 1 s -> "+str(sent)+" invii alla lampadina")
