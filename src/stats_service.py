"""Stats service utilities.

stats_service
=============
Module that contains logic used for collecting stats about savings in sensor data sent over the internet.

Classes
---------

Stats
    Class representing stats regarding single sensor data transmission.
OverallStats
    Class representing stats regarding whole gateway app data transmission.

Functions
---------

Constants
---------

"""
import time
import logging.config

# setting up loggers
logging.config.fileConfig('logging.conf')
errorLogger = logging.getLogger('customErrorLogger')
customLogger = logging.getLogger('customConsoleLogger')


class Stats:
    """
    Represents single sensor stats regarding data collected and transmitted over network.

    Attributes
    ----------
    dataBytes: int
        Amount of collected sensor data in bytes.
    dataBytesForwarded: int
        Amount of sensor data sent to cloud services in bytes.
    dataRequests: int
        Number of requests to cloud services.

    Methods
    -------
    update_data(self, bytes, forwarded, requests)
        Updating stats data.
    """

    def __init__(self):
        """Initialize Stats object."""
        self.dataBytes = 0
        self.dataBytesForwarded = 0
        self.dataRequests = 0

    def update_data(self, bytes, forwarded, requests):
        """
        Update current stats  with new collected sensor data.

        Parameters
        ----------
        bytes: int
            Collected sensor data in bytes.
        forwarded: int
            Sent sensor data in bytes.
        requests: int
            Number of made cloud service requests.

        Returns
        -------
        None
        """
        self.dataBytes += bytes
        self.dataBytesForwarded += forwarded
        self.dataRequests += requests


class OverallStats:
    """
    Represents overall IoT gateway stats regarding data collected and transmitted over network.

    Attributes
    ----------
    time_pattern: str
        Server date-time format.
    url: str
        Stats cloud service URL.
    jwt: str
    startTime: str
        Start of collecting stats.
    endTime: str
        End of collecting stats.
    tempDataBytes: int
        Amount of collected temperature data [byte].
    tempDataBytesForwarded: int
        Amount of transmitted temperature data [byte].
    tempDataRequests: int
        Number of requests to temperature stats service.
    loadDataBytes: int
        Amount of collected load data [byte].
    loadDataBytesForwarded: int
        Amount of transmitted load data [byte].
    loadDataRequests: int
        Number of requests to load stats service.
    fuelDataBytes: int
        Amount of collected fuel data [byte].
    fuelDataBytesForwarded: int
        Amount of transmitted fuel data [byte].
    fuelDataRequests: int
        Number of requests to fuel stats service.

    Methods
    -------
    combine_stats(self, temp_stats, load_stats, fuel_stats)
        Combines stats from different sensors into overall stats.
    send_stats(self):
        Sends collected stats dato to stats cloud service.
    """

    def __init__(self, time_pattern):
        """Init OverallStats object.

        Parameters
        ----------
        url
        jwt
        username
        time_pattern
        mqtt_client
        """
        self.time_pattern = time_pattern
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
        """
        Combine stats from different sensors into overall stats.

        Parameters
        ----------
        temp_stats: Stats
            Temperature stats data.
        load_stats: Stats
            Load stats data.
        fuel_stats: Stats
            Fuel stats data.

        Returns
        -------
        None
        """
        self.tempDataBytes = temp_stats.dataBytes
        self.tempDataBytesForwarded = temp_stats.dataBytesForwarded
        self.tempDataRequests = temp_stats.dataRequests
        self.loadDataBytes = load_stats.dataBytes
        self.loadDataBytesForwarded = load_stats.dataBytesForwarded
        self.loadDataRequests = load_stats.dataRequests
        self.fuelDataBytes = fuel_stats.dataBytes
        self.fuelDataBytesForwarded = fuel_stats.dataBytesForwarded
        self.fuelDataRequests = fuel_stats.dataRequests

        self.endTime = time.strftime(self.time_pattern, time.localtime())
        payload = {"startTime": self.startTime,
                   "endTime": self.endTime,
                   "tempDataBytes": self.tempDataBytes,
                   "tempDataBytesForwarded": self.tempDataBytesForwarded,
                   "tempDataRequests": self.tempDataRequests,
                   "loadDataBytes": self.loadDataBytes,
                   "loadDataBytesForwarded": self.loadDataBytesForwarded,
                   "loadDataRequests": self.loadDataRequests,
                   "fuelDataBytes": self.fuelDataBytes,
                   "fuelDataBytesForwarded": self.fuelDataBytesForwarded,
                   "fuelDataRequests": self.fuelDataRequests}
        return payload

