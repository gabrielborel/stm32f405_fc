"""Lista pads (numero, rede, posicao absoluta) dos footprints pedidos. Somente leitura.

Uso: PY tools/pcb_pads.py ARQUIVO.kicad_pcb REF [REF ...]
PY = Python do app do KiCad (ver tools/README.md).
Obs.: o tamanho do pad vem no referencial do proprio pad, sem a rotacao do footprint.
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
    p = f.GetPosition()
    print(f"{ref} {f.GetValue()} {f.GetFPID().GetLibItemName()} em {mm(p.x):.3f},{mm(p.y):.3f} rot {f.GetOrientationDegrees():.0f} face {board.GetLayerName(f.GetLayer())}")
    for pad in f.Pads():
        q = pad.GetPosition()
        s = pad.GetSize()
        print(f"   pad {pad.GetNumber():>3} {pad.GetNetname():<24} {mm(q.x):.2f},{mm(q.y):.2f} {mm(s.x):.2f}x{mm(s.y):.2f}")
