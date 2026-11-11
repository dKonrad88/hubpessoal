/* Commodities — service worker só desta pasta.
   Escopo: a pasta do script. No GitHub Pages isso é /hubpessoal/commodities/.
   index.html e data.json entram em network-first (a edição nova aparece sozinha).
   Sem rede, a última cópia em cache abre. */
var CACHE = 'commodities-v1';

self.addEventListener('install', function (e) {
  var scope = self.registration.scope;
  e.waitUntil(
    caches.open(CACHE).then(function (c) {
      return Promise.all(['index.html', 'manifest.json', 'icon-192.png', 'icon-512.png', 'apple-touch-icon.png'].map(function (u) {
        return c.add(scope + u).catch(function () {});
      }));
    }).then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener('activate', function (e) {
  e.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(keys.map(function (k) {
        if (k !== CACHE && k.indexOf('commodities-') === 0) return caches.delete(k);
      }));
    }).then(function () { return self.clients.claim(); })
  );
});

function shellCacheUrl(url) {
  var scope = self.registration.scope;
  if (url.href.indexOf(scope) !== 0) return null;
  if (/\/data\.json$/.test(url.pathname)) return scope + 'data.json';
  if (url.href === scope || url.href.indexOf(scope + 'index.html') === 0) return scope + 'index.html';
  return null;
}

self.addEventListener('fetch', function (e) {
  var req = e.request;
  if (req.method !== 'GET') return;
  var url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  if (url.href.indexOf(self.registration.scope) !== 0) return;

  var key = shellCacheUrl(url);
  if (!key && req.mode !== 'navigate') {
    e.respondWith(
      caches.match(req).then(function (cached) {
        var net = fetch(req).then(function (res) {
          if (res && res.status === 200) {
            var copy = res.clone();
            caches.open(CACHE).then(function (c) { c.put(req, copy).catch(function () {}); });
          }
          return res;
        }).catch(function () { return cached; });
        return cached || net;
      })
    );
    return;
  }

  var store = key || (self.registration.scope + 'index.html');
  e.respondWith(
    fetch(req, { cache: 'no-store' }).then(function (res) {
      if (res && res.status === 200) {
        var copy = res.clone();
        caches.open(CACHE).then(function (c) { c.put(store, copy).catch(function () {}); });
      }
      return res;
    }).catch(function () {
      return caches.match(store).then(function (hit) {
        if (hit) return hit;
        return caches.match(self.registration.scope + 'index.html');
      });
    })
  );
});
