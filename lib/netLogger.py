import os
import time
import gc
from appLogger import AppLogger


class NetLogger:

    FILE_PREFIX = '/data/logger/'

    def __init__(self):
        pass

    def file_or_dir_exists(self, filename):
        try:
            os.stat(filename)
            return True
        except OSError:
            return False

    def getNDFileName(self, id, type):
        # return the file name to be used for todays netdata records for the host id
        # e.g. nd20230602bing002.tab
        now = time.localtime()
        NDFileName = self.FILE_PREFIX + \
            "nd{}{:0>2}{:0>2}{}{:0>3}.tab".format(
                now[0], now[1], now[2], type, id)
        return NDFileName

    def loggerLineBuilder(self, netLoggerRecord, quiet=True):
        loggerLine = ""
        not quiet and print(netLoggerRecord)
        type = netLoggerRecord["type"]
        if type == "ping":
            if netLoggerRecord["success"]:
                loggerLine = "{}\t{}\n".format(
                    int(time.time()), netLoggerRecord["rtl"])
            else:
                loggerLine = "{}\t{}\n".format(int(time.time()), -1)
        if type == "bing":
            loggerLine = "{}\t{}\t{}\n".format(
                int(time.time()), netLoggerRecord["bps"], netLoggerRecord["rtl"])
        if type == "web":
            if netLoggerRecord["success"]:
                loggerLine = "{}\t{}\t{}\t{}\n".format(
                    int(time.time()), netLoggerRecord["ms"], netLoggerRecord["match"], netLoggerRecord["status"])
            else:
                loggerLine = "{}\t{}\t{}\t{}\n".format(
                    int(time.time()), -1, False, -1)
        not quiet and print(loggerLine)
        return loggerLine

    def writeloggerRecord(self, netLoggerRecord, quiet=True):
        # Write a new network test results data record to
        # the appropriate netData file.

        if "id" not in netLoggerRecord:
            raise Exception("id missing from netLoggerRecord")
        if "type" not in netLoggerRecord:
            raise Exception("type missing from netLoggerRecord")
        if "success" not in netLoggerRecord:
            raise Exception("success missing from netLoggerRecord")
        if not (netLoggerRecord["type"] == "ping" or netLoggerRecord["type"] == "bing" or netLoggerRecord["type"] == "web"):
            raise Exception(
                "invalid netLoggerRecord type, must be ping, bing or web")
        loggerLine = self.loggerLineBuilder(netLoggerRecord, quiet)
        netDataLoggerFileName = self.getNDFileName(
            netLoggerRecord["id"], netLoggerRecord["type"])
        with open(netDataLoggerFileName, "a") as netDataLoggerFile:
            netDataLoggerFile.write(loggerLine)

    def getStartOfDay(self, timestamp):
        startOfDay = timestamp - \
            (time.localtime(timestamp)[3] * 60 * 60) - \
            (time.localtime(timestamp)[4] * 60) + 1
        return startOfDay

    def getStartOfHour(self, timestamp):
        startOfHour = timestamp - \
            (time.localtime(timestamp)[4] * 60) - \
            (time.localtime(timestamp)[5]) + 1
        return startOfHour

    def calcStatistics(self, values):
        mean = sum(values)/len(values)
        count = len(values)
        values.sort()
        P50Index = int(count * 0.5)
        P10Index = int(count * 0.1)
        P90Index = int(count * 0.9)
        return ({"v": mean, "p50": values[P50Index], "p90": values[P90Index], "p10": values[P10Index]})

    def getHistory(self, startTimestamp, id, type):
        # summarize based on hours of data selected
        # 12 hours no summary
        # 12-72 hours do hourly summary
        # >72 hours do daily summary

        # by default report on rtl for ping, bps for bing and ms for web
        # if summarizing also show average value, and the 20,50,80the percental values

        gc.collect()

        SECONDS_IN_HOUR = 60*60
        SECONDS_IN_DAY = 60*60*24

        entries = []
        values = []
        lastSummaryTime = 0

        begin = startTimestamp
        end = int(time.time())

        hoursHistory = (end-begin)/SECONDS_IN_HOUR
        summaryType = "X"  # x = no summary
        if hoursHistory >= 48 and hoursHistory < 120:
            summaryType = "H"
            lastSummaryTime = self.getStartOfHour(startTimestamp)
        if hoursHistory >= 120:
            summaryType = "D"
            lastSummaryTime = self.getStartOfDay(startTimestamp)

        # Read all the logger files in time range for the host and test type
        try:
            print("getHistory:",startTimestamp,end)
            for fileDate in range(self.getStartOfDay(startTimestamp), end, SECONDS_IN_DAY):
                localFileDate = time.localtime(fileDate)
                logName = self.FILE_PREFIX + "nd{}{:0>2}{:0>2}{}{:0>3}.tab".format(
                    localFileDate[0], localFileDate[1], localFileDate[2], type, id)
                if self.file_or_dir_exists(logName):
                    with open(logName, "r") as loggingFile:
                        # filter out entries that are not in required range
                        # loggingFileLines = loggingFile.readlines()
                        logline = loggingFile.readline()
                        while logline:
                            lineValues = logline.split("\t")
                            # Output a summary?
                            timestamp = int(float(lineValues[0]))
                            value = int(lineValues[1])
                            if (summaryType == "H" and (timestamp - lastSummaryTime) > SECONDS_IN_HOUR) \
                                    or (summaryType == "D" and (timestamp - lastSummaryTime) > SECONDS_IN_DAY):
                                # Add a summary entry
                                if len(values) > 0:
                                    entry = self.calcStatistics(values)
                                    entry["ts"] = lastSummaryTime
                                    entries.append(entry)
                                # Reset summary data
                                values = []
                                # Calculate the start of the next summary time
                                if summaryType == "H":
                                    # set to beginning or the hour
                                    lastSummaryTime = self.getStartOfHour(
                                        timestamp)
                                else:
                                    # set to beginning or the day
                                    lastSummaryTime = self.getStartOfDay(
                                        timestamp)

                            if timestamp >= begin and timestamp <= end and value > 0:
                                if summaryType == "X":
                                    entries.append(
                                        {"ts": timestamp, "v": value})
                                else:
                                    # Store data values for summarization
                                    values.append(value)
                            logline = loggingFile.readline()
            # If we have data still to be summarized for partial hour or day
            if len(values) > 0:
                entry = self.calcStatistics(values)
                entry["ts"] = lastSummaryTime
                entries.append(entry)
            return entries
        except Exception as e:
            print("getHistory e:",e)
            appLogger = AppLogger()
            appLogger.writeException(e)
            return entries
