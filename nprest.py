import config
import flask
#import flask_cors
import sys
import jsonpickle
import json
import logging
import threading
import logging
import socket
from npproductnearest import NPNearest
from npproductcompare import NPComparer
from npimnearest import NPImageNearest

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
    for rule in app.url_map.iter_rules():
        s += f"{rule.methods} <a href='http://{ip}:{config.port}{rule}'>{rule}</a> {rule.arguments}<br/>"
    s+="</body></html>"
    return s

@app.route("/ping", methods=['GET'])
def ping():
    return "pong"

@app.route("/version", methods=['GET'])
def version():
    return config.version

@app.route("/product/all", methods=['GET'])
def get_all():
    l = npproduct.get_ids()
    return jsonify(l)

@app.route("/product/<int:id>", methods=['GET'])
def get_product(id):
    try:
        p = npproduct.get_by_id(id)
        return jsonify(p)
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
        res["USE"] = {"score" : comparer.compare(p1, p2), "details" : comparer.compp(p1, p2)}
        res["Gestalt"] = {"score" : comparer.comparel(p1, p2), "details" : comparer.comppl(p1, p2)}
        res["Total"] = (comparer.compare(p1, p2) + comparer.comparel(p1, p2)) / 2
        return flask.jsonify(res)
    except KeyError:
        return flask.abort(404)

@app.route("/reset", methods=['GET'])
def reset():
    logging.warning("Reset")
    with lock:
        npproduct.reset()
    return flask.jsonify(len(npproduct.db))

if __name__ == '__main__':
    print("NP REST")
    print("=======")
    print(f"V{config.version}")
    logging.info('Starting NPRest')
    try:
        # flask_cors.CORS(app)
        cli = sys.modules['flask.cli']
        cli.show_server_banner = lambda *x: None
        lock = threading.RLock()
        npproduct = NPNearest(config.product_h_file)
        app.run(host='0.0.0.0', port=config.port, threaded=True, debug=config.debug, use_reloader=False)
    except Exception as ex:
        logging.fatal(ex)