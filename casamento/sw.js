/* Casamento — só esta pasta. index.html e version.json em network-first. */
var CACHE='casamento-v2';
self.addEventListener('install',function(){self.skipWaiting()});
self.addEventListener('activate',function(e){e.waitUntil(self.clients.claim())});
self.addEventListener('fetch',function(e){
  var req=e.request;
  if(req.method!=='GET')return;
  var url=new URL(req.url);
  if(/supabase\.(co|in)/.test(url.hostname))return;
  var shell=req.mode==='navigate'||/\/casamento\/(?:index\.html)?$/.test(url.pathname)||/\/version\.json$/.test(url.pathname);
  if(!shell)return;
  e.respondWith(fetch(req,{cache:'no-store'}).then(function(res){
    var copy=res.clone();
    caches.open(CACHE).then(function(c){c.put(req,copy)}).catch(function(){});
    return res;
  }).catch(function(){return caches.match(req)}));
});
