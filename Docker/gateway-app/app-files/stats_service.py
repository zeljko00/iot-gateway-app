import time
import requests
import logging.config

logging.config.fileConfig('logging.conf')
errorLogger = logging.getLogger('customErrorLogger')
customLogger=logging.getLogger('customConsoleLogger')

class Stats:
    def __init__(self):
        self.dataBytes = 0
        self.dataBytesForwarded = 0
        self.dataRequests = 0

    def update_data(self, bytes, forwarded, requests):
        self.dataBytes += bytes
        self.dataBytesForwarded += forwarded
        self.dataRequests += requests


class OverallStats:

    def __init__(self, url, jwt, time_pattern):
        self.time_pattern = time_pattern
        self.url = url
        self.jwt = jwt
        self.startTime = time.strftime(self.time_pattern, time.localtime())
        self.endTime = ""
        self.tempDataBytes = 0
        self.tempDataBytesForwarded = 0
        self.tempDataRequests = 0
        self.loadDataBytes = 0
        self.loadDataBytesForwarded = 0
        self.loadDataRequests = 0
        self.fuelDataBytes = 0
        self.fuelDataBytesForwarded = 0
        self.fuelDataRequests = 0

    def combine_stats(self, temp_stats, load_stats, fuel_stats):
        self.tempDataBytes = temp_stats.dataBytes
        self.tempDataBytesForwarded = temp_stats.dataBytesForwarded
        self.tempDataRequests = temp_stats.dataRequests
        self.loadDataBytes = load_stats.dataBytes
        self.loadDataBytesForwarded = load_stats.dataBytesForwarded
        self.loadDataRequests = load_stats.dataRequests
        self.fuelDataBytes = fuel_stats.dataBytes
        self.fuelDataBytesForwarded = fuel_stats.dataBytesForwarded
        self.fuelDataRequests = fuel_stats.dataRequests

    def send_stats(self):
        self.endTime = time.strftime(self.time_pattern, time.localtime())
        payload = {"startTime": self.startTime, "endTime": self.endTime, "tempDataBytes": self.tempDataBytes,
                   "tempDataBytesForwarded": self.tempDataBytesForwarded,
                   "tempDataRequests": self.tempDataRequests,
                   "loadDataBytes": self.loadDataBytes,
                   "loadDataBytesForwarded": self.loadDataBytesForwarded,
                   "loadDataRequests": self.loadDataRequests,
                   "fuelDataBytes": self.fuelDataBytes,
                   "fuelDataBytesForwarded": self.fuelDataBytesForwarded,
                   "fuelDataRequests": self.fuelDataRequests}
        for i in range(0, 5):
            try:
                post_req = requests.post(self.url, json=payload, headers={"Authorization": "Bearer " + self.jwt})
                if post_req.status_code == 200:
                    break
                else:
                    errorLogger.error("problem with Stats Cloud service!")
                    customLogger.critical("Stats service unavailable!")
            except:
                errorLogger.error("Stats Cloud service unavailable!")
                customLogger.critical("Stats service unavailable!")

