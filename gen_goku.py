"""Goku MUI (Mastered Ultra Instinct) pixel generator for dsh-go.
100x100 logical grid -> 3x NEAREST upscale -> 300x300 sprite sheets.
Anime-accurate MUI: tall silver spiky hair, bare muscular chest,
only orange tattered gi pants, blue boots with red stripe, silver eyes."""
from __future__ import annotations
import math, os
from PIL import Image, ImageDraw

SIZE, SCALE, OUT = 100, 3, 300
TAU = math.tau
ANIM_COLS = {"idle":6,"working":8,"thinking":6,"error":5,"success":10,"sleep":6}

def rgba(h,a=255):
    h=h.lstrip('#'); return (int(h[:2],16),int(h[2:4],16),int(h[4:6],16),a)

PAL={
 "light":{"o":rgba('000000'),"skin":rgba('deb887'),"skinShade":rgba('cda475'),
          "hair":rgba('e8e8e8'),"hairShade":rgba('b8b8b8'),"gi":rgba('ff8c00'),
          "giShade":rgba('d67500'),"blue":rgba('1e56a6'),"blueShade":rgba('164080'),
          "eye":rgba('d0d0d0'),"pupil":rgba('808080'),"aura":rgba('c0d8ff'),
          "auraShade":rgba('80a8e0'),"shoe":rgba('2e5aa8'),"shoeShade":rgba('1e4078'),
          "white":rgba('ffffff'),"shoeLace":rgba('d2691e')},
 "dark":{"o":rgba('000000'),"skin":rgba('cda475'),"skinShade":rgba('a8805c'),
          "hair":rgba('f0f0f0'),"hairShade":rgba('989898'),"gi":rgba('e87a0c'),
          "giShade":rgba('c06000'),"blue":rgba('3070c8'),"blueShade":rgba('2050a0'),
          "eye":rgba('e8e8e8'),"pupil":rgba('a0a0a0'),"aura":rgba('d0e8ff'),
          "auraShade":rgba('90b8f0'),"shoe":rgba('4078c8'),"shoeShade":rgba('3060a8'),
          "white":rgba('ffffff'),"shoeLace":rgba('d2691e')},
}

def line(d,a,b,c,w=1): d.line([a,b],fill=c,width=w)
def poly(d,p,c,o=None): d.polygon(p,fill=c,outline=o)
def rect(d,b,c,o=None): d.rectangle(b,fill=c,outline=o)
def ell(d,b,c,o=None): d.ellipse(b,fill=c,outline=o)

def draw_limb(d,x1,y1,x2,y2,c,w):
    d.line([(x1,y1),(x2,y2)],fill=c,width=w)

# ---------- aura ----------
def aura(img,p,cfg):
    inten=cfg['aura']
    if inten<=0.05: return
    g=ImageDraw.Draw(img)
    cx,cy=50+cfg['dx'],52+cfg['dy']; ph=cfg['phase']
    for k in range(16):
        a=k*TAU/16+ph; r=34+6*math.sin(k*1.5+ph*2)
        x=cx+r*math.cos(a); y=cy+r*0.75*math.sin(a)
        if 4<x<96 and 4<y<96:
            col=p['aura'][:3]+(int(70+140*inten),)
            ell(g,(x-1,y-1,x+1,y+1),col)

# ---------- hair: tall MUI silver spikes ----------
def hair(d,p,cfg):
    dx,dy=cfg['dx'],cfg['dy']
    # center tall spike to top edge
    poly(d,[(48+dx,24+dy),(50+dx,0+dy),(52+dx,24+dy)],p['hair'],p['o'])
    # left tall spikes
    poly(d,[(42+dx,20+dy),(34+dx,4+dy),(38+dx,14+dy)],p['hair'],p['o'])
    poly(d,[(38+dx,16+dy),(30+dx,0+dy),(34+dx,10+dy)],p['hair'],p['o'])
    poly(d,[(44+dx,18+dy),(36+dx,10+dy),(40+dx,16+dy)],p['hair'],p['o'])
    # right tall spikes
    poly(d,[(58+dx,20+dy),(66+dx,4+dy),(62+dx,14+dy)],p['hair'],p['o'])
    poly(d,[(62+dx,16+dy),(70+dx,0+dy),(66+dx,10+dy)],p['hair'],p['o'])
    poly(d,[(56+dx,18+dy),(64+dx,10+dy),(60+dx,16+dy)],p['hair'],p['o'])
    # side hair wrapping head
    poly(d,[(36+dx,22+dy),(42+dx,16+dy),(48+dx,22+dy)],p['hair'],p['o'])
    poly(d,[(64+dx,22+dy),(58+dx,16+dy),(52+dx,22+dy)],p['hair'],p['o'])
    # hair shade under mass
    poly(d,[(38+dx,26+dy),(50+dx,18+dy),(62+dx,26+dy)],p['hairShade'],p['o'])

# ---------- head / face ----------
def head(d,p,cfg):
    dx,dy=cfg['dx'],cfg['dy']
    # smaller head oval (anime proportion, not chibi)
    ell(d,(39+dx,24+dy,61+dx,38+dy),p['skin'],p['o'])
    # thin neck
    rect(d,(47+dx,38+dy,53+dx,42+dy),p['skin'],p['o'])
    # MUI silver eyes - serious half-lidded
    rect(d,(41+dx,30+dy,47+dx,33+dy),p['eye'],p['o'])
    rect(d,(53+dx,30+dy,59+dx,33+dy),p['eye'],p['o'])
    rect(d,(43+dx,31+dy,45+dx,32+dy),p['pupil'])
    rect(d,(55+dx,31+dy,57+dx,32+dy),p['pupil'])
    d.point((43+dx,31+dy),fill=p['white']); d.point((55+dx,31+dy),fill=p['white'])
    # small nose
    line(d,(49+dx,34+dy),(51+dx,35+dy),p['o'],1)
    line(d,(51+dx,35+dy),(53+dx,34+dy),p['o'],1)
    # neutral mouth (serious)
    line(d,(47+dx,37+dy),(53+dx,37+dy),p['o'],1)
    # ears (small)
    ell(d,(37+dx,30+dy,39+dx,36+dy),p['skin'],p['o'])
    ell(d,(61+dx,30+dy,63+dx,36+dy),p['skin'],p['o'])

# ---------- bare muscular torso (no shirt) ----------
def torso(d,p,cfg):
    dx,dy=cfg['dx'],cfg['dy']
    # V-taper muscular chest, longer - bare skin only, from neck to waist
    poly(d,[(32+dx,42+dy),(68+dx,42+dy),(64+dx,76+dy),(58+dx,88+dy),(50+dx,92+dy),
            (42+dx,88+dy),(36+dx,76+dy)],p['skin'],p['o'])
    # pec definition
    line(d,(38+dx,50+dy),(46+dx,66+dy),p['skinShade'],1)
    line(d,(62+dx,50+dy),(54+dx,66+dy),p['skinShade'],1)
    # abs definition (6-pack)
    line(d,(47+dx,60+dy),(47+dx,72+dy),p['skinShade'],1)
    line(d,(53+dx,60+dy),(53+dx,72+dy),p['skinShade'],1)
    line(d,(45+dx,74+dy),(49+dx,82+dy),p['skinShade'],1)
    line(d,(51+dx,74+dy),(55+dx,82+dy),p['skinShade'],1)
    # shoulder / collarbone lines
    line(d,(34+dx,48+dy),(44+dx,62+dy),p['skinShade'],1)
    line(d,(66+dx,48+dy),(56+dx,62+dy),p['skinShade'],1)

# ---------- orange tattered gi pants only ----------
def pants(d,p,cfg):
    dx,dy=cfg['dx'],cfg['dy']; t=cfg.get('t',0)
    sway=int(2*math.sin(t*TAU))
    # blue sash belt at WAIST (not neck)
    rect(d,(34+dx,74+dy+sway,66+dx,82+dy+sway),p['blue'],p['o'])
    rect(d,(46+dx,72+dy+sway,54+dx,84+dy+sway),p['blueShade'],p['o'])
    # orange gi pants - longer, tattered at bottom, starts below belt
    poly(d,[(34+dx,80+dy+sway),(66+dx,80+dy+sway),(64+dx,100+dy+sway),
            (58+dx,100+dy+sway),(50+dx,100+dy+sway),(42+dx,100+dy+sway),(36+dx,100+dy+sway)],
         p['gi'],p['o'])
    # pants shade folds
    line(d,(38+dx,86+dy+sway),(46+dx,94+dy+sway),p['giShade'],2)
    line(d,(62+dx,86+dy+sway),(54+dx,94+dy+sway),p['giShade'],2)
    line(d,(42+dx,92+dy+sway),(58+dx,92+dy+sway),p['giShade'],2)
    # tattered hem
    for hx in range(38,62,6):
        d.line([(hx+dx,96+dy+sway),(hx+2+dx,100+dy+sway)],fill=p['giShade'],width=1)
        d.line([(hx+4+dx,96+dy+sway),(hx+2+dx,100+dy+sway)],fill=p['giShade'],width=1)

# ---------- arms ----------
def arms(d,p,cfg,state,i,n):
    dx,dy=cfg['dx'],cfg['dy']; t=i/n
    # right arm down - longer, from shoulder area
    draw_limb(d,30+dx,48+dy,20+dx,86+dy,p['skin'],10)
    ell(d,(14+dx,82+dy,26+dx,92+dy),p['skin'],p['o'])
    # left arm state-dependent
    if state=='working':
        draw_limb(d,30+dx,48+dy,40+dx,56+dy,p['skin'],10)
        draw_limb(d,40+dx,56+dy,48+dx,54+dy,p['skin'],8)
        ell(d,(44+dx,52+dy,54+dx,60+dy),p['skin'],p['o'])
        draw_limb(d,70+dx,48+dy,60+dx,56+dy,p['skin'],10)
        draw_limb(d,60+dx,56+dy,48+dx,54+dy,p['skin'],8)
    elif state=='success':
        draw_limb(d,30+dx,48+dy,38+dx,60+dy,p['skin'],10)
        draw_limb(d,38+dx,60+dy,46+dx,52+dy,p['skin'],8)
        ell(d,(42+dx,48+dy,52+dx,56+dy),p['skin'],p['o'])
        draw_limb(d,70+dx,48+dy,80+dx,72+dy,p['skin'],10)
        ell(d,(76+dx,68+dy,86+dx,76+dy),p['skin'],p['o'])
    elif state=='error':
        draw_limb(d,30+dx,48+dy,34+dx,66+dy,p['skin'],10)
        ell(d,(28+dx,62+dy,38+dx,72+dy),p['skin'],p['o'])
        draw_limb(d,70+dx,48+dy,66+dx,66+dy,p['skin'],10)
        ell(d,(62+dx,62+dy,72+dx,72+dy),p['skin'],p['o'])
    else:
        draw_limb(d,70+dx,48+dy,78+dx,86+dy,p['skin'],10)
        ell(d,(72+dx,82+dy,84+dx,92+dy),p['skin'],p['o'])

# ---------- blue boots with red stripe ----------
def boots(d,p,cfg):
    dx,dy=cfg['dx'],cfg['dy']
    rect(d,(32+dx,94+dy,46+dx,100+dy),p['shoe'],p['o'])
    rect(d,(54+dx,94+dy,68+dx,100+dy),p['shoe'],p['o'])
    # red stripe down boots
    rect(d,(37+dx,94+dy,40+dx,100+dy),p['shoeLace'],p['o'])
    rect(d,(59+dx,94+dy,62+dx,100+dy),p['shoeLace'],p['o'])
    # boot soles
    rect(d,(30+dx,98+dy,48+dx,100+dy),p['blueShade'],p['o'])
    rect(d,(52+dx,98+dy,70+dx,100+dy),p['blueShade'],p['o'])
    # ankle wraps
    rect(d,(32+dx,90+dy,46+dx,96+dy),p['skinShade'],p['o'])
    rect(d,(54+dx,90+dy,68+dx,96+dy),p['skinShade'],p['o'])

# ---------- blue wristbands ----------
def wristbands(d,p,cfg):
    dx,dy=cfg['dx'],cfg['dy']
    rect(d,(18+dx,80+dy,26+dx,84+dy),p['blue'],p['o'])
    rect(d,(74+dx,80+dy,82+dx,84+dy),p['blue'],p['o'])

# ---------- FX ----------
def fx(d,p,cfg,state,i,n):
    t=i/n; cx,cy=50+cfg['dx'],52+cfg['dy']
    def spark(x,y,s=1,col=None):
        col=col or p['aura']
        d.line([(x-s,y),(x+s,y)],fill=col,width=1)
        d.line([(x,y-s),(x,y+s)],fill=col,width=1)
    def orb(x,y,r,fill,outline):
        d.ellipse((x-r,y-r,x+r,y+r),fill=fill,outline=outline,width=1)
    if state=='idle':
        for k in range(6):
            a=cfg['phase']*TAU+k*TAU/6; x=50+cfg['dx']+24*math.cos(a); y=52+cfg['dy']+16*math.sin(a)
            spark(round(x),round(y),1,p['auraShade'])
    elif state=='working':
        bx,by=50+cfg['dx'],54+cfg['dy']
        r=6+2*math.sin(t*TAU*4)
        orb(bx,by,r,p['aura'],p['o'])
        orb(bx,by,round(r*0.6),p['white'],p['o'])
        for k in range(8):
            a=cfg['phase']*TAU+k*TAU/8
            x2=bx+round(12*math.cos(a)); y2=by+round(8*math.sin(a))
            d.line([(bx,by),(x2,y2)],fill=p['auraShade'],width=1)
    elif state=='thinking':
        for k in range(5):
            a=cfg['phase']*TAU+k*TAU/5; x=cx+round(16*math.cos(a)); y=cy+round(10*math.sin(a))
            spark(x,y,1,p['white'])
    elif state=='error':
        d.rectangle((47+cfg['dx'],4+cfg['dy'],53+cfg['dx'],10+cfg['dy']),fill=p['aura'],outline=p['o'])
        for k in range(4):
            x=18+k*20+((i*3+k)%5); y=16+((i*7+k*9)%40)
            d.line([(x,y),(x+4,y-5)],fill=p['auraShade'],width=1)
    elif state=='success':
        r=8+24*t
        d.ellipse((cx-r,cy-r*0.7,cx+r,cy+r*0.7),outline=p['aura'],width=2)
        if t>0.4:
            r2=6+14*t
            d.ellipse((cx-r2,cy-r2*0.7,cx+r2,cy+r2*0.7),outline=p['white'],width=1)
        for k in range(12):
            a=k*TAU/12+t*TAU
            spark(round(cx+(30+8*t)*math.cos(a)),round(cy+(22+7*t)*math.sin(a)),1,p['aura'])
    elif state=='sleep':
        # sleeping eating noodle - bowl + chopsticks
        dx2,dy2=cfg['dx'],cfg['dy']
        rect(d,(60+dx2,80+dy2,80+dx2,88+dy2),p['gi'],p['o'])  # noodle bowl
        rect(d,(62+dx2,82+dy2,78+dx2,86+dy2),p['white'],p['o'])  # noodles
        d.line([(58+dx2,78+dy2),(68+dx2,70+dy2)],fill=p['blue'],width=2)  # chopstick
        d.line([(60+dx2,80+dy2),(70+dx2,72+dy2)],fill=p['blue'],width=2)
        for k,s in enumerate((4,3,2)):
            x=66+dx2+k*3; y=12+dy2-k*5-int(t*2)
            d.line([(x,y),(x+s,y)],fill=p['blue'],width=1)
            d.line([(x+s,y),(x,y+s)],fill=p['blue'],width=1)
            d.line([(x,y+s),(x+s,y+s)],fill=p['blue'],width=1)

# ---------- pose ----------
def pose(state,i,n):
    t=i/n
    c={'dx':0,'dy':0,'t':t,'aura':0.4,'phase':t}
    if state=='idle':
        c.update(dy=int(math.sin(t*TAU)),aura=0.4+0.2*math.sin(t*TAU*2),phase=t)
    elif state=='working':
        c.update(dx=int(math.sin(t*TAU*3)),dy=int(math.cos(t*TAU*2)),aura=0.9,phase=t*4)
    elif state=='thinking':
        c.update(aura=0.25,phase=t*TAU)
    elif state=='error':
        c.update(dx=(-2,2,-1,1,0)[i],dy=(0,-1,0,-1,0)[i],aura=0.8,phase=t*3)
    elif state=='success':
        c.update(dy=-int(4*math.sin(math.pi*t)),aura=1.0,phase=t*2)
    elif state=='sleep':
        c.update(aura=0.05,phase=t*0.2)
    return c

def make_frame(state,i,n,dark=False):
    p=PAL['dark' if dark else 'light']; c=pose(state,i,n)
    img=Image.new('RGBA',(SIZE,SIZE),(0,0,0,0)); gl=Image.new('RGBA',(SIZE,SIZE),(0,0,0,0))
    aura(gl,p,c); img=Image.alpha_composite(img,gl)
    d=ImageDraw.Draw(img)
    torso(d,p,c); hair(d,p,c); head(d,p,c); pants(d,p,c)
    arms(d,p,c,state,i,n); boots(d,p,c); wristbands(d,p,c)
    fx(d,p,c,state,i,n)
    return img.resize((OUT,OUT),Image.Resampling.NEAREST)

def make_sheet(state,dark=False):
    n=ANIM_COLS[state]; s=Image.new('RGBA',(OUT*n,OUT),(0,0,0,0))
    for i in range(n): s.paste(make_frame(state,i,n,dark),(i*OUT,0))
    return s

def generate_all(output_dir='.'):
    os.makedirs(os.path.join(output_dir,'dark'),exist_ok=True)
    for state in ANIM_COLS:
        make_sheet(state).save(os.path.join(output_dir,state+'.png'))
        make_sheet(state,True).save(os.path.join(output_dir,'dark',state+'.png'))
    make_frame('idle',0,6).save(os.path.join(output_dir,'preview.png'))

if __name__=='__main__': generate_all(os.path.dirname(os.path.abspath(__file__)))
