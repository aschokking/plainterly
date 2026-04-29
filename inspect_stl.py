"""Inspect an STL: bounding box and triangle count."""
import re
import sys

path = sys.argv[1]
xs, ys, zs = [], [], []
n = 0
with open(path) as f:
    for line in f:
        if line.lstrip().startswith("vertex"):
            parts = line.split()
            xs.append(float(parts[1]))
            ys.append(float(parts[2]))
            zs.append(float(parts[3]))
        elif line.lstrip().startswith("facet"):
            n += 1

print(f"triangles: {n}")
print(f"X: {min(xs):.3f} .. {max(xs):.3f}  (size {max(xs)-min(xs):.3f} mm)")
print(f"Y: {min(ys):.3f} .. {max(ys):.3f}  (size {max(ys)-min(ys):.3f} mm)")
print(f"Z: {min(zs):.3f} .. {max(zs):.3f}  (size {max(zs)-min(zs):.3f} mm)")
