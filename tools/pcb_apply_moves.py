"""Move footprints (e opcionalmente vira para a face de baixo) e GRAVA o arquivo.
Aborta sem gravar se a rede ou a geometria de qualquer trilha ou via mudar.

Uso: PY tools/pcb_apply_moves.py ARQUIVO.kicad_pcb moves.json
moves.json: {"R1": [x, y, rot], "TP1": [x, y, 0, true]}  (4o valor true = virar para B.Cu)

ATENCAO: so rodar com o KiCad fechado e com o git limpo (CLAUDE.md, Seguranca do arquivo).
Teste antes numa copia, com o .kicad_pro ao lado, e rode o DRC. Nao use em footprint cujo pad
toca uma trilha: ao salvar, o KiCad pode reatribuir as redes dessas trilhas (checagem abaixo).
"""
import json
import sys
import pcbnew

path, moves_file = sys.argv[1], sys.argv[2]
moves = json.load(open(moves_file))
board = pcbnew.LoadBoard(path)


def snapshot():
    return {
        str(t.m_Uuid.AsString()): (t.GetNetname(), t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y)
        for t in board.GetTracks()
    }


before = snapshot()
for ref, v in moves.items():
    f = board.FindFootprintByReference(ref)
    if f is None:
        sys.exit(f"ABORTADO: {ref} nao existe")
    x, y, rot = v[0], v[1], v[2]
    flip = len(v) > 3 and bool(v[3])
    if flip and f.GetLayer() == pcbnew.F_Cu:
        f.Flip(f.GetPosition(), False)
    elif not flip:
        f.SetOrientationDegrees(rot)
    f.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))

if snapshot() != before:
    sys.exit("ABORTADO: redes ou geometria de trilhas/vias mudaram. Nada foi gravado.")
board.Save(path)
print(f"OK: {len(moves)} footprints movidos; {len(before)} trilhas/vias intactas; arquivo gravado.")
