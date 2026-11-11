/* MGF no Plural — comportamento do site.
   Tudo é melhoria: sem JavaScript, o site continua navegável.
   Não faz pedidos de rede. Só guarda no browser a lista "Abertas recentemente". */
(function () {
  "use strict";
  var raiz = document.documentElement.getAttribute("data-raiz") || "";
  var catalogo = window.MGF_CATALOGO || [];

  function normalizar(t) {
    return (t || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[₂²]/g, "2");
  }
  function lerRecentes() {
    try { return JSON.parse(localStorage.getItem("mgf:recentes") || "[]"); } catch (e) { return []; }
  }

  /* ---------- Bibliografia longa: abre para imprimir e volta a fechar ---------- */
  var bib = document.getElementById("bib");
  if (bib && bib.tagName === "DETAILS") {
    var abertaAntes = false;
    window.addEventListener("beforeprint", function () { abertaAntes = bib.open; bib.open = true; });
    window.addEventListener("afterprint", function () { bib.open = abertaAntes; });
  }

  /* ---------- Menus (Ferramentas e grupo da ferramenta): fechar ao clicar fora ou com Esc ---------- */
  document.querySelectorAll(".menu-ferramentas, .grupo-menu").forEach(function (menu) {
    document.addEventListener("click", function (e) {
      if (menu.open && !menu.contains(e.target)) menu.open = false;
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && menu.open) { menu.open = false; menu.querySelector("summary").focus(); }
    });
  });

  /* ---------- Pesquisa instantânea ---------- */
  document.querySelectorAll("[data-pesquisa]").forEach(function (caixa) {
    var campo = caixa.querySelector("input");
    var lista = caixa.querySelector(".pesquisa-resultados");
    var indice = catalogo.map(function (f) {
      var texto = normalizar([f.titulo, f.descricao, f.area, f.grupo].concat(f.palavras || []).join(" "));
      /* versão só com letras: "chads" encontra "CHA2DS2-VASc" */
      return { f: f, texto: texto, letras: texto.replace(/[^a-z]/g, "") };
    });
    function mostrar() {
      var q = normalizar(campo.value.trim());
      lista.innerHTML = "";
      if (!q) { lista.hidden = true; return; }
      var termos = q.split(/\s+/);
      var achados = indice.filter(function (x) {
        return termos.every(function (t) {
          var l = t.replace(/[^a-z]/g, "");
          return x.texto.indexOf(t) !== -1 || (l.length > 2 && x.letras.indexOf(l) !== -1);
        });
      }).slice(0, 8);
      if (!achados.length) {
        var vazio = document.createElement("p");
        vazio.className = "pesquisa-vazia";
        vazio.textContent = "Nada encontrado. Ainda estamos a migrar ferramentas para o site.";
        lista.appendChild(vazio);
      }
      achados.forEach(function (x) {
        var a = document.createElement("a");
        a.className = "pesquisa-resultado";
        a.href = raiz + x.f.url;
        if (x.f.layout === "completa") { a.target = "_blank"; a.rel = "noopener"; }
        var img = document.createElement("img");
        img.src = raiz + "assets/img/icones/" + x.f.icone + ".svg"; img.alt = "";
        var bloco = document.createElement("span");
        var t = document.createElement("strong"); t.textContent = x.f.titulo;
        var s = document.createElement("small"); s.textContent = x.f.area + " › " + x.f.grupo;
        bloco.appendChild(t); bloco.appendChild(s);
        a.appendChild(img); a.appendChild(bloco);
        lista.appendChild(a);
      });
      lista.hidden = false;
    }
    campo.addEventListener("input", mostrar);
    campo.addEventListener("keydown", function (e) {
      if (e.key === "Enter") { var primeiro = lista.querySelector("a"); if (primeiro) primeiro.click(); }
      if (e.key === "ArrowDown") { var p = lista.querySelector("a"); if (p) { p.focus(); e.preventDefault(); } }
      if (e.key === "Escape") { campo.value = ""; mostrar(); }
    });
    lista.addEventListener("keydown", function (e) {
      var ligacoes = Array.prototype.slice.call(lista.querySelectorAll("a"));
      var i = ligacoes.indexOf(document.activeElement);
      if (e.key === "ArrowDown" && i < ligacoes.length - 1) { ligacoes[i + 1].focus(); e.preventDefault(); }
      if (e.key === "ArrowUp") { (i > 0 ? ligacoes[i - 1] : campo).focus(); e.preventDefault(); }
    });
  });

  /* ---------- Abertas recentemente (só neste browser) ---------- */
  var corpo = document.body;
  if (corpo.dataset.ferramenta) {
    try {
      var r = lerRecentes().filter(function (x) { return x.id !== corpo.dataset.ferramenta; });
      r.unshift({ id: corpo.dataset.ferramenta });
      localStorage.setItem("mgf:recentes", JSON.stringify(r.slice(0, 5)));
    } catch (e) { /* armazenamento indisponível: ignorar */ }
  }
  var recentes = document.querySelector("[data-recentes]");
  if (recentes) {
    var porId = {};
    catalogo.forEach(function (f) { porId[f.id] = f; });
    var itens = lerRecentes().map(function (x) { return porId[x.id]; }).filter(Boolean);
    itens.forEach(function (f) {
      var a = document.createElement("a");
      a.href = raiz + f.url; a.textContent = f.titulo + (f.layout === "completa" ? " ↗" : "");
      if (f.layout === "completa") { a.target = "_blank"; a.rel = "noopener"; }
      recentes.appendChild(a);
    });
    recentes.hidden = itens.length === 0;
  }

  /* ---------- Copiar endereço de email ---------- */
  document.querySelectorAll("[data-copiar]").forEach(function (botao) {
    botao.addEventListener("click", function () {
      var texto = botao.getAttribute("data-copiar");
      var original = botao.textContent;
      function feito() { botao.textContent = "Copiado"; setTimeout(function () { botao.textContent = original; }, 2000); }
      function alternativa() {
        var ta = document.createElement("textarea");
        ta.value = texto; ta.style.position = "fixed"; ta.style.opacity = "0";
        document.body.appendChild(ta); ta.select();
        try { document.execCommand("copy"); } catch (e) {}
        document.body.removeChild(ta); feito();
      }
      if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(texto).then(feito, alternativa);
      else alternativa();
    });
  });
})();
