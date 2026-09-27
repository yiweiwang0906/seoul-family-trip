const CACHE='seoul-family-v1';
const ROOT=new URL('./',self.location.href);
const FILES=['./','./index.html','./style.css','./data.js','./app.js','./icon.svg','./manifest.webmanifest'].map(p=>new URL(p,ROOT).href);
self.addEventListener('install',event=>{event.waitUntil(caches.open(CACHE).then(c=>c.addAll(FILES)).then(()=>self.skipWaiting()));});
self.addEventListener('activate',event=>{event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('seoul-family-')&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));});
self.addEventListener('fetch',event=>{
  if(event.request.method!=='GET')return;
  const u=new URL(event.request.url);
  if(u.origin!==ROOT.origin||!u.pathname.startsWith(ROOT.pathname))return;
  event.respondWith(fetch(event.request).then(response=>{if(response.ok&&FILES.includes(u.href)){const copy=response.clone();event.waitUntil(caches.open(CACHE).then(c=>c.put(event.request,copy)));}return response;}).catch(async()=>{
    const hit=await caches.match(event.request);if(hit)return hit;
    if(event.request.mode==='navigate')return caches.match(new URL('index.html',ROOT).href);
    return Response.error();
  }));
});
