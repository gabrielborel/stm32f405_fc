"""Offscreen PNG previews of the case sketch (VTK). Run case.py first.

Usage: python3 case/render.py
Writes case/out/preview_*.png and case/out/preview.png (montage, needs ImageMagick).
"""

import subprocess
from pathlib import Path

import vtk

OUT = Path(__file__).resolve().parent / "out"

PARTS = {  # name: (file, rgb, opacity)
    "base": ("case_base.stl", (0.55, 0.57, 0.62), 1.0),
    "lid": ("case_lid.stl", (0.30, 0.31, 0.35), 1.0),
    "board": ("board.stl", (0.12, 0.50, 0.25), 1.0),
}


def actor(name, dz=0.0, opacity=None):
    f, rgb, op = PARTS[name]
    r = vtk.vtkSTLReader()
    r.SetFileName(str(OUT / f))
    n = vtk.vtkPolyDataNormals()
    n.SetInputConnection(r.GetOutputPort())
    n.SetFeatureAngle(40)
    m = vtk.vtkPolyDataMapper()
    m.SetInputConnection(n.GetOutputPort())
    a = vtk.vtkActor()
    a.SetMapper(m)
    a.GetProperty().SetColor(*rgb)
    a.GetProperty().SetOpacity(op if opacity is None else opacity)
    a.GetProperty().SetSpecular(0.2)
    a.SetPosition(0, 0, dz)
    return a


def render(actors, pos, up, fname, title):
    ren = vtk.vtkRenderer()
    ren.SetBackground(0.96, 0.96, 0.97)
    for a in actors:
        ren.AddActor(a)
    cam = ren.GetActiveCamera()
    cam.SetFocalPoint(0, 0, 8)
    cam.SetPosition(*pos)
    cam.SetViewUp(*up)
    ren.ResetCamera()
    cam.Zoom(1.25)
    txt = vtk.vtkTextActor()
    txt.SetInput(title)
    txt.GetTextProperty().SetFontSize(22)
    txt.GetTextProperty().SetColor(0.1, 0.1, 0.1)
    txt.SetPosition(12, 12)
    ren.AddViewProp(txt)
    win = vtk.vtkRenderWindow()
    win.SetOffScreenRendering(1)
    win.AddRenderer(ren)
    win.SetSize(900, 700)
    win.Render()
    w2i = vtk.vtkWindowToImageFilter()
    w2i.SetInput(win)
    w2i.Update()
    png = vtk.vtkPNGWriter()
    png.SetFileName(str(OUT / fname))
    png.SetInputConnection(w2i.GetOutputPort())
    png.Write()
    return OUT / fname


def main():
    has_board = (OUT / "board.stl").exists()
    files = []
    ex = [actor("base"), actor("lid", dz=22)]
    if has_board:
        ex.append(actor("board", dz=6))
    files.append(render(ex, (-90, -110, 90), (0, 0, 1), "preview_exploded.png",
                        "exploded, from rear-right (USB/microSD side)"))
    files.append(render([actor("base"), actor("lid")], (120, 80, 110), (0, 0, 1),
                        "preview_front.png", "closed, from front-left (GPS/ELRS side)"))
    files.append(render([actor("base"), actor("lid")], (0, 0, 200), (0, 1, 0),
                        "preview_top.png", "top (front = right)"))
    inside = [actor("base"), actor("lid", opacity=0.35)]
    if has_board:
        inside.append(actor("board"))
    files.append(render(inside, (-60, -120, 70), (0, 0, 1), "preview_inside.png",
                        "lid transparent, board inside"))
    try:
        subprocess.run(["magick", "montage", *map(str, files), "-tile", "2x2",
                        "-geometry", "+4+4", str(OUT / "preview.png")], check=True)
    except Exception as e:
        print("montage skipped:", e)
    print("\n".join(map(str, files)))


if __name__ == "__main__":
    main()
