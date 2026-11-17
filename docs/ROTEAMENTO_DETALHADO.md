# Roteamento detalhado, passo a passo (placa de 58 x 44 mm)

Complementa o `docs/ROTEAMENTO.md` (regras gerais, larguras e checklist). Aqui fica o "o quê liga em quê" por bloco, com referência, pino e coordenada.

- Coordenadas em mm, tiradas do `.kicad_pcb` pelo `pcbnew` em 2026-11-02 (com o R17 já na posição nova, `995dbbf`). Se uma peça se mover, a coordenada aqui fica velha.
- Distância "pino ao pad" é em linha reta, entre centros, não é comprimento de trilha.
- Legenda: **[manual]** vem do documento citado; **[projeto]** é prática ou decisão do projeto; **[inferência]** é dedução minha, sem manual; **[conta]** é conta minha feita sobre as coordenadas.
- Aviso: eu não tenho noção espacial confiável. Os caminhos sugeridos são pontos de partida; quem decide olhando a placa é você. Depois de cada passo eu confiro por DRC e por script (só leitura).

## 0. Como o GND e o +3V3 chegam nas peças

### Planos


| Camada      | O que é                             | Consequência no roteamento                                                                                                |
| ----------- | ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| L2 (In1.Cu) | `GND_L2`, GND sólido na placa toda  | Nenhuma trilha de GND precisa ser desenhada até longe. Cada pad de GND ganha uma via logo ao lado e "desce" para o plano. |
| L3 (In2.Cu) | `3V3_L3`, +3V3 sólido na placa toda | Igual para o +3V3: cada pad de +3V3 ganha uma via para o plano. O +3V3 **não** precisa de trilha longa da classe Power.   |


As vias ligam direto nas zonas (sem alívio térmico), configuração já feita nas zonas. Via de todas as classes: 0,6 / 0,3 mm.

### Capacitor de desacoplamento: a ordem é pino, capacitor, via

AN4488 Rev 7, Seção 8.3 e Figura 23 (p.38) [manual]: a figura mostra o pino VDD e o pino VSS indo por trilha curta até os dois pads do capacitor, e **só depois** a via ("Via to VDD" ao lado do pad de VDD do capacitor, "Via to VSS" ao lado do pad de VSS). O texto pede ligações "as low impedance as possible" e capacitores "as close as possible to, or below, the appropriate pins".

```
   via +3V3 (L3)   via GND (L2)
        o               o
        |               |
     [ C+ ]-----------[ C- ]      capacitor
        |               |
      pino VDD       pino VSS     (MCU)
```

Por que nessa ordem [inferência apoiada na Figura 23]: a corrente de alta frequência que o pino puxa sai do capacitor pelo caminho mais curto. Se a via ficar entre o pino e o capacitor, o pino passa a "ver" primeiro o plano (com a indutância da via) e o capacitor fica de lado.

Na prática, para cada capacitor:

1. Trilha curta do pino de alimentação até o pad + do capacitor.
2. Se o pino de GND do CI for vizinho, trilha curta dele até o pad - do capacitor (U1: pinos 18, 63 e 12; nos outros pinos de VDD o vizinho não é GND).
3. Uma via ao lado do pad +, para a L3; uma via ao lado do pad -, para a L2. Via **ao lado**, não dentro do pad (via no pad puxa solda na montagem, prática de projeto).

### Padrão de distância das vias (decidido em 2026-11-02, `129a801`)

Distância do **centro da via** (0,6 / 0,3 mm) ao **centro do pad** a que ela se liga, em linha reta, com um só segmento de trilha do centro do pad até a via [projeto]. Os valores saíram do que já estava roteado no U1 e deixam de 0,2 a 0,37 mm de cobre entre a via e o pad [conta].

| Caso | Distância | Exemplos no U1 |
| ---- | --------- | -------------- |
| Capacitor 0402 | 0,82 mm | C1, C3, C4, C5 (GND) |
| Capacitor 0603 | 1,12 mm | C12 (GND) |
| Capacitor 0805 | 1,35 mm | C2 (+3V3 e GND) |
| Via para dentro do U1 (sob o corpo) | 1,27 mm do centro do pino | pinos 1, 12, 19, 32, 48, 64 |

- Exceção com motivo vale mais que o padrão: o C11 (via em diagonal, 1,19 mm), porque a via reta ao norte cai sobre o TP10 da face de baixo (o DRC acusa curto), e o pino 63 (dobra), que fica ao lado da via do pino 64.
- Como colocar sem o mouse: rotear até perto, selecionar a via, `E` e digitar X e Y. A diferença elétrica de alguns centésimos é irrelevante [inferência]; o padrão serve para organização e repetição. Com o mouse saem degraus pequenos (0,005 a 0,02 mm), que eram os do C3 e do C5.
- **Ao fim de cada bloco**, antes de passar ao próximo, eu meço as vias (distância, folga, degraus) e proponho a padronização (passo 13).

### Armadilha: via de GND dentro do vão da ilha do oscilador

A rule area `HSE_ISLAND_GAP_L2` proíbe cobre de zona na L2 nas faixas abaixo [conta, polígono lido do arquivo]:

- perna norte: X 140,7 a 149,6, Y 89,2 a 89,7;
- perna sul: X 140,7 a 149,6, Y 96,4 a 96,9;
- perna leste: X 149,1 a 149,6, Y 89,2 a 96,9.

Uma via de GND com o centro dentro dessas faixas (ou a menos de cerca de 0,5 mm delas) **não encosta no plano** da L2. O DRC não acusa, porque a via continua ligada ao pad em L1. Nesses pontos, mover a via para fora da faixa.

## 1. Preparação

- [x] Reencher as zonas (`B`).
- [x] Lista de larguras em "usar largura da net class" e o ajuste automático de largura desligado (ver `ROTEAMENTO.md`, item 1).
- [x] **Sobre a trilha que saiu com 0,151 mm:** 0,151 é a largura da classe SDIO_50 (a do USB é 0,154). No arquivo salvo não há trilha com 0,151. Se ela apareceu numa rede que não é SDIO, as causas prováveis são: (a) ajuste automático ligado, começando na ponta de uma trilha SDIO; (b) a lista de larguras num valor fixo em vez de "net class"; (c) a rede é mesmo SDIO. Para ver a classe de uma rede: passar o mouse sobre o pad e olhar o painel de propriedades.
- [x] Ponto de partida (2026-11-02, `6a1ff4e`): só as trilhas do oscilador, o anel de GND e as 15 vias dele. As ligações de desacoplamento do U1 (+3V3 e +3.3VA) foram apagadas para recomeçar do zero; os testes não commitados foram descartados (cópia guardada fora do repositório). DRC: 15 violações, todas anteriores; 247 não conectados.

## 2. Desacoplamento do U1 (MCU)

U1 em (134; 92), rot 180. Com essa rotação, o pino 1 fica no canto sudeste: **lado leste** pinos 1 a 16, **norte** 17 a 32, **oeste** 33 a 48, **sul** 49 a 64.

Regras: AN4488 Seção 8.3 [manual]; um 100 nF por VDD e um 4,7 µF para o encapsulamento, AN4488 Seção 2.2 [manual]. Largura: o +3V3 sai do pino com 0,25 mm (regra "Power neckdown U1 U5" do `.kicad_dru`); a regra "Power width outside neckdown" isenta os courtyards de C1 a C6, então a ligação inteira até o capacitor pode ficar em 0,25 mm. GND é classe Default (0,2 mm).


| Pino U1                   | Rede                      | Capacitor (pad)                    | Distância       | GND vizinho                                   | Caminho e via                                                                                                                                                                                                                                  |
| ------------------------- | ------------------------- | ---------------------------------- | --------------- | --------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 19 (136,75; 86,33), norte | +3V3                      | C4.1 (136,82; 84,8)                | 1,53            | pino 18 (137,25) ao C4.2 (137,78; 84,8), 1,62 | Os dois sobem retos. Vias: +3V3 a oeste do C4.1, GND a leste do C4.2. **Atenção:** o pino 17 (IMU_INT1, 137,75) fica bem embaixo do C4.2; ver passo 8.                                                                                         |
| 32 (130,25; 86,33), norte | +3V3                      | C3.1 (129,38; 84,8)                | 1,76            | não (pino 31 é VCAP_1)                        | Diagonal para noroeste. Via GND a oeste do C3.2 (128,42). Não cruza a trilha do pino 31, que sobe reta em X 130,75.                                                                                                                            |
| 48 (128,32; 95,75), oeste | +3V3                      | C5.1 (127,38; 96,7)                | 1,34            | não (pino 47 é VCAP_2)                        | Diagonal para sudoeste. Via GND a oeste do C5.2 (126,42).                                                                                                                                                                                      |
| 64 (137,75; 97,67), sul   | +3V3                      | C6.1 (138,12; 99,3)                | 1,67            | pino 63 (137,25) ao C6.2 (137,16; 99,3), 1,63 | Os dois descem retos (a ordem dos pads do C6 casa com a dos pinos). **Vias:** entre o C6 e o R24 sobram 0,7 mm, não cabe via (precisa de 0,9) [conta]. Via +3V3 a leste do C6.1 (X 138,9 ou mais), via GND a oeste do C6.2 (X 136,4 ou menos). |
| 1 (139,68; 95,75), leste  | +3V3 (VBAT ligado ao 3V3) | C1.1 (141,3; 95,82)                | 1,62            | não                                           | Reta para leste. **Atenção:** o pad C1.2 (GND, Y 96,5 a 97,06) fica em cima da perna sul do vão (Y 96,4 a 96,9). A via de GND do C1 vai ao sul, com centro em Y 97,4 ou mais [conta].                                                          |
| C2 4,7 µF (135; 101,5)    | +3V3 / GND                | pads C2.1 (134,05) e C2.2 (135,95) | 3,8 do lado sul | -                                             | Capacitor de volume do encapsulamento (AN4488 Seção 2.2). Basta uma via para a L3 junto do C2.1 e uma para a L2 junto do C2.2 [projeto].                                                                                                       |


### VCAP (regulador interno do núcleo)

DS8626 Rev 12, Seção 6.3.2 e Tabela 16 [manual]: CEXT de 2,2 µF com ESR &lt; 2 Ω em VCAP_1 e VCAP_2. O DS8626 não dá regra de layout; trilha curta e larga é [prática de projeto].


| Pino U1                   | Rede            | Capacitor             | Distância | Caminho                                                                                                                       |
| ------------------------- | --------------- | --------------------- | --------- | ----------------------------------------------------------------------------------------------------------------------------- |
| 31 (130,75; 86,33), norte | Net-(U1-VCAP_1) | C11.1 (130,75; 84,42) | 1,91      | Reta para o norte. Largura 0,3 mm (o máximo que entra no pad, conta do `.kicad_dru`). Via GND junto do C11.2 (130,75; 82,88). |
| 47 (128,32; 95,25), oeste | Net-(U1-VCAP_2) | C12.1 (126,38; 95,25) | 1,94      | Reta para oeste, 0,3 mm. Via GND junto do C12.2 (124,83; 95,25).                                                              |


Para usar 0,3 mm: `W` antes de começar, ou largura personalizada na lista. A classe Default daria 0,2 mm (funciona, só fica mais indutivo).

### Pino 12 (VSSA) e o GND da ilha

O pino 12 (139,68; 90,25) é o GND mais próximo do oscilador. Ele vai por trilha ao C8.2 (141,5; 90,48), 1,83 mm. Esse pad cai na região onde a ilha se liga ao plano (X 140,7 a 141,9). Via do C8.2 para a L2 com o centro em Y 90,2 ou mais (fora da perna norte do vão) [conta]. AN2867 Rev 24, Seção 7.1 [manual]: o plano do oscilador se liga "to the nearest MCU/MPU ground".

### Checklist do passo 2

Estado em 2026-11-02 (`da8c2d1` e `129a801`): passo 2 feito. DRC com as 6 violações antigas, 221 não conectados; as 15 vias de desacoplamento ligadas aos planos depois do reenchimento.

- [x] Pinos 19, 32, 48, 64 e 1 com seus capacitores. Na prática o +3V3 desses pinos desce por uma via para dentro do U1 (1,27 mm) e a via de GND fica no pad - do capacitor.
- [x] Pinos 18, 63 e 12 de GND ligados ao pad - do capacitor vizinho.
- [x] VCAP_1 e VCAP_2 ligados. Ficaram com 0,2 mm (0,3 era sugestão, opcional).
- [x] C2 só por vias: +3V3 em (134,05; 102,85) e GND em (135,95; 102,85).
- [x] Nenhuma via de GND dentro do vão da ilha (a do C1 ficou em Y 97,6).
- [x] Conferência e padronização das vias (`129a801`).
- [x] A trilha +3.3VA do pino 13 ao C8.1 passa sobre a perna norte do vão: aceita como exceção (passo 3, ponto aberto 4).

## 3. VDDA (filtro do analógico)

Cadeia: +3V3 no R34.1 (145,03; 88,4), R34 de 0 ohm, R34.2 (143,38; 88,4) = +3.3VA, depois C7.1 (141,5; 88,33), depois C8.1 (141,5; 89,52), depois pino 13 (139,68; 89,75). O TP4 (145; 87, face de baixo) também é +3.3VA.

AN4488 Seção 2.2 [manual]: VDDA com 100 nF + 1 µF (C8 e C7). O filtro perto dos pinos 12 e 13 é [projeto].

Estado em 2026-11-02 (`5d3974d`): passo 3 feito. DRC com as 6 violações antigas, 216 não conectados; as duas vias novas ligadas aos planos.

- [x] R34.1: via para a L3 em (146,145; 88,4), a leste, 1,12 mm (padrão 0603), trilha de 0,5 mm (classe Power).
- [x] R34.2 ao C7.1 e o C7.1 ao C8.1 (classe Default, 0,2 mm). O degrau de 0,075 mm junto do R34.2 vem da diferença de Y entre os centros dos pads (88,325 e 88,4), não do mouse.
- [x] C8.1 ao pino 13.
- [x] C7.2: via para a L2 em (141,5; 85,655), ao norte, 1,12 mm, longe do vão.
- [x] TP4: trilha em L1 do R34.2 até uma via no centro do pad do TP4 (145; 87).

**Exceção aceita (decisão do Gabriel, 2026-11-02):** o pad C8.1 (Y 89,24 a 89,8) já fica em cima da perna norte do vão (Y 89,2 a 89,7), então a ligação do C7 ao C8 cruza o vão. É uma linha de alimentação filtrada, sem borda rápida; o laço de desacoplamento (pino 13, C8, pino 12) fica todo em L1 [inferência: risco baixo]. A regra "não cruzar o vão" foi pensada para sinais. Decisão: fica como está, sem mexer no C7/C8.

## 4. Desacoplamento dos outros CIs


| CI        | Pino                        | Rede | Capacitor                         | Distância | Fonte                                     |
| --------- | --------------------------- | ---- | --------------------------------- | --------- | ----------------------------------------- |
| U5 BMI270 | 5 (134,74; 80,5) VDDIO      | +3V3 | C20.2 (133,6; 80,5), C20 rot 90   | 1,14      | BMI270 Rev 1.6, Seção 7.2, p.136 [manual] |
| U5        | 8 (135,0; 82,26) VDD        | +3V3 | C21.2 (135,0; 83,52)              | 1,26      | idem                                      |
| U5        | 6 e 7 (134,74; 81,0 e 81,5) | GND  | C20.1 (133,6; 81,46), direto      | -         | -                                         |
| U4 BMP280 | 6 (155,32; 79,8) VDDIO      | +3V3 | C18.2 (157,1; 79,32)              | 1,84      | BMP280 Rev 1.26, Figura 17, p.37 [manual] |
| U4        | 8 (154,03; 79,8) VDD        | +3V3 | C19.1 (154,52; 80,9)              | 1,21      | idem                                      |
| U4        | 1, 5, 7                     | GND  | vias para a L2                    | -         | -                                         |
| U4        | 2 (154,68; 78,2)            | +3V3 | via para a L3                     | -         | -                                         |


U5: o +3V3 sai do pino com 0,25 mm (neckdown); o pad do U5 aceita no máximo 0,35 mm [conta do `.kicad_dru`].

Revisão de 2026-11-02 (`2e5894d`), testada numa cópia com todas as ligações abaixo (DRC sem violação nova, vias ligadas aos planos):

- **C20 na vertical** a oeste do U5: pad de +3V3 de frente para o pino 5 e pad de GND de frente para os pinos 6 e 7. Ligações retas em L1 (pino 5 ao C20.2 com 0,25 mm; pinos 6 e 7 juntos ao C20.1 com 0,2 mm), laço de desacoplamento todo em L1, como o C4 com o pino 18 [prática de projeto, padrão da AN4488 Figura 23]. Vias a oeste, 0,82 mm: +3V3 em (132,78; 80,5) com 0,5 mm (fora dos courtyards vale a largura Power) e GND em (132,78; 81,46).
- **C21 fica** em (135; 84), rot 90: pino 8 ao C21.2 reto. Vias a oeste, 0,82 mm: +3V3 em (134,18; 83,52) com 0,5 mm e GND em (134,18; 84,48). A via de GND não pode ir ao sul (cairia sobre o pino 22 do U1).
- **C19** subiu 0,5 mm (o C18 já encostava no U4). Aproximar o C20 e o C21 mais 0,15 mm não muda nada [inferência]; o ganho do C20 é o caminho de volta pelo GND.

LDOs (todos na linha Y 102,7; regra de alimentação em [projeto], DS39724 para valores):


| Peça                       | Entrada (+5V)                                                                 | Saída                                                                                                                                       | GND                                                                      |
| -------------------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| U2 (123,7; 102,7), +3V3    | pinos 1 e 3 (122,56; 101,75 e 103,65), C9.1 (120,8; 101,92)                   | pino 5 (124,84; 101,75) ao C10.1 (126,7; 101,92); **2 vias** para a L3 junto do pino 5 ou do C10.1 (é a entrada do plano inteiro) [projeto] | pino 2 (122,56; 102,7) e C9.2, C10.2: várias vias para a L2 (decisão 13) |
| U6 (115,5; 102,7), +3V3_SD | pino 1 (114,36; 101,75), C22.1 (112,6; 101,92)                                | pino 5 (116,64; 101,75) ao C23.1 (118,4; 101,92), segue por trilha (passo 9)                                                                | pino 2 (114,36; 102,7), C22.2, C23.2: várias vias (decisão 13)           |
| U6                         | pino 3 = SD_EN (114,36; 103,65), vem do U1 pino 11 e do R15.1 (109,9; 103,53) | -                                                                                                                                           | -                                                                        |


Estado em 2026-11-02: passo 4 feito. U5 (`2c4ea27`), U4 (`161505b`: pino 6 ao C18 por baixo do corpo, pinos 1 e 7 juntos numa via a oeste, CSB na L3), LDOs (`48f4ddf`: EN do U2 ligado ao pino 1 por baixo do corpo, duas vias do +3V3 do U2 para a L3, uma no TP6; C9 e C23 dividem uma via de GND). DRC com as 6 violações antigas; 175 não conectados. Pendentes neste bloco: SD_EN (sai do U6 pelo sul até o R15), TP5 (GND, embaixo do pino 4 do U2, sem lugar para via no pad) e TP13 (+3V3_SD, liga com a trilha até o J4, passo 9).

Decisão 13 [projeto]: preenchimento de GND em F.Cu em volta do U2 e do U6, com várias vias para a L2 junto do pino 2. Pode ser uma zona pequena de GND em F.Cu (fica para o passo 12, preenchimentos).

## 5. Saída dos pinos do U1, lado por lado

Como funciona o "fanout para dentro" [prática de projeto]: o LQFP64 não tem pad central, então o miolo do U1 em L1 é livre (pads internos terminam em X 129,1 e 138,9, Y 87,1 e 96,9) [conta]. Um sinal que precisa ir para o outro lado da placa sai do pad **para dentro**, desce numa via sob o corpo do CI e segue em L4. Isso libera o lado de fora para quem fica em L1. Cuidados: vias espaçadas, sem formar uma fileira que corte o plano da L2; vias cobertas por máscara (tented) embaixo do CI. Faixa útil para o centro da via: X 129,55 a 138,45, Y 87,55 a 96,45 [conta, 0,15 mm de clearance ao pad].

Medidas que travam o fanout [conta, pads de 1,55 x 0,3 mm]:

- **Leste:** a ponta dos pads fica em X 140,455 e o vão começa em X 140,7: sobram 0,245 mm. Não passa trilha nenhuma em L1 entre os pinos do leste e o vão no trecho Y 89,2 a 96,9.
- **Leste, pinos 14 a 16:** entre a ponta dos pads (140,455) e o C7 (141,025) sobram 0,57 mm: cabe **uma** trilha de 0,2 mm.
- **Sul:** a ponta dos pads fica em Y 98,445 e o R17 começa em Y 99,225: sobram 0,78 mm. Cabe **uma** trilha SDIO (0,151 mm com 0,2 de cada lado = 0,551 mm), e são quatro. Ver passo 6.

### Lado leste (pinos 1 a 16), de frente para o oscilador


| Pino | Rede            | Vai para                                            | Sugestão                                                                                                                                   |
| ---- | --------------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| 1    | +3V3            | C1                                                  | passo 2                                                                                                                                    |
| 2    | SD_CD           | R18.2 (126,3; 88,47), J4.10 (119,4; 99,04)          | Para dentro, via, L4 até o oeste. Lento.                                                                                                   |
| 3    | PC14            | J13.2 (142,3; 105,9)                                | Para dentro, via, L4 para o sul.                                                                                                           |
| 4    | PC15            | J13.3 (142,3; 103,36)                               | Para dentro, via, L4 para o sul.                                                                                                           |
| 5, 6 | OSC_IN, OSC_OUT | ilha                                                | feito (passo 4.1 do `ROTEAMENTO.md`)                                                                                                       |
| 7    | NRST            | C15, SW1, J2.5                                      | Ver passo 11. **O caminho de L1 do `ROTEAMENTO.md` (subir em X ≈ 140,5) não cabe** (0,245 mm). Para dentro, via, L4.                       |
| 8    | VBAT_SENSE      | R2.2 (144,82; 98,6), R3.1, C26.1, TP3               | Para dentro, via, L4 para o sudeste, subir em L1 perto do R2/R3. AN4073: lento, mas é ADC; longe do +5V e do buzzer [inferência].          |
| 9    | LED_RED         | R5.2 (148,43; 82,2)                                 | Para dentro, via, L4 para o nordeste.                                                                                                      |
| 10   | PC2             | R39.2, R38.1, C27.2 (cerca de 159 a 161; 100 a 104) | Para dentro, via, L4 para o leste. Entrada de ADC: evitar correr junto do I2C e do buzzer [inferência].                                    |
| 11   | SD_EN           | U6.3 (114,36; 103,65), R15.1 (109,9; 103,53)        | Para dentro, via, L4 até o sudoeste (28 mm).                                                                                               |
| 12   | GND (VSSA)      | C8.2                                                | passo 2                                                                                                                                    |
| 13   | +3.3VA          | C8.1                                                | passo 3                                                                                                                                    |
| 14   | UART4_TX        | J10.3 (143,38; 74,5)                                | Pino em Y 89,25 fica dentro da faixa da perna norte do vão: para dentro, via, L4.                                                          |
| 15   | UART4_RX        | J10.4 (145,92; 74,5)                                | A única trilha que cabe no corredor de 0,57 mm entre os pads e o C7. Sobe em L1 até acima do C7 e segue ao J10. Ou para dentro, como o 14. |
| 16   | PA2 (AUX1)      | R35.1 (131,6; 74,83)                                | Vai para o noroeste, longe: para dentro, via, L4.                                                                                          |


### Lado norte (pinos 17 a 32)


| Pino    | Rede                     | Vai para                                      | Sugestão                                                                                                                                                  |
| ------- | ------------------------ | --------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 17      | IMU_INT1                 | TP9 (137,6; 84,0, baixo), U5.4 (135,0; 79,74) | passo 8                                                                                                                                                   |
| 18      | GND                      | C4.2                                          | passo 2                                                                                                                                                   |
| 19      | +3V3                     | C4.1                                          | passo 2                                                                                                                                                   |
| 20 a 23 | SPI1 CS, SCK, MISO, MOSI | U5 e TPs                                      | passo 8                                                                                                                                                   |
| 24, 25  | LED_GREEN, LED_YELLOW    | R7.2 e R6.2                                   | Plano do lado norte, abaixo.                                                                                                                              |
| 26, 27  | MOTOR3, MOTOR4           | R25.1 e R26.1                                 | Plano do lado norte, abaixo (R25 movido para junto do R26).                                                                                               |
| 28      | BOOT1                    | R16.1 (131,0; 80,33)                          | Plano do lado norte, abaixo.                                                                                                                              |
| 29, 30  | ELRS_TX, ELRS_RX         | J5.3 e J5.4                                   | Plano do lado norte, abaixo.                                                                                                                              |
| 31      | VCAP_1                   | C11                                           | passo 2                                                                                                                                                   |
| 32      | +3V3                     | C3                                            | passo 2                                                                                                                                                   |


#### Plano do lado norte (testado numa cópia em 2026-11-02; R25 movido em `9d636b1`)

O R25 estava logo acima dos pinos 24 a 28 e, junto com as vias do C21, fechava a saída dos LEDs em L1. Ele foi para (129,0; 79,45), rot 90, empilhado acima do R26 (pad 1 MOTOR3 em (129,0; 80,275), pad 2 M3_OUT em (129,0; 78,625)). Referência do R11 escondida no silk. Com o esboço completo, o DRC não teve violação nova e as 7 linhas fecharam; as trilhas ficam por sua conta.

Larguras: 0,2 mm (Default). Cantos a 45°. Pontos em mm.

| Rede | Trecho | Pontos | Vias |
| ---- | ------ | ------ | ---- |
| BOOT1 | L1 | pino 28 (132,25; 86,325), (132,25; 85,45), (131,55; 84,75), (131,55; 82,3), (131,2; 81,95), (131,2; 80,525), R16.1 (131,0; 80,325) | - |
| GND do R16.2 | L1 | (131,0; 78,675) até a via | (130,0; 77,6) |
| LED_YELLOW | L1 | pino 25 (133,75; 86,325), (133,75; 85,35), (132,1; 83,7), (132,1; 82,3), (131,75; 81,95), (131,75; 78,9), (132,1; 78,55), via | (132,1; 78,0) |
| | L4 | via, (133,7; 76,4), (149,9; 76,4), (150,2; 76,7), via | (150,2; 79,8) |
| | L1 | via até R6.2 (148,425; 79,8) | - |
| LED_GREEN | L1 | pino 24 (134,25; 86,325), (134,25; 85,35), (132,6; 83,7), (132,6; 82,3), (132,1; 81,8), (132,1; 79,9), (132,6; 79,4), via | (132,6; 78,9) |
| | L4 | via, (134,65; 76,85), (149,2; 76,85), via | (149,5; 77,15) |
| | L1 | via, (148,75; 77,4), R7.2 (148,425; 77,4) | - |
| ELRS_RX | L1 | pino 30 (131,25; 86,325) reto até a via | (131,25; 88,5) |
| | L4 | via, (131,0; 88,25), (131,0; 75,6), (131,3; 75,3), (159,45; 75,3), (159,75; 75,6), via | (159,75; 77,905) |
| | L1 | via até J5.4 (161,4; 77,905) | - |
| ELRS_TX | L1 | pino 29 (131,75; 86,325), (131,75; 87,4), via | (131,95; 87,6) |
| | L4 | via, (131,5; 87,15), (131,5; 76,05), (131,8; 75,75), (158,7; 75,75), (159,0; 76,05), via | (159,0; 79,155) |
| | L1 | via até J5.3 (161,4; 79,155) | - |
| MOTOR4 | L1 | pino 27 (132,75; 86,325), (132,75; 87,25), (132,6; 87,4), via | (132,6; 88,45) |
| | L4 | via, (132,6; 89,0), (132,3; 89,3), (127,9; 89,3), (127,6; 89,0), (127,6; 83,82), via | (128,0; 83,42) |
| | L1 | via até R26.1 (129,0; 83,42) | - |
| MOTOR3 | L1 | pino 26 (133,25; 86,325) reto até a via | (133,25; 89,4) |
| | L4 | via, (132,75; 89,9), (127,45; 89,9), (127,15; 89,6), (127,15; 81,125), via | (128,0; 80,275) |
| | L1 | via até R25.1 (129,0; 80,275) | - |

Por que assim:

- Os LEDs não têm saída para dentro do U1 (a saída do MOSI passa embaixo do pino 24) nem para o norte reto (vias do C21). Sobem em L1 pelo corredor onde estava o R25 e passam entre o R16 e as vias do C20, que é o gargalo (cabem duas trilhas, a 0,15 mm uma da outra) [conta].
- ELRS e motores descem logo no U1 (vias desencontradas, porque os pinos são vizinhos). O ELRS sobe em L4 numa coluna curta; os motores vão para oeste por baixo do U1, ao sul das vias do ELRS, para não cruzar.
- Faixa da L4 ao norte (barramento leste-oeste): ELRS_RX em Y 75,3, ELRS_TX em 75,75, LED_YELLOW em 76,4, LED_GREEN em 76,85. As linhas que sobem para os conectores do topo (UART4, PA2, PB7, PA10, SWD, NRST) cruzam essa faixa em L1.
- O INT1 fica como está (ponto aberto 8): a faixa não precisou do espaço dele.

Folgas apertadas (todas passam no DRC): par de LEDs no gargalo 0,15; LED_GREEN junto da via de GND do C21 0,166; LED_YELLOW junto do R16 0,175; coluna do ELRS_TX junto da via do LED_YELLOW 0,2; coluna do ELRS_RX junto das vias do pino 32 e do C11 0,2.

Pendências que este plano cria:

- Resolvido (`631b066`): M3_OUT e M4_OUT. Via junto do R25.2 em (128,0; 78,625) e, para o M4_OUT, trilha em L1 do R26.2 para oeste até a via em (126,0; 81,78). Na L4 descem em X 126,75 (M3) e 126,0 (M4), a oeste das colunas dos motores; logo abaixo da faixa dos motores (Y 90,3) entram sob os pads oeste do U1 (X 128,1 e 127,6) para desviar do TP1 e do TP2. O M3 vai para leste em Y 100,8 (logo abaixo do U1), desce a oeste do C2 em X 133,4 e corre em Y 105,3; o M4 volta para X 126,0 (entre o TP5 e a via de GND do C10) e corre em Y 105,8. Sobem por vias ao norte do R32.2 (136,6; 104,5) e do R33.2 (138,4; 104,5) e seguem em L1 até J8.3 e J8.4, passando entre os resistores. 45,2 e 49,5 mm, 2 vias cada. Menor folga 0,2 mm (M3_OUT contra o MOTOR3). Ficam bloqueados na L4: a faixa X 126 a 128 a oeste do U1 (Y 79 a 102) e a faixa Y 100,8 a 106 ao sul do U1 até X 138,4. O I2C e o BUZZER, que saem pelo sul, devem ficar acima de Y 104 e a leste de X 133,4.
- As linhas dos motores na L4 em Y 89,3 e 89,9 (X 127 a 133) fecham essa faixa por baixo do U1: SPI2 (pinos 33 a 36) e GPS (37 e 38) não podem ter via para dentro nesse trecho. Entra no plano do lado oeste.

#### Leste, parte 1 (2026-11-02, testado numa cópia, DRC sem violação nova)

- Vias movidas (`9e61881`): GND do pino 63 e do C6 saiu de dentro do U1 para junto do C6.2, em (136,34; 99,3); via do BUZZER para logo abaixo do pino 58, em (134,95; 99,15). Liberam o leque dos pinos 59 a 62.
- UART4 (`573d1d8`): TX (pino 14) por via funda em (137,55; 89,25) e canal nordeste na L4 (X 137,55, depois 138,25), sobe em (138,25; 77,6) e cruza a faixa do norte em L1 em Y 75,8 até o J10.3. RX (pino 15) por via rasa em (138,4; 88,6) e corredor leste (X 140,05), sobe em (140,05; 77,6) e cruza em Y 76,4 até o J10.4. TP7 (GND) mudou para (143,2; 83,9), com via no pad.
- LED_RED e NRST (`b1fb9cb`): LED_RED (pino 9) por via funda em (137,45; 91,75), corredor leste em X 140,5, leste em Y 82,2 até a via a leste do R5.2. NRST (pino 7) por via em (137,45; 93,45), corredor em X 140,95, leste em Y 87,8 (entre o TP4 e a via do R34), via junto do C15.1; L1 até o C15 e por baixo do SW1 até os dois pads 2. Passa na L4 por baixo dos pads do oscilador [inferência: os planos L2 e L3 blindam]. Falta o NRST até o J2.5.
- Leque reservado para os pinos 8 e 10: vias em (136,6; 92,6) e (136,6; 90,9).

Capacidade que sobra (ponto aberto, resolvido na parte 2): o canal nordeste e o corredor leste estão cheios (UART4, LED_RED, NRST). O PA2 fica sem caminho por ali. O J13 saiu (`894256c`, PC14 e PC15 sem ligação).

#### Leste, parte 2: canto sudeste e I2C (`91912c6`, 2026-11-02, testado numa cópia, DRC sem violação nova, 144 para 119 não conectados)

A "reserva" da parte 1 (vias em X 136,6) não foi usada. Sem cruzamento fora do U1: o PC2 cruza por dentro do U1 em L1.

| Rede | Caminho | Vias |
| ---- | ------- | ---- |
| VBAT_SENSE | pino 8, L1 para dentro até a via (136,4; 92,6); L4 desce, leste em Y 94,2 (abaixo da via do NRST), corredor X 141,45, leste em Y 96,9 até o TP3, agora em (145,6; 97,3) com via no pad; L1 ao R2.2, ao R3.1 e ao C26.1. 21,6 mm | 2 |
| PC2 | pino 10, L1 a oeste em Y 91,15 (acima da via do LED_RED) e desce em X 133,9 até a via entre os pinos 56 e 57 (133,9; 96,35); faixa; via (157,9; 99,0) a oeste do R39; L1 ao R39.2, ao R38.1 e ao C27.2. 44,1 mm | 2 |
| PA15 | via (131,0; 95,75); faixa; via (162,89; 102,34); L1 ao J12.2. 39,9 mm | 2 |
| BOOT0 | via (135,75; 95,35); faixa; via (150,9; 98,55) entre o R4 e o SW2.1; L1 ao R4.1 e, em Y 98,55 por baixo do SW2, aos dois pads SW2.2. 34,2 mm | 2 |
| I2C1_SCL | via (136,35; 96,15); faixa; sobe em X 150,15; leste em Y 89,75 até a via (157,85; 89,75), L1 pelo R13.2 até o J6.5; coluna X 157,2 até a via (157,2; 77,7) a leste do U4.4 | 3 |
| I2C1_SDA | via (137,0; 95,45); faixa; sobe em X 149,7; leste em Y 89,2; coluna X 156,4 com via (156,4; 88,5), L1 pelo R14.2 até o J6.6; via (155,325; 76,5) ao norte do U4.3 | 3 |
| /Power/+VBAT | R2.1, L1 até a via (143,175; 100,7) ao sul da faixa; L4 de 0,5 mm desce e vai a oeste em Y 109,5 até o J1.1 (pad passante). 25,3 mm | 1 |

- Faixa na L4: embaixo dos pads sul do U1, de norte a sul, SDA 97,06, SCL 97,44, BOOT0 97,82, PC2 98,2, PA15 98,58; diagonais de 45 graus entre a via do C1 (141,3; 97,6) e a via do M2_OUT (140,2; 100,8); a leste, Y 98,25, 98,7, 99,15, 99,6 e 100,05.
- Peças movidas: TP3 para (145,6; 97,3); R14 (pull-up do SDA) para (157,6; 87,675), rot 270; R13 (SCL) para (159,2; 90,575), rot 90. Referências do J6 para (159,0; 93,9) e do SW1 para (153,84; 84,25), na horizontal.
- Também: via de GND (148,6; 97,35) para o R3.2, o C26.2 e o R4.2 (a faixa ocupa a L4 embaixo deles); vias de +3V3 nos dois pads SW2.1 (151,965; 93,1 e 101,2) e nos pull-ups (158,2; 91,4 e 158,6; 86,85).
- Folgas abaixo de 0,25 mm: linhas embaixo dos pads sul 0,18; PA15 contra a via do BUZZER 0,17; VBAT_SENSE contra o NRST na saída do pino 8 cerca de 0,19; grupo de vias BOOT0, SCL e SDA 0,2.
- Risco: as vias do BOOT0, do SCL e do SDA, com as duas de +3V3 dos pinos 1 e 64, abrem na L2 uma fenda de cerca de 3,7 mm sob o U1. Só sinais lentos passam por cima [inferência].
- Pendentes: GPS_TX e GPS_RX sem caminho até o J6 (a faixa sob os pads sul está cheia); via de GND do R39.1 e do C27.1; CURR_IN (R38.2 ao J12.3). Para o SD_CD (pino 2) sobra a L4 em Y 94,75 (entre o VBAT_SENSE e as vias do sul); o PB7 (pino 59) sai em L1 para o norte em X 135,1.

### Lado oeste (pinos 33 a 48)


| Pino    | Rede                      | Vai para                                   | Sugestão                                                                                                                                  |
| ------- | ------------------------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| 33 a 36 | SPI2 NSS, SCK, MISO, MOSI | J9.3 a J9.6 (121,18 a 128,8; 70,09)        | 19 mm para o norte. L1 é possível pelo noroeste do U1, mas o USB e os pull-ups do SDIO ocupam essa região: provavelmente L4 [inferência]. |
| 37, 38  | GPS_TX, GPS_RX            | J6.3, J6.4 (161,4; 92,25 e 91,0)           | 33 mm até o leste: via junto do pino (ou para dentro), L4.                                                                                |
| 39, 40  | SDIO_D0, SDIO_D1          | passo 6                                    | L1                                                                                                                                        |
| 41      | PA8 (MCO1)                | TP1 (126,3; 92,25, baixo)                  | 2 mm para oeste e via no pad do TP1.                                                                                                      |
| 42      | VBUS_DET                  | R11.1 (126,9; 78,62), R10.2 (125,1; 76,97) | Lento: L4.                                                                                                                                |
| 43      | PA10 (AUX3)               | R37.1 (135,2; 74,83)                       | Lento, longe: para dentro, via, L4.                                                                                                       |
| 44, 45  | USB_D-, USB_D+            | U3.4, U3.6                                 | passo 7                                                                                                                                   |
| 46      | SWDIO                     | J2.4 (151,84; 70,61)                       | 34 mm até o nordeste: para dentro, via, L4.                                                                                               |
| 47      | VCAP_2                    | C12                                        | passo 2                                                                                                                                   |
| 48      | +3V3                      | C5                                         | passo 2                                                                                                                                   |


### Lado sul (pinos 49 a 64)


| Pino    | Rede                 | Vai para                            | Sugestão                                                                                                                                                                                                                                                                                           |
| ------- | -------------------- | ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 49      | SWCLK                | J2.2 (146,76; 70,61)                | Para dentro, via, L4 (libera o corredor do SDIO).                                                                                                                                                                                                                                                  |
| 50      | PA15                 | J12.2 (164,61; 102,34)              | Para dentro, via, L4 (libera o corredor do SDIO).                                                                                                                                                                                                                                                  |
| 51 a 54 | SDIO D2, D3, CK, CMD | passo 6                             | L1                                                                                                                                                                                                                                                                                                 |
| 55      | SWO                  | J2.6 (156,92; 70,61)                | Para dentro, via, L4.                                                                                                                                                                                                                                                                              |
| 56      | MOTOR1               | R17.1 (132,32; 101,2)               | Com o R17 na posição nova (passo 6), o pad MOTOR1 fica do lado do pino: o MOTOR1 desce do pino, vira para oeste abaixo das linhas SDIO (Y cerca de 100,35) antes do C2 (Y 100,775) e entra no pad por cima.                                                                                        |
| 57      | MOTOR2               | R24.1 (137,68; 100,8)               | Desce e vai para leste, entre o C6 e o C2, até entrar no R24.1 pelo oeste. L1.                                                                                                                                                                                                                     |
| 58      | BUZZER               | R28.1 (137,68; 102,6)               | **Cruza o MOTOR2** [conta]: em L1, o único caminho até o R28 é a passagem entre o C2 (X 136,45) e o R24 (X 137,275), de 0,825 mm, e o MOTOR2 atravessa essa passagem para entrar no R24.1. Proposta: BUZZER para dentro do U1, via, L4 e via junto do R28.1. O sinal é lento (PWM de 2,4 a 4 kHz). |
| 59      | PB7 (AUX2)           | R36.1 (133,4; 74,83)                | Vai para o norte, longe: para dentro, via, L4.                                                                                                                                                                                                                                                     |
| 60      | BOOT0                | R4.1 (149,7; 100,42), SW2.2         | passo 11                                                                                                                                                                                                                                                                                           |
| 61, 62  | I2C1_SCL, I2C1_SDA   | U4, R13, R14, J6 (leste e nordeste) | Para dentro, via, L4 (passo 10).                                                                                                                                                                                                                                                                   |
| 63      | GND                  | C6.2                                | passo 2                                                                                                                                                                                                                                                                                            |
| 64      | +3V3                 | C6.1                                | passo 2                                                                                                                                                                                                                                                                                            |


#### Sul, parte 1: motores 1 e 2 e buzzer (`ecb5421`, testado numa cópia, DRC sem violação nova)

| Rede | Camadas | Caminho | Vias |
| ---- | ------- | ------- | ---- |
| MOTOR1 | L1 | pino 56 desce até Y 99,95, diagonal até (133,35; 100,35), oeste até X 132,32 e entra no R17.1 por cima | 0 |
| M1_OUT | L1 | R17.2 desce em X 130,68 até Y 103,95, diagonal até (132,0; 105,27), desce em X 132,0 (a oeste do R30) até o J8.1; ramal até o R30.2 em Y 105,47 | 0 |
| MOTOR2 | L1 | pino 57 desce até Y 99,6, diagonal, leste em Y 99,97 entre o C6 e o C2 (folga 0,26 do C6.2), entra no R24.1 por cima | 0 |
| M2_OUT | L1, L4, L1 | R24.2 até a via em (140,2; 100,8); L4 desce em X 140,2 até Y 106,9, oeste em Y 107,2 (abaixo dos resistores), via em (135,7; 108,6); L1 até o J8.2 e sobe em X 135,7 (entre R31 e R32) até o R31.2 | 2 |
| BUZZER | L1, L4, L1 | via para dentro do U1 em (134,75; 96,4); L4 desce em X 134,75 até Y 99,5, diagonal até (137,3; 102,05), via ao sul do R28.1 em (137,68; 103,6) | 2 |
| Gate do Q1 | L1 | R28.2, leste em Y 101,9 abaixo do C26, do R4 e do SW2, desce em X 151,56 até o Q1.1; segue até X 156,2 e desce até o R29.2 | 0 |

Menor folga 0,25 mm (passo dos pinos do U1). O que isso reserva para depois:

- O SDIO do sul (pinos 51 a 54) tem que virar para oeste acima de Y 99,97 (o MOTOR1 passa em Y 100,35, e o SDIO pede 0,2 mm de folga).
- Os pinos 58 a 62 não saem para o sul em L1 (o MOTOR2 passa por baixo deles em Y 99,97): PB7, BOOT0 e I2C saem por via para dentro do U1.
- L1 em Y 101,9 de X 140 a 156,2 ocupada pelo gate do Q1: o BOOT0 até o SW2 passa acima (perto de Y 101,2).

## 6. SDIO (classe SDIO_50, 0,151 mm, L1)

AN4488 Rev 7, Seção 8.4.1, p.38 [manual]: referência em GND; 50 ohm ± 10%; skew entre dados e clock abaixo de 250 ps @ 10 mm; trilha abaixo de 120 mm; até 20 pF a 3,3 V; até 16 nH; "mismatch within data bus, data and CK or CK and CMD should be below 10mm"; "same number of vias between the data signals".


| Rede     | Pino U1            | Pull-up (pad do lado do sinal) | TP (baixo)         | J4                | Reta U1 ao J4 |
| -------- | ------------------ | ------------------------------ | ------------------ | ----------------- | ------------- |
| SDIO_D0  | 39 (128,32; 91,25) | R20.2 (122,9; 85,17)           | -                  | 7 (109,55; 89,81) | 18,8          |
| SDIO_D1  | 40 (128,32; 91,75) | R19.2 (124,6; 85,17)           | -                  | 8 (109,55; 88,75) | 19,0          |
| SDIO_D2  | 51 (131,25; 97,67) | R23.2 (124,6; 90,12)           | -                  | 1 (109,55; 96,41) | 21,7          |
| SDIO_D3  | 52 (131,75; 97,67) | R22.2 (122,9; 90,12)           | -                  | 2 (109,55; 95,31) | 22,3          |
| SDIO_CK  | 53 (132,25; 97,67) | sem pull-up                    | TP15 (123,9; 89,6) | 5 (109,55; 92,0)  | 23,4          |
| SDIO_CMD | 54 (132,75; 97,67) | R21.2 (126,3; 85,17)           | TP14 (124,0; 91,9) | 3 (109,55; 94,2)  | 23,5          |


Os outros pads do J4: 4 (109,55; 93,11) = +3V3_SD; 6 e 9 = GND (via para a L2); 10 = SD_CD (119,4; 99,04); as 4 abas SH = GND.

- [ ] Os contatos do J4 ficam na borda oeste (X 109,55), então as trilhas chegam neles passando por baixo do corpo do soquete, em L1. O footprint do KiCad não tem área proibida; conferir no desenho da Molex 104031 se há recomendação de não passar trilha por baixo [pendente, não conferido].
- [ ] Pull-up: passar a trilha pelo pad do resistor (em cadeia) quando o caminho permitir; se não, um ramal curto até o pull-up. Para o SDIO a 24 ou 48 MHz, um ramal de poucos mm até um pull-up de 10k tem efeito desprezível [inferência].
- [ ] Comprimentos: igualar dentro de 10 mm (manual). As linhas reta variam de 18,8 a 23,5 mm. D0/D1 saem do oeste e as demais do sul, então D0/D1 provavelmente ficam mais curtas: usar a ferramenta de ajuste de comprimento (atalho `7`, "Tune length") em D0/D1 só se a diferença passar de 10 mm.
- [ ] Eu meço os comprimentos depois (script) e digo a diferença.

### Saída sul (D2, D3, CK, CMD): R17 mudado (`995dbbf`)

Medida [conta]: entre a ponta dos pinos 49 a 54 (Y 98,445) e o R17 na posição atual (pads a partir de Y 99,225) sobram 0,78 mm, e cada linha SDIO precisa de 0,551 mm (0,151 mais 0,2 de clearance de cada lado). Cabe uma, e são quatro. Além disso, o MOTOR1 (pino 56) precisa ir para oeste até o R17.1 e cruza essas saídas. É a decisão 10.

Solução escolhida: **R17 de (131,5; 99,7) rot 0 para (131,5; 101,2) rot 180.**

- Teste numa cópia em 2026-11-02: DRC com 10 violações antes e 10 depois, nenhuma nova; não conectados 247 antes e depois; 54 trilhas e vias intactas. Folga de courtyard do R17 ao C2: 0,23 mm.
- O único aviso novo era de silk: a referência do C2 encostava no silk do R17. Com a referência do C2 em (135; 103,25), embaixo do C2, o aviso some.
- Corredor sob os pinos 49 a 54 passa a 2,28 mm (pads do R17 a partir de Y 100,725). As quatro linhas SDIO precisam de cerca de 1,6 mm (4 x 0,151 mais 5 x 0,2).
- Pads depois da mudança: MOTOR1 em (132,32; 101,2), do lado do pino 56; M1_OUT em (130,68; 101,2), segue ao sul para o R30 e o J8.1.
- Pinos 49 (SWCLK) e 50 (PA15) saem para dentro do U1, para não ocupar o corredor.

- [x] Aplicado em 2026-11-02 (`995dbbf`): R17 em (131,5; 101,2) rot 180; referência do C2 em (135; 103,25). DRC igual ao da cópia (15 violações, 241 não conectados). Falta a sua revisão visual.

Alternativas descartadas: levar D2, D3, CK e CMD por L4 (exigiria vias também em D0 e D1, pela regra "same number of vias between the data signals"); descer só o CMD entre o R17 e o C2 (as outras três continuariam sem saída).

### W1: SDIO sul aplicado (`c63db33`, 2026-11-17, testado numa cópia, DRC igual ao do repositório: 6 violações antigas, 119 para 113 não conectados)

**Correção do plano acima.** "Tudo em L1, sem vias, retas" não é possível. De cima para baixo, os pinos saem em D2 (51), D3 (52), CK (53), CMD (54). No J4, de norte para sul, os pads são CK (Y 92,0), CMD (94,2), D3 (95,31), D2 (96,41). Como o feixe vem do sul, a ordem de cima para baixo precisaria ser CK, CMD, D3, D2: 5 dos 6 pares estão invertidos [conta]. O mínimo são duas linhas na L4: D2 e D3 saltam por baixo das outras. A regra do AN4488 8.4.1 é "mesmo número de vias entre os dados", não "zero vias": D2 e D3 ficaram com 2 vias, então **D0 e D1 recebem um salto simétrico de 2 vias na W2** [inferência: uma via a mais por linha é desprezível a 25 ou 50 MHz].

Caminho (largura 0,151 mm, cantos de 45 graus, tudo em L1 salvo os saltos):

| Trecho | Níveis (Y) e pontos |
| ------ | ------------------- |
| Saída dos pinos (passo 0,36 mm) | D2 98,75, D3 99,11, CK 99,47, CMD 99,83. Descem retos do pino e viram para oeste (o D2 a 0,2 mm da ponta dos pinos 49 e 50). O MOTOR1 (Y 100,35 a oeste de X 133,35) fica a 0,34 mm do CMD. |
| Afastamento (X 129,9 a 128,8) | D2 sobe para 98,4 (antes do D3, senão ficam a 0,25 mm), depois D3 99,0, CK 99,6, CMD 100,2 (passo 0,6 mm, para caber vias de 0,6 mm entre as linhas). |
| Salto do D2 | vias em (125,6; 98,4) e (125,6; 100,9), trecho de L4 em X 125,6. Volta à L1 abaixo do CMD. |
| Reajuste (X 125,2 a 124,7) | D3, CK e CMD sobem 0,5: D3 98,5, CK 99,1, CMD 99,7. |
| Salto do D3 | vias em (124,2; 98,5) e (124,2; 100,3), trecho de L4 em X 124,2. Volta entre o CMD e o D2. Ordem final de cima para baixo: CK 99,1, CMD 99,7, D3 100,3, D2 100,9. |
| Descida (X 123,2 a 120,8, em degraus de 45 graus, de baixo para cima) | CK 100,0, CMD 100,36, D3 100,72, D2 101,08 (passo 0,36). Passam **abaixo** dos pads 9 e 10 do J4 (Y 98,44 a 99,64) e do pad SH (120,38; 95,54), a 0,28 mm de folga. O C25 **não** precisou sair. |
| Subidas até o J4 | CK em X 114,3 até Y 92,0; CMD em X 113,5 até 94,2; D3 em X 112,7 até 95,31; D2 em X 111,9 até 96,41. Chegam horizontais aos pads em X 109,55. A linha mais ao norte sobe por último de leste, sem cruzar. |

- **TP15 (CK)** foi para (114,3; 95,0) e **TP14 (CMD)** para (113,5; 97,8), sobre as subidas, com via no pad (pads na face de baixo, sob o corpo do J4). As referências ficaram ocultas até a limpeza de silk (com elas visíveis dava `silk_overlap`).
- Comprimentos medidos: D2 29,64 mm, D3 30,75, CK 32,61, CMD 31,63. Vias: D2 2, D3 2, CK 1, CMD 1.
- J4.4 (+3V3_SD, 109,55; 93,11) ficou numa bolsa fechada entre as horizontais do CMD (94,2) e do CK (92,0), com a subida do CK (X 114,3) no lado leste: o +3V3_SD tem que entrar por L4 (via junto do pad).
- O pad 10 (SD_CD) e o pad 9 (GND) do J4 ficam acima das linhas (Y 98,44 a 99,64): acessíveis pelo norte, dentro do corpo, ou pelo sul se sobrar espaço.
- **Parede da L4 a oeste do U1 (achado):** M4_OUT (X 126,0 e 127,6) e M3_OUT (X 126,75 e 128,1), mais MOTOR3 e MOTOR4 em Y 89,3 e 89,9, fecham a L4 entre Y 79 e 101. O corredor sul da L4 (Y 106 a 109) também está fechado em X 135,7 (M2_OUT, via em (135,7; 108,6) e +VBAT em Y 109,5). Por isso o SD_CD (pino 2) e o SD_EN (pino 11), que saem pelo leste, não chegam ao oeste pela L4 sem mudar algo. Decisão em aberto (W4): trocar o SD_CD com o PB12 (pino 33, SPI2_NSS, sem perda real) e ver o SD_EN, ou mover o M2/M3/M4_OUT. O SPI2 nos pads J9 fica (decisão do Gabriel).

### TP14 e TP15 estão na face de baixo

"SDIO sem vias" e "TP passando pelo pad, sem ramal" só convivem assim [inferência]: a trilha segue em L1 e passa por cima de uma via colocada no centro do pad do TP (via no pad do TP; o TP não recebe componente, então não há problema de solda). A linha não troca de camada; o único efeito é o stub da via na espessura da placa (1,56 mm), desprezível para o SDIO. Isso coloca uma via no CK e no CMD, mas não nos dados, então a regra do manual (vias iguais entre os dados) continua atendida.

## 7. USB (classe USB_90)

AN4879 Rev 12, Seção 2.3, Tabela 11 [manual]: ESD (U3) o mais perto possível do receptáculo. 90 ohm diferencial: calculadora da JLCPCB, 0,154 / 0,203 mm [manual]. Ferramenta de par diferencial: atalho `6`.


| Trecho                        | De                   | Para                  | Nota                                                                                                                                       |
| ----------------------------- | -------------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Junção dos lados do USB-C, D+ | J3.A6 (115,2; 80,35) | J3.B6 (115,2; 81,35)  | O J3.A7 (D-) fica entre os dois. Um dos pares precisa de via ou de contornar por fora dos pads [prática de projeto, padrão de todo USB-C]. |
| Junção dos lados, D-          | J3.B7 (115,2; 79,85) | J3.A7 (115,2; 80,85)  | idem                                                                                                                                       |
| Conector ao ESD, D+           | J3 (USB_CONN_D+)     | U3.1 (119,55; 81,44)  | Curto.                                                                                                                                     |
| Conector ao ESD, D-           | J3 (USB_CONN_D-)     | U3.3 (121,45; 81,44)  | O U3.3 fica do lado leste: contornar o U3 por baixo (Y acima de 82,1).                                                                     |
| ESD ao MCU, D-                | U3.4 (121,45; 79,16) | U1.44 (128,32; 93,75) | cerca de 16 mm                                                                                                                             |
| ESD ao MCU, D+                | U3.6 (119,55; 79,16) | U1.45 (128,32; 94,25) | cerca de 17,5 mm                                                                                                                           |


- [ ] Cruzamento com o SDIO D0/D1 (que vão do oeste do U1 até os pull-ups em Y 85,17): o par passa por baixo em L4, com duas vias simétricas por linha (proposta do `ROTEAMENTO.md`) [inferência]. O stackup é simétrico, então 0,154 / 0,203 em L4 com referência na L3 também dá cerca de 90 ohm.
- [ ] Ordem das linhas: saindo do U3 para o sul e virando para leste até o U1, o D- (lado leste no U3) termina ao norte, como o pino 44 [conta, conferir no KiCad].
- [ ] VBUS_RAW (classe Power, 0,5 mm): J3.A4/B9 (78,15) e J3.A9/B4 (83,05) ao U3.5 (120,5; 79,16), C17.2 (124,08; 82), R12.1 (123,3; 78,62), R10.1 (125,1; 78,62) e D4.2 (127,15; 74,0).
- [ ] CC: J3.A5 ao R8.1 (119,4; 76,12); J3.B5 ao R9.1 (121,2; 76,12). Classe Default.
- [ ] Abas SH do J3: GND direto (decisão 1), via para a L2 junto de cada aba.
- [ ] U3.2 (GND): via para a L2 colada no pad (o caminho de terra do ESD precisa ser curto) [inferência].

## 8. SPI1 até a IMU (U5)

ES0182 Rev 19, Seção 2.12.4 [manual]: SCK curto, só com a IMU, sem capacitor. TPs passando pelo pad (decisão 11). Os TPs ficam na face de baixo.

**Plano testado numa cópia em 2026-11-02** (esboço completo, DRC sem violação nova, todas as linhas ligadas). Os TPs já estão nas posições abaixo (`2e5894d`); as trilhas são suas. Imagem do esboço fora do repositório.

Por que três linhas em L4: andando em volta de cada CI no mesmo sentido, a ordem dos pinos do U1 (MOSI, MISO, SCK, CS, INT1) e a do U5 não casam em mais de um ponto [conta]. A nota antiga de "um cruzamento só" não se confirma. A L4 resolve sem custo para o SPI (não há regra de número de vias), e nas linhas em L4 a trilha passa direto sobre o pad do TP, sem via a mais.

| Rede | Pino U1 | Pino U5 | Caminho | Vias | TP (baixo) | Comprimento |
| ---- | ------- | ------- | ------- | ---- | ---------- | ----------- |
| SPI1_SCK | 21 (135,75; 86,33) | 13 (136,76; 81,0) | L1: sobe em X 135,75 entre o C21 e o C4 até Y 83,25, leste até X 138,3, sobe até Y 81,0, oeste até o pino | 1 (a do TP) | TP12 (137,0; 83,25), via no pad | 9,4 mm |
| IMU_INT1 | 17 (137,75; 86,33) | 4 (135,0; 79,74) | L1: sai do pino para leste em Y 86,33 até X 139,3, sobe até Y 77,9, oeste até X 135,0, desce ao pino | 1 (a do TP) | TP9 (139,3; 82,5), via no pad | 16,1 mm |
| SPI1_IMU_CS | 20 (136,25; 86,33) | 12 (136,76; 81,5) | via para dentro do U1 em (135,8; 88,5); L4 sobe em X 135,8 até Y 81,95, leste até a via (137,65; 81,95); L1 ao pino | 2 | TP11 (135,8; 88,5), na via de dentro | 11,7 mm |
| SPI1_MISO | 22 (135,25; 86,33) | 1 (136,5; 79,74) | via para dentro em (135,15; 87,65); L4 sobe em X 135,15 até Y 78,85, leste até a via (136,5; 78,85); L1 desce ao pino | 2 | TP8 (135,15; 80,0), na trilha da L4 | 12,4 mm |
| SPI1_MOSI | 23 (134,75; 86,33) | 14 (136,76; 80,5) | via para dentro em (134,3; 88,45); L4 em X 133,5 (a oeste das vias do C21) até Y 78,2, leste até X 137,65, desce até a via (137,65; 79,95); L1 ao pino | 2 | TP10 (133,5; 86,3), na trilha da L4 | 19,8 mm |

- As vias para dentro do U1 ficam desencontradas (pinos 20, 22 e 23 são vizinhos, e a via do pino 19 já está em (136,75; 87,6)). As distâncias foram conferidas pelo DRC; se mudar uma, conferir de novo.
- Na L4, CS (X 135,8) e MISO (X 135,15) correm lado a lado; o TP de cada um fica onde o outro não passa.
- O SCK em L1 e o CS em L4 se sobrepõem na vista de cima, mas ficam em camadas separadas pelos planos L2 e L3.
- Pinos do U5 sem ligação: 2, 3, 9, 10 e 11 (sem rede).

**Risco (planejar antes do lado norte):** o laço do INT1 em L1 e a linha do MOSI em L4 fecham a passagem direta para leste. Os pinos 24 a 30 do U1 (LED_GREEN, LED_YELLOW, MOTOR3, MOTOR4, BOOT1, ELRS_TX, ELRS_RX) saem pelo norte; LEDs e ELRS vão para leste e precisam passar ao norte do U5, na faixa de cerca de 2 mm entre Y 75,8 (J10) e Y 77,8 (topo do INT1) em L1, ou acima de Y 78 em L4 [conta]. As vias do C20 em X 132,78 ocupam parte do corredor a oeste.

## 9. Alimentação por trilha (classe Power, 0,5 mm)

O +3V3 vai pelo plano da L3 (passo 0). Só estas redes vão por trilha:


| Rede           | Origem                | Destinos                                                                                                                                                                                                                                                     | Sugestão                                                                                                                                        |
| -------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| +5V            | J1.4 (116,44; 110,83) | C16.2 (117,7; 107,88); U6.1 e C22.1; U2.1, U2.3 e C9.1 (LDOs, Y cerca de 102); D4.1 (123,85; 74,0, USB); J10.2 (140,84; 74,5); D1, D2, D3 pino 2 (144,54; 77,4 a 82,2); J5.2 (161,4; 80,41); J6.2 (161,4; 93,5); J7.1 (145,89; 110,91), R27.1, D5.1 (buzzer) | Tronco curto em L1 do J1 ao C16 e aos LDOs. Para o resto da placa, tronco em L4 [inferência]. Nas trocas de camada, 2 vias por ponto [projeto]. |
| +3V3_SD        | U6.5 (116,64; 101,75) | C23.1 (118,4; 101,92), TP13 (121; 101, baixo), C25.1 (122,12; 97,6), C24.1 (123,25; 93,3), pull-ups R19 a R23 pino 1 (122,9 a 126,3; 86,83 e 88,47), J4.4 (109,55; 93,11)                                                                                    | L1. O C25 (100 nF) é o capacitor junto do soquete (Kingston SDCS2 / [projeto]).                                                                 |
| /USB/VBUS_RAW  | J3                    | passo 7                                                                                                                                                                                                                                                      | L1                                                                                                                                              |
| /Power/+VBAT   | J1.1 (129,04; 110,83) | R2.1 (143,18; 98,6)                                                                                                                                                                                                                                          | Corrente quase nula (divisor), mas a classe pede 0,5 mm. L1 ou L4.                                                                              |
| /Buzzer/BZ_NEG | J7.2 (148,43; 110,91) | Q1.3 (153,44; 106,6), D5.2 (154,65; 110,6), R27.2 (148,03; 106,6)                                                                                                                                                                                            | L1, lado a lado com o +5V do buzzer, curtos (laço chaveado pequeno) [inferência].                                                               |
| +12V           | J1.2 (124,84; 110,83) | nenhum                                                                                                                                                                                                                                                       | Sem ligação na placa.                                                                                                                           |


- [ ] Q1.2 (GND) e R29.1: vias para a L2. Gate: R28.2 (139,32; 102,6) ao Q1.1 (151,56; 105,65) e ao R29.2 (156,2; 105,78), classe Default.

## 10. Sinais lentos em L4

L4 tem a L3 como referência. Todos em classe Default, 0,2 mm.


| Rede                  | De                                  | Para                                                           | Reta        |
| --------------------- | ----------------------------------- | -------------------------------------------------------------- | ----------- |
| GPS_TX, GPS_RX        | U1.37, 38 (oeste)                   | J6.3, J6.4 (161,4; 92,25 e 91,0)                               | 33          |
| ELRS_TX, ELRS_RX      | U1.29, 30 (norte)                   | J5.3, J5.4 (161,4; 79,16 e 77,91)                              | 31          |
| I2C1_SCL              | U1.61 (sul)                         | R13.2 (151,4; 76,58), U4.4 (155,97; 78,2), J6.5 (161,4; 89,75) | 26 a 28     |
| I2C1_SDA              | U1.62 (sul)                         | R14.2 (151,4; 80,17), U4.3 (155,32; 78,2), J6.6 (161,4; 88,5)  | 23 a 27     |
| M3_OUT                | R25.2 (133,1; 82,67)                | R32.2 (136,6; 105,47), J8.3 (137,57; 110,91)                   | cerca de 28 |
| M4_OUT                | R26.2 (129,0; 81,78)                | R33.2 (138,4; 105,47), J8.4 (140,11; 110,91)                   | cerca de 30 |
| M1_OUT, M2_OUT        | R17.2, R24.2                        | R30.2, R31.2, J8.1, J8.2                                       | curtas, L1  |
| UART4_TX, RX          | U1.14, 15                           | J10.3, J10.4                                                   | 15          |
| SPI2 x4               | U1.33 a 36                          | J9.3 a J9.6                                                    | 19          |
| LEDs                  | U1.9, 24, 25                        | R5.2, R7.2, R6.2 (148,43; 82,2 / 77,4 / 79,8)                  | 13 a 17     |
| AUX                   | U1.16 (PA2), 59 (PB7), 43 (PA10)    | R35.1, R36.1, R37.1 (131,6 a 135,2; 74,83)                     | 16 a 23     |
| SWD                   | U1.46 (SWDIO), 49 (SWCLK), 55 (SWO) | J2.4, J2.2, J2.6 (borda norte)                                 | 32 a 36     |
| PA15, PC2, PC14, PC15 | U1.50, 10, 3, 4                     | J12, R38/R39/C27, J13                                          | 10 a 34     |
| SD_CD, SD_EN          | U1.2, 11                            | R18 e J4.10; U6.3 e R15                                        | 15 a 32     |


- [ ] I2C: contornar o oscilador pelo sul e pelo leste (`ROTEAMENTO.md` 4.7). Em L4, embaixo da ilha (com a L2 da ilha no meio), também serve [inferência], mas contornar é mais conservador.
- [ ] Os resistores série dos AUX (R35 a R37) já ficam junto do J14: o trecho do pad do resistor ao J14 é curto em L1.

## 11. NRST e BOOT0

**NRST** (pino 7, 139,68; 92,75): destinos C15.1 (148,8; 87,78), SW1.2 (155,72; 91,8 e 85,8) e J2.5 (154,38; 70,61).

- [ ] Proposta nova: trilha curta do pino para dentro do U1, via sob o corpo, L4 até perto do C15, via e L1 até o C15.1, ao SW1 e ao J2.5. A ordem "pino, C15, SW1, J2" é [projeto]; o DS8626 não dá distância.
- [ ] O caminho antigo (L1 subindo em X ≈ 140,5) não cabe: sobram 0,245 mm entre a ponta dos pads e o vão [conta].

**BOOT0** (pino 60, 135,75; 97,67): destinos R4.1 (149,7; 100,42) e SW2.2 (155,72; 100,2 e 94,2).

- [ ] Para dentro ou para baixo, L4 até o R4, via e L1 ao SW2. SW2.1 (+3V3): via para a L3.

**BOOT1** (pino 28) ao R16.1 (131,0; 80,33): passo 5, lado norte.

## 12. Fechamento

- [ ] Preenchimento de GND em L1 e L4 com vias de costura para a L2 (AN4488 Figura 21, "+ GND" nas camadas externas) [projeto]. Inclui o cobre de GND em volta do U2 e do U6 (decisão 13).
- [ ] Ao criar zona de GND em F.Cu: não cobrir a ilha do oscilador por cima da `HSE_GND_POUR` (ela já é a zona local) e manter a zona longe dos pinos 5 e 6.
- [ ] Reencher (`B`) e rodar o DRC.
- [ ] Revisar a posição dos TPs.

## 13. O que eu confiro ao fim de cada passo (só leitura)

- DRC numa cópia e comparação com a referência.
- Vias: distância ao pad pelo padrão do passo 0 (0,82 / 1,12 / 1,35 / 1,27 mm), folga e degraus deixados pelo mouse; proponho a padronização e, com o KiCad fechado e teste na cópia, aplico.
- Larguras por classe (inclusive o neckdown e trechos Power finos esquecidos).
- Vias de GND dentro do vão da ilha e trilhas de L1 cruzando o vão.
- SDIO: comprimento de cada linha, diferença entre elas e número de vias.
- USB: comprimento e diferença entre D+ e D-.
- Ramais (stubs) nos TPs do SPI1 e do SDIO.

## Pontos abertos levantados neste documento

1. Resolvido (`995dbbf`): saída sul do SDIO. R17 em (131,5; 101,2) rot 180 e referência do C2 em (135; 103,25).
2. NRST: o caminho de L1 não cabe; nova proposta por L4 (passo 11). Já corrigido no `ROTEAMENTO.md`.
3. BUZZER (pino 58) cruza o MOTOR2 (pino 57) na passagem entre o C2 e o R24: BUZZER por dentro do U1 e L4 (passo 5, lado sul).
4. Resolvido (2026-11-02, exceção aceita): o C8.1 fica em cima da perna norte do vão e a trilha +3.3VA cruza o vão; alimentação filtrada, risco baixo [inferência] (passo 3).
5. C1.2 (GND) também fica em cima da perna sul: a via vai ao sul, Y 97,4 ou mais (passo 2).
6. TPs do SDIO e do SPI1 na face de baixo: via no pad do TP, sem trocar a trilha de camada (passos 6 e 8) [inferência]. TP14 e TP15 já estão sobre as subidas do CMD e do CK, sob o corpo do J4 (W1, `c63db33`).
9. W2 (D0 e D1): D0 e D1 saem do oeste e ficam com cerca de 20 a 22 mm [conta, sem rotear] contra 30 a 33 mm das linhas do sul. O AN4488 8.4.1 pede menos de 10 mm de diferença entre dados e CK: serpentina de pelo menos 10 mm em cada um (corredor Y 90,6 a 92,7), mais o salto simétrico de 2 vias em cada.
10. Ramais dos pull-ups (R19 a R23) ainda sem ligação: de 6 a 15 mm das linhas. Decisão do Gabriel: manter e medir a capacitância no fim (limite 20 pF, AN4488 8.4.1).
11. J4.4 (+3V3_SD) entra por L4; J4.10 (SD_CD) e J4.9 (GND) pelo norte (W4).
12. SD_CD e SD_EN: parede da L4 (ver W1 acima). Opções: SD_CD no PB12; SD_EN por PA8 (perde o TP de clock MCO1) ou mover o M2/M3/M4_OUT..
7. Área proibida embaixo do J4: conferir no desenho da Molex (passo 6).
8. SPI1, folgas de 0,15 mm (2026-11-02, `dd3ddef`, decisão do Gabriel: deixar para depois). Tudo passa no DRC; são pontos que dá para folgar se sobrar espaço:
   - INT1 junto das vias do MISO (136,5; 78,85) e do MOSI (137,65; 79,95): subir o trecho de cima de Y 78,3 para 77,9. **Decidir junto com o lado norte:** subir o INT1 come a faixa por onde LEDs e ELRS passam ao norte do U5.
   - MOSI (L4) junto da via do MISO: horizontal de Y 78,3 para 78,1.
   - MOSI (L4) junto do TP8: subir em X 133,5 até Y 79,0 antes da diagonal.
   - Saídas do U1: MOSI junto da via do MISO (0,15) e CS junto do pad 21 (0,18); voltar a uma diagonal única do pad à via dá cerca de 0,23.
   - CS (L4) junto do TP12 e SCK junto da via do CS: manter (mexer exige deslocar o TP12).
   Os casos de 0,25 a 0,275 mm na saída dos pinos do U1 e do U5 vêm do passo de 0,5 mm e não mudam.

