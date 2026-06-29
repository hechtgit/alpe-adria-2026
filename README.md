# Alpe Adria 2026 — MVP appka

Offline-first cockpit pre 4 ľudí. Tenká vrstva: appka nerenderuje mapy ani turn-by-turn — na navigáciu odovzdáva mapy.cz/Komoot. Všetky dáta sú embedded (funguje offline).

## Súbory
- `index.html` — celá appka (CSS + JS inline), 4 taby: Dnes · Mapa · Plán · SOS.
- `data.js` — dátový balík (12 dní, 8 ubytovaní, 18 POI, GPX stopy) generovaný z Wordu + Sheets + GPX.
- `manifest.json`, `sw.js` — PWA (inštalovateľná na home-screen, offline cache).

## Spustiť lokálne
```
cd .../alpe_adria_doc_updated/app
python3 -m http.server 8799
```
Otvor `http://localhost:8799` (alebo na mobile v rovnakej WiFi `http://<IP-mac>:8799`).

## Nasadiť pre 4 telefóny (1 link)
Nahrať priečinok `app/` na statický hosting (Netlify drop, GitHub Pages, Cloudflare Pages). Každý otvorí link → „Pridať na plochu" → appka beží offline. Stiahnuť pred odchodom na WiFi.

## Funkcie (MVP)
- **Dnes**: aktuálny deň, etapa, **proximity „pred nami po trase"** (GPS alebo simulácia), cut-offy, ubytko (s tel. + skladovaním bicyklov), tipy.
- **Mapa**: schematický GPX náhľad + poloha + „Otvor v mapy.cz/Komoot".
- **Plán**: rezervácie & cut-offy (vrátane platobných termínov ubytovaní), zoznam ubytovaní, itinerár 12 dní.
- **SOS**: núdzové čísla po krajinách (AT 140 / IT 118 / SI 112, tap = volať), zdieľanie polohy SMS-kou, skupinový check-in (lokálny).

## Regenerovať dáta
Po zmene Wordu/Sheets/GPX: `python3 gen_appdata.py` (skript v scratchpade / pri zdroji) → prepíše `data.js`.

## Známe obmedzenia (na doladenie)
- POI ako tunel/hranica/Kozjak majú **približnú polohu** (odvodené z trasy) — pred cestou spresniť reálnymi súradnicami.
- mapy.cz odkaz vedie na bod (stred etapy/ubytko); turn-by-turn po GPX otestovať pre každý úsek.
- D6/D8 (voľná) bez GPX stopy — sú to oddychové dni.
