import json
import pickle
import jsonpickle

def load(path):
    ext = path.split(".")[-1]
    print(f"Load {path}")
    if ext == "pickle":
        with open(path, "rb") as f:
            db = pickle.load(f)
    elif ext == "json":
        with open(path) as f:
            db = json.load(f)
    else:
        raise ValueError(f"Unknown extension {ext}")
    return db

def save(db, name, prefix="", method="pickle"):
    if prefix != "":
        name += f".{prefix}"
    if method == "pickle":
        name += ".pickle"
    elif method == "json" or method == "jsonpickle":
        name += ".json"
    elif method == "pretty":
        name += ".pretty.json"
    else:
        raise ValueError(f"Unknown method {method}")
    print(f"Save {name}")
    if method == "pickle":
        with open(name,"wb") as f:
            pickle.dump(db, f)
    else:
        with open(name,"w") as f:
            if method == "json":
                json.dump(db, f,indent = 4 if method == "pretty" else None)
            else:
                s = jsonpickle.dumps(db, unpicklable=False,indent=4)
                f.write(s)
