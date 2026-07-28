#!/usr/bin/env python3
"""
NashSecurity Cinematic Video - Direct ffmpeg pipe approach
"""
import os, math, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT, FPS, DURATION = 1280, 720, 24, 45
TOTAL_FRAMES = FPS * DURATION
OUTPUT = '/tmp/media/nash_cinematic.mp4'

BG = (3, 5, 10)
BLUE = (0, 212, 255)
BLUE_DIM = (0, 80, 160)

class P:
    def __init__(self):
        self.x, self.y = random.randint(0,WIDTH), random.randint(0,HEIGHT)
        self.s, self.sp = random.uniform(1,3), random.uniform(0.3,1.2)
        self.dr = random.uniform(-0.3,0.3)
    def step(self):
        self.y -= self.sp; self.x += self.dr
        if self.y < -10: self.y = HEIGHT+10; self.x = random.randint(0,WIDTH)

parts = [P() for _ in range(60)]
stars = [(random.randint(0,WIDTH), random.randint(0,HEIGHT//2), random.uniform(0.3,1)) for _ in range(80)]
bldgs = []
for i in range(20):
    w = random.randint(50,130); h = random.randint(150,450)
    bldgs.append({'x': i*(WIDTH//20)+random.randint(-15,15), 'y': HEIGHT-h, 'w': w, 'h': h,
                  'wr': random.randint(3,7), 'lr': random.uniform(0.3,0.8)})

def ease(t): return t*t*(3-2*t)
def clamp(v,a=0,b=1): return max(a,min(b,v))

def grad(d,y0,y1,c0,c1):
    for y in range(max(0,int(y0)),min(HEIGHT,int(y1))):
        t = (y-y0)/max(1,(y1-y0))
        d.line([(0,y),(WIDTH,y)], fill=tuple(int(c0[i]+(c1[i]-c0[i])*t) for i in range(3)))

def get_font(sz, bold=True):
    try: return ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf", sz)
    except: return ImageFont.load_default()

def txt(d, text, y, sz=48, color=(255,255,255), glow=False, bold=True):
    f = get_font(sz, bold)
    bb = d.textbbox((0,0), text, font=f)
    x = (WIDTH - bb[2]+bb[0])//2
    if glow:
        for dx in range(-2,3):
            for dy in range(-2,3):
                d.text((x+dx,y+dy), text, fill=BLUE_DIM, font=f)
    d.text((x,y), text, fill=color, font=f)

def scene(t):
    scenes = [
        (0,6,1.0,0,1.0,'SMART CITY','FUTURE CITY · AI POWERED'),
        (6,11,1.5,-80,0.7,'NASH SECURITY','AI SECURITY CENTER'),
        (11,18,2.0,-180,0.3,'PRODUCT SHOWROOM','CCTV · AI · ACCESS CONTROL · FIRE'),
        (18,24,2.5,-280,0.2,'AI DASHBOARD','FACE RECOGNITION · ANALYTICS'),
        (24,30,1.8,-120,0.5,'SERVICES','INSTALLATION · SUPPORT · MAINTENANCE'),
        (30,35,1.5,-50,0.4,'DOWNLOAD','WINDOWS · ANDROID · IOS · LINUX'),
        (35,39,1.2,0,0.6,'NASH BLOG','AI · SECURITY · INNOVATION'),
        (39,43,1.0,0,1.0,None,None),
        (43,45,1.0,0,1.0,None,None),
    ]
    for s in scenes:
        if s[0] <= t < s[1]:
            frac = (t-s[0])/(s[1]-s[0])
            return s[2], s[3], s[4], s[5], s[6], frac
    return 1.0,0,1.0,None,None,0

def render(fi):
    t = fi/FPS
    zoom,cy,net,t1,t2,frac = scene(t)
    img = Image.new('RGB',(WIDTH,HEIGHT),BG)
    d = ImageDraw.Draw(img)
    
    grad(d,0,HEIGHT*0.4,(5,8,20),(3,5,12))
    grad(d,HEIGHT*0.4,HEIGHT,(3,5,12),(8,12,25))
    
    sa = clamp(1.5-zoom,0,1)
    if sa > 0.05:
        for sx,sy,sb in stars:
            d.point((sx,sy), fill=(int(200*sa),int(220*sa),int(255*sa)))
    
    if net > 0.05:
        for i in range(int(12*net)):
            x1 = int(WIDTH*(i/12)+math.sin(fi*0.01+i)*50)
            y1 = int(HEIGHT*0.3+math.sin(fi*0.015+i*2)*100)
            x2 = int(WIDTH*((i+2)/12)+math.cos(fi*0.012+i)*80)
            y2 = int(HEIGHT*0.5+math.cos(fi*0.01+i*3)*120)
            d.line([(x1,y1),(x2,y2)], fill=(0,100,200), width=1)
            d.ellipse([x1-2,y1-2,x1+2,y1+2], fill=(0,180,255))
    
    for b in bldgs:
        bx = int(b['x']*zoom+(1-zoom)*WIDTH/2)
        by = int((b['y']+cy)*zoom+(1-zoom)*HEIGHT)
        bw = int(b['w']*zoom); bh = int(b['h']*zoom)
        if bx+bw<0 or bx>WIDTH or by>HEIGHT: continue
        d.rectangle([bx,by,bx+bw,HEIGHT], fill=(12,15,25))
        d.rectangle([bx,by,bx+bw,by+2], fill=(20,25,40))
        ww = max(2,bw//(b['wr']+1))
        for wy in range(by+10,min(HEIGHT-10,by+bh-10),20):
            for wx in range(bx+5,bx+bw-5,ww+4):
                if random.random() < b['lr']:
                    fl = math.sin(fi*0.02+wx*0.1+wy*0.05)*0.2+0.8
                    br = int(40*fl)
                    d.rectangle([wx,wy,wx+ww-2,wy+8], fill=(br,br+20,br+50))
    
    for p in parts:
        p.step()
        d.ellipse([int(p.x)-1,int(p.y)-1,int(p.x)+1,int(p.y)+1], fill=(0,160,255))
    
    m = 40
    for cx,cy2 in [(m,m),(WIDTH-m,m),(m,HEIGHT-m),(WIDTH-m,HEIGHT-m)]:
        sz = 30
        dx = 1 if cx==m else -1
        dy = 1 if cy2==m else -1
        d.line([(cx,cy2),(cx+sz*dx,cy2)], fill=(0,120,220), width=1)
        d.line([(cx,cy2),(cx,cy2+sz*dy)], fill=(0,120,220), width=1)
    
    sy = int((fi*4)%HEIGHT)
    d.line([(0,sy),(WIDTH,sy)], fill=(0,80,180), width=1)
    
    if t1:
        if frac < 0.2: a = ease(frac/0.2)
        elif frac > 0.8: a = ease((1-frac)/0.2)
        else: a = 1.0
        if a > 0.1:
            txt(d, t1, HEIGHT//2-40, sz=60, glow=True)
            if t2:
                txt(d, t2, HEIGHT//2+30, sz=20, bold=False)
    
    if t < 4 or t > 40:
        la = ease(clamp(t/3)) if t < 4 else ease(clamp((45-t)/3))
        if la > 0.1:
            txt(d, 'NASH SECURITY', HEIGHT//2-60, sz=80, glow=True)
            txt(d, 'PROTECTING TOMORROW WITH AI', HEIGHT//2+30, sz=20, bold=False)
    
    bw2 = 200
    bx2 = (WIDTH-bw2)//2
    by2 = HEIGHT-25
    d.rectangle([bx2,by2,bx2+bw2,by2+3], fill=(20,25,40))
    d.rectangle([bx2,by2,bx2+int(bw2*t/DURATION),by2+3], fill=BLUE)
    
    return np.array(img)

if __name__ == '__main__':
    os.makedirs('/tmp/media', exist_ok=True)
    print(f"🎬 Generating {DURATION}s @ {FPS}fps = {TOTAL_FRAMES} frames")
    print(f"📐 {WIDTH}x{HEIGHT} → {OUTPUT}")
    
    # Use ffmpeg pipe directly
    cmd = [
        'ffmpeg', '-y',
        '-f', 'rawvideo', '-vcodec', 'rawvideo',
        '-s', '1280x720', '-pix_fmt', 'rgb24',
        '-r', str(FPS),
        '-i', '-',
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        '-preset', 'medium', '-crf', '23',
        OUTPUT
    ]
    
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    
    for fi in range(TOTAL_FRAMES):
        frame = render(fi)
        proc.stdin.write(frame.tobytes())
        if fi % 50 == 0:
            print(f"  Frame {fi}/{TOTAL_FRAMES} ({fi*100//TOTAL_FRAMES}%)")
    
    proc.stdin.close()
    stderr = proc.stderr.read()
    proc.wait()
    
    if proc.returncode != 0:
        print(f"❌ ffmpeg error: {stderr.decode()[-500:]}")
    else:
        sz = os.path.getsize(OUTPUT) / 1024 / 1024
        print(f"\n✅ Done! {sz:.1f}MB → {OUTPUT}")
