const C='alpeadria-v19';
const ASSETS=['./','./index.html','./data.js?v=19','./manifest.json'];

function netRace(req,ms){
  return Promise.race([
    fetch(req),
    new Promise((_,r)=>setTimeout(()=>r(new Error('sw-timeout')),ms))
  ]);
}

self.addEventListener('install',e=>{self.skipWaiting();e.waitUntil(caches.open(C).then(c=>c.addAll(ASSETS)));});
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
