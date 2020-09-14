import flask
import sys
import shutil
import urllib.request
import config
from npparser import NPParser
#pip install flask

print("NP Indexer")
print("==========")
app: flask.Flask = flask.Flask(__name__)
cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None

np = NPParser()

@app.route("/", methods=['GET'])
def autodoc():
    s="<html><body><h1>NP Indexer</h1>"
    for rule in app.url_map.iter_rules():
        s += f"{rule.methods} <a href='http://localhost:{config.indexer_port}{rule}'>{rule}</a> {rule.arguments}<br/>"
    s+="</body></html>"
    return s

@app.route("/ping", methods=['GET'])
def ping():
    return "pong"

@app.route("/indexer", methods=['GET'])
def index():
    np.parse(config.data_file)
    np.normalize()
    np.h()
    np.save(prefix="temp", method="pickle")
    name = config.data_file.split(".")[0]
    try:
        shutil.move(name+".h.pickle",name+".bak.pickle")
    except:
        pass
    shutil.move(name+".temp.pickle",name+".h.pickle")
    try:
        with urllib.request.urlopen(f"http://localhost:{config.port}/reset") as response:
            _ = response.read()
    except:
        pass
    return flask.jsonify(len(np.db))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config.indexer_port, threaded=False, debug=config.debug, use_reloader=False)