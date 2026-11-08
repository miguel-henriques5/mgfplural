# MGF no Plural

**Ferramentas clínicas feitas por quem as usa.**

Site nacional de recursos para Médicos de Família: escalas, guias de prescrição, interpretação de exames, programas de saúde e modelos, feitos em comunidade. É gratuito, aberto e não recolhe dados.

- Site: https://miguel-henriques5.github.io/mgfplural/
- Contacto: Miguel Cachinho Henriques, Médico de Família na USF Conde da Lousã, ULS Amadora-Sintra · mgfplural@gmail.com

## Usar

- **No browser:** abre o site e escolhe a ferramenta.
- **Uma ferramenta offline:** em cada ferramenta, carrega em "Descarregar HTML". O ficheiro funciona sozinho, sem internet.
- **O site inteiro offline:** descarrega o [ZIP do repositório](https://github.com/miguel-henriques5/mgfplural/archive/refs/heads/main.zip), descomprime e abre `index.html`.

## Contribuir

Não precisas de saber programar nem de usar o GitHub. Lê o [CONTRIBUIR.md](CONTRIBUIR.md) e envia a tua ferramenta ou o teu feedback por email.

## Como está organizado

| Pasta | O que tem |
| --- | --- |
| `fonte/ferramentas/` | As ferramentas, uma por ficheiro. **É aqui que se edita.** |
| `fonte/estrutura.json` | Áreas e grupos do site (nomes, ícones, ordem). |
| `fonte/modelo/` | O modelo de ferramenta para colegas. |
| `assets/` | Cores, letras, ícones e o JavaScript do site. |
| `scripts/construir.py` | Gera o site a partir de `fonte/`. |
| `index.html`, `acerca.html`, `ferramentas/`, `descarregar/`, `modelos/` | **Gerados.** Não editar à mão. |

Para gerar o site depois de alterar uma ferramenta: `python3 scripts/construir.py` (só precisa de Python 3).

## Princípios

- Cada ferramenta é um ficheiro HTML autónomo, sem nada carregado da internet.
- O que o utilizador escreve fica no seu computador. As ferramentas não conseguem enviar dados (Content-Security-Policy com `connect-src 'none'`).
- Cada ferramenta mostra quem a criou, a versão, a data de revisão e a bibliografia.
- Funciona em Edge, Chrome e Firefox dos últimos cinco anos, em computador e telemóvel, e imprime bem.

## Licença

[MIT](LICENSE). Podes usar, adaptar e partilhar, mantendo o nome de quem criou. Escalas e imagens de terceiros mantêm os direitos dos seus autores.

As ferramentas apoiam, não substituem, o juízo clínico.
