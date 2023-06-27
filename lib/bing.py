from pythonping import ping
import time
import traceback
import sys


def getLowestPing(host, samples=2, maxSize=16, timeout=5000, quiet=False):
    # Make a list containing the ping results for each of the ping samples
    if maxSize > 8164:
        return None
    pings = []
    failCnt = 0
    for x in range(samples):
        useDf = False
        if maxSize > 1460:
            useDf = True
        try:
            pingItem = ping(host, count=1, size=maxSize,
                            timeout=5, df=useDf).rtt_avg
        except:
            print("Exception in  Ping code:")
            print("-"*60)
            traceback.print_exc(file=sys.stdout)
            print("-"*60)
            pingItem = None
        if (pingItem == None or pingItem == 5):
            failCnt += 1
            if (failCnt >= 2):
                return None
        else:
            pings.append(pingItem)
        not quiet and print(
            "getLowestPing host %s size %u sample# %u result: " % (host, maxSize, x), pingItem)
        time.sleep(.5)
    # Review results for number of successful pings and get the lowest latency
    minPing = timeout

    for pingItem in pings:
        if (minPing > pingItem):
            minPing = pingItem
    return minPing * 1000


def bing(host, samples=5, maxSize=1460, timeout=5000, quiet=False):
    # perform required number of ping samples to the host using 16byte and maxsize packets
    # calculate and return bandwidth (bps) and latency (ms) based on the ping samples

    # Drop out straight away if any getLowestPings fail, no point calculating
    # Saves buffer allocations

    # return the bps value of -1 if failed bing, second value represents error

    # Check if maxsize works, if not than scale back to 1460
    if maxSize > 8164:
        maxSize = 8164
    testMaxSizeLatency = getLowestPing(host, samples, maxSize, timeout, quiet)
    if (testMaxSizeLatency == None or testMaxSizeLatency == timeout):
        #  scale back maxsize
        not quiet and print(
            "testMaxSizeLatency failed: scaling back maxSize to 1400")
        maxSize = 1400

    # Get latency
    latency = getLowestPing(host, samples, 16, timeout, quiet)
    if (latency == None or latency == timeout):
        not quiet and print("getlowestPing failed: latency == None")
        return (-1, -10)

    # Get Lowest target latencies
    target26 = getLowestPing(host, samples, 26, timeout, quiet)
    if (target26 == None or latency == timeout):
        not quiet and print("getlowestPing failed: target26 == None")
        return (-1, -14)
    targetMax = getLowestPing(host, samples, maxSize, timeout, quiet)
    if (targetMax == None or latency == timeout):
        not quiet and print("getlowestPing failed: targetMax == None")
        return (-1, -15)

    # Check Results before calculating
    if (target26 > targetMax):
        not quiet and print(
            "bing calculation not possable: target26 > targetMax")
        return (-1, -17)
    targetDelta = (targetMax - target26)
    not quiet and print("targetDelta:", targetDelta)

    deltaLatency = targetMax - target26
    if (deltaLatency <= 0):
        not quiet and print(
            "bing calculation not possable: deltaLatency <= 0")
        return (-1, -18)
    not quiet and print("deltaLatency:", deltaLatency)
    deltaPayloadBits = (maxSize-26) * 8
    not quiet and print("deltaPayloadBits:", deltaPayloadBits)
    bps = int(deltaPayloadBits * 2 * 1000 / deltaLatency)
    not quiet and print("bps:", bps)

    return (bps, latency)


# print("lowestPing:", getLowestPing(host="ftp.nz.debian.org", samples=5,
#                                    maxSize=1460, timeout=5000, quiet=False))

# print("bing:", bing(host="iqvia.com", samples=5,
#                     maxSize=1400, timeout=5000, quiet=False))
