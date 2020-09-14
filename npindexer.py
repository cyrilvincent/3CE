import flask
import sys
import shutil
import urllib.request
from npparser import NPParser
#pip install flask

file = "data/data.csv"

print("NP Indexer")
print("==========")
app: flask.Flask = flask.Flask(__name__)
cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None

try:
    port = int(sys.argv[0])
except ValueError:
    port = 5001
np = NPParser()

@app.route("/", methods=['GET'])
def autodoc():
    s="<html><body><h1>NP Indexer</h1>"
    for rule in app.url_map.iter_rules():
        s += f"{rule.methods} <a href='http://localhost:{port}{rule}'>{rule}</a> {rule.arguments}<br/>"
    s+="</body></html>"
    return s

@app.route("/ping", methods=['GET'])
def ping():
    return "pong"

@app.route("/indexer", methods=['GET'])
def index():
    np.parse(file)
    np.normalize()
    np.h()
    np.save(prefix="temp", method="pickle")
    name = file.split(".")[0]
    try:
        shutil.move(name+".h.pickle",name+".bak.pickle")
    except:
        pass
    shutil.move(name+".temp.pickle",name+".h.pickle")
    try:
        with urllib.request.urlopen("http://localhost:5000/reset") as response:
            _ = response.read()
    except:
        pass
    return flask.jsonify(len(np.db))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, threaded=False, debug=True, use_reloader=False)