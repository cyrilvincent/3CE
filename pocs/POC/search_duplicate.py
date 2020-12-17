import cyrilload

def search_duplicate(db, cid = 0):
    dico = {}
    for pid in db.keys():
        c = db[pid].get_car_by_id(cid)
        if c != None:
            if c.val in dico:
                dico[c.val].append(pid)
            else:
                dico[c.val] = [pid]
    res = dict(dico)
    for val in dico.keys():
        if len(dico[val]) < 2:
            del res[val]
    return res

if __name__ == '__main__':
    ncar = 6
    print(f"NP Search duplicate")
    print("===================")
    db = cyrilload.load("../../data/data.pickle")
    pid = list(db.keys())[0]
    print(f"Carac at the position {ncar} found cid={db[pid].l[ncar].id}")
    res = search_duplicate(db, db[pid].l[ncar].id)
    print(res)
    for k in res.keys():
        print(f'pid: {res[k]} => "{k[:40]}"')