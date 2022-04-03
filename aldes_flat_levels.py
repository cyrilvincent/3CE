import os
import shutil

def scan_directory(path, nb=0, path4=None):
    if 0 <nb <= level:
        index = path.rindex("/")
        if path4 is None:
            path4 = path[(index + 1):]
        else:
            path4 = path4 + "@" + path[(index + 1):]
    files = os.listdir(path)
    for f in files:
        if os.path.isdir(f"{path}/{f}"):
            scan_directory(f"{path}/{f}", nb + 1, path4)
        elif f.endswith(".png") and nb >= 4:
            print(f"Copy {path}/{f} to {out_path}/{path4}")
            if not os.path.exists(f"{out_path}/{path4}"):
                os.mkdir(f"{out_path}/{path4}")
            shutil.copy(f"{path}/{f}", f"{out_path}/{path4}/{f}")


if __name__ == '__main__':
    level = 2
    path = "images/catalogues_aldes/01-Produits_Corporate"
    out_path = f"images/catalogues_aldes/ai{level}"
    scan_directory(path)

