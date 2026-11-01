"""Mapa de ocupacao em texto: courtyards (letra = 1a letra da ref, # = sobreposicao) e vias (+).
Somente leitura.

Uso: PY tools/pcb_map.py ARQUIVO.kicad_pcb X0 X1 Y0 Y1 PASSO
Ex.: PY tools/pcb_map.py projeto.kicad_pcb 126 154 84 104 0.5
A linha de cabecalho mostra o digito das unidades de X a cada 2 passos.
"""
import sys
import pcbnew

mm = pcbnew.ToMM
board = pcbnew.LoadBoard(sys.argv[1])
x0, x1, y0, y1, st = [float(v) for v in sys.argv[2:7]]

boxes = []
for f in board.GetFootprints():
    r = f.GetCourtyard(pcbnew.F_CrtYd).BBox()
    if r.GetWidth() == 0:
        r = f.GetBoundingBox(False)
    boxes.append((f.GetReference(), mm(r.GetLeft()), mm(r.GetRight()), mm(r.GetTop()), mm(r.GetBottom())))
vias = [(mm(t.GetPosition().x), mm(t.GetPosition().y)) for t in board.GetTracks() if t.GetClass() == "PCB_VIA"]
for z in board.Zones():
    bb = z.GetBoundingBox()
    print(f"zona {z.GetZoneName()} x {mm(bb.GetLeft()):.2f}..{mm(bb.GetRight()):.2f} y {mm(bb.GetTop()):.2f}..{mm(bb.GetBottom()):.2f}")

print("      " + "".join(str(int(x0 + i * st * 2) % 10) for i in range(int((x1 - x0) / st / 2) + 1)))
y = y0
while y <= y1:
    row = ""
    x = x0
    while x <= x1:
        c = "."
        for ref, l, rr, t, bt in boxes:
            if l <= x <= rr and t <= y <= bt:
                c = ref[0] if c == "." else "#"
        for vx, vy in vias:
            if abs(vx - x) < st / 2 and abs(vy - y) < st / 2:
                c = "+"
        row += c
        x += st
    print(f"{y:6.1f} {row}")
    y += st
