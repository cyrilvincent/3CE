import cyrilload

def search_duplicate(db, ncar = 0):
    dico = {}
    for pid in db.keys():
        try:
            c = db[pid].l[ncar]
            if c.val in dico:
                dico[c.val].append(pid)
            else:
                dico[c.val] = [pid]
        except:
            pass
    res = dict(dico)
    for val in dico.keys():
        if len(dico[val]) < 2:
            del res[val]
    return res

if __name__ == '__main__':
    ncar = 0
    print(f"NP Search duplicate")
    print("===================")
    db = cyrilload.load("data/data.pickle")
    pid = list(db.keys())[0]
    print(f"Carac at the position {0} found cid {db[pid].l[0].id}")
    res = search_duplicate(db, ncar)
    print(res)
    for k in res.keys():
        print(f'pid: {res[k]} => "{k[:40]}"')