import config
import flask
import sys
import jsonpickle
import json
import threading
import logging
import socket
from npproductnearest import NPNearest
from npproductcompare import NPComparer
# from npimnearest import NPImageNearest
# from npimcomparer import NPImageComparer

def jsonify(o):
    js = jsonpickle.dumps(o, False)
    dico = json.loads(js)
    return flask.jsonify(dico)

app:flask.Flask = flask.Flask(__name__)

@app.route("/", methods=['GET'])
def autodoc():
    s=f"<html><body><h1>NP Rest V{config.version}</h1>"
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    s+= f"<p>{host}@{ip}:{config.port}</p>"
    l = list(app.url_map.iter_rules())
    l.sort(key=lambda x: x.rule)
    for rule in l:
        s += f"{rule.methods} <a href='http://{ip}:{config.port}{rule.rule}'>{rule.rule.replace('<','&lt;').replace('>','&gt;')}</a><br/>"
    s+="</body></html>"
    return s

@app.route("/ping", methods=['GET'])
def ping():
    return "pong"

@app.route("/version", methods=['GET'])
def version():
    return config.version

@app.route("/sentence/compare/<s1>/<s2>", methods=['GET'])
def compare_sentence(s1, s2):
    return flask.jsonify(npproduct.comp.compare_value_gestalt(s1, s2))

@app.route("/sentence/compare/list", methods=['POST'])
def compare_sentences():
    #[["il fait beau","le soleil"],["il fait encore bieau","le sol"]]
    json = flask.request.json
    return flask.jsonify([npproduct.comp.compare_value_gestalt(s1, s2) for s1, s2 in zip(json[0], json[1])])

@app.route("/product/all", methods=['GET'])
def get_all():
    l = npproduct.get_ids()
    return flask.jsonify(l)

@app.route("/product/<int:id>", methods=['GET'])
def get_product(id):
    try:
        p = npproduct.get_by_id(id)
        return jsonify(p)
    except KeyError:
        return flask.abort(404)

@app.route("/product", methods=['PUT', 'POST'])
def add_update_product():
    p = flask.request.json
    npproduct.db[p.id]=p

@app.route("/product/<int:pid>/car/<int:cid>", methods=['PUT'])
def update_product_car(pid, cid):
    try:
        p = npproduct.get_by_id(pid)
        car = [c for c in p.l if c.id == cid][0]
        car.val = str(flask.request.json)
        car.h = None
        return jsonify(p)
    except KeyError:
        return flask.abort(404)

@app.route("/product/<int:id>", methods=['DELETE'])
def delete_product(id):
    try:
        p = npproduct.get_by_id(id)
        del npproduct.db[p.id]
        return flask.jsonify(True)
    except KeyError:
        return flask.abort(404)

@app.route("/product/nearests/<int:id>/<int:nb>", methods=['GET'])
def product_nearests_nb(id, nb):
    try:
        res = npproduct.search(id, take=nb)
        return flask.jsonify(res)
    except KeyError:
        logging.warning(f"nbrest.nearests id:{id} not found")
        return flask.abort(404)

@app.route("/product/nearests/<int:id>", methods=['GET'])
def product_nearests(id):
    return product_nearests_nb(id, 10)

@app.route("/product/compare/<int:id1>/<int:id2>", methods=['GET'])
def compare(id1, id2):
    try:
        p1 = npproduct.get_by_id(id1)
        p2 = npproduct.get_by_id(id2)
        comparer = NPComparer()
        res = {}
        res["USE"] = {"score" : comparer.compare_product(p1, p2), "details" : comparer.compare_product_to_scores(p1, p2)}
        res["Gestalt"] = {"score" : comparer.compare_product_gestalt(p1, p2), "details" : comparer.compare_product_gestalt_to_scores(p1, p2)}
        res["Total"] = (comparer.compare_product(p1, p2) + comparer.compare_product_gestalt(p1, p2)) / 2
        res["Cids"] = [c.id for c in p1.l]
        return flask.jsonify(res)
    except KeyError:
        return flask.abort(404)


# @app.route("/image/all", methods=['GET'])
# def iget_all():
#     l = npim.get_iids()
#     return flask.jsonify(l)
#
# @app.route("/image/compare/<int:id1>/<int:id2>", methods=['GET'])
# def icompare(id1, id2):
#     try:
#         i1 = npim.get_im_by_iid(id1)
#         i2 = npim.get_im_by_iid(id2)
#         comparer = NPImageComparer()
#         res = {}
#         res["diff"] = comparer.diff(i1, i2)
#         res["score"] = comparer.compare(i1, i2)
#         return flask.jsonify(res)
#     except KeyError:
#         return flask.abort(404)
#
# @app.route("/image/nearests/<int:id>/<int:nb>", methods=['GET'])
# def image_nearests_nb(id, nb):
#     try:
#         res = npim.search_by_im(id, take=nb)
#         return flask.jsonify(res)
#     except KeyError:
#         logging.warning(f"nbrest.image_nearests id:{id} not found")
#         return flask.abort(404)
#
# @app.route("/image/nearests/<int:id>", methods=['GET'])
# def image_nearests(id):
#     return image_nearests_nb(id, 10)
#
# @app.route("/image/product/nearests/<int:id>/<int:nb>", methods=['GET'])
# def product_byimage_nearests_nb(id, nb):
#     try:
#         res = npim.search_by_product(id, take=nb)
#         return flask.jsonify(res)
#     except KeyError:
#         logging.warning(f"nbrest.product_byimage_nearests id:{id} not found")
#         return flask.abort(404)
#
# @app.route("/image/product/nearests/<int:id>", methods=['GET'])
# def product_byimage_nearests(id):
#     return product_byimage_nearests_nb(id, 10)

@app.route("/reset", methods=['GET'])
def reset():
    logging.warning("Reset")
    with lock:
        npproduct.reset()
    # with lock:
    #     npim.reset()
    return flask.jsonify(len(npproduct.db))

if __name__ == '__main__':
    print("NP REST")
    print("=======")
    print(f"V{config.version}")
    logging.info('Starting NPRest')
    try:
        cli = sys.modules['flask.cli']
        cli.show_server_banner = lambda *x: None
        lock = threading.RLock()
        npproduct = NPNearest(config.product_h_file)
        #npim = NPImageNearest(config.image_h_file)
        app.run(host='0.0.0.0', port=config.port, threaded=True, debug=config.debug, use_reloader=False)
    except Exception as ex:
        logging.fatal(ex)