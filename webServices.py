import sys
sys.path.append('/home/pi/netProbeLinux/lib')

from hosts import Hosts
from appLogger import AppLogger
from netLogger import NetLogger
import time
from flask import Flask,send_file,request
from flask_cors import CORS

# Initialize class instances
hosts = Hosts()
netLogger = NetLogger()
appLogger = AppLogger()

app = Flask(__name__)
CORS(app, allowed_origins="*", allow_credentials=True)

@app.route('/hostStatus')
def getHostStatus():
    hosts.loadHostsTests()
    return hosts.getHostStatus(), 200


@app.route('/history/<start>/<id>/<type>')
def getHistory( start, id, type):
    return netLogger.getHistory(int(start), int(id), type), 200


@app.route('/host/<id>')
def getHost( id):
    return hosts.getHost(int(id))


@app.post('/host/add')
def addHost():
    newHost = hosts.addHost(request.get_json())
    print("addHost",newHost)
    return str(newHost), 200


@app.post('/host/update')
def updateHost():
    updatedHostId = hosts.updateHost(request.get_json())
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
    appLogger.writeLogLine("Log Cleared ")
    return "OK", 200,  {'Content-Type': 'text/html'}


@app.before_request
def func():
    global skipTestTimestamp
    skipTestTimestamp = time.time() + 10


@app.after_request
def func( response):
    if (request.method!="OPTIONS"):
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
    appLogger.writeLogLine("* Start webServices *")
    app.run(host='0.0.0.0',port=80)