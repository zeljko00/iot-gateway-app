'''
sensor_devices
============
Module with logic that simulates three different sensors: fuel level sensor, engine temperature sensor, arm load sensor

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

'''
import multiprocessing
import threading
import time
import random
from pathlib import Path

import numpy
import json
import math
import paho.mqtt.client as mqtt
from multiprocessing import Process, Event
import logging.config
import logging

from can_service import read_can, read_app_conf
from config_util import ConfFlags, start_config_observer
from mqtt_utils import MQTTClient
from config_util import Config

# setting up loggers
logging_path = Path(__file__).parent / 'logging.conf'
logging.config.fileConfig(logging_path)
infoLogger = logging.getLogger('customInfoLogger')
errorLogger = logging.getLogger('customErrorLogger')
customLogger = logging.getLogger("customConsoleLogger")

# keywords used in sensors' config file
mode = "mode"
temp_settings = "temp_settings"
load_settings = "load_settings"
fuel_settings = "fuel_settings"
can_general_settings = "can_general_settings"
channel = "channel"
interface = "interface"
bitrate = "bitrate"

temp_sensor = "temp_sensor"
arm_sensor = "arm_sensor"
arm_min_t = "min_t"
arm_max_t = "max_t"
fuel_sensor = "fuel_sensor"
fuel_consumption = "consumption"
fuel_capacity = "capacity"
fuel_efficiency = "efficiency"
fuel_refill = "refill"
interval = "period"
mqtt_user = "username"
mqtt_password = "password"
max = "max_val"
min = "min_val"
avg = "avg_val"
mqtt_broker = "mqtt_broker"
address = "address"
port = "port"

# sensors config file
conf_file_path = "configuration/sensor_conf.json"
app_conf_file_path = "configuration/app_conf.json"

# mqtt config data
transport_protocol = "tcp"
qos = 2

# REST APIs
temp_topic = "sensors/temperature"
load_topic = "sensors/arm-load"
fuel_topic = "sensors/fuel-level"

data_pattern = "[ value={} , time={} , unit={} ]"
time_format = "%d.%m.%Y %H:%M:%S"

celzius = "C"
kg = "kg"
liter = "l"


def on_publish(client, userdata, result):
    '''
    Logic executed after receiving mqtt message.

    Parameters
    ----------
    client : paho.mqtt.client
    userdata : object
    result: object

    Returns
    -------
    None
    '''
    pass


def on_connect_temp_sensor(client, userdata, flags, rc, props):
    '''
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
    '''
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
    '''
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
    '''
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
    '''
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
    '''
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
    '''
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
    '''
    customLogger.debug("Temperature sensor started!")
    customLogger.debug(
        "Temperature sensor conf: interval={}s , min={}˚C , avg={}C".format(
            period, min_val, avg_val))
    # preventing division by zero
    if period == 0:
        period = 1
    period = abs(round(period))
    # establishing connection with MQTT broker
    client = mqtt.Client(
        client_id="temp-sensor-mqtt-client",
        transport=transport_protocol,
        protocol=mqtt.MQTTv5)
    client.username_pw_set(username=mqtt_username, password=mqtt_pass)
    client.on_connect = on_connect_temp_sensor
    client.on_publish = on_publish
    while not client.is_connected():
        try:
            infoLogger.info(
                "Temperature sensor establishing connection with MQTT broker!")
            client.connect(
                broker_address,
                port=broker_port,
                keepalive=period * 3)
            client.loop_start()
            time.sleep(0.2)
        except BaseException:
            errorLogger.error(
                "Temperature sensor failed to establish connection with MQTT broker!")
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
            config = Config(app_conf_file_path, errorLogger, customLogger)
            config.try_open()
            if config.get_temp_mode() == "CAN":
                temp_lock.acquire()
                init_flags.temp_simulator_initiated = False
                temp_lock.release()
                config_flag.clear()
                break  # TODO BREAK?? or flag?

        time.sleep(period)
        # check connection to mqtt broker
        while not client.is_connected():
            errorLogger.error(
                "Temperature sensor lost connection to MQTT broker!")
            client.reconnect()
            time.sleep(0.2)
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
                "Temperature: " + data_pattern.format(
                    "{:.2f}".format(value),
                    str(
                        time.strftime(
                            time_format,
                            time.localtime())),
                    celzius))
            # send data to MQTT broker
            client.publish(
                temp_topic, data_pattern.format(
                    "{:.2f}".format(value), str(
                        time.strftime(
                            time_format, time.localtime())), celzius), qos=qos)
        except BaseException:
            errorLogger.error(
                "Connection between temperature sensor and MQTT broker is broken!")
            customLogger.critical(
                "Connection between temperature sensor and MQTT broker is broken!")
    client.loop_stop()
    client.disconnect()
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
    '''
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
    '''
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
    client = mqtt.Client(
        client_id="arm-load-sensor-mqtt-client",
        transport=transport_protocol,
        protocol=mqtt.MQTTv5)
    client.username_pw_set(username=mqtt_username, password=mqtt_pass)
    client.on_connect = on_connect_load_sensor
    client.on_publish = on_publish
    while not client.is_connected() and not flag.is_set():
        try:
            infoLogger.info(
                "Arm load sensor establishing connection with MQTT broker!")
            client.connect(
                broker_address,
                port=broker_port,
                keepalive=min_t * 3)
            client.loop_start()
            time.sleep(0.2)
        except BaseException:
            errorLogger.error(
                "Arm load sensor failed to establish connection with MQTT broker!")
    # provide sensor with data for at least 7 days
    values_count = round(7 * 24 * 60 * 60 / min_t)
    # measuring intervals
    intervals = numpy.random.uniform(min_t, max_t, values_count)
    # measured data
    data = numpy.random.uniform(min_val, max_val, values_count)
    counter = 0
    # shut down sensor depending on set flag
    while not flag.is_set():

        if config_flag.is_set(
        ):  # TODO this is just for the mode, what if the broker data has been changed?
            config = Config(app_conf_file_path, errorLogger, customLogger)
            config.try_open()
            if config.get_load_mode() == "CAN":
                load_lock.acquire()
                init_flags.load_simulator_initiated = False
                load_lock.release()
                config_flag.clear()
                break  # TODO BREAK?? or flag?

        time.sleep(round(intervals[counter % values_count]))
        # check connection to mqtt broker
        while not client.is_connected() and not flag.is_set():
            errorLogger.error(
                "Arm load sensor lost connection to MQTT broker!")
            client.reconnect()
            time.sleep(0.1)
        try:
            customLogger.info("Load: " + data_pattern.format("{:.2f}".format(data[counter % values_count]),
                                                             str(time.strftime(time_format, time.localtime())),
                                                             kg))
            # send data to MQTT broker
            client.publish(load_topic, data_pattern.format("{:.2f}".format(data[counter % values_count]), str(
                time.strftime(time_format, time.localtime())), kg), qos=qos)
        except BaseException:
            errorLogger.error(
                "Connection between arm load sensor and MQTT broker is broken!")
            customLogger.critical(
                "Connection between arm load sensor and MQTT broker is broken!")
        counter += 1
    client.loop_stop()
    client.disconnect()
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
    '''
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

    Returns
    -------

    None
    '''
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
    client = mqtt.Client(
        client_id="fuel-sensor-mqtt-client",
        transport=transport_protocol,
        protocol=mqtt.MQTTv5)
    client.username_pw_set(username=mqtt_username, password=mqtt_pass)
    client.on_connect = on_connect_fuel_sensor
    client.on_publish = on_publish
    while not client.is_connected():
        infoLogger.info(
            "Fuel level sensor establishing connection with MQTT broker!")
        try:
            client.connect(
                broker_address,
                port=broker_port,
                keepalive=period * 3)
            client.loop_start()
            time.sleep(0.2)
        except BaseException:
            errorLogger.error(
                "Fuel sensor failed to establish connection with MQTT broker!")
    # at first fuel tank is randomly filled
    value = random.randint(round(capacity / 2), round(capacity))
    # constant for scaling consumption per hour to per second
    scale = 1 / (60 * 60)
    # shutting down sensor depending on set flag
    refilling = False
    while not flag.is_set():

        if config_flag.is_set():
            config = Config(app_conf_file_path, errorLogger, customLogger)
            config.try_open()
            if config.get_fuel_mode() == "CAN":
                fuel_lock.acquire()
                init_flags.fuel_simulator_initiated = False
                fuel_lock.release()
                config_flag.clear()
                break  # TODO BREAK?? or flag?

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
        while not client.is_connected():
            errorLogger.error(
                "Fuel level sensor lost connection to MQTT broker!")
            client.reconnect()
            time.sleep(0.1)
        try:
            customLogger.warning(
                "Fuel: " + data_pattern.format(
                    "{:.2f}".format(value),
                    str(
                        time.strftime(
                            time_format,
                            time.localtime())),
                    liter))
            # send data to MQTT broker
            client.publish(
                fuel_topic, data_pattern.format(
                    "{:.2f}".format(value), str(
                        time.strftime(
                            time_format, time.localtime())), liter), qos=qos)
        except BaseException:
            errorLogger.error(
                "Connection between fuel level sensor and MQTT broker is broken!")
            customLogger.critical(
                "Connection between fuel level sensor and MQTT broker is broken!")
    client.loop_stop()
    client.disconnect()
    infoLogger.info("Fuel level sensor shutdown!")
    customLogger.debug("Fuel level sensor shutdown!")


# read sensor conf data
def read_conf():
    '''
    Loads sensors' config from config file.

    If config file is inaccessible, default config is used.

    Parameters
    ----------

    Returns
    -------
    '''
    data = None
    try:
        conf_file = open(conf_file_path)
        data = json.load(conf_file)
    except BaseException:
        errorLogger.critical(
            "Using default config! Can't read sensor config file - ",
            conf_file_path,
            " !")
        customLogger.critical(
            "Using default config! Can't read sensor config file - ",
            conf_file_path,
            " !")

        data = {
            temp_sensor: {
                interval: 5,
                min: -10,
                avg: 100},
            arm_sensor: {
                arm_min_t: 10,
                arm_max_t: 100,
                min: 0,
                max: 800},
            fuel_sensor: {
                interval: 5,
                fuel_capacity: 300,
                fuel_consumption: 3000,
                fuel_efficiency: 0.6,
                fuel_refill: 0.02},
            mqtt_broker: {
                address: "localhost",
                port: 1883,
                mqtt_user: "iot-device",
                mqtt_password: "password"}}
    return data


def read_app_conf():
    data = None
    try:
        conf_file = open(app_conf_file_path)
        data = json.load(conf_file)
    except BaseException:
        errorLogger.critical(
            "Using default config! Can't read app config file - ",
            app_conf_file_path,
            " !")
        customLogger.critical(
            "Using default config! Can't read app config file - ",
            app_conf_file_path,
            " !")

        data = {fuel_settings: {"fuel_level_limit": 200, mode: "CAN"},
                temp_settings: {"temp_interval": 20, mode: "CAN"},
                load_settings: {"load_interval": 20, mode: "SIMULATOR"}, }

    return data


# creating sensor processes
def sensors_devices(temp_flag, load_flag, fuel_flag, can_flag, config_flags,
                    init_flags, temp_lock, load_lock, fuel_lock, can_lock):
    '''
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
    '''
    conf_data = read_conf()
    # app_conf_data = read_app_conf()
    app_conf = Config(app_conf_file_path, errorLogger, customLogger)
    app_conf.try_open()

    sensors = []

    is_can_temp = False
    is_can_load = False
    is_can_fuel = False

    if app_conf.get_temp_mode() == "CAN":
        is_can_temp = True
    if app_conf.get_load_mode() == "CAN":
        is_can_load = True
    if app_conf.get_fuel_mode() == "CAN":
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
    if app_conf.get_temp_mode() == "SIMULATOR":
        if not init_flags.temp_simulator_initiated:
            simulation_temperature_sensor = threading.Thread(
                target=measure_temperature_periodically,
                args=(
                    conf_data[temp_sensor][interval],
                    conf_data[temp_sensor][min],
                    conf_data[temp_sensor][avg],
                    conf_data[mqtt_broker][address],
                    conf_data[mqtt_broker][port],
                    conf_data[mqtt_broker][mqtt_user],
                    conf_data[mqtt_broker][mqtt_password],
                    temp_flag,
                    config_flags.temp_flag,
                    init_flags,
                    temp_lock))
            sensors.append(simulation_temperature_sensor)
            temp_lock.acquire()
            init_flags.temp_simulator_initiated = True
            temp_lock.release()
    if app_conf.get_load_mode() == "SIMULATOR":
        if not init_flags.load_simulator_initiated:
            simulation_load_sensor = threading.Thread(
                target=measure_load_randomly,
                args=(
                    conf_data[arm_sensor][arm_min_t],
                    conf_data[arm_sensor][arm_max_t],
                    conf_data[arm_sensor][min],
                    conf_data[arm_sensor][max],
                    conf_data[mqtt_broker][address],
                    conf_data[mqtt_broker][port],
                    conf_data[mqtt_broker][mqtt_user],
                    conf_data[mqtt_broker][mqtt_password],
                    load_flag,
                    config_flags.load_flag,
                    init_flags,
                    load_lock))
            sensors.append(simulation_load_sensor)
            load_lock.acquire()
            init_flags.load_simulator_initiated = True
            load_lock.release()
    if app_conf.get_fuel_mode() == "SIMULATOR":

        if not init_flags.fuel_simulator_initiated:
            simulation_fuel_sensor = threading.Thread(
                target=measure_fuel_periodically,
                args=(
                    conf_data[fuel_sensor][interval],
                    conf_data[fuel_sensor][fuel_capacity],
                    conf_data[fuel_sensor][fuel_consumption],
                    conf_data[fuel_sensor][fuel_efficiency],
                    conf_data[fuel_sensor][fuel_refill],
                    conf_data[mqtt_broker][address],
                    conf_data[mqtt_broker][port],
                    conf_data[mqtt_broker][mqtt_user],
                    conf_data[mqtt_broker][mqtt_password],
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
    def __init__(self):
        self.can_initiated = False
        self.temp_simulator_initiated = False
        self.load_simulator_initiated = False
        self.fuel_simulator_initiated = False

    def has_started(self):
        if (self.can_initiated is True or
                self.temp_simulator_initiated is True or
                self.load_simulator_initiated is True or
                self.fuel_simulator_initiated is True):
            return True
        return False


def main():
    '''
    Used for testing sensors.

    Creates and executes 3 sensor subprocesses. Contains logic for user requested sensors' shutdown.

    Parameters
    ----------

    Returns
    -------
    None
    '''
    temp_simulation_flag = Event()
    load_simulation_flag = Event()
    fuel_simulation_flag = Event()
    can_flag = Event()

    main_execution_flag = Event()

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

    app_config_observer.join()
    infoLogger.info("Sensor system shutdown!")
    customLogger.debug("Sensor system shutdown!")


def shutdown_controller(
        temp_handler_flag,
        load_handler_flag,
        fuel_handler_flag,
        can_flag,
        main_execution_flag):
    '''
    Handles user request for sensor shutdown.

    When user requests shutdown, sets sensor processes' stop tokens.

    Parameters
    ----------
    temp_handler_flag: multiprocessing.Event
        Token used for stopping temperature sensor process.
    load_handler_flag: multiprocessing.Event
        Token used for stopping load sensor process.
    fuel_handler_flag: multiprocessing.Event
        Token used for stopping fuel sensor process.

    Returns
    -------
    '''
    # waiting for shutdown signal
    input("")
    infoLogger.info("Sensor app shutting down! Please wait")
    customLogger.debug("Sensor app shutting down! Please wait")
    # shutting down handler processes
    temp_handler_flag.set()
    load_handler_flag.set()
    fuel_handler_flag.set()
    can_flag.set()
    main_execution_flag.set()


if __name__ == '__main__':
    main()
