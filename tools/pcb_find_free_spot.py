"""Procura a posicao livre (sem sobrepor courtyards) mais perto de um alvo. Somente leitura.
Nao grava nada: imprime as posicoes e salva um moves.json para o pcb_apply_moves.py.

Uso: PY tools/pcb_find_free_spot.py ARQUIVO.kicad_pcb plano.json saida_moves.json
plano.json: lista de {"ref": "R17", "target": [x, y], "padnet": "MOTOR1", "rots": [0, 90],
                      "win": [x0, y0, x1, y1]}
  target = onde o pad indicado por padnet deve ficar perto (ex.: pino do MCU)
  win    = janela de busca, em mm
As pecas do plano sao colocadas em ordem; cada uma passa a ocupar espaco para as seguintes.
Margem da borda e folga entre courtyards: constantes abaixo.
"""
import json
import math
import sys
import pcbnew

mm, fm = pcbnew.ToMM, pcbnew.FromMM
board = pcbnew.LoadBoard(sys.argv[1])
plan = json.load(open(sys.argv[2]))
out = sys.argv[3]

edge_bb = board.GetBoardEdgesBoundingBox()
EDGE = (mm(edge_bb.GetLeft()), mm(edge_bb.GetTop()), mm(edge_bb.GetRight()), mm(edge_bb.GetBottom()))
MARGIN, GAP, STEP = 0.9, 0.15, 0.1


def bbox(f):
    r = f.GetCourtyard(pcbnew.F_CrtYd).BBox()
    if r.GetWidth() == 0:
        r = f.GetBoundingBox(False)
    return (mm(r.GetLeft()), mm(r.GetTop()), mm(r.GetRight()), mm(r.GetBottom()))


def overlaps(a, c):
    return not (a[2] + GAP <= c[0] or c[2] + GAP <= a[0] or a[3] + GAP <= c[1] or c[3] + GAP <= a[1])


moving = {p["ref"] for p in plan}
occupied = {}
for f in board.GetFootprints():
    if f.GetReference() in moving:
        continue
    bb = bbox(f)
    if EDGE[0] - 5 <= bb[0] and bb[2] <= EDGE[2] + 5 and EDGE[1] - 5 <= bb[1] and bb[3] <= EDGE[3] + 5:
        occupied[f.GetReference()] = bb

result = {}
for p in plan:
    f = board.FindFootprintByReference(p["ref"])
    pads = [q for q in f.Pads() if q.GetNetname() == p["padnet"]] or [f.Pads()[0]]
    best = None
    x0, y0, x1, y1 = p["win"]
    for rot in p["rots"]:
        f.SetOrientationDegrees(rot)
        y = y0
        while y <= y1:
            x = x0
            while x <= x1:
                f.SetPosition(pcbnew.VECTOR2I(fm(x), fm(y)))
                bb = bbox(f)
                inside = (bb[0] >= EDGE[0] + MARGIN and bb[2] <= EDGE[2] - MARGIN and
                          bb[1] >= EDGE[1] + MARGIN and bb[3] <= EDGE[3] - MARGIN)
                if inside and not any(overlaps(bb, c) for c in occupied.values()):
                    pp = pads[0].GetPosition()
                    d = math.hypot(mm(pp.x) - p["target"][0], mm(pp.y) - p["target"][1])
                    if best is None or d < best[0]:
                        best = (d, round(x, 2), round(y, 2), rot, bb)
                x += STEP
            y += STEP
    if best is None:
        print(p["ref"], "SEM POSICAO na janela")
        continue
    d, x, y, rot, bb = best
    result[p["ref"]] = [x, y, rot]
    f.SetOrientationDegrees(rot)
    f.SetPosition(pcbnew.VECTOR2I(fm(x), fm(y)))
    occupied[p["ref"]] = bb
    print(f"{p['ref']} -> x={x:.2f} y={y:.2f} rot={rot}  (pad a {d:.2f} mm do alvo)")
json.dump(result, open(out, "w"))
