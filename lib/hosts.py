import json
import os


class Hosts:
    # hosts data
    HOSTS_FILE = "hosts.json"
    HOSTSTESTS_FILE = "hostsTests.json"
    hosts = []
    maxId = 0
    # host test scheduling
    lastHostTested = 0
    hostsTests = []

    def __init__(self):
        self.getHosts()

    def file_or_dir_exists(self, filename):
        try:
            os.stat(filename)
            return True
        except OSError:
            return False

    #  ***************************
    # hostsTests specific routines

    def buildHostsTests(self):
        self.getHosts()
        # Build a new host tests array based on hosts data
        self.hostsTests = []
        for host in self.hosts:
            self.addHostTests(host["id"])
        self.saveHostsTests()

    def addHostTests(self, id):
        host = self.getHost(id)
        hostTests = {"id": host["id"],
                     "lastPing": 0, "pingRTL": 0, "pingSuccess": False, "lastBing": 0, "bingBPS": 0, "bingRTL": 0, "bingSuccess": False, "lastWeb": 0, "webMS": 0, "webMatch": False, "webSuccess": False}
        self.hostsTests.append(hostTests)

    def getHostTests(self, id):
        for hostTests in self.hostsTests:
            if hostTests["id"] == id:
                return(hostTests)
        return {}

    def updateHostTests(self, updatedHostTests):
        # Updated a hostTests based on the updated host's id
        for hostTests in self.hostsTests:
            if hostTests["id"] == updatedHostTests["id"]:
                self.hostsTests.remove(hostTests)
                self.hostsTests.append(updatedHostTests)
        self.saveHostsTests()

    def saveHostsTests(self):
        # Write a copy of hosts tests data after each update
        with open(self.HOSTSTESTS_FILE, "w") as hostsTestsFile:
            hostsTestsFile.write(json.dumps(self.hostsTests))

    def loadHostsTests(self):
        # Read hosts tests data 
        if self.file_or_dir_exists(self.HOSTSTESTS_FILE):
            with open(self.HOSTSTESTS_FILE, "r") as hostsTestsFile:
                self.hostsTests = json.loads(hostsTestsFile.read())

        

    def getId(self, obj):
        return obj["id"]

    def findNextHostToTest(self):
        self.hostsTests.sort(key=self.getId)
        nextFound = False
        for hostTests in self.hostsTests:
            if hostTests["id"] > self.lastHostTested:
                nextFound = True
                self.lastHostTested = hostTests["id"]
                break
        if not nextFound:
            for hostTests in self.hostsTests:
                if hostTests["id"] > 0:
                    nextFound = True
                    self.lastHostTested = hostTests["id"]
                    break
        if not nextFound:
            # Not really needed
            self.lastHostTested = 0
        return self.lastHostTested

    #  *************
    # hosts routines

    def setMaxId(self):
        # Find the maximum id
        self.maxId = 0
        for host in self.hosts:
            if host["id"] > self.maxId:
                self.maxId = host["id"]

    def getHosts(self):
        if not self.file_or_dir_exists(self.HOSTS_FILE):
            raise Exception("File required: " + self.HOSTS_FILE)

        with open(self.HOSTS_FILE, "r") as hostsFile:
            self.hosts = json.loads(hostsFile.read())
            self.setMaxId()

    def getHost(self, id):
        self.getHosts()
        for host in self.hosts:
            if host["id"] == id:
                return(host)
        return {}

    def updateHost(self, updatedHost):
        # Updated a host based on the updated host's id
        for host in self.hosts:
            if host["id"] == updatedHost["id"]:
                self.hosts.remove(host)
                self.hosts.append(updatedHost)
                # self.setMaxId()
                self.writeHosts()
        return int(host["id"])

    def deleteHost(self, id):
        print("deleteHost:", id)
        for host in self.hosts:
            if int(host["id"]) == int(id):
                self.hosts.remove(host)
                self.setMaxId()
                self.writeHosts()
        # Also update hostsTests
        for hostTests in self.hostsTests:
            if int(hostTests["id"]) == int(id):
                self.hostsTests.remove(hostTests)
        self.saveHostsTests()
        return id

    def addHost(self, host):
        host["id"] = self.maxId + 1
        self.hosts.append(host)
        self.setMaxId()
        self.writeHosts()
        # Also update hostsTests
        self.addHostTests(host["id"])
        self.saveHostsTests()
        return int(host["id"])

    def writeHosts(self):
        with open(self.HOSTS_FILE, "w") as hostsFile:
            hostsFile.write(json.dumps(self.hosts))

    def getHostStatus(self):
        #     # Return merged version of the hosts with their most recent test results
        hosts = []
        for host in self.hosts:
            hostTests = self.getHostTests(host["id"])
            hostTests["address"] = host["address"]
            hosts.append(hostTests)
        return hosts
