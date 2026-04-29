# Bookmark Heightmap Generator

Converts an image into a 2-color 3D printable bookmark using a heightmap approach.
Targets the Bambu X1C with AMS (2-filament: dark base + light surface).

## What this does

Grayscale image -> posterized tonal bands -> OpenSCAD heightmap model -> single STL

The core technique: a dark base filament prints first as a flat substrate. At
`z = base_thickness`, the slicer swaps to the light filament for a single global
filament change. Above that swap, the bookmark's thickness varies per pixel: the
heightmap encodes how many thin light layers stack at each (x, y), with brighter
pixels = more layers = brighter appearance. Typically 4-8 tonal levels at
0.08-0.12mm layer height.

The bookmark has variable total thickness (this is intentional; see Design notes).

Output files:
- `heightmap.png` -- grayscale PNG consumed by OpenSCAD's `surface()` function
- `bookmark.scad` -- OpenSCAD file with one body, ready to export as one STL

## File structure

```
bookmark_heightmap.py   # main script (single file for now)
CLAUDE.md               # this file
```

## Usage

```bash
pip install Pillow numpy
python bookmark_heightmap.py input.jpg [options]
```

Key options:
```
--width   float   Bookmark width mm (default: 50)
--height  float   Bookmark height mm (default: 150)
--levels  int     Tonal levels, 2-8 (default: 6)
--layer   float   Layer height mm (default: 0.08)
--base    float   Base thickness mm (default: 0.8)
--contrast float  Contrast boost, >1.0 (default: 1.3)
--blur    float   Gaussian blur radius px (default: 0.5)
--invert          Flip dark/light mapping
--out     path    Output directory (default: .)
```

The script prints the layer number where the filament change should be inserted
(`round(base_thickness / layer_height)`).

## Print workflow (Bambu X1C)

1. Run script. Verify `heightmap.png` looks like a good posterized image.
2. Open `bookmark.scad` in OpenSCAD, render (F6), Export STL.
3. BambuStudio: import `bookmark.stl` as a new project.
4. Filament 1 = dark, Filament 2 = light.
5. Add a filament change at the layer the script printed
   ("Add Pause/Filament Change" on the slicer's layer slider).
   Below that layer = dark; above = light.
6. Layer height: match `--layer` value used when generating.
7. Supports: OFF.

## Known issues / future work

### Direct STL output
Bypassing OpenSCAD entirely and generating STL directly from Python (e.g. using
`numpy-stl` or `trimesh`) would remove the OpenSCAD dependency and make the workflow
smoother. The heightmap -> triangle mesh conversion is straightforward and we'd
gain the ability to also emit 3MF directly with the filament-change layer baked in.

### Preview / iteration speed
Currently the only way to see the result is to render in OpenSCAD (slow for large
heightmaps) or check heightmap.png manually. A quick matplotlib preview of the
posterized image overlaid with tonal level bands would help iteration.

### Image preprocessing
The current pipeline is: grayscale -> letterbox to bookmark aspect -> optional blur
-> contrast boost -> posterize. Could explore:
- Edge enhancement before posterizing to keep fine linework crisp
- Histogram equalization as an alternative to manual contrast adjustment
- Auto-contrast that clips darkest/lightest N% of pixels

### Project 3MF with filament change pre-baked
Standard 3MF can bundle the mesh but Bambu's project format also stores the
filament-change marker. Reverse-engineering that XML schema would let us output
a single file the user just opens in BambuStudio with everything pre-set --
no manual layer-change step.

### Potential GUI / web wrapper
A small Gradio or Streamlit app would make this accessible without CLI familiarity.
Could show live preview of posterization at different level counts before committing.

## Design notes

### Why variable thickness, not constant
An earlier iteration tried a constant-thickness model where light filament occupied
the top of the bookmark with a contoured underside, and dark filled below. That
forced a per-XY filament transition on every layer above the base, meaning
N filament swaps and a purge tower per swap. Variable thickness gets the same
visual result with **one** filament change at z=base_thickness; the "tonal levels"
emerge from how many light layers physically stack at each point. The cost is a
slightly bumpy top surface (max ~0.6mm relief at default settings), which is
acceptable -- and arguably part of the look.

### Level 0 has no light filament
The darkest tonal band is bare dark base, no light layers above. The heightmap
PNG encodes pixel value 0 there, which after `resize()` in OpenSCAD ends up
sub-printable thickness (~0.002mm, well below `--layer`). The slicer skips it,
so level-0 areas print as exposed dark filament. This is intentional -- adding
a "minimum light layer everywhere" would wash out the dark regions.

### OpenSCAD surface() with resize()
The SCAD uses `resize([width, height, surface_max_z]) surface(...)` to map pixel
dimensions to physical mm in one shot. This works because surface() generates a
solid with a flat bottom slightly below the min pixel value, so resize stretches
that natural bbox to the requested dimensions and the result is always manifold.

### Print physics: the painterly look
- `px_per_mm = 3` gives ~150 DPI effective resolution, plenty for FDM. Going
  higher doesn't improve print quality and bloats the heightmap PNG.
- OpenSCAD's `surface()` does bilinear interpolation between pixel values, which
  creates smooth slopes between tonal levels rather than sharp staircase steps.
  This is the source of the "painterly" quality -- preserve this behavior, don't
  try to snap to sharp level boundaries in the SCAD.
- Light filament is somewhat translucent, so stacking more layers reads as
  brighter against the dark substrate. This is what makes the multi-tone look
  work with only 2 filaments.

### Hardware specifics
- The hole punch (4mm diameter, 7mm from top edge) matches standard bookmark
  hardware. Make these configurable if expanding the script.
- `--invert` exists for users who want to run the filament assignment in reverse
  (light base, dark surface). Less common but valid aesthetic choice.
