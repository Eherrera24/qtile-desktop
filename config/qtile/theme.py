from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import json
import sys

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % tuple(int(x) for x in rgb)

def get_dominant_colors(image_path, k=8):
    img = Image.open(image_path).convert("RGB")
    img = img.resize((200, 200))  # reduce tamaño para velocidad

    pixels = np.array(img).reshape(-1, 3)

    kmeans = KMeans(n_clusters=k, n_init=10)
    kmeans.fit(pixels)

    colors = kmeans.cluster_centers_
    return [rgb_to_hex(c) for c in colors]

def brightness(hex_color):
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2],16), int(hex_color[2:4],16), int(hex_color[4:6],16)
    return (r*299 + g*587 + b*114) / 1000

def generate_theme(colors):
    # ordenar por brillo
    colors = sorted(colors, key=brightness)

    dark = colors[0]
    grey = colors[len(colors)//3]
    light = colors[-1]

    text = "#000000" if brightness(light) > 128 else "#FFFFFF"

    theme = {
        "dark": [dark, dark],
        "grey": [grey, grey],
        "light": [light, light],
        "text": [text, text],
        "focus": [colors[-2], colors[-2]],
        "active": [light, light],
        "inactive": [colors[len(colors)//2], colors[len(colors)//2]],
        "urgent": [colors[1], colors[1]],
        "color1": [colors[2], colors[2]],
        "color2": [colors[3], colors[3]],
        "color3": [colors[4], colors[4]],
        "color4": [colors[5], colors[5]],
        "color5": [colors[6], colors[6]],
    }

    return theme

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python theme.py imagen.jpg")
        sys.exit(1)

    image_path = sys.argv[1]

    colors = get_dominant_colors(image_path, k=8)
    theme = generate_theme(colors)

    print(json.dumps(theme, indent=4))
