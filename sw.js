const C='alpeadria-v27';
const CORE=['./','./index.html','./data.js?v=27','./manifest.json'];
const ROUTES=[];
['D2_VillachHostel_TarvisioSchaefer','D3_TarvisioSchaefer_CasaBlissVenzone','D4_CasaBlissVenzone_UdineSunset42','D5_UdineSunset42_GradoRivaFoscolo','D7a_GradoRivaFoscolo_GradoFerry','D7b_TriesteFerry_PortorozKorotan','D9a_PortorozKorotan_TriesteCentrale','D9b_GoriziaCentrale_StaraGo','D10_StaraGoGorizia_BlueHouseCiginj','D11a_BlueHouseCiginj_Kobarid','D11b_Kolovrat_BlueHouseCiginj','D12b_JeseniceStation_Bled_okruh'].forEach(b=>{ROUTES.push('./'+b+'.gpx','./'+b+'.kml');});

function netRace(req,ms){
  return Promise.race([
    fetch(req),
    new Promise((_,r)=>setTimeout(()=>r(new Error('sw-timeout')),ms))
  ]);
}

self.addEventListener('install',e=>{self.skipWaiting();e.waitUntil(caches.open(C).then(c=>c.addAll(CORE).then(()=>Promise.allSettled(ROUTES.map(u=>c.add(u))))));});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k.startsWith('alpeadria-')&&k!==C).map(k=>caches.delete(k)))));self.clients.claim();});

function cacheStore(req,res){
  return caches.open(C).then(c=>c.put(req,res)).catch(()=>{});
}

self.addEventListener('fetch',e=>{
  if(e.request.method!=='GET')return;
  const u=e.request.url;
  const netFirst=u.includes('data.js')||u.endsWith('index.html')||u.endsWith('/');
  const shell=()=>caches.match('./index.html');

  if(netFirst){
    e.respondWith(
      netRace(e.request,4000).then(res=>{
        if(!res.ok||res.status!==200)throw new Error('bad-response');
        const cp=res.clone();
        return cacheStore(e.request,cp).then(()=>res,()=>res);
      }).catch(()=>{
        const base=e.request.mode==='navigate'?shell():caches.match(e.request);
        return base.then(r=>r||shell()).then(r=>r||new Response('',{status:408,statusText:'Offline'}));
      })
    );
  } else {
    e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request).then(res=>{
      if(res.ok&&res.status===200){const cp=res.clone();cacheStore(e.request,cp);}
      return res;
    }).catch(()=>e.request.mode==='navigate'?shell():new Response('',{status:408,statusText:'Offline'}))));
  }
});
