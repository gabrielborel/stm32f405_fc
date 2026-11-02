# Guia de roteamento da FC (placa de 58 x 44 mm)

Guia para o roteamento manual no KiCad 10. Resume o que foi decidido antes do roteamento (2026-11-01 e 2026-11-02). O registro completo, com o histórico das decisões, está no `CLAUDE.md`. O passo a passo com referência, pino e coordenada de cada ligação está em `docs/ROTEAMENTO_DETALHADO.md`.

Legenda da fonte: **[manual]** vem do documento citado. **[projeto]** é prática ou decisão do projeto. **[inferência]** é dedução, não está em manual.

## 1. Antes de começar

- [ ] Reencher as zonas (`B`). O preenchimento da `HSE_GND_POUR` está desatualizado e gera `clearance` falsos contra o R1 e as trilhas do oscilador.
- [ ] Na barra de cima, lista de larguras em **"usar largura da net class"**.
- [ ] Desligar o botão de **ajuste automático de largura**. Com ele ligado, uma trilha que começa na ponta de outra copia a largura dela (documentação do KiCad, "Interactive Router > Track width").
- [ ] Conferir em Board Setup > Custom Rules que as regras do `STM32F405_FLIGHT_CONTROLLER.kicad_dru` aparecem.

## 2. Stackup e camadas

JLCPCB JLC04161H-3313, 1,56 mm. Fonte: jlcpcb.com/impedance e calculadora da JLCPCB.

| Camada | Função |
|---|---|
| L1 (F.Cu) | componentes, sinais rápidos (SDIO, USB, SPI1, oscilador), GND local |
| L2 (In1.Cu) | GND sólido (`GND_L2`), com a ilha do oscilador separada por um vão de 0,5 mm aberto para o U1 |
| L3 (In2.Cu) | +3V3 sólido (`3V3_L3`) |
| L4 (B.Cu) | sinais lentos, test points, rótulos dos pads |

Base: AN4488 Rev 7, Seção 8.1 e Figura 21 [manual]. Ilha do oscilador: AN2867 Rev 24, Seção 7.1 e Figuras 14 e 15 [manual].

## 3. Larguras por rede (net classes)

| Classe | Redes | Trilha | Clearance | Via |
|---|---|---|---|---|
| SDIO_50 | SDIO_CK, SDIO_CMD, SDIO_D0 a D3 | 0,151 mm (50 ohm) | 0,2 mm | 0,6 / 0,3 |
| USB_90 | USB_D+/-, /USB/USB_CONN_D+/- | par de 0,154 mm, espaço 0,203 mm (90 ohm) | 0,2 mm | 0,6 / 0,3 |
| Power | +5V, /USB/VBUS_RAW, +3V3, +3V3_SD, /Power/+VBAT, +12V, /Buzzer/BZ_NEG | 0,5 mm | 0,2 mm | 0,6 / 0,3 |
| Default | todas as outras (inclui +3.3VA, OSC_IN, OSC_OUT, GND fora dos planos) | 0,2 mm | 0,15 mm | 0,6 / 0,3 |

- Impedâncias: calculadora da JLCPCB, sinal em L1 com referência L2 [manual]. Pelo stackup simétrico, a mesma geometria em L4 com referência L3 também dá cerca de 50 e 90 ohm [inferência].
- Largura da Power: [projeto], sem conta de corrente.

### Regras do `.kicad_dru`

- **Power neckdown U1 U5:** dentro do courtyard do U1 e do U5, a classe Power usa 0,25 mm (mínimo 0,2 mm). A largura máxima que entra nos pinos de +3V3 é 0,30 mm no U1 (LQFP64, passo de 0,5 mm) e 0,35 mm no U5 (conta do projeto). Em todos os outros pads da placa a largura da classe cabe.
- **Power width outside neckdown:** fora do U1, do U5 e dos capacitores C1 a C6, C20 e C21, toda trilha Power precisa ter pelo menos 0,5 mm. O DRC acusa um trecho fino esquecido.

### Como o router escolhe a largura

- A largura é definida **no ponto onde a trilha começa** e vale para a trilha inteira.
- Para alimentar um pino do U1 ou do U5: começar no pino (sai com 0,25 mm), terminar logo fora do CI e recomeçar a partir da ponta (sai com 0,5 mm). Começando pelo capacitor, apertar `W` para 0,25 mm antes de entrar no CI.
- `W` e `Shift+W` trocam a largura durante a rota.

## 4. Ordem sugerida [projeto]

Do mais restrito para o mais livre. O U1 é o ponto mais apertado, então o roteamento começa por ele.

### 4.1 Oscilador (feito)

- [x] OSC_IN e OSC_OUT do Y1, C13 e C14 até os pinos 5 e 6 do U1, dentro da ilha.
- [ ] Deixar OSC_IN e OSC_OUT com a mesma largura (hoje 0,3 e 0,2 mm). O AN2867 Seção 7.2, Figura 18, cita "symmetry between oscillator capacitances"; estender às trilhas é [inferência].
- [ ] Decisão 8: R1 e o anel de guarda (courtyard sobreposto e clearance). É seu.
- [ ] Conferir no datasheet do X32258MOB4SI se o corpo é metálico. Se for, não ligar ao GND do oscilador (AN2867 Seção 7.1) [manual].

### 4.2 Desacoplamento

- [ ] Cada 100 nF ligado direto ao seu pino, curto, com via para o plano junto do pad (AN4488 Seção 8.3, "as close as possible", "as low impedance as possible") [manual].
- [ ] Ordem: pino, capacitor e só depois a via, do lado de fora do capacitor: via para a L3 no pad de +3V3 e via para a L2 no pad de GND (AN4488 Figura 23, p.38) [manual].
- [ ] Nenhuma via de GND dentro do vão da ilha na L2 (X 140,7 a 149,6 nas faixas Y 89,2 a 89,7 e Y 96,4 a 96,9; X 149,1 a 149,6): ali a via não encosta no plano e o DRC não acusa. Caso do C1: via de GND ao sul, Y 97,4 ou mais [conta].
- [ ] U1: pinos de VDD 19, 32, 48, 64 e o pino 1 (VBAT ligado ao +3V3) com C1 a C6 (C2 é o de 4,7 µF).
- [ ] VDDA (pino 13, rede +3.3VA): R34, C7 e C8 junto dos pinos 12 e 13.
- [ ] U5 (BMI270): C20 no pino 5 (VDDIO) e C21 no pino 8 (VDD), 1,26 mm cada (BMI270 Seção 7.2) [manual].
- [ ] U4 (BMP280): C19 no pino 8 (VDD) e C18 no pino 6 (VDDIO) (BMP280 Figura 17) [manual].
- [ ] LDOs U2 e U6: C9, C10, C22, C23 junto dos pinos.

### 4.3 Saída dos pinos do U1 (fanout)

- [ ] Decisão 10: pinos 14 a 16 (UART4 e vizinhos) apertados pelo grupo do VDDA (entre os pads e o C7 cabe uma trilha só, 0,57 mm); SDIO D2, D3, CK e CMD saem pelo lado sul, com o R17 embaixo dos pinos 51 a 55 (sobram 0,78 mm, cabe uma linha SDIO). Resolvido (`995dbbf`): R17 em (131,5; 101,2) rot 180, corredor de 2,28 mm; referência do C2 em (135; 103,25).
- [ ] Lado leste: entre a ponta dos pads (X 140,455) e o vão da L2 (X 140,7) não passa trilha. Os sinais desse lado (SD_CD, PC14, PC15, NRST, VBAT_SENSE, LED_RED, PC2, SD_EN, UART4_TX) saem para dentro do U1, descem numa via sob o corpo e seguem em L4 [conta / prática de projeto].
- [ ] Lado oeste, de cima para baixo: GPS_TX/RX (37, 38), SDIO_D0/D1 (39, 40), USB_D-/D+ (44, 45).
- [ ] GPS_TX/RX: via para L4 logo junto dos pinos.

### 4.4 Sinais com impedância

**USB (USB_90)**
- [ ] Usar a ferramenta de par diferencial (atalho `6`).
- [ ] O par sobe do U1 ao U3 e cruza o SDIO D0/D1: passar o par em L4 com duas vias simétricas por linha [inferência]. USB Full Speed, 12 Mbit/s.
- [ ] Trecho do conector até o U3 (USBLC6) curto: ESD o mais perto possível do receptáculo (AN4879 Rev 12, Seção 2.3, Tabela 11) [manual].
- [ ] Não passar o par sobre o vão da ilha na L2.

**SDIO (SDIO_50)** (AN4488 Rev 7, Seção 8.4.1) [manual]
- [ ] Tudo em L1, sem vias (garante o "mesmo número de vias" entre os dados).
- [ ] Comprimento abaixo de 120 mm (hoje 22 a 32 mm em linha reta).
- [ ] Diferença entre dados e CK, e entre CK e CMD, pequena: o manual pede skew abaixo de 250 ps @ 10 mm.
- [ ] Test points TP15 (CK) e TP14 (CMD) passando pelo pad, sem ramal (decisão 11). Eles ficam na face de baixo: a trilha segue em L1 e passa sobre uma via no centro do pad do TP, sem trocar de camada. Isso põe uma via no CK e no CMD, não nos dados [inferência].

### 4.5 SPI1 até a IMU

- [ ] SCK (cerca de 5,7 mm) em L1, curto, só com a IMU e sem capacitor (ES0182 Rev 19, Seção 2.12.4) [manual]. Passar pelo TP12 sem ramal (decisão 11).
- [ ] Sobra um cruzamento entre MOSI e MISO em qualquer rotação do U5 (conta do projeto). Usar a via que a linha já tem para o seu TP na face de baixo (TP10 MOSI, TP8 MISO).
- [ ] CS e INT1 com os TPs TP11 e TP9 da mesma forma.

### 4.6 Alimentação por trilha

- [ ] +5V do J1 aos LDOs (U2, U6), ao J5, J6, J10, ao buzzer (J7) e ao D4 (VBUS do USB).
- [ ] +3V3_SD do U6 ao J4 e aos pull-ups do SDIO.
- [ ] Buzzer: BZ_NEG e +5V do buzzer lado a lado em L1, curtos, para reduzir a área do laço chaveado [inferência].
- [ ] LDOs: preenchimento de GND em F.Cu em volta do U2 e do U6, com várias vias para a L2 junto do pino 2 (GND) (decisão 13) [projeto]. TJ estimada do U6 cerca de 103 °C a 200 mA.

### 4.7 Sinais lentos em L4

L4 se referencia à L3 e não passa pelo vão da ilha da L2.

- [ ] GPS_TX/RX: do lado oeste do U1 até o J6 (cerca de 33 mm).
- [ ] ELRS_TX/RX: do lado norte do U1 até o J5 (cerca de 31 mm).
- [ ] I2C1 SCL/SDA: do lado sul do U1 até o U4 e o J6 (39 a 44 mm), contornando o oscilador pelo sul e pelo leste.
- [ ] M3_OUT e M4_OUT: do R25/R26 (norte) até o J8 (sul), passando sob o U1.
- [ ] UART4 até o J10, LEDs, botões e demais sinais lentos.

### 4.8 NRST e BOOT0

- [ ] NRST: o pino 7 fica colado nos pinos 5 e 6 do oscilador. Sair para dentro do U1, descer numa via sob o corpo, seguir em L4 até perto do C15 e subir com via até C15, SW1 e J2. (Corrigido em 2026-11-02: o caminho antigo, subindo em L1 em X ≈ 140,5, não cabe; a ponta dos pads fica em X 140,455 e o vão começa em X 140,7, sobram 0,245 mm [conta].)
- [ ] BOOT0: do pino 60 (sul) até R4 e SW2.

### 4.9 Fim

- [ ] Preenchimento de GND em L1 e L4 com vias de costura para a L2 (AN4488 Figura 21: "+ GND" nas camadas externas) [projeto].
- [ ] Reencher as zonas (`B`) e rodar o DRC.
- [ ] Revisar as posições dos test points na face de baixo (podem mudar depois do roteamento).

## 5. Não fazer

- Não cruzar o vão da ilha do oscilador na L2 com trilhas de L1. Exceção aceita (2026-11-02): o C8.1 (+3.3VA) fica em cima da perna norte do vão e a trilha do VDDA cruza o vão; é alimentação filtrada, risco baixo [inferência] (ver `ROTEAMENTO_DETALHADO.md`, passo 3).
- Não pôr via de GND dentro do vão (não liga ao plano).
- BUZZER (pino 58) e MOTOR2 (pino 57) se cruzam em L1 entre o C2 e o R24: BUZZER por dentro do U1 e L4.
- Não passar sinais de alta frequência perto do oscilador (AN2867 Seção 7.1, Figura 16) [manual].
- Não deixar ramal (stub) nos test points do SPI1 e do SDIO.
- Não alimentar servos pelos pads AUX: a corrente vem da PDB ou do BEC [projeto].

## 6. Conferência

Ao terminar cada trecho, pedir ao Claude para conferir (só leitura, sem mexer nas trilhas):
- DRC numa cópia e comparação com a referência;
- comprimentos e diferença entre as linhas do SDIO e do par USB;
- número de vias no SDIO;
- trilhas cruzando o vão da ilha;
- larguras de cada classe.

DRC de referência antes do roteamento: 8 violações (4 avisos de footprint excluídos) e 249 itens não conectados. Depois dos primeiros trechos (2026-11-02): 11 violações, sendo 5 `clearance` de preenchimento desatualizado da `HSE_GND_POUR` (somem com `B`), 2 `clearance` e 2 `courtyards_overlap` do R1 (decisão 8) e 2 avisos de silk do J3 (decisão 1).

## 7. Depois do roteamento (fora da PCB)

- Decisão 12, firmware: eixos da IMU com o U5 em rot 270 sem remapeamento; OSPEEDR alto no SCK; esperar pelo menos uns 2,3 ms ao desligar e religar o cartão (SD Spec 9.10 Seção 6.4.1.2) e pôr as linhas SDIO em nível baixo antes de desligar.
- Decisão 14: confirmar com a JLCPCB que não usam solda por fase de vapor (BMP280 Seção 7.6) [manual].
- Custo do controle de impedância na cotação da JLCPCB.
