# Guia de design das ferramentas

Este guia serve para que qualquer ferramenta nova entre no MGF no Plural sem ter de ser refeita. Começa sempre pelo [modelo de ferramenta](modelos/modelo-ferramenta.html): já traz tudo o que está descrito aqui.

## Regras essenciais

1. **Um único ficheiro HTML**, sem nada carregado da internet: nem letras do Google Fonts, nem bibliotecas de CDN, nem imagens externas. Imagens pequenas vão embutidas no ficheiro. As únicas exceções são as imagens dos mapas e as fotografias com licença aberta das ferramentas em página completa (ver «Página completa»).
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

## Arrumação da página

Todas as páginas de ferramenta seguem a mesma arrumação (aprovada a 10/11/2026):

- **Cabeçalho compacto**, gerado pelo site: migalhas com o menu das outras ferramentas do grupo, ilustração, título e uma linha com o resumo (campo `resumo` da ficha, até ~50 caracteres), autor, versão e data; os botões Descarregar e Feedback, discretos. O aviso «Apoia, não substitui, o juízo clínico» é posto pelo site no fim da coluna dos comandos.
- **Bibliografia** no fim da página; com mais de 5 referências fica fechada e abre ao carregar.
- **Folha para o doente:** se o que se imprime é para o doente, põe `"impressao": "doente"` na ficha e a impressão sai sem cabeçalho, autoria nem bibliografia.
- **Ferramentas sem conteúdo clínico** (organização, horários): `"aviso_clinico": false` na ficha tira o aviso «Apoia, não substitui, o juízo clínico».
- **Bibliotecas** (por exemplo para criar PDF ou Excel): nada vem da internet. Põe o ficheiro em `assets/vendor/`, com a licença ao lado, e lista-o na ficha em `"bibliotecas": ["jspdf.umd.min.js"]`. A página do site carrega-o a partir de `assets/vendor/` e a versão para descarregar leva-o lá dentro. Hoje há jsPDF 2.5.1 e jsPDF-AutoTable 3.8.2 (MIT) e SheetJS 0.18.5 (Apache 2.0).
- **Caixas de seleção:** o estilo comum (linha leve, uma só seta para baixo) aplica-se sozinho; não lhes dês bordas nem setas próprias.
- **A ferramenta assenta no fundo da página**, sem caixa à volta. Uma caixa, não caixas dentro de caixas.
- **Bancada** (por defeito): comandos à esquerda, resposta à direita. A resposta fica sempre à vista enquanto se preenche. No telemóvel passa a uma só coluna.

```html
<div class="mgf-bancada">                      <!-- calculadora: perguntas largas, resultado estreito -->
  <div class="mgf-comandos"> … perguntas e campos … </div>
  <div class="mgf-resposta"> … mgf-resultado, mgf-botoes … </div>
</div>

<div class="mgf-bancada mgf-bancada-guia">     <!-- guia de consulta: coluna estreita à esquerda -->
  <div class="mgf-comandos"> … pesquisa, filtros, separadores (ficam em lista vertical), legenda … </div>
  <div class="mgf-resposta"> … secções e cartões … </div>
</div>
```

  Numa ferramenta com separadores de escalas, cada painel tem a sua bancada, por baixo do título da escala. Enquanto não há resultado, `<div class="mgf-espera">` logo a seguir a um elemento com `hidden` mostra «O resultado aparece aqui…».
- **Coluna** (quando a bancada não faz sentido, por exemplo uma lista larga que se vai construindo): põe `"corpo": "coluna"` na ficha. A ferramenta fica numa só coluna e começa por uma pergunta grande (`<h2 class="mgf-pergunta">`).
- **O resultado aparece uma vez.** Uma frase ou número grande com o que interessa; detalhes repetidos ficam num `<details>` fechado.
- **O que se usa em cada consulta vem primeiro.** Legendas, princípios e notas longas ficam abaixo ou na coluna da esquerda.

### Página completa (programas, mapas, plataformas)

Ferramentas grandes, que ocupam o ecrã todo, levam `"layout": "completa"` na ficha (decidido a 08/11/2026). Abrem num separador novo, sem o menu do site, e o `<main>` fica só com a aplicação. O site junta uma **barra pequena no canto inferior direito**: símbolo (volta ao site), autor e versão (abre um painel com os avisos, a bibliografia e o contacto), Descarregar, Feedback e × para a esconder. Na impressão a barra não aparece.

- **Letras e cores:** as letras da marca são obrigatórias; a cor de destaque tem alguma liberdade, com bom contraste. As cores clínicas são as de sempre.
- **Ferramentas do site dentro de um programa:** em vez de copiar o HTML de outra ferramenta, escreve `"{{FERRAMENTA:<id>}}"` (com as aspas) no JavaScript. O site troca-o pela versão para descarregar atual dessa ferramenta, como texto, para pôr num `<iframe srcdoc>`. Para esconder o cabeçalho dela dentro do programa, usa `.autonomo-topo{display:none}`. Exemplo: a Saúde infantil e juvenil leva a Vacinação e as Doses pediátricas; a Vigilância da gravidez leva a Planificação e os Fármacos na gravidez.
- **Imagens de fora** (só quando não podem ir no ficheiro, por exemplo fotografias do Wikimedia Commons): lista os servidores em `"imagens_externas": ["https://upload.wikimedia.org"]`. Cada imagem leva autor, licença e ligação para a origem na legenda, e a ferramenta tem de continuar a funcionar sem internet (mostra a legenda com a ligação). Os pedidos de dados continuam bloqueados.
- **Sem `alert()` nem `confirm()`:** para limpar tudo, pede um segundo clique no mesmo botão.
- **Bibliotecas com folha de estilo** (por exemplo `leaflet.css`): lista-as em `"bibliotecas"` como os ficheiros `.js`. No site ficam ligadas; na versão para descarregar vão lá dentro.

### Modelos de documentos (Documentação)

- Sem logótipo, nomes ou siglas de nenhuma unidade nem nomes de profissionais. O nome e a sigla da unidade e da ULS são campos que se escrevem no próprio documento (todos os sítios ficam iguais) e o logótipo escolhe-se no computador. Em branco, imprimem como uma linha para preencher à mão.
- «Guardar HTML» guarda o documento já com a unidade e o logótipo de quem o adaptou, sem a barra do site.

### Mapa de recursos por zonas

- Cada zona é uma ferramenta do grupo `zonas` (`fonte/ferramentas/mapa-de-recursos/zonas/<zona>.html`), com `zona`, `regiao` e `unidade_territorial` na ficha. A página do Mapa de recursos agrupa as zonas por região.
- Tudo o que é da zona (nome, descrição, centro do mapa, notas, fontes e recursos) está num só bloco do script, entre `/* {{ZONA}}` e `/* {{FIM-ZONA}} */`. O modelo para outras zonas é o mesmo mapa com o bloco de `fonte/modelo/mapa-de-recursos-zona.js` (sem recursos). Para publicar o mapa que um colega enviar, tira-se o bloco ZONA do ficheiro dele e cria-se uma ficha nova.
- O mapa é a única exceção ao «nada sai da página»: `"dados_externos": ["https://tiles.openfreemap.org"]` (mapa de fundo vetorial), `"imagens_externas": ["https://services.arcgisonline.com"]` (alternativa) e `"workers": true` (a biblioteca desenha num worker). Sem internet, a pesquisa, as categorias e a lista funcionam, e o mapa avisa que o fundo não aparece.

## Cores

Usa sempre as variáveis, nunca códigos de cor soltos.

| Variável | Cor | Para quê |
| --- | --- | --- |
| `--cor-verde` | #0F6E64 | Só ação e seleção: botão principal, ligações, opção ou separador escolhido |
| `--cor-verde-fundo` | #13423D | Hover, estados ativos |
| `--cor-menta-clara` | #D7EDE7 | Fundos suaves de contexto (não em barras de título) |
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
| Só versões, datas e código | JetBrains Mono (400, 500) | `--letra-mono` |

Texto com pelo menos 15 px; o normal é 17 px. Valores, resultados e campos ficam em Atkinson (distingue 0 de O e 1 de l), não em mono. Rótulos em texto normal a negrito, não em maiúsculas espaçadas. Sem barras escuras: o resultado tem moldura verde e fundo branco.

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
| Bancada | `.mgf-bancada` > `.mgf-comandos` + `.mgf-resposta` (`.mgf-bancada-guia` num guia) | Ver «Arrumação da página» |
| Lugar do resultado | `.mgf-espera` logo a seguir ao resultado escondido | Some quando o resultado aparece |
| Pergunta grande | `h2.mgf-pergunta` | Só no corpo «coluna» |
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
- Arruma a ferramenta em bancada, como no modelo: perguntas e campos em <div class="mgf-comandos">, resultado em <div class="mgf-resposta">, os dois dentro de <div class="mgf-bancada">. Num guia de consulta usa <div class="mgf-bancada mgf-bancada-guia"> com a pesquisa e os filtros à esquerda. Se a bancada não fizer sentido, põe "corpo": "coluna" na ficha e começa por uma pergunta (<h2 class="mgf-pergunta">). Sem caixas dentro de caixas.
- Estilos próprios só no bloco <style data-mgf="ferramenta">; JavaScript só no bloco <script data-mgf="ferramenta">, sem bibliotecas externas.
- Preenche a ficha JSON (id, titulo, descricao, resumo com até 50 caracteres, area, grupo, autor, versao, revisto, layout, palavras, bibliografia completa). Opcional: `icone`, o nome de uma ilustração de `assets/img/icones/` (sem `.svg`) que aparece no cabeçalho e nos cartões da ferramenta; sem ele, usa-se a do grupo.
- Português de Portugal com o Acordo Ortográfico; decimais com vírgula.
- Sem emojis. A cor nunca é o único sinal: escreve sempre o nível em texto.
- Não envies dados para a internet e não guardes dados que identifiquem doentes.
- Tem de funcionar em telemóvel (360 px) e imprimir bem.
- Cada limiar, dose ou recomendação tem de ter referência na bibliografia. Não inventes valores.

A ferramenta que quero: [descreve o problema da consulta, a escala ou o cálculo, e as fontes que queres usar].
```

Depois, confirma tu os valores clínicos com as fontes. A IA pode enganar-se.
