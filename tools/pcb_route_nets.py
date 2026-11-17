"""Roteia uma ou mais ligacoes com o roteador A* (tools/pcb_router.py) e grava no arquivo. SO EM COPIA.

Uso: PY tools/pcb_route_nets.py ARQUIVO.kicad_pcb REDE REF1 PAD1 REF2 PAD2 [REDE REF1 PAD1 REF2 PAD2 ...]
Exemplo: PY tools/pcb_route_nets.py COPIA.kicad_pcb GPS_TX U1 37 J6 3 GPS_RX U1 38 J6 4
Depois: reencher GND_L2 e 3V3_L3 (nao a HSE_GND_POUR), rodar o DRC e comparar com a referencia.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pcb_router import Router
path, args = sys.argv[1], sys.argv[2:]
if len(args) % 5 != 0:
    sys.exit("argumentos: REDE REF1 PAD1 REF2 PAD2 (repetidos)")
r = Router(path); ok = []
for i in range(0, len(args), 5):
    ok.append(r.route(*args[i:i+5]))
r.b.Save(path)
print("salvo", ok)
