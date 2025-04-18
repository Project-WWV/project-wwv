from PIL import Image
import os
import numpy as np
from sklearn.neighbors import NearestNeighbors
import json

SOURCE_DIR = "tiles/"
DEST_DIR = "tiles_resized/"
SIZE = (100, 100)

print("[1/6] Kachelverzeichnis vorbereiten...")
os.makedirs(DEST_DIR, exist_ok=True)

print(f"[2/6] Kacheln aus '{SOURCE_DIR}' werden auf Größe {SIZE} gebracht...")
count = 0
for filename in os.listdir(SOURCE_DIR):
    if filename.lower().endswith((".jpg", ".jpeg", ".png")):
        path = os.path.join(SOURCE_DIR, filename)
        img = Image.open(path).convert("RGB")
        img = img.resize(SIZE)
        img.save(os.path.join(DEST_DIR, filename))
        count += 1
print(f"    → {count} Bilder verarbeitet.")

print("[3/6] Zielbild 'master.jpg' wird geladen...")
if not os.path.exists("master.jpg"):
    raise FileNotFoundError("FEHLER: 'master.jpg' nicht gefunden!")

target_img = Image.open("master.jpg").convert("RGB")
target_img = target_img.resize((15000, 15000))
print("    → Bildgröße angepasst auf 15000x15000 Pixel.")

def average_color(img):
    return np.array(img).mean(axis=(0, 1))

print("[4/6] Farben der Kacheln analysieren...")
tile_images = []
tile_colors = []
tile_filenames = []

for filename in sorted(os.listdir(DEST_DIR)):
    if filename.lower().endswith((".jpg", ".jpeg", ".png")):
        path = os.path.join(DEST_DIR, filename)
        img = Image.open(path)
        tile_images.append(img)
        tile_colors.append(average_color(img))
        tile_filenames.append(filename)

tile_colors = np.array(tile_colors)
print(f"    → {len(tile_images)} Kacheln geladen und analysiert.")

tile_size = SIZE[0]
rows = target_img.height // tile_size
cols = target_img.width // tile_size
print(f"[5/6] Erzeuge Mosaik mit {rows} Zeilen x {cols} Spalten...")

output_img = Image.new("RGB", target_img.size)
nbrs = NearestNeighbors(n_neighbors=1).fit(tile_colors)
tile_mapping = {}

source_files = sorted([f for f in os.listdir(SOURCE_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png"))])

index = 0
for y in range(rows):
    for x in range(cols):
        box = (x * tile_size, y * tile_size, (x+1) * tile_size, (y+1) * tile_size)
        region = target_img.crop(box)
        avg_color = average_color(region).reshape(1, -1)
        _, idx = nbrs.kneighbors(avg_color)
        output_img.paste(tile_images[idx[0][0]], box)

        # Ursprünglicher Dateiname aus SOURCE_DIR
        original_filename = source_files[idx[0][0]]
        tile_mapping[str(index)] = original_filename
        index += 1

    if y % 10 == 0:
        print(f"    → Zeile {y+1} von {rows} verarbeitet...")

print("[6/6] Speichere Ausgaben...")
output_img.save("mosaic_result.jpg")
print("    → 'mosaic_result.jpg' gespeichert.")

with open("tile_mapping.json", "w") as f:
    json.dump(tile_mapping, f)

print("    → 'tile_mapping.json' gespeichert.")
print("Fertig!")
