import config
import flask
import sys
import shutil
import urllib.request
import logging
import socket
from npproductparser import NPParser
from npproductnearest import NPNearestPool, NPNearestNN

app: flask.Flask = flask.Flask(__name__)

@app.route("/", methods=['GET'])
def autodoc():
    s=f"<html><body><h1>NP Rest Indexer V{config.version}</h1>"
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    s += f"<p>{host}@{ip}:{config.indexer_port}</p>"
    l = list(app.url_map.iter_rules())
    l.sort(key=lambda x: x.rule)
    for rule in l:
        s += f"<a href='http://{ip}:{config.indexer_port}{rule.rule}'>{rule.rule.replace('<', '&lt;').replace('>', '&gt;')}</a> {rule.methods}<br/>"
    s+="</body></html>"
    return s

@app.route("/ping", methods=['GET'])
def ping():
    return "pong"

@app.route("/version", methods=['GET'])
def version():
    return config.version

@app.route("/indexer/<instance>", methods=['GET'])
def index(instance):
    logging.info(f"Indexer {instance}")
    try:
        path = config.product_data_file.replace("{instance}", instance)
        npparser.parse(path)
        npparser.normalize()
        npparser.h()
        npparser.save(prefix="temp", method="pickle")
        name = path.split(".")[0]
    except Exception as ex:
        logging.fatal(ex)
    try:
        shutil.move(name+".h.pickle", name+".bak.pickle")
        logging.info(f"Creating {name}.h.pickle")
        shutil.move(name+".temp.pickle", name+".h.pickle")
    except:
        logging.error("Cannot move h")
    if len(npparser.db) < config.product_nn_limit:
        try:
            use2 = len(npparser.db) < config.use2_limit
            logging.info(f"Indexer NN with use2: {use2}")
            nn = NPNearestNN(name+".h.pickle", use2=use2)
            nn.train()
            nn.save()
        except Exception as ex:
            logging.error(f"NN NOK {ex}")
    logging.info(f"Call reset")
    if instance not in config.pool:
        logging.error(f"Instance {instance} not in config.pool, please update config.py")
    else:
        try:
            npproductpool[instance].reset()
        except Exception as ex:
            logging.error(f"Call reset nok: {ex}")
        try:
            with urllib.request.urlopen(f"http://localhost:{config.port}/reset/{instance}") as response:
                nb = response.read()
                print(f"Call reset ok: {nb}")
        except Exception as ex:
            logging.warning(f"Call HTTP reset nok: {ex}, perhaps the server {config.port} is not started")
    return flask.jsonify(len(npparser.db))

@app.route("/indexer/all", methods=['GET'])
def index_all():
    logging.info(f"Indexer All")
    for instance in config.pool:
        index(instance)
    return flask.jsonify(len(config.pool))

@app.route("/shutdown", methods=['GET'])
def shutdown():
    func = flask.request.environ.get('werkzeug.server.shutdown')
    if func is None:
        return "NOK"
    else:
        func()
        return "OK"

if __name__ == '__main__':
    print("NP Rest Indexer")
    print("===============")
    print(f"V{config.version}")
    logging.info("NPRestIndexer")
    cli = sys.modules['flask.cli']
    cli.show_server_banner = lambda *x: None
    npparser = NPParser()
    npproductpool = NPNearestPool()
    app.run(host='0.0.0.0', port=config.indexer_port, threaded=True, debug=config.debug, use_reloader=False)