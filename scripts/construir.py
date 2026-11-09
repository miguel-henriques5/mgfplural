#!/usr/bin/env python3
"""
MGF no Plural — construção do site.

Lê as ferramentas em fonte/ferramentas/ e a estrutura em fonte/estrutura.json
e gera, na raiz do repositório:

  index.html                         página inicial
  acerca.html                        acerca, contribuir, privacidade, offline
  ferramentas/<area>/index.html      página de cada área com ferramentas ("Ver tudo")
  ferramentas/<area>/<grupo>/index.html   página de cada grupo (só as ferramentas desse grupo)
  ferramentas/<area>/<grupo>/<id>.html   página da ferramenta no site
  descarregar/<id>.html              versão autónoma, para descarregar (funciona offline)
  assets/js/catalogo.js              catálogo para a pesquisa

Uso:  python3 scripts/construir.py
Só usa a biblioteca padrão do Python 3.8+. Não altera nada em fonte/.
"""
import base64
import datetime as dt
import html
import json
import re
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FONTE = RAIZ / "fonte"
ASSETS = RAIZ / "assets"
JS_FERRAMENTA = (Path(__file__).resolve().parent.parent / "assets" / "js" / "ferramenta.js").read_text(encoding="utf-8")
ESTRUTURA = json.loads((FONTE / "estrutura.json").read_text(encoding="utf-8"))
SITE = ESTRUTURA["site"]
HOJE = dt.date.today().isoformat()

CAMPOS_OBRIGATORIOS = ["id", "titulo", "descricao", "area", "grupo", "autor", "versao", "revisto", "layout", "bibliografia"]

CSP_SITE = ("default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; font-src 'self' data:; connect-src 'none'; object-src 'none'; "
            "base-uri 'none'; form-action 'none'")
CSP_AUTONOMO = ("default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; "
                "font-src data:; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'")

e = html.escape


def erro(msg):
    print("ERRO:", msg, file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------- símbolo e ícones

SIMBOLO_PATHS = (
    '<path d="M5.2 86.6L10.8 63.4Q16.0 42.0 30.2 25.2L33.8 20.8Q48.0 4.0 70.0 2.9L108.0 1.1Q130.0 0.0 150.9 7.0L157.1 9.0Q178.0 16.0 186.0 36.5L198.0 67.5Q206.0 88.0 209.0 103.0L209.0 103.0Q212.0 118.0 204.9 138.8L203.1 144.2Q196.0 165.0 177.8 177.3L168.2 183.7Q150.0 196.0 128.9 202.1L126.1 202.9Q105.0 209.0 88.5 203.0L88.5 203.0Q72.0 197.0 54.0 184.3L26.0 164.7Q8.0 152.0 4.1 130.4L3.9 129.6Q0.0 108.0 5.2 86.6Z" fill="none" stroke="{c1}" stroke-width="{sw}" stroke-linejoin="round"/>'
    '<path d="M56.9 112.7L61.1 102.3Q70.0 80.0 86.6 62.7L103.4 45.3Q120.0 28.0 143.8 25.3L166.2 22.7Q190.0 20.0 210.6 32.3L249.4 55.7Q270.0 68.0 277.9 90.7L280.1 97.3Q288.0 120.0 284.1 143.7L279.9 168.3Q276.0 192.0 264.9 213.3L263.1 216.7Q252.0 238.0 228.3 241.9L173.7 251.1Q150.0 255.0 127.6 246.4L117.4 242.6Q95.0 234.0 82.3 213.6L67.7 190.4Q55.0 170.0 51.5 152.5L51.5 152.5Q48.0 135.0 56.9 112.7Z" fill="#DE9B2C"/>'
    '<path d="M169.0 97.5L169.0 97.5Q175.0 75.0 194.2 60.6L195.8 59.4Q215.0 45.0 238.2 38.7L246.8 36.3Q270.0 30.0 292.2 39.2L307.8 45.8Q330.0 55.0 344.9 73.8L357.1 89.2Q372.0 108.0 368.2 131.7L365.8 146.3Q362.0 170.0 349.0 190.2L335.0 211.8Q322.0 232.0 298.4 236.5L293.6 237.5Q270.0 242.0 247.0 235.3L245.0 234.7Q222.0 228.0 201.8 215.1L198.2 212.9Q178.0 200.0 173.0 182.5L173.0 182.5Q168.0 165.0 165.5 142.5L165.5 142.5Q163.0 120.0 169.0 97.5Z" fill="none" stroke="{c2}" stroke-width="{sw}" stroke-linejoin="round"/>'
)


def simbolo(sw=13, c1="#0F6E64", c2="#13201E", rotulo=None):
    aria = f'role="img" aria-label="{e(rotulo)}"' if rotulo else 'aria-hidden="true"'
    return (f'<svg viewBox="-3 -3 378 262" {aria} focusable="false">'
            + SIMBOLO_PATHS.format(c1=c1, c2=c2, sw=sw) + '</svg>')


def logo(prefixo, negativo=False):
    c1, c2 = ("#8FCFC0", "#F6F7F4") if negativo else ("#0F6E64", "#13201E")
    return (f'<a class="logo" href="{prefixo}index.html">{simbolo(13, c1, c2)}'
            f'<span class="logo-texto"><span>mgf no </span><b>plural</b></span>'
            f'<span class="so-leitor"> — página inicial</span></a>')


def icone(prefixo, nome):
    return f'{prefixo}assets/img/icones/{nome}.svg'


def icone_ferramenta(f):
    """Ilustração própria da ferramenta (campo «icone» da ficha) ou, se não tiver, a do grupo."""
    if f.get("icone"):
        if not (ASSETS / "img" / "icones" / f"{f['icone']}.svg").exists():
            erro(f"{f['id']}: ilustração em falta: assets/img/icones/{f['icone']}.svg")
        return f["icone"]
    return grupo_por_id(area_por_id(f["area"]), f["grupo"])["icone"]


def tem_ferramentas(ferramentas, area_id, grupo_id):
    return any(f["area"] == area_id and f["grupo"] == grupo_id for f in ferramentas)


SVG_DESCARREGAR = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 4v11"/><polyline points="7 10 12 15 17 10"/><path d="M4 19h16"/></svg>'
SVG_MENSAGEM = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 5h16v11H9l-5 4z"/></svg>'
SVG_SETA_BAIXO = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="6 9 12 15 18 9"/></svg>'


# ---------------------------------------------------------------- leitura das ferramentas

def extrair(padrao, texto, nome, obrigatorio=True):
    m = re.search(padrao, texto, re.S)
    if not m:
        if obrigatorio:
            erro(f"{nome}: bloco em falta ({padrao[:40]}…)")
        return ""
    return m.group(1).strip("\n")


def ler_ferramentas():
    ferramentas = []
    for f in sorted((FONTE / "ferramentas").rglob("*.html")):
        t = f.read_text(encoding="utf-8")
        ficha = json.loads(extrair(r'<script type="application/json" id="mgf-ficha">(.*?)</script>', t, f.name))
        for c in CAMPOS_OBRIGATORIOS:
            if c not in ficha:
                erro(f"{f.name}: falta o campo '{c}' na ficha")
        if ficha["id"] != f.stem:
            erro(f"{f.name}: o id da ficha ({ficha['id']}) tem de ser igual ao nome do ficheiro")
        if re.search(r'https?://[^"\'\s]+\.(js|css|woff2?|ttf)', t) or "fonts.googleapis" in t:
            erro(f"{f.name}: carrega scripts, estilos ou letras de fora do site")
        ficha["estilo"] = extrair(r'<style data-mgf="ferramenta">(.*?)</style>', t, f.name, False)
        ficha["conteudo"] = extrair(r'(<main class="mgf-ferramenta" id="ferramenta">.*?</main>)', t, f.name)
        ficha["script"] = extrair(r'<script data-mgf="ferramenta">(.*?)</script>', t, f.name, False)
        rel = f.relative_to(FONTE / "ferramentas")
        if rel.parts[0] != ficha["area"] or rel.parts[1] != ficha["grupo"]:
            erro(f"{f.name}: a pasta não corresponde à área/grupo da ficha")
        ficha["caminho"] = f"ferramentas/{ficha['area']}/{ficha['grupo']}/{ficha['id']}.html"
        ferramentas.append(ficha)
    return ferramentas


def area_por_id(aid):
    for a in ESTRUTURA["areas"]:
        if a["id"] == aid:
            return a
    erro(f"área desconhecida: {aid}")


def grupo_por_id(area, gid):
    for g in area["grupos"]:
        if g["id"] == gid:
            return g
    erro(f"grupo desconhecido: {gid} em {area['id']}")


# ---------------------------------------------------------------- peças comuns

def cabeca(titulo, prefixo, descricao, csp=CSP_SITE, extra=""):
    return f"""<!doctype html>
<html lang="pt-PT" data-raiz="{prefixo}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="{csp}">
<meta name="referrer" content="no-referrer">
<title>{e(titulo)}</title>
<meta name="description" content="{e(descricao)}">
<link rel="icon" href="{prefixo}assets/img/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{prefixo}assets/css/tokens.css">
<link rel="stylesheet" href="{prefixo}assets/css/site.css">
{extra}</head>"""


def menu_ferramentas(prefixo, ferramentas, ativo=False):
    partes = []
    principal = ESTRUTURA["areas"][0]
    partes.append(f'<a class="menu-area-titulo" href="{prefixo}ferramentas/{principal["id"]}/index.html">'
                  f'<img src="{icone(prefixo, principal["icone"])}" alt="">{e(principal["nome"])} →</a>')
    partes.append('<div class="menu-grupos">')
    for g in principal["grupos"]:
        fs = [f for f in ferramentas if f["area"] == principal["id"] and f["grupo"] == g["id"]]
        if fs:
            partes.append(f'<div><a class="menu-grupo-titulo" href="{prefixo}ferramentas/{principal["id"]}/{g["id"]}/index.html"><img src="{icone(prefixo, g["icone"])}" alt="">{e(g["nome"])}</a>')
        else:
            partes.append(f'<div><span class="menu-grupo-titulo"><img src="{icone(prefixo, g["icone"])}" alt="">{e(g["nome"])}</span>')
        for f in fs:
            seta = " ↗" if f["layout"] == "completa" else ""
            alvo = ' target="_blank" rel="noopener"' if f["layout"] == "completa" else ""
            partes.append(f'<a class="menu-ligacao" href="{prefixo}{f["caminho"]}"{alvo}>{e(f["titulo"])}{seta}</a>')
        if not fs:
            partes.append('<span class="menu-em-breve">Em breve</span>')
        partes.append('</div>')
    partes.append('</div>')
    lateral = ['<div class="menu-lateral"><span class="etiqueta-mono">Outras áreas</span>']
    for a in ESTRUTURA["areas"][1:]:
        fs = [f for f in ferramentas if f["area"] == a["id"]]
        if fs:
            lateral.append(f'<a class="menu-outra-area" href="{prefixo}ferramentas/{a["id"]}/index.html">'
                           f'<img src="{icone(prefixo, a["icone"])}" alt=""><span>{e(a["nome"])}</span></a>')
        else:
            lateral.append(f'<span class="menu-outra-area em-breve"><img src="{icone(prefixo, a["icone"])}" alt="">'
                           f'<span>{e(a["nome"])}<small>Em breve</small></span></span>')
    lateral.append('</div>')
    classe = "menu-ferramentas ativo" if ativo else "menu-ferramentas"
    return (f'<details class="{classe}"><summary>Ferramentas {SVG_SETA_BAIXO}</summary>'
            f'<div class="menu-painel"><div class="menu-painel-interior"><div>{"".join(partes)}</div>{"".join(lateral)}</div></div></details>')


def topo(prefixo, ferramentas, atual=""):
    acerca = ' aria-current="page"' if atual == "acerca" else ""
    return f"""<a class="saltar" href="#conteudo">Saltar para o conteúdo</a>
<header class="topo"><div class="contentor">
{logo(prefixo)}
<nav class="nav-principal" aria-label="Principal">
{menu_ferramentas(prefixo, ferramentas, atual == "ferramentas")}
<a href="{prefixo}acerca.html#contribuir">Contribuir</a>
<a href="{prefixo}acerca.html"{acerca}>Acerca</a>
<a class="botao-escuro" href="{prefixo}acerca.html#offline">{SVG_DESCARREGAR}Usar offline</a>
</nav>
</div></header>"""


def rodape(prefixo):
    return f"""<footer class="rodape"><div class="contentor">
<div class="rodape-linha">
<div class="rodape-contacto">
{logo(prefixo, negativo=True)}
<span>{e(SITE["contacto_nome"])}<br>{e(SITE["contacto_funcao"])}</span>
<a href="mailto:{SITE["email"]}">{SITE["email"]}</a>
</div>
<nav aria-label="Rodapé">
<a href="{prefixo}acerca.html">Acerca</a>
<a href="{prefixo}acerca.html#contribuir">Contribuir</a>
<a href="{prefixo}acerca.html#escalas">Escalas não incluídas</a>
<a href="{prefixo}acerca.html#offline">Usar offline</a>
<a href="{prefixo}acerca.html#privacidade">Privacidade</a>
<a href="{SITE["repositorio"]}">Código no GitHub</a>
</nav>
</div>
<div class="rodape-fim">
<span class="rodape-aviso">As ferramentas apoiam, não substituem, o juízo clínico. O que escreves nelas não sai do teu computador; mesmo assim, não escrevas dados que identifiquem doentes, porque o computador e o browser podem ser usados por outras pessoas.</span>
<span class="mono">licença MIT · site v{SITE["versao"]} · {HOJE}</span>
</div>
</div></footer>
<script src="{prefixo}assets/js/catalogo.js"></script>
<script src="{prefixo}assets/js/site.js"></script>"""


def iniciais(nome):
    p = [x for x in nome.split() if x[:1].isupper()]
    return (p[0][0] + p[-1][0]) if len(p) > 1 else nome[:2].upper()


def assunto_feedback(f):
    from urllib.parse import quote
    assunto = f"Feedback: {f['titulo']} (v{f['versao']})"
    corpo = ("Ferramenta: " + f["titulo"] + " (v" + f["versao"] + ")\n\n"
             "O que encontrei ou sugiro:\n\n\n"
             "Por favor, não incluas dados que identifiquem doentes.")
    return f"mailto:{SITE['email']}?subject={quote(assunto)}&body={quote(corpo)}"


def bibliografia_html(f, titulo_tag="h2"):
    itens = "".join(f"<li>{e(r)}</li>" for r in f["bibliografia"])
    return (f'<section class="bibliografia" aria-labelledby="bib-titulo"><{titulo_tag} id="bib-titulo">Bibliografia</{titulo_tag}>'
            f'<ol>{itens}</ol>'
            f'<p>Criado por {e(f["autor"])} · v{e(f["versao"])} · revisto em {e(f["revisto"])}</p></section>')


AVISO_CLINICO = "Apoia, não substitui, o juízo clínico."
AVISO_PRIVACIDADE = ("O que escreves nesta ferramenta não sai do teu computador; mesmo assim, não escrevas dados que "
                     "identifiquem doentes, porque o computador e o browser podem ser usados por outras pessoas.")
FUNDO_TOM = {"menta": "tom-menta", "ambar": "tom-ambar", "papel": "tom-areia", "areia": "tom-areia"}


def tem_estilo(f):
    return bool(re.sub(r"/\*.*?\*/", "", f["estilo"], flags=re.S).strip())


# ---------------------------------------------------------------- página da ferramenta no site

def pagina_ferramenta(f, ferramentas):
    prefixo = "../../../"
    area = area_por_id(f["area"])
    grupo = grupo_por_id(area, f["grupo"])
    irmas = [x for x in ferramentas if x["area"] == f["area"] and x["grupo"] == f["grupo"]]
    i = irmas.index(f)
    atual = ' aria-current="page"'
    lista = "".join(
        f'<li><a href="{x["id"]}.html"{atual if x is f else ""}>{e(x["titulo"])}</a></li>' for x in irmas)
    ant = irmas[i - 1] if i > 0 else None
    seg = irmas[i + 1] if i < len(irmas) - 1 else None
    nav_as = ""
    if ant or seg:
        nav_as = '<nav class="anterior-seguinte" aria-label="Outras ferramentas do grupo">'
        if ant:
            nav_as += f'<a href="{ant["id"]}.html"><span>← Anterior</span><strong>{e(ant["titulo"])}</strong></a>'
        if seg:
            nav_as += f'<a class="seguinte" href="{seg["id"]}.html"><span>Seguinte →</span><strong>{e(seg["titulo"])}</strong></a>'
        nav_as += '</nav>'
    estilo = f'<link rel="stylesheet" href="{prefixo}assets/css/ferramenta.css">\n'
    if tem_estilo(f):
        estilo += f"<style>\n{f['estilo']}\n</style>\n"
    tom = FUNDO_TOM[grupo["tom"]]
    return f"""{cabeca(f["titulo"] + " · MGF no Plural", prefixo, f["descricao"], extra=estilo)}
<body data-ferramenta="{e(f["id"])}" data-titulo="{e(f["titulo"])}">
{topo(prefixo, ferramentas, "ferramentas")}
<div class="contentor ferramenta-pagina">
<ol class="migalhas" aria-label="Estás aqui">
<li><a href="{prefixo}index.html">Início</a></li>
<li><a href="../index.html">{e(area["nome"])}</a></li>
<li><a href="index.html">{e(grupo["nome"])}</a></li>
<li aria-current="page">{e(f["titulo"])}</li>
</ol>
<div class="ferramenta-topo">
<div class="ficha {tom}" id="conteudo">
<div class="ficha-cabeca">
<img class="ficha-ilustracao" src="{icone(prefixo, icone_ferramenta(f))}" alt="">
<div class="ficha-titulo">
<h1>{e(f["titulo"])}</h1>
<div class="ficha-meta">
<span class="autor"><span class="autor-iniciais" aria-hidden="true">{e(iniciais(f["autor"]))}</span>Criado por <strong>{e(f["autor"])}</strong></span>
<span class="ficha-versao">v{e(f["versao"])} · revisto em {e(f["revisto"])} · <a href="#bib-titulo">bibliografia</a></span>
</div>
</div>
</div>
<div class="ficha-base">
<p class="aviso-clinico"><img src="{icone(prefixo, "privacidade")}" alt="">{AVISO_CLINICO}</p>
<div class="ficha-acoes">
<a class="botao botao-principal" href="{prefixo}descarregar/{f["id"]}.html" download="{f["id"]}.html">{SVG_DESCARREGAR}Descarregar HTML</a>
<a class="botao" href="{assunto_feedback(f)}">{SVG_MENSAGEM}Enviar feedback</a>
</div>
</div>
</div>
<nav class="ferramenta-irmas {tom}" aria-label="{e(grupo["nome"])}">
<a class="ferramenta-irmas-grupo" href="index.html"><img src="{icone(prefixo, grupo["icone"])}" alt="">{e(grupo["nome"])}</a>
<ul>{lista}</ul>
</nav>
</div>
<div class="area-ferramenta">
{f["conteudo"]}
</div>
<div class="ferramenta-pe">
{bibliografia_html(f)}
<div class="feedback">
<strong>Encontraste um erro? Escreve-nos e corrigimos juntos.</strong>
<div class="feedback-linha"><a href="{assunto_feedback(f)}">Enviar feedback por email</a><code>{SITE["email"]}</code><button type="button" class="botao-texto" data-copiar="{SITE["email"]}">Copiar endereço</button></div>
</div>
</div>
{nav_as}
</div>
{rodape(prefixo)}
<script src="{prefixo}assets/js/ferramenta.js"></script>
<script>
{f["script"]}
</script>
</body>
</html>
"""


# ---------------------------------------------------------------- versão autónoma (descarregar)

def css_autonomo():
    tokens = (ASSETS / "css" / "tokens.css").read_text(encoding="utf-8")

    def embutir(m):
        nome = m.group(1)
        dados = base64.b64encode((ASSETS / "fonts" / nome).read_bytes()).decode("ascii")
        return f'url("data:font/woff2;base64,{dados}")'
    tokens = re.sub(r'url\("\.\./fonts/([^"]+)"\)', embutir, tokens)
    ferr = (ASSETS / "css" / "ferramenta.css").read_text(encoding="utf-8")
    pagina = """
body { margin: 0; background: var(--cor-papel); color: var(--cor-tinta); font-family: var(--letra-texto); }
.autonomo { max-width: 960px; margin: 0 auto; padding: 24px 16px 48px; display: flex; flex-direction: column; gap: 16px; }
.autonomo-topo { background: var(--cor-branco); border: 1px solid var(--cor-linha-suave); border-radius: 22px; padding: 20px 22px; display: flex; flex-direction: column; gap: 12px; }
.autonomo-marca { display: flex; align-items: center; gap: 10px; font-family: var(--letra-titulo); font-size: 18px; letter-spacing: -0.02em; color: var(--cor-tinta); }
.autonomo-marca svg { width: 40px; height: 28px; }
.autonomo-topo h1 { margin: 0; font-family: var(--letra-titulo); font-weight: 800; font-size: 32px; letter-spacing: -0.03em; line-height: 1.05; }
.autonomo-meta { font-family: var(--letra-mono); font-size: 13px; color: var(--cor-texto-3); }
.autonomo-aviso { background: var(--cor-menta-clara); border-radius: 12px; padding: 10px 14px; font-size: 15px; }
.autonomo-ferramenta { background: var(--cor-branco); border: 1px solid var(--cor-linha-suave); border-radius: 22px; padding: 22px; }
.bibliografia { background: var(--cor-branco); border: 1px solid var(--cor-linha-suave); border-radius: 18px; padding: 16px 20px; font-size: 13px; color: var(--cor-texto-3); }
.bibliografia h2 { font-family: var(--letra-mono); font-size: 12px; font-weight: 500; letter-spacing: .08em; text-transform: uppercase; color: var(--cor-verde); margin: 0 0 8px; }
.bibliografia ol { margin: 0 0 8px; padding-left: 18px; }
.bibliografia p, .autonomo-rodape { margin: 0; font-family: var(--letra-mono); font-size: 12px; color: var(--cor-texto-3); }
.autonomo a { color: var(--cor-verde); }
@media print {
  body { background: #fff; }
  .autonomo { padding: 0; gap: 6px; }
  .autonomo-topo, .autonomo-ferramenta, .bibliografia { border: 0; padding: 0 0 6px; }
  .autonomo-topo { gap: 2px; }
  .autonomo-marca { font-size: 12px; } .autonomo-marca svg { width: 24px; height: 17px; }
  .autonomo-topo h1 { font-size: 20px; }
  .autonomo-meta, .autonomo-rodape, .bibliografia p { font-size: 9px; }
  .autonomo-aviso { background: none; padding: 0; font-size: 10px; }
  .bibliografia { font-size: 9px; }
  .autonomo-rodape a { text-decoration: none; }
}
"""
    return tokens + "\n" + ferr + "\n" + pagina


def pagina_autonoma(f, css):
    url = SITE["url"] + f["caminho"]
    estilo_proprio = f"\n{f['estilo']}\n" if tem_estilo(f) else ""
    return f"""<!doctype html>
<html lang="pt-PT">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="{CSP_AUTONOMO}">
<title>{e(f["titulo"])} · MGF no Plural</title>
<!--
  {f["titulo"]} — versão {f["versao"]}, revista em {f["revisto"]}
  Criado por {f["autor"]} para o projeto MGF no Plural.
  Versão mais recente: {url}
  Licença MIT. Podes usar, adaptar e partilhar, mantendo o nome de quem criou.
  Este ficheiro funciona sem internet e não envia dados para lado nenhum.
-->
<style>
{css}{estilo_proprio}</style>
</head>
<body>
<div class="autonomo">
<header class="autonomo-topo">
<span class="autonomo-marca">{simbolo(14)}<span><span style="font-weight:400">mgf no </span><b>plural</b></span></span>
<h1>{e(f["titulo"])}</h1>
<span class="autonomo-meta">Criado por {e(f["autor"])} · v{e(f["versao"])} · revisto em {e(f["revisto"])}</span>
<span class="autonomo-aviso">{AVISO_CLINICO}</span>
</header>
<div class="autonomo-ferramenta">
{f["conteudo"]}
</div>
{bibliografia_html(f)}
<p class="autonomo-rodape">{AVISO_PRIVACIDADE}</p>
<p class="autonomo-rodape">Versão mais recente e outras ferramentas: <a href="{url}">{e(url)}</a> · Feedback: {SITE["email"]} · Licença MIT</p>
</div>
<script>
{JS_FERRAMENTA}
</script>
<script>
{f["script"]}
</script>
</body>
</html>
"""


# ---------------------------------------------------------------- página inicial

TONS = ["menta", "ambar", "papel", "areia"]


def pagina_inicio(ferramentas):
    p = ""
    total = len(ferramentas)
    blocos = []
    principal = ESTRUTURA["areas"][0]
    n_principal = len([f for f in ferramentas if f["area"] == principal["id"]])
    grupos = []
    for g in principal["grupos"]:
        n = len([f for f in ferramentas if f["area"] == principal["id"] and f["grupo"] == g["id"]])
        conteudo = (f'<span class="mancha"></span><img src="{icone(p, g["icone"])}" alt="">'
                    f'<span class="cartao-grupo-rodape"><strong>{e(g["nome"])}</strong>'
                    f'<span>{n if n else "Em breve"}</span></span>')
        if n:
            grupos.append(f'<a class="cartao-grupo tom-{g["tom"]}" href="ferramentas/{principal["id"]}/{g["id"]}/index.html">{conteudo}</a>')
        else:
            grupos.append(f'<div class="cartao-grupo tom-{g["tom"]} em-breve">{conteudo}</div>')
    blocos.append(f"""<div class="bloco-area">
<div class="bloco-area-cabeca"><img src="{icone(p, principal["icone"])}" alt="">
<div><h3>{e(principal["nome"])}</h3><span>{e(principal["descricao"])}</span></div>
<a href="ferramentas/{principal["id"]}/index.html">Ver tudo →</a></div>
<div class="grelha">{"".join(grupos)}</div>
</div>""")
    outras = []
    for a in ESTRUTURA["areas"][1:]:
        n = len([f for f in ferramentas if f["area"] == a["id"]])
        corpo = (f'<img src="{icone(p, a["icone"])}" alt=""><strong>{e(a["nome"])}</strong>'
                 f'<p>{e(a["descricao"])}</p>')
        if n:
            outras.append(f'<a class="cartao-area" href="ferramentas/{a["id"]}/index.html">{corpo}'
                          f'<span class="etiqueta-mono">{n} ferramenta{"s" if n > 1 else ""} →</span></a>')
        else:
            outras.append(f'<div class="cartao-area em-breve">{corpo}<span class="em-breve-texto">Em breve</span></div>')
    blocos.append(f'<div class="grelha">{"".join(outras)}</div>')

    return f"""{cabeca("MGF no Plural — Ferramentas clínicas feitas por quem as usa", p, "Ferramentas clínicas para Medicina Geral e Familiar, feitas em comunidade. Gratuitas, abertas e sem recolha de dados.")}
<body>
{topo(p, ferramentas)}
<main id="conteudo">
<section class="contentor heroi">
<div class="heroi-texto">
<span class="selo">Gratuito · Código aberto · Não recolhe dados</span>
<h1>Ferramentas clínicas feitas por quem as usa.</h1>
<p>Escalas, guias de prescrição, interpretação de exames e programas de saúde para Medicina Geral e Familiar. Feitas em comunidade, para usar na consulta ou descarregar.</p>
<div class="pesquisa" data-pesquisa>
<form role="search" onsubmit="return false">
<label for="procura" class="so-leitor">Procurar ferramenta</label>
<input id="procura" type="search" placeholder="Procurar: Wells, CHA₂DS₂-VASc, vacinação…" autocomplete="off">
</form>
<div class="pesquisa-resultados" hidden></div>
</div>
</div>
<div class="heroi-simbolo">{simbolo(4.5, rotulo="Símbolo mgf no plural: três formas que se cruzam")}</div>
</section>
<section class="contentor recentes" data-recentes hidden aria-label="Abertas recentemente">
<span class="etiqueta-mono">Abertas recentemente · só neste browser</span>
</section>
<section class="contentor seccao" id="areas">
<div class="seccao-cabeca"><h2>Por onde começar</h2><span class="mono">{total} ferramenta{"s" if total != 1 else ""} publicada{"s" if total != 1 else ""} · migração em curso</span></div>
{"".join(blocos)}
</section>
<section class="circulo" id="contribuir"><div class="contentor">
<h2>Entra no círculo.</h2>
<div class="circulo-passos">
<div><strong>Dá feedback</strong><span>Encontraste um erro ou tens uma ideia? Cada ferramenta tem um botão para nos escreveres.</span></div>
<div><strong>Faz a tua ferramenta</strong><span>Usa o modelo e o guia de design com a tua IA. Não precisas de saber programar.</span></div>
<div><strong>Envia por email</strong><span>Anexa o HTML. Revemo-la juntos antes de entrar no site, com o teu nome.</span></div>
</div>
<div class="circulo-botoes">
<a class="botao-branco" href="acerca.html#contribuir">Como contribuir</a>
<a class="botao-contorno" href="{SITE["repositorio"]}/blob/main/GUIA-DESIGN.md">Guia de design</a>
</div>
</div></section>
</main>
{rodape(p)}
</body>
</html>
"""


# ---------------------------------------------------------------- cartão de ferramenta e página de grupo

def cartao_ferramenta(f, prefixo, pasta):
    completa = f["layout"] == "completa"
    alvo = ' target="_blank" rel="noopener"' if completa else ""
    etiqueta = '<span class="etiqueta-completa">↗ separador novo</span>' if completa else ""
    return (f'<a class="cartao-ferramenta" href="{pasta}{f["id"]}.html"{alvo}>'
            f'<span class="cartao-ferramenta-cabeca"><img src="{icone(prefixo, icone_ferramenta(f))}" alt=""><strong>{e(f["titulo"])}</strong></span>'
            f'{etiqueta}<p>{e(f["descricao"])}</p>'
            f'<span class="cartao-ferramenta-rodape"><span>{e(f["autor"])} · v{e(f["versao"])}</span><span aria-hidden="true">→</span></span></a>')


def pagina_grupo(area, grupo, ferramentas):
    prefixo = "../../../"
    fs = [f for f in ferramentas if f["area"] == area["id"] and f["grupo"] == grupo["id"]]
    botoes = []
    for g in area["grupos"]:
        if not tem_ferramentas(ferramentas, area["id"], g["id"]):
            continue
        atual = ' aria-current="page"' if g is grupo else ""
        n = len([f for f in ferramentas if f["area"] == area["id"] and f["grupo"] == g["id"]])
        botoes.append(f'<a class="{FUNDO_TOM[g["tom"]]}" href="../{g["id"]}/index.html"{atual}>'
                      f'<img src="{icone(prefixo, g["icone"])}" alt="">{e(g["nome"])} <span>{n}</span></a>')
    botoes.append(f'<a class="ver-tudo" href="../index.html">Ver tudo →</a>')
    cartoes = "".join(cartao_ferramenta(f, prefixo, "") for f in fs)
    return f"""{cabeca(grupo["nome"] + " · MGF no Plural", prefixo, area["descricao"])}
<body>
{topo(prefixo, ferramentas, "ferramentas")}
<main id="conteudo">
<div class="contentor area-topo">
<ol class="migalhas" aria-label="Estás aqui"><li><a href="{prefixo}index.html">Início</a></li><li><a href="../index.html">{e(area["nome"])}</a></li><li aria-current="page">{e(grupo["nome"])}</li></ol>
<div class="area-titulo grupo-titulo {FUNDO_TOM[grupo["tom"]]}"><img src="{icone(prefixo, grupo["icone"])}" alt="">
<div><h1>{e(grupo["nome"])}</h1><p>{len(fs)} ferramenta{"s" if len(fs) != 1 else ""} · {e(area["nome"])}</p></div></div>
</div>
<div class="grupos-chips"><nav class="contentor" aria-label="Outros grupos de ferramentas">{"".join(botoes)}</nav></div>
<div class="contentor seccao">
<div class="grelha">{cartoes}</div>
</div>
</main>
{rodape(prefixo)}
</body>
</html>
"""


# ---------------------------------------------------------------- página de área

def pagina_area(area, ferramentas):
    prefixo = "../../"
    fs_area = [f for f in ferramentas if f["area"] == area["id"]]
    chips, seccoes = [], []
    for g in area["grupos"]:
        fs = [f for f in fs_area if f["grupo"] == g["id"]]
        if not fs:
            continue
        chips.append(f'<a href="#{g["id"]}">{e(g["nome"])} · {len(fs)}</a>')
        cartoes = []
        for f in fs:
            cartoes.append(cartao_ferramenta(f, prefixo, f'{g["id"]}/'))
        fundo = {"menta": "var(--cor-menta-clara)", "ambar": "var(--cor-ambar-claro)", "papel": "var(--cor-branco)", "areia": "var(--cor-areia)"}[g["tom"]]
        seccoes.append(f"""<section class="grupo" id="{g["id"]}">
<div class="grupo-cabeca"><img src="{icone(prefixo, g["icone"])}" alt="" style="background:{fundo}"><h2><a href="{g["id"]}/index.html">{e(g["nome"])}</a></h2><span class="mono">{len(fs)}</span></div>
<div class="grelha">{"".join(cartoes)}</div>
</section>""")
    em_falta = [g["nome"] for g in area["grupos"] if not [f for f in fs_area if f["grupo"] == g["id"]]]
    aviso = ""
    if em_falta:
        aviso = (f'<p class="aviso-migracao">Estamos a migrar as restantes ferramentas para o site. '
                 f'Em breve: {e(", ".join(em_falta))}.</p>')
    return f"""{cabeca(area["nome"] + " · MGF no Plural", prefixo, area["descricao"])}
<body>
{topo(prefixo, ferramentas, "ferramentas")}
<main id="conteudo">
<div class="contentor area-topo">
<ol class="migalhas" aria-label="Estás aqui"><li><a href="{prefixo}index.html">Início</a></li><li aria-current="page">{e(area["nome"])}</li></ol>
<div class="area-titulo"><img src="{icone(prefixo, area["icone"])}" alt="">
<div><h1>{e(area["nome"])}</h1><p>{e(area["descricao"])}</p></div></div>
</div>
<div class="grupos-chips"><nav class="contentor" aria-label="Grupos">{"".join(chips)}</nav></div>
<div class="contentor seccao">
{aviso}
{"".join(seccoes)}
</div>
</main>
{rodape(prefixo)}
</body>
</html>
"""


# ---------------------------------------------------------------- acerca

ESCALAS_NAO_INCLUIDAS = [
    ("MMSE (Mini-Mental State Examination)", "Não incluída. A PAR detém os direitos e não autoriza a reprodução da escala completa.", "https://www.parinc.com/products/MMSE-2", "Versão oficial (PAR)"),
    ("MoCA (Montreal Cognitive Assessment)", "Não incluída. Os autores proíbem versões eletrónicas e exigem formação certificada desde 2021.", "https://mocacognition.com/", "Site oficial do MoCA"),
    ("HADS", "Só a calculadora de pontuação, sem o texto dos itens. Vendida pela GL Assessment.", "https://www.gl-assessment.co.uk/products/hospital-anxiety-depression-scale/", "GL Assessment"),
    ("EPDS (Escala de Depressão Pós-Parto de Edimburgo)", "Só a calculadora de pontuação. Distribuir o texto exige autorização do Royal College of Psychiatrists.", "https://camcops.readthedocs.io/en/latest/tasks/epds.html", "Esclarecimento sobre os direitos"),
    ("Escala de Sonolência de Epworth", "Só a calculadora de pontuação. O autor exige licença.", "https://epworthsleepinessscale.com/", "Site oficial"),
    ("STOP-Bang", "Só a calculadora de pontuação. O uso precisa de autorização dos autores.", "https://www.stopbang.ca/", "Site oficial"),
    ("GPCOG", "Só a calculadora de pontuação. É gratuito para clínicos, mas não pode ser alterado e não tem versão portuguesa no site oficial.", "https://gpcog.com.au/", "Site oficial"),
    ("Mini-Cog", "Só a calculadora de pontuação. Uso clínico livre, mas não pode ser modificado.", "https://mini-cog.com/", "Site oficial"),
    ("M-CHAT", "Só a indicação de quando aplicar. A reprodução eletrónica precisa de autorização.", "https://mchatscreen.com/", "Site oficial (versão M-CHAT-R/F)"),
]


def pagina_acerca(ferramentas):
    p = ""
    escalas = "".join(
        f'<tr><td><strong>{e(n)}</strong></td><td>{e(d)}</td><td><a href="{u}" rel="noopener">{e(t)}</a></td></tr>'
        for n, d, u, t in ESCALAS_NAO_INCLUIDAS)
    return f"""{cabeca("Acerca · MGF no Plural", p, "Quem faz o MGF no Plural, como contribuir, privacidade e uso offline.")}
<body>
{topo(p, ferramentas, "acerca")}
<main id="conteudo">
<section class="contentor area-topo">
<span class="etiqueta-mono">Acerca</span>
<h1 style="font-weight:800;font-size:clamp(2.4rem,5vw,3.6rem);letter-spacing:-0.035em">Feito por muitos. Para todos.</h1>
<div class="texto-longo">
<p>Olá, o meu nome é Miguel Henriques, sou médico de família na Amadora e criei este site para que, em conjunto, possamos construir ferramentas que nos ajudem no dia a dia como médicos de família.</p>
<p>O site é totalmente gratuito e não recolhe qualquer informação tua nem dos dados que nele colocas. Para além de gratuito, é também totalmente aberto, o que significa que podes descarregar qualquer ferramenta e o respetivo código, para usares livremente offline ou para construíres novas ferramentas com base nas disponíveis no site.</p>
<p>Em vários locais do site vais poder descarregar as ferramentas, dar feedback sobre as mesmas por email e enviar-me novas ferramentas para eu poder incluí-las no site.</p>
<p>Espero que a MGF no Plural possa passar a ser a tua companheira diária no centro de saúde e ajudar-te nos vários desafios do dia a dia!</p>
</div>
<div class="feedback" style="max-width:520px">
<strong>{e(SITE["contacto_nome"])}</strong>
<span>{e(SITE["contacto_funcao"])}</span>
<div class="feedback-linha"><a href="mailto:{SITE["email"]}">Escrever por email</a><code>{SITE["email"]}</code><button type="button" class="botao-texto" data-copiar="{SITE["email"]}">Copiar endereço</button></div>
</div>
</section>

<section class="circulo" id="contribuir" style="margin-top:40px"><div class="contentor">
<h2>Entra no círculo.</h2>
<div class="circulo-passos">
<div><strong>1 · Dá feedback</strong><span>Em cada ferramenta há um botão "Enviar feedback" que abre um email com o nome e a versão já preenchidos.</span></div>
<div><strong>2 · Faz uma ferramenta</strong><span>Descarrega o modelo, lê o guia de design e pede à tua IA. Sai logo com o aspeto do site.</span></div>
<div><strong>3 · Envia por email</strong><span>Anexa o HTML. Revemo-la juntos e entra no site com o teu nome. Ao enviar, aceitas a licença MIT e confirmas que és autor ou tens autorização.</span></div>
</div>
<div class="circulo-botoes">
<a class="botao-branco" href="modelos/modelo-ferramenta.html" download>Descarregar o modelo</a>
<a class="botao-contorno" href="{SITE["repositorio"]}/blob/main/GUIA-DESIGN.md">Guia de design</a>
<a class="botao-contorno" href="{SITE["repositorio"]}/blob/main/CONTRIBUIR.md">Guia para contribuir</a>
</div>
</div></section>

<section class="contentor seccao" id="escalas">
<div class="seccao-cabeca"><h2>Escalas que não podemos publicar por inteiro</h2></div>
<p style="margin:0;max-width:760px;color:var(--cor-texto-2)">Algumas escalas têm direitos de autor que impedem reproduzir o texto dos itens num site. Nestes casos, publicamos só o que é permitido e indicamos onde obter a versão autorizada.</p>
<div style="overflow-x:auto;background:var(--cor-branco);border:1px solid var(--cor-linha-suave);border-radius:18px">
<table class="tabela-simples" style="width:100%;border-collapse:collapse;font-size:15px">
<thead><tr><th style="text-align:left;padding:10px 14px">Escala</th><th style="text-align:left;padding:10px 14px">O que publicamos</th><th style="text-align:left;padding:10px 14px">Versão autorizada</th></tr></thead>
<tbody>{escalas}</tbody>
</table>
</div>
<p style="margin:0;color:var(--cor-texto-2)">Alternativas livres para rastreio cognitivo: GPCOG e Mini-Cog (em migração para o site).</p>
</section>

<section class="contentor seccao" id="offline" style="padding-top:0">
<div class="seccao-cabeca"><h2>Usar offline</h2></div>
<div class="grelha">
<div class="cartao-area" style="min-height:0"><strong style="margin-top:0">Uma ferramenta</strong><p>Em cada ferramenta, carrega em "Descarregar HTML". O ficheiro funciona sem internet e mantém o aspeto do site.</p></div>
<a class="cartao-area" style="min-height:0" href="{SITE["zip"]}"><strong style="margin-top:0">O site inteiro (ZIP)</strong><p>Descomprime e abre o ficheiro index.html. Útil em computadores com restrições de internet.</p><span class="etiqueta-mono">Descarregar →</span></a>
</div>
</section>

<section class="contentor seccao" id="privacidade" style="padding-top:0">
<div class="seccao-cabeca"><h2>Privacidade e licença</h2></div>
<div class="grelha">
<div class="cartao-area" style="min-height:0"><img src="{icone(p, "privacidade")}" alt=""><strong style="margin-top:0">Privacidade</strong><p>Sem contas, sem cookies, sem estatísticas. As ferramentas estão impedidas de enviar dados para a internet. O que guardas numa ferramenta fica na memória deste computador e és responsável por não partilhar essa memória nem os ficheiros exportados em locais sem segurança.</p></div>
<div class="cartao-area" style="min-height:0"><img src="{icone(p, "puzzle")}" alt=""><strong style="margin-top:0">Licença MIT</strong><p>Usa, adapta e partilha, mantendo o nome de quem criou. Código no <a href="{SITE["repositorio"]}">GitHub</a>. As escalas de terceiros mantêm os direitos dos seus autores.</p></div>
</div>
</section>
</main>
{rodape(p)}
</body>
</html>
"""


# ---------------------------------------------------------------- catálogo

def escrever_catalogo(ferramentas):
    dados = []
    for f in ferramentas:
        area = area_por_id(f["area"])
        grupo = grupo_por_id(area, f["grupo"])
        dados.append({
            "id": f["id"], "titulo": f["titulo"], "descricao": f["descricao"],
            "area": area["nome"], "grupo": grupo["nome"], "icone": icone_ferramenta(f),
            "url": f["caminho"], "layout": f["layout"], "autor": f["autor"],
            "palavras": f.get("palavras", []),
        })
    js = ("/* Gerado por scripts/construir.py — não editar à mão. */\n"
          "window.MGF_CATALOGO = " + json.dumps(dados, ensure_ascii=False, indent=1) + ";\n")
    (ASSETS / "js" / "catalogo.js").write_text(js, encoding="utf-8")


# ---------------------------------------------------------------- principal

def gerar_modelo(css):
    """Modelo para colegas: ficheiro único, com as cores e letras do site embutidas."""
    modelo = (FONTE / "modelo" / "modelo-ferramenta.html").read_text(encoding="utf-8")
    base = "/* NÃO ALTERAR: cores, letras e componentes do MGF no Plural (gerado automaticamente). */\n" + css
    modelo = modelo.replace("/* {{BASE}} */", base).replace("/* {{BASE_JS}} */", "/* NÃO ALTERAR (gerado automaticamente). */\n" + JS_FERRAMENTA)
    escrever(RAIZ / "modelos" / "modelo-ferramenta.html", modelo)


def escrever(caminho, texto):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8")


def main():
    ferramentas = ler_ferramentas()
    ordem = {(a["id"], g["id"]): (i, j) for i, a in enumerate(ESTRUTURA["areas"]) for j, g in enumerate(a["grupos"])}
    ferramentas.sort(key=lambda f: (ordem[(f["area"], f["grupo"])], f.get("ordem", 99), f["titulo"]))

    for pasta in ("ferramentas", "descarregar"):
        shutil.rmtree(RAIZ / pasta, ignore_errors=True)

    css = css_autonomo()
    for f in ferramentas:
        escrever(RAIZ / f["caminho"], pagina_ferramenta(f, ferramentas))
        escrever(RAIZ / "descarregar" / f"{f['id']}.html", pagina_autonoma(f, css))
    for a in ESTRUTURA["areas"]:
        if any(f["area"] == a["id"] for f in ferramentas):
            escrever(RAIZ / "ferramentas" / a["id"] / "index.html", pagina_area(a, ferramentas))
            for g in a["grupos"]:
                if tem_ferramentas(ferramentas, a["id"], g["id"]):
                    escrever(RAIZ / "ferramentas" / a["id"] / g["id"] / "index.html", pagina_grupo(a, g, ferramentas))
    escrever(RAIZ / "index.html", pagina_inicio(ferramentas))
    escrever(RAIZ / "acerca.html", pagina_acerca(ferramentas))
    escrever_catalogo(ferramentas)
    gerar_modelo(css)
    print(f"Site construído: {len(ferramentas)} ferramenta(s).")


if __name__ == "__main__":
    main()
