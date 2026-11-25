/* MGF no Plural — service worker (aplicação instalável e uso sem internet).
   GERADO por scripts/construir.py a partir de scripts/sw.js — não editar à mão.

   Regras, para não ficarem ferramentas clínicas desatualizadas:
   · Páginas, CSS e JavaScript: primeiro a rede (com revalidação); a cópia guardada só serve sem ligação
     (ou se a rede demorar mais de 8 s e já houver cópia).
   · Letras, imagens e bibliotecas: primeiro a cópia guardada.
   · Cada ficheiro guardado leva o resumo (hash) da versão do site em que foi guardado. Quando sai uma versão
     nova do site, este ficheiro muda, o browser instala-o e só se voltam a descarregar os ficheiros que mudaram.
     Os que já não existem saem com a cache antiga.
   · Só ficheiros do próprio site. Nada sai para outros servidores e não se guarda nada do que se escreve. */
"use strict";

var VERSAO = "1.0-2026-11-17-06d7df02";
var FICHEIROS = {"acerca.html":"13078131bc9d","assets/css/completa.css":"6adcf1ed0589","assets/css/ferramenta.css":"374525426667","assets/css/site.css":"c9cc31991f79","assets/css/tokens.css":"6025e4a5aff2","assets/fonts/atkinson-hyperlegible-latin-400-italic.woff2":"bc8825fd435d","assets/fonts/atkinson-hyperlegible-latin-400-normal.woff2":"d64ba838ef54","assets/fonts/atkinson-hyperlegible-latin-700-italic.woff2":"73e0c9e1e284","assets/fonts/atkinson-hyperlegible-latin-700-normal.woff2":"140e2bd25a73","assets/fonts/bricolage-grotesque-latin-400-normal.woff2":"826772cb1251","assets/fonts/bricolage-grotesque-latin-600-normal.woff2":"b34fc8c1ef0a","assets/fonts/bricolage-grotesque-latin-800-normal.woff2":"3e1b5f0a56ee","assets/fonts/jetbrains-mono-latin-400-normal.woff2":"14425ba9c695","assets/fonts/jetbrains-mono-latin-500-normal.woff2":"cb182feeed4d","assets/img/app-192.png":"610fd0e473bb","assets/img/app-512.png":"015f5107d6ce","assets/img/app-maskable-512.png":"ae8c84ce8770","assets/img/apple-touch-icon.png":"0677318325e2","assets/img/favicon.svg":"79ada8a4c92e","assets/img/icones/analises.svg":"08816f962ff6","assets/img/icones/arcos.svg":"8d8bc4ac64d5","assets/img/icones/arvore.svg":"0806c49b019c","assets/img/icones/avisos.svg":"93df3cb3093d","assets/img/icones/bacteria.svg":"9fe26b4dd63c","assets/img/icones/bebe.svg":"3e999fba9b9d","assets/img/icones/calculadora.svg":"2772a2e04756","assets/img/icones/calendario.svg":"7cbc17fba7bf","assets/img/icones/cerebro.svg":"805c5050ab3b","assets/img/icones/checklist.svg":"06bc5e0e385f","assets/img/icones/circulos.svg":"786a5ed62b93","assets/img/icones/codificacao.svg":"ffde2b328d9f","assets/img/icones/codigo.svg":"c8e160720a9d","assets/img/icones/comprimidos.svg":"baa9a424df3a","assets/img/icones/comunidade.svg":"d4e575525fb9","assets/img/icones/consulta.svg":"27521c171f07","assets/img/icones/contactos.svg":"f75b85cbb005","assets/img/icones/coracao.svg":"3b937ae10293","assets/img/icones/crianca.svg":"43936f0a24a3","assets/img/icones/cuidar.svg":"32fad6a7a1a5","assets/img/icones/design.svg":"894e3b999e65","assets/img/icones/diabetes.svg":"12f80a181201","assets/img/icones/documento.svg":"cd26697a2386","assets/img/icones/domicilio.svg":"4a763c87c1f0","assets/img/icones/doses-pediatricas.svg":"b94021185566","assets/img/icones/download.svg":"d12994523a87","assets/img/icones/ecg.svg":"2294cb266059","assets/img/icones/ecografia.svg":"459c4843f64a","assets/img/icones/enfermagem.svg":"bfb07ad68fda","assets/img/icones/equipa.svg":"f2b2b1345112","assets/img/icones/escala.svg":"afcd49aebb14","assets/img/icones/espiral.svg":"c4c1306cc7b1","assets/img/icones/estetoscopio.svg":"78d00a1da766","assets/img/icones/estomago.svg":"5caa9c4faac1","assets/img/icones/exercicio.svg":"bf0a75f64389","assets/img/icones/explosao.svg":"5ab3a564dd2b","assets/img/icones/familia.svg":"0fd6ebbd5d68","assets/img/icones/femur.svg":"24d72fea5cff","assets/img/icones/folha.svg":"19870cfa8516","assets/img/icones/folheto.svg":"7203a076ef9a","assets/img/icones/formacao.svg":"bb7af8937d81","assets/img/icones/formulario.svg":"64b536aeb578","assets/img/icones/frasco.svg":"81c16e6598a6","assets/img/icones/gravidez.svg":"acff9d420ae1","assets/img/icones/horario.svg":"749d89ead1f0","assets/img/icones/ideia.svg":"8bebe196c7f2","assets/img/icones/idoso.svg":"e2f42316f6dd","assets/img/icones/imagiologia.svg":"71995f86b9d4","assets/img/icones/indicadores.svg":"567ea34ed24f","assets/img/icones/ligacao.svg":"61b2824aa35c","assets/img/icones/livro.svg":"21bfe304903a","assets/img/icones/local.svg":"1580dc428cf7","assets/img/icones/maos.svg":"826734aa5925","assets/img/icones/mapa.svg":"6e67929da7ac","assets/img/icones/medico.svg":"620d90bd8c17","assets/img/icones/mensagem.svg":"29d4087df315","assets/img/icones/microscopio.svg":"21a0f30160a9","assets/img/icones/modelos.svg":"2fc26000ffa1","assets/img/icones/mulher.svg":"f7e8382179b6","assets/img/icones/nota-soap.svg":"2f482e331b7e","assets/img/icones/novelo.svg":"4f8eeddf55ce","assets/img/icones/nutricao.svg":"581a9937da0b","assets/img/icones/olho.svg":"742f1cbbde54","assets/img/icones/ondas.svg":"f2377bff43a1","assets/img/icones/osso.svg":"afb3d47eb102","assets/img/icones/ouvido.svg":"f356159378b4","assets/img/icones/pasta.svg":"e8cfa7a61044","assets/img/icones/pedras.svg":"b7c44ae70e60","assets/img/icones/pele.svg":"c451094f0479","assets/img/icones/penso.svg":"726f0156b415","assets/img/icones/pesquisa.svg":"ecab08aac773","assets/img/icones/pessoa.svg":"f17cb906bf98","assets/img/icones/privacidade.svg":"306c3e3f949a","assets/img/icones/programas.svg":"209d289e6a07","assets/img/icones/pulmoes.svg":"895d5458ea81","assets/img/icones/puzzle.svg":"a2b46648ae33","assets/img/icones/rebento.svg":"13c0f6c76a5d","assets/img/icones/receita.svg":"d776a94b7a75","assets/img/icones/rede.svg":"92daaad7ad8c","assets/img/icones/referenciacao.svg":"1090bac4070b","assets/img/icones/registo.svg":"65de121083a2","assets/img/icones/rins.svg":"b368373283ad","assets/img/icones/sites.svg":"7c27ea589801","assets/img/icones/sol.svg":"4bba220bec4f","assets/img/icones/sono.svg":"9ac71d988081","assets/img/icones/tabaco.svg":"d091efb47fc9","assets/img/icones/tensiometro.svg":"6027e3ee66a5","assets/img/icones/termometro.svg":"941ca7c44131","assets/img/icones/tiroide.svg":"8fe4cb81afab","assets/img/icones/vacina.svg":"8db31d6c1b30","assets/img/simbolo.svg":"d1cc2d753545","assets/js/catalogo.js":"653befd553ae","assets/js/ferramenta.js":"50640e4a5922","assets/js/pwa.js":"3320801756b0","assets/js/site.js":"2e119a794ff4","assets/vendor/jspdf.plugin.autotable.min.js":"27a9c3b61843","assets/vendor/jspdf.umd.min.js":"98ccf17aa10c","assets/vendor/leaflet-maplibre-gl.js":"1e6cf8cb3eb5","assets/vendor/leaflet.css":"a78371028241","assets/vendor/leaflet.js":"dc71f8a6880b","assets/vendor/maplibre-gl.css":"ab1e70d59ec4","assets/vendor/maplibre-gl.js":"8b2c6bfadb8c","assets/vendor/xlsx.full.min.js":"c9506197caf8","contribuir.html":"a8f016b572ae","ferramentas/documentacao/index.html":"a12a475b86e5","ferramentas/documentacao/modelos/consentimento-diu-l.html":"5bde56f4f23c","ferramentas/documentacao/modelos/consentimento-diu.html":"c8702f78d60a","ferramentas/documentacao/modelos/consentimento-implante.html":"7822d2b6a68b","ferramentas/documentacao/modelos/index.html":"7b10d4918437","ferramentas/documentacao/modelos/manual-de-procedimentos.html":"060e8078921c","ferramentas/documentacao/modelos/modelo-de-ata.html":"1c47de52c341","ferramentas/mapa-de-recursos/index.html":"14a41378c8ac","ferramentas/mapa-de-recursos/modelo.html":"d588959c65c6","ferramentas/mapa-de-recursos/zonas/amadora.html":"37edb47d5135","ferramentas/mapa-de-recursos/zonas/index.html":"c11bd07323d8","ferramentas/plataforma-de-indicadores/geral/index.html":"7e8fcb11cf31","ferramentas/plataforma-de-indicadores/geral/plataforma-de-indicadores.html":"6cc9a2d2b9bd","ferramentas/plataforma-de-indicadores/index.html":"b105b0507159","ferramentas/recursos-de-enfermagem/geral/index.html":"9dda7295462c","ferramentas/recursos-de-enfermagem/geral/vacinacao.html":"97175bbed965","ferramentas/recursos-de-enfermagem/index.html":"3f9e7057395f","ferramentas/recursos-medicos/cabulas/index.html":"abaa2defbd39","ferramentas/recursos-medicos/cabulas/menopausa.html":"4eb9f03d6b1a","ferramentas/recursos-medicos/cabulas/osteoporose.html":"2adf841c5ae8","ferramentas/recursos-medicos/canivete/combinar-listas.html":"4034a48ca26c","ferramentas/recursos-medicos/canivete/construir-horario.html":"c9a4c839bc4c","ferramentas/recursos-medicos/canivete/consulta-resultados-exames.html":"c39ba7d9acda","ferramentas/recursos-medicos/canivete/formulario-referenciacao.html":"d77fa8960d4d","ferramentas/recursos-medicos/canivete/index.html":"95e6f2bd0eab","ferramentas/recursos-medicos/canivete/pesquisa-icpc2.html":"b52075aeef9f","ferramentas/recursos-medicos/escalas-e-calculadoras/escalas-cardiovasculares.html":"f73b14fe5b39","ferramentas/recursos-medicos/escalas-e-calculadoras/escalas-doencas-respiratorias.html":"71a11287738e","ferramentas/recursos-medicos/escalas-e-calculadoras/escalas-saude-mental.html":"2d8674917467","ferramentas/recursos-medicos/escalas-e-calculadoras/escalas-urologia-nefrologia.html":"a7157b3dda99","ferramentas/recursos-medicos/escalas-e-calculadoras/index.html":"30356a45e7e6","ferramentas/recursos-medicos/escalas-e-calculadoras/planificacao-vigilancia-gravidez.html":"1cf2fc9cb42a","ferramentas/recursos-medicos/ferramentas-de-prescricao/apoio-a-prescricao.html":"5a41bc62f4e0","ferramentas/recursos-medicos/ferramentas-de-prescricao/doses-pediatricas.html":"146841675068","ferramentas/recursos-medicos/ferramentas-de-prescricao/farmacos-na-gravidez.html":"d3fd659eb48e","ferramentas/recursos-medicos/ferramentas-de-prescricao/guia-antibioterapia.html":"d6120184c33b","ferramentas/recursos-medicos/ferramentas-de-prescricao/guia-terapeutico.html":"a34154cdf5fb","ferramentas/recursos-medicos/ferramentas-de-prescricao/index.html":"4916e2ccd19e","ferramentas/recursos-medicos/index.html":"aee64d30f04a","ferramentas/recursos-medicos/interpretar-exames/audiograma-e-timpanograma.html":"b517a72df8d9","ferramentas/recursos-medicos/interpretar-exames/calculadora-ampa.html":"1e07483a20f2","ferramentas/recursos-medicos/interpretar-exames/ecg-e-holter.html":"544fde2d9755","ferramentas/recursos-medicos/interpretar-exames/ecocardiograma.html":"37928ba67a8f","ferramentas/recursos-medicos/interpretar-exames/ecografia-renal-vesical-urofluxometria.html":"c018b1a6f786","ferramentas/recursos-medicos/interpretar-exames/espirometria.html":"9b7a4a2ad2b8","ferramentas/recursos-medicos/interpretar-exames/index.html":"ff6f298e50c4","ferramentas/recursos-medicos/interpretar-exames/interpretar-analises.html":"1b670b6c193f","ferramentas/recursos-medicos/interpretar-exames/tc-cerebral-e-coluna.html":"b5a58d6a23f6","ferramentas/recursos-medicos/programas-e-valencias/index.html":"f90790557865","ferramentas/recursos-medicos/programas-e-valencias/saude-infantil.html":"bd99968e0cf8","ferramentas/recursos-medicos/programas-e-valencias/vigilancia-gravidez.html":"637c73dbb72b","ferramentas/recursos-medicos/recursos-externos/index.html":"016d59c10437","ferramentas/recursos-medicos/registo-e-vigilancia/index.html":"219b1d2f2d4a","ferramentas/recursos-medicos/registo-e-vigilancia/nota-soap.html":"056eb26f0716","ferramentas/recursos-medicos/registo-e-vigilancia/vigilancia-mgf.html":"55678be3d52b","guia-design.html":"9754aa33779b","index.html":"ab88c9e6fcbb","manifest.webmanifest":"740622b84c8a","offline.html":"9677e8ba83e1"};
var ESSENCIAIS = ["index.html","acerca.html","offline.html","manifest.webmanifest","assets/css/completa.css","assets/css/ferramenta.css","assets/css/site.css","assets/css/tokens.css","assets/fonts/atkinson-hyperlegible-latin-400-italic.woff2","assets/fonts/atkinson-hyperlegible-latin-400-normal.woff2","assets/fonts/atkinson-hyperlegible-latin-700-italic.woff2","assets/fonts/atkinson-hyperlegible-latin-700-normal.woff2","assets/fonts/bricolage-grotesque-latin-400-normal.woff2","assets/fonts/bricolage-grotesque-latin-600-normal.woff2","assets/fonts/bricolage-grotesque-latin-800-normal.woff2","assets/fonts/jetbrains-mono-latin-400-normal.woff2","assets/fonts/jetbrains-mono-latin-500-normal.woff2","assets/img/icones/analises.svg","assets/img/icones/arcos.svg","assets/img/icones/arvore.svg","assets/img/icones/avisos.svg","assets/img/icones/bacteria.svg","assets/img/icones/bebe.svg","assets/img/icones/calculadora.svg","assets/img/icones/calendario.svg","assets/img/icones/cerebro.svg","assets/img/icones/checklist.svg","assets/img/icones/circulos.svg","assets/img/icones/codificacao.svg","assets/img/icones/codigo.svg","assets/img/icones/comprimidos.svg","assets/img/icones/comunidade.svg","assets/img/icones/consulta.svg","assets/img/icones/contactos.svg","assets/img/icones/coracao.svg","assets/img/icones/crianca.svg","assets/img/icones/cuidar.svg","assets/img/icones/design.svg","assets/img/icones/diabetes.svg","assets/img/icones/documento.svg","assets/img/icones/domicilio.svg","assets/img/icones/doses-pediatricas.svg","assets/img/icones/download.svg","assets/img/icones/ecg.svg","assets/img/icones/ecografia.svg","assets/img/icones/enfermagem.svg","assets/img/icones/equipa.svg","assets/img/icones/escala.svg","assets/img/icones/espiral.svg","assets/img/icones/estetoscopio.svg","assets/img/icones/estomago.svg","assets/img/icones/exercicio.svg","assets/img/icones/explosao.svg","assets/img/icones/familia.svg","assets/img/icones/femur.svg","assets/img/icones/folha.svg","assets/img/icones/folheto.svg","assets/img/icones/formacao.svg","assets/img/icones/formulario.svg","assets/img/icones/frasco.svg","assets/img/icones/gravidez.svg","assets/img/icones/horario.svg","assets/img/icones/ideia.svg","assets/img/icones/idoso.svg","assets/img/icones/imagiologia.svg","assets/img/icones/indicadores.svg","assets/img/icones/ligacao.svg","assets/img/icones/livro.svg","assets/img/icones/local.svg","assets/img/icones/maos.svg","assets/img/icones/mapa.svg","assets/img/icones/medico.svg","assets/img/icones/mensagem.svg","assets/img/icones/microscopio.svg","assets/img/icones/modelos.svg","assets/img/icones/mulher.svg","assets/img/icones/nota-soap.svg","assets/img/icones/novelo.svg","assets/img/icones/nutricao.svg","assets/img/icones/olho.svg","assets/img/icones/ondas.svg","assets/img/icones/osso.svg","assets/img/icones/ouvido.svg","assets/img/icones/pasta.svg","assets/img/icones/pedras.svg","assets/img/icones/pele.svg","assets/img/icones/penso.svg","assets/img/icones/pesquisa.svg","assets/img/icones/pessoa.svg","assets/img/icones/privacidade.svg","assets/img/icones/programas.svg","assets/img/icones/pulmoes.svg","assets/img/icones/puzzle.svg","assets/img/icones/rebento.svg","assets/img/icones/receita.svg","assets/img/icones/rede.svg","assets/img/icones/referenciacao.svg","assets/img/icones/registo.svg","assets/img/icones/rins.svg","assets/img/icones/sites.svg","assets/img/icones/sol.svg","assets/img/icones/sono.svg","assets/img/icones/tabaco.svg","assets/img/icones/tensiometro.svg","assets/img/icones/termometro.svg","assets/img/icones/tiroide.svg","assets/img/icones/vacina.svg","assets/js/catalogo.js","assets/js/ferramenta.js","assets/js/pwa.js","assets/js/site.js","assets/img/app-192.png","assets/img/app-512.png","assets/img/app-maskable-512.png","assets/img/apple-touch-icon.png","assets/img/favicon.svg","assets/img/simbolo.svg"];
var TAMANHO = 8975096;

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
