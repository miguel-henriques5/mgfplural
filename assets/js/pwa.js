/* MGF no Plural — aplicação instalável (PWA) e cópia para usar sem internet.
   Regista o service worker (/sw.js) quando o site é aberto pela internet (não a partir do disco).
   Na página «Acerca» (secção Usar offline): botão Instalar, estado da cópia offline, «Disponibilizar tudo offline»
   e «Apagar a cópia offline». Tudo é melhoria: se o browser ou a informática não deixarem, o site funciona igual. */
(function () {
  "use strict";
  var este = document.currentScript;
  if (!este || !("serviceWorker" in navigator) || !/^https?:$/.test(location.protocol)) return;
  var raiz = new URL("../../", este.src).href;
  var registo = navigator.serviceWorker.register(raiz + "sw.js", { scope: raiz }).catch(function () { return null; });

  var MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];
  function dataPt(iso) {
    var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso || "");
    return m ? (+m[3]) + " " + MESES[+m[2] - 1] + " " + m[1] : iso;
  }
  function mb(bytes) { return (bytes / 1048576).toFixed(1).replace(".", ",") + " MB"; }

  /* ---------- Instalar ---------- */
  var pedidoInstalar = null;
  var instalada = window.matchMedia && window.matchMedia("(display-mode: standalone)").matches;
  function mostrarInstalar() {
    document.querySelectorAll("[data-pwa-instalar]").forEach(function (b) { b.hidden = !pedidoInstalar; });
    document.querySelectorAll("[data-pwa-instalada]").forEach(function (s) { s.hidden = !instalada; });
  }
  window.addEventListener("beforeinstallprompt", function (ev) {
    ev.preventDefault();
    pedidoInstalar = ev;
    mostrarInstalar();
  });
  window.addEventListener("appinstalled", function () { pedidoInstalar = null; instalada = true; mostrarInstalar(); });
  document.addEventListener("click", function (ev) {
    var b = ev.target.closest && ev.target.closest("[data-pwa-instalar]");
    if (!b || !pedidoInstalar) return;
    pedidoInstalar.prompt();
    pedidoInstalar.userChoice.then(function () { pedidoInstalar = null; mostrarInstalar(); });
  });
  mostrarInstalar();

  /* ---------- Cópia offline (página Acerca) ---------- */
  var painel = document.querySelector("[data-pwa-offline]");
  if (!painel) return;
  var linha = painel.querySelector("[data-pwa-estado]");
  var botaoTudo = painel.querySelector("[data-pwa-tudo]");
  var botaoApagar = painel.querySelector("[data-pwa-apagar]");
  var barra = painel.querySelector("progress");
  painel.hidden = false;

  function pedir(mensagem, aoReceber) {
    return navigator.serviceWorker.ready.then(function (reg) {
      var sw = reg.active;
      if (!sw) throw new Error("sem service worker");
      var canal = new MessageChannel();
      canal.port1.onmessage = function (ev) { aoReceber(ev.data); };
      sw.postMessage(mensagem, [canal.port2]);
    });
  }
  function escreverEstado(s) {
    var versao = String(s.versao || "").split("-");
    var texto = "Guardados neste browser: " + s.guardados + " de " + s.total + " ficheiros";
    if (s.guardados >= s.total) texto = "Tudo disponível offline (" + s.total + " ficheiros, " + mb(s.tamanho) + ")";
    texto += " · versão " + versao[0] + " de " + dataPt(versao.slice(1, 4).join("-")) + ".";
    if (s.falhas) texto += " Faltaram " + s.falhas + " ficheiros: tenta outra vez com ligação.";
    linha.textContent = texto;
    botaoTudo.textContent = s.guardados >= s.total ? "Atualizar a cópia offline" : "Disponibilizar tudo offline (" + mb(s.tamanho) + ")";
    botaoTudo.disabled = false;
    botaoApagar.hidden = s.guardados === 0;
    barra.hidden = true;
  }
  function semServico() {
    linha.textContent = "Este browser (ou a informática do teu serviço) não deixa guardar o site para usar sem internet. Usa o ZIP ou descarrega as ferramentas.";
    botaoTudo.hidden = true;
    botaoApagar.hidden = true;
  }
  function atualizar() { return pedir({ tipo: "estado" }, escreverEstado); }

  registo.then(function (reg) {
    if (!reg) return semServico();
    linha.textContent = "A preparar…";
    atualizar().catch(semServico);
  });

  botaoTudo.addEventListener("click", function () {
    if (!navigator.onLine) { linha.textContent = "Precisas de ligação à internet para guardar o site."; return; }
    botaoTudo.disabled = true;
    barra.hidden = false; barra.value = 0;
    linha.textContent = "A guardar…";
    pedir({ tipo: "tudo" }, function (m) {
      if (m.tipo === "progresso") {
        barra.max = m.total; barra.value = m.feitos;
        linha.textContent = "A guardar… " + m.feitos + " de " + m.total + " ficheiros";
      } else if (m.tipo === "fim") {
        escreverEstado(m);
      } else if (m.tipo === "erro") {
        botaoTudo.disabled = false; barra.hidden = true;
        linha.textContent = "Não foi possível guardar tudo. Tenta outra vez com ligação.";
      }
    }).catch(semServico);
  });

  botaoApagar.addEventListener("click", function () {
    pedir({ tipo: "apagar" }, function (m) {
      escreverEstado(m);
      linha.textContent = "Cópia offline apagada. " + linha.textContent;
    }).catch(semServico);
  });
})();
