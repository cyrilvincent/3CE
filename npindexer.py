import flask
import sys
import shutil
import urllib.request
import config
from npparser import NPParser

print("NP Indexer")
print("==========")
app: flask.Flask = flask.Flask(__name__)
cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None
np = NPParser()

@app.route("/", methods=['GET'])
def autodoc():
    s="<html><body><h1>NP Indexer {config.version}</h1>"
    for rule in app.url_map.iter_rules():
        s += f"{rule.methods} <a href='http://localhost:{config.indexer_port}{rule}'>{rule}</a> {rule.arguments}<br/>"
    s+="</body></html>"
    return s

@app.route("/ping", methods=['GET'])
def ping():
    return "pong"

@app.route("/version", methods=['GET'])
def version():
    return config.version

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
        print(f"Call reset")
        with urllib.request.urlopen(f"http://localhost:{config.port}/reset") as response:
            _ = response.read()
        print(f"Call reset ok")
    except:
        print(f"Call reset nok")
    return flask.jsonify(len(np.db))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config.indexer_port, threaded=False, debug=config.debug, use_reloader=False)