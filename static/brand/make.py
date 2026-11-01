from PIL import Image, ImageDraw, ImageFont, ImageFilter
A='/cursor/stores/store-f5cc99dd-eb26-4690-8e38-01dd5b40936f/grok-bot/agents/7002c6f2-f872-46df-ad3b-aaadbe43aae9/assets/'
logo=Image.open(A+'7a56dde32ebee116928711238b7e47d9fdf5268991d0d8a3f4488f78ebcf17d9.jpg').convert('RGB')
ban=Image.open(A+'25f60304ee8e446245c3c6c8c1f0e1a7892a621627f74e630fa1f028260ff5e8.jpg').convert('RGB')
OR=(242,70,21); F='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
font=lambda s:ImageFont.truetype(F,s,index=2)
c,r=512,458
em=logo.crop((c-r,c-r,c+r,c+r))
def emblem(size,bg=True):
    m=Image.new('L',(r*8,r*8),0);ImageDraw.Draw(m).ellipse((0,0,r*8-1,r*8-1),fill=255)
    m=m.resize(em.size,Image.LANCZOS)
    base=Image.new('RGBA',em.size,OR+(255,) if bg else (0,0,0,0)); base.paste(em,(0,0),m)
    return base.resize((size,size),Image.LANCZOS)
emblem(400).convert('RGB').save('x-avatar-400.png')
emblem(512,False).save('logo-512.png')
for s,n in [(180,'apple-touch-icon.png'),(192,'android-chrome-192x192.png'),(512,'android-chrome-512x512.png')]:
    emblem(s).convert('RGB').save(n)
emblem(64,False).save('logo-64.png')
emblem(48,False).save('favicon.ico',sizes=[(16,16),(32,32),(48,48)])
emblem(32,False).save('favicon-32x32.png')
def addurl(img,x,y,s):
    d=ImageDraw.Draw(img);f=font(s);w=d.textlength('fwqabc.com',font=f);d.text((x-w,y),'fwqabc.com',font=f,fill='white')
# X header 1500x500: recompose
h=Image.new('RGB',(1500,500),OR); d=ImageDraw.Draw(h)
for cx,cy,R in [(1330,250,380)]:
    lw=18;col=(245,92,50)
    d.ellipse((cx-R,cy-R,cx+R,cy+R),outline=col,width=lw)
    for k in (0.45,0.8): d.ellipse((cx-R*k,cy-R,cx+R*k,cy+R),outline=col,width=lw)
    for t in (-0.5,0,0.5):
        y=cy+t*R; import math; w=R*math.sqrt(1-t*t); d.line((cx-w,y,cx+w,y),fill=col,width=lw)
cm=Image.new('L',logo.size,0);ImageDraw.Draw(cm).ellipse((c-r+30,c-r+30,c+r-30,c+r-30),fill=255)
from PIL import ImageChops
g=logo.crop((150,110,880,580)); gm=ImageChops.multiply(g.convert('L').point(lambda v:255 if v>200 else 0),cm.crop((150,110,880,580))).filter(ImageFilter.GaussianBlur(1))
gw=430; gh=int(g.height*gw/g.width); gm2=gm.resize((gw,gh),Image.LANCZOS)
h.paste(Image.new('RGB',(gw,gh),'white'),(330,250-gh//2-10),gm2)
f1=font(64);f2=font(32)
d.text((830,150),'出海服务器，',font=f1,fill='white');d.text((830,232),'少踩坑少花钱',font=f1,fill='white')
d.text((832,330),'VPS优惠 · 线路科普 · 免费服务器指南',font=f2,fill=(255,236,228))
addurl(h,1450,430,28)
h.save('x-header-1500x500.png')
# OG 1200x630
og=ban.resize((1200,675),Image.LANCZOS).crop((0,22,1200,652))
og.save('og-default-1200x630.png')
