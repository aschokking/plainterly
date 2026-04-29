# Bookmark Heightmap Generator

Converts an image into a 2-color 3D printable bookmark using a heightmap approach.
Targets the Bambu X1C with AMS (2-filament: dark base + light surface).

## What this does

Grayscale image -> posterized tonal bands -> OpenSCAD heightmap model -> 2-part STL pair

The core technique: a dark base filament is printed first as a flat substrate. A light
filament is printed on top, with the number of thin layers at each point encoding image
brightness. More light layers = brighter appearance. Typically 4-8 tonal levels at
0.08-0.12mm layer height.

Output files:
- `heightmap.png` -- grayscale PNG consumed by OpenSCAD's `surface()` function
- `bookmark.scad` -- OpenSCAD file with base + surface bodies, ready to export as 2 STLs

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
--levels  int     Tonal levels, 4-8 (default: 6)
--layer   float   Layer height mm (default: 0.12)
--base    float   Base thickness mm (default: 0.8)
--contrast float  Contrast boost, >1.0 (default: 1.3)
--blur    float   Gaussian blur radius px (default: 0.5)
--invert          Flip dark/light mapping
--out     path    Output directory (default: .)
```

## Print workflow (Bambu X1C)

1. Run script, verify `heightmap.png` looks like a good posterized image
2. Open `bookmark.scad` in OpenSCAD
3. Export base body as `bookmark_base.stl` (dark filament)
4. Uncomment surface body, export as `bookmark_surface.stl` (light filament)
5. BambuStudio: new project, add base STL, right-click -> Add Part -> surface STL
6. Assign filaments: base = dark, surface = light
7. Layer height: match `--layer` value used when generating
8. Supports: OFF

## Known issues / future work

### OpenSCAD surface() scaling
The `surface()` call in the generated SCAD file needs the `resize()` wrapper to map
pixel dimensions to physical mm. The current generated SCAD has the resize logic
partially stubbed -- it works but should be cleaned up into a single clean module.

### SCAD export UX is awkward
Users must manually comment/uncomment two sections to export the two STLs separately.
Better options to explore:
- Use OpenSCAD's `--export-format` CLI with two separate SCAD files
- Or generate two separate SCAD files (bookmark_base.scad, bookmark_surface.scad)
- Or investigate BambuStudio's 3MF format for bundling both bodies + filament assignments

### Direct STL output
Bypassing OpenSCAD entirely and generating STL directly from Python (e.g. using
`numpy-stl` or `trimesh`) would remove the OpenSCAD dependency and make the workflow
smoother. The heightmap -> triangle mesh conversion is straightforward.

### Preview / iteration speed
Currently the only way to see the result is to render in OpenSCAD (slow for large
heightmaps) or check heightmap.png manually. A quick matplotlib preview of the
posterized image overlaid with tonal level bands would help iteration.

### Image preprocessing
The current pipeline is: grayscale -> optional blur -> contrast boost -> posterize.
Could explore:
- Edge enhancement before posterizing to keep fine linework crisp
- Histogram equalization as an alternative to manual contrast adjustment
- Auto-contrast that clips darkest/lightest N% of pixels

### Potential GUI / web wrapper
A small Gradio or Streamlit app would make this accessible without CLI familiarity.
Could show live preview of posterization at different level counts before committing.

## Design notes

- `px_per_mm = 3` in the script gives ~150 DPI effective resolution, which is plenty
  for FDM. Going higher doesn't improve print quality and bloats the heightmap PNG.
- OpenSCAD's `surface()` does bilinear interpolation between pixel values, which creates
  smooth slopes between tonal levels rather than sharp staircase steps. This is the
  source of the "painterly" quality -- preserve this behavior, don't try to snap to
  sharp level boundaries in the SCAD.
- The hole punch (4mm diameter, 7mm from top edge) matches standard bookmark hardware.
  Make these configurable if expanding the script.
- `--invert` exists for users who want to run the filament assignment in reverse (light
  base, dark surface). Less common but valid aesthetic choice.
