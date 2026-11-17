# Ferramentas de apoio ao placement

Scripts usados nas sessões com o Claude Code. Foram escritos e testados só neste projeto, com o KiCad 10.0.6 no macOS. Não são oficiais do KiCad.

PY = Python embutido no app do KiCad:

```
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
```

O aviso `wxApp assert` ao rodar é inofensivo.

| Script | O que faz | Grava? |
|---|---|---|
| `pcb_pads.py` | pads (número, rede, posição) de footprints | não |
| `pcb_courtyards.py` | retângulo do courtyard de footprints | não |
| `pcb_map.py` | mapa de ocupação em texto de uma região | não |
| `pcb_find_free_spot.py` | posição livre mais perto de um alvo, gera `moves.json` | não |
| `pcb_apply_moves.py` | aplica `moves.json` (move e vira para B.Cu) com checagem de redes | **sim** |
| `pcb_router.py` | roteador A* de duas camadas (módulo): lê pads, trilhas e vias da PCB e acha caminhos de 45 graus com via | **sim**, só em cópia |
| `pcb_route_nets.py` | linha de comando do roteador: `REDE REF1 PAD1 REF2 PAD2` | **sim**, só em cópia |
| `drc_compare.py` | compara dois DRC em JSON | não |
| `pdf_text.swift` | texto de PDF via PDFKit (`swift tools/pdf_text.swift A.pdf S.txt`) | não |
| `pdf_png.swift` | página de PDF em PNG (`swift tools/pdf_png.swift A.pdf 3 S.png`) | não |

## Fluxo usado em cada bloco
1. Copiar a PCB e o `.kicad_pro` (mais `fp-lib-table`, `sym-lib-table` e as bibliotecas locais) para uma pasta de rascunho.
2. Rodar `pcb_apply_moves.py` na **cópia**.
3. Rodar o DRC na cópia: `kicad-cli pcb drc --output X.json --format json --units mm --severity-all CÓPIA.kicad_pcb`.
4. Comparar com o DRC do projeto: `python3 -I tools/drc_compare.py DEPOIS.json ANTES.json`.
5. Só com o KiCad fechado (`pgrep -il kicad` vazio e sem `~*.lck`) e com aprovação, rodar `pcb_apply_moves.py` no projeto real e conferir que o DRC dá o mesmo resultado da cópia.

## Roteador (`pcb_router.py`)
Usado a partir de 2026-11-17 (PA8, VBUS_DET e PA10 foram achados por ele em cerca de 18 segundos). Lê as folgas reais da PCB (pad pela caixa que o envolve, trilha, via, zona `HSE_GND_POUR`, borda a 0,62 mm para trilha e 0,82 mm para via, de acordo com `min_copper_edge_clearance` de 0,5 mm), grade de 0,05 mm, folga de 0,2 mm, trilha de 0,2 mm. Ignora as larguras de classe (SDIO, USB, Power) e o `.kicad_dru`, e é guloso: a ordem das redes importa (as mais difíceis primeiro). Sempre numa cópia; depois reencher `GND_L2` e `3V3_L3`, rodar o DRC e só então aplicar no arquivo real.

## Cuidados
- `pcb_apply_moves.py` aborta se qualquer trilha ou via mudar de rede ou geometria. Mesmo assim, não mova por script um footprint cujo pad toca uma trilha.
- Antes de gravar no projeto real, o `git status` deve estar limpo ou ter um commit.
