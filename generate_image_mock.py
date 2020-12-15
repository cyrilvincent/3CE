import os

with open("data/imagemock.txt", "w") as f:
    f.write("family_id\tproduct_id\timage_id\timage_path\n")
    i = 0
    for file  in os.listdir("images"):
        t= file.upper()
        if ".JPG" in t or ".GIF" in t or ".PNG" in t or ".JPEG" in t or ".BMP" in t or ".SVG" in t:
            f.write(f"1\t{i//2}\t{i}\t./{file}\n")
        i+=1
