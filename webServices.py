import sys
sys.path.append('lib')

from hosts import Hosts
from appLogger import AppLogger
from netLogger import NetLogger
import time
from flask import Flask,send_file

# Initialize class instances
hosts = Hosts()
netLogger = NetLogger()
appLogger = AppLogger()

app = Flask(__name__)

@app.route('/hostStatus')
def getHostStatus():
    print(hosts.getHostStatus())
    return hosts.getHostStatus(), 200


@app.route('/history/<start>/<id>/<type>')
def getHistory( start, id, type):
    gc.collect()
    return netLogger.getHistory(int(start), int(id), type), 200


@app.route('/host/<id>')
def getHost( id):
    return hosts.getHost(int(id))


@app.post('/host/add')
def addHost():
    newHostId = hosts.addHost(request.json)
    return str(newHostId), 200


@app.post('/host/update')
def updateHost():
    updatedHostId = hosts.updateHost(request.json)
    return str(updatedHostId), 200


@app.delete('/host/<id>')
def deleteHost( id):
    deletedHostId = hosts.deleteHost(id)
    return str(deletedHostId), 200


@app.route('/log')
def log():
    return send_file(appLogger.getFileName())


@app.route('/log/clear')
def clearSysLog():
    appLogger = AppLogger()
    appLogger.clearLog()
    appLogger.writeLogLine("Log Cleared " + str(gc.mem_free()))
    return "OK", 200,  {'Content-Type': 'text/html'}


@app.before_request
def func():
    global skipTestTimestamp
    skipTestTimestamp = time.time() + 10


@app.after_request
def func( response):
    response.headers.update({"Access-Control-Allow-Origin": "*"})
    return response


@app.route('/')
def net_probe_ui_index():
    return send_file('net-probe-ui/index.html')


@app.route('/<path:path>')
def net_probe_ui_static( path):
    if '..' in path:
        return 'Not found', 404
    return send_file('net-probe-ui/' + path)


if __name__ == '__main__':
    app.run(host='0.0.0.0')