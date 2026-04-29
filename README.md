# plainterly

Turn an image into a 2-color 3D-printable bookmark with a painterly, posterized look.

The pipeline takes a grayscale image, posterizes it into a few tonal bands, and emits an
OpenSCAD heightmap model. Print it on a Bambu X1C (or any AMS / dual-material printer)
with **one** filament change at the base layer — no per-layer purges, no separate STLs.

Brighter pixels in the source image stack more layers of light filament on top of a dark
substrate. The light filament is somewhat translucent, so the layer count reads as
brightness against the dark base. That's the whole trick.

## Install

Requires Python 3.10+ and OpenSCAD.

```bash
pip install Pillow numpy
```

## Generate

```bash
python bookmark_heightmap.py input.jpg --out out
```

Useful options:

| Flag | Default | What it does |
|---|---|---|
| `--width` | 50 | Bookmark width (mm) |
| `--height` | 150 | Bookmark height (mm) |
| `--levels` | 6 | Tonal bands (2–8) |
| `--layer` | 0.08 | Print layer height (mm) |
| `--base` | 0.8 | Dark base thickness (mm) |
| `--contrast` | 1.3 | Contrast boost before posterizing |
| `--blur` | 0.5 | Pre-posterize Gaussian blur (px) |
| `--invert` | — | Flip dark/light mapping |

The script writes `heightmap.png` and `bookmark.scad` to the output dir, and prints the
layer number where the filament change should go.

## Print (Bambu X1C)

1. Open `bookmark.scad` in OpenSCAD, render (F6), Export STL.
2. Import the STL into BambuStudio.
3. Filament 1 = dark, Filament 2 = light.
4. On the layer slider, add a filament change at the layer the script printed.
   Below = dark; above = light.
5. Set layer height to match `--layer`. Supports off.

## How it works

The bookmark is a single body with variable total thickness. Below `base_thickness` it's
solid dark filament; above it, the heightmap encodes how many light layers stack at each
(x, y). Level-0 regions have zero light layers, so dark filament shows through directly.
Bilinear interpolation between pixels gives the smooth painterly slopes between bands.

Earlier iterations used two STLs and a per-layer filament transition, which forced a
purge tower per swap. The single-body approach gets the same look with one global swap.

## Layout

```
bookmark_heightmap.py        # main script
make_calibration_gradient.py # generate a calibration gradient PNG
inspect_heightmap.py         # quick check on a heightmap
inspect_stl.py               # parse + sanity-check an STL
```
