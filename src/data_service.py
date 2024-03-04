"""
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

Constants
---------
data_pattern
    Request body data pattern.
http_not_found
    Http status code.
http_ok
    Http status code.
http_no_content
    Http status code.

"""
import time
import logging.config


logging.config.fileConfig('logging.conf')
errorLogger = logging.getLogger('customErrorLogger')
customLogger = logging.getLogger('customConsoleLogger')

data_pattern = "[ value={} , time={} , unit={} ]"
http_not_found = 404
http_ok = 200
http_no_content = 204

qos = 2
temp_alarm_topic = "alarms/temperature"
load_alarm_topic = "alarms/load"
fuel_alarm_topic = "alarms/fuel"


def parse_incoming_data(data, type):
    data_sum = 0.0
    # summarizing colleceted data
    # for item in data:
    try:
        tokens = data.split(" ")
        data_sum += float(tokens[1].split("=")[1])
    except BaseException:
        errorLogger.error("Invalid " + type + " data format! - " + data)
    # time_value = time.strftime(time_format, time.localtime()) not needed
    unit = "unknown"
    try:
        unit = data.split(" ")[6].split("=")[1]
    except BaseException:
        errorLogger.error("Invalid " + type + " data format! - " + data)
    return data_sum, unit

# [REST/MQTT] [New parameter from mqtt client added to all handle functions]


def handle_temperature_data(data, url, jwt, username, time_format, mqtt_client):
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
       time_format: str
            Cloud services' time format.

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

    # creating request payload

    time_value = time.strftime(time_format, time.localtime())
    payload = {"value": round(data_sum / len(data), 2), "time": time_value, "unit": unit}
    customLogger.warning("Forwarding temperature data: " + str(payload))
    try:
        # [REST/MQTT]
        mqtt_payload = {"username": username, "payload": payload}
        # publish(gcb_temp_topic, json.dumps(mqtt_payload), gcb_qos)
        customLogger.debug("TEMP MESSAGE PUBLISHED")

        # post_req = requests.post(url, json=payload, headers={"Authorization": "Bearer " + jwt})
        # if post_req.status_code != http_ok:
        #    errorLogger.error("Problem with temperature Cloud service! - Http status code: "
        #    + str(post_req.status_code))
        # return post_req.status_code
    except BaseException:
        errorLogger.error("Temperature Cloud service cant be reached!")
        customLogger.critical("Temperature Cloud service cant be reached!")
        return http_not_found


def handle_load_data(data, url, jwt, username, time_format, mqtt_client):
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
    time_format: str
        Cloud services' time format.

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
    # request payload
    time_value = time.strftime(time_format, time.localtime())
    payload = {"value": round(data_sum, 2), "time": time_value, "unit": unit}
    customLogger.warning("Forwarding load data: " + str(payload))
    try:
        # [REST/MQTT]
        mqtt_payload = {"username": username, "payload": payload}
        # mqtt_client.publish(gcb_load_topic, json.dumps(mqtt_payload), gcb_qos) # ASK usage
        customLogger.debug("LOAD MESSAGE PUBLISHED")

        # post_req = requests.post(url, json=payload, headers={"Authorization": "Bearer " + jwt})
        # if post_req.status_code != http_ok:
        #    errorLogger.error("Problem with arm load Cloud service! - Http status code: " + str(post_req.status_code))
        #    customLogger.error("Problem with arm load Cloud service! - Http status code: " + str(post_req.status_code))
        # return post_req.status_code
    except BaseException:
        errorLogger.error("Arm load Cloud service cant be reached!")
        customLogger.critical("Arm load Cloud service cant be reached!")
        return http_not_found


def handle_fuel_data(data, limit, url, jwt, username, time_format, alarm_client, mqtt_client):
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
     time_format: str
         Cloud services' time format.
     mqtt_client: paho.mqtt.client.Client
         MQTT client used to send data to gateway-cloud broker.

     Returns
     -------
     http status code
    """
    try:
        tokens = data.split(" ")
        value = float(tokens[1].split("=")[1])
        # sends data to cloud services only if it is value of interest
        if value <= limit:  # ASK same limit as his or a different one?

            # sound the alarm! ask him what do I send #ASK
            customLogger.info("Fuel is below the designated limit! Sounding the alarm")

            alarm_client.publish(fuel_alarm_topic, True, qos)

            unit = "unknown"
            try:
                unit = tokens[6].split("=")[1]
            except BaseException:
                errorLogger.error("Invalid fuel data format! - " + data)
            time_value = time.strftime(time_format, time.localtime())
            # request payload

            payload = {"value": round(value, 2), "time": time_value, "unit": unit}
            customLogger.warning("Forwarding fuel data: " + str(payload))

            try:
                # [REST/MQTT]
                mqtt_payload = {"username": username, "payload": payload}
                # mqtt_client.publish(gcb_fuel_topic, json.dumps(mqtt_payload), gcb_qos)
                customLogger.debug("FUEL MESSAGE PUBLISHED")

                # post_req = requests.post(url, json=payload, headers={"Authorization": "Bearer " + jwt})

                # if post_req.status_code != http_ok:

                #    errorLogger.error("Problem with fuel Cloud service! - Http status code: "
                #    + str(post_req.status_code))
                #    customLogger.error("Problem with fuel Cloud service! - Http status code: "
                #    + str(post_req.status_code))
                # return post_req.status_code
            except BaseException:
                errorLogger.error("Fuel Cloud service cant be reached!")
                customLogger.error("Fuel Cloud service cant be reached!")
                return http_not_found
        else:
            # data is handled but is not sent because fuel level is over the limit
            return http_no_content
    except BaseException:
        errorLogger.error("Invalid fuel data format! - " + data)
        # data can not be parsed, trying again to parse it and send in next iteration is redundant
        return http_no_content
