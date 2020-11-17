import flask
#import flask_cors
import sys
import jsonpickle
import json
import logging
import config
import threading
import logging
from npnearest import NPNearest
from npcompare import NPComparer

print("NP REST")
print("=======")
logging.info('Starting NPRest')
try:
    app: flask.Flask = flask.Flask(__name__)
    #flask_cors.CORS(app)
    cli = sys.modules['flask.cli']
    cli.show_server_banner = lambda *x: None
    lock = threading.RLock()
    np = NPNearest(config.h_file)
except Exception as ex:
    logging.fatal(ex)

def jsonify(o):
    js = jsonpickle.dumps(o, False)
    dico = json.loads(js)
    return flask.jsonify(dico)

@app.route("/", methods=['GET'])
def autodoc():
    s=f"<html><body><h1>NP Rest {config.version}</h1>"
    for rule in app.url_map.iter_rules():
        s += f"{rule.methods} <a href='http://localhost:{config.port}{rule}'>{rule}</a> {rule.arguments}<br/>"
    s+="</body></html>"
    return s

@app.route("/ping", methods=['GET'])
def ping():
    return "pong"

@app.route("/version", methods=['GET'])
def version():
    return config.version

@app.route("/product/<int:id>", methods=['GET'])
def get_product(id):
    try:
        p = np.get_by_id(id)
        return jsonify(p)
    except KeyError:
        return flask.abort(404)

@app.route("/nearests/<int:id>/<int:nb>", methods=['GET'])
def nearests_nb(id, nb):
    try:
        res = np.search(id,take=nb)
        return flask.jsonify(res)
    except KeyError:
        logging.warn(f"nbrest.nearests id:{id} not found")
        return flask.abort(404)

@app.route("/nearests/<int:id>", methods=['GET'])
def nearests(id):
    return nearests_nb(id, 10)

@app.route("/compare/<int:id1>/<int:id2>", methods=['GET'])
def compare(id1, id2):
    try:
        p1 = np.get_by_id(id1)
        p2 = np.get_by_id(id2)
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
    with lock:
        logging.warn("Reset")
        np.reset()
    return flask.jsonify(len(np.db))

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=config.port, threaded=True, debug=config.debug, use_reloader=False)
    except Exception as ex:
        logging.fatal(ex)