import json
import pickle
import jsonpickle
import logging

def load(path):
    """
    Intelligent loading data from pickle and json
    :param path: db file path
    :return: the pickle object
    """
    ext = path.split(".")[-1]
    logging.info(f"Load {path}")
    try:
        if ext == "pickle":
            with open(path, "rb") as f:
                db = pickle.load(f)
        elif ext == "json":
            with open(path) as f:
                db = json.load(f)
        else:
            raise ValueError(f"Unknown extension {ext}")
            logging.FATAL(f"cyrilload.load: Unknown extension {ext} in {path}")
    except Exception as ex:
        logging.FATAL(f"cyril.load: {ex}")
    return db

def save(db, name, prefix="", method="pickle"):
    """
    Intelligent data save
    :param db: The object to save
    :param name: File name without extension
    :param prefix: extension prefix file.prefix.extension
    :param method: pickle | jsonpickle | json | pretty (pretty json)
    """
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
        logging.FATAL(f"cyrilload.save: Unknown extension {ext} in {path}")
    print(f"Save {name}")
    try:
        if method == "pickle":
            with open(name,"wb") as f:
                pickle.dump(db, f)
        else:
            with open(name,"w") as f:
                if method == "json" or method == "pretty":
                    try:
                        json.dump(db, f,indent = 4 if method == "pretty" else None)
                    except TypeError:
                        s = jsonpickle.dumps(db, unpicklable=False, indent = 4 if method == "pretty" else None)
                        f.write(s)
                else:
                    s = jsonpickle.dumps(db, unpicklable=False,indent=4)
                    f.write(s)
    except Exception as ex:
        logging.FATAL(f"cyrilload.save: {ex}")
        raise ex
