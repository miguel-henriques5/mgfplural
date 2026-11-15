/* =====================================================================
   MGF no Plural — comportamentos comuns das ferramentas (window.MGF)
   Incluído automaticamente no site e na versão descarregável.
   Não faz pedidos de rede nem guarda dados.

   MGF.separadores(raiz)           liga os separadores (.mgf-separador) aos painéis
   MGF.escalas(raiz, configs)      liga escalas de pontuação declaradas em configs
   MGF.copiar(texto, botao)        copia texto e dá feedback no botão
   MGF.decimal(n)                  1.5 → "1,5"
   MGF.dobras(raiz)                liga os cartões que abrem e fecham (.mgf-dobra); devolve abrir(dobra, sim)
   ===================================================================== */
(function () {
  "use strict";

  function decimal(n) {
    return Number.isInteger(n) ? String(n) : String(Math.round(n * 10) / 10).replace(".", ",");
  }

  function separadores(raiz) {
    var seps = raiz.querySelectorAll(".mgf-separador");
    function mostrar(sep) {
      seps.forEach(function (s) {
        var ativo = s === sep;
        s.setAttribute("aria-selected", ativo ? "true" : "false");
        s.tabIndex = ativo ? 0 : -1;
        var p = document.getElementById(s.getAttribute("aria-controls"));
        if (p) p.hidden = !ativo;
      });
    }
    // Na bancada (proposta B) os separadores ficam numa lista vertical à esquerda
    var lista = seps.length && seps[0].closest("[role=tablist]");
    if (lista && lista.closest(".mgf-comandos")) lista.setAttribute("aria-orientation", "vertical");
    seps.forEach(function (s, i) {
      s.tabIndex = s.getAttribute("aria-selected") === "true" ? 0 : -1;
      s.addEventListener("click", function () { mostrar(s); });
      s.addEventListener("keydown", function (e) {
        var d = (e.key === "ArrowRight" || e.key === "ArrowDown") ? 1 : (e.key === "ArrowLeft" || e.key === "ArrowUp") ? -1 : 0;
        if (!d) return;
        var n = seps[(i + d + seps.length) % seps.length];
        n.focus(); mostrar(n); e.preventDefault();
      });
    });
    return mostrar;
  }

  function marcar(el) {
    el.querySelectorAll(".mgf-opcao").forEach(function (o) {
      var i = o.querySelector("input");
      if (i) o.classList.toggle("marcada", i.checked);
    });
  }

  function copiar(texto, botao) {
    function feito() {
      if (!botao) return;
      var original = botao.innerHTML;
      botao.classList.add("copiado");
      if (botao.lastChild) botao.lastChild.textContent = "Copiado";
      setTimeout(function () { botao.innerHTML = original; botao.classList.remove("copiado"); }, 2000);
    }
    function alternativa() {
      var ta = document.createElement("textarea");
      ta.value = texto; ta.setAttribute("readonly", ""); ta.style.position = "fixed"; ta.style.opacity = "0";
      document.body.appendChild(ta); ta.select();
      try { document.execCommand("copy"); } catch (e) { /* sem acesso à área de transferência */ }
      document.body.removeChild(ta); feito();
    }
    if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(texto).then(feito, alternativa);
    else alternativa();
  }

  /* ---------------------------------------------------------------
     Escalas de pontuação.
     Cada painel tem data-escala="id" e contém:
       - caixas:  <input type="checkbox" data-pontos="n">
       - opções:  <input type="radio" name="grupo" value="n">  (um grupo por pergunta;
                  com data-fora-da-soma não conta para a pontuação nem para "completo")
       - #id-pontuacao, #id-barra (opcional), #id-interp
       - botões com data-acao="limpar" | "imprimir" | "copiar"
     configs[id] = {
       max: número (para a barra e o "/max"),
       sufixo: "/max" por defeito, ou p. ex. "pts",
       faixas: [[min, max, "normal|atencao|elevado|alerta|info", "html"], ...]  (a primeira que encaixa;
               se nenhuma encaixar, usa a última),
       mostrar: "sempre" (caixas: mostra após a 1.ª alteração) | "completo" (só com todas
                as perguntas de opção respondidas). Por defeito: "completo" se houver opções.
       interp: função opcional (s, estado) → [nivel, html] | null, em vez de faixas,
       barra: função opcional (s) → percentagem,
       titulo: texto para "Copiar resultado",
       copia: função opcional (s, textoInterp, estado) → linhas extra
     }
     --------------------------------------------------------------- */
  function escalas(raiz, configs) {
    function painel(id) { return raiz.querySelector('[data-escala="' + id + '"]'); }
    function grupos(p) {
      var nomes = [];
      p.querySelectorAll('input[type="radio"]:not([data-fora-da-soma])').forEach(function (r) {
        if (nomes.indexOf(r.name) === -1) nomes.push(r.name);
      });
      return nomes;
    }
    function estado(id) {
      var p = painel(id), s = 0, nomes = grupos(p), respondidas = 0, valores = {};
      p.querySelectorAll('input[type="checkbox"]:checked').forEach(function (c) { s += parseFloat(c.dataset.pontos); });
      nomes.forEach(function (n) {
        var r = p.querySelector('input[name="' + n + '"]:checked');
        if (r) { s += parseFloat(r.value); respondidas++; valores[n] = parseFloat(r.value); }
      });
      return { soma: s, grupos: nomes.length, respondidas: respondidas, valores: valores, completo: respondidas === nomes.length };
    }
    function el(id, sufixo) { return document.getElementById(id + "-" + sufixo); }
    function sufixo(cfg) { return cfg.sufixo || ("/" + cfg.max); }
    function escreverPontuacao(id, cfg, s) {
      el(id, "pontuacao").innerHTML = decimal(s) + "<small>" + sufixo(cfg) + "</small>";
      var b = el(id, "barra");
      if (b) b.style.width = Math.max(0, Math.min(cfg.barra ? cfg.barra(s) : s / cfg.max * 100, 100)) + "%";
    }
    function esconder(id) {
      var c = el(id, "interp"); c.hidden = true; c.innerHTML = ""; delete c.dataset.nivel;
    }
    function calcular(id, alterado) {
      var cfg = configs[id], st = estado(id), s = st.soma;
      escreverPontuacao(id, cfg, s);
      var modo = cfg.mostrar || (st.grupos ? "completo" : "sempre");
      if ((modo === "completo" && !st.completo) || (modo === "sempre" && !alterado)) { esconder(id); return; }
      var r = null;
      if (cfg.interp) r = cfg.interp(s, st);
      else {
        var m = cfg.faixas[cfg.faixas.length - 1];
        for (var i = 0; i < cfg.faixas.length; i++) {
          var f = cfg.faixas[i];
          if (s >= f[0] && s <= f[1]) { m = f; break; }
        }
        r = [m[2], m[3]];
      }
      if (!r) { esconder(id); return; }
      var c = el(id, "interp");
      c.dataset.nivel = r[0]; c.innerHTML = r[1]; c.hidden = false;
    }
    function limpar(id) {
      var p = painel(id);
      p.querySelectorAll("input").forEach(function (i) { if (i.type === "checkbox" || i.type === "radio") i.checked = false; });
      marcar(p);
      escreverPontuacao(id, configs[id], 0);
      esconder(id);
      if (configs[id].aoLimpar) configs[id].aoLimpar();
    }
    function textoCopia(id) {
      var cfg = configs[id], st = estado(id), c = el(id, "interp");
      var suf = sufixo(cfg);
      var t = cfg.titulo + "\nPontuação: " + decimal(st.soma) + (suf.charAt(0) === "/" ? suf : " " + suf);
      var interp = !c.hidden ? c.textContent.replace(/\s+/g, " ").trim() : "";
      if (interp) t += "\nInterpretação: " + interp;
      else if (st.grupos) t += "\nInterpretação: responda a todas as questões para obter resultado.";
      if (cfg.copia) { var extra = cfg.copia(st.soma, interp, st); if (extra) t += "\n" + extra; }
      return t;
    }
    Object.keys(configs).forEach(function (id) {
      var p = painel(id);
      if (!p) return;
      p.addEventListener("change", function () { marcar(p); calcular(id, true); });
      p.addEventListener("click", function (e) {
        var b = e.target.closest("[data-acao]");
        if (!b) return;
        if (b.dataset.acao === "limpar") limpar(id);
        else if (b.dataset.acao === "imprimir") window.print();
        else if (b.dataset.acao === "copiar") copiar(textoCopia(id), b);
      });
      calcular(id, false);
    });
    return { calcular: calcular, limpar: limpar, estado: estado, textoCopia: textoCopia };
  }

  /* ---------------------------------------------------------------
     Cartões que abrem e fecham:
       <div class="mgf-dobra">
         <button type="button" class="mgf-dobra-topo" aria-expanded="false" aria-controls="x">…</button>
         <div class="mgf-dobra-corpo" id="x" hidden>…</div>
       </div>
     --------------------------------------------------------------- */
  function abrir(dobra, sim) {
    var b = dobra.querySelector(".mgf-dobra-topo"), c = dobra.querySelector(".mgf-dobra-corpo");
    if (!b || !c) return;
    b.setAttribute("aria-expanded", sim ? "true" : "false");
    c.hidden = !sim;
  }
  function aberta(dobra) {
    var b = dobra.querySelector(".mgf-dobra-topo");
    return !!b && b.getAttribute("aria-expanded") === "true";
  }
  function dobras(raiz) {
    raiz.addEventListener("click", function (e) {
      var b = e.target.closest(".mgf-dobra-topo");
      if (!b || !raiz.contains(b)) return;
      var d = b.closest(".mgf-dobra");
      abrir(d, !aberta(d));
    });
    return abrir;
  }

  window.MGF = { separadores: separadores, escalas: escalas, copiar: copiar, decimal: decimal, marcar: marcar,
                 dobras: dobras, abrir: abrir, aberta: aberta };
})();
