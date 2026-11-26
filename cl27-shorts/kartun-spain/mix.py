import sys,json,numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly
SR=48000; id=sys.argv[1]; T=json.load(open('timing.json'))[id]
def load(p):
    sr,x=wavfile.read(p); x=x.astype(np.float32)/(32768 if x.dtype==np.int16 else 1)
    if x.ndim>1: x=x.mean(1)
    if sr!=SR: x=resample_poly(x,SR,sr).astype(np.float32)
    return x
v=load(f'vo/{id}.wav'); N=len(v); t=np.arange(N)/SR
rms=lambda x: np.sqrt(np.mean(x[np.abs(x)>0.01]**2)+1e-9)
vr=rms(v); rng=np.random.default_rng(1)
twist=T['lines'][-1]['t0']
# music: bouncy march (bass + plucky melody), drops out at twist, then light drone
bpm=112; beat=60/bpm; mus=np.zeros(N,np.float32)
notes=[7,8,7,5, 4,5,4,1, 0,1,4,5, 7,5,4,1]  # Phrygian dominant, Spanish guitar flavour
def pluck(f,d,a=1.0):
    n=int(d*SR); tt=np.arange(n)/SR; return a*np.sin(2*np.pi*f*tt)*np.exp(-tt*9)*(1+0.3*np.sin(2*np.pi*2*f*tt))
b=0;k=0
while b<twist-0.2:
    i=int(b*SR); f=220.0*2**(notes[k%16]/12); s=pluck(f,beat*0.9,0.5); 
    bs=pluck(55.0*2**(([0,-2,-4,-5][(k//4)%4])/12),beat*0.9,0.9) if k%2==0 else pluck(130.8,0.1,0.3)*0
    e=min(N,i+len(s)); mus[i:e]+=s[:e-i]; e2=min(N,i+len(bs)); mus[i:e2]+=bs[:e2-i]
    if k%2==1: n=int(0.05*SR); h=rng.standard_normal(n)*np.exp(-np.arange(n)/SR*80)*0.15; e3=min(N,i+n); mus[i:e3]+=h[:e3-i]
    b+=beat/2; k+=1
m=t>=twist+0.3; mus[m]+=0.25*np.sin(2*np.pi*98*t[m])*np.minimum(1,(t[m]-twist-0.3)/1.0)
mus*=vr/rms(mus)*0.5   # -6 dB
# sfx: whoosh at each line start, sting at twist
sfx=np.zeros(N,np.float32)
def whoosh(at,d=0.45):
    n=int(d*SR); w=rng.standard_normal(n); 
    from scipy.signal import lfilter
    w=lfilter([0.15],[1,-0.85],w); env=np.sin(np.pi*np.arange(n)/n)**2; i=int(at*SR); e=min(N,i+n)
    if i<N: sfx[i:e]+=(w*env)[:e-i]
for L in T['lines'][1:]: whoosh(max(0,L['t0']-0.3))
i=int(twist*SR); n=int(0.6*SR); tt=np.arange(n)/SR; st=sum(np.sin(2*np.pi*f*tt) for f in (523,659,784))*np.exp(-tt*5); e=min(N,i+n); sfx[i:e]+=st[:e-i]
sfx*=vr*0.5/max(rms(sfx),1e-6)
h=load('huss.wav'); h*=vr*0.6/rms(h)
for at in [9,18,27,36,45]:
    if at<N/SR-2.2: i=int(at*SR); e=min(N,i+len(h)); sfx[i:e]+=h[:e-i]
import sys as _s
RAIN={'realmadrid':[(0,3.2),(42.4,48.2)],'barcelona':[(0,3.4),(45.9,51.6)]}.get(id,[])
from scipy.signal import lfilter
rn=lfilter([0.3],[1,-0.6],rng.standard_normal(N)).astype(np.float32); env=np.zeros(N,np.float32)
for a,b in RAIN:
    i,j=int(a*SR),min(N,int(b*SR)); w=np.ones(j-i,np.float32); r=min(int(0.25*SR),(j-i)//2); w[:r]=np.linspace(0,1,r); w[-r:]=np.linspace(1,0,r); env[i:j]=w
rn*=env; rn*=vr*0.22/max(rms(rn),1e-6) if env.any() else 0
out=v+mus+sfx+rn; out/=max(1,np.abs(out).max()/0.95)
wavfile.write(f'mix_{id}.wav',SR,(out*32767).astype(np.int16)); print(id,N/SR)
