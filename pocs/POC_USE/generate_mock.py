import csv

nb = 100000
nbcar = 3
with open(f"data/mock{nb}.txt","w") as f:
    f.write("product_id	carac_id	poids	valeur\n")
    for i in range(nb):
        for j in range(nbcar):
            f.write(f"{i}\t{j}\t1\tLorem ipsum délor sit amet consectetur adipiscing elit\n")