# Guia de design das ferramentas

Este guia serve para que qualquer ferramenta nova entre no MGF no Plural sem ter de ser refeita. Começa sempre pelo [modelo de ferramenta](modelos/modelo-ferramenta.html): já traz tudo o que está descrito aqui.

## Regras essenciais

1. **Um único ficheiro HTML**, sem nada carregado da internet: nem letras do Google Fonts, nem bibliotecas de CDN, nem imagens externas. Imagens pequenas vão embutidas no ficheiro.
2. **Sem dados de doentes.** A ferramenta não envia nada para a internet e não guarda nomes, números de utente ou datas de nascimento, a não ser que essa seja a função da ferramenta e o Miguel o aprove.
3. **Português de Portugal**, com o Acordo Ortográfico. "Descarregar", não "fazer download". Decimais com vírgula (1,5), datas como 08/11/2026.
4. **Ficha completa:** título, descrição, autor, versão, data de revisão e bibliografia.
5. **Sem emojis.** Usa texto ou os ícones do projeto.
6. **A cor nunca é o único sinal.** Escreve sempre o nível ("Baixo risco", "Alerta").
7. **Funciona em telemóvel** (a partir de 360 px de largura) e **imprime bem**.

## Estrutura do ficheiro

```html
<script type="application/json" id="mgf-ficha"> … ficha … </script>
<style data-mgf="base"> … cores e letras do site (não alterar) … </style>
<style data-mgf="ferramenta"> … estilos só desta ferramenta … </style>

<main class="mgf-ferramenta" id="ferramenta">
  … a ferramenta …
</main>

<script data-mgf="ferramenta"> … JavaScript da ferramenta … </script>
```

Não ponhas cabeçalho com o nome da ferramenta, autor ou bibliografia dentro do `<main>`: o site gera esses elementos a partir da ficha.

## Cores

Usa sempre as variáveis, nunca códigos de cor soltos.

| Variável | Cor | Para quê |
| --- | --- | --- |
| `--cor-verde` | #0F6E64 | Botões principais, ligações, seleção |
| `--cor-verde-fundo` | #13423D | Hover, estados ativos |
| `--cor-menta-clara` | #D7EDE7 | Fundos suaves, títulos de cartões |
| `--cor-ambar-claro` | #F8E7C4 | Destaques quentes |
| `--cor-ambar-texto` | #845406 | Único âmbar para texto |
| `--cor-tinta` | #13201E | Texto principal |
| `--cor-texto-2` / `--cor-texto-3` | #2C3A38 / #4B5B58 | Texto secundário, etiquetas |
| `--cor-papel` | #F6F7F4 | Fundo geral |
| `--cor-linha` | #DCE3E0 | Bordas |

**Cores clínicas** (iguais em todas as ferramentas, não são cores da marca):

| Nível | Uso | Classe |
| --- | --- | --- |
| normal | baixo risco, valor normal | `data-nivel="normal"` / `.mgf-nivel-normal` |
| atenção | risco intermédio, vigiar | `data-nivel="atencao"` / `.mgf-nivel-atencao` |
| alerta | risco alto, urgente | `data-nivel="alerta"` / `.mgf-nivel-alerta` |
| info | informação neutra | `data-nivel="info"` |

Ferramentas grandes em página completa podem ter uma cor de destaque própria, desde que o contraste com o texto seja de pelo menos 4,5:1.

## Letras

| Uso | Letra | Variável |
| --- | --- | --- |
| Títulos | Bricolage Grotesque (400, 600, 800) | `--letra-titulo` |
| Texto | Atkinson Hyperlegible (400, 700) | `--letra-texto` |
| Números, versões, códigos | JetBrains Mono (400, 500) | `--letra-mono` |

Texto com pelo menos 15 px; o normal é 16 px.

## Componentes

| Componente | Classe | Notas |
| --- | --- | --- |
| Separadores | `.mgf-separadores` + `.mgf-separador` (`role="tab"`, `aria-selected`) | Um painel `.mgf-painel` por separador |
| Título de uma escala | `.mgf-titulo-escala` com `h2` + `p` | |
| Cartão de perguntas | `fieldset.mgf-cartao` + `legend.mgf-cartao-titulo` + `.mgf-cartao-corpo` | |
| Opção (caixa ou botão de opção) | `label.mgf-opcao` com `input`, `.mgf-opcao-marca`, `.mgf-opcao-texto`, `.mgf-opcao-pontos` | Os inputs são reais (teclado e leitores de ecrã funcionam) |
| Resultado | `.mgf-resultado` > `.mgf-resultado-topo` (h3 + `.mgf-pontuacao`) + `.mgf-resultado-corpo` | |
| Barra | `.mgf-barra > span` | Largura em % |
| Interpretação | `.mgf-interp` com `data-nivel` | |
| Tabela | `.mgf-tabela-caixa > table.mgf-tabela` | |
| Nota | `.mgf-nota` | Começa por `<strong>Nota.</strong>` |
| Botões | `.mgf-botoes` > `.mgf-botao` (`.mgf-botao-principal` para o principal) | Ícones em SVG, não emojis |

A ferramenta [Escalas cardiovasculares](fonte/ferramentas/recursos-medicos/escalas-e-calculadoras/escalas-cardiovasculares.html) é o exemplo completo.

## Prompt para a tua IA

Copia este texto, junta o ficheiro do modelo e descreve a ferramenta que queres:

```text
Vais criar uma ferramenta clínica para o site MGF no Plural, para médicos de família em Portugal.

Usa o ficheiro modelo-ferramenta.html em anexo como base e segue estas regras:
- Um único ficheiro HTML. Não carregues nada da internet (sem Google Fonts, CDN ou imagens externas).
- Mantém intacto o bloco <style data-mgf="base">. Não definas cores nem letras novas: usa as variáveis CSS (var(--cor-verde), var(--letra-titulo), etc.).
- Escreve a ferramenta dentro de <main class="mgf-ferramenta" id="ferramenta">, usando as classes mgf- do modelo (mgf-cartao, mgf-opcao, mgf-resultado, mgf-interp com data-nivel="normal|atencao|alerta|info", mgf-tabela, mgf-nota, mgf-botao).
- Estilos próprios só no bloco <style data-mgf="ferramenta">; JavaScript só no bloco <script data-mgf="ferramenta">, sem bibliotecas externas.
- Preenche a ficha JSON (id, titulo, descricao, area, grupo, autor, versao, revisto, layout, palavras, bibliografia completa). Opcional: `icone`, o nome de uma ilustração de `assets/img/icones/` (sem `.svg`) que aparece no cabeçalho e nos cartões da ferramenta; sem ele, usa-se a do grupo.
- Português de Portugal com o Acordo Ortográfico; decimais com vírgula.
- Sem emojis. A cor nunca é o único sinal: escreve sempre o nível em texto.
- Não envies dados para a internet e não guardes dados que identifiquem doentes.
- Tem de funcionar em telemóvel (360 px) e imprimir bem.
- Cada limiar, dose ou recomendação tem de ter referência na bibliografia. Não inventes valores.

A ferramenta que quero: [descreve o problema da consulta, a escala ou o cálculo, e as fontes que queres usar].
```

Depois, confirma tu os valores clínicos com as fontes. A IA pode enganar-se.
