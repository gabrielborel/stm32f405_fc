# Flight Controller STM32F405 - instruções para o Claude Code

Placa de flight controller autoral (inspirada no layout do SpeedyBee F7 V3, não é clone). Firmware do zero, não Betaflight/INAV. Projeto KiCad 10, versionado no git. Fabricação e montagem SMD na JLCPCB.

## Etapa atual

Esquemático fechado (ERC 0 erros). Footprints e campo LCSC preenchidos. **Etapa: placement.** O Gabriel faz o roteamento depois, à mão. Não rotear, não criar trilhas, não mexer em zonas de cobre.

## Como trabalhar

- Uma etapa por resposta (um bloco de circuito por vez), com a pergunta no fim. Respostas curtas: primeiro a ação ou conclusão, depois a fonte. Detalhe só quando ele pedir ("detalha").
- Toda regra ou valor cita documento + seção/figura/tabela. Se não vem de manual, escrever "prática de projeto" ou "inferência". Nunca atribuir a um documento algo que ele não diz.
- Riscos, divergências entre fontes e pendências sempre aparecem, mesmo em uma linha.
- O Gabriel quer aprender: explique o porquê das posições, não só as coordenadas. Ao estudar um manual, ele expõe o entendimento primeiro e a confirmação vem depois, com o texto real.
- Não usar travessão (—), só hífen simples. Não usar tags HTML. Textos que vão dentro do esquemático do KiCad ficam em inglês.
- Nunca inventar número (registrador, pino, corrente, capacitor). Sem certeza, dizer e localizar a seção.

## Segurança do arquivo

1. Antes de qualquer edição, `git status` limpo ou commit feito. Cada bloco posicionado vira um commit.
2. Só editar o `.kicad_pcb` com o KiCad fechado. Editar com ele aberto arrisca sobrescrita ao salvar.
3. Mostrar o diff e esperar aprovação antes de aplicar posições.
4. Depois de cada bloco: exportar imagem da placa e rodar o DRC, e relatar sobreposições de courtyard.
5. Claude não tem noção espacial confiável: a revisão visual final é do Gabriel. Dizer isso quando for relevante.

## Ferramentas (confirmar na primeira sessão)

- macOS. O `kicad-cli` normalmente fica em `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli` (caminho não confirmado). Testar com `--version`.
- O `pcbnew` em Python costuma importar só com o Python embutido no app do KiCad. Plano B: editar o `.kicad_pcb` como texto com `kiutils`. Não verifiquei se o `kiutils` lê o formato do KiCad 10: testar leitura antes de qualquer escrita.
- Pontos a confirmar na documentação oficial do KiCad (não vêm dos manuais do projeto): flags do `kicad-cli`, API de scripting do KiCad 10.

## Estado da placa (decisões já tomadas)

- Contorno 45 x 45 mm, raio de canto 2 mm, 4 furos M3 (MountingHole_3.2mm_M3) em 30,5 x 30,5 mm. As ferragens do stack ainda não estão definidas.
- 4 camadas. Montagem SMD em uma face só (componentes em cima). O stackup da JLCPCB ainda não foi fechado.
- USB-C (J3, HRO TYPE-C-31-M-12) na borda da frente (embaixo no editor): X 131 mm, Y 105,81 mm, rotação 0. Footprint padrão do KiCad, que difere cerca de 0,4 mm do desenho do HRO (decisão registrada). Solda das 4 pernas reforçada à mão no bring-up. O modelo 3D do J3 ainda não existe.
- Test points: pad SMD redondo de cerca de 1,0 mm, **na face de baixo**. Pads de GPIO e de fio: em cima, na borda.
- Pads de GPIO: SPI2 (PB12 a PB15), UART4 (PA0/PA1), PA2, PA10, PA15, PB7, PC2, PC14/PC15 (estes dois são os primeiros a sair se faltar área). Pads S1 a S4 + GND dos motores, BZ+/BZ-, J1 da PDB (pads para soldar fio, fixo).
- Conectores JST GH de 4 pinos para ELRS (J5) e GPS (J6). SWD em J2 (1x6, DNP).
- Primeiro pedido: 5 placas montadas na JLCPCB. Um lado só.
- Divergência: a página "A fazer" do Notion ainda cita meta de 36 x 36 mm e teto de 50 x 50 mm. A decisão mais recente é 45 x 45 mm.

## Regras de placement por bloco

Legenda da fonte: **[manual]** vem do documento citado. **[projeto]** é prática ou decisão do projeto. **[inferência]** é dedução, não está em manual.

### Geral
- Stackup de 4 camadas: top com sinais de alta velocidade + GND, L2 plano de GND, L3 plano de alimentação, bottom com sinais + GND. [manual] AN4488 Rev 7, Seção 8.1 e Figura 21 (a Seção 8.1 diz que 4 ou 6 camadas é o mínimo).
- Desacoplamento: cada par de alimentação com 100 nF e um capacitor de 4,7 µF a 10 µF em paralelo, o mais perto possível dos pinos, ou embaixo da placa. [manual] AN4488 Rev 7, Seção 8.3. Divergência: o texto da seção cita "Figure 22", mas o layout VDD/VSS está na Figura 23 do PDF.
- Um capacitor de 100 nF por pino VDD do MCU (LQFP64: pinos 19, 32, 48, 64), colado no pino, caminho curto até o GND. Passivos de desacoplamento em 0402 ou 0603. [projeto] + AN4488 Seção 8.3.

### MCU e oscilador HSE
- Cristal o mais perto possível do MCU, trilhas curtas, guard ring de GND em volta, plano de GND local em outra camada ligado ao GND mais próximo do MCU. [manual] AN2867 Rev 24, Seção 7.1 e Figura 13. Sinais de alta frequência longe do oscilador (Seção 7.1, Figura 14).
- Não ligar o corpo do cristal ao GND do oscilador se ele for de encapsulamento metálico. [manual] AN2867, Seção 7.1.
- Test point de clock (PA8, MCO1) + GND: [projeto].
- Os 4 resistores de 220 ohm dos motores perto dos pinos do MCU (PB4, PB5, PB0, PB1). [projeto]

### Alimentação
- Dois AP2112K: um para MCU e sensores, outro para o microSD (+3V3_SD), por causa da térmica. Dar cobre ao redor deles e afastá-los da IMU. [projeto] / [inferência] (calor perto da IMU). Pendente: reavaliar o encapsulamento do LDO do cartão (SOT25 hoje).
- Filtro VDDA (R34 = 0 ohm, capacitores mantidos): posição perto dos pinos VDDA/VSSA. [projeto]. A regra de posição não foi conferida nos manuais.
- Divisor de VBAT: C26 (100 nF) em paralelo com o resistor de baixo, perto do pino do ADC. [projeto] (origem do C26: AN4073).

### IMU BMI270 (SPI1)
- 100 nF nos pinos 5 (VDDIO) e 8 (VDD), colados no CI. [manual] BMI270 Datasheet Rev 1.6, Seção 7.2.
- Trilha de SCK do SPI1 curta, só com a IMU e sem capacitor na linha (carga capacitiva alta no SCK atrasa o feedback e corrompe o último bit). [manual] ES0182 Rev 19, Seção 2.12.4 (Tabela 5 dá a frequência de APB permitida por OSPEEDR a 30 pF). Firmware: OSPEEDR high ou very high no SCK.
- IMU perto do centro da placa. [projeto]. Não achei no datasheet do BMI270 uma regra de posição. Afastar de LDOs, furos e bordas é [inferência] (o datasheet cita deriva de offset por estresse termomecânico, Seção da compensação IOC).

### Barômetro BMP280 (U4, I2C)
- Folga de pelo menos 0,1 mm acima da tampa metálica, ventilação para a pressão ambiente, evitar luz forte, sem contato com líquidos. [manual] BMP280 Datasheet Rev 1.26, Seção 7.6.
- Ficar longe de fontes de calor (a temperatura medida depende da temperatura da PCB). [manual] BMP280 Datasheet (descrição da temperatura medida) + [inferência] para a distância.

### microSD (SDIO, 4 bits)
- Sinais SDIO referenciados a plano de GND (ou PWR com 10 nF entre PWR e GND), impedância de 50 ohm +/-10%, trilha menor que 120 mm, descasamento entre dados e CK, e entre CK e CMD, menor que 10 mm, mesmo número de vias entre os sinais de dados, capacitância da trilha até 20 pF a 3,3 V. [manual] AN4488 Rev 7, Seção 8.4.1.
- Soquete J4 (Molex 104031-0811) perto da borda e do MCU, para encurtar o barramento. 100 nF o mais perto possível do VDD do soquete. Limite C_HOST + C_BUS de 30 pF (Kingston SDCS2, Table 6-6). [projeto] vindo das Pendências do Notion, não conferido neste projeto (o documento da Kingston não está na pasta de manuais).
- Test points só em SDIO_CK e SDIO_CMD, como pads sobre a trilha, sem ramal. [projeto] (referência: AN4488 Seção 8.4.1).

### USB
- ESD (USBLC6-2SC6) o mais perto possível do receptáculo. [manual] AN4879 Rev 12, Seção 2.3 (Tabela 11).
- Par D+/D- curto e com impedância diferencial de 90 ohm. O valor está nas Pendências do Notion e depende do stackup da JLCPCB. O AN4879 Rev 12 não traz regra de roteamento nem de impedância do par. [projeto]
- Diodo Schottky do VBUS (B5819W SL) e resistor de sangria perto do conector. [projeto]
- Abas de fixação do conector: ligação ao GND ainda por definir (direto ou via RC).

### Motores (DShot, TIM3)
- Pads S1 a S4 + GND na borda, tamanho para solda de fio. R30 a R33 (pull-downs DNP de 10 kohm, 0603) em área acessível ao ferro de solda, no net do lado do pad. Marcar Exclude from BOM e Exclude from position files nos conectores de pads. [projeto]

### Buzzer
- Resistor de gate perto do PB6. MOSFET (AO3400A), diodo e resistor de descarga perto dos pads BZ+/BZ-. [projeto]

### Debug
- J2 (SWD 1x6, com SWO no pino 6): decidir se fica na lateral da placa (por exemplo a 90 graus) para não interferir no stack. Pendente.

## Manuais de referência

Ficam em `docs/manuais/` (fora do git, listado no `.gitignore`). Abrir só o manual certo, não varrer a pasta. Tabelas extraídas de PDF podem sair com as colunas embaralhadas: conferir visualmente pinagem e tabelas de DMA.

| Arquivo | Para quê |
|---|---|
| DS8626 (STM32F405xx/407xx, Rev 12) | pinout, alternate functions, características elétricas, package |
| ES0182 (errata F405/407, Rev 19) | erratas por periférico |
| AN4488 (Rev 7) | hardware e layout do STM32F4: alimentação, stackup, SDIO |
| AN2867 (Rev 24) | oscilador: cristal, capacitores de carga, layout |
| AN4879 (Rev 12) | USB no STM32: ESD, VBUS, esquemas |
| AN4073 (Rev 5) | precisão do ADC |
| AN2606 (Rev 70) | boot do bootloader de sistema (DFU, USART3 em PB10/PB11) |
| BMI270 Datasheet (Rev 1.6) | IMU. O arquivo `.pdf` na pasta é texto puro, não um PDF de verdade |
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

O RM0090 não está nesta pasta: ele fica fatiado por capítulo no Drive. Pedir ao Gabriel o capítulo necessário.

## Como entregar um placement

Para cada bloco: (1) lista de designadores envolvidos, (2) regras aplicáveis com fonte, (3) tabela de ref, X, Y, rotação, face e justificativa em uma linha, (4) riscos e pendências, (5) pergunta de aprovação. Ordem sugerida: MCU e oscilador, desacoplamento VDD, alimentação (LDOs, VDDA), IMU, conectores e bordas (USB, J1, J5, J6, J2), microSD, motores e buzzer, barômetro, test points e pads.
