
import sys
sys.path.append('lib')

from hosts import Hosts
from appLogger import AppLogger
from netLogger import NetLogger
import time
import bing 
import webPage
import gc

# Initialize class instances
hosts = Hosts()
netLogger = NetLogger()
appLogger = AppLogger()

def scheduler(quiet=True):
    while True:
        nextHostToTest = hosts.findNextHostToTest()
        host = hosts.getHost(nextHostToTest)
        not quiet and print(
            host["address"])
        hostTests = hosts.getHostTests(nextHostToTest)
        if "ping" in host:
            ping = host["ping"]
            hostTests["pingActive"] = ping["active"]
            if ping["active"]:
                if hostTests["lastPing"] + (ping["intervalMinutes"] * 60) < time.time():
                    hostTests["lastPing"] = time.time()
                    pingResult = bing.getLowestPing(host["address"],quiet=quiet)
                    if pingResult == None:
                        hostTests["pingSuccess"] = False
                        netLoggerRecord = {
                            "id": host["id"], "type": "ping",  "success": False}
                    else:
                        hostTests["pingSuccess"] = True
                        hostTests["pingRTL"] = int(pingResult)
                        netLoggerRecord = {
                            "id": host["id"], "type": "ping", "rtl": int(pingResult), "success": True}
                    netLogger.writeloggerRecord(netLoggerRecord)
        if "bing" in host:
            bingTest = host["bing"]
            hostTests["bingActive"] = bingTest["active"]
            if bingTest["active"]:
                if hostTests["lastBing"] + (bingTest["intervalMinutes"] * 60) < time.time():
                    hostTests["lastBing"] = time.time()
                    bingResult = bing.bing(
                        host["address"], maxSize=5000,quiet=quiet)
                    if bingResult[0] == -1:
                        hostTests["bingSuccess"] = False
                        netLoggerRecord = {
                            "id": host["id"], "type": "bing", "bps": bingResult[0], "rtl":  int(bingResult[1]),  "success": False}
                    else:
                        hostTests["bingSuccess"] = True
                        hostTests["bingBPS"] = int(bingResult[0])
                        hostTests["bingRTL"] = int(bingResult[1])
                        netLoggerRecord = {
                            "id": host["id"], "type": "bing", "bps": bingResult[0], "rtl":  int(bingResult[1]),  "success": True}
                    netLogger.writeloggerRecord(netLoggerRecord)
        if "web" in host:
            web = host["web"]
            hostTests["webActive"] = web["active"]
            if web["active"]:
                if hostTests["lastWeb"] + (web["intervalMinutes"] * 60) < time.time():
                    hostTests["lastWeb"] = time.time()
                    if web["https"]:
                        target = "https://"
                    else:
                        target = "http://"
                    target += host["address"] + web["url"]
                    webResult = webPage.webPage(
                        target, web["match"], quiet=quiet)
                    if webResult == None:
                        hostTests["webSuccess"] = False
                        netLoggerRecord = {
                            "id": host["id"], "type": "web",  "success": False}
                    else:
                        hostTests["webSuccess"] = True
                        hostTests["webMS"] = int(webResult[0])
                        hostTests["webMatch"] = webResult[1]
                        netLoggerRecord = {"id": host["id"], "type": "web", "ms": int(webResult[0]),
                                            "match": webResult[1], "status": webResult[2], "success": True}
                    netLogger.writeloggerRecord(netLoggerRecord)
        hosts.updateHostTests(hostTests)
        time.sleep(5)

if __name__ == '__main__':
    appLogger.writeLogLine("* Restart *")
    # Fire up scheduler to run forever
    scheduler(quiet=False)
