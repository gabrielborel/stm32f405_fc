# Flight Controller STM32F405 - instruções para o Claude Code

Placa de flight controller autoral (inspirada no layout do SpeedyBee F7 V3, não é clone). Firmware do zero, não Betaflight/INAV. Projeto KiCad 10, versionado no git. Fabricação e montagem SMD na JLCPCB.

## Etapa atual

Esquemático fechado (ERC 0 erros). Footprints e campo LCSC preenchidos. **Etapa: placement dos blocos da lista concluído** (ver "Blocos já posicionados"). Falta decidir as peças sem bloco e as decisões abertas. O Gabriel faz o roteamento depois, à mão. Não rotear, não criar trilhas, não mexer em zonas de cobre. Já existem trilhas e a zona `HSE_GND_POUR` (F.Cu) feitas por ele em volta do oscilador: não tocar.

## Como trabalhar

- Uma etapa por resposta (um bloco de circuito por vez), com a pergunta no fim. Respostas curtas: primeiro a ação ou conclusão, depois a fonte. Detalhe só quando ele pedir ("detalha").
- Toda regra ou valor cita documento + seção/figura/tabela. Se não vem de manual, escrever "prática de projeto" ou "inferência". Nunca atribuir a um documento algo que ele não diz.
- Riscos, divergências entre fontes e pendências sempre aparecem, mesmo em uma linha.
- O Gabriel quer aprender: explique o porquê das posições, não só as coordenadas. Ao estudar um manual, ele expõe o entendimento primeiro e a confirmação vem depois, com o texto real.
- Não usar travessão (—), só hífen simples. Não usar tags HTML. Textos que vão dentro do esquemático do KiCad ficam em inglês.
- Nunca inventar número (registrador, pino, corrente, capacitor). Sem certeza, dizer e localizar a seção.
- Commit só quando o Gabriel pedir, só com a PCB (ou só o arquivo pedido), sem linha de Co-Authored-By.

## Segurança do arquivo

1. Antes de qualquer edição, `git status` limpo ou commit feito. Cada bloco posicionado vira um commit.
2. Só editar o `.kicad_pcb` com o KiCad fechado. Editar com ele aberto arrisca sobrescrita ao salvar. Conferir com `pgrep -il kicad` e `ls ~*.lck`: fechar a janela não encerra o aplicativo (é preciso Cmd+Q).
3. Mostrar o diff e esperar aprovação antes de aplicar posições.
4. Depois de cada bloco: exportar imagem da placa e rodar o DRC, e relatar sobreposições de courtyard. A proposta é testada antes numa cópia (com o `.kicad_pro` ao lado); o DRC do projeto real deve dar o mesmo resultado da cópia.
5. Claude não tem noção espacial confiável: a revisão visual final é do Gabriel. Dizer isso quando for relevante.

## Ferramentas (confirmadas)

- macOS. O `kicad-cli` 10.0.6 fica em `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli` (não está no PATH).
- DRC: `kicad-cli pcb drc --output X --format json --units mm --severity-all ARQUIVO.kicad_pcb` (o `.kicad_pro` precisa estar ao lado para valerem as regras do projeto). Imagem: `kicad-cli pcb export svg --layers "F.Cu,F.Silkscreen,F.Courtyard,Edge.Cuts" --mode-single --page-size-mode 2 --exclude-drawing-sheet ARQUIVO.kicad_pcb`; a vista de baixo usa as camadas B e `--mirror`. Para PNG: `qlmanage -t -s 1800` (não há `rsvg-convert`).
- O `pcbnew` em Python funciona com o Python do app: `/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3` (`LoadBoard` e `Save`; virar para a face de baixo: `Flip(pos, False)`). O aviso `wxApp assert` é inofensivo. O `kiutils` não está instalado e não foi necessário.
- Cuidado: mover por script um footprint cujo pad toca uma trilha pode reatribuir as redes das trilhas ao salvar (aconteceu com o R1 numa cópia). Antes de gravar, comparar rede e geometria de todas as trilhas e vias, e abortar se mudar.
- Não há `pdftotext`: extrair texto de PDF com PDFKit via `swift`, e renderizar página em PNG para ler figuras. PDF só com imagem (HRO TYPE-C-31-M-12) precisa ser lido como imagem.
- Scripts de apoio em `tools/` (ver `tools/README.md`): pads e courtyards, mapa de ocupação, busca de posição livre, aplicação de posições com checagem de redes, comparação de DRC e leitura de PDF.
- Ainda não conferido na documentação oficial do KiCad: lista completa de flags do `kicad-cli` e a API de scripting do KiCad 10 (o que está acima foi testado, não lido).

## Estado da placa (decisões já tomadas)

- Contorno 45 x 45 mm, raio de canto 2 mm, 4 furos M3 (MountingHole_3.2mm_M3) em 30,5 x 30,5 mm. As ferragens do stack ainda não estão definidas. **Em reavaliação:** ver "Decisão em andamento: novo tamanho da placa".
- 4 camadas configuradas no KiCad (F.Cu, In1.Cu, In2.Cu, B.Cu). O stackup é o padrão do KiCad (1,6 mm, prepreg 0,1 mm, core 1,24 mm), não o da JLCPCB, e "Impedance controlled" está desligado. As zonas de GND (L2) e de alimentação (L3) ainda não existem. Montagem SMD em uma face só (componentes em cima).
- USB-C (J3, HRO TYPE-C-31-M-12) na borda da frente (embaixo no editor): X 131 mm, Y 110,31 mm, rotação 0. Com essa posição a frente do corpo (7,4 mm de profundidade, Fab de Y 106,61 a 114,01) passa 0,48 mm da borda (Y 113,525). O valor antigo Y 105,81 deste arquivo era de um contorno anterior e deixaria a frente cerca de 4 mm para dentro. O desenho da HRO (layout recomendado, p.1) põe a borda da PCB a 5,79 mm do topo dos pads, o que sugere um conector saindo cerca de 2,5 a 3 mm além da borda ([inferência]: desenho fora de escala, pad do footprint mais curto que o da HRO). Decisão aberta. Footprint padrão do KiCad. Solda das 4 pernas reforçada à mão no bring-up. O modelo 3D do J3 ainda não existe.
- Test points: pad SMD redondo de cerca de 1,0 mm, **na face de baixo** (TP1 a TP15 já estão em B.Cu). Pads de GPIO e de fio: em cima, na borda ou perto dela (J9 a J12 posicionados; o J13 não coube e continua estacionado fora da placa).
- Pads de GPIO: SPI2 (PB12 a PB15), UART4 (PA0/PA1), PA2, PA10, PA15, PB7, PC2, PC14/PC15 (estes dois são os primeiros a sair se faltar área). Pads S1 a S4 + GND dos motores, BZ+/BZ-, J1 da PDB (pads para soldar fio, fixo).
- Conectores JST GH de 4 pinos para ELRS (J5) e GPS (J6). SWD em J2 (1x6, DNP, hoje em pino vertical).
- Primeiro pedido: 5 placas montadas na JLCPCB. Um lado só.
- Divergência: a página "A fazer" do Notion ainda cita meta de 36 x 36 mm e teto de 50 x 50 mm. A decisão mais recente é 45 x 45 mm.

## Decisão em andamento: novo tamanho da placa

Conversa de 2026-11-01. As medidas finais ainda não foram decididas. Enquanto não forem, o contorno de 45 x 45 mm e os furos em 30,5 x 30,5 mm acima continuam valendo no arquivo. Atualizar este arquivo quando o tamanho for fechado.

- Motivo: a placa de 45 x 45 mm ficou apertada (botões SW1 e SW2 não cabem, J13 e J10 sem lugar, Q1 longe do J7, saídas do U1 congestionadas, resistores sob o U1).
- Referência: Pixhawk 6C Mini, 53,3 x 39 x 16,2 mm, e Pixhawk 6C, 84,8 x 44 x 12,4 mm (PX4 docs; a página da 6C Mini não diz se as medidas são da PCB ou da caixa, e o padrão de furos não está no texto, só no desenho de cotas em imagem). O Gabriel quer algo inspirado na 6C Mini e um pouco maior que ela.
- Fixação: pode fugir do padrão 30,5 x 30,5 mm, porque ele vai imprimir uma case 3D.
- **Etapa 1 fechada (2026-11-01):** contorno retangular com raio de canto de 2 mm (como hoje). Fixação A: 4 furos nos cantos, em retângulo, M2 com furo de 2,2 mm [prática de projeto, valor de folga comum], com inserto heat-set na case (a posição exata dos furos só depois do tamanho). Tamanho: sem medida fixa, teto de até +15% por lado sobre 53,3 x 39 mm (cerca de 61,3 x 44,9 mm) se as interfaces extras exigirem. Referência de ocupação (courtyards em caixa, é teto): peças dentro 1462 mm2 mais cerca de 153 mm2 das 12 peças ainda fora, total cerca de 1615 mm2; 80% de ocupação na placa atual (2029 mm2), 70% em +5% por lado (56 x 41), 64% em +10%, 59% em +15%. A faixa de 55 a 60% como confortável é [inferência]. A IMU (U5) longe dos furos e das bordas é [inferência] (BMI270 Seção 4.13, p.66). Footprint M2: conferir o nome exato na biblioteca MountingHole do KiCad.
- **Etapa 2 fechada (2026-11-01):** o U1 (LQFP64) não tem GPIO livre: todo I/O já é sinal ou pad (DS8626 Tabelas 7 e 9). Fica em 64 pinos (LQFP100 descartado). Escolhido: (a) 3 saídas auxiliares de timer em pads de borda: AUX1 = PA2 (TIM2_CH3 AF1, TIM5_CH3 AF2; DMA1 Stream 1 Canal 3 ou Stream 0 Canal 6), AUX2 = PB7 (TIM4_CH2 AF2; DMA1 Stream 3 Canal 2), AUX3 = PA10 (TIM1_CH3 AF1; DMA2 Stream 6 Canal 0 ou 6). DMA conforme RM0090 Rev 22, Tabelas 43 e 44 (p.309 e 310, lidas na imagem). PA15 continua pad de GPIO: TIM2_CH1 usa DMA1 Stream 5 Canal 3, o mesmo stream do MOTOR2 (TIM3_CH2, Canal 5). Para o AUX3, o firmware deve pôr o SDIO no DMA2 Stream 3 (o SDIO também aparece no Stream 6). Servo: alimentar pela PDB ou BEC, não pelas trilhas da FC [prática de projeto]. (b) PC2 como entrada de ADC (ADC123_IN12) para sensor de corrente: módulo agora, PDB própria no futuro. Deixar espaço para divisor e capacitor DNP [prática de projeto]; confirmar que a saída da PDB fique em 0 a 3,3 V (AN4073 para impedância da fonte). (c) J6 (GPS) passa de 4 para 6 pinos: +5V, GND, GPS_TX, GPS_RX, I2C1_SCL, I2C1_SDA, com a bússola no módulo do GPS. Não escolhidos: CAN2 (PB12/PB13, AF9, precisa de transceiver) e USART2 em PA2/PA3 (exigiria mover o IMU_INT1). Pendências: ainda não mexi no esquemático (ERC 0 será refeito); footprint JST GH de 6 pinos e campo LCSC não conferidos; limite de capacitância do I2C1 com cabo externo não conferido; PC14 e PC15 (sem AF digital, Tabela 9) seguem como primeiros a sair se faltar área.
- **Etapa 3, estratégia (2026-11-01):** reposicionar tudo, partindo limpo. Grupo rígido que não muda por dentro: U1 + bloco do HSE (Y1, C13, C14, R1, anel de guarda de GND com 27 segmentos de 0,5 mm em F.Cu, 15 vias de GND sobre o anel e a zona `HSE_GND_POUR`). Move-se em conjunto por translação e, se preciso, rotação de múltiplo de 90 graus (pcbnew em Python); a zona precisa ser reenchida depois (B no KiCad). As trilhas do oscilador (OSC_IN e a rede do C14) o Gabriel refaz. Existem 37 trilhas de 0,3 mm (GND, +3V3, VCAP_1, VCAP_2) e 4 vias fora do contorno, sobras de uma posição antiga do MCU; apagar só com o OK dele. Antes de editar a PCB: commitar CLAUDE.md e tools/ (git status limpo) e KiCad fechado.
- **Mapa de lados proposto (aprovado "no geral" pelo Gabriel, ainda ajustável):** oeste: microSD (J4) e USB-C (J3), com SW1 e SW2 perto do USB [inferência: se forem BOOT e reset]. Sul: PDB J1, LDOs U2 e U6 perto dela, pads de motor S1 a S4 + GND e buzzer. Leste: GPS J6 (6 pinos) e ELRS J5, e o BMP280 ventilado. Norte: AUX1 a AUX3, SWD J2, pads de expansão (SPI2, UART4) e LEDs. Centro: grupo U1 + HSE com a IMU perto do centro. Furos M2 nos 4 cantos. Risco: microSD a cerca de 16 mm do grupo do MCU no desenho (limite de 120 mm, AN4488 Seção 8.4.1); confirmar no placement. Orientação da placa no drone: ver o item seguinte.
- **Orientação decidida (2026-11-01):** frente da placa = borda leste do mapa de lados (lado do GPS J6 e do ELRS J5; USB e microSD ficam atrás, a oeste). Referencial do firmware: frente, esquerda, cima (X para a frente, Y para a esquerda, Z para cima), sem remapear os dados da IMU. Base: BMI270 Datasheet Rev 1.6, Seção 8.2 (p.144, figura e tabela de saídas): lendo a tabela, +X e +Y apontam para o canto do pino 1 e +Z sai pela face de cima [leitura de imagem, a conferir no teste de bancada]; pino 1 no canto superior esquerdo da vista de topo (Seção 7.4.5, p.142) e marcado por um ponto (Seção 8.4, p.146). Premissa [inferência]: os ícones da tabela têm a orientação da vista de topo do pino-out. Footprint `Bosch_LGA-14_3x2.5mm_P0.5mm` conferido: numeração anti-horária vista de cima, igual à do datasheet (sem espelhamento). Rotação do U5 para esta orientação: 270 graus (pino 1 no canto superior direito do encapsulamento, no editor). Hoje o U5 está a 90 graus (frente a oeste). Na tabela de rotações: frente oeste 90, norte 0, leste 270, sul 180 (rotação positiva do KiCad é anti-horária). O remapeamento do BMI270 vale só para as funções de interrupção, não para DATA_0 a DATA_13 nem FIFO (Seção 4.8.1). Teste de bancada: conferir os valores da tabela da Seção 8.2 antes de voar. Seta de frente no silk (F.Silkscreen), perto do centro, apontando para leste: a ser adicionada na PCB depois do placement, com aprovação, tamanho e posição não fixados.
- **Etapa 4 e ordem de trabalho (2026-11-01):** esquemático primeiro, depois a medida do contorno, depois a PCB. O Gabriel edita o esquemático no KiCad; eu só confiro o resultado com o ERC (`kicad-cli sch erc`). Lista de mudanças: (1) J6 em 6 pinos (`Connector_JST:JST_GH_SM06B-GHS-TB_1x06-1MP_P1.25mm_Horizontal`, existe na biblioteca do KiCad 10; LCSC provável C133065 = SM06B-GHS-TB(LF)(SN), fonte LCSC/Flux.ai, a conferir estoque e se é Extended); a ordem dos pinos 5 e 6 (I2C1_SCL, I2C1_SDA) e dos demais depende do módulo de GPS escolhido, ainda não conferida; (2) pads AUX só com sinal e GND (a corrente do servo vem da PDB ou do BEC, não passa pela FC) [prática de projeto]: novo conector 1x04 `Connector_FC:SolderPads_1x04_P2.54mm` com PA2, PB7, PA10 e GND, mantendo os nomes das nets do MCU e rotulando AUX1 a AUX3 no silk; (3) J12 reduzido: PA15, entrada de corrente e GND; PC2 vira entrada de ADC com resistor série de 0 ohm e filtro RC/divisor DNP, valores a definir com o AN4073 quando o sensor existir; (4) ERC em 0 erros. Pendências novas: alimentação do módulo de corrente (fora da FC, a definir); `MountingHole_2.2mm_M2` existe na biblioteca. Decisões abertas do CLAUDE.md que o redesenho resolve: 5, 7, 12; melhora parcial: 1, 2, 6, 10, 14; não resolve: 3, 4, 8 (R1 fica dentro do grupo rígido do HSE), 9, 11, 13; a 15 é refeita.
- Empilhar com a PDB: indefinido; não restringe o projeto por enquanto.
- Case 3D: fica para depois. `kicad-cli pcb render` e `pcb export step/stl/glb` existem na 10.0.6 (conferido no `--help`); a case seria código parametrizado (CadQuery ou OpenSCAD, nenhum instalado hoje). Precisa de altura máxima, espessura de parede e saídas dos conectores.
- Interfaces extras: bem-vindas se forem plausíveis no F405. Conferir pinos livres e alternate functions no DS8626 e conflitos com o que já está usado. Não inventar pino nem número.
- Orientação da placa e lados dos conectores: ainda não decididos; ficam para depois da etapa 2 (interfaces extras), de acordo com o Gabriel.
- A discutir, uma etapa por vez e conversando antes de propor: (1) tamanho, formato do contorno e fixação para a case; (2) interfaces extras; (3) crescer o contorno e reaproveitar os 8 blocos, ou reposicionar (os conectores da borda que crescer andam junto); (4) o que isso resolve das decisões abertas abaixo.
- Perguntar antes de fixar qualquer medida.

## Blocos já posicionados (um commit cada)

| Bloco | Commit | Resumo |
|---|---|---|
| 4 camadas, MCU, HSE, VDD | e1b2cef (wip), 4935abb | Oscilador e capacitores já movidos por ele. C6 espelhado sob os pinos 63 e 64. |
| Alimentação | 1448a49 | LDOs U2 e U6 embaixo à esquerda (22 mm do BMP280). VDDA (R34, C7, C8) junto dos pinos 12 e 13. Divisor de VBAT abaixo do cristal. |
| IMU | ae644af | U5 girado 90 graus (sem cruzamento nas linhas do SPI1, SCK com 4,4 mm). C20 e C21 nos pinos 5 e 8. |
| USB (apoio) | 7ae9b07 | U3 entre J3 e U1, R8 e R9 nas laterais, D4, R12, R10, R11 e C17 à direita do J3. |
| microSD | 4beb8ea | Pull-ups no corredor entre J4 e U1, C24 abaixo deles, C25 acima do J4, R15 perto do U6. |
| Motores e buzzer | fce4eec | R17, R24, R28 abaixo do U1, R25 e R26 acima. R30 a R33 ao lado de H3. Buzzer: Q1 e R29 à esquerda de H2. |
| Barômetro | 45743bf | C18 acima do U4, C19 abaixo, R13 e R14 a leste e ao norte. |
| Test points e pads | 8c7765d | TP1 a TP15 em B.Cu. J9 acima do J4, J11 ao lado, J12 na borda direita, J10 na borda esquerda. |

## Decisões abertas e pendências

1. J3 na borda: 0,48 mm hoje contra o que sugere o desenho da HRO. Ligação das abas do J3 ao GND (direto ou via RC).
2. J2: trocar para footprint horizontal ou aceitar o pino vertical (bate no stack).
3. VDD do cartão: C23 (1 uF) + C24 (10 uF) + C25 (0,1 uF) somam cerca de 11,1 uF, contra o máximo de 5 uF da Kingston SDCS2 (Tabela 6-6, p.13). Decisão de esquemático.
4. C18 e C19 como capacitores do U4, C20 e C21 como os do U5: atribuído por proximidade no esquemático, a confirmar. O C18 está a 3,1 mm do pino 6 (VDDIO) do U4, e a Fig. 17 do BMP280 mostra o capacitor nesse pino.
5. Q1 fica a 10,4 mm do J7 (H2 e o próprio J7 impedem algo mais perto). Alternativa: mover o J7 ao longo da borda.
6. J13 (PC14 e PC15) não coube: remover do esquemático ou achar lugar. J10 (UART4) ficou a 34 mm dos pinos 14 e 15 do U1.
7. Sem bloco no CLAUDE.md e ainda estacionadas fora da placa: SW1, SW2, LEDs D1 a D3 com R5 a R7, C15, R4 e R16.
8. R1: courtyard sobreposto com Y1 e C14 e 5 erros de clearance contra o guard ring. Depende do roteamento do anel (dele).
9. Zonas de GND (L2) e de alimentação (L3), ilha de GND do cristal (o AN2867 Seção 7.1 pede plano distinto, e a L2 seria GND sólido), stackup da JLCPCB (impedância de 90 ohm no USB e 50 ohm no SDIO).
10. Roteamento apertado: pinos 14 a 16 do U1 (o grupo VDDA bloqueia a saída para leste), SDIO D2, D3, CK e CMD pela fileira de baixo do U1 (R17 está sob os pinos 51 a 55), mesmo número de vias nos dados.
11. TP12 (SCK), TP14 e TP15 devem ser roteados passando pelo pad, sem ramal. TP12 acrescenta carga ao SCK (ES0182 Seção 2.12.4). As posições dos TPs provavelmente mudam depois do roteamento.
12. Firmware: eixos da IMU mudaram com o U5 em rot 90 (o remapeamento do BMI270 vale só para as funções de interrupção, não para os registradores de dados). OSPEEDR alto no SCK.
13. LDOs: sem orçamento de corrente. O AP2112 em SOT25 tem 184 C/W (DS39724, p.3).
14. BMP280: folga de 0,1 mm acima da tampa e ventilação dependem do stack. Confirmar com a JLCPCB que não usam solda por fase de vapor (BMP280 Seção 7.6).
15. DRC de referência no último commit: 214 violações (quase todas de silk) e 258 itens não conectados (esperado, sem roteamento). Limpar o silk por último.

## Regras de placement por bloco

Legenda da fonte: **[manual]** vem do documento citado. **[projeto]** é prática ou decisão do projeto. **[inferência]** é dedução, não está em manual.

### Geral
- Stackup de 4 camadas: top com sinais de alta velocidade + GND, L2 plano de GND, L3 plano de alimentação, bottom com sinais + GND. [manual] AN4488 Rev 7, Seção 8.1 e Figura 21 (a Seção 8.1 diz que 4 ou 6 camadas é o mínimo).
- Desacoplamento: cada par de alimentação com 100 nF e um capacitor de 4,7 µF a 10 µF em paralelo, o mais perto possível dos pinos, ou embaixo da placa. [manual] AN4488 Rev 7, Seção 8.3. Divergência: o texto da seção cita "Figure 22", mas o layout VDD/VSS está na Figura 23 do PDF (p.38). O AN4488 Seção 2.2 (Power supply schemes) esclarece: um capacitor de 4,7 a 10 µF para o encapsulamento mais 100 nF por pino VDD, VDDA com 100 nF + 1 µF e VBAT sem bateria ligado a VDD com 100 nF. O projeto segue a Seção 2.2 (um único C2 de 4,7 µF).
- Um capacitor de 100 nF por pino VDD do MCU (LQFP64: pinos 19, 32, 48, 64), colado no pino, caminho curto até o GND. Passivos de desacoplamento em 0402 ou 0603. [projeto] + AN4488 Seção 8.3.

### MCU e oscilador HSE
- Cristal o mais perto possível do MCU, trilhas curtas, guard ring de GND em volta, plano de GND local em outra camada ligado ao GND mais próximo do MCU. [manual] AN2867 Rev 24, Seção 7.1 e Figura 13. Sinais de alta frequência longe do oscilador (Seção 7.1, Figura 14).
- Não ligar o corpo do cristal ao GND do oscilador se ele for de encapsulamento metálico. [manual] AN2867, Seção 7.1.
- Test point de clock (PA8, MCO1) + GND: [projeto].
- Os 4 resistores de 220 ohm dos motores perto dos pinos do MCU (PB4, PB5, PB0, PB1). [projeto]

### Alimentação
- Dois AP2112K: um para MCU e sensores, outro para o microSD (+3V3_SD), por causa da térmica. Dar cobre ao redor deles e afastá-los da IMU. [projeto] / [inferência] (calor perto da IMU). Pendente: reavaliar o encapsulamento do LDO do cartão (SOT25 hoje).
- Filtro VDDA (R34 = 0 ohm, capacitores mantidos): posição perto dos pinos VDDA/VSSA. [projeto]. AN4488 Seção 2.2 pede 100 nF + 1 µF no VDDA (C8 e C7). O AN4073 Seção 2.2 só diz que o filtro reduz ruído, sem distância.
- Divisor de VBAT: C26 (100 nF) em paralelo com o resistor de baixo, perto do pino do ADC. [projeto]. O texto extraído do AN4073 não traz essa regra do C26.

### IMU BMI270 (SPI1)
- 100 nF nos pinos 5 (VDDIO) e 8 (VDD), colados no CI. [manual] BMI270 Datasheet Rev 1.6, Seção 7.2, p.136 (C20 e C21 no projeto).
- Trilha de SCK do SPI1 curta, só com a IMU e sem capacitor na linha (carga capacitiva alta no SCK atrasa o feedback e corrompe o último bit). [manual] ES0182 Rev 19, Seção 2.12.4 (Tabela 5 dá a frequência de APB permitida por OSPEEDR a 30 pF). Firmware: OSPEEDR high ou very high no SCK.
- IMU perto do centro da placa. [projeto]. Não achei no datasheet do BMI270 uma regra de posição. Afastar de LDOs, furos e bordas é [inferência] (o datasheet cita deriva de offset por estresse termomecânico na Seção 4.13, p.66, e dá 0,010 mg por µstrain de deformação da PCB na p.13).

### Barômetro BMP280 (U4, I2C)
- Folga de pelo menos 0,1 mm acima da tampa metálica, ventilação para a pressão ambiente, evitar luz forte, sem contato com líquidos. [manual] BMP280 Datasheet Rev 1.26, Seção 7.6, p.43 (e sem solda por fase de vapor). Fig. 17, p.37: 100 nF no VDD e no VDDIO.
- Ficar longe de fontes de calor (a temperatura medida depende da temperatura da PCB). [manual] BMP280 Datasheet, p.9, nota 3 (a temperatura medida depende da temperatura da PCB e do autoaquecimento) + [inferência] para a distância.

### microSD (SDIO, 4 bits)
- Sinais SDIO referenciados a plano de GND (ou PWR com 10 nF entre PWR e GND), impedância de 50 ohm +/-10%, trilha menor que 120 mm, descasamento entre dados e CK, e entre CK e CMD, menor que 10 mm, mesmo número de vias entre os sinais de dados, capacitância da trilha até 20 pF a 3,3 V. [manual] AN4488 Rev 7, Seção 8.4.1.
- Soquete J4 (Molex 104031-0811) perto da borda e do MCU, para encurtar o barramento. 100 nF o mais perto possível do VDD do soquete. Kingston SDCS2, Tabela 6-6, p.13 (conferida): C_HOST + C_BUS até 30 pF por linha e capacitância ligada à alimentação até 5 µF. O cartão sai pela borda oeste, como no desenho da Molex (corpo do J4 passa 3,2 mm da borda). [manual] + [projeto].
- Test points só em SDIO_CK e SDIO_CMD, como pads sobre a trilha, sem ramal. [projeto] (referência: AN4488 Seção 8.4.1).

### USB
- ESD (USBLC6-2SC6) o mais perto possível do receptáculo. [manual] AN4879 Rev 12, Seção 2.3 (Tabela 11).
- Par D+/D- curto e com impedância diferencial de 90 ohm. O valor está nas Pendências do Notion e depende do stackup da JLCPCB. O AN4879 Rev 12 não traz regra de roteamento nem de impedância do par. [projeto]
- Diodo Schottky do VBUS (B5819W SL) e resistor de sangria perto do conector. [projeto]
- Divisor de VBUS (33k e 82k, cerca de 3,57 V e 43 µA a 5 V, conta minha): dentro de < 4 V, > 0,7 x VDD e até 200 µA. [manual] AN4879 Rev 12, FAQ.
- Abas de fixação do conector: ligação ao GND ainda por definir (direto ou via RC).

### Motores (DShot, TIM3)
- Pads S1 a S4 + GND na borda, tamanho para solda de fio. R30 a R33 (pull-downs DNP de 10 kohm, 0603) em área acessível ao ferro de solda, no net do lado do pad. Marcar Exclude from BOM e Exclude from position files nos conectores de pads. [projeto]

### Buzzer
- Resistor de gate perto do PB6. MOSFET (AO3400A), diodo e resistor de descarga perto dos pads BZ+/BZ-. [projeto]

### Debug
- J2 (SWD 1x6, com SWO no pino 6): decidir se fica na lateral da placa (por exemplo a 90 graus) para não interferir no stack. Pendente. Hoje é pino vertical na borda de baixo; a alternativa é o footprint `PinHeader_1x06_P2.54mm_Horizontal`.

## Manuais de referência

Ficam em `docs/manuals/` (fora do git, listado no `.gitignore`). Abrir só o manual certo, não varrer a pasta. Tabelas extraídas de PDF podem sair com as colunas embaralhadas: conferir visualmente pinagem e tabelas de DMA.

| Arquivo | Para quê |
|---|---|
| DS8626 (STM32F405xx/407xx, Rev 12) | pinout, alternate functions, características elétricas, package |
| ES0182 (errata F405/407, Rev 19) | erratas por periférico |
| AN4488 (Rev 7) | hardware e layout do STM32F4: alimentação, stackup, SDIO |
| AN2867 (Rev 24) | oscilador: cristal, capacitores de carga, layout |
| AN4879 (Rev 12) | USB no STM32: ESD, VBUS, esquemas |
| AN4073 (Rev 5) | precisão do ADC |
| AN2606 (Rev 70) | boot do bootloader de sistema (DFU, USART3 em PB10/PB11) |
| BMI270 Datasheet (Rev 1.6) | IMU. É um PDF de verdade (150 páginas) |
| BMP280 Datasheet (Rev 1.26) | barômetro, montagem, I2C |
| SD Physical Layer Simplified Spec (Ver 9.10) | protocolo do cartão SD |
| DS39724 (AP2112, Rev 2-2) | LDO 3V3 |
| UM1724 (Nucleo-64 MB1136, Rev 17) | gravador SWD via NUCLEO (CN4) |
| USBLC6-2 (Rev 5), B5819W, AO3400A | ESD, Schottky, MOSFET |
| TYPE-C-31-M-12, Molex 104031-0811, JST GH | desenhos dos conectores |
| NCD0805R1, KT-0805G, KT-0805Y | LEDs |
| X32258MOB4SI (YXC), TS-1187A (XKB) | cristal, botão |
| Matek PDB-XT60 (manual) | PDB externa (5 V, 12 V, VBAT) |
| Betaflight DSHOT, DShot Missing Handbook, dshot_command.h, Digital_Cmd_Spec.txt | protocolo DShot |

O RM0090 (Rev 22) está na pasta, completo e por capítulo, junto com o PM0214. Arquivos listados acima que **não** estão na pasta: X32258MOB4SI (YXC), USBLC6-2, UM1724 e dshot_command.h. O desenho da TYPE-C-31-M-12 é só imagem.

## Como entregar um placement

Para cada bloco: (1) lista de designadores envolvidos, (2) regras aplicáveis com fonte, (3) tabela de ref, X, Y, rotação, face e justificativa em uma linha, (4) riscos e pendências, (5) pergunta de aprovação. Ordem sugerida: MCU e oscilador, desacoplamento VDD, alimentação (LDOs, VDDA), IMU, conectores e bordas (USB, J1, J5, J6, J2), microSD, motores e buzzer, barômetro, test points e pads (todos já feitos). Depois de aplicar: comparar redes das trilhas antes e depois, rodar o DRC no projeto real e conferir que bate com o da cópia.
