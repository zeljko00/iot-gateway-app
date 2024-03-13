"""Data service utilities.

data_services
============
Module containing logic for sending collected and processed data to cloud services.

Functions
---------
handle_temperature_data(data, url, jwt, time_format)
    Summarizing collected temperature data and forwarding result to cloud service.
handle_load_data(data, url, jwt, time_format)
    Summarizing load temperature data and forwarding result to cloud service.
handle_fuel_data(data, limit, url, jwt, time_format)
    Filtering collected temperature data and forwarding result to cloud service.
parse_incoming_data(data, type)
    Parsing all types of data that come from sources

Constants
---------
DATA_PATTERN
    Request body data pattern.
HTTP_NOT_FOUND
    Http status code.
HTTP_OK
    Http status code.
HTTP_NO_CONTENT
    Http status code.
qos
    Quality of Service of MQTT broker
temp_alarm_topic: str
    MQTT alarm topic for temperature alarms
load_alarm_topic: str
    MQTT alarm topic for load alarms
fuel_alarm_topic: str
    MQTT alarm topic for fuel alarms
"""
import time
import json
import logging.config

logging.config.fileConfig('logging.conf')
errorLogger = logging.getLogger('customErrorLogger')
customLogger = logging.getLogger('customConsoleLogger')

DATA_PATTERN = "[ value={} , time={} , unit={} ]"
HTTP_NOT_FOUND = 404
HTTP_OK = 200
HTTP_NO_CONTENT = 204

QOS = 2
TEMP_ALARM_TOPIC = "alarms/temperature"
LOAD_ALARM_TOPIC = "alarms/load"
FUEL_ALARM_TOPIC = "alarms/fuel"

EMPTY_PAYLOAD = {}

def parse_incoming_data(data, data_type):
    """
    Parsing all types of data that come from sources

    Args:
    ----
        data: str
            Data to be parsed
        data_type: str
            Data type (Temperature, Load, Fuel) for console output

    Returns:
    -------
        data_sum: double
            Parsed data value
        unit: str
            Unit of the parsed data
    """
    data_sum = 0.0
    # summarizing colleceted data
    # for item in data:
    try:
        tokens = data.split(" ")
        data_sum += float(tokens[1].split("=")[1])
    except BaseException:
        errorLogger.error("Invalid " + data_type + " data format! - " + data)
    unit = "unknown"
    try:
        unit = data.split(" ")[6].split("=")[1]
    except BaseException:
        errorLogger.error("Invalid " + data_type + " data format! - " + data)
    return data_sum, unit


def handle_temperature_data(data, time_format):
    """
    Summarizes and sends collected temperature data.

    Triggered periodically.

    Parameters
    ----------
    data: list
        Collected temperature data.
    url: str
        Cloud services' URL.
    jwt: str
        JSON wen auth token
    username: str
        Username of the IoT device
    time_format: str
        Cloud services' time format.
    mqtt_client: paho.mqtt.client.Client
        Gateway IoT broker client

    Returns
    -------
    http status code
    """
    data_sum = 0.0
    unit = "Unknown"
    for info in data:
        data_value, parsed_unit = parse_incoming_data(info, "temperature")
        unit = parsed_unit
        data_sum += data_value

    time_value = time.strftime(time_format, time.localtime())
    payload = {"value": round(data_sum / len(data), 2), "time": time_value, "unit": unit}
    return payload


def handle_load_data(data, time_format):
    """
    Summarizes and sends collected load data.

    Triggered periodically  (variable interval).

    Parameters
    ----------
    data: list
        Collected load data.
    url: str
        Cloud services' URL.
    jwt: str
        JSON wen auth token
    username: str
        Username of the IoT device
    time_format: str
        Cloud services' time format.
    mqtt_client: paho.mqtt.client.Client
        Gateway IoT broker client
    Returns
    -------
    http status code
    """
    data_sum = 0.0
    unit = "Unknown"
    for info in data:
        data_value, parsed_unit = parse_incoming_data(info, "load")
        unit = parsed_unit
        data_sum += data_value

    time_value = time.strftime(time_format, time.localtime())
    payload = {"value": round(data_sum, 2), "time": time_value, "unit": unit}
    return payload


def handle_fuel_data(data, limit, time_format, alarm_client):
    """
    Sends filtered fuel data.

    Triggered periodically.

    Parameters
    ----------
    data: list
     Collected load data.
    limit: double
     Critical fuel level.
    url: str
     Cloud services' URL.
    jwt: str
     JSON web auth token.
    username: str
    Username of the IoT device
    time_format: str
     Cloud services' time format.
    alarm_client: MQTTClient
     MQTT broker alarm client
    mqtt_client: paho.mqtt.client.Client
     MQTT client used to send data to gateway-cloud broker.

    Returns
    -------
    http status code
    """
    try:
        tokens = data.split(" ")
        value = float(tokens[1].split("=")[1])

        if value <= limit:  # ASK same limit as his or a different one?
            # sound the alarm! ask him what do I send #ASK
            customLogger.info("Fuel is below the designated limit! Sounding the alarm")

            alarm_client.publish(FUEL_ALARM_TOPIC, True, QOS)

            unit = "unknown"
            try:
                unit = tokens[6].split("=")[1]
            except BaseException:
                errorLogger.error("Invalid fuel data format! - " + data)
            time_value = time.strftime(time_format, time.localtime())

            payload = {"value": round(value, 2), "time": time_value, "unit": unit}
            return payload
        else:
            return EMPTY_PAYLOAD
    except BaseException:
        errorLogger.error("Invalid fuel data format! - " + data)
        return EMPTY_PAYLOAD
