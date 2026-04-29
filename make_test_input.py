from PIL import Image
import numpy as np

arr = np.zeros((300, 100), dtype=np.uint8)
for y in range(300):
    for x in range(100):
        arr[y, x] = int(255 * (y / 300) * 0.6 + 255 * (x / 100) * 0.4)
Image.fromarray(arr, "L").save("test_input.png")
print("made test_input.png")
