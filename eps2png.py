from PIL import Image
import os

def convert(path, width_max = 1024):
    print(f"Convert {path} to png")
    image = Image.open(path)
    image = image.convert('RGBA')
    width, height = image.size
    if width > 1024:
        image = image.resize((width_max, int(height * width_max / width)))
    image.save(path.replace(".eps", ".png"))

def scan_directory(path):
    files = os.listdir(path)
    for f in files:
        if os.path.isdir(f"{path}/{f}"):
            scan_directory(f"{path}/{f}")
        elif f.endswith(".eps"):
            convert(f"{path}/{f}")

if __name__ == '__main__':
    path = r"c:/aldes"
    scan_directory(path)
