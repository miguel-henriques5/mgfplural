/* MGF no Plural — service worker (aplicação instalável e uso sem internet).
   Gerado por scripts/construir.py a partir de scripts/sw.js: não editar o /sw.js à mão.

   Regras, para não ficarem ferramentas clínicas desatualizadas:
   · Páginas, CSS e JavaScript: primeiro a rede (com revalidação); a cópia guardada só serve sem ligação
     (ou se a rede demorar mais de 8 s e já houver cópia).
   · Letras, imagens e bibliotecas: primeiro a cópia guardada.
   · Cada ficheiro guardado leva o resumo (hash) da versão do site em que foi guardado. Quando sai uma versão
     nova do site, este ficheiro muda, o browser instala-o e só se voltam a descarregar os ficheiros que mudaram.
     Os que já não existem saem com a cache antiga.
   · Só ficheiros do próprio site. Nada sai para outros servidores e não se guarda nada do que se escreve. */
"use strict";

var VERSAO = "{{VERSAO}}";
var FICHEIROS = {{FICHEIROS}};
var ESSENCIAIS = {{ESSENCIAIS}};
var TAMANHO = {{TAMANHO}};

var PREFIXO = "mgfplural-";
var CACHE = PREFIXO + VERSAO;
var BASE = new URL("./", self.location).href;
var META = BASE + "__mgf-offline__";
var ESPERA_REDE = 8000;

function chave(url) {
  var u = new URL(url, BASE);
  u.hash = ""; u.search = "";
  if (u.href.indexOf(BASE) !== 0) return null;
  var p = decodeURIComponent(u.href.slice(BASE.length));
  if (p === "" || p.slice(-1) === "/") p += "index.html";
  return p;
}

function estatico(p) {
  return /\.(woff2|png|svg|jpg|jpeg|webp|ico)$/i.test(p) || p.indexOf("assets/vendor/") === 0;
}

/* Resposta pronta a guardar: sem redireções (os browsers recusam-nas em navegações) e com o resumo da versão. */
function paraGuardar(r, p) {
  return r.clone().blob().then(function (corpo) {
    var h = new Headers(r.headers);
    h.set("x-mgf-hash", FICHEIROS[p] || "");
    return new Response(corpo, { status: r.status, statusText: r.statusText, headers: h });
  });
}

function descarregar(cache, p) {
  return fetch(BASE + p, { cache: "no-cache", credentials: "same-origin" }).then(function (r) {
    if (!r.ok) throw new Error(p + ": " + r.status);
    return paraGuardar(r, p).then(function (g) { return cache.put(BASE + p, g); });
  });
}

/* Descarrega uma lista, 6 de cada vez. Devolve o número de falhas. */
function descarregarLista(cache, lista, progresso) {
  var i = 0, feitos = 0, falhas = 0;
  function seguinte() {
    if (i >= lista.length) return Promise.resolve();
    var p = lista[i++];
    return descarregar(cache, p).catch(function () { falhas++; }).then(function () {
      feitos++;
      if (progresso) progresso(feitos, lista.length);
      return seguinte();
    });
  }
  var filas = [];
  for (var k = 0; k < 6; k++) filas.push(seguinte());
  return Promise.all(filas).then(function () { return falhas; });
}

function lerMeta(cache) {
  return cache.match(META).then(function (r) { return r ? r.json() : null; }).catch(function () { return null; });
}
function gravarMeta(cache, m) {
  return cache.put(META, new Response(JSON.stringify(m), { headers: { "content-type": "application/json" } }));
}

/* Cache anterior (de outra versão do site), se houver. */
function cacheAnterior() {
  return caches.keys().then(function (ks) {
    var antigas = ks.filter(function (k) { return k.indexOf(PREFIXO) === 0 && k !== CACHE; });
    return antigas.length ? caches.open(antigas[antigas.length - 1]) : null;
  });
}

function preparar() {
  return Promise.all([caches.open(CACHE), cacheAnterior()]).then(function (cs) {
    var nova = cs[0], antiga = cs[1];
    var meta = { tudo: false };
    var passo = Promise.resolve();
    if (antiga) {
      passo = lerMeta(antiga).then(function (m) {
        if (m) meta.tudo = !!m.tudo;
        return antiga.keys();
      }).then(function (pedidos) {
        /* Aproveita o que não mudou. */
        return Promise.all(pedidos.map(function (pedido) {
          var p = chave(pedido.url);
          if (!p || !(p in FICHEIROS)) return null;
          return antiga.match(pedido).then(function (r) {
            if (r && r.headers.get("x-mgf-hash") === FICHEIROS[p]) return nova.put(BASE + p, r);
          });
        }));
      });
    }
    return passo.then(function () { return nova.keys(); }).then(function (ja) {
      var tem = {};
      ja.forEach(function (q) { tem[chave(q.url)] = true; });
      var lista = (meta.tudo ? Object.keys(FICHEIROS) : ESSENCIAIS).filter(function (p) { return !tem[p]; });
      return descarregarLista(nova, lista);
    }).then(function () { return gravarMeta(nova, meta); });
  });
}

self.addEventListener("install", function (ev) {
  ev.waitUntil(preparar().then(function () { return self.skipWaiting(); }));
});

self.addEventListener("activate", function (ev) {
  ev.waitUntil(caches.keys().then(function (ks) {
    return Promise.all(ks.filter(function (k) { return k.indexOf(PREFIXO) === 0 && k !== CACHE; })
      .map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});

function comPrazo(promessa, ms) {
  return new Promise(function (ok, falha) {
    var t = setTimeout(function () { falha(new Error("demorou")); }, ms);
    promessa.then(function (r) { clearTimeout(t); ok(r); }, function (e) { clearTimeout(t); falha(e); });
  });
}

function paginaOffline() {
  return caches.open(CACHE).then(function (c) { return c.match(BASE + "offline.html"); }).then(function (r) {
    return r || new Response("Sem ligação à internet.", { status: 503, headers: { "content-type": "text/plain; charset=utf-8" } });
  });
}

function primeiroRede(ev, p, navegacao) {
  return caches.open(CACHE).then(function (cache) {
    return cache.match(BASE + p).then(function (guardada) {
      var rede = fetch(BASE + p, { cache: "no-cache", credentials: "same-origin" }).then(function (r) {
        if (r.ok) ev.waitUntil(paraGuardar(r, p).then(function (g) { return cache.put(BASE + p, g); }));
        return r;
      });
      var tentativa = guardada ? comPrazo(rede, ESPERA_REDE) : rede;
      return tentativa.catch(function () {
        if (guardada) return guardada;
        return navegacao ? paginaOffline() : Response.error();
      });
    });
  });
}

function primeiroCache(ev, p) {
  return caches.open(CACHE).then(function (cache) {
    return cache.match(BASE + p).then(function (guardada) {
      if (guardada) return guardada;
      return fetch(BASE + p, { credentials: "same-origin" }).then(function (r) {
        if (r.ok) ev.waitUntil(paraGuardar(r, p).then(function (g) { return cache.put(BASE + p, g); }));
        return r;
      });
    });
  });
}

self.addEventListener("fetch", function (ev) {
  var pedido = ev.request;
  if (pedido.method !== "GET") return;
  var url = new URL(pedido.url);
  if (url.origin !== self.location.origin) return;
  var p = chave(pedido.url);
  if (p === null || !(p in FICHEIROS)) return;   /* ex.: versões para descarregar — vão sempre à rede */
  ev.respondWith(estatico(p) ? primeiroCache(ev, p) : primeiroRede(ev, p, pedido.mode === "navigate"));
});

/* Conversa com a página «Acerca» (estado, disponibilizar tudo, apagar). */
function estado() {
  return caches.open(CACHE).then(function (c) {
    return Promise.all([c.keys(), lerMeta(c)]);
  }).then(function (r) {
    var guardados = 0;
    r[0].forEach(function (q) { var p = chave(q.url); if (p in FICHEIROS) guardados++; });
    return { tipo: "estado", versao: VERSAO, total: Object.keys(FICHEIROS).length, guardados: guardados,
             tamanho: TAMANHO, tudo: !!(r[1] && r[1].tudo) };
  });
}

self.addEventListener("message", function (ev) {
  var porta = ev.ports && ev.ports[0];
  var dados = ev.data || {};
  function responder(m) { if (porta) porta.postMessage(m); }
  var trabalho;
  if (dados.tipo === "estado") {
    trabalho = estado().then(responder);
  } else if (dados.tipo === "tudo") {
    trabalho = caches.open(CACHE).then(function (c) {
      return gravarMeta(c, { tudo: true }).then(function () { return c.keys(); }).then(function (ja) {
        var tem = {};
        ja.forEach(function (q) { tem[chave(q.url)] = true; });
        var lista = Object.keys(FICHEIROS).filter(function (p) { return !tem[p]; });
        return descarregarLista(c, lista, function (feitos, total) {
          if (feitos % 5 === 0 || feitos === total) responder({ tipo: "progresso", feitos: feitos, total: total });
        });
      });
    }).then(function (falhas) {
      return estado().then(function (s) { s.tipo = "fim"; s.falhas = falhas; responder(s); });
    });
  } else if (dados.tipo === "apagar") {
    trabalho = caches.keys().then(function (ks) {
      return Promise.all(ks.filter(function (k) { return k.indexOf(PREFIXO) === 0; }).map(function (k) { return caches.delete(k); }));
    }).then(function () {
      return caches.open(CACHE).then(function (c) { return descarregarLista(c, ["offline.html"]).then(function () { return gravarMeta(c, { tudo: false }); }); });
    }).then(estado).then(responder);
  }
  if (trabalho) ev.waitUntil(trabalho.catch(function (e) { responder({ tipo: "erro", mensagem: String(e) }); }));
});
