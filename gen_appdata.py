#!/usr/bin/env python3
import re, json, math, os

BASE="/Users/hecht/Library/Mobile Documents/com~apple~CloudDocs/NanoClaw/outputs"
ACC=os.path.join(BASE,"alpe_adria_gpx_accommodation_nature")
QUAL=os.path.join(BASE,"alpe_adria_gpx_quality")
OUT=os.path.join(BASE,"alpe_adria_doc_updated","app")
os.makedirs(OUT, exist_ok=True)

def pts(path):
    if not os.path.exists(path): return []
    t=open(path,encoding="utf-8").read()
    return [(float(a),float(b)) for a,b in re.findall(r'<trkpt lat="([-\d.]+)" lon="([-\d.]+)"',t)]

def downsample(p,maxn=140):
    if len(p)<=maxn: return p
    step=len(p)/maxn
    out=[p[int(i*step)] for i in range(maxn)]
    if out[-1]!=p[-1]: out.append(p[-1])
    return out

def haversine(a,b):
    R=6371000;la1,lo1=map(math.radians,a);la2,lo2=map(math.radians,b)
    dla=la2-la1;dlo=lo2-lo1
    h=math.sin(dla/2)**2+math.cos(la1)*math.cos(la2)*math.sin(dlo/2)**2
    return 2*R*math.asin(math.sqrt(h))

def tracklen(p):
    return round(sum(haversine(p[i],p[i+1]) for i in range(len(p)-1))/1000,1)

# day -> gpx track(s) (lodging-to-lodging bike portions)
DAY_GPX={
 "D2":[os.path.join(ACC,"D2_VillachHostel_TarvisioSchaefer.gpx")],
 "D3":[os.path.join(ACC,"D3_TarvisioSchaefer_CasaBlissVenzone.gpx")],
 "D4":[os.path.join(ACC,"D4_CasaBlissVenzone_UdineSunset42.gpx")],
 "D5":[os.path.join(ACC,"D5_UdineSunset42_GradoRivaFoscolo.gpx")],
 "D7":[os.path.join(ACC,"D7b_TriesteFerry_PortorozKorotan.gpx")],
 "D9":[os.path.join(ACC,"D9a_PortorozKorotan_TriesteCentrale.gpx")],
 "D10":[os.path.join(ACC,"D10_StaraGoGorizia_BlueHouseCiginj.gpx")],
 "D11":[os.path.join(ACC,"D11a_BlueHouseCiginj_Kobarid.gpx"),os.path.join(ACC,"D11b_Kolovrat_BlueHouseCiginj.gpx")],
}

tracks={}
for d,files in DAY_GPX.items():
    allp=[]
    for f in files: allp+=pts(f)
    tracks[d]=downsample(allp,140) if allp else []

def endpoint(path, which):
    p=pts(path)
    if not p: return None
    return list(map(lambda x:round(x,5), p[0] if which=="start" else p[-1]))

# accommodation coords from lodging-to-lodging endpoints
acc_coord={
 "D1":endpoint(os.path.join(ACC,"D2_VillachHostel_TarvisioSchaefer.gpx"),"start"),
 "D2":endpoint(os.path.join(ACC,"D2_VillachHostel_TarvisioSchaefer.gpx"),"end"),
 "D3":endpoint(os.path.join(ACC,"D3_TarvisioSchaefer_CasaBlissVenzone.gpx"),"end"),
 "D4":endpoint(os.path.join(ACC,"D4_CasaBlissVenzone_UdineSunset42.gpx"),"end"),
 "D5-6":endpoint(os.path.join(ACC,"D5_UdineSunset42_GradoRivaFoscolo.gpx"),"end"),
 "D7-8":endpoint(os.path.join(ACC,"D7b_TriesteFerry_PortorozKorotan.gpx"),"end"),
 "D9":endpoint(os.path.join(ACC,"D9b_GoriziaCentrale_StaraGo.gpx"),"end"),
 "D10-11":endpoint(os.path.join(ACC,"D10_StaraGoGorizia_BlueHouseCiginj.gpx"),"end"),
}

acc=json.load(open(os.path.join(BASE,"alpe_adria_doc_updated","accommodations.json")))
for a in acc:
    a["coord"]=acc_coord.get(a["dni"])

# ---- day metadata (from docx) ----
DAYS=[
 {"id":"D1","date":"16.7.","title":"Žilina/BB → Villach","type":"presun","km":None,"up":None,"down":None,
  "desc":"Autami cez Trnavu do Villachu (~6 h). AT diaľničná známka 10 dní €12.80 — kúpiť vopred online.",
  "tips":["Stretnutie pri Trnave"],"warn":["Kúpiť AT vignette vopred: shop.asfinag.at"],"food":[],"komoot":None},
 {"id":"D2","date":"17.7.","title":"Villach → Tarvisio IT","type":"zmiešané","km":44.7,"up":340,"down":80,
  "desc":"Pozdĺž Gailu cez Arnoldstein (kláštor) a Thörl-Maglern (hranica AT→IT pri Coccau) na ex-železničnú cyklotrasu do Tarvisia.",
  "tips":["Arnoldstein — ruiny benediktínskeho opátstva (12. stor.)"],
  "warn":["Coccau (hranica): pár km zdieľaných s autami, v júli rušno — drž bike pruh"],
  "food":["Tarvisio: prvá talianska káva, aperitivo s tramezzini"],"komoot":"https://www.komoot.com/tour/900346118"},
 {"id":"D3","date":"18.7.","title":"Tarvisio → Venzone","type":"cyklotrasa","km":57.7,"up":100,"down":580,
  "desc":"Najkrajší deň. 100% ex-železnica: Camporosso, Malborghetto, kaňon Fella, Chiusaforte. Záver: stredoveká Venzone (UNESCO). Takmer celé z kopca.",
  "tips":["Malborghetto — opevnený Palazzo Veneziano (14. stor.), priamo na trase"],
  "warn":["TUNELY: viacero, najdlhší ~400 m — POVINNÉ svetlá vpred aj vzad, 2 zadné blikačky; okuliare dole pred vstupom"],
  "food":["Venzone: cjarsoni, Montasio; kúpiť prosciutto San Daniele DOP"],"komoot":"https://www.komoot.com/tour/907978879"},
 {"id":"D4","date":"19.7.","title":"Venzone → Udine","type":"zmiešané","km":57,"up":200,"down":310,
  "desc":"Gemona del Friuli (panoráma Júlskych Álp), rovina Friuli vinicami. Udine — Piazza della Libertà, Castello.",
  "tips":["Gemona — katedrála S. Maria Assunta (13. stor.), stúpanie do centra ~100 m"],
  "warn":[],"food":["Udine: Frico, cjarsoni, Tajut — najlepšia gastro zastávka trasy"],"komoot":"https://www.komoot.com/tour/943400539"},
 {"id":"D5","date":"20.7.","title":"Udine → Grado","type":"cesta","km":58.7,"up":30,"down":130,
  "desc":"Palmanova (hviezdicová pevnosť UNESCO), Aquileia (rímske UNESCO + bazilika s mozaikami), záverečná cyklotrasa k moru v Grade.",
  "tips":["Aquileia (~0 km na trase): rímske ruiny + mozaiky 4. stor., počítať 1–1.5 h"],
  "warn":["Grado v júli najrušnejšie letovisko — rezervovať vopred; loď Glimble rezervovať IHNEĎ"],
  "food":["Grado: Boreto alla Gradese; L'Approdo (sunset, rezervovať)"],"komoot":"https://www.komoot.com/tour/944296889"},
 {"id":"D6","date":"21.7.","title":"VOĽNO — Grado","type":"voľno","km":None,"up":None,"down":None,
  "desc":"Oddych na ostrove. Bazilika sv. Eufémie (mozaiky), ostrov Barbana (loďkou), Aquileia (12 km).",
  "tips":["Ostrov Barbana — kláštor, loďkou 15 min"],"warn":[],"food":["Boreto alla Gradese; Trattoria Alla Borsa"],"komoot":None},
 {"id":"D7","date":"22.7.","title":"Trieste → Portorož","type":"cyklotrasa","km":42,"up":180,"down":180,
  "desc":"Ráno loď Grado→Trieste (Glimble). Pobrežná EV8/Parenzana: Muggia (hranica IT→SI), Koper, Izola, Portorož. 2 noci.",
  "tips":["Trieste: Piazza Unità, espresso na Piazza"],
  "warn":["Muggia–Koper: pár km po hlavnej ceste; EV8 miestami slabo značená — GPS nutnosť","PLÁN B: loď plná → bike Grado→Monfalcone (~20 km) + Trenitalia do Trieste"],
  "food":["Trieste: Caffè San Marco; Jota, gulaš alla triestina"],"komoot":None},
 {"id":"D8","date":"23.7.","title":"VOĽNO — Portorož","type":"voľno","km":None,"up":None,"down":None,
  "desc":"Oddych pri mori. Piran (4 km, Tartiniho námestie), Strunjan (cliff walk), Sečovlje soľné panvy.",
  "tips":["Piran — najkrajšie mestečko slovinského pobrežia"],"warn":[],"food":["Piran: Stara Gostilna; Malvazija + Refošk"],"komoot":None},
 {"id":"D9","date":"24.7.","title":"Portorož → Trieste → vlak → Gorizia","type":"logistika","km":42,"up":180,"down":180,
  "desc":"Posledné ráno pri mori. EV8 Portorož→Trieste (~42 km), potom vlak Trieste Centrale→Gorizia (~50 min). Gorizia=Nova Gorica (Schengen).",
  "tips":["Trieste: posledné espresso na Piazza Unità"],
  "warn":["Trenitalia: max 4 bicykle/vlak, overiť piktogram 🚲, rezervovať deň vopred","CUT-OFF: do 13:00 na Trieste Centrale, inak ďalší vlak (jazdia každých ~30–60 min do 22:30)"],
  "food":["Nova Gorica: Rebula víno (Goriška Brda)"],"komoot":None},
 {"id":"D10","date":"25.7.","title":"Nova Gorica/Solkan → Tolmin","type":"cyklotrasa","km":38,"up":200,"down":50,
  "desc":"Vstup do Soče. Solkan (najdlhší kamenný oblúkový most v Európe), pozdĺž smaragdovej Soče po Bohinjskej žel. Most na Soči (tyrkysové jazero). Tolmin — basecamp 2 noci.",
  "tips":["Tolminska korita (~2 km): divoké rokliny, smaragdová voda","NABI bicykle na 100% — večer dobíjaš na D11"],
  "warn":[],"food":["Tolmin: Labrca; sočský pstruh"],"komoot":None},
 {"id":"D11","date":"26.7.","title":"Tolmin → Kobarid → Kolovrat","type":"cyklotrasa","km":46,"up":200,"down":920,
  "desc":"Najšpecifickejší deň. Tolmin→Kobarid (16 km), shuttle na Kolovrat (~1100 m, preskočíš 940 m výstup), 4 km panorámy + WW1 pamätníky, dlhý zostup (~30 km, ~900 m dole).",
  "tips":["Kozjak vodopád (~3 km detour z Kobaridu): jaskynný vodopád — NEZABUDNÚŤ","Batérie na 100% — zostup šetrí, výstup rieši shuttle"],
  "warn":["SHUTTLE Kolovrat (Positive Sport) rezervovať 2–3 dni vopred","CUT-OFF: ráno bez potvrdeného shuttle alebo vietor >40 km/h na hrebeni → Plán B (Kozjak + kúpanie + Topli Val)","POČASIE Kolovrat: Windy/Meteoblue bod 46.24°N,13.52°E"],
  "food":["Kobarid: Topli Val (sočské ryby); Hiša Polonka; Hiša Franko (3* Michelin)"],"komoot":None},
 {"id":"D12","date":"27.7.","title":"Tolmin → Jesenice → Villach","type":"presun","km":None,"up":None,"down":None,
  "desc":"Bohinjská žel. cez tunel pod Júlskymi Alpami (6341 m) do Jeseníc, prestup ÖBB do Villachu (~30 min). Autami domov.",
  "tips":[],"warn":["Bicykle na Bohinjskej žel.: len motorailvagón, 30 miest — REZERVOVAŤ VOPRED (SŽ)","CUT-OFF: zvoľ ranný vlak 7:00–9:00 a rezervuj naň miesta"],"food":[],"komoot":None},
]

# attach accommodation + coords to days
acc_by_dni={a["dni"]:a for a in acc}
def acc_for(dayid):
    for key,a in acc_by_dni.items():
        days=re.findall(r'D(\d+)',key)
        if str(int(dayid[1:])) in [str(int(x)) for x in days]:
            return a
    return None
for d in DAYS:
    a=acc_for(d["id"])
    d["acc"]=a["miesto"] if a else None
    d["accCoord"]=a.get("coord") if a else None
    d["track"]=tracks.get(d["id"],[])
    if d["track"]: d["trackKm"]=tracklen([tuple(p) for p in d["track"]])

# ---- POIs with coords (real where possible) ----
def along(dayid, frac):
    t=tracks.get(dayid,[])
    if not t: return None
    return [round(x,5) for x in t[int(len(t)*frac)]]

POIS=[]
# accommodations as POIs
for a in acc:
    if a.get("coord"):
        POIS.append({"name":a["miesto"].split("/")[-1].strip()[:34],"type":"ubytko","day":a["dni"],"coord":a["coord"],
                     "info":(a.get("bike_storage") or "")[:80]})
# key route POIs (approx flagged)
POIS+=[
 {"name":"Hranica AT→IT (Coccau)","type":"hranica","day":"D2","coord":along("D2",0.62),"info":"prechod, bike pruh"},
 {"name":"Malborghetto","type":"vyhlad","day":"D3","coord":along("D3",0.30),"info":"Palazzo Veneziano (14. st.)"},
 {"name":"Tunel (ex-železnica)","type":"tunel","day":"D3","coord":along("D3",0.45),"info":"~400 m — ZAPNI SVETLÁ (približná poloha)"},
 {"name":"Chiusaforte","type":"zastavka","day":"D3","coord":along("D3",0.60),"info":"hradná ruina"},
 {"name":"Gemona del Friuli","type":"vyhlad","day":"D4","coord":along("D4",0.25),"info":"katedrála 13. st."},
 {"name":"Aquileia","type":"vyhlad","day":"D5","coord":along("D5",0.55),"info":"rímske UNESCO + mozaiky"},
 {"name":"Hranica IT→SI (Muggia)","type":"hranica","day":"D7","coord":along("D7",0.25),"info":"EV8 pobrežie"},
 {"name":"Most na Soči","type":"vyhlad","day":"D10","coord":along("D10",0.80),"info":"tyrkysové jazero"},
 {"name":"Kobarid (shuttle)","type":"zastavka","day":"D11","coord":along("D11",0.35),"info":"shuttle na Kolovrat"},
 {"name":"Kozjak vodopád (detour)","type":"vyhlad","day":"D11","coord":along("D11",0.30),"info":"~3 km odbočka"},
]
POIS=[p for p in POIS if p.get("coord")]

emergency={
 "AT":{"general":"112","mountain":"140"},"IT":{"general":"112","ambulance":"118"},"SI":{"general":"112"}
}
reservations=[
 {"day":"D1","when":"do 16.7.","what":"AT diaľničná známka (10 dní €12.80)","url":"https://shop.asfinag.at/en","status":"todo"},
 {"day":"D7","when":"vopred","what":"Loď Grado→Trieste (Glimble, max 25 bikes)","url":"https://glimble.it","status":"todo"},
 {"day":"D9","when":"deň vopred","what":"Trenitalia Trieste→Gorizia (max 4 bikes)","url":"https://www.thetrainline.com/en/train-times/trieste-to-gorizia","status":"todo"},
 {"day":"D11","when":"2–3 dni vopred","what":"Shuttle Kolovrat (Positive Sport)","url":"https://positive-sport.com/","status":"todo"},
 {"day":"D12","when":"vopred","what":"Bohinjská žel. motorail (30 bike miest)","url":"https://potniski.sz.si/en/","status":"todo"},
 {"day":"D12","when":"vopred","what":"ÖBB Jesenice→Villach (€3/bike)","url":"https://www.oebb.at/en/","status":"todo"},
]
# accommodation payment cut-offs
acc_cutoffs=[
 {"day":"D7-8","when":"do 7.7.2026","what":"Portorož Apartma Karmen — NEZAPLATENÉ €507, rozhodnúť/zaplatiť","status":"warn"},
 {"day":"D3","when":"čoskoro","what":"Venzone Casa Bliss — dovolať a potvrdiť (platba na mieste)","status":"warn"},
 {"day":"D2","when":"do 15.7.","what":"Tarvisio Schaefer — voľný storno €0 (možná zmena na 2a do 10.7.)","status":"info"},
]

TRIP={"meta":{"title":"Alpe Adria 2026","people":["Petr & Paja","Draho & Zuzka"],
      "start":"2026-07-16","end":"2026-07-27","totalKm":386.1,
      "accTotal":"2132,43","accPerPerson":"533,11"},
      "days":DAYS,"acc":acc,"pois":POIS,"emergency":emergency,
      "reservations":reservations,"accCutoffs":acc_cutoffs}

open(os.path.join(OUT,"data.js"),"w",encoding="utf-8").write("window.TRIP="+json.dumps(TRIP,ensure_ascii=False)+";")
print("data.js written:",os.path.getsize(os.path.join(OUT,"data.js")),"bytes")
print("days:",len(DAYS),"| acc:",len(acc),"| pois:",len(POIS),"| tracks:",{k:len(v) for k,v in tracks.items()})
print("acc coords:",{a['dni']:a.get('coord') for a in acc})
