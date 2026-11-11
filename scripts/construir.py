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
from urllib.parse import quote

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
        if re.search(r'https?://[^"\'\s]+\.(js|css|woff2?|ttf)\b', t) or "fonts.googleapis" in t:
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


BIBLIOGRAFIA_LONGA = 5   # mais referências do que isto: a lista fica fechada até se carregar


def bibliografia_html(f, titulo_tag="h2"):
    refs = f["bibliografia"]
    itens = "".join(f"<li>{e(r)}</li>" for r in refs)
    autoria = f'<p>Criado por {e(f["autor"])} · v{e(f["versao"])} · revisto a {data_pt(f["revisto"])}</p>'
    if len(refs) > BIBLIOGRAFIA_LONGA:
        return (f'<section class="bibliografia bibliografia-longa"><details id="bib">'
                f'<summary><{titulo_tag} id="bib-titulo">Bibliografia <span>· {len(refs)} referências</span></{titulo_tag}></summary>'
                f'<ol>{itens}</ol></details>{autoria}</section>')
    return (f'<section class="bibliografia" aria-labelledby="bib-titulo"><{titulo_tag} id="bib-titulo">Bibliografia</{titulo_tag}>'
            f'<ol>{itens}</ol>{autoria}</section>')


AVISO_CLINICO = "Apoia, não substitui, o juízo clínico."
AVISO_PRIVACIDADE = ("O que escreves nesta ferramenta não sai do teu computador; mesmo assim, não escrevas dados que "
                     "identifiquem doentes, porque o computador e o browser podem ser usados por outras pessoas.")
FUNDO_TOM = {"menta": "tom-menta", "ambar": "tom-ambar", "papel": "tom-areia", "areia": "tom-areia"}


def tem_estilo(f):
    return bool(re.sub(r"/\*.*?\*/", "", f["estilo"], flags=re.S).strip())


# ---------------------------------------------------------------- página da ferramenta no site

MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def data_pt(iso):
    """2026-11-08 → 8 nov 2026 (formato das datas no site)."""
    a, m, d = iso.split("-")
    return f"{int(d)} {MESES[int(m) - 1]} {a}"


def meta_ficha(f):
    """Linha por baixo do título: resumo curto · autor · versão · data (como no mockup B)."""
    partes = [e(f["resumo"])] if f.get("resumo") else []
    partes += [f'<strong>{e(f["autor"])}</strong>', f'v{e(f["versao"])}', data_pt(f["revisto"])]
    return " · ".join(partes)


SVG_ESCUDO = ('<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" '
              'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z"/>'
              '<path d="M9 12l2 2 4-4"/></svg>')


def fim_div(t, i):
    """Índice a seguir ao </div> que fecha o <div> que começa em t[i]."""
    nivel = 0
    for m in re.finditer(r"<(/?)div\b[^>]*>", t[i:]):
        nivel += -1 if m.group(1) else 1
        if nivel == 0:
            return i + m.end()
    erro("div sem fecho")


def com_aviso(conteudo, f=None):
    """O aviso clínico fica junto dos comandos (fim da coluna da esquerda), como no mockup B;
    numa ferramenta em coluna, logo no início."""
    if f is not None and f.get("aviso_clinico") is False:   # ferramentas que não são clínicas (ex.: horário)
        return conteudo
    aviso = f'<p class="aviso-clinico">{SVG_ESCUDO}{AVISO_CLINICO}</p>'
    marca = '<div class="mgf-comandos">'
    if marca not in conteudo:
        return aviso + "\n" + conteudo
    partes, i = [], 0
    while True:
        j = conteudo.find(marca, i)
        if j < 0:
            break
        k = fim_div(conteudo, j)
        partes.append(conteudo[i:k - len("</div>")] + aviso + "\n")
        i = k - len("</div>")
    partes.append(conteudo[i:])
    return "".join(partes)


VENDOR = Path(__file__).resolve().parent.parent / "assets" / "vendor"


def bibliotecas(f):
    """"bibliotecas" na ficha: ficheiros de assets/vendor/ de que a ferramenta precisa (ex.: jspdf.umd.min.js).
    Ficam dentro do site (nada vem da internet); a versão descarregável leva-os embutidos."""
    nomes = f.get("bibliotecas", [])
    for n in nomes:
        if not (VENDOR / n).is_file():
            erro(f"{f['id']}: biblioteca em falta em assets/vendor/: {n}")
    return nomes


def bibliotecas_css(f, prefixo, autonomo):
    """Folhas de estilo de assets/vendor/ (ex.: leaflet.css): ligadas no site, embutidas na versão descarregável."""
    css = [n for n in bibliotecas(f) if n.endswith(".css")]
    if autonomo:
        return "".join((VENDOR / n).read_text(encoding="utf-8") + "\n" for n in css)
    return "".join(f'<link rel="stylesheet" href="{prefixo}assets/vendor/{n}">\n' for n in css)


def bibliotecas_js(f, prefixo, autonomo):
    js = [n for n in bibliotecas(f) if n.endswith(".js")]
    if autonomo:
        return "".join("<script>\n" + (VENDOR / n).read_text(encoding="utf-8") + "\n</script>\n" for n in js)
    return "".join(f'<script src="{prefixo}assets/vendor/{n}"></script>\n' for n in js)


def impressao(f):
    """"impressao": "doente" na ficha: a folha impressa é para o doente, sem cabeçalho, autoria nem bibliografia."""
    if f.get("impressao") not in (None, "doente"):
        erro(f"{f['id']}: o campo «impressao» da ficha só pode ser «doente»")
    return ' data-impressao="doente"' if f.get("impressao") == "doente" else ""


def classe_corpo(f):
    """Proposta B («bancada», por defeito) ou C («coluna») para o corpo da ferramenta."""
    corpo = f.get("corpo", "bancada")
    if corpo not in ("bancada", "coluna"):
        erro(f"{f['id']}: o campo «corpo» da ficha só pode ser «bancada» ou «coluna»")
    return "corpo-" + corpo


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
            nav_as += f'<a href="{ant["id"]}.html">← {e(ant["titulo"])}</a>'
        if seg:
            nav_as += f'<a class="seguinte" href="{seg["id"]}.html">{e(seg["titulo"])} →</a>'
        nav_as += '</nav>'
    estilo = f'<link rel="stylesheet" href="{prefixo}assets/css/ferramenta.css">\n'
    if tem_estilo(f):
        estilo += f"<style>\n{f['estilo']}\n</style>\n"
    tom = FUNDO_TOM[grupo["tom"]]
    return f"""{cabeca(f["titulo"] + " · MGF no Plural", prefixo, f["descricao"], extra=estilo)}
<body data-ferramenta="{e(f["id"])}" data-titulo="{e(f["titulo"])}"{impressao(f)}>
{topo(prefixo, ferramentas, "ferramentas")}
<div class="contentor ferramenta-pagina pagina-{tom}">
<nav class="migalhas-ferramenta" aria-label="Estás aqui">
<ol class="migalhas">
<li><a href="{prefixo}index.html">Início</a></li>
<li><a href="../index.html">{e(area["nome"])}</a></li>
<li><details class="grupo-menu"><summary>{e(grupo["nome"])} <span>· {len(irmas)}</span>{SVG_SETA_BAIXO}</summary>
<div class="grupo-menu-painel"><a class="grupo-menu-titulo" href="index.html"><img src="{icone(prefixo, grupo["icone"])}" alt="">{e(grupo["nome"])}</a>
<ul>{lista}</ul></div></details></li>
</ol>
</nav>
<header class="ficha" id="conteudo">
<img class="ficha-ilustracao" src="{icone(prefixo, icone_ferramenta(f))}" alt="">
<div class="ficha-titulo">
<h1>{e(f["titulo"])}</h1>
<p class="ficha-meta">{meta_ficha(f)}</p>
</div>
<div class="ficha-acoes">
<a class="botao" href="{prefixo}descarregar/{f["id"]}.html" download="{f["id"]}.html">{SVG_DESCARREGAR}Descarregar</a>
<a class="botao" href="{assunto_feedback(f)}">{SVG_MENSAGEM}Feedback</a>
</div>
</header>
<div class="area-ferramenta {classe_corpo(f)}">
{com_aviso(f["conteudo"], f)}
</div>
<footer class="ferramenta-pe">
{bibliografia_html(f)}
<div class="feedback">
<strong>Encontraste um erro? Escreve-nos e corrigimos juntos.</strong>
<div class="feedback-linha"><a href="{assunto_feedback(f)}">Enviar feedback por email</a> · <span class="mono">{SITE["email"]}</span> <button type="button" class="botao-texto" data-copiar="{SITE["email"]}">Copiar endereço</button></div>
</div>
</footer>
{nav_as}
</div>
{rodape(prefixo)}
{bibliotecas_js(f, prefixo, False)}<script src="{prefixo}assets/js/ferramenta.js"></script>
<script>
{f["script"]}
</script>
</body>
</html>
"""


# ---------------------------------------------------------------- versão autónoma (descarregar)

def tokens_css(fontes=None):
    """tokens.css com as letras embutidas (fontes=None) ou ligadas a partir de <fontes>assets/fonts/."""
    tokens = (ASSETS / "css" / "tokens.css").read_text(encoding="utf-8")

    def embutir(m):
        nome = m.group(1)
        if fontes is not None:
            return f'url("{fontes}assets/fonts/{nome}")'
        dados = base64.b64encode((ASSETS / "fonts" / nome).read_bytes()).decode("ascii")
        return f'url("data:font/woff2;base64,{dados}")'
    return re.sub(r'url\("\.\./fonts/([^"]+)"\)', embutir, tokens)


def css_autonomo(fontes=None):
    tokens = tokens_css(fontes)
    ferr = (ASSETS / "css" / "ferramenta.css").read_text(encoding="utf-8")
    pagina = """
body { margin: 0; background: var(--cor-papel); color: var(--cor-tinta); font-family: var(--letra-texto); line-height: 1.55; }
.autonomo { max-width: 1200px; margin: 0 auto; padding: 20px 24px 48px; display: flex; flex-direction: column; gap: 20px; }
.autonomo-topo { display: flex; flex-direction: column; gap: 4px; padding-bottom: 16px; border-bottom: 1px solid var(--cor-linha); }
.autonomo-marca { display: flex; align-items: center; gap: 8px; font-family: var(--letra-titulo); font-size: 16px; letter-spacing: -0.02em; color: var(--cor-tinta); margin-bottom: 6px; }
.autonomo-marca svg { width: 34px; height: 24px; }
.autonomo-topo h1 { margin: 0; font-family: var(--letra-titulo); font-weight: 800; font-size: 30px; letter-spacing: -0.03em; line-height: 1.1; }
.autonomo-meta { font-size: 15px; color: var(--cor-texto-3); margin: 0; }
.autonomo-meta strong { color: var(--cor-texto-2); }
.autonomo-pe { display: flex; flex-wrap: wrap; gap: 16px 40px; border-top: 1px solid var(--cor-linha); padding-top: 18px; }
.bibliografia { flex: 1 1 420px; font-size: 14px; color: var(--cor-texto-3); }
.bibliografia h2 { font-family: var(--letra-texto); font-size: 15px; font-weight: 700; color: var(--cor-tinta); margin: 0 0 6px; }
.bibliografia ol { margin: 0 0 8px; padding-left: 18px; line-height: 1.5; }
.bibliografia p, .autonomo-rodape { margin: 0; font-size: 14px; color: var(--cor-texto-3); }
.autonomo-avisos { flex: 1 1 320px; display: flex; flex-direction: column; gap: 8px; }
.autonomo a { color: var(--cor-verde); }
@media print {
  body { background: #fff; }
  .autonomo { padding: 0; gap: 6px; }
  .autonomo-topo { gap: 2px; padding-bottom: 6px; }
  .autonomo-marca { font-size: 12px; margin: 0; } .autonomo-marca svg { width: 24px; height: 17px; }
  .autonomo-topo h1 { font-size: 20px; }
  .autonomo-meta, .autonomo-rodape, .bibliografia p { font-size: 9px; }
  .autonomo-pe { padding-top: 6px; }
  .bibliografia, .bibliografia h2 { font-size: 9px; }
  .autonomo-rodape a { text-decoration: none; }
  body[data-impressao="doente"] .autonomo-topo, body[data-impressao="doente"] .autonomo-pe,
  body[data-impressao="doente"] .aviso-clinico { display: none !important; }
}
"""
    return tokens + "\n" + ferr + "\n" + pagina


def pagina_autonoma(f, css, csp=CSP_AUTONOMO):
    url = SITE["url"] + f["caminho"]
    estilo_proprio = f"\n{f['estilo']}\n" if tem_estilo(f) else ""
    return f"""<!doctype html>
<html lang="pt-PT">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="{csp}">
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
<body{impressao(f)}>
<div class="autonomo">
<header class="autonomo-topo">
<span class="autonomo-marca">{simbolo(14)}<span><span style="font-weight:400">mgf no </span><b>plural</b></span></span>
<h1>{e(f["titulo"])}</h1>
<p class="autonomo-meta">{meta_ficha(f)}</p>
</header>
<div class="autonomo-ferramenta {classe_corpo(f)}">
{com_aviso(f["conteudo"], f)}
</div>
<div class="autonomo-pe">
{bibliografia_html(f)}
<div class="autonomo-avisos">
<p class="autonomo-rodape">{AVISO_PRIVACIDADE}</p>
<p class="autonomo-rodape">Versão mais recente e outras ferramentas: <a href="{url}">{e(url)}</a> · Feedback: {SITE["email"]} · Licença MIT</p>
</div>
</div>
</div>
{bibliotecas_js(f, "", True)}<script>
{JS_FERRAMENTA}
</script>
<script>
{f["script"]}
</script>
</body>
</html>
"""


# ---------------------------------------------------------------- página completa (programas, mapas, plataformas)
#
# "layout": "completa" na ficha: abre num separador novo, sem o menu do site, com uma barra flutuante pequena
# (símbolo, autor e versão, Descarregar, Feedback e × para a esconder). Na barra, «autor · versão» abre um painel
# com os avisos, a bibliografia e o contacto.
#  · "imagens_externas": ["https://..."] — únicos servidores de onde a ferramenta pode mostrar imagens (ex.: fotografias
#    do Wikimedia Commons). Não abre mais nada: os pedidos de dados continuam bloqueados (connect-src 'none').
#  · "{{FERRAMENTA:<id>}}" (com as aspas) no script é trocado pela versão descarregável atual dessa ferramenta, como
#    texto JavaScript, para a embutir num <iframe srcdoc>. Assim os programas levam sempre a versão mais recente.

def hosts_imagens(f):
    hs = f.get("imagens_externas", [])
    for h in hs:
        if not re.fullmatch(r"https://[a-z0-9.-]+\.[a-z]{2,}", h):
            erro(f"{f['id']}: servidor de imagens inválido em «imagens_externas»: {h}")
    return hs


def csp_com_imagens(csp, hs):
    return re.sub(r"img-src ([^;]*)", lambda m: "img-src " + m.group(1) + "".join(" " + h for h in hs), csp, count=1) if hs else csp


def csp_ferramenta(csp, f):
    """CSP de uma página completa. Por defeito nada sai da página (connect-src 'none'). Exceções da ficha:
     · "imagens_externas": servidores de imagens (fotografias, mosaicos do mapa);
     · "dados_externos": servidores a que a página pode pedir dados (só o mapa de fundo do Mapa de recursos);
     · "workers": true — a biblioteca do mapa desenha num worker criado a partir de um blob."""
    csp = csp_com_imagens(csp, hosts_imagens(f))
    dados = f.get("dados_externos", [])
    for h in dados:
        if not re.fullmatch(r"https://[a-z0-9.-]+\.[a-z]{2,}", h):
            erro(f"{f['id']}: servidor inválido em «dados_externos»: {h}")
    if dados:
        csp = csp.replace("connect-src 'none'", "connect-src " + " ".join(dados))
    if f.get("workers"):
        csp = re.sub(r"img-src ([^;]*)", r"img-src \1 blob:", csp, count=1)
        csp += "; worker-src blob:; child-src blob:"
    return csp


def texto_js(h):
    """HTML como texto JavaScript que pode ficar dentro de <script> sem o fechar nem confundir o leitor de HTML."""
    s = json.dumps(h, ensure_ascii=False)
    s = s.replace("</", "<\\/").replace("<!--", "\\u003c!--")
    return re.sub(r"<(script)", r"\\u003c\1", s, flags=re.I)


def embutir_ferramentas(f, ferramentas, css, fontes=None):
    def troca(m):
        alvo = [x for x in ferramentas if x["id"] == m.group(1)]
        if not alvo or alvo[0]["layout"] == "completa":
            erro(f"{f['id']}: não há ferramenta normal com o id «{m.group(1)}» para embutir")
        csp = CSP_AUTONOMO if fontes is None else CSP_AUTONOMO.replace("font-src data:", "font-src 'self' data:")
        return texto_js(pagina_autonoma(alvo[0], css, csp))
    return re.sub(r'"\{\{FERRAMENTA:([a-z0-9-]+)\}\}"', troca, f["script"])


def barra_completa(f, prefixo, autonomo):
    url = SITE["url"] + f["caminho"]
    inicio = SITE["url"] if autonomo else f"{prefixo}index.html"
    if autonomo:
        principal = f'<a class="bc-botao" href="{url}" target="_blank" rel="noopener">{SVG_SETA_FORA}<span>Versão mais recente</span></a>'
    else:
        principal = f'<a class="bc-botao" href="{prefixo}descarregar/{f["id"]}.html" download="{f["id"]}.html">{SVG_DESCARREGAR}<span>Descarregar</span></a>'
    refs = "".join(f"<li>{e(r)}</li>" for r in f["bibliografia"])
    fotos = ""
    if any("wikimedia" in h for h in hosts_imagens(f)):
        fotos = ("<h3>Fotografias</h3><p>As fotografias vêm do Wikimedia Commons, com o autor e a licença na legenda de cada uma. "
                 "Precisam de internet: sem ligação, aparece só a legenda com a ligação para a fotografia.</p>")
    if f.get("dados_externos"):
        fotos += ("<h3>Mapa de fundo</h3><p>O mapa de fundo vem da internet (OpenFreeMap; se falhar, Esri). É o único pedido que "
                  "esta página faz, e não leva nada do que escreves. Sem ligação, a pesquisa, as categorias e a lista de recursos funcionam.</p>")
    return f"""<aside class="barra-completa" aria-label="MGF no Plural">
<a class="bc-simbolo" href="{inicio}" title="MGF no Plural — todas as ferramentas"{' target="_blank" rel="noopener"' if autonomo else ''}>{simbolo(14)}<span class="so-leitor">MGF no Plural — todas as ferramentas</span></a>
<button type="button" class="bc-info" aria-expanded="false" aria-controls="bc-painel"><span class="bc-info-texto"><strong>{e(f["autor"])}</strong> · v{e(f["versao"])}</span><span class="so-leitor"> — sobre esta ferramenta</span> ⓘ</button>
{principal}
<a class="bc-botao" href="{assunto_feedback(f)}">{SVG_MENSAGEM}<span>Feedback</span></a>
<button type="button" class="bc-fechar" aria-label="Esconder esta barra">×</button>
<div class="bc-painel" id="bc-painel" hidden>
<h2>{e(f["titulo"])}</h2>
<p class="bc-meta">Criado por {e(f["autor"])} · v{e(f["versao"])} · revisto a {data_pt(f["revisto"])} · licença MIT</p>
<p class="bc-aviso">{"" if f.get("aviso_clinico") is False else AVISO_CLINICO + " "}{AVISO_PRIVACIDADE}</p>
{fotos}<details><summary>Bibliografia · {len(f["bibliografia"])} referência{"" if len(f["bibliografia"]) == 1 else "s"}</summary><ol>{refs}</ol></details>
<h3>Encontraste um erro?</h3>
<p>Escreve-nos e corrigimos juntos: <a href="{assunto_feedback(f)}">{SITE["email"]}</a> · <button type="button" class="bc-copiar" data-copiar="{SITE["email"]}">Copiar endereço</button></p>
<p><a href="{inicio}"{' target="_blank" rel="noopener"' if autonomo else ''}>Todas as ferramentas do MGF no Plural</a></p>
</div>
</aside>
<button type="button" class="bc-mostrar" hidden aria-label="Mostrar a barra do MGF no Plural">{simbolo(14)}</button>"""


JS_BARRA = r"""(function () {
  var b = document.querySelector(".barra-completa"), m = document.querySelector(".bc-mostrar");
  if (!b || !m) return;   /* ficheiro guardado por quem usa: já sem a barra */
  var i = b.querySelector(".bc-info"), p = document.getElementById("bc-painel");
  function painel(abrir) { i.setAttribute("aria-expanded", String(abrir)); p.hidden = !abrir; }
  i.addEventListener("click", function () { painel(p.hidden); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !p.hidden) painel(false); });
  document.addEventListener("click", function (e) { if (!p.hidden && !b.contains(e.target)) painel(false); });
  b.querySelector(".bc-fechar").addEventListener("click", function () { painel(false); b.hidden = true; m.hidden = false; m.focus(); });
  m.addEventListener("click", function () { m.hidden = true; b.hidden = false; i.focus(); });
  var c = b.querySelector("[data-copiar]");
  c.addEventListener("click", function () {
    var t = c.getAttribute("data-copiar"), ok = function () { c.textContent = "Copiado"; setTimeout(function () { c.textContent = "Copiar endereço"; }, 1500); };
    if (navigator.clipboard && window.isSecureContext) { navigator.clipboard.writeText(t).then(ok, function () {}); return; }
    var a = document.createElement("textarea"); a.value = t; document.body.appendChild(a); a.select();
    try { document.execCommand("copy"); ok(); } catch (x) { /* sem acesso: o endereço está escrito ao lado */ } a.remove();
  });
  var id = document.body.getAttribute("data-ferramenta");
  if (id && document.body.hasAttribute("data-recentes")) {
    try {
      var r = JSON.parse(localStorage.getItem("mgf:recentes") || "[]").filter(function (x) { return x.id !== id; });
      r.unshift({ id: id }); localStorage.setItem("mgf:recentes", JSON.stringify(r.slice(0, 5)));
    } catch (x) { /* armazenamento indisponível: ignorar */ }
  }
})();"""

SVG_SETA_FORA = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 4h6v6"/><path d="M20 4l-9 9"/><path d="M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/></svg>'


def pagina_completa(f, ferramentas, css=None):
    """Página completa: no site (css=None) ou a versão autónoma para descarregar (css = CSS com as letras embutidas)."""
    autonomo = css is not None
    prefixo = "../../../"
    estilo = f"\n{f['estilo']}\n" if tem_estilo(f) else ""
    completa = (ASSETS / "css" / "completa.css").read_text(encoding="utf-8")
    if autonomo:
        csp = csp_ferramenta(CSP_AUTONOMO, f)
        cabeca_css = f"<style>\n{tokens_css()}\n{completa}{bibliotecas_css(f, prefixo, True)}{estilo}</style>"
        script = embutir_ferramentas(f, ferramentas, css)
        url = SITE["url"] + f["caminho"]
        comentario = f"""<!--
  {f["titulo"]} — versão {f["versao"]}, revista em {f["revisto"]}
  Criado por {f["autor"]} para o projeto MGF no Plural.
  Versão mais recente: {url}
  Licença MIT. Podes usar, adaptar e partilhar, mantendo o nome de quem criou.
  Este ficheiro funciona sem internet e não envia dados para lado nenhum.
-->
"""
    else:
        csp = csp_ferramenta(CSP_SITE, f)
        cabeca_css = (f'<link rel="icon" href="{prefixo}assets/img/favicon.svg" type="image/svg+xml">\n'
                      f'<link rel="stylesheet" href="{prefixo}assets/css/tokens.css">\n'
                      f'<link rel="stylesheet" href="{prefixo}assets/css/completa.css">\n'
                      + bibliotecas_css(f, prefixo, False)
                      + (f"<style>{estilo}</style>" if estilo else ""))
        script = embutir_ferramentas(f, ferramentas, css_autonomo(fontes=prefixo), fontes=prefixo)
        comentario = ""
    return f"""<!doctype html>
<html lang="pt-PT">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="{csp}">
<meta name="referrer" content="no-referrer">
<title>{e(f["titulo"])} · MGF no Plural</title>
<meta name="description" content="{e(f["descricao"])}">
{comentario}{cabeca_css}
</head>
<body class="pagina-completa" data-ferramenta="{e(f["id"])}" data-titulo="{e(f["titulo"])}"{'' if autonomo else ' data-recentes'}>
{f["conteudo"]}
{barra_completa(f, prefixo, autonomo)}
{bibliotecas_js(f, prefixo, autonomo)}<script data-mgf="barra">
{JS_BARRA}
</script>
<script>
{script}
</script>
</body>
</html>
"""


# ---------------------------------------------------------------- mapa de recursos: zonas e modelo
#
# Cada zona é uma ferramenta do grupo «zonas» (ex.: fonte/ferramentas/mapa-de-recursos/zonas/amadora.html). Tudo o
# que é da zona está num só bloco do script, entre «/* {{ZONA}}» e «/* {{FIM-ZONA}} */». O modelo para outras zonas é
# o mesmo mapa com esse bloco trocado pelo de fonte/modelo/mapa-de-recursos-zona.js (estrutura e categorias, sem
# recursos). Para publicar o mapa que um colega enviar: tirar-lhe o bloco ZONA e criar uma ficha nova com ele.

ZONA_RE = re.compile(r"  /\* \{\{ZONA\}\}.*?/\* \{\{FIM-ZONA\}\} \*/\n", re.S)
PAGINA_MODELO = "ferramentas/mapa-de-recursos/modelo.html"


def mapa_modelo(ferramentas):
    """Ficha do modelo vazio, feita a partir do primeiro mapa de zona que tenha «modelo» na ficha."""
    base = [f for f in ferramentas if f.get("modelo")]
    if not base:
        return None
    f = base[0]
    m = f["modelo"]
    zona = (FONTE / m["zona"]).read_text(encoding="utf-8")
    script, n = ZONA_RE.subn(lambda _: zona, f["script"])
    if n != 1:
        erro(f"{f['id']}: o script tem de ter exatamente um bloco {{{{ZONA}}}} … {{{{FIM-ZONA}}}}")
    return dict(f, id=m["ficheiro"].removesuffix(".html"), titulo=m["titulo"], script=script, caminho=PAGINA_MODELO,
                descricao="Estrutura do mapa de recursos (categorias, filtros, pesquisa e lista para imprimir) sem recursos, para preencheres com os da tua zona.",
                bibliografia=[r for r in f["bibliografia"] if r.startswith(("Mapa de fundo", "Bibliotecas"))],
                palavras=["modelo", "mapa", "recursos", "comunidade"])


def cartao_zona(f, prefixo):
    return (f'<a class="cartao-zona" href="zonas/{f["id"]}.html" target="_blank" rel="noopener">'
            f'<span class="cartao-zona-mapa" aria-hidden="true"><img src="{icone(prefixo, "mapa")}" alt=""></span>'
            f'<span class="cartao-zona-texto"><strong>{e(f.get("zona", f["titulo"]))}</strong>'
            f'<span>{e(f.get("resumo", ""))}</span>'
            f'<small>{e(f.get("unidade_territorial", ""))}{" · " if f.get("unidade_territorial") else ""}{e(f["autor"])} · v{e(f["versao"])}</small></span>'
            f'<span class="etiqueta-completa">↗ abre o mapa noutra janela</span></a>')


def pagina_area_mapa(area, ferramentas):
    """Página de escolha: as zonas com mapa (por região) e a ligação para o modelo."""
    prefixo = "../../"
    zonas = [f for f in ferramentas if f["area"] == area["id"]]
    regioes = {}
    for f in zonas:
        regioes.setdefault(f.get("regiao", "Outras zonas"), []).append(f)
    blocos = "".join(f'<section class="grupo"><div class="grupo-cabeca"><h2>{e(r)}</h2><span class="mono">{len(fs)}</span></div>'
                     f'<div class="grelha grelha-zonas">{"".join(cartao_zona(f, prefixo) for f in fs)}</div></section>'
                     for r, fs in regioes.items())
    return f"""{cabeca(area["nome"] + " · MGF no Plural", prefixo, area["descricao"])}
<body>
{topo(prefixo, ferramentas, "ferramentas")}
<main id="conteudo">
<div class="contentor area-topo">
<ol class="migalhas" aria-label="Estás aqui"><li><a href="{prefixo}index.html">Início</a></li><li aria-current="page">{e(area["nome"])}</li></ol>
<div class="area-titulo"><img src="{icone(prefixo, area["icone"])}" alt="">
<div><h1>{e(area["nome"])}</h1><p>Recursos da comunidade num mapa: saúde, apoio social, desporto, ensino, cultura e espaços verdes, com uma lista para imprimir para o utente. Escolhe a tua zona.</p></div></div>
</div>
<div class="contentor seccao">
<h2 class="mapa-passo"><span>1</span> Escolhe a zona</h2>
{blocos}
<h2 class="mapa-passo"><span>2</span> Não encontras a tua zona?</h2>
<a class="cartao-modelo" href="modelo.html">
<img src="{icone(prefixo, "pasta")}" alt="">
<span><strong>Modelo do mapa para a tua zona</strong>
<span>O mesmo mapa, com as categorias e a lista para imprimir, mas sem recursos. Descarrega-o, preenche-o com os recursos da tua zona e partilha-o connosco para o pormos no site.</span></span>
<span class="cartao-modelo-seta" aria-hidden="true">→</span></a>
</div>
</main>
{rodape(prefixo)}
</body>
</html>
"""


def pagina_modelo_mapa(area, modelo, ferramentas):
    prefixo = "../../"
    zona = (FONTE / [f for f in ferramentas if f.get("modelo")][0]["modelo"]["zona"]).read_text(encoding="utf-8")
    exemplo = re.search(r"Exemplo:\n\s*(\{.*?\})\n", zona).group(1)
    return f"""{cabeca("Modelo do mapa de recursos · MGF no Plural", prefixo, modelo["descricao"])}
<body>
{topo(prefixo, ferramentas, "ferramentas")}
<main id="conteudo">
<div class="contentor area-topo">
<ol class="migalhas" aria-label="Estás aqui"><li><a href="{prefixo}index.html">Início</a></li><li><a href="index.html">{e(area["nome"])}</a></li><li aria-current="page">Modelo para a tua zona</li></ol>
<div class="area-titulo"><img src="{icone(prefixo, "pasta")}" alt="">
<div><h1>Modelo do mapa para a tua zona</h1><p>A estrutura toda do mapa de recursos (categorias, filtros, pesquisa e lista para imprimir), sem recursos. Preenches tu com os da tua zona.</p></div></div>
</div>
<div class="contentor seccao modelo-mapa">
<div class="modelo-mapa-acoes">
<a class="botao-escuro" href="{prefixo}descarregar/{modelo["id"]}.html" download="{modelo["id"]}.html">{SVG_DESCARREGAR}Descarregar o modelo</a>
<a class="botao-claro" href="{prefixo}descarregar/{modelo["id"]}.html" target="_blank" rel="noopener">Ver o modelo vazio ↗</a>
</div>
<ol class="modelo-passos">
<li><strong>Descarrega o modelo.</strong> É um único ficheiro HTML. Funciona no teu computador, sem instalar nada.</li>
<li><strong>Abre-o num editor de texto</strong> (Bloco de notas, TextEdit em texto simples, VS Code) e procura o bloco <code>ZONA</code>, no início do script. É o único sítio a mudar: o resto (categorias, cores, filtros, lista para imprimir) fica igual em todas as zonas.</li>
<li><strong>Escreve os dados da zona:</strong> nome, concelho, descrição, centro do mapa (latitude e longitude do centro de saúde; no Google Maps, botão direito no local) e as fontes de onde tiraste os recursos.</li>
<li><strong>Acrescenta os recursos</strong>, um por linha, no formato do exemplo. Só o nome, a categoria e as coordenadas são obrigatórios. Se preferires, cola o bloco numa IA com a tua lista de recursos e pede-lhe que o preencha.</li>
<li><strong>Abre o ficheiro no browser</strong> para confirmares que os recursos aparecem no sítio certo.</li>
<li><strong>Partilha-o connosco:</strong> envia o ficheiro para <a href="mailto:{SITE["email"]}?subject={quote("Mapa de recursos — nova zona")}">{SITE["email"]}</a>, com o nome com que queres aparecer como autor. Revemos e pomos a tua zona no site, para todos.</li>
</ol>
<div class="modelo-mapa-ajuda">
<h2>Categorias</h2>
<p><code>saude</code> Saúde (com <code>s</code>: SNS, Privados ou Convencionados) · <code>social</code> Apoio social · <code>desporto</code> Clubes e desporto · <code>ensino</code> Ensino · <code>verde</code> Espaços verdes e rios · <code>cultura</code> Cultura e património · <code>junta</code> Juntas de freguesia e câmara municipal.</p>
<h2>Exemplo de um recurso</h2>
<pre><code>{e(exemplo)}</code></pre>
<p class="mono-nota">Não ponhas dados de utentes nem nomes de profissionais: o mapa é público.</p>
</div>
</div>
</main>
{rodape(prefixo)}
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
    ("M-CHAT", "Só a indicação de quando aplicar e a contagem das falhas (por número de item, na Saúde infantil e juvenil). O texto das perguntas não é reproduzido: a reprodução eletrónica precisa de autorização.", "https://mchatscreen.com/", "Site oficial (versão M-CHAT-R/F)"),
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
        if f["layout"] == "completa":
            escrever(RAIZ / f["caminho"], pagina_completa(f, ferramentas))
            escrever(RAIZ / "descarregar" / f"{f['id']}.html", pagina_completa(f, ferramentas, css))
            continue
        escrever(RAIZ / f["caminho"], pagina_ferramenta(f, ferramentas))
        escrever(RAIZ / "descarregar" / f"{f['id']}.html", pagina_autonoma(f, css))
    modelo = mapa_modelo(ferramentas)
    if modelo:
        escrever(RAIZ / "descarregar" / f"{modelo['id']}.html", pagina_completa(modelo, ferramentas, css))
    for a in ESTRUTURA["areas"]:
        if any(f["area"] == a["id"] for f in ferramentas):
            if a["id"] == "mapa-de-recursos":
                escrever(RAIZ / "ferramentas" / a["id"] / "index.html", pagina_area_mapa(a, ferramentas))
                if modelo:
                    escrever(RAIZ / PAGINA_MODELO, pagina_modelo_mapa(a, modelo, ferramentas))
            else:
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
