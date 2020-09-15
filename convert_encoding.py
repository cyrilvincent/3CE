#pip install chardet
#chardetect fichier-cyril.txt
#fichier-cyril.txt: ISO-8859-1 with confidence 0.73
with open("data/fichier-cyril.txt", encoding="ISO-8859-1") as f:
    s = f.read()
    with open("data/data-utf8.txt", "w", encoding="utf8") as f2:
        f2.write(s)

