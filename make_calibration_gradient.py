"""Generates a vertical black-to-white gradient for calibration prints."""
from PIL import Image
import numpy as np

# Match the bookmark aspect (50x150 mm at 3 px/mm = 150x450 px),
# but extra resolution is fine -- the script will resize.
W, H = 200, 600
arr = np.linspace(0, 255, H, dtype=np.float32)
arr = np.tile(arr[:, None], (1, W)).astype(np.uint8)
Image.fromarray(arr, "L").save("calibration_gradient.png")
print(f"wrote calibration_gradient.png ({W}x{H})")
