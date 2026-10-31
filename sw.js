/* HUB Pessoal — service worker (PWA)
   Estratégia segura para um app single-file que muda com frequência:
   - Navegação (abrir o app): network-first -> sempre pega o index.html mais novo quando online;
     se estiver offline, cai no cache (app abre mesmo sem internet).
   - Supabase (dados do usuário): NUNCA passa pelo cache. Sempre rede.
   - equilibrio.js do Foco (mesma origem): network-first, cache só como fallback offline.
   - Demais GET (CDNs: fontes, ícones, chart.js, supabase-js): stale-while-revalidate.
   Bump CACHE quando quiser forçar limpeza do cache antigo. */
var CACHE = 'hub-v40';
var SHELL = ['./', './index.html', './manifest.json',
             './apple-touch-icon.png', './icon-192.png', './icon-512.png'];

self.addEventListener('message', function (e) {
  if (e.data && e.data.type === 'SKIP_WAITING') self.skipWaiting();
});

self.addEventListener('install', function (e) {
  e.waitUntil(
    caches.open(CACHE).then(function (c) {
      // addAll falha tudo se 1 recurso falhar; usamos add individual tolerante
      return Promise.all(SHELL.map(function (u) { return c.add(u).catch(function () {}); }));
    }).then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener('activate', function (e) {
  e.waitUntil(
    caches.keys().then(function (keys) {
      // a origem dkonrad88.github.io é compartilhada com os outros apps da suíte: só limpa caches do HUB
      return Promise.all(keys.map(function (k) { if (k !== CACHE && k.indexOf('hub-') === 0) return caches.delete(k); }));
    }).then(function () { return self.clients.claim(); })
  );
});

self.addEventListener('fetch', function (e) {
  var req = e.request;
  if (req.method !== 'GET') return;                       // não toca em POST/PUT/etc.
  var url = new URL(req.url);

  // Dados do usuário: deixa passar direto, sem cache.
  if (/supabase\.(co|in)/.test(url.hostname)) return;

  // Painel do apartamento (./apto/, read-only, dados em apto/data.json): sempre rede, sem cache do HUB
  // (senão a navegação do iframe gravaria a página do apto no lugar do index.html do HUB).
  if (url.origin === self.location.origin && /\/hubpessoal\/apto\//.test(url.pathname)) return;
  // Painel de gastos do casamento (./casamento/, read-only, dados em casamento/data.json): mesma regra do apto
  if (url.origin === self.location.origin && /\/hubpessoal\/casamento\//.test(url.pathname)) return;

  // Abrir o app: network-first com fallback pro cache (offline).
  if (req.mode === 'navigate') {
    e.respondWith(
      fetch(req).then(function (res) {
        var copy = res.clone();
        caches.open(CACHE).then(function (c) { c.put('./index.html', copy); });
        return res;
      }).catch(function () {
        return caches.match('./index.html').then(function (m) { return m || caches.match('./'); });
      })
    );
    return;
  }

  // Domínio do Foco (https://dkonrad88.github.io/Foco/equilibrio.js, mesma origem): network-first com
  // fallback pro cache, para o HUB calcular com a mesma versão do app. Sem cache-busting por query.
  if (url.origin === self.location.origin && /\/equilibrio\.js$/.test(url.pathname)) {
    e.respondWith(
      fetch(req).then(function (res) {
        if (res && res.status === 200) {
          var copy = res.clone();
          caches.open(CACHE).then(function (c) { c.put(req, copy); });
        }
        return res;
      }).catch(function () {
        return caches.match(req);
      })
    );
    return;
  }

  // Outros recursos (CDNs estáticos): stale-while-revalidate.
  e.respondWith(
    caches.match(req).then(function (cached) {
      var net = fetch(req).then(function (res) {
        if (res && res.status === 200 && (res.type === 'basic' || res.type === 'cors')) {
          var copy = res.clone();
          caches.open(CACHE).then(function (c) { c.put(req, copy); });
        }
        return res;
      }).catch(function () { return cached; });
      return cached || net;
    })
  );
});
