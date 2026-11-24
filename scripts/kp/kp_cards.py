"""Kansas-definition 'ten counties' social-media cards for New Mexico (adapted from the Kansas build_flip.py layout).
Definition (Kansas): registered Democrats fell AND Democratic governor votes rose; ranked by gap in votes =
D26 - D22 x (RegDem26/RegDem22). Every number comes from the verified pass-A registry and is logged for the pass-B check."""
import csv, json
from PIL import Image, ImageDraw, ImageFont
from kpfmt import Reg, fmt
R=Reg('cards'); OUT='/workspace/nm-election/wiki/resources/social-media/'
FB='/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'; f=lambda s:ImageFont.truetype(FB,s)
BLUE=(0,66,130); NAVY=(10,30,60); GRAY=(95,95,95); BLK=(0,0,0); WHT=(255,255,255); GOLD=(255,214,102)
SRC='Source: New Mexico SOS. *2026 UNOFFICIAL (SOS 11/12/2026; state canvass Nov 24).'
top=R.raw('ten.counties'); R.use('ten.counties'); ncand=R.v('ten.n_candidates','int')
def ctext(d,y,t,font,fill,W=1080): d.text(((W-d.textlength(t,font=font))/2,y),t,font=font,fill=fill)
def fit(d,t,size,mw):
    while d.textlength(t,font=f(size))>mw: size-=2
    return f(size)
def arrow(d,cx,top_,h,w,up,col):
    sw=w*0.42; hh=h*0.42
    pts=[(cx,top_),(cx+w/2,top_+hh),(cx+sw/2,top_+hh),(cx+sw/2,top_+h),(cx-sw/2,top_+h),(cx-sw/2,top_+hh),(cx-w/2,top_+hh)] if up else [(cx,top_+h),(cx+w/2,top_+h-hh),(cx+sw/2,top_+h-hh),(cx+sw/2,top_),(cx-sw/2,top_),(cx-sw/2,top_+h-hh),(cx-w/2,top_+h-hh)]
    d.polygon(pts,fill=col,outline=BLK,width=4)
rows=[]; man=[]
for i,c in enumerate(top,1):
    k=lambda x:f'c.{c}.{x}'
    r22=R.v(k('regdem22'),'int'); r26=R.v(k('regdem26'),'int'); rd=R.v(k('reg_change'),'sint')
    v22=R.v(k('dem22'),'int'); v26=R.v(k('dem26'),'int'); vd=R.v(k('vote_change'),'sint'); vp=R.v(k('vote_pct'),'spct0')
    gp=R.v(k('gap_votes'),'sint'); sh=R.v(k('gap_share_ballots26'),'pct1')
    assert rd.startswith('-') and vd.startswith('+') and gp.startswith('+')
    im=Image.new('RGB',(1080,1350),WHT); d=ImageDraw.Draw(im)
    d.rectangle([0,0,1080,210],fill=NAVY)
    ctext(d,28,f'#{i} OF 33 NEW MEXICO COUNTIES',f(34),GOLD)
    t=c.upper()+' COUNTY'; ctext(d,78,t,fit(d,t,100,1000),WHT)
    arrow(d,130,270,170,130,False,GRAY)
    d.text((240,262),'REGISTERED DEMOCRATS',font=f(40),fill=BLK)
    t=f'{r22} \u2192 {r26}'; d.text((240,312),t,font=fit(d,t,84,800),fill=BLK)
    d.text((240,408),f'\u2212{rd[1:]}  (2022 \u2192 2026)',font=f(44),fill=GRAY)
    arrow(d,130,540,220,150,True,BLUE)
    d.text((240,540),'DEMOCRATIC VOTES',font=f(40),fill=BLUE); d.text((240,585),'FOR GOVERNOR',font=f(40),fill=BLUE)
    t=f'{v22} \u2192 {v26}*'; d.text((240,640),t,font=fit(d,t,84,800),fill=BLUE)
    d.text((240,738),f'{vd}*  ({vp}*)',font=f(48),fill=BLUE)
    d.rectangle([0,860,1080,1150],fill=BLUE)
    ctext(d,885,'VOTES BEYOND WHAT REGISTRATION EXPLAINS',f(40),WHT)
    ctext(d,945,f'{gp}*',f(150),WHT)
    ctext(d,1170,f'That is {sh} of 2026* ballots cast.',f(36),BLK)
    ctext(d,1235,'Fewer Democrats registered. More Democratic votes.',f(34),BLK)
    ctext(d,1285,SRC,fit(d,SRC,22,1040),GRAY)
    ctext(d,1318,'A pattern in the numbers, not a finding about cause.',f(22),GRAY)
    fn=f'NM_Flip_{i:02d}_{c.replace(" ","_")}.png'; im.save(OUT+fn)
    man.append(dict(file=fn,strings=[c.upper()+' COUNTY',r22,r26,rd,v22,v26,vd,vp,gp,sh]))
    rows.append([i,c,R.v(k('population'),'int'),r22,r26,rd,v22,v26,vd,vp,gp,sh])
im=Image.new('RGB',(1080,1350),WHT); d=ImageDraw.Draw(im)
d.rectangle([0,0,1080,200],fill=NAVY)
ctext(d,30,'TEN NEW MEXICO COUNTIES',f(64),WHT); ctext(d,115,'Fewer Democrats registered. More Democratic votes.',f(36),GOLD)
ctext(d,225,'Votes beyond what registration explains, 2022 \u2192 2026*',f(34),BLK)
mx=R.use(f'c.{top[0]}.gap_votes'); y=290
for i,c in enumerate(top,1):
    d.text((40,y+8),f'{i}. {c}',font=f(36),fill=BLK); gv=R.use(f'c.{c}.gap_votes')
    L=int(480*gv/mx); d.rectangle([370,y,370+max(L,6),y+56],fill=BLUE)
    d.text((370+max(L,6)+14,y+8),R.v(f'c.{c}.gap_votes','sint')+'*',font=f(36),fill=BLK); y+=88
ctext(d,1170,'Each county: registered Democrats fell, Democratic votes for governor rose.',f(28),BLK)
ctext(d,1215,'Value = 2026 Dem votes \u2212 2022 Dem votes \u00d7 (2026 Dem reg \u00f7 2022 Dem reg)',f(26),GRAY)
ctext(d,1265,SRC,fit(d,SRC,22,1040),GRAY)
ctext(d,1298,f'Ranked among the {ncand} counties where Dem registration fell and Dem votes rose.',f(22),GRAY)
im.save(OUT+'NM_Flip_00_Summary_Top10.png')
with open(OUT+'NM_Top10_Flip_Counties.csv','w',newline='') as fh:
    w=csv.writer(fh); w.writerow(['rank','county','population_2025','dem_reg_2022','dem_reg_2026','dem_reg_change','dem_gov_votes_2022','dem_gov_votes_2026_unofficial','dem_vote_change_unofficial','dem_vote_pct_change_unofficial','gap_votes_unofficial','gap_pct_of_2026_ballots_cast_unofficial'])
    w.writerows(rows)
json.dump(man,open('/workspace/nm-election/verification/kp_cards_manifest.json','w'),indent=1)
R.save('wiki/resources/social-media/NM_Top10_Flip_Counties.csv'); print(*rows,sep='\n')
