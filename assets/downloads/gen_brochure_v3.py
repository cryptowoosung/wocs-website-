#!/usr/bin/env python3
"""WOCS Glamping Integrated Brochure v3 — Light Theme, Content-Rich"""
import os
from PIL import Image, ImageDraw, ImageFont

DPI = 200
W, H = int(8.27*DPI), int(11.69*DPI)
IMG = "/home/claude/images"
FD = "/usr/share/fonts/opentype/noto"
OUT = "/home/claude/wocs_brochure_v3.pdf"

BG = (255,255,255); CARD = (245,243,238); GREEN = (27,67,50); GREEN_L = (45,100,72)
GOLD = (160,130,50); GOLD_L = (140,115,45); GRAY = (100,100,100); GRAY_D = (150,150,150)
TEXT = (50,50,50); WHITE = (255,255,255); BG_GREEN = (235,245,238)

_fc = {}
_fm = {'sans':("NotoSansCJK-Regular.ttc",1),'sans-light':("NotoSansCJK-Light.ttc",1),
       'sans-medium':("NotoSansCJK-Medium.ttc",1),'sans-bold':("NotoSansCJK-Bold.ttc",1),
       'sans-black':("NotoSansCJK-Black.ttc",1),'serif':("NotoSerifCJK-Regular.ttc",1),
       'serif-bold':("NotoSerifCJK-Bold.ttc",1)}
def mm(v): return int(v*DPI/25.4)
def font(n,pt):
    px=int(pt*DPI/72); k=(n,px)
    if k not in _fc: fn,idx=_fm[n]; _fc[k]=ImageFont.truetype(os.path.join(FD,fn),px,index=idx)
    return _fc[k]
def dc(d,t,x,y,f,fill,anchor="mm"): d.text((x,y),t,font=f,fill=fill,anchor=anchor)
def fit(path,tw,th,mode='cover'):
    try: img=Image.open(os.path.join(IMG,path) if not os.path.isabs(path) else path).convert("RGB")
    except: img=Image.new("RGB",(tw,th),CARD)
    iw,ih=img.size
    if mode=='cover':
        s=max(tw/iw,th/ih); img=img.resize((int(iw*s),int(ih*s)),Image.LANCZOS)
        cx,cy=img.size[0]//2,img.size[1]//2; img=img.crop((cx-tw//2,cy-th//2,cx+tw//2,cy+th//2))
    else:
        s=min(tw/iw,th/ih); img=img.resize((int(iw*s),int(ih*s)),Image.LANCZOS)
    return img
def newp(): p=Image.new("RGB",(W,H),BG); return p,ImageDraw.Draw(p)
def gold_line(d,x1,y,x2): d.line([(x1,y),(x2,y)],fill=GOLD,width=2)
MX=mm(12); MY=mm(10); CW=W-2*MX
def footer(d): dc(d,"WOCS  |  010-4337-0582  |  wocs.kr",W//2,H-mm(7),font('sans',8),GRAY_D)
def top_bar(d): d.rectangle([(0,0),(W,mm(2))],fill=GREEN)

pages=[]

# === P1: COVER ===
p,d=newp()
top_bar(d)
try:
    logo=Image.open(os.path.join(IMG,"logo_green_clean.png")).convert("RGBA")
    lsz=mm(32); logo=logo.resize((lsz,lsz),Image.LANCZOS)
    p.paste(logo,(W//2-lsz//2,mm(18)),logo)
except: pass
y=mm(55)
dc(d,"WOCS",W//2,y,font('serif-bold',44),GREEN); y+=mm(16)
dc(d,"우성어닝천막공사캠프시스템",W//2,y,font('sans-medium',14),GREEN); y+=mm(12)
gold_line(d,W//2-mm(28),y,W//2+mm(28)); y+=mm(10)
dc(d,"직접 설계 · 제작 · 시공하는 프리미엄 글램핑",W//2,y,font('sans-bold',15),GOLD); y+=mm(12)
tw3=(CW-mm(6))//3; th3=mm(40)
covers=[("07-suite-c24-ext.png","사파리 텐트"),("17-d600-ext.png","지오데식 돔"),("22-sig-o-ext.png","시그니처 텐트")]
for i,(fn,lb) in enumerate(covers):
    tx=MX+i*(tw3+mm(3)); im=fit(fn,tw3,th3,'cover'); p.paste(im,(tx,y))
    dc(d,lb,tx+tw3//2,y+th3+mm(4),font('sans-bold',9),GREEN)
y+=th3+mm(12)
d.rectangle([(MX,y),(W-MX,y+mm(18))],fill=BG_GREEN)
feats=["특허 무용접 조인트","KS STK400 프레임","화순 직영 100% 국내 제조","16종 풀 라인업"]
fw=CW//4
for i,ft in enumerate(feats): dc(d,ft,MX+i*fw+fw//2,y+mm(9),font('sans-bold',8),GREEN)
y+=mm(26)
dc(d,"\"현장을 아는 사람이 만든 구조물은 다릅니다.\"",W//2,y,font('serif-bold',14),GREEN); y+=mm(10)
dc(d,"사파리 텐트 5종  ·  지오데식 돔 4종  ·  시그니처 텐트 7종",W//2,y,font('sans',10),GRAY)
dc(d,"010-4337-0582  |  candlejs6@gmail.com  |  wocs.kr",W//2,H-mm(15),font('sans-bold',10),GOLD)
dc(d,"전남 화순군 사평면 유마로 592  |  화순 O4O 쇼룸 방문 예약제",W//2,H-mm(8),font('sans',8),GRAY_D)
d.rectangle([(0,H-mm(2)),(W,H)],fill=GREEN)
pages.append(p)

# === P2: CEO + STRENGTHS ===
p,d=newp(); top_bar(d); y=MY+mm(2)
dc(d,"WOCS — 회사 소개",MX,y,font('serif-bold',22),GREEN,"lm"); y+=mm(9)
gold_line(d,MX,y,MX+mm(55)); y+=mm(7)
col_w=int(CW*0.58)
dc(d,"대표 인사말",MX,y,font('serif-bold',14),GREEN,"lm"); y+=mm(8)
ceo=["안녕하십니까, WOCS 대표 김우성입니다.","",
     "저는 16년간 관공서, 농업시설, 주택, 상가 등","100건 이상의 현장을 직접 설계하고 시공했습니다.",
     "그 경험 위에 WOCS 글램핑 브랜드를 만들었습니다.","",
     "구조물의 본질은 변하지 않습니다.","튼튼한 뼈대, 정확한 시공, 오래 쓸 수 있는 내구성.","",
     "제가 직접 설계하고, 제가 만들고, 제가 시공합니다."]
for ln in ceo:
    if ln=="": y+=mm(2); continue
    dc(d,ln,MX+mm(2),y,font('sans',9),TEXT,"lm"); y+=mm(5.5)
y+=mm(2)
dc(d,"\"모든 현장에 제 이름을 걸겠습니다.\" — 대표 김우성",MX+mm(2),y,font('serif-bold',10),GOLD,"lm")
ry=MY+mm(20); rw=CW-col_w-mm(4); rx=MX+col_w+mm(4)
ri1=fit("46-construction.png",rw,mm(40),'cover'); p.paste(ri1,(rx,ry))
dc(d,"대표 직접 현장 시공",rx+rw//2,ry+mm(40)+mm(3),font('sans',7),GRAY)
ri2=fit("47-factory.png",rw,mm(40),'cover'); p.paste(ri2,(rx,ry+mm(48)))
dc(d,"화순 직영 공장",rx+rw//2,ry+mm(88)+mm(3),font('sans',7),GRAY)
y=max(y+mm(10),MY+mm(100))
gold_line(d,MX,y,W-MX); y+=mm(6)
dc(d,"핵심 경쟁력",MX,y,font('serif-bold',14),GREEN,"lm"); y+=mm(8)
strengths=[("❶ 특허 무용접 조인트","이중 쐐기 가압. 볼트렌치 1개로 완성. 인건비 30%↓"),
           ("❷ 화순 직영 공장","KS STK400 100% 국내 생산. 중간 유통 0원"),
           ("❸ 대표 직접 시공","설계→제작→시공→A/S 전 과정 1인 책임"),
           ("❹ 16종 풀 라인업","커플 글램핑부터 대형 이벤트까지 대응"),
           ("❺ 사계절 운영","4중 단열 + KFI 방염 + IoT 스마트 옵션")]
half=CW//2
for i,(t,desc) in enumerate(strengths):
    sx=MX+mm(2)+(i%2)*half; sy=y+(i//2)*mm(14)
    dc(d,t,sx,sy,font('sans-bold',9),GOLD,"lm")
    dc(d,desc,sx,sy+mm(6),font('sans',8),GRAY,"lm")
ri3=fit("49-showroom-int.png",CW,mm(32),'cover'); sy_img=y+(3)*mm(14)+mm(3); p.paste(ri3,(MX,sy_img))
dc(d,"화순 O4O 쇼룸 — 실물 구조물 직접 확인 가능 (방문 예약제)",MX+CW//2,sy_img+mm(32)+mm(3),font('sans',8),GREEN)
footer(d); pages.append(p)

# === P3: WHY WOCS ===
p,d=newp(); top_bar(d); y=MY+mm(2)
dc(d,"왜 WOCS인가",MX,y,font('serif-bold',22),GREEN,"lm"); y+=mm(9)
gold_line(d,MX,y,MX+mm(55)); y+=mm(7)
dc(d,"글램핑 구조물, WOCS는 이렇게 다릅니다.",MX,y,font('sans',10),TEXT,"lm"); y+=mm(8)
comp=[("비교 항목","WOCS","일반 업체"),("시공 방식","특허 무용접 조인트\n볼트 체결 완성","현장 용접\n3~7일 소요"),
      ("프레임","KS D 3566 STK400\n아연도금 강관","일반 파이프\n규격 미표기"),
      ("생산","화순 직영 공장\n100% 국내 제조","중국 완제품 수입\n또는 OEM 납품"),
      ("중간 유통","대표 직접 설계·생산·시공\n마진 0원","2~3단계 외주\n중간 마진 30%+"),
      ("커버 인증","KFI 방염 인증\nPVC 750~850g/m²","인증 미비\n또는 확인 불가"),
      ("A/S","대표 직접 대응\n부분 교체 가능","연락 두절\n또는 별도 비용")]
cx0,cx1,cx2=MX,MX+mm(26),MX+mm(82)
for ri,(c1,c2,c3) in enumerate(comp):
    hdr=ri==0; rh=mm(11) if hdr else mm(14)
    if hdr: d.rectangle([(MX,y),(W-MX,y+rh)],fill=GREEN)
    elif ri%2==0: d.rectangle([(MX,y),(W-MX,y+rh)],fill=BG_GREEN)
    cy=y+rh//2
    for ci,(txt,cx) in enumerate([(c1,cx0+mm(2)),(c2,cx1+mm(2)),(c3,cx2+mm(2))]):
        lns=txt.split('\n'); ly=cy-(len(lns)-1)*mm(2.5)
        for li,ln in enumerate(lns):
            if hdr: dc(d,ln,cx,ly+li*mm(5),font('sans-bold',8),WHITE,"lm")
            elif ci==1: dc(d,ln,cx,ly+li*mm(5),font('sans-bold',8),GOLD_L,"lm")
            elif ci==0: dc(d,ln,cx,ly+li*mm(5),font('sans',8),GREEN,"lm")
            else: dc(d,ln,cx,ly+li*mm(5),font('sans',8),GRAY_D,"lm")
    d.line([(MX,y+rh),(W-MX,y+rh)],fill=(200,200,200),width=1); y+=rh
y+=mm(6)
dc(d,"\"외주 하청 없는 대표 직접 시공. 이것이 WOCS의 전부입니다.\"",MX+mm(2),y,font('serif-bold',11),GOLD,"lm"); y+=mm(10)
iw3=(CW-mm(6))//3; ih3=mm(38)
for i,(fn,lb) in enumerate([("45-joint-closeup.png","특허 무용접 조인트"),("47-factory1.png","화순 직영 공장"),("48-showroom-ext.png","화순 O4O 쇼룸")]):
    ix=MX+i*(iw3+mm(3)); im=fit(fn,iw3,ih3,'cover'); p.paste(im,(ix,y))
    dc(d,lb,ix+iw3//2,y+ih3+mm(3),font('sans',8),GREEN)
y+=ih3+mm(10)
d.rectangle([(MX,y),(W-MX,y+mm(24))],fill=BG_GREEN)
dc(d,"투자 수익 시뮬레이션 (10동 기준, 참고용)",MX+mm(4),y+mm(4),font('sans-bold',10),GREEN,"lm")
roi=[("초기 투자","약 3~5억원"),("월 매출 예상","1,500~3,000만원"),("투자 회수","12~24개월")]
for i,(k,v) in enumerate(roi):
    rx=MX+mm(4)+i*mm(52); dc(d,k,rx,y+mm(12),font('sans-bold',8),GOLD,"lm"); dc(d,v,rx,y+mm(18),font('sans',8),TEXT,"lm")
footer(d); pages.append(p)

# === PRODUCT HELPER ===
def ppg(title,sub,hero,sub_fn,desc,specs,sell,extras=None):
    p,d=newp(); hh=int(H*0.36)
    h=fit(hero,W,hh,'cover'); p.paste(h,(0,0))
    for gy in range(mm(12)): d.line([(0,hh-mm(12)+gy),(W,hh-mm(12)+gy)],fill=BG)
    dc(d,title,MX+mm(2),hh-mm(20),font('serif-bold',24),WHITE,"lm")
    if sub: dc(d,sub,MX+mm(2),hh-mm(8),font('sans-light',11),GOLD_L,"lm")
    y=hh+mm(3)
    for ln in desc: dc(d,ln,MX,y,font('sans',9),TEXT,"lm"); y+=mm(5.5)
    y+=mm(3)
    sw=int(CW*0.48); iw2=CW-sw-mm(4)
    sy=y
    for si,(lb,val) in enumerate(specs):
        rh=mm(7)
        if si==0: d.rectangle([(MX,sy),(MX+sw,sy+rh)],fill=GREEN)
        elif si%2==0: d.rectangle([(MX,sy),(MX+sw,sy+rh)],fill=BG_GREEN)
        dc(d,lb,MX+mm(2),sy+rh//2,font('sans-bold',8),GOLD if si>0 else WHITE,"lm")
        dc(d,val,MX+mm(20),sy+rh//2,font('sans',8),TEXT if si>0 else WHITE,"lm")
        d.line([(MX,sy+rh),(MX+sw,sy+rh)],fill=(200,200,200),width=1); sy+=rh
    if sub_fn:
        ih2=max(sy-y,mm(42)); si2=fit(sub_fn,iw2,ih2,'cover'); p.paste(si2,(MX+sw+mm(4),y))
    y=max(sy,y+mm(42))+mm(4)
    for pt in sell: dc(d,f"▸ {pt}",MX+mm(2),y,font('sans-bold',8),GOLD_L,"lm"); y+=mm(6)
    if extras and y<H-mm(45):
        y+=mm(3); ew=(CW-mm(6))//3; eh=mm(28)
        for i,fn in enumerate(extras[:3]):
            ex=MX+i*(ew+mm(3)); ei=fit(fn,ew,eh,'cover'); p.paste(ei,(ex,y))
    footer(d); return p

# === P4: SAFARI OVERVIEW ===
p,d=newp(); top_bar(d); y=MY+mm(2)
dc(d,"Ⅰ. 사파리 텐트 (5종)",MX,y,font('serif-bold',22),GOLD,"lm"); y+=mm(9)
gold_line(d,MX,y,MX+mm(75)); y+=mm(7)
dc(d,"검증된 A-프레임 구조. 글램핑장 운영자에게 가장 높은 투자 대비 수익을 제공하는 핵심 라인.",MX,y,font('sans',10),TEXT,"lm"); y+=mm(10)
SC="WOCS__Modular_Glamping_Systems_Architectural_photography_of_a_ace3ea2f-e6c0-4610-9d16-32bfc0611ad3_0.png"
safari=[(SC,"S-Classic","14.7~17.5m²","1~2인","15~20만원"),("04-ex46-ext.png","S-Classic EX","14.7~42.0m²","2~6인","25~35만원"),
        ("07-suite-c24-ext.png","S-Suite","24.0~38.0m²","2~5인","25~35만원"),("11-lodge-e36-ext.png","S-Lodge","36.0~45.6m²","3~6인","30~40만원"),
        ("15-lodge-lx-ext.png","S-Lodge LX","70.0m²","4~6인","30~50만원")]
tw=(CW-mm(8))//3; th=mm(36)
for i,(fn,nm,area,cap,price) in enumerate(safari):
    r,c=i//3,i%3; tx=MX+c*(tw+mm(4)); ty=y+r*(th+mm(18))
    im=fit(fn,tw,th,'cover'); p.paste(im,(tx,ty))
    dc(d,nm,tx+tw//2,ty+th+mm(3),font('sans-bold',9),GREEN)
    dc(d,f"{area} | {cap} | 객단가 {price}",tx+tw//2,ty+th+mm(9),font('sans',7),GRAY)
y+=2*(th+mm(18))+mm(3)
d.rectangle([(MX,y),(W-MX,y+mm(26))],fill=BG_GREEN)
dc(d,"전 모델 공통 사양",MX+mm(4),y+mm(4),font('sans-bold',10),GREEN,"lm")
cmn=["KS D 3566 STK400 아연도금 프레임","PVC 750~850g/m² KFI 방염 인증 커버","특허 무용접 조인트 — 볼트 체결 시공","4중 단열 시스템 — 사계절 운영"]
for i,c in enumerate(cmn):
    cx=MX+mm(4)+(i%2)*mm(76); cy=y+mm(12)+(i//2)*mm(6.5)
    dc(d,f"✓ {c}",cx,cy,font('sans',8),TEXT,"lm")
footer(d); pages.append(p)

# === P5~P9: SAFARI PRODUCTS ===
pages.append(ppg("S-Classic","A-프레임 클래식 사파리 텐트",SC,"내부이미지S.png",
    ["A-프레임 클래식 사파리 텐트. 검증된 수익 모델.","볼트 체결 시공. 가설건축물 인허가 대응.","화순 직영 공장 100% 국내 생산. 중간 유통 0원."],
    [("항목","사양"),("사이즈","A1: 3.5×4.2m / A2: 3.5×5.0m"),("면적","14.7~17.5 m²"),("높이","2.8~3.3 m"),("프레임","KS D 3566 STK400 아연도금"),("커버","PVC 750g/m² · KFI 방염"),("수용","1~2인")],
    ["커플·1인 글램핑 최적 — 객단가 15~20만원","A1/A2 사이즈 선택 — 부지에 맞춤","KS STK400 아연도금 — 15년+ 장기 사용"]))
pages.append(ppg("S-Classic EX","EX15 · EX25 · EX35 · EX46 · EX67","04-ex46-ext.png","05-ex46-int.png",
    ["S-Classic의 확장형 5종. 다인실·패밀리 수요 대응.","최대 42m² — 4인 가족 글램핑장의 핵심 모델."],
    [("항목","사양"),("라인업","EX15 / EX25 / EX35 / EX46 / EX67"),("면적","14.7~42.0 m²"),("높이","2.8~3.8 m"),("프레임","KS D 3566 STK400"),("커버","PVC 750g/m² · KFI 방염")],
    ["5종 사이즈 — 부지에 맞는 선택","최대 42m² 패밀리 → 객단가 25~35만원"],
    ["01-ex15-ext.png","02-ex25-ext.png","06-ex67-ext.png"]))
pages.append(ppg("S-Suite","C24 · C38","07-suite-c24-ext.png","08-suite-c24-int.png",
    ["스위트룸급 프리미엄 사파리 텐트.","C24·C38 두 사이즈. 커플~패밀리 대응.","호텔·펜션 대비 차별화 — 리피트율 상승."],
    [("항목","사양"),("라인업","C24 / C38"),("면적","24.0~38.0 m²"),("높이","3.0~3.5 m"),("프레임","KS D 3566 STK400"),("커버","PVC 750g/m² · KFI 방염"),("수용","2~5인")],
    ["객단가 25~35만원 — 프리미엄 포지셔닝","4중 단열 — 사계절 운영, 비수기 0"],
    ["09-suite-c38-ext.png","10-suite-c38-int.png"]))
pages.append(ppg("S-Lodge","E36 · E46","11-lodge-e36-ext.png","12-lodge-e36-int.png",
    ["로지형 대형 사파리. 리조트급 다실 구성.","로프트 2층 구조 가능. 프라이빗 욕실 옵션."],
    [("항목","사양"),("라인업","E36 / E46"),("면적","36.0~45.6 m²"),("높이","3.5~4.0 m"),("프레임","KS D 3566 STK400"),("커버","PVC 850g/m² · KFI 방염"),("수용","3~6인")],
    ["2층 로프트 → 공간 효율 극대화","객단가 30~40만원 — 투자 회수 가속"],
    ["13-lodge-e46-ext.png","14-lodge-e46-int.png"]))
pages.append(ppg("S-Lodge LX","풀 글라스월 + 2층 로프트","15-lodge-lx-ext.png","16-lodge-lx-int.png",
    ["Lodge의 최상위 럭셔리 모델.","풀 글라스월 + 2층 로프트. 호텔급 프라이빗 공간.","객단가 30~50만원. 투자 회수 5~7개월."],
    [("항목","사양"),("면적","70.0 m²"),("높이","4.5 m (2층 로프트)"),("구조","풀 글라스월 + 로프트"),("프레임","KS D 3566 STK400"),("커버","PVC 850g/m² · KFI 방염"),("수용","4~6인")],
    ["객단가 30~50만원 — 업계 최고 수익","VIP·허니문·기업 워크숍 타겟"]))

# === P10: DOME OVERVIEW ===
p,d=newp(); top_bar(d); y=MY+mm(2)
dc(d,"Ⅱ. 지오데식 돔 (4종)",MX,y,font('serif-bold',22),GOLD,"lm"); y+=mm(9)
gold_line(d,MX,y,MX+mm(75)); y+=mm(7)
dc(d,"지오데식 프레임 × 무용접 조인트. 360° 파노라마 뷰. SNS 바이럴 자동 발생.",MX,y,font('sans',10),TEXT,"lm"); y+=mm(10)
tdw=(CW-mm(6))//3; tdh=mm(42)
for i,(fn,nm,desc) in enumerate([("17-d600-ext.png","D600","직경 6m | 28.3m² | 커플"),("19-d800-ext.png","D800","직경 8m | 50.3m² | 패밀리"),("21-d-pro-ext.png","D-Pro","직경 10m | 78.5m² | 이벤트")]):
    tx=MX+i*(tdw+mm(3)); im=fit(fn,tdw,tdh,'cover'); p.paste(im,(tx,y))
    dc(d,nm,tx+tdw//2,y+tdh+mm(3),font('sans-bold',9),GREEN); dc(d,desc,tx+tdw//2,y+tdh+mm(9),font('sans',7),GRAY)
y+=tdh+mm(16)
for i,(fn,lb) in enumerate([("18-d600-int.png","D600 내부"),("20-d800-int.png","D800 내부"),("내부이미지D.png","돔 인테리어")]):
    tx=MX+i*(tdw+mm(3)); im=fit(fn,tdw,mm(32),'cover'); p.paste(im,(tx,y))
    dc(d,lb,tx+tdw//2,y+mm(32)+mm(3),font('sans',7),GRAY)
y+=mm(32)+mm(10)
d.rectangle([(MX,y),(W-MX,y+mm(20))],fill=BG_GREEN)
for i,b in enumerate(["투명 패널·PVC·폴리카보네이트 선택","360° 파노라마 뷰 → SNS 바이럴","별 관측·이벤트·레스토랑 다용도","WOCS 특허 무용접 조인트 적용"]):
    bx=MX+mm(4)+(i%2)*mm(76); by=y+mm(4)+(i//2)*mm(6.5); dc(d,f"✓ {b}",bx,by,font('sans',8),TEXT,"lm")
footer(d); pages.append(p)

# === P11: SIGNATURE OVERVIEW ===
p,d=newp(); top_bar(d); y=MY+mm(2)
dc(d,"Ⅲ. 시그니처 텐트 (7종)",MX,y,font('serif-bold',22),GOLD,"lm"); y+=mm(9)
gold_line(d,MX,y,MX+mm(75)); y+=mm(7)
dc(d,"독자 디자인. 입지와 컨셉에 맞는 유일무이한 외관. 전 모델 디자인특허 출원 예정.",MX,y,font('sans',10),TEXT,"lm"); y+=mm(10)
sw4=(CW-mm(9))//4; sh4=mm(30)
sigs=[("22-sig-o-ext.png","Sig-O Cocoon","코쿤 | 44m²"),("24-sig-a-ext.png","Sig-A Sailing","세일링 | 30m²"),
      ("26-sig-p-ext.png","Sig-P Boat","보트캐빈 | 28m²"),("28-sig-h-ext.png","Sig-H Hexa","헥사티피 | 32m²"),
      ("30-sig-t-single-ext.png","Sig-T Peak","첨탑3종 | 25~50m²"),("35-sig-q-ext.png","Sig-Q Cube","큐브 | 12m²"),
      ("37-sig-m-s60-ext.png","Sig-M Modular","모듈러 | 무제한")]
for i,(fn,nm,desc) in enumerate(sigs):
    r,c=i//4,i%4; tx=MX+c*(sw4+mm(3)); ty=y+r*(sh4+mm(15))
    im=fit(fn,sw4,sh4,'cover'); p.paste(im,(tx,ty))
    dc(d,nm,tx+sw4//2,ty+sh4+mm(3),font('sans-bold',7),GREEN); dc(d,desc,tx+sw4//2,ty+sh4+mm(8),font('sans',7),GRAY)
y+=2*(sh4+mm(15))+mm(3)
siw=(CW-mm(9))//4; sih=mm(26)
for i,(fn,lb) in enumerate([("23-sig-o-int.png","Cocoon"),("25-sig-a-int.png","Sailing"),("29-sig-h-int.png","Hexa Tipi"),("36-sig-q-int.png","Cube")]):
    tx=MX+i*(siw+mm(3)); im=fit(fn,siw,sih,'cover'); p.paste(im,(tx,y))
    dc(d,lb,tx+siw//2,y+sih+mm(3),font('sans',7),GRAY)
y+=sih+mm(8)
d.rectangle([(MX,y),(W-MX,y+mm(14))],fill=BG_GREEN)
dc(d,"전 모델: WOCS 특허 무용접 조인트 적용 | KS STK400 프레임 | 화순 직영 공장 100% 국내 제조",MX+CW//2,y+mm(7),font('sans-bold',8),GREEN)
footer(d); pages.append(p)

# === P12~15: SIG PRODUCTS ===
pages.append(ppg("Sig-O Cocoon","유선형 코쿤 44m²","22-sig-o-ext.png","23-sig-o-int.png",
    ["유선형 코쿤 실루엣의 44m² 대형 텐트.","곡면 프레임이 하중을 균등 분산.","디자인특허 출원 — WOCS 독점 모델."],
    [("항목","사양"),("형태","코쿤"),("면적","44 m²"),("크기","11.0×4.0m"),("높이","3.2 m"),("수용","4~6인")],
    ["디자인특허 출원 — WOCS 독점 모델","44m² 대형 패밀리 → 객단가 35~50만원"]))
pages.append(ppg("Sig-H Hexa Tipi","6각형 티피 구조","28-sig-h-ext.png","29-sig-h-int.png",
    ["6각형 티피. 헥사곤 하중 균등 분산.","적설 하중 대비. 동계 운영 설계."],
    [("항목","사양"),("형태","헥사티피"),("면적","32 m²"),("크기","6.5×5.5m"),("높이","3.8 m"),("수용","2~4인")],
    ["산악지역 → 동계 가동률 확보","전통+현대 조화 → 차별화 포토존"]))
pages.append(ppg("Sig-T Peak Series","싱글 · 트윈 · 더블 피크","30-sig-t-single-ext.png","34-sig-t-double-int.png",
    ["첨탑형 지붕 — 빗물·적설 배출 최적.","피크 수 선택으로 25~50m² 면적 확장."],
    [("항목","사양"),("형태","싱글/트윈/더블 피크"),("면적","25~50 m²"),("높이","3.5~4.5 m"),("수용","2~8인")],
    ["3종 라인업 → 수요에 맞춤 확장","웨딩·이벤트 겸용 → 주중 매출"],
    ["32-sig-t-twin-ext.png","33-sig-t-double-ext.png","31-sig-t-single-int.png"]))
pages.append(ppg("Sig-M Modular","S60 · S100 · S190 · L150","37-sig-m-s60-ext.png","41-sig-m-int.png",
    ["단위 모듈 조합 → 면적 무제한 확장.","레스토랑·웨딩홀·대형 이벤트까지."],
    [("항목","사양"),("시스템","S60 / S100 / S190 / L150"),("면적","최소 60 ~ 무제한"),("구조","모듈러 조합"),("수용","소규모~대규모")],
    ["무한 확장 모듈 → 규모 제한 없음","상업 공간 전환 → 매출 극대화"],
    ["38-sig-m-s100-ext.png","39-sig-m-s190-ext.png","40-sig-m-l150-ext.png"]))

# === P16: TECHNOLOGY ===
p,d=newp(); top_bar(d); y=MY+mm(2)
dc(d,"핵심 기술",MX,y,font('serif-bold',22),GOLD,"lm"); y+=mm(9)
gold_line(d,MX,y,MX+mm(55)); y+=mm(6)
ji=fit("45-joint-closeup.png",CW,mm(42),'cover'); p.paste(ji,(MX,y)); y+=mm(42)+mm(5)
techs=[("특허 무용접 다방향 유니버설 조인트","이중 쐐기 가압. 5방향 독립 잠금. 볼트렌치 1개 완성.\n인건비 30%↓, 공기 1/3↓. 열변형·도금 손상 차단. 재조립 가능."),
       ("KS STK400 구조용 강관","전 모델 KS D 3566 규격. 인장·항복강도 확보.\n용융아연도금. 부식 저항. 15년+ 장기 사용 설계."),
       ("4중 단열 시스템","외피(PVC) + 단열층(XPS/EPE) + 내피(방염) + 에어갭.\n동계 영하 15°C 실내 온도 유지. 하계 차열 효과."),
       ("KFI 방염 인증","한국소방산업기술원 방염 인증 원단.\n야영장업 등록·가설건축물 인허가 필수 요건 충족.")]
for t,desc in techs:
    dc(d,t,MX+mm(2),y,font('sans-bold',10),GREEN,"lm"); y+=mm(6)
    for ln in desc.split('\n'): dc(d,ln,MX+mm(4),y,font('sans',8),TEXT,"lm"); y+=mm(5)
    y+=mm(3)
y+=mm(2); gold_line(d,MX,y,W-MX); y+=mm(5)
dc(d,"가구·옵션 (턴키 제공 가능)",MX,y,font('sans-bold',10),GREEN,"lm"); y+=mm(6)
fw2=(CW-mm(9))//4; fh2=mm(22)
for i,(fn,lb) in enumerate([("53-furniture-bed.png","퀸 침대"),("56-furniture-chair.png","라운지 체어"),("65-furniture-aircon.png","냉난방기"),("44-modular-deck.png","데크 시스템")]):
    fx=MX+i*(fw2+mm(3)); bg=Image.new("RGB",(fw2,fh2),CARD); fi=fit(fn,fw2,fh2,'contain')
    ox=(fw2-fi.size[0])//2; oy=(fh2-fi.size[1])//2; bg.paste(fi,(ox,oy)); p.paste(bg,(fx,y))
    dc(d,lb,fx+fw2//2,y+fh2+mm(3),font('sans',7),GRAY)
footer(d); pages.append(p)

# === P17: PROCESS ===
p,d=newp(); top_bar(d); y=MY+mm(2)
dc(d,"시공 프로세스",MX,y,font('serif-bold',22),GOLD,"lm"); y+=mm(9)
gold_line(d,MX,y,MX+mm(55)); y+=mm(8)
proc=[("01","상담 · 부지 분석","전화/카카오톡/이메일. 부지 위치, 면적, 동수, 타겟 파악.\n1차 모델·배치 제안."),
      ("02","현장 실측 · 3D 가설계","대표 직접 방문. 경사도, 배수, 진입로, 전기·수도 확인.\n3D 가설계·배치도 무료 제공."),
      ("03","견적 · 계약","모델 단가 + 기초 + 배관·전기 + 데크 + 가구.\n2~3 옵션 비교. 추가비용 사전 고지."),
      ("04","인허가 지원","가설건축물 축조신고, 야영장업 등록.\n도면·서류 지원. 관할 지자체 기준 안내."),
      ("05","제조 · 제작","화순 공장에서 프레임 절단·도금·조인트 가공.\n커버 재단. 2~4주. 진행 사진 공유."),
      ("06","현장 시공","기초→프레임→조인트→커버→배수·전기→단열→마감.\n대표 직접 시공. 현장 변경 즉시 대응."),
      ("07","검수 · 인도","최종 검수. 사용법·관리법·교체시기 안내.\n유지관리 상담 지속 제공.")]
for num,title,desc in proc:
    cx=MX+mm(7)
    d.ellipse([(cx-mm(4.5),y-mm(4.5)),(cx+mm(4.5),y+mm(4.5))],fill=GREEN)
    dc(d,num,cx,y,font('sans-bold',8),GOLD)
    dc(d,title,MX+mm(15),y-mm(1),font('sans-bold',10),GREEN,"lm")
    ty=y+mm(5.5)
    for ln in desc.split('\n'): dc(d,ln,MX+mm(15),ty,font('sans',8),GRAY,"lm"); ty+=mm(5)
    y=ty+mm(4)
y+=mm(2)
ci=fit("46-construction.png",CW,mm(35),'cover'); p.paste(ci,(MX,y))
dc(d,"대표 직접 현장 시공 — 외주 하청 0건",MX+CW//2,y+mm(35)+mm(3),font('sans-bold',8),GREEN)
footer(d); pages.append(p)

# === P18: CTA ===
p,d=newp()
nh=int(H*0.32); night=fit("52-night-scene.png",W,nh,'cover'); p.paste(night,(0,0))
dc(d,"\"실제 시공된 구조물을 눈으로 보고, 손으로 만져보십시오.\"",W//2,nh-mm(8),font('serif-bold',13),WHITE)
y=nh+mm(8)
dc(d,"상담 안내",MX,y,font('serif-bold',16),GREEN,"lm"); y+=mm(9)
for q,a in [("\"글램핑장 처음 준비. 어디서부터?\"","→ 부지 선정~인허가~시공~운영 전 과정 상담"),
            ("\"견적은 어떻게?\"","→ 부지 위치+동수만 알려주시면 당일 개략 견적"),
            ("\"쇼룸에서 실물 확인?\"","→ 예. 방문 예약 후 프레임·커버·조인트 직접 확인"),
            ("\"중국 OEM?\"","→ 조인트 브라켓 OEM 가능. 별도 상담")]:
    dc(d,q,MX+mm(2),y,font('sans-bold',9),GREEN,"lm"); y+=mm(6)
    dc(d,a,MX+mm(4),y,font('sans',8),GRAY,"lm"); y+=mm(7)
y+=mm(3); gold_line(d,MX,y,W-MX); y+=mm(6)
d.rectangle([(MX,y),(W-MX,y+mm(42))],fill=GREEN); cy=y+mm(6)
dc(d,"WOCS  |  우성어닝천막공사캠프시스템",W//2,cy,font('sans-bold',12),GOLD_L); cy+=mm(8)
dc(d,"대표 김우성  |  010-4337-0582",W//2,cy,font('sans-bold',11),WHITE); cy+=mm(7)
dc(d,"candlejs6@gmail.com  |  wocs.kr",W//2,cy,font('sans',10),GOLD_L); cy+=mm(7)
dc(d,"전남 화순군 사평면 유마로 592  |  방문 상담 예약제",W//2,cy,font('sans',9),(180,210,180)); cy+=mm(6)
dc(d,"블로그: blog.naver.com/glampingtentgo | 인스타: @woosung_tent | 유튜브: @countrydiy",W//2,cy,font('sans',7),GRAY_D)
y+=mm(48)
ctas=["무료 3D 가설계 받기","현장 사진으로 견적 받기","화순 쇼룸 방문 예약","투자 수익 시뮬레이션"]
bw=(CW-mm(9))//4
for i,ct in enumerate(ctas):
    bx=MX+i*(bw+mm(3)); d.rectangle([(bx,y),(bx+bw,y+mm(9))],outline=GOLD,width=2)
    dc(d,ct,bx+bw//2,y+mm(4.5),font('sans-bold',7),GOLD)
y+=mm(16)
# Showroom + resort mood
mw=(CW-mm(4))//2; mh=mm(30)
m1=fit("48-showroom-ext.png",mw,mh,'cover'); p.paste(m1,(MX,y))
m2=fit("50-resort-mountain.png",mw,mh,'cover'); p.paste(m2,(MX+mw+mm(4),y))
dc(d,"화순 O4O 쇼룸",MX+mw//2,y+mh+mm(3),font('sans',7),GRAY)
dc(d,"WOCS 글램핑 리조트 이미지",MX+mw+mm(4)+mw//2,y+mh+mm(3),font('sans',7),GRAY)
footer(d); pages.append(p)

# === P19: BACK COVER (no white gradient) ===
p,d=newp()
resort=fit("50-resort-mountain3.png",W,H,'cover'); p.paste(resort,(0,0))
band_y=H//2-mm(38); band_h=mm(76)
band=Image.new("RGBA",(W,band_h),(27,67,50,210))
p_rgba=p.convert("RGBA"); p_rgba.paste(band,(0,band_y),band)
p=p_rgba.convert("RGB"); d=ImageDraw.Draw(p)
cy=band_y+mm(8)
dc(d,"WOCS",W//2,cy,font('serif-bold',44),GOLD); cy+=mm(16)
dc(d,"우성어닝천막공사캠프시스템",W//2,cy,font('sans-medium',13),WHITE); cy+=mm(10)
dc(d,"직접 설계 · 제작 · 시공하는 프리미엄 글램핑",W//2,cy,font('sans-bold',13),GOLD_L); cy+=mm(10)
gold_line(d,W//2-mm(28),cy,W//2+mm(28)); cy+=mm(7)
dc(d,"010-4337-0582  |  candlejs6@gmail.com  |  wocs.kr",W//2,cy,font('sans',10),WHITE); cy+=mm(7)
dc(d,"전남 화순군 사평면 유마로 592",W//2,cy,font('sans-light',9),GOLD_L)
dc(d,"\"모든 현장에 제 이름을 걸겠습니다.\" — 대표 김우성",W//2,H-mm(18),font('serif-bold',12),WHITE)
d.rectangle([(0,0),(W,mm(2))],fill=GREEN)
d.rectangle([(0,H-mm(2)),(W,H)],fill=GREEN)
pages.append(p)

# === SAVE ===
print(f"Saving {len(pages)} pages...")
pages[0].save(OUT,save_all=True,append_images=pages[1:],resolution=DPI)
sz=os.path.getsize(OUT)
print(f"Done: {OUT} ({sz//1024} KB, {len(pages)} pages)")
