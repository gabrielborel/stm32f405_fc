"""Mostra o retangulo do courtyard (F.CrtYd) dos footprints pedidos. Somente leitura.

Uso: PY tools/pcb_courtyards.py ARQUIVO.kicad_pcb REF [REF ...]
"""
import sys
import pcbnew

mm = pcbnew.ToMM
board = pcbnew.LoadBoard(sys.argv[1])
for ref in sys.argv[2:]:
    f = board.FindFootprintByReference(ref)
    if f is None:
        print(ref, "nao encontrado")
        continue
    r = f.GetCourtyard(pcbnew.F_CrtYd).BBox()
    print(f"{ref} x {mm(r.GetLeft()):.2f}..{mm(r.GetRight()):.2f}  y {mm(r.GetTop()):.2f}..{mm(r.GetBottom()):.2f}")
