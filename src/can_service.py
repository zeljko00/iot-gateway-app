"""
can_service
============
Module that provides functionality for CAN bus communication.

Classes
-------
CANListener: A class that accepts messages from the CAN bus

Functions
---------
read_can(execution_flag, config_flag, init_flags, can_lock)
    Thread execution function from sensor_devices main() for CAN communication
stop_can(notifier, bus, temp_client, load_client, fuel_client)
    Used for stopping all CAN functionalities
init_mqtt_clients(bus, is_can_temp, is_can_load, is_can_fuel, config, flag)
    Used for initializing MQTT clients that publish read CAN messages
on_publish(topic, payload, qos)
    Event handler for published messages to a MQTT topic
on_subscribe_temp_alarm(client, userdata, flags, rc, props)
    Event handler for subscribing to the temperature alarm MQTT topic
on_subscribe_load_alarm(client, userdata, flags, rc, props)
    Event handler for subscribing to the load alarm MQTT topic
on_subscribe_fuel_alarm(client, userdata, flags, rc, props)
    Event handler for subscribing to the fuel alarm MQTT topic
on_connect_temp_sensor(client, userdata, flags, rc, props)
    Even handler for subscribing to the temperature messages MQTT topic
on_connect_load_sensor(client, userdata, flags, rc, props)
    Even handler for subscribing to the load messages MQTT topic
on_connect_fuel_sensor(client, userdata, flags, rc, props)
    Even handler for subscribing to the fuel messages MQTT topic

Constants
---------
app_conf_file_path: str
    Path to the configuration file
transport_protocol: str
    JSON key for MQTT transport protocol
temp_topic: str
    MQTT topic for temperature data
load_topic: str
    MQTT topic for load data
fuel_topic: str
    MQTT topic for fuel data
data_pattern: str
    Format by which data is sent to MQTT brokers
time_format: str
    Format by which time is sent to MQTT brokers
celzius: str
    Temperature measuring unit
kg: str
    Load measuring unit
_l: str
    Fuel measuring unit
qos: int
    Quality of service of MQTT.
"""
import can
import logging.config
import paho.mqtt.client as mqtt
import logging
import time
from mqtt_utils import MQTTClient
from can.listener import Listener
from can.interface import Bus
from config_util import Config

logging.config.fileConfig('logging.conf')
infoLogger = logging.getLogger('customInfoLogger')
errorLogger = logging.getLogger('customErrorLogger')
customLogger = logging.getLogger("customConsoleLogger")

CONF_FILE_PATH = "configuration/sensor_conf.json"
APP_CONF_FILE_PATH = "configuration/app_conf.json"

TRANSPORT_PROTOCOL = "tcp"
TEMP_TOPIC = "sensors/temperature"
LOAD_TOPIC = "sensors/arm-load"
FUEL_TOPIC = "sensors/fuel-level"


DATA_PATTERN = "[ value={} , time={} , unit={} ]"
TIME_FORMAT = "%d.%m.%Y %H:%M:%S"
CELZIUS = "C"
KG = "kg"
_L = "l"

MODE = "mode"
TEMP_SETTINGS = "temp_settings"
LOAD_SETTINGS = "load_settings"
FUEL_SETTINGS = "fuel_settings"
CAN_GENERAL_SETTINGS = "can_general_settings"

CHANNEL = "channel"
INTERFACE = "interface"
BITRATE = "bitrate"

TEMP_SENSOR = "temp_sensor"
ARM_SENSOR = "arm_sensor"
ARM_MIN_T = "min_t"
ARM_MAX_T = "max_t"
FUEL_SENSOR = "fuel_sensor"
FUEL_CONSUMPTION = "consumption"
FUEL_CAPACITY = "capacity"
FUEL_EFFICIENCY = "efficiency"
FUEL_REFILL = "refill"
INTERVAL = "period"
MQTT_USER = "username"
MQTT_PASSWORD = "password"
_MAX = "max_val"
_MIN = "min_val"
_AVG = "avg_val"
MQTT_BROKER = "mqtt_broker"
ADDRESS = "address"
PORT = "port"

QOS = 2
TEMP_ALARM_TOPIC = "alarms/temperature"
LOAD_ALARM_TOPIC = "alarms/load"
FUEL_ALARM_TOPIC = "alarms/fuel"


def read_can(execution_flag, config_flag, init_flags, can_lock):
    """
    Thread execution function from sensor_devices main() for CAN communication
    It connects to an instance of CAN bus, which is then tied to a Notifier object, which listens to the bus for
    incoming messages

    Args:
    ----
        execution_flag: multithreading.Event
            Token used for stopping CAN thread.
        config_flag: multithreading.Event
            Token used for detecting configuration changes
        init_flags: InitFlags
            Object that keeps track of initiated threads
        can_lock: multithreading.Lock
            Used to prevent race condition

    """
    customLogger.debug("CAN process started!")

    period = 2

    initial = True
    notifier = None
    temp_client = None
    load_client = None
    fuel_client = None

    bus = None

    try:
        while not execution_flag.is_set():
            if config_flag.is_set() or initial:

                config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
                config.try_open()
                stop_can(notifier, bus, temp_client, load_client, fuel_client)

                interface_value = config.can_interface
                channel_value = config.can_channel
                bitrate_value = config.can_bitrate

                is_can_temp = True if config.temp_mode == "CAN" else False
                is_can_load = True if config.load_mode == "CAN" else False
                is_can_fuel = True if config.fuel_mode == "CAN" else False

                if (is_can_temp is False) and (
                        is_can_load is False) and (is_can_fuel is False):
                    break

                bus = Bus(interface=interface_value,
                          channel=channel_value,
                          bitrate=bitrate_value)

                temp_client, load_client, fuel_client = init_mqtt_clients(
                    bus, is_can_temp, is_can_load, is_can_fuel, config, execution_flag)
                notifier = can.Notifier(bus, [], timeout=period)
                can_listener = CANListener(temp_client, load_client, fuel_client)
                notifier.add_listener(can_listener)
                initial = False
                config_flag.clear()

            time.sleep(period)
    except Exception:
        errorLogger.error("CAN device not available.")
        customLogger.debug("CAN device not available.")

    can_lock.acquire()
    init_flags.can_initiated = False
    can_lock.release()

    stop_can(notifier, bus, temp_client, load_client, fuel_client)
    execution_flag.clear()
    customLogger.debug("CAN process shutdown!")


def stop_can(notifier, bus, temp_client, load_client, fuel_client):
    """
    Used for stopping all CAN functionalities

    Args:
    ----
        notifier: can.Notifier
            Object that listens to incoming CAN messages
        bus: can.Bus
            CAN bus
        temp_client: mqtt_utils.MQTTClient
            Temperature MQTT broker client
        load_client: mqtt_utils.MQTTClient
            Load MQTT broker client
        fuel_client: mqtt_utils.MQTTClient
            Fuel MQTT broker client

    """
    if notifier is not None:
        notifier.stop(timeout=5)
    if temp_client is not None:
        temp_client.disconnect()
    if load_client is not None:
        load_client.disconnect()
    if fuel_client is not None:
        fuel_client.disconnect()
    if bus is not None:
        bus.shutdown()


def init_mqtt_clients(
        bus,
        is_can_temp,
        is_can_load,
        is_can_fuel,
        config,
        flag):
    """
    Used for stopping all CAN functionalities

    Args:
    ----
        bus: can.Bus
            CAN bus
        is_can_temp: boolean
            Flag that indicates if the configuration demands the Notifier to read CAN temperature messages
        is_can_load: boolean
            Flag that indicates if the configuration demands the Notifier to read CAN load messages
        is_can_fuel: boolean
            Flag that indicates if the configuration demands the Notifier to read CAN fuel messages

    """
    temp_client = None
    load_client = None
    fuel_client = None

    if is_can_temp:
        temp_client = MQTTClient(
            "temp-can-sensor-mqtt-client",
            transport_protocol=TRANSPORT_PROTOCOL,
            protocol_version=mqtt.MQTTv5,
            mqtt_username=config.mqtt_broker_username,
            mqtt_pass=config.mqtt_broker_password,
            broker_address=config.mqtt_broker_address,
            broker_port=config.mqtt_broker_port,
            keepalive=config.temp_settings_interval,
            infoLogger=infoLogger,
            errorLogger=errorLogger,
            flag=flag,
            sensor_type="TEMP")

        def on_message_temp_alarm(client, userdata, msg):
            can_message = can.Message(arbitration_id=0x120,
                                      data=[bool(msg.payload)],
                                      is_extended_id=False,
                                      is_remote_frame=False)
            bus.send(msg=can_message, timeout=5)
            customLogger.info(
                "Temperature alarm registered! Forwarding to CAN!")

        temp_client.set_on_connect(on_connect_temp_sensor)
        temp_client.set_on_publish(on_publish)
        temp_client.set_on_subscribe(on_subscribe_temp_alarm)
        temp_client.set_on_message(on_message_temp_alarm)
        temp_client.connect()

    if is_can_load:
        load_client = MQTTClient(
            "load-can-sensor-mqtt-client",
            transport_protocol=TRANSPORT_PROTOCOL,
            protocol_version=mqtt.MQTTv5,
            mqtt_username=config.mqtt_broker_username,
            mqtt_pass=config.mqtt_broker_password,
            broker_address=config.mqtt_broker_address,
            broker_port=config.mqtt_broker_port,
            keepalive=config.load_settings_interval,
            infoLogger=infoLogger,
            errorLogger=errorLogger,
            flag=flag,
            sensor_type="LOAD")

        def on_message_load_alarm(client, userdata, msg):
            can_message = can.Message(arbitration_id=0x121,
                                      data=[bool(msg.payload)],
                                      is_extended_id=False,
                                      is_remote_frame=False)
            bus.send(msg=can_message, timeout=5)
            customLogger.info("Load alarm registered! Forwarding to CAN!")

        load_client.set_on_connect(on_connect_load_sensor)
        load_client.set_on_publish(on_publish)
        load_client.set_on_subscribe(on_subscribe_load_alarm)
        load_client.set_on_message(on_message_load_alarm)
        load_client.connect()

    if is_can_fuel:
        fuel_client = MQTTClient(
            "fuel-can-sensor-mqtt-client",
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
            sensor_type="FUEL")

        def on_message_fuel_alarm(client, userdata, msg):
            can_message = can.Message(arbitration_id=0x122,
                                      data=[bool(msg.payload)],
                                      is_extended_id=False,
                                      is_remote_frame=False)
            bus.send(msg=can_message, timeout=5)
            customLogger.info("Fuel alarm registered! Forwarding to CAN!")

        fuel_client.set_on_connect(on_connect_fuel_sensor)
        fuel_client.set_on_publish(on_publish)
        fuel_client.set_on_subscribe(on_subscribe_fuel_alarm)
        fuel_client.set_on_message(on_message_fuel_alarm)
        fuel_client.connect()
    return temp_client, load_client, fuel_client


def on_publish(topic, payload, qos):
    """
    Event handler for published messages to a MQTT topic
    Args:
    ----
        topic: str
            The topic that the message was sent to
        payload: bytearray
            Message published
        qos: int
            Quality of Service of MQTT broker

    """
    pass


def on_subscribe_temp_alarm(client, userdata, flags, rc, props):
    """
    Event handler for published messages to a MQTT topic
    Args:
    ----
        client: paho.mqtt.client.Client
        userdata:
        flags:
        rc:
        props:

    """
    if rc == 0:
        infoLogger.info(
            "CAN Temperature alarm client successfully established connection with MQTT broker!")
        customLogger.debug(
            "CAN Temperature alarm client successfully established connection with MQTT broker!")
    else:
        errorLogger.error(
            "CAN Temperature alarm client failed to establish connection with MQTT broker!")
        customLogger.critical(
            "CAN Temperature alarm client failed to establish connection with MQTT broker!")


def on_subscribe_load_alarm(client, userdata, flags, rc, props):
    """
    Event handler for published messages to a MQTT topic
    Args:
    ----
        client: paho.mqtt.client.Client
        userdata:
        flags:
        rc:
        props:

    """
    if rc == 0:
        infoLogger.info(
            "CAN Load alarm client successfully established connection with MQTT broker!")
        customLogger.debug(
            "CAN Load alarm client successfully established connection with MQTT broker!")
    else:
        errorLogger.error(
            "CAN Load alarm client failed to establish connection with MQTT broker!")
        customLogger.critical(
            "CAN Load alarm client failed to establish connection with MQTT broker!")


def on_subscribe_fuel_alarm(client, userdata, flags, rc, props):
    """
    Event handler for published messages to a MQTT topic
    Args:
    ----
        client: paho.mqtt.client.Client
        userdata:
        flags:
        rc:
        props:

    """
    if rc == 0:
        infoLogger.info(
            "CAN Load alarm client successfully established connection with MQTT broker!")
        customLogger.debug(
            "CAN Load alarm client successfully established connection with MQTT broker!")
        # client.subscribe(FUEL_ALARM_TOPIC, qos=QOS)
    else:
        errorLogger.error(
            "CAN Load alarm client failed to establish connection with MQTT broker!")
        customLogger.critical(
            "CAN Load alarm client failed to establish connection with MQTT broker!")


def on_connect_temp_sensor(client, userdata, flags, rc, props):
    """
    Event handler for published messages to a MQTT topic
    Args:
    ----
        client: paho.mqtt.client.Client
        userdata:
        flags:
        rc:
        props:

    """
    if rc == 0:
        infoLogger.info(
            "CAN Temperature sensor successfully established connection with MQTT broker!")
        customLogger.debug(
            "CAN Temperature sensor successfully established connection with MQTT broker!")
        client.subscribe(TEMP_ALARM_TOPIC, qos=QOS)
    else:
        errorLogger.error(
            "CAN Temperature sensor failed to establish connection with MQTT broker!")
        customLogger.critical(
            "CAN Temperature sensor failed to establish connection with MQTT broker!")


def on_connect_load_sensor(client, userdata, flags, rc, props):
    """
    Event handler for published messages to a MQTT topic
    Args:
    ----
        client: paho.mqtt.client.Client
        userdata:
        flags:
        rc:
        props:

    """
    if rc == 0:
        infoLogger.info(
            "CAN Load sensor successfully established connection with MQTT broker!")
        customLogger.debug(
            "CAN Load sensor successfully established connection with MQTT broker!")
        client.subscribe(LOAD_ALARM_TOPIC, qos=QOS)
    else:
        errorLogger.error(
            "CAN Load sensor failed to establish connection with MQTT broker!")
        customLogger.critical(
            "CAN Load sensor failed to establish connection with MQTT broker!")


def on_connect_fuel_sensor(client, userdata, flags, rc, props):
    """
    Event handler for published messages to a MQTT topic
    Args:
    ----
        client: paho.mqtt.client.Client
        userdata:
        flags:
        rc:
        props:

    """
    if rc == 0:
        infoLogger.info(
            "CAN Fuel sensor successfully established connection with MQTT broker!")
        customLogger.debug(
            "CAN Fuel sensor successfully established connection with MQTT broker!")
        client.subscribe(FUEL_ALARM_TOPIC, qos=QOS)
    else:
        errorLogger.error(
            "CAN Fuel sensor failed to establish connection with MQTT broker!")
        customLogger.critical(
            "CAN Fuel sensor failed to establish connection with MQTT broker!")


class CANListener (Listener):
    """
    A class that accepts messages from the CAN bus.

    This class inherits the functionality of can.listener.Listener

    Inherits:
    --------
        can.listener.Listener: Base class for CAN bus listener functionality

    Methods:
    -------
        __init__(temp_client, load_client, fuel_client): Class constructor for initializing class objects
        set_temp_client(client): Setter for the temperature MQTT broker client
        set_load_client(client): Setter for the load MQTT broker client
        set_fuel_client(client): Setter for the fuel MQTT broker client
        on_message_received(msg): Event handler for receiving messages from the CAN bus
    """

    def __init__(self, temp_client, load_client, fuel_client):
        """
        Constructor for initializing CANListener object

        Args:
        ----
            temp_client: MQTT temperature broker client
            load_client: MQTT load broker client
            fuel_client: MQTT fuel broker client

        """
        super().__init__()
        if temp_client is not None:
            temp_client.connect()
        self.temp_client = temp_client

        if load_client is not None:
            load_client.connect()
        self.load_client = load_client

        if fuel_client is not None:
            fuel_client.connect()
        self.fuel_client = fuel_client

    def set_temp_client(self, client):
        """
        Setter for the temperature MQTT broker client

        Args:
        ----
            client: MQTT temperature broker client

        """
        if client is None:
            if self.temp_client is not None:
                self.temp_client.disconnect()
        self.temp_client = client

    def set_load_client(self, client):
        """
        Setter for the load MQTT broker client

        Args:
        ----
            client: MQTT load broker client

        """
        if client is None:
            if self.temp_client is not None:
                self.temp_client.disconnect()
        self.load_client = client

    def set_fuel_client(self, client):
        """
        Setter for the fuel MQTT broker client

        Args:
        ----
            client: MQTT fuel broker client

        """
        if client is None:
            if self.temp_client is not None:
                self.temp_client.disconnect()
        self.fuel_client = client

    def on_message_received(self, msg):
        """
        Event handler for receiving messages from the CAN bus

        Args:
        ----
            msg: bytearray
                Received message from the CAN bus

        """
        # msg.data is a byte array, need to turn it into a single value
        int_value = int.from_bytes(msg.data, byteorder="big", signed=True)
        value = int_value / 10.0

        if self.temp_client is not None:
            self.temp_client.try_reconnect()
        if self.load_client is not None:
            self.load_client.try_reconnect()
        if self.fuel_client is not None:
            self.fuel_client.try_reconnect()

        if hex(msg.arbitration_id) == "0x123" and self.temp_client is not None:
            self.temp_client.publish(
                TEMP_TOPIC, DATA_PATTERN.format(
                    "{:.2f}".format(value), str(
                        time.strftime(
                            TIME_FORMAT, time.localtime())), CELZIUS), QOS)
            customLogger.info("Temperature: " + DATA_PATTERN.format("{:.2f}".format(value),
                                                                    str(time.strftime(TIME_FORMAT, time.localtime())),
                                                                    CELZIUS))
        elif hex(msg.arbitration_id) == "0x124" and self.load_client is not None:
            self.load_client.publish(
                LOAD_TOPIC, DATA_PATTERN.format(
                    "{:.2f}".format(value), str(
                        time.strftime(
                            TIME_FORMAT, time.localtime())), CELZIUS), QOS)
            customLogger.info(
                "Load: " + DATA_PATTERN.format(
                    "{:.2f}".format(value), str(
                        time.strftime(
                            TIME_FORMAT, time.localtime())), KG))
        elif hex(msg.arbitration_id) == "0x125" and self.fuel_client is not None:
            self.fuel_client.publish(
                FUEL_TOPIC, DATA_PATTERN.format(
                    "{:.2f}".format(value), str(
                        time.strftime(
                            TIME_FORMAT, time.localtime())), CELZIUS), QOS)
            customLogger.info(
                "Fuel: " + DATA_PATTERN.format(
                    "{:.2f}".format(value), str(
                        time.strftime(
                            TIME_FORMAT, time.localtime())), _L))
