"""Quick inspection of a generated heightmap."""
import sys
from PIL import Image
import numpy as np

path = sys.argv[1] if len(sys.argv) > 1 else "out_cal/heightmap.png"
im = np.asarray(Image.open(path))
print(f"size: {im.shape}  unique values: {sorted(set(im.flatten().tolist()))}")
col = im[:, im.shape[1] // 2]
prev = -1
for i, v in enumerate(col):
    if v != prev:
        print(f"  y={i}: pixel value {v}")
        prev = int(v)
