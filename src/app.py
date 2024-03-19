"""Main gateway application.

app
============
Module that contains main iot gateway logic.

Functions
---------
signup_periodically(key, username, password, time_pattern, url, interval)
    Periodically initiates device signup on cloud services.
on_connect_temp_handler(client, userdata, flags, rc,props)
    Logic executed after successfully connecting temperature sensor to MQTT broker.
on_connect_load_handler(client, userdata, flags, rc,props)
    Logic executed after successfully connecting load sensor to MQTT broker.
on_connect_fuel_handler(client, userdata, flags, rc,props)
    Logic executed after successfully connecting fuel sensor to MQTT broker.
collect_temperature_data(interval, url, jwt, time_pattern, mqtt_address,
mqtt_port, mqtt_user,mqtt_pass, flag, stats_queue)
    Collects temperature data and periodically initiates data processing and forwarding.
collect_load_data(interval, url, jwt, time_pattern, mqtt_address, mqtt_port, mqtt_user,mqtt_pass,flag, stats_queue)
    Collects load data and periodically initiates data processing and forwarding.
collect_fuel_data(limit, url, jwt, time_pattern, mqtt_address, mqtt_port, mqtt_user,mqtt_pass, flag, stats_queue)
    Collects temperature data and initiates data filtering and forwarding.
main()
    Iot gateway app entrypoint.

Constants
---------
CONF_PATH: str
    App config file path.
USER: str
    Device username.
PASSWORD: str
    Device password.
SERVER_URL: str
    Cloud services' URL.
AUTH_INTERVAL: int
    Time lapse between signup requests.
TIME_FORMAT: str
    Time format.
SERVER_TIME_FORMAT: str
    Server's time format.
FUEL_LEVEL_LIMIT:
    Critical level of fuel.
TEMP_INTERVAL: int
    Time lapse between temperature cloud service requests.
LOAD_INTERVAL = "load_interval"
    Time lapse between load cloud service requests.
API_KEY: str
    Cloud platform API key.
TRANSPORT_PROTOCOL: str
    Transport protocol for MQTT.
TEMP_TOPIC: str
    MQTT topic for  temperature data.
LOAD_TOPIC: str
    MQTT topic for load data.
FUEL_TOPIC: str
    MQTT topic for fuel data.
HTTP_UNAUTHORIZED: int
TEMP_ALARM_TOPIC: str
    MQTT alarm topic for temperature alarms
LOAD_ALARM_TOPIC: str
    MQTT alarm topic for load alarms
FUEL_ALARM_TOPIC: str
    MQTT alarm topic for fuel alarms
    Http status code.
HTTP_OK: int
    Http status code.
HTTP_NO_CONTENT: int
    Http status code.
QOS: int
    Quality of service of MQTT.
mqtt_broker_local: str
    Reference of local mqtt broker
"""
import signal
import auth
import stats_service
import data_service
import time
import logging.config
import paho.mqtt.client as mqtt
from threading import Thread, Event
from queue import Queue
from mqtt_util import MQTTConf, GcbService, \
    GCB_TEMP_TOPIC, GCB_LOAD_TOPIC, GCB_FUEL_TOPIC, GCB_STATS_TOPIC
from config_util import ConfFlags, get_temp_interval, get_fuel_level_limit, \
    start_config_observer
from mqtt_utils import MQTTClient
from config_util import Config
from data_service import EMPTY_PAYLOAD
from signal_control import BetterSignalHandler

logging.config.fileConfig('logging.conf')
infoLogger = logging.getLogger('customInfoLogger')
errorLogger = logging.getLogger('customErrorLogger')
customLogger = logging.getLogger('customConsoleLogger')

CONF_PATH = "configuration/app_conf.json"
USER = "username"
PASSWORD = "password"
SERVER_URL = "server_url"
AUTH_INTERVAL = "auth_interval"
TIME_FORMAT = "time_format"
SERVER_TIME_FORMAT = "server_time_format"

CAN_GENERAL_SETTINGS = "can_general_settings"
INTERFACE = "interface"
CHANNEL = "channel"
BITRATE = "bitrate"

TEMP_SETTINGS = "temp_settings"
LOAD_SETTINGS = "load_settings"
FUEL_SETTINGS = "fuel_settings"
INTERVAL = "interval"
LEVEL_LIMIT = "level_limit"

API_KEY = "api_key"
MQTT_BROKER = "mqtt_broker"
MQTT_BROKER_LOCAL = "mqtt_broker_local"
ADDRESS = "address"
PORT = "port"
TRANSPORT_PROTOCOL = "tcp"
TEMP_TOPIC = "sensors/temperature"
LOAD_TOPIC = "sensors/arm-load"
FUEL_TOPIC = "sensors/fuel-level"
HTTP_UNAUTHORIZED = 401
HTTP_OK = 200
HTTP_NO_CONTENT = 204
QOS = 2

TEMP_ALARM_TOPIC = "alarms/temperature"
LOAD_ALARM_TOPIC = "alarms/load"
FUEL_ALARM_TOPIC = "alarms/fuel"


def signup_periodically(key, username, password, time_pattern, url, interval):
    """
    Periodically requests device signup.

    Parameters
    ----------
    key: str
        API key.
    username: str
        Device's username,
    password: str
        Device's password,
    time_pattern: str
        Device's time pattern.
    url: str
        Cloud services URL.
    interval: int
        Time lapse between consecutive requests.

    Returns
    -------
    jwt: str
        JSON web token for accessing cloud services.
    """
    jwt = None
    while jwt is None:
        customLogger.debug("Trying to sign up!")
        jwt = auth.register(key, username, password, time_pattern, url)
        time.sleep(interval)
    customLogger.debug("Successful sign up!")
    return jwt


def on_connect_temp_handler(client, userdata, flags, rc, props):
    """
    Logic executed after successfully connecting temperature sensor to MQTT broker.

    Parameters
    ----------
    client: mqtt.client
    userdata: object
    flags:
    rc: int
    props:
    """
    if rc == 0:
        infoLogger.info(
            "Temperature data handler successfully established connection with MQTT broker!")
        customLogger.info(
            "Temperature data handler successfully established connection with MQTT broker!")
        client.subscribe(TEMP_TOPIC, qos=QOS)
    else:
        errorLogger.error(
            "Temperature data handler failed to establish connection with MQTT broker!")
        customLogger.critical(
            "Temperature data handler failed to establish connection with MQTT broker!")


def on_connect_load_handler(client, userdata, flags, rc, props):
    """
    Logic executed after successfully connecting arm load sensor to MQTT broker.

    Parameters
    ----------
    client: mqtt.client
    userdata: object
    flags:
    rc: int
    props:
    """
    if rc == 0:
        infoLogger.info(
            "Arm load data handler successfully established connection with MQTT broker!")
        customLogger.info(
            "Arm load data handler successfully established connection with MQTT broker!")
        client.subscribe(LOAD_TOPIC, qos=QOS)
    else:
        errorLogger.error(
            "Arm load data handler failed to establish connection with MQTT broker!")
        customLogger.critical(
            "Arm load data handler failed to establish connection with MQTT broker!")


def on_connect_fuel_handler(client, userdata, flags, rc, props):
    """
    Logic executed after successfully connecting fuel level sensor to MQTT broker.

    Parameters
    ----------
    client: mqtt.client
    userdata: object
    flags:
    rc: int
    props:
    """
    if rc == 0:
        infoLogger.info(
            "Fuel data handler successfully established connection with MQTT broker!")
        customLogger.info(
            "Fuel data handler successfully established connection with MQTT broker!")
        client.subscribe(FUEL_TOPIC, qos=QOS)
    else:
        errorLogger.error(
            "Fuel data handler failed to establish connection with MQTT broker!")
        customLogger.critical(
            "Fuel data handler failed to establish connection with MQTT broker!")

# iot data aggregation and forwarding to cloud


def collect_temperature_data(config, flag, conf_flag, stats_queue, gcb_queue):
    """
    Temperature data handler logic.

    Establishes connection with MQTT broker. Listens for incoming messages. Handles received temperature messages and
    periodically initiates data processing.

    Parameters
    ----------
    config: Config
        Configuration object
    flag: multithreading.Event
        Object used for stopping temperature sensor process.
    conf_flag: multithreading.Event
        Object used for signalling configuration changes
    stats_queue: multithreading.Queue
        Stats data wrapper.
    gcb_queue: queue.Queue
        Belongs to some GcbService instance and is used to queue payload that is to
        be sent via mqtt.
    """
    new_data = []
    old_data = []

    interval = get_temp_interval(config)

    sensors_broker_client = MQTTClient(
        "temp-data-handler-mqtt-client",
        transport_protocol=TRANSPORT_PROTOCOL,
        protocol_version=mqtt.MQTTv5,
        mqtt_username=config.mqtt_broker_username,
        mqtt_pass=config.mqtt_broker_password,
        broker_address=config.mqtt_broker_address,
        broker_port=config.mqtt_broker_port,
        keepalive=config.temp_settings_interval * 3,
        infoLogger=infoLogger,
        errorLogger=errorLogger,
        flag=flag,
        sensor_type="TEMP",
    )

    # called when there is new message in temp_topic topic
    def on_message_handler(client, userdata, message):
        """
        Handle received mqtt message.

        After receiving mqtt message, locally stores temperature data.

        Parameters
        ----------
        client: mqtt.client
        userdata: object
        message: object

        Returns
        -------
        None
        """
        if not flag.is_set():
            data = message.payload.decode("utf-8")
            new_data.append(str(data))
            customLogger.info("Received temperature data: " + str(data))
            data_value, unit = data_service.parse_incoming_data(
                str(data), "temperature")
            if data_value > 95:
                # sound the alarm! ask him what do I send
                customLogger.info(
                    "Temperature of " + str(data_value) + " C is too high! Sounding the alarm!")
                client.publish(TEMP_ALARM_TOPIC, True, QOS)

    # initializing stats object
    stats = stats_service.Stats()
    # initializing mqtt client for collecting sensor data from broker
    sensors_broker_client.set_on_connect(on_connect_temp_handler)
    sensors_broker_client.set_on_message(on_message_handler)
    sensors_broker_client.connect()
    # periodically processes collected data and forwards result to cloud
    # services
    while not flag.is_set():
        customLogger.debug(f"INTERVAL: {interval}")

        if conf_flag.is_set():
            interval = config.temp_settings_interval
            conf_flag.clear()

        # copy data from list that is populated with newly arrived data and
        # clear that list
        data = new_data.copy()
        new_data.clear()
        # append data that is not sent in previous iterations due to connection
        # problem
        for i in old_data:
            data.append(i)
        old_data.clear()
        # send payload to Cloud only if there is available data
        if len(data) > 0:
            payload = data_service.handle_temperature_data(data, config.time_format)
            if payload != EMPTY_PAYLOAD:
                GcbService.push_message(gcb_queue, GCB_TEMP_TOPIC, payload)
                stats.update_data(len(data) * 4, 4, 1)
                customLogger.info("TEMP PUBLISHED")
        else:
            infoLogger.warning(
                "There is no temperature sensor data to handle!")
        time.sleep(config.temp_settings_interval)

    # shutting down temperature sensor
    stats_queue.put(stats)
    sensors_broker_client.disconnect()

    customLogger.debug("Temperature data handler shutdown!")


def collect_load_data(config, flag, conf_flag, stats_queue, gcb_queue):
    """
    Load data handler logic.

    Establishes connection with MQTT broker. Listens for incoming messages. Handles received load messages and
    periodically initiates data processing.

    Parameters
    ----------
    config: Config
        Configuration object
    flag: multithreading.Event
       Object used for stopping temperature sensor process.
    conf_flag: multithreading.Event
        Object used for signalling configuration changes
    stats_queue: multithreading.Queue
        Stats data wrapper.
    gcb_queue: queue.Queue
        Belongs to some GcbService instance and is used to queue payload that is to
        be sent via mqtt.
    """
    new_data = []
    old_data = []

    # called when there is new message in load_topic topic
    # initializing mqtt client for collecting sensor data from broker

    sensors_broker_client = MQTTClient(
        "load-data-handler-mqtt-client",
        transport_protocol=TRANSPORT_PROTOCOL,
        protocol_version=mqtt.MQTTv5,
        mqtt_username=config.mqtt_broker_username,
        mqtt_pass=config.mqtt_broker_password,
        broker_address=config.mqtt_broker_address,
        broker_port=config.mqtt_broker_port,
        keepalive=config.load_settings_interval * 3,
        infoLogger=infoLogger,
        errorLogger=errorLogger,
        flag=flag,
        sensor_type="LOAD",
    )

    def on_message_handler(client, userdata, message):
        """
        Handle received mqtt message.

        After receiving mqtt message, locally stores load data.

        Parameters
        ----------
        client: mqtt.client
        userdata: object
        message: object
        """
        if not flag.is_set():
            data = message.payload.decode("utf-8")
            new_data.append(str(data))
            customLogger.info("Received load data: " + str(data))
            data_sum, unit = data_service.parse_incoming_data(
                str(data), "load")
            if data_sum > 1000:
                # sound the alarm!
                customLogger.info("Load of " + str(data_sum) + " kg is too high! Sounding the alarm!")
                client.publish(LOAD_ALARM_TOPIC, True, QOS)

    # initializing stats object
    stats = stats_service.Stats()
    # initializing mqtt client for collecting sensor data from broker
    sensors_broker_client.set_on_connect(on_connect_load_handler)
    sensors_broker_client.set_on_message(on_message_handler)
    sensors_broker_client.connect()

    # periodically processes collected data and forwards result to cloud
    # services
    sleep_period = config.load_settings_interval

    while not flag.is_set():
        if conf_flag.is_set():
            conf_flag.clear()

        # copy data from list that is populated with newly arrived data and
        # clear that list
        data = new_data.copy()
        new_data.clear()
        # append data that is not sent in previous iterations due to connection
        # problem
        for i in old_data:
            data.append(i)
        old_data.clear()
        # send request to Cloud only if there is available data
        if len(data) > 0:
            payload = data_service.handle_load_data(data, config.time_format)
            if payload != EMPTY_PAYLOAD:
                GcbService.push_message(gcb_queue, GCB_LOAD_TOPIC, payload)
                stats.update_data(len(data) * 4, 4, 1)
                customLogger.info("LOAD PUBLISHED")
        else:
            infoLogger.warning("There is no arm load sensor data to handle!")
        time.sleep(sleep_period)

    # shutting down load sensor
    stats_queue.put(stats)
    sensors_broker_client.disconnect()

    customLogger.debug("Arm load data handler shutdown!")


def collect_fuel_data(config, flag, conf_flag, stats_queue, gcb_queue):
    """
    Fuel data handler logic.

    Establishes connection with MQTT broker. Listens for incoming messages. Handles received fuel messages and
    initiates data filtering and forwarding.

    Parameters
    ----------
    config: Config
        Configuration object
    flag: multithreading.Event
      Object used for stopping temperature sensor process.
    conf_flag: multithreading.Event
      Object used for signalling configuration changes
    stats_queue: multithreading.Queue
       Stats data wrapper.
    gcb_queue: queue.Queue
        Belongs to some GcbService instance and is used to queue payload that is to
        be sent via mqtt.
    """
    # initializing stats object

    stats = stats_service.Stats()
    limit = get_fuel_level_limit(config)

    # called when there is new message in load_topic topic

    sensors_broker_client = MQTTClient(
        "fuel-data-handler-mqtt-client",
        transport_protocol=TRANSPORT_PROTOCOL,
        protocol_version=mqtt.MQTTv5,
        mqtt_username=config.mqtt_broker_username,
        mqtt_pass=config.mqtt_broker_password,
        broker_address=config.mqtt_broker_address,
        broker_port=config.mqtt_broker_port,
        keepalive=config.fuel_settings_interval,
        infoLogger=infoLogger,
        errorLogger=errorLogger,
        flag=flag,
        sensor_type="FUEL",
    )

    def on_message_handler(client, userdata, message):
        """
        Handle received mqtt message.

        After receiving mqtt message, initiates fuel data processing.

        Parameters
        ----------
        client: mqtt.client
        userdata: object
        message: object
        """
        # making sure that flag is not set in meantime
        if not flag.is_set():
            if conf_flag.is_set():
                nonlocal limit
                limit = config.fuel_settings_level_limit
                conf_flag.clear()

            customLogger.info("Received fuel data: " + str(message.payload.decode("utf-8")))
            payload = data_service.handle_fuel_data(
                str(message.payload.decode("utf-8")),
                config.fuel_settings_level_limit,
                config.time_format,
                sensors_broker_client)

            if payload != EMPTY_PAYLOAD:
                GcbService.push_message(gcb_queue, GCB_FUEL_TOPIC, payload)
                stats.update_data(4, 4, 1)
                customLogger.info("FUEL PUBLISHED")
            else:
                stats.update_data(4, 0, 0)

    # initializing stats object
    stats = stats_service.Stats()
    # initializing mqtt client for collecting sensor data from broker
    sensors_broker_client.set_on_connect(on_connect_fuel_handler)
    sensors_broker_client.set_on_message(on_message_handler)
    sensors_broker_client.connect()

    # must do like this to be able to stop thread acquired for incoming
    # messages(on_message) after flag is set

    while not flag.is_set():
        time.sleep(config.fuel_settings_interval)
    # shutting down temperature sensor
    stats_queue.put(stats)
    sensors_broker_client.disconnect()

    customLogger.debug("Fuel level data handler shutdown!")


def main():
    """Start IoT gateway app entrypoint."""
    # used for restarting device due to jwt expiration

    # used as an indicator for termination request for main loop
    main_execution_flag = Event()

    while not main_execution_flag.is_set():
        config = Config(CONF_PATH, errorLogger, customLogger)
        config.try_open()
        # if config is read successfully, start app logic
        if config is not None:
            infoLogger.info("IoT Gateway app started!")
            customLogger.debug("IoT Gateway app started!")

            conf_flags = ConfFlags()
            conf_observer = start_config_observer(conf_flags)

            gcb_service = GcbService(config.iot_username,
                                     config.iot_username + "_gcb_client_id",
                                     MQTTConf.from_app_config(config, "gateway_cloud_broker"))
            gcb_service.start()

            # iot cloud platform login

            jwt = auth.login(config.iot_username,
                             config.iot_password,
                             config.server_url + "/auth/login")
            # if failed, periodically request signup
            if jwt is None:
                customLogger.error(
                    "Login failed! Trying to sign up periodically!")
                jwt = signup_periodically(
                    config.api_key,
                    config.iot_username,
                    config.iot_password,
                    config.server_time_format,
                    config.server_url + "/auth/signup",
                    config.auth_interval)
            else:
                customLogger.debug("Login successful!")
            # now JWT required for Cloud platform auth is stored in jwt var
            customLogger.info("Received JWT: " + jwt)
            # starting stats collecting

            # using shared memory Queue objects for returning stats data from
            # processes
            customLogger.debug("Initializing devices stats data!")

            stats = stats_service.OverallStats(config.time_format)
            temp_stats_queue = Queue()
            load_stats_queue = Queue()
            fuel_stats_queue = Queue()
            # flags are used for stopping data handlers on app shutdown
            temp_handler_flag = Event()
            load_handler_flag = Event()
            fuel_handler_flag = Event()

            BetterSignalHandler(signal.SIGTERM, [temp_handler_flag,
                                                 load_handler_flag,
                                                 fuel_handler_flag,
                                                 main_execution_flag])

            customLogger.debug("Starting workers!")
            # creates and starts data handling workers

            temperature_data_handler = Thread(
                target=collect_temperature_data,
                args=(
                    config,
                    temp_handler_flag,
                    conf_flags.temp_flag,
                    temp_stats_queue,
                    gcb_service.queue
                ))
            temperature_data_handler.start()
            time.sleep(1)
            load_data_handler = Thread(
                target=collect_load_data,
                args=(
                    config,
                    load_handler_flag,
                    conf_flags.load_flag,
                    load_stats_queue,
                    gcb_service.queue
                ))
            load_data_handler.start()
            time.sleep(1)
            fuel_data_handler = Thread(
                target=collect_fuel_data,
                args=(
                    config,
                    fuel_handler_flag,
                    conf_flags.fuel_flag,
                    fuel_stats_queue,
                    gcb_service.queue
                ))
            fuel_data_handler.start()
            time.sleep(1)
            # waiting fow workers to stop
            temperature_data_handler.join()
            load_data_handler.join()
            fuel_data_handler.join()
            customLogger.debug("Workers stopped!")

            conf_observer.stop()
            conf_observer.join()

            gcb_service.stop()

            # finalizing stats

            stats_payload = stats.combine_stats(
                temp_stats_queue.get(),
                load_stats_queue.get(),
                fuel_stats_queue.get()
            )

            customLogger.debug("Sending device stats data!")

            if stats_payload != EMPTY_PAYLOAD:
                GcbService.push_message(gcb_service.queue, GCB_STATS_TOPIC, stats_payload)
                print("STATS PUBLISHED: " + str(stats_payload))

        else:
            customLogger.critical("Cant read config file! Aborting...")


if __name__ == '__main__':
    main()
