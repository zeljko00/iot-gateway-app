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
import time
import random
import numpy
import json
import math
import paho.mqtt.client as mqtt
from multiprocessing import Process, Event
import logging.config

# setting up loggers
logging.config.fileConfig('logging.conf')
infoLogger = logging.getLogger('customInfoLogger')
errorLogger = logging.getLogger('customErrorLogger')
customLogger=logging.getLogger("customConsoleLogger")

# keywords used in sensors' config file
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
avg= "avg_val"
mqtt_broker="mqtt_broker"
address="address"
port="port"

# sensors config file
conf_file_path = "sensor_conf.json"

# mqtt config data
transport_protocol="tcp"
qos = 2

# REST APIs
temp_topic="sensors/temperature"
load_topic="sensors/arm-load"
fuel_topic="sensors/fuel-level"

data_pattern="[ value={} , time={} , unit={} ]"
time_format = "%d.%m.%Y %H:%M:%S"

celzius = "C"
kg = "kg"
liter = "l"

def on_publish(client, userdata,result):
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
def on_connect_temp_sensor(client, userdata, flags, rc,props):
    '''
    Logic executed after establishing connection between temperature sensor process and mqtt broker

    Parameters
    ----------
    client : mqttclient
    userdata : object
    flags:
    rc: int
    props:


    Returns
    -------
    None
    '''
    if rc == 0:
        infoLogger.info("Temperature sensor successfully established connection with MQTT broker!")
        customLogger.debug("Temperature sensor successfully established connection with MQTT broker!")
    else:
        errorLogger.error("Temperature sensor failed to establish connection with MQTT broker!")
        customLogger.critical("Temperature sensor failed to establish connection with MQTT broker!")
def on_connect_load_sensor(client, userdata, flags, rc,props):
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
        infoLogger.info("Arm load sensor successfully established connection with MQTT broker!")
        customLogger.debug("Arm load sensor successfully established connection with MQTT broker!")
    else:
        errorLogger.error("Arm load sensor failed to establish connection with MQTT broker!")
        errorLogger.critical("Arm load sensor failed to establish connection with MQTT broker!")
def on_connect_fuel_sensor(client, userdata, flags, rc,props):
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
        infoLogger.info("Fuel sensor successfully established connection with MQTT broker!")
        customLogger.debug("Fuel sensor successfully established connection with MQTT broker!")
    else:
        errorLogger.error("Fuel sensor failed to establish connection with MQTT broker!")
        customLogger.critical("Fuel sensor failed to establish connection with MQTT broker!")

# period = measuring interval in sec, min_val/max_val = min/max measured value
def measure_temperature_periodically(period, min_val, avg_val, broker_address, broker_port,mqtt_username,mqtt_pass, flag):
    '''
    Emulates temperature sensor.

    Periodically generates temperature sensor reading.

    Parameters
    ----------
    period: int
    min_val: int
    avg_val: int
    broker_address: str
    broker_port: int
    mqtt_username: str
    mqtt_pass: str
    flag: multiprocessing.Event

    Returns
    -------
    None
    '''
    customLogger.debug("Temperature sensor started!")
    customLogger.debug("Temperature sensor conf: interval={}s , min={}˚C , avg={}C".format(period, min_val,avg_val))
    # preventing division by zero
    if period == 0:
        period = 1
    period = abs(round(period))
    # establishing connection with MQTT broker
    client = mqtt.Client(client_id="temp-sensor-mqtt-client", transport=transport_protocol, protocol=mqtt.MQTTv5)
    client.username_pw_set(username=mqtt_username, password=mqtt_pass)
    client.on_connect=on_connect_temp_sensor
    client.on_publish=on_publish
    while not client.is_connected():
        try:
            infoLogger.info("Temperature sensor establishing connection with MQTT broker!")
            client.connect(broker_address, port=broker_port, keepalive=period*3)
            client.loop_start()
            time.sleep(0.2)
        except:
            errorLogger.error("Temperature sensor failed to establish connection with MQTT broker!")
    # provide sensor with data for 7 days
    values_count = round(7 * 24 * 60 * 60 / period)
    data = numpy.random.uniform(-5, 5, values_count)
    counter = 0
    # determines whether engine is warming up
    raising=True
    # starting temp
    value = min_val
    # shutting down sensor depending on set flag
    while not flag.is_set():
        time.sleep(period)
        # check connection to mqtt broker
        while not client.is_connected():
            errorLogger.error("Temperature sensor lost connection to MQTT broker!")
            client.reconnect()
            time.sleep(0.2)
        try:
            # generating new measured value
            if raising:
                value += numpy.random.uniform(0, math.ceil(period/10),1)[0]
                if value > avg_val:
                    raising = False
            else:
                value = avg_val+data[counter % values_count]
                counter += 1
            customLogger.error("Temperature: "+data_pattern.format("{:.2f}".format(value), str(time.strftime(time_format, time.localtime())), celzius))
            # send data to MQTT broker
            client.publish(temp_topic, data_pattern.format("{:.2f}".format(value), str(time.strftime(time_format,
                                                                                         time.localtime())), celzius),qos=qos)
        except:
            errorLogger.error("Connection between temperature sensor and MQTT broker is broken!")
            customLogger.critical("Connection between temperature sensor and MQTT broker is broken!")
    client.loop_stop()
    client.disconnect()
    infoLogger.info("Temperature sensor shutdown!")
    customLogger.debug("Temperature sensor shutdown!")


# min_t/max_t = min/max measuring period in sec, min_val/max_val = min/max measured value
def measure_load_randomly(min_t, max_t, min_val, max_val, broker_address, broker_port, mqtt_username,mqtt_pass, flag):
    '''
    Emulates arm load sensor.

    Randomly generates arm load sensor reading.

    Parameters
    ----------
    min_t: int
    max_t: int
    min_val: int
    max_val: int
    broker_address: str
    broker_port: int
    mqtt_username: str
    mqtt_pass: str
    flag: multiprocessing.Event

    Returns
    -------
    None
    '''
    customLogger.debug("Arm laod sensor started!")
    customLogger.debug("Arm load sensor conf: min_interval={}s , max_interval={}s , min={}kg , max={}kg".format(min_t, max_t, min_val, max_val))
    # parameter validation
    if max_t <= min_t:
        max_t = min_t + random.randint(0,10)
    min_t = abs(round(min_t))
    max_t = abs(round(max_t))
    # establishing connection with MQTT broker
    client = mqtt.Client(client_id="arm-load-sensor-mqtt-client", transport=transport_protocol, protocol=mqtt.MQTTv5)
    client.username_pw_set(username=mqtt_username, password=mqtt_pass)
    client.on_connect = on_connect_load_sensor
    client.on_publish = on_publish
    while not client.is_connected():
        try:
            infoLogger.info("Arm load sensor establishing connection with MQTT broker!")
            client.connect(broker_address, port=broker_port, keepalive=min_t*3)
            client.loop_start()
            time.sleep(0.2)
        except:
            errorLogger.error("Arm load sensor failed to establish connection with MQTT broker!")
    # provide sensor with data for at least 7 days
    values_count = round(7 * 24 * 60 * 60 / min_t)
    # measuring intervals
    intervals = numpy.random.uniform(min_t, max_t, values_count)
    # measured data
    data = numpy.random.uniform(min_val, max_val, values_count)
    counter = 0
    # shut down sensor depending on set flag
    while not flag.is_set():
        time.sleep(round(intervals[counter % values_count]))
        # check connection to mqtt broker
        while not client.is_connected():
            errorLogger.error("Arm load sensor lost connection to MQTT broker!")
            client.reconnect()
            time.sleep(0.1)
        try:
            customLogger.info("Load: "+data_pattern.format("{:.2f}".format(data[counter % values_count]),
                                      str(time.strftime(time_format, time.localtime())), kg))
            # send data to MQTT broker
            client.publish(load_topic, data_pattern.format("{:.2f}".format(data[counter % values_count]),str(time.strftime(time_format, time.localtime())),kg),
                           qos=qos)
        except:
            errorLogger.error("Connection between arm load sensor and MQTT broker is broken!")
            customLogger.critical("Connection between arm load sensor and MQTT broker is broken!")
        counter += 1
    client.loop_stop()
    client.disconnect()
    infoLogger.info("Arm load sensor shutdown!")
    customLogger.debug("Arm load sensor shutdown!")


# period = measuring interval , capacity = fuel tank capacity , refill = fuel tank refill probability (0-1)
# consumption = fuel usage consumption per working hour, efficiency = machine work efficiency (0-1)
def measure_fuel_periodically(period, capacity, consumption, efficiency, refill, broker_address, broker_port,
                              mqtt_username, mqtt_pass, flag):
    '''
    Emulates fuel sensor.

    Periodically generates fuel level sensor reading.

    Parameters
    ----------
    period: int
    capacity: int
    consumption: float
    efficiency: float
    refill: float
    broker_address: str
    broker_port: int
    mqtt_username: str
    mqtt_pass: str
    flag: multiprocessing.Event

    Returns
    -------
    None
    '''
    customLogger.debug("Fuel level sensor started!")
    customLogger.debug("Fuel level sensor conf: period={}s , capacity={}l , consumption={}l/h , efficiency={} , refill={}".
          format(period, capacity, consumption, efficiency, refill))
    # parameter validation
    if period == 0:
        period = 1
    period = abs(round(period))
    # establishing connection with MQTT broker
    client = mqtt.Client(client_id="fuel-sensor-mqtt-client", transport=transport_protocol, protocol=mqtt.MQTTv5)
    client.username_pw_set(username=mqtt_username, password=mqtt_pass)
    client.on_connect = on_connect_fuel_sensor
    client.on_publish = on_publish
    while not client.is_connected():
        infoLogger.info("Fuel level sensor establishing connection with MQTT broker!")
        try:
            client.connect(broker_address, port=broker_port, keepalive=period * 3)
            client.loop_start()
            time.sleep(0.2)
        except:
            errorLogger.error("Fuel sensor failed to establish connection with MQTT broker!")
    # at first fuel tank is randomly filled
    value = random.randint(round(capacity / 2), round(capacity))
    # constant for scaling consumption per hour to per second
    scale = 1 / (60 * 60)
    # shutting down sensor depending on set flag
    refilling = False
    while not flag.is_set():
        time.sleep(period)
        # fuel tank is filling
        if refilling:
            value = random.randint(round(value), round(capacity))
            refilling = False
        else:
            # deciding whether fuel tank should be refilled based on refill probability
            refilling = random.random() < refill
            # amount of consumed fuel is determined based on fuel consumption, time elapsed
            # from previous measuring and machine state (on/of)
            consumed = period * consumption * scale * (1 + 1 - efficiency)
            # generating new measured value
            value -= consumed;
            if value <= 0:
                value = 0
                refilling = True
        # check connection to mqtt broker
        while not client.is_connected():
            errorLogger.error("Fuel level sensor lost connection to MQTT broker!")
            client.reconnect()
            time.sleep(0.1)
        try:
            customLogger.warning("Fuel: "+data_pattern.format("{:.2f}".format(value),
                                      str(time.strftime(time_format, time.localtime())), liter))
            # send data to MQTT broker
            client.publish(fuel_topic,
                           data_pattern.format("{:.2f}".format(value),str(time.strftime(time_format, time.localtime())), liter),
                           qos=qos)
        except:
            errorLogger.error("Connection between fuel level sensor and MQTT broker is broken!")
            customLogger.critical("Connection between fuel level sensor and MQTT broker is broken!")
    client.loop_stop()
    client.disconnect()
    infoLogger.info("Fuel level sensor shutdown!")
    customLogger.debug("Fuel level sensor shutdown!")



# read sensor conf data
def read_conf():
    '''
    Loads sensors' config from config file. If config file is inaccessible, default config is used.

    Parameters
    ----------

    Returns
    -------
    None
    '''
    data = None
    try:
        conf_file = open(conf_file_path)
        data = json.load(conf_file)
    except:
        errorLogger.critical("Using default config! Can't read sensor config file - ", conf_file_path, " !")
        customLogger.critical("Using default config! Can't read sensor config file - ", conf_file_path, " !")

        data = {temp_sensor: {interval: 5, min: -10, avg: 100},
                arm_sensor: {arm_min_t: 10, arm_max_t: 100, min: 0, max: 800},
                fuel_sensor: {interval: 5, fuel_capacity: 300, fuel_consumption: 3000, fuel_efficiency: 0.6,
                              fuel_refill: 0.02},
                mqtt_broker: { address: "localhost", port:1883, mqtt_user: "iot-device", mqtt_password: "password"}}
    return data


# creating sensor processes
def sensors_devices(temp_flag, load_flag, fuel_flag):
    '''
    Creates 3 subprocesses representing 3 sensor devices.

    Parameters
    ----------
    temp_flag : multiprocessing.Event
    load_flagž : multiprocessing.Event
    fuel_flag: multiprocessing.Event

    Returns
    -------
    None
    '''
    conf_data = read_conf()
    temperature_sensor = Process(target=measure_temperature_periodically, args=(conf_data[temp_sensor][interval],
                                                                                conf_data[temp_sensor][min],
                                                                                conf_data[temp_sensor][avg],
                                                                                conf_data[mqtt_broker][address],
                                                                                conf_data[mqtt_broker][port],
                                                                                conf_data[mqtt_broker][mqtt_user],
                                                                                conf_data[mqtt_broker][mqtt_password],
                                                                                temp_flag, ))
    excavator_arm_sensor = Process(target=measure_load_randomly, args=(conf_data[arm_sensor][arm_min_t],
                                                                       conf_data[arm_sensor][arm_max_t],
                                                                       conf_data[arm_sensor][min],
                                                                       conf_data[arm_sensor][max],
                                                                       conf_data[mqtt_broker][address],
                                                                       conf_data[mqtt_broker][port],
                                                                       conf_data[mqtt_broker][mqtt_user],
                                                                       conf_data[mqtt_broker][mqtt_password],
                                                                       load_flag,))
    fuel_level_sensor = Process(target=measure_fuel_periodically, args=(conf_data[fuel_sensor][interval],
                                                                        conf_data[fuel_sensor][fuel_capacity],
                                                                        conf_data[fuel_sensor][fuel_consumption],
                                                                        conf_data[fuel_sensor][fuel_efficiency],
                                                                        conf_data[fuel_sensor][fuel_refill],
                                                                        conf_data[mqtt_broker][address],
                                                                        conf_data[mqtt_broker][port],
                                                                        conf_data[mqtt_broker][mqtt_user],
                                                                        conf_data[mqtt_broker][mqtt_password],
                                                                        fuel_flag,))
    return [temperature_sensor, excavator_arm_sensor, fuel_level_sensor]


def main():
    '''
    Used for testing sensors.

    Creates and executes 3 sensor subprocesses.

    Parameters
    ----------

    Returns
    -------
    None
    '''
    temp_flag = Event()
    load_flag = Event()
    fuel_flag = Event()
    sensors = sensors_devices(temp_flag, load_flag, fuel_flag)
    infoLogger.info("Sensor system started!")
    customLogger.debug("Sensor system starting!")
    for sensor in sensors:
        sensor.start()
        time.sleep(0.1)
    # waiting for shutdown signal (input)
    input("")
    infoLogger.info("Sensor system shutting down! Please wait")
    customLogger.info("Sensor system shutting down! Please wait")
    # shutting down sensor processes
    temp_flag.set()
    load_flag.set()
    fuel_flag.set()
    for sensor in sensors:
        sensor.join()
    infoLogger.info("Sensor system shutdown!")
    customLogger.debug("Sensor system shutdown!")

if __name__ == '__main__':
    main()