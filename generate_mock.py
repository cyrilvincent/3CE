import csv

with open("data/mock.csv","w") as f:
    f.write("pid,cid,weight,val\n")
    for i in range(10000):
        for j in range(5):
            f.write(f"{i},{j},1,Lorem ipsum dolor sit amet consectetur adipiscing elit\n")