import config
import flask
import sys
import shutil
import urllib.request
import logging
import socket
from npproductparser import NPParser

app: flask.Flask = flask.Flask(__name__)

@app.route("/", methods=['GET'])
def autodoc():
    s=f"<html><body><h1>NP Rest Indexer V{config.version}</h1>"
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    s += f"<p>{host}@{ip}:{config.port}</p>"
    l = list(app.url_map.iter_rules())
    l.sort(key=lambda x: x.rule)
    for rule in l:
        s += f"{rule.methods} <a href='http://{ip}:{config.port}{rule.rule}'>{rule.rule.replace('<', '&lt;').replace('>', '&gt;')}</a><br/>"
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
    try:
        np.parse(config.product_data_file)
        np.normalize()
        np.h()
        np.save(prefix="temp", method="pickle")
        name = config.product_data_file.split(".")[0]
    except Exception as ex:
        logging.fatal(ex)
    try:
        shutil.move(name+".h.pickle",name+".bak.pickle")
    except:
        logging.warning("Cannot copy h to bak")
    try:
        logging.info(f"Creating {name}.h.pickle")
        shutil.move(name+".temp.pickle",name+".h.pickle")
    except:
        logging.error("Cannot copy temp to h")
    try:
        logging.info(f"Call reset")
        with urllib.request.urlopen(f"http://localhost:{config.port}/reset") as response:
            nb = response.read()
        print(f"Call reset ok: {nb}")
    except Exception as ex:
        logging.error(f"Call reset nok: {ex}")
    return flask.jsonify(len(np.db))

if __name__ == '__main__':
    print("NP Rest Indexer")
    print("===============")
    print(f"V{config.version}")
    logging.info("NPRestIndexer")
    try:
        cli = sys.modules['flask.cli']
        cli.show_server_banner = lambda *x: None
        np = NPParser()
        app.run(host='0.0.0.0', port=config.indexer_port, threaded=False, debug=config.debug, use_reloader=False)
    except Exception as ex:
        logging.fatal(ex)