import csv

with open("data/mock100.csv","w") as f:
    f.write("pid,cid,weight,val\n")
    for i in range(100):
        for j in range(5):
            f.write(f"{i},{j},1,Lorem ipsum dolor sit amet consectetur adipiscing elit\n")