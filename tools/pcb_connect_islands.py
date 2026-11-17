"""Liga as ilhas de uma rede (sem plano) com o roteador A*, de duas em duas, pelo par de pads mais perto. Grava no arquivo dado.
SO PARA USAR EM COPIA.

Uso: PY tools/pcb_connect_islands.py ARQUIVO.kicad_pcb REDE LARGURA_MM
Ex.: PY tools/pcb_connect_islands.py COPIA.kicad_pcb +5V 0.5
Acha as ilhas (pads, trilhas e vias ligados entre si), e enquanto houver mais de uma tenta ligar o par de pads mais perto
entre ilhas diferentes; se o roteador nao achar caminho, tenta o proximo par. Depois: reencher GND_L2 e 3V3_L3 e rodar o DRC.
"""
import os, sys, math, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew
from pcb_router import Router, mm

path, net, w = sys.argv[1], sys.argv[2], float(sys.argv[3])
r = Router(path); b = r.b
b.BuildConnectivity(); cn = b.GetConnectivity()
code = b.FindNet(net).GetNetCode()
pads = [(f, p) for f in b.GetFootprints() for p in f.Pads() if p.GetNetCode() == code]
cl = {}; nid = 0
for f, p in pads:
    k = p.m_Uuid.AsString()
    if k in cl: continue
    seen = {k}; todo = [p]; cl[k] = nid
    while todo:
        it = todo.pop()
        for n in cn.GetConnectedItems(it):
            u = n.m_Uuid.AsString()
            if u in seen: continue
            seen.add(u)
            if n.Type() == pcbnew.PCB_ZONE_T: continue
            cl[u] = nid; todo.append(n)
    nid += 1
cid = {p.m_Uuid.AsString(): cl[p.m_Uuid.AsString()] for f, p in pads}
print("%s: %d pads em %d ilhas" % (net, len(pads), nid), flush=True)
falhas = set(); ok = 0
while len(set(cid.values())) > 1:
    cand = []
    for (f1, p1), (f2, p2) in itertools.combinations(pads, 2):
        a, c = cid[p1.m_Uuid.AsString()], cid[p2.m_Uuid.AsString()]
        if a == c or (min(a, c), max(a, c)) in falhas: continue
        q1, q2 = p1.GetPosition(), p2.GetPosition()
        cand.append((math.hypot(mm(q1.x - q2.x), mm(q1.y - q2.y)), f1, p1, f2, p2))
    if not cand: break
    cand.sort(key=lambda t: t[0])
    d, f1, p1, f2, p2 = cand[0]
    a, c = cid[p1.m_Uuid.AsString()], cid[p2.m_Uuid.AsString()]
    if r.route(net, f1.GetReference(), p1.GetNumber(), f2.GetReference(), p2.GetNumber(), w):
        ok += 1
        for k in cid:
            if cid[k] == c: cid[k] = a
    else:
        falhas.add((min(a, c), max(a, c)))
r.b.Save(path); print("ligacoes feitas: %d; ilhas que sobraram: %d" % (ok, len(set(cid.values()))))
