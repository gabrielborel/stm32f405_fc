# Handoff do projeto (2026-11-17)

Resumo para retomar o trabalho em outro computador, sem o histórico das conversas com o Claude Code. Os registros completos continuam onde sempre estiveram:

| Arquivo | O que tem |
|---|---|
| `CLAUDE.md` | decisões de projeto, regras de placement com fonte, decisões abertas, histórico do placement |
| `docs/ROTEAMENTO.md` | guia geral do roteamento (camadas, net classes, checklist por bloco) |
| `docs/ROTEAMENTO_DETALHADO.md` | passo a passo pino a pino, com coordenadas de tudo que já foi roteado e os pontos abertos |
| `tools/README.md` | scripts de apoio (escritos no macOS, não rodados no Linux) |
| `case/` | rascunho da case em CadQuery (`case.py`) e render (`render.py`); saídas em `case/out/` (fora do git) |

Atenção: a seção "Etapa atual" do `CLAUDE.md` ainda diz "não rotear". Isso ficou velho: desde 2026-11-02 o roteamento é feito em conjunto (o Claude planeja, testa numa cópia e aplica). Este arquivo vale para o estado atual.

## 1. Onde o projeto está

- Esquemático fechado, ERC 0 erros. Mudança recente: J13 removido, PC14 e PC15 sem ligação (`894256c`, `c621dd6`).
- PCB 58 x 44 mm, 4 camadas (JLC04161H-3313), placement aprovado, roteamento em andamento.
- DRC em 2026-11-17 (cópia do HEAD, `--severity-error --severity-warning`): **6 violações, todas antigas**: 2 `courtyards_overlap` e 2 `clearance` do R1 no anel do HSE (decisão 8) e 2 `silk_edge_clearance` do J3 (o conector cruza a borda de propósito). **119 itens não conectados** (eram 249 antes do roteamento). Depois do SDIO sul (`c63db33`) e de D0 e D1 (`2666c02`), 2026-11-17: mesmas 6 violações e **111 não conectados**; com o par USB (U3 ao U1): **109**; com D+ e D- do J3 ao U3: **105**; com o VBUS_RAW: **99**; com CC1 e CC2: **97**; com o GND do USB: **89**; com os pull-ups R21 a R23 na B.Cu: **83** (e 2 avisos de silk do TP13 e do R22); com os ramais do D0 e do D1: **81**; com o +3V3_SD do cartão: **75**; sem o SD_CD e o SD_EN (e o EN do U6 ao +5V): **69**. Firmware: sem SD_EN nem SD_CD (o cartão liga junto com o +5V e é detectado tentando inicializar). Com o PA8, o VBUS_DET e o PA10: **65**. Com SWCLK, SWDIO e NRST: **62** (8 violações no total, as mesmas). Com SPI2 (3 linhas), PA2 e os AUX_OUT: **55** (8 violações, as mesmas). Com os catodos dos LEDs e o CURR_IN: **51** (as mesmas 8). Com as 28 vias de GND: **23** (as mesmas 8). Com +5V, BZ_NEG e o +3V3 do J9: **6** (as mesmas 8).

### Já roteado (cada bloco é um commit, detalhes no `ROTEAMENTO_DETALHADO.md`)

| Bloco | Commits |
|---|---|
| Oscilador HSE e primeiros desacoplamentos | `7729a6c` |
| Desacoplamento do U1 (VDD, VCAP, C2) e padrão de vias | `da8c2d1`, `129a801` |
| Filtro do VDDA | `5d3974d` |
| Desacoplamento do U5, U4 e dos LDOs | `2c4ea27`, `161505b`, `48f4ddf` |
| SPI1 até a IMU (45 graus) | `c14c4f9`, `dd3ddef` |
| Lado norte do U1 (BOOT1, LEDs verde e amarelo, ELRS, MOTOR3/4) | `9d636b1`, `6ec3613` |
| M3_OUT e M4_OUT até o J8 | `631b066` |
| Sul: motores 1 e 2, BUZZER, gate do Q1 | `ecb5421`, `9e61881` |
| Leste: UART4, LED_RED, NRST até C15 e SW1 | `573d1d8`, `b1fb9cb` |
| Canto sudeste: VBAT_SENSE, PC2, PA15, BOOT0, I2C (U4, J6, R13, R14), +VBAT | `91912c6` |
| SDIO sul (D2, D3, CK, CMD) até o J4, com saltos de D2 e D3 pela L4; TP14 e TP15 movidos | `c63db33` |
| SDIO D0 e D1 até o J4: serpentinas (31 mm cada) e saltos de 2 vias | `2666c02` |
| Par USB D+/D- do U3 ao U1 em L4; D0 refeito para abrir o corredor | `e16cf6b` |
| USB D+ e D- do J3 ao U3: face oeste dos pads e uma via L4 no D- | `e0ed237` |
| VBUS_RAW (J3 norte e sul, U3.5, C17, R12, R10, D4); vias do par USB descidas 0,1 mm | `dadfcc3` |
| CC1 e CC2 do J3 até R8.1 e R9.1, por L4 | `7d97a6f` |
| GND do lado do USB (J3, abas SH, U3.2, R8, R9, R11, R12, C17): 12 vias | `72a53e2` |
| Pull-ups R21, R22 e R23 na B.Cu (solda manual), stubs curtos e +3V3_SD em B.Cu | `88b7148` |
| Ramais dos pull-ups do D0 (R20) e do D1 (R19) em L1 | `cbf9df2` (o do D0 foi refeito em `6072787`) |
| +3V3_SD do cartão (J4.4, TP13, C24, C25, R19, R20) e ramal do D0 refeito | `6072787` |
| SD_CD e SD_EN removidos (esquemático e PCB, R15 e R18 fora); EN do U6 ao +5V | esquemático `2397ca6`, PCB `a0c2172` |
| PA8 (TP1), VBUS_DET (R10 e R11) e PA10 (R37) por busca A* pelo miolo do U1 | `a6385ea` |
| SWCLK, SWDIO e NRST até o J2 (A*, J2 no norte; DRC 8 violações, 62 não conectados) | `ad19fcb` |
| SPI2 NSS, SCK e MISO até o J9; PA2 até o R35; AUX1 a AUX3 dos resistores R35 a R37 ao J14 (A*; DRC 8 violações, 55 não conectados) | `3e4b1ad` |
| Catodos dos LEDs D1 a D3 (aos R7, R6 e R5) e CURR_IN (R38.2 ao J12.3) (A*; DRC 8 violações, 51 não conectados) | `5fc2e77` |
| 28 pads de GND ligados ao plano L2 por trilha curta e via (`tools/pcb_gnd_vias.py`; DRC 8 violações, 23 não conectados) | `bf13d55` |
| +5V (13 ligações), BZ_NEG (3) e o +3V3 do J9.2 (`tools/pcb_connect_islands.py` e `pcb_gnd_vias.py`, trilha de 0,5 mm; DRC 8 violações, 6 não conectados) | `37e0335` |

### O que falta (lista do DRC de 2026-11-17)

- **Oeste do U1:** os seis sinais do SDIO e os cinco pull-ups estão roteados (R21 a R23 na B.Cu, solda manual; **no esquemático marcar R21 a R23 como Exclude from BOM e Exclude from position files**); o cartão está completo (o SD_CD e o SD_EN foram removidos de propósito, ver "Decisão: SD_CD e SD_EN removidos" no `ROTEAMENTO_DETALHADO.md`); o PA8, o VBUS_DET e o PA10 já estão roteados (A* pelo miolo do U1); o USB está completo (D+, D-, VBUS_RAW, CC1, CC2 e GND) (par de 90 ohm, VBUS_RAW, CC1/CC2, VBUS_DET), SD_CD, SD_EN, PA8 (TP1).
- **Norte:** SWO até o J2.6 (sem caminho pelo roteador, ver abaixo); **SPI2_MOSI** (pino 36 ao J9.6) e **PB7** (pino 59 ao R36.1, AUX2) sem caminho pelo roteador: em 6 ordens o SPI2 nunca passou de 3 das 4 linhas (MOSI fecha só perdendo o MISO e o NSS), e o PB7 não fechou em nenhuma, nem com o R36 movido para o sul (PB7 ao R36 fecha com 17,1 mm, mas o R36 ao J14 não passa do sul para o norte). Feitos em `3e4b1ad`: SPI2 NSS, SCK e MISO (o MISO tem 55,6 mm e 4 vias), PA2 ao R35 e AUX1 a AUX3 ao J14. Os catodos dos LEDs e o CURR_IN estão feitos (cada catodo usa 2 vias por B.Cu num trecho de 4 a 5 mm; pode ser refeito à mão em L1).
- **GPS_TX e GPS_RX** (pinos 37 e 38, oeste) até o J6 (leste) e **SWO** (pino 55): **sem caminho pelo roteador A\***. Estudo de 2026-11-17, tudo em cópia (a PCB real não foi tocada): (1) mover o J2 para o sul não cabe (só há 13,8 mm livres, o J2 precisa de 16,3; a busca de posição livre só acha a posição atual no norte), e forçando ali SWO, NRST e GPS continuam sem caminho; (2) trilha e folga de 0,15 mm não destravam o GPS e violam regras do projeto (vias de 0,55 / 0,25 mm dão `drill_out_of_range` e `via_diameter`; classe Power pede 0,2 mm); (3) apagando o PA10 e rodando 6 ordens: o GPS fecha com no máximo um fio do SWD, nunca com SWDIO e SWCLK juntos; apagando também o VBUS_DET, o GPS (38,5 mm e 60,1 mm, L1) fecha e derruba o SWD inteiro; (4) SWD sozinho com o PA10 mantido: SWCLK, SWDIO e NRST fecham, o SWO não (com o PA10 apagado o SWO fecha, 59,6 mm). Mover o J6 para o noroeste não foi avaliado (a busca de posição livre só põe peças no interior) e traria o I2C1 (pinos 61 e 62, sul) para o lado errado. O roteador não empurra trilhas: à mão, com push and shove no KiCad, pode passar. **Alternativa sem roteamento [inferência, a conferir no firmware]:** ligar o GPS UART pelo J10 (GND, +5V, UART4_TX, UART4_RX, já roteados), deixando o J6 só com a alimentação e o I2C da bússola.
- **Alimentação por trilha:** feita (`37e0335`). Observação: o roteador liga ilhas pelo par de pads mais perto, então o +5V tem trechos longos em B.Cu (um de 57 mm do D4.1 ao J10.2, outros de 16 a 26 mm); passa no DRC, mas um barramento ou um preenchimento de cobre seria mais limpo.
- **GND:** só o **J4.6** (pino VSS do microSD, na borda oeste, entre os pads de CLK e DAT0) ficou sem ligação ao plano: o gerador não achou lugar para a via nem com 12 mm de alcance. Ligar à mão (via entre os pads ou trilha até um pad de blindagem).
- **Fechamento:** preenchimento de GND em L1 e L4 com costura, cobre em volta do U2 e do U6 (decisão 13), revisão dos TPs e das referências do silk.

Sugestão de ordem: lado oeste (SDIO e USB primeiro, são os mais restritos), depois o norte, depois GPS, depois alimentação e GND.

### Pontos abertos registrados

- SPI1 com folgas de 0,15 mm em alguns pontos (passa no DRC; `ROTEAMENTO_DETALHADO.md`, ponto aberto 8).
- Canto sudeste com folgas de 0,17 a 0,2 mm e uma fenda de cerca de 3,7 mm na L2 sob o U1 (vias de BOOT0, SCL, SDA e dos pinos 1 e 64). Só sinais lentos por cima [inferência].
- Decisão 8 (R1 e o anel do HSE): marcada como feita no `ROTEAMENTO.md`, mas o DRC ainda acusa os 4 erros do R1. Conferir.
- Firmware e fabricação: ver `ROTEAMENTO.md` seção 7.

## 2. Como trabalhamos (combinados com o Claude)

Estas preferências estavam na memória local do Claude Code, que não vai junto para o outro computador:

1. **Fluxo de cada bloco:** o Claude planeja e mostra; testa numa cópia da PCB no scratchpad (reencher só `GND_L2` e `3V3_L3`, DRC, comparar com a referência, medir folgas); só aplica no arquivo real com o KiCad fechado; o resultado real tem que bater com o da cópia.
2. **Validar antes de passar ao próximo bloco:** conferir distância via-pad, larguras, degraus de mouse, e padronizar. Padrão de via (centro a centro do pad): 0402 0,82 mm, 0603 1,12 mm, 0805 1,35 mm; via para dentro do U1 1,27 mm do centro do pino.
3. **Cantos de 45 graus**, nunca 90. Folga de 0,25 mm ou mais quando couber (o DRC aceita 0,15).
4. **Commitar cada passo validado sem perguntar**, PCB e docs em commits separados, sem o ruído do `.kicad_prl` e do `.kicad_pro`, **sem linha de Co-Authored-By**.
5. Uma etapa por resposta, pergunta no fim, fonte em toda regra ou valor (documento e seção, ou [prática de projeto], [inferência], [conta]). Sem travessão. Respostas em português.
6. Esquemático: o Gabriel edita, o Claude só roda o ERC. Revisão visual final é sempre do Gabriel.

## 3. Ambiente e armadilhas

- **KiCad 10.0.7 no Fedora:** `kicad-cli` no PATH e `pcbnew` importável pelo `python3` do sistema. Em outro sistema, ver os caminhos no `CLAUDE.md` (seção Ferramentas).
- **Nunca editar o `.kicad_pcb` com o KiCad aberto.** Conferir `pgrep -il kicad`; um `~*.lck` sobrando sem processo é inofensivo.
- **Cópia para DRC:** copiar `.kicad_pcb`, `.kicad_pro`, `.kicad_dru`, `fp-lib-table`, `sym-lib-table`, `Connector_FC.pretty` e `lib/`. Sem as bibliotecas aparecem `footprint_link_issues` falsos.
- **Zonas:** reencher só `GND_L2` e `3V3_L3` por `pcbnew.ZONE_FILLER`. **Não reencher a `HSE_GND_POUR`** (por isso não usar `kicad-cli pcb drc --refill-zones`). Sem reencher, aparecem `clearance` falsos de plano desatualizado. No KiCad, depois de adicionar vias, apertar `B`.
- **DRC:** `kicad-cli pcb drc --output X.json --format json --units mm --severity-error --severity-warning ARQUIVO.kicad_pcb`. O `kicad-cli` regrava o `.kicad_pro` (`td_enabled`, `net_colors`): descartar com `git checkout`. A checagem de paridade dá cerca de 98 `extra_footprint` falsos neste Linux (também no HEAD): ignorar.
- **Scripts em pcbnew:** apagar com `b.Delete`, não `b.Remove` em loop (segfault). Mover footprint cujo pad toca trilha pode trocar a rede da trilha ao salvar: comparar redes antes de gravar. Comparar arquivo real e cópia depois de normalizar os UUIDs.
- **`pcbnew` salvando com outro nome:** `LoadBoard(a)` e `Save(b)` em outra pasta ou nome grava o `.kicad_pro` da pasta com regras padrão (perde net classes, clearance 0,2). O DRC então dá dezenas de erros falsos. Recopiar o `.kicad_pro` do repositório antes do DRC, e no arquivo real descartar a mudança com `git checkout -- STM32F405_FLIGHT_CONTROLLER.kicad_pro`.
- **Restaurar backup do KiCad:** em 2026-11-02 o "restore backup" trocou o `.kicad_pro` por uma versão velha (perdeu net classes e exclusões). Se o KiCad oferecer, recusar e conferir o `git diff` do `.kicad_pro`.
- Os scripts do roteamento (por bloco) ficaram no scratchpad da sessão, fora do repositório; as coordenadas finais estão no `ROTEAMENTO_DETALHADO.md` e no próprio `.kicad_pcb`.
- `docs/manuals/` está fora do git: copiar os PDFs à mão para o outro computador.

## 4. Para começar no outro computador

1. `git pull`, abrir o projeto no KiCad, apertar `B` e rodar o DRC: deve dar as mesmas 6 violações e 119 não conectados.
2. Copiar `docs/manuals/`.
3. Para a case: `pip install cadquery` (e `vtk` para o render), depois `python3 case/case.py`.
4. Pedir ao Claude para ler este arquivo e o `ROTEAMENTO_DETALHADO.md` antes do próximo bloco.
