import flask
import flask_cors
import sys
import jsonpickle
import json
import logging
from npnearest import NPNearest
from npcompare import NPComparer

#pip install flask
#pip install flask_cores
#pip install watchdog
#pip install jsonpickle

file = "data/mock.h.pickle"

print("NP REST")
print("=======")
app: flask.Flask = flask.Flask(__name__)
flask_cors.CORS(app)
cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None

try:
    port = int(sys.argv[0])
except ValueError:
    port = 5000
np = NPNearest(file)

def jsonify(o):
    js = jsonpickle.dumps(o, False)
    dico = json.loads(js)
    return flask.jsonify(dico)

@app.route("/", methods=['GET'])
def autodoc():
    s="<html><body><h1>NP Rest</h1>"
    for rule in app.url_map.iter_rules():
        s += f"{rule.methods} <a href='http://localhost:{port}{rule}'>{rule}</a> {rule.arguments}<br/>"
    s+="</body></html>"
    return s

@app.route("/ping", methods=['GET'])
def ping():
    return "pong"

@app.route("/product/<id>", methods=['GET'])
def get_product(id):
    try:
        p = np.get_by_id(id)
        return jsonify(p)
    except KeyError:
        return flask.abort(404)

@app.route("/nearests/<id>/<int:nb>", methods=['GET'])
def nearests_nb(id, nb):
    try:
        res = np.search(id,take=nb)
        return flask.jsonify(res)
    except KeyError:
        return flask.abort(404)

@app.route("/nearests/<id>", methods=['GET'])
def nearests(id):
    return nearests_nb(id, 10)

@app.route("/compare/<id1>/<id2>", methods=['GET'])
def compare(id1, id2):
    try:
        p1 = np.get_by_id(id1)
        p2 = np.get_by_id(id2)
        comparer = NPComparer()
        res = {}
        res["USE"] = {"score" : comparer.compare(p1, p2), "details" : comparer.compp(p1, p2)}
        res["Gestalt"] = {"score" : comparer.comparel(p1, p2), "details" : comparer.comppl(p1, p2)}
        return flask.jsonify(res)
    except KeyError:
        return flask.abort(404)

@app.route("/reset", methods=['GET'])
def reset():
    global np
    np = NPNearest(file)
    return flask.jsonify(len(np.db))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, threaded=True, debug=True, use_reloader=False)