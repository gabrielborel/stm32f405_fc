"""Preliminary FDM case sketch for the STM32F405 flight controller (58 x 44 mm).

Two parts:
  - base: tray with 4 standoffs; M2 cap screws go in from the bottom.
  - lid:  cover with 4 bosses holding M2 heat-set inserts; it clamps the board.

Frame: origin at the board centre, X to the front (east in the KiCad editor),
Y to the left (north in the editor), Z up, z = 0 at the bottom of the base.
KiCad (X, Y) maps to case (X - 137.5, 90.5 - Y).

Positions come from the .kicad_pcb (2026-11-02). Heights come from the board
STEP exported with kicad-cli. Values marked "guess" are not from a datasheet.

Usage:
  python3 case/case.py [board.step]
Writes case/out/case_base.stl, case_lid.stl, case_assembly.step.
"""

import sys
from pathlib import Path

import cadquery as cq

OUT = Path(__file__).resolve().parent / "out"

# ---------------------------------------------------------------- parameters
BOARD_W, BOARD_H, BOARD_R = 58.0, 44.0, 2.0  # PCB outline
BOARD_T = 1.56                               # JLC04161H-3313 stackup
BOARD_CX, BOARD_CY = 137.5, 90.5             # board centre in KiCad coords

GAP = 0.4        # board edge to inner wall (FDM, guess)
WALL = 2.0       # side wall (guess)
FLOOR = 1.6      # base floor
TOP = 1.6        # lid top
STANDOFF = 3.0   # board bottom above the floor (J2 pins go 1.42 mm below)
HEADROOM = 5.5   # board top to lid inner top (tallest part: JST GH, 4.26 mm)

HOLE_DX, HOLE_DY = 25.5, 18.5  # M2 holes, 3.5 mm from the board edge
BOSS_D = 5.4                   # standoff / boss diameter (guess)
SCREW_D = 2.4                  # M2 clearance hole (guess)
HEAD_D, HEAD_H = 4.2, 2.0      # M2 cap head counterbore (head 3.8 x 2.0)
INSERT_D, INSERT_H = 3.2, 4.5  # heat-set insert hole (check the insert you buy)

ENGRAVE = 0.5

# derived Z levels
Z_BOARD_BOT = FLOOR + STANDOFF
Z_BOARD_TOP = Z_BOARD_BOT + BOARD_T      # split plane between base and lid
Z_LID_IN = Z_BOARD_TOP + HEADROOM
Z_TOP = Z_LID_IN + TOP

IN_W, IN_H = BOARD_W + 2 * GAP, BOARD_H + 2 * GAP
OUT_W, OUT_H = IN_W + 2 * WALL, IN_H + 2 * WALL
IN_R, OUT_R = BOARD_R + GAP, BOARD_R + GAP + WALL

HOLES = [(sx * HOLE_DX, sy * HOLE_DY) for sx in (-1, 1) for sy in (-1, 1)]


def k(x, y):
    """KiCad editor coords to case coords."""
    return (x - BOARD_CX, BOARD_CY - y)


def rrect(w, h, r, z0, z1):
    return (cq.Workplane("XY").workplane(offset=z0)
            .sketch().rect(w, h).vertices().fillet(r).finalize()
            .extrude(z1 - z0))


def box(x0, x1, y0, y1, z0, z1):
    return (cq.Workplane("XY")
            .box(x1 - x0, y1 - y0, z1 - z0, centered=False)
            .translate((x0, y0, z0)))


# ------------------------------------------------- side openings (both parts)
def side_cutters():
    c = []
    xw_out, xw_in = -OUT_W / 2 - 1, -IN_W / 2 + 0.3   # west wall span
    xe_in, xe_out = IN_W / 2 - 0.3, OUT_W / 2 + 1     # east wall span
    yn_in, yn_out = IN_H / 2 - 0.3, OUT_H / 2 + 1     # north wall span
    ys_out, ys_in = -OUT_H / 2 - 1, -IN_H / 2 + 0.3   # south wall span
    zt = Z_BOARD_TOP

    # West: USB-C (J3). Plug overmold 12 x 7 mm (guess, cables vary).
    _, y = k(0, 80.6)
    usb = (cq.Workplane("YZ").workplane(offset=xw_out)
           .center(y, zt + 1.6)
           .sketch().rect(12.0, 7.0).vertices().fillet(2.5).finalize()
           .extrude(xw_in - xw_out))
    c.append(usb)

    # West: microSD (J4), card 11 mm wide, slot 13 x 3 mm, plus finger recess
    _, y = k(0, 93.3)
    c.append(box(xw_out, xw_in, y - 6.5, y + 6.5, zt - 0.6, zt + 2.4))
    recess = (cq.Workplane("YZ").workplane(offset=xw_out)
              .center(y, zt + 0.9)
              .sketch().rect(18.0, 9.0).vertices().fillet(3.0).finalize()
              .extrude(1.0 + 1.0))   # 1 mm into the 2 mm wall
    c.append(recess)

    # East: JST GH J5 (ELRS) and J6 (GPS). Receptacle body from the STEP + 0.6 mm.
    for y_top, y_bot in ((75.7, 83.9), (86.2, 97.0)):
        _, y0 = k(0, y_bot)
        _, y1 = k(0, y_top)
        c.append(box(xe_in, xe_out, y0 - 0.6, y1 + 0.6, zt - 0.2, zt + 5.1))

    # East: J12 wire slot (GPIO / current pads)
    _, y0 = k(0, 105.75)
    _, y1 = k(0, 98.92)
    c.append(box(xe_in, xe_out, y0 - 0.2, y1 + 0.2, zt, zt + 3.0))

    # South: wire slot for J1 (PDB), J8 (motors), J7 (buzzer), J13
    x0, _ = k(114.5, 0)
    x1, _ = k(149.6, 0)
    c.append(box(x0, x1, ys_out, ys_in, zt, zt + 3.0))

    # North: wire slot for J9 (SPI2) and J14 (AUX)
    x0, _ = k(115.0, 0)
    x1, _ = k(140.9, 0)
    c.append(box(x0, x1, yn_in, yn_out, zt, zt + 3.0))

    # North: J2 (SWD header, DNP, 10.1 mm tall) - open notch through the lid
    x0, _ = k(142.0, 0)
    x1, _ = k(159.2, 0)
    _, y0 = k(0, 73.0)
    c.append(box(x0, x1, y0, yn_out, zt, Z_TOP + 1))

    out = c[0]
    for s in c[1:]:
        out = out.union(s)
    return out


# ------------------------------------------------------------------ the base
def make_base():
    body = rrect(OUT_W, OUT_H, OUT_R, 0, Z_BOARD_TOP)
    try:
        body = body.faces("<Z").edges().fillet(0.8)
    except Exception:
        pass
    body = body.cut(rrect(IN_W, IN_H, IN_R, FLOOR, Z_BOARD_TOP + 1))
    for x, y in HOLES:
        post = (cq.Workplane("XY").workplane(offset=FLOOR - 0.01)
                .center(x, y).circle(BOSS_D / 2).extrude(STANDOFF + 0.01))
        body = body.union(post)
        body = body.cut(cq.Workplane("XY").center(x, y)
                        .circle(SCREW_D / 2).extrude(Z_BOARD_BOT + 1))
        body = body.cut(cq.Workplane("XY").workplane(offset=-0.01).center(x, y)
                        .circle(HEAD_D / 2).extrude(HEAD_H + 0.01))
    return body


# ------------------------------------------------------------------- the lid
def make_lid():
    body = rrect(OUT_W, OUT_H, OUT_R, Z_BOARD_TOP, Z_TOP)
    try:
        body = body.faces(">Z").edges().fillet(1.0)
    except Exception:
        pass
    body = body.cut(rrect(IN_W, IN_H, IN_R, Z_BOARD_TOP - 1, Z_LID_IN))
    for x, y in HOLES:
        boss = (cq.Workplane("XY").workplane(offset=Z_BOARD_TOP)
                .center(x, y).circle(BOSS_D / 2).extrude(HEADROOM + 0.01))
        body = body.union(boss)
        body = body.cut(cq.Workplane("XY").workplane(offset=Z_BOARD_TOP - 0.01)
                        .center(x, y).circle(INSERT_D / 2).extrude(INSERT_H))

    def through(x, y, d):
        return (cq.Workplane("XY").workplane(offset=Z_LID_IN - 0.1)
                .center(x, y).circle(d / 2).extrude(TOP + 1))

    # BMP280 (U4) vent: 4 holes of 1.5 mm; put open-cell foam inside
    x, y = k(155.0, 79.0)
    for dx, dy in ((-1.2, -1.2), (-1.2, 1.2), (1.2, -1.2), (1.2, 1.2)):
        body = body.cut(through(x + dx, y + dy, 1.5))

    # LEDs D1 to D3: 1.5 mm windows
    for ky in (77.4, 79.8, 82.2):
        body = body.cut(through(*k(143.6, ky), 1.5))

    # Buttons: SW1 = RESET (NRST), SW2 = BOOT0. 2.5 mm holes, press with a pin.
    for ky, label in ((88.8, "RST"), (97.2, "BOOT")):
        x, y = k(153.84, ky)
        body = body.cut(through(x, y, 2.5))
        txt = (cq.Workplane("XY").workplane(offset=Z_TOP - ENGRAVE)
               .center(x + 6.5, y)
               .text(label, 2.2, ENGRAVE + 0.1, halign="center", valign="center"))
        body = body.cut(txt)

    # Front arrow (points +X, same as the silk arrow)
    arrow = (cq.Workplane("XY").workplane(offset=Z_TOP - ENGRAVE)
             .polyline([(-9, -1.5), (2, -1.5), (2, -4.5), (9, 0),
                        (2, 4.5), (2, 1.5), (-9, 1.5)]).close()
             .extrude(ENGRAVE + 0.1)
             .translate((-6.0, -6.0, 0)))
    body = body.cut(arrow)
    body = body.cut(cq.Workplane("XY").workplane(offset=Z_TOP - ENGRAVE)
                    .center(-6.0, -12.0)
                    .text("F405 FC", 3.0, ENGRAVE + 0.1, halign="center", valign="center"))
    return body


def main():
    OUT.mkdir(exist_ok=True)
    cut = side_cutters()
    base = make_base().cut(cut)
    lid = make_lid().cut(cut)

    cq.exporters.export(base, str(OUT / "case_base.stl"), tolerance=0.02, angularTolerance=0.1)
    cq.exporters.export(lid, str(OUT / "case_lid.stl"), tolerance=0.02, angularTolerance=0.1)

    asm = cq.Assembly()
    asm.add(base, name="base", color=cq.Color(0.25, 0.25, 0.28))
    asm.add(lid, name="lid", color=cq.Color(0.15, 0.15, 0.17))
    if len(sys.argv) > 1:
        board = cq.importers.importStep(sys.argv[1])
        board = board.translate((-BOARD_CX, BOARD_CY, Z_BOARD_BOT))
        asm.add(board, name="board", color=cq.Color(0.1, 0.45, 0.2))
        cq.exporters.export(board, str(OUT / "board.stl"), tolerance=0.05, angularTolerance=0.2)
    asm.export(str(OUT / "case_assembly.step"))

    print(f"outer {OUT_W:.1f} x {OUT_H:.1f} x {Z_TOP:.2f} mm")
    print(f"board top (split) z = {Z_BOARD_TOP:.2f}, lid inner top z = {Z_LID_IN:.2f}")
    screw = (Z_BOARD_BOT - HEAD_H) + BOARD_T + INSERT_H - 0.5
    print(f"M2 screw thread length about {screw:.1f} mm")


if __name__ == "__main__":
    main()
