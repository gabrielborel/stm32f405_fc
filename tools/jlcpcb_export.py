"""Gera a BOM e o arquivo de posicoes (CPL) no formato da JLCPCB a partir da PCB. Somente leitura da PCB.

Uso: PY tools/jlcpcb_export.py ARQUIVO.kicad_pcb PASTA_DE_SAIDA

- Fica de fora da BOM e do CPL: pecas marcadas como DNP, "Exclude from BOM" ou "Exclude from position files".
- BOM: Comment, Designator, Footprint, LCSC Part # (agrupa por valor, footprint e LCSC).
- CPL: Designator, Val, Package, Mid X, Mid Y, Rotation, Layer. Origem: a origem auxiliar da PCB (Place > Drill/Place File
  Origin) se existir, senao a origem da pagina. Y para cima. Use a MESMA origem ao exportar os Gerbers.
- Avisa de peca na BOM sem LCSC, de peca na face de baixo (a montagem Economic e de uma face so) e de THT.
A rotacao e a do KiCad: a JLCPCB tem desvios por encapsulamento (SOT-23, LEDs, cristal, conectores); conferir no visualizador.
"""
import csv, os, re, sys
import pcbnew

mm = pcbnew.ToMM
board = pcbnew.LoadBoard(sys.argv[1]); out = sys.argv[2]
os.makedirs(out, exist_ok=True)
org = board.GetDesignSettings().GetAuxOrigin()
ox, oy = mm(org.x), mm(org.y)


def nat(r):
    m = re.match(r"([A-Za-z#]+)(\d+)", r)
    return (m.group(1), int(m.group(2))) if m else (r, 0)


rows = []; avisos = []
for f in sorted(board.GetFootprints(), key=lambda f: nat(f.GetReference())):
    if f.IsDNP() or f.IsExcludedFromBOM() or f.IsExcludedFromPosFiles(): continue
    ref = f.GetReference(); val = f.GetValue(); fp = str(f.GetFPID().GetLibItemName())
    lcsc = f.GetFieldText("LCSC") if f.HasField("LCSC") else ""
    bottom = f.GetLayer() == pcbnew.B_Cu
    if not lcsc: avisos.append("%s (%s): sem LCSC" % (ref, val))
    if bottom: avisos.append("%s: na face de baixo (Economic monta uma face so)" % ref)
    if not f.GetAttributes() & pcbnew.FP_SMD: avisos.append("%s: nao e SMD" % ref)
    p = f.GetPosition()
    rot = f.GetOrientationDegrees() % 360
    rows.append(dict(ref=ref, val=val, fp=fp, lcsc=lcsc, x=mm(p.x) - ox, y=oy - mm(p.y), rot=rot, layer="Bottom" if bottom else "Top"))

grupos = {}
for r in rows: grupos.setdefault((r["val"], r["fp"], r["lcsc"]), []).append(r["ref"])
with open(os.path.join(out, "bom.csv"), "w", newline="") as fh:
    w = csv.writer(fh, quoting=csv.QUOTE_ALL); w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
    for (val, fp, lcsc), refs in sorted(grupos.items(), key=lambda kv: nat(kv[1][0])):
        w.writerow([val, ",".join(sorted(refs, key=nat)), fp, lcsc])
with open(os.path.join(out, "cpl.csv"), "w", newline="") as fh:
    w = csv.writer(fh, quoting=csv.QUOTE_ALL); w.writerow(["Designator", "Val", "Package", "Mid X", "Mid Y", "Rotation", "Layer"])
    for r in rows: w.writerow([r["ref"], r["val"], r["fp"], "%.6fmm" % r["x"], "%.6fmm" % r["y"], "%.1f" % r["rot"], r["layer"]])
print("origem usada: (%.3f; %.3f) mm%s" % (ox, oy, "" if (ox or oy) else " (origem da pagina, sem origem auxiliar)"))
print("%d pecas na BOM em %d linhas; %d no CPL" % (len(rows), len(grupos), len(rows)))
for a in avisos: print("AVISO:", a)
