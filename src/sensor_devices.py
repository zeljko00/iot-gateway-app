"""
sensor_devices
============
Module with logic that simulates three different sensors: fuel level sensor, engine temperature sensor, arm load sensor
Classes
---------
InitFlags: A class that encapsulates four flags that keep track which threads have been initiated

Functions
---------
on_publish(client, userdata,result)
    Logic executed after receiving MQTT broadcast message.

on_connect_temp_sensor(client, userdata, flags, rc,props)
    Logic executed after successfully establishing connection between temperature sensor and MQTT broker.

on_connect_load_sensor(client, userdata, flags, rc,props)
    Logic executed after successfully establishing connection between arm load sensor and MQTT broker.

on_connect_fuel_sensor(client, userdata, flags, rc,props)
    Logic executed after successfully establishing connection between fuel sensor and MQTT broker.

measure_temperature_periodically(period, min_val, avg_val, broker_address, broker_port,mqtt_username,mqtt_pass, flag)
    Periodically generates value representing current temperature.

measure_load_randomly(min_t, max_t, min_val, max_val, broker_address, broker_port, mqtt_username,mqtt_pass, flag)
    Periodically generates value representing current arm load mass.

measure_fuel_periodically(period, capacity, consumption, efficiency, refill, broker_address, broker_port,
                              mqtt_username, mqtt_pass, flag=
    Periodically generates value representing current fuel level.

read_conf()
    Loading config data from config file. Returns sensors' configuration.

sensor_devices()
    Creates 3 processes that represent 3 types of sensors, based on sensors' config and implemented logic.

main()
    Used for testing purposes only. Starts 3 sensors processes and stops them after user request.

Constants
---------
conf_file_path : str
    Path to sensors' config file.

"""
import threading
import time
import random
from pathlib import Path

import signal
import numpy
import json
import math
import paho.mqtt.client as mqtt
from multiprocessing import Event
import logging.config
import logging

from can_service import read_can
from config_util import ConfFlags, start_config_observer
from mqtt_utils import MQTTClient
from config_util import Config
from signal_control import BetterSignalHandler

# setting up loggers
logging_path = Path(__file__).parent / 'logging.conf'
logging.config.fileConfig(logging_path)
infoLogger = logging.getLogger('customInfoLogger')
errorLogger = logging.getLogger('customErrorLogger')
customLogger = logging.getLogger("customConsoleLogger")

# keywords used in sensors' config file
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
MAX = "max_val"
MIN = "min_val"
AVG = "avg_val"
MQTT_BROKER = "mqtt_broker"
ADDRESS = "address"
PORT = "port"

# sensors config file
CONF_FILE_PATH = "configuration/sensor_conf.json"
APP_CONF_FILE_PATH = "configuration/app_conf.json"

# mqtt config data
TRANSPORT_PROTOCOL = "tcp"
QOS = 2

# REST APIs
TEMP_TOPIC = "sensors/temperature"
LOAD_TOPIC = "sensors/arm-load"
FUEL_TOPIC = "sensors/fuel-level"

DATA_PATTERN = "[ value={} , time={} , unit={} ]"
TIME_FORMAT = "%d.%m.%Y %H:%M:%S"

CELZIUS = "C"
KG = "kg"
LITER = "l"


def on_publish(client, userdata, result):
    """
    Logic executed after receiving mqtt message.

    Parameters
    ----------
    client : paho.mqtt.client
    userdata : object
    result: object

    Returns
    -------
    None
    """
    pass


def on_connect_temp_sensor(client, userdata, flags, rc, props):
    """
    Logic executed after establishing connection between temperature sensor process and mqtt broker

    Parameters
    ----------
    client : mqtt.client
    userdata : object
    flags:
    rc: int
    props:


    Returns
    -------
    None
    """
    if rc == 0:
        infoLogger.info(
            "Temperature sensor successfully established connection with MQTT broker!")
        customLogger.debug(
            "Temperature sensor successfully established connection with MQTT broker!")
    else:
        errorLogger.error(
            "Temperature sensor failed to establish connection with MQTT broker!")
        customLogger.critical(
            "Temperature sensor failed to establish connection with MQTT broker!")


def on_connect_load_sensor(client, userdata, flags, rc, props):
    """
    Logic executed after establishing connection between arm load sensor process and mqtt broker

    Parameters
    ----------
    client : paho.mqtt.client
    userdata : object
    flags:
    rc: int
    props:


    Returns
    -------
    None
    """
    if rc == 0:
        infoLogger.info(
            "Arm load sensor successfully established connection with MQTT broker!")
        customLogger.debug(
            "Arm load sensor successfully established connection with MQTT broker!")
    else:
        errorLogger.error(
            "Arm load sensor failed to establish connection with MQTT broker!")
        errorLogger.critical(
            "Arm load sensor failed to establish connection with MQTT broker!")


def on_connect_fuel_sensor(client, userdata, flags, rc, props):
    """
    Logic executed after establishing connection between FUEL sensor process and mqtt broker

    Parameters
    ----------
    client : paho.mqtt.client
    userdata : object
    flags:
    rc: int
    props:


    Returns
    -------
    None
    """
    if rc == 0:
        infoLogger.info(
            "Fuel sensor successfully established connection with MQTT broker!")
        customLogger.debug(
            "Fuel sensor successfully established connection with MQTT broker!")
    else:
        errorLogger.error(
            "Fuel sensor failed to establish connection with MQTT broker!")
        customLogger.critical(
            "Fuel sensor failed to establish connection with MQTT broker!")


# period = measuring interval in sec, min_val/max_val = min/max measured value


def measure_temperature_periodically(
        period,
        min_val,
        avg_val,
        broker_address,
        broker_port,
        mqtt_username,
        mqtt_pass,
        flag,
        config_flag,
        init_flags,
        temp_lock):
    """
    Emulates temperature sensor.

    Periodically generates temperature sensor reading.

    Parameters
    ----------
    period: int
        Measuring interval.
    min_val: int
        Min temperature value that sensor can detect.
    avg_val: int
        Avg engine temperature value.
    broker_address: str
        MQTT broker's URL.
    broker_port: int
        MQTT broker's port.
    mqtt_username: str
        Username required for establishing connection with MQTT broker.
    mqtt_pass: str
        Password required for establishing connection with MQTT broker.
    flag: multiprocessing.Event
        Object used for stopping temperature sensor process.

    Returns
    -------
    None
    """
    customLogger.debug("Temperature sensor started!")
    customLogger.debug(
        "Temperature sensor conf: interval={}s , min={}˚C , avg={}C".format(
            period, min_val, avg_val))
    # preventing division by zero
    if period == 0:
        period = 1
    period = abs(round(period))
    # establishing connection with MQTT broker
    temp_client = MQTTClient(
        "temp-sensor-mqtt-client",
        transport_protocol=TRANSPORT_PROTOCOL,
        protocol_version=mqtt.MQTTv5,
        mqtt_username=mqtt_username,
        mqtt_pass=mqtt_pass,
        broker_address=broker_address,
        broker_port=broker_port,
        keepalive=2 * 3,
        infoLogger=infoLogger,
        errorLogger=errorLogger,
        flag=flag,
        sensor_type="TEMP")
    temp_client.set_on_connect(on_connect_temp_sensor)
    temp_client.set_on_publish(on_publish)
    temp_client.connect()
    # provide sensor with data for 7 days
    values_count = round(7 * 24 * 60 * 60 / period)
    data = numpy.random.uniform(-5, 5, values_count)
    counter = 0
    # determines whether engine is warming up
    raising = True
    # starting temp
    value = min_val
    # shutting down sensor depending on flag
    while not flag.is_set():

        if config_flag.is_set():
            config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
            config.try_open()
            if config.temp_mode == "CAN":
                temp_lock.acquire()
                init_flags.temp_simulator_initiated = False
                temp_lock.release()
                config_flag.clear()
                break

        time.sleep(period)
        # check connection to mqtt broker
        temp_client.try_reconnect()
        try:
            # generating new measured value
            if raising:
                value += numpy.random.uniform(0, math.ceil(period / 10), 1)[0]
                if value > avg_val:
                    raising = False
            else:
                value = avg_val + data[counter % values_count]
                counter += 1
            customLogger.error(
                "Temperature: " + DATA_PATTERN.format(
                    "{:.2f}".format(value),
                    str(
                        time.strftime(
                            TIME_FORMAT,
                            time.localtime())),
                    CELZIUS))
            # send data to MQTT broker
            temp_client.publish(
                TEMP_TOPIC, DATA_PATTERN.format(
                    "{:.2f}".format(value), str(
                        time.strftime(
                            TIME_FORMAT, time.localtime())), CELZIUS), qos=QOS)
        except BaseException:
            errorLogger.error(
                "Connection between temperature sensor and MQTT broker is broken!")
            customLogger.critical(
                "Connection between temperature sensor and MQTT broker is broken!")
    temp_client.disconnect()
    flag.clear()
    infoLogger.info("Temperature sensor shutdown!")
    customLogger.debug("Temperature sensor shutdown!")


# min_t/max_t = min/max measuring period in sec, min_val/max_val = min/max
# measured value
def measure_load_randomly(
        min_t,
        max_t,
        min_val,
        max_val,
        broker_address,
        broker_port,
        mqtt_username,
        mqtt_pass,
        flag,
        config_flag,
        init_flags,
        load_lock):
    """
    Emulates arm load sensor.

    Randomly generates arm load sensor reading.

    Parameters
    ----------
    min_t: int
        Min time-lapse between two measurements.
    max_t: int
        Max time-lapse between two measurements.
    min_val: int
        Min load value that sensor can detect.
    max_val: int
        Max load value that sensor can handle.
    broker_address: str
        MQTT broker's URL
    broker_port: int
        MQTT broker's port.
    mqtt_username: str
        Username required for establishing connection with MQTT broker.
    mqtt_pass: str
        Password required for establishing connection with MQTT broker.
    flag: multiprocessing.Event
        Object used for stopping temperature sensor process.

    Returns
    -------
    None
    """
    customLogger.debug("Arm load sensor started!")
    customLogger.debug(
        "Arm load sensor conf: min_interval={}s , max_interval={}s , min={}kg , max={}kg".format(
            min_t, max_t, min_val, max_val))
    # parameter validation
    if max_t <= min_t:
        max_t = min_t + random.randint(0, 10)
    min_t = abs(round(min_t))
    max_t = abs(round(max_t))
    # establishing connection with MQTT broker
    load_client = MQTTClient(
        "arm-load-sensor-mqtt-client",
        transport_protocol=TRANSPORT_PROTOCOL,
        protocol_version=mqtt.MQTTv5,
        mqtt_username=mqtt_username,
        mqtt_pass=mqtt_pass,
        broker_address=broker_address,
        broker_port=broker_port,
        keepalive=2 * 3,
        infoLogger=infoLogger,
        errorLogger=errorLogger,
        flag=flag,
        sensor_type="LOAD")
    load_client.set_on_connect(on_connect_load_sensor)
    load_client.set_on_publish(on_publish)
    load_client.connect()

    # provide sensor with data for at least 7 days
    values_count = round(7 * 24 * 60 * 60 / min_t)
    # measuring intervals
    intervals = numpy.random.uniform(min_t, max_t, values_count)
    # measured data
    data = numpy.random.uniform(min_val, max_val, values_count)
    counter = 0
    # shut down sensor depending on set flag
    while not flag.is_set():

        if config_flag.is_set():
            config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
            config.try_open()
            if config.load_mode == "CAN":
                load_lock.acquire()
                init_flags.load_simulator_initiated = False
                load_lock.release()
                config_flag.clear()
                break

        time.sleep(round(intervals[counter % values_count]))
        # check connection to mqtt broker
        load_client.try_reconnect()
        try:
            customLogger.info("Load: " + DATA_PATTERN.format("{:.2f}".format(data[counter % values_count]),
                                                             str(time.strftime(TIME_FORMAT, time.localtime())),
                                                             KG))
            # send data to MQTT broker
            load_client.publish(LOAD_TOPIC, DATA_PATTERN.format("{:.2f}".format(data[counter % values_count]), str(
                time.strftime(TIME_FORMAT, time.localtime())), KG), qos=QOS)
        except BaseException:
            errorLogger.error(
                "Connection between arm load sensor and MQTT broker is broken!")
            customLogger.critical(
                "Connection between arm load sensor and MQTT broker is broken!")
        counter += 1
    load_client.disconnect()
    flag.clear()
    infoLogger.info("Arm load sensor shutdown!")
    customLogger.debug("Arm load sensor shutdown!")


# period = measuring interval , capacity = fuel tank capacity , refill = fuel tank refill probability (0-1)
# consumption = fuel usage consumption per working hour, efficiency =
# machine work efficiency (0-1)
def measure_fuel_periodically(
        period,
        capacity,
        consumption,
        efficiency,
        refill,
        broker_address,
        broker_port,
        mqtt_username,
        mqtt_pass,
        flag,
        config_flag,
        init_flags,
        fuel_lock):
    """
    Emulates fuel sensor.

    Periodically generates fuel level sensor reading.

    Parameters
    ----------
    period: int
        Measuring interval.
    capacity: int
        Capacity of fuel tank.
    consumption: float
        Engine fuel consumption [l/h].
    efficiency: float
        Engine efficiency.
    refill: float
        Probability of engine refill.
    broker_address: str
        MQTT broker's URL
    broker_port: int
        MQTT broker's port.
    mqtt_username: str
        Username required for establishing connection with MQTT broker.
    mqtt_pass: str
        Password required for establishing connection with MQTT broker.
    flag: multiprocessing.Event
        Object used for stopping temperature sensor process.
    """
    customLogger.debug("Fuel level sensor started!")
    customLogger.debug(
        "Fuel level sensor conf: period={}s, capacity={}l, consumption={}l/h, efficiency={}, refill={}".format(
            period,
            capacity,
            consumption,
            efficiency,
            refill))

    # parameter validation
    if period == 0:
        period = 1
    period = abs(round(period))
    # establishing connection with MQTT broker
    fuel_client = MQTTClient(
        "fuel-sensor-mqtt-client",
        transport_protocol=TRANSPORT_PROTOCOL,
        protocol_version=mqtt.MQTTv5,
        mqtt_username=mqtt_username,
        mqtt_pass=mqtt_pass,
        broker_address=broker_address,
        broker_port=broker_port,
        keepalive=2 * 3,
        infoLogger=infoLogger,
        errorLogger=errorLogger,
        flag=flag,
        sensor_type="FUEL")
    fuel_client.set_on_connect(on_connect_fuel_sensor)
    fuel_client.set_on_publish(on_publish)
    fuel_client.connect()
    # at first fuel tank is randomly filled
    value = random.randint(round(capacity / 2), round(capacity))
    # constant for scaling consumption per hour to per second
    scale = 1 / (60 * 60)
    # shutting down sensor depending on set flag
    refilling = False
    while not flag.is_set():

        if config_flag.is_set():
            config = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
            config.try_open()
            if config.fuel_mode == "CAN":
                fuel_lock.acquire()
                init_flags.fuel_simulator_initiated = False
                fuel_lock.release()
                config_flag.clear()
                break

        time.sleep(period)
        # fuel tank is filling
        if refilling:
            value = random.randint(round(value), round(capacity))
            refilling = False
        else:
            # deciding whether fuel tank should be refilled based on refill
            # probability
            refilling = random.random() < refill
            # amount of consumed fuel is determined based on fuel consumption, time elapsed
            # from previous measuring and machine state (on/of)
            consumed = period * consumption * scale * (1 + 1 - efficiency)
            # generating new measured value
            value -= consumed
            if value <= 0:
                value = 0
                refilling = True
        # check connection to mqtt broker
        fuel_client.try_reconnect()
        try:
            customLogger.warning(
                "Fuel: " + DATA_PATTERN.format(
                    "{:.2f}".format(value),
                    str(
                        time.strftime(
                            TIME_FORMAT,
                            time.localtime())),
                    LITER))
            # send data to MQTT broker
            fuel_client.publish(
                FUEL_TOPIC, DATA_PATTERN.format(
                    "{:.2f}".format(value), str(
                        time.strftime(
                            TIME_FORMAT, time.localtime())), LITER), qos=QOS)
        except BaseException:
            errorLogger.error(
                "Connection between fuel level sensor and MQTT broker is broken!")
            customLogger.critical(
                "Connection between fuel level sensor and MQTT broker is broken!")
    fuel_client.disconnect()
    flag.clear()
    infoLogger.info("Fuel level sensor shutdown!")
    customLogger.debug("Fuel level sensor shutdown!")


# read sensor conf data
def read_conf():
    """
    Loads sensors' config from config file.

    If config file is inaccessible, default config is used.
    """
    data = None
    try:
        conf_file = open(CONF_FILE_PATH)
        data = json.load(conf_file)
    except BaseException:
        errorLogger.critical(
            "Using default config! Can't read sensor config file - ",
            CONF_FILE_PATH,
            " !")
        customLogger.critical(
            "Using default config! Can't read sensor config file - ",
            CONF_FILE_PATH,
            " !")

        data = {
            TEMP_SENSOR: {
                INTERVAL: 5,
                MIN: -10,
                AVG: 100},
            ARM_SENSOR: {
                ARM_MIN_T: 10,
                ARM_MAX_T: 100,
                MIN: 0,
                MAX: 800},
            FUEL_SENSOR: {
                INTERVAL: 5,
                FUEL_CAPACITY: 300,
                FUEL_CONSUMPTION: 3000,
                FUEL_EFFICIENCY: 0.6,
                FUEL_REFILL: 0.02},
            MQTT_BROKER: {
                ADDRESS: "localhost",
                PORT: 1883,
                MQTT_USER: "iot-device",
                MQTT_PASSWORD: "password"}}
    return data


# creating sensor processes
def sensors_devices(temp_flag, load_flag, fuel_flag, can_flag, config_flags,
                    init_flags, temp_lock, load_lock, fuel_lock, can_lock):
    """
    Creates 3 subprocesses representing 3 sensor devices.

    Parameters
    ----------
    can_flag : multiprocessing.Event
    temp_flag : multiprocessing.Event
    load_flag : multiprocessing.Event
    fuel_flag : multiprocessing.Event

    Returns
    -------
    None
    """
    conf_data = read_conf()
    # app_conf_data = read_app_conf()
    app_conf = Config(APP_CONF_FILE_PATH, errorLogger, customLogger)
    app_conf.try_open()

    sensors = []

    is_can_temp = False
    is_can_load = False
    is_can_fuel = False

    if app_conf.temp_mode == "CAN":
        is_can_temp = True
    if app_conf.load_mode == "CAN":
        is_can_load = True
    if app_conf.fuel_mode == "CAN":
        is_can_fuel = True

    if is_can_temp or is_can_load or is_can_fuel:
        if not init_flags.can_initiated:
            can_sensor = threading.Thread(
                target=read_can,
                args=(
                    can_flag,
                    config_flags.can_flag,
                    init_flags,
                    can_lock))

            sensors.append(can_sensor)
            can_lock.acquire()
            init_flags.can_initiated = True
            can_lock.release()
    if app_conf.temp_mode == "SIMULATOR":
        if not init_flags.temp_simulator_initiated:
            simulation_temperature_sensor = threading.Thread(
                target=measure_temperature_periodically,
                args=(
                    conf_data[TEMP_SENSOR][INTERVAL],
                    conf_data[TEMP_SENSOR][MIN],
                    conf_data[TEMP_SENSOR][AVG],
                    conf_data[MQTT_BROKER][ADDRESS],
                    conf_data[MQTT_BROKER][PORT],
                    conf_data[MQTT_BROKER][MQTT_USER],
                    conf_data[MQTT_BROKER][MQTT_PASSWORD],
                    temp_flag,
                    config_flags.temp_flag,
                    init_flags,
                    temp_lock))
            sensors.append(simulation_temperature_sensor)
            temp_lock.acquire()
            init_flags.temp_simulator_initiated = True
            temp_lock.release()
    if app_conf.load_mode == "SIMULATOR":
        if not init_flags.load_simulator_initiated:
            simulation_load_sensor = threading.Thread(
                target=measure_load_randomly,
                args=(
                    conf_data[ARM_SENSOR][ARM_MIN_T],
                    conf_data[ARM_SENSOR][ARM_MAX_T],
                    conf_data[ARM_SENSOR][MIN],
                    conf_data[ARM_SENSOR][MAX],
                    conf_data[MQTT_BROKER][ADDRESS],
                    conf_data[MQTT_BROKER][PORT],
                    conf_data[MQTT_BROKER][MQTT_USER],
                    conf_data[MQTT_BROKER][MQTT_PASSWORD],
                    load_flag,
                    config_flags.load_flag,
                    init_flags,
                    load_lock))
            sensors.append(simulation_load_sensor)
            load_lock.acquire()
            init_flags.load_simulator_initiated = True
            load_lock.release()
    if app_conf.fuel_mode == "SIMULATOR":

        if not init_flags.fuel_simulator_initiated:
            simulation_fuel_sensor = threading.Thread(
                target=measure_fuel_periodically,
                args=(
                    conf_data[FUEL_SENSOR][INTERVAL],
                    conf_data[FUEL_SENSOR][FUEL_CAPACITY],
                    conf_data[FUEL_SENSOR][FUEL_CONSUMPTION],
                    conf_data[FUEL_SENSOR][FUEL_EFFICIENCY],
                    conf_data[FUEL_SENSOR][FUEL_REFILL],
                    conf_data[MQTT_BROKER][ADDRESS],
                    conf_data[MQTT_BROKER][PORT],
                    conf_data[MQTT_BROKER][MQTT_USER],
                    conf_data[MQTT_BROKER][MQTT_PASSWORD],
                    fuel_flag,
                    config_flags.fuel_flag,
                    init_flags,
                    fuel_lock))
            sensors.append(simulation_fuel_sensor)
            fuel_lock.acquire()
            init_flags.fuel_simulator_initiated = True
            fuel_lock.release()
    return sensors


class InitFlags:
    """A class that encapsulates four flags that keep track which threads have been initiated"""

    def __init__(self):
        """
        Constructor that initializes an MQTT object.
        None of the threads are initiated at first.
        """
        self.can_initiated = False
        self.temp_simulator_initiated = False
        self.load_simulator_initiated = False
        self.fuel_simulator_initiated = False


def main():
    """
    Used for testing sensors.

    Creates and executes 3 sensor subprocesses. Contains logic for user requested sensors' shutdown.
    """
    temp_simulation_flag = Event()
    load_simulation_flag = Event()
    fuel_simulation_flag = Event()
    can_flag = Event()

    main_execution_flag = Event()

    BetterSignalHandler([signal.SIGINT,
                         signal.SIGTERM],
                        [temp_simulation_flag,
                         load_simulation_flag,
                         fuel_simulation_flag,
                         can_flag,
                         main_execution_flag])

    temp_lock = threading.Lock()
    load_lock = threading.Lock()
    fuel_lock = threading.Lock()
    can_lock = threading.Lock()

    app_config_flags = ConfFlags()
    init_flags = InitFlags()
    app_config_observer = start_config_observer(app_config_flags)

    initial = True
    sensors = []

    customLogger.debug("Sensor system starting!")
    initial = True

    # dictionary to track which thread to join, remembering old and new flags
    # from config

    while not main_execution_flag.is_set():
        if app_config_flags.execution_flag.is_set() or initial:
            initial = False
            sensors = sensors_devices(
                temp_simulation_flag,
                load_simulation_flag,
                fuel_simulation_flag,
                can_flag,
                app_config_flags,
                init_flags,
                can_lock,
                temp_lock,
                load_lock,
                fuel_lock)
            app_config_flags.execution_flag.clear()
            if sensors is not None:
                for sensor in sensors:
                    sensor.start()
                    time.sleep(0.1)
        time.sleep(2)
    for sensor in sensors:
        sensor.join()

    app_config_observer.stop()
    app_config_observer.join()
    infoLogger.info("Sensor system shutdown!")
    customLogger.debug("Sensor system shutdown!")


if __name__ == '__main__':
    main()
