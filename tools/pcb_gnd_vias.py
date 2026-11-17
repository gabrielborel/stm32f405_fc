"""Liga pads de GND ao plano GND_L2 com uma trilha curta e uma via. Grava no arquivo dado. SO PARA USAR EM COPIA.

Para cada pad de GND sem ligacao ao plano, procura a celula livre mais perto (ate 4 mm de trilha) onde uma via cabe e liga
o pad a ela. Usa os mesmos mapas de obstaculos do pcb_router.py (folga 0,2 mm, trilha de 0,2 mm, via de 0,6 / 0,3 mm,
centros de vias a pelo menos 0,8 mm) e acrescenta a regra de que o centro da via fica a pelo menos 0,5 mm de QUALQUER pad
(inclusive de GND), para nao cair em cima de pad vizinho.

Uso: PY tools/pcb_gnd_vias.py ARQUIVO.kicad_pcb [REF PAD ...]
Sem REF PAD, acha sozinho os pads de GND que nao chegam ao plano. Depois: reencher GND_L2 e 3V3_L3, rodar o DRC.
Variaveis de ambiente (padroes GND, GND_L2, 0.2): PLANE_NET, PLANE_ZONE, PLANE_W. Ex.: PLANE_NET=+3V3 PLANE_ZONE=3V3_L3 PLANE_W=0.5
"""
import os, sys, math, heapq
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew
from pcb_router import Router, mm, M, FC, BC, G

NET = os.environ.get("PLANE_NET", "GND"); ZONE = os.environ.get("PLANE_ZONE", "GND_L2"); W = float(os.environ.get("PLANE_W", "0.2"))
MAXLEN = float(os.environ.get("GND_MAXLEN", "4.0"))   # mm de trilha ate a via (variavel GND_MAXLEN)
PAD_VIA = 0.5  # mm: centro da via a esta distancia de qualquer pad


def pads_sem_plano(b):
    zs = [z for z in b.Zones() if z.GetZoneName() in ("GND_L2", "3V3_L3")]
    pcbnew.ZONE_FILLER(b).Fill(zs)
    b.BuildConnectivity(); cn = b.GetConnectivity()
    gnd = b.FindNet(NET).GetNetCode(); out = []
    for f in b.GetFootprints():
        for p in f.Pads():
            if p.GetNetCode() != gnd: continue
            seen = {p.m_Uuid.AsString()}; todo = [p]; ok = False
            while todo and not ok:
                it = todo.pop()
                for n in cn.GetConnectedItems(it):
                    u = n.m_Uuid.AsString()
                    if u in seen: continue
                    seen.add(u)
                    if n.Type() == pcbnew.PCB_ZONE_T:
                        if n.GetZoneName() == ZONE: ok = True; break
                        continue
                    todo.append(n)
            if not ok: out.append(p)
    return out


class GndVias(Router):
    def prepara(self):
        self.build(NET, W)
        nx = self.nx
        for fp in self.b.GetFootprints():
            for p in fp.Pads():
                if not (p.IsOnLayer(FC) or p.IsOnLayer(BC)): continue
                r = p.GetBoundingBox(); a, b_, c, d = mm(r.GetX()), mm(r.GetY()), mm(r.GetRight()), mm(r.GetBottom())
                i0, j0 = self.idx(a - PAD_VIA, b_ - PAD_VIA); i1, j1 = self.idx(c + PAD_VIA, d + PAD_VIA)
                for j in range(max(j0, 0), min(j1, self.ny - 1) + 1):
                    for i in range(max(i0, 0), min(i1, nx - 1) + 1):
                        x, y = self.xy(i, j)
                        if math.hypot(max(a - x, 0, x - c), max(b_ - y, 0, y - d)) < PAD_VIA: self.vblk[j * nx + i] = 1

    def marca_via(self, x, y):
        nx = self.nx; R = 0.8
        i0, j0 = self.idx(x - R, y - R); i1, j1 = self.idx(x + R, y + R)
        for j in range(max(j0, 0), min(j1, self.ny - 1) + 1):
            for i in range(max(i0, 0), min(i1, nx - 1) + 1):
                if math.hypot(self.xy(i, j)[0] - x, self.xy(i, j)[1] - y) < R: self.vblk[j * nx + i] = 1

    def liga(self, pad):
        l0 = FC if pad.IsOnLayer(FC) else BC; k = 0 if l0 == FC else 1
        nx = self.nx; blk = self.blk[k]
        starts = self.pad_nodes(pad, l0)
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        pq = []; best = {}; prev = {}; cnt = 0
        for s in starts:
            best[s] = 0; cnt += 1; heapq.heappush(pq, (0, cnt, s))
        goal = None
        while pq:
            g, _, s = heapq.heappop(pq)
            if best.get(s, 1e18) < g - 1e-9: continue
            i, j, _k = s
            if s not in starts and not self.vblk[j * nx + i]: goal = s; break
            if g > MAXLEN: continue
            for di, dj in dirs:
                ni, nj = i + di, j + dj
                if not (0 <= ni < self.nx and 0 <= nj < self.ny): continue
                ns = (ni, nj, k)
                if blk[nj * nx + ni] and ns not in starts: continue
                ng = g + math.hypot(di, dj) * G
                if ng < best.get(ns, 1e18):
                    best[ns] = ng; prev[ns] = s; cnt += 1; heapq.heappush(pq, (ng, cnt, ns))
        if goal is None: return None
        path = [goal]
        while path[-1] in prev: path.append(prev[path[-1]])
        path = path[::-1]
        c0 = (mm(pad.GetPosition().x), mm(pad.GetPosition().y)); gx, gy = self.xy(goal[0], goal[1])
        items, _ = self.to_items(path, c0, (gx, gy), NET, l0, l0)
        L = sum(math.dist(a, b_) for kk, pts in items for a, b_ in zip(pts[:-1], pts[1:]))
        self.add(NET, items, [(gx, gy)], W)
        self.marca_via(gx, gy)
        return L, (gx, gy)


if __name__ == "__main__":
    path = sys.argv[1]; args = sys.argv[2:]
    r = GndVias(path)
    if args:
        pads = []
        for i in range(0, len(args), 2):
            pads += [p for p in r.b.FindFootprintByReference(args[i]).Pads() if p.GetNumber() == args[i + 1]]
    else:
        pads = pads_sem_plano(r.b)
    print(len(pads), "pads de %s sem ligacao ao plano" % NET, flush=True)
    r.prepara(); falhou = 0
    for p in pads:
        f = p.GetParentFootprint(); res = r.liga(p)
        nome = "%s.%s" % (f.GetReference(), p.GetNumber())
        if res is None: print("SEM LUGAR PARA A VIA:", nome, flush=True); falhou += 1
        else: print("%s: trilha %.2f mm, via em (%.2f; %.2f)" % (nome, res[0], res[1][0], res[1][1]), flush=True)
    r.b.Save(path); print("salvo; sem via:", falhou)
