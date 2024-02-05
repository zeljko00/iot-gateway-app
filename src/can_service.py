import can
import logging.config

import numpy as np
import paho.mqtt.client as mqtt
import logging
import time
import struct

from multiprocessing import Process, Event
from src.mqtt_utils import MQTTClient


logging.config.fileConfig('logging.conf')
infoLogger = logging.getLogger('customInfoLogger')
errorLogger = logging.getLogger('customErrorLogger')
customLogger=logging.getLogger("customConsoleLogger")

transport_protocol="tcp"
temp_topic="sensors/temperature"
load_topic="sensors/arm-load"
fuel_topic="sensors/fuel-level"

data_pattern ="[ value={} , time={} , unit={} ]"
time_format = "%d.%m.%Y %H:%M:%S"
celzius = "C"

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
avg= "avg_val"
mqtt_broker="mqtt_broker"
address="address"
port="port"

qos = 2


def read_can(interface, channel, bitrate, is_can_temp, is_can_load, is_can_fuel, conf_data, flag):
    bus = can.interface.Bus(interface=interface,
                            channel=channel,
                            bitrate=bitrate)
    customLogger.debug("CAN process started!")
    print("CAN PROCESS STARTED")
    period = conf_data[temp_sensor][interval]
    if period == 0:
        period = 1
    period = abs(round(period))

    temp_client = None
    load_client = None
    fuel_client = None

    if is_can_temp:
        temp_client = MQTTClient("temp-sensor-mqtt-client", transport_protocol=transport_protocol,
                             protocol_version=mqtt.MQTTv5,
                             mqtt_username=conf_data[mqtt_broker][mqtt_user],
                             mqtt_pass=conf_data[mqtt_broker][mqtt_password],
                             broker_address=conf_data[mqtt_broker][address],
                             broker_port=conf_data[mqtt_broker][port],
                             keepalive=conf_data[temp_sensor][interval] * 3,
                             infoLogger=infoLogger,
                             errorLogger=errorLogger,
                             flag=flag)
        temp_client.set_on_connect(on_connect_temp_sensor)
        temp_client.set_on_publish(on_publish)

    if is_can_load:
        load_client = MQTTClient("load-sensor-mqtt-client", transport_protocol=transport_protocol,
                             protocol_version=mqtt.MQTTv5,
                             mqtt_username=conf_data[mqtt_broker][mqtt_user],
                             mqtt_pass=conf_data[mqtt_broker][mqtt_password],
                             broker_address=conf_data[mqtt_broker][address],
                             broker_port=conf_data[mqtt_broker][port],
                             keepalive=2 * 3,
                             infoLogger=infoLogger,
                             errorLogger=errorLogger,
                             flag=flag)
        load_client.set_on_connect(on_connect_load_sensor)
        load_client.set_on_publish(on_publish)

    if is_can_fuel:
        fuel_client = MQTTClient("fuel-sensor-mqtt-client", transport_protocol=transport_protocol,
                             protocol_version=mqtt.MQTTv5,
                             mqtt_username=conf_data[mqtt_broker][mqtt_user],
                             mqtt_pass=conf_data[mqtt_broker][mqtt_password],
                             broker_address=conf_data[mqtt_broker][address],
                             broker_port=conf_data[mqtt_broker][port],
                             keepalive=conf_data[fuel_sensor][interval] * 3,
                             infoLogger=infoLogger,
                             errorLogger=errorLogger,
                             flag=flag)
        fuel_client.set_on_connect(on_connect_fuel_sensor)
        fuel_client.set_on_publish(on_publish)

    notifier = can.Notifier(bus, [], timeout=period)
    can_listener = CANListener(temp_client, load_client, fuel_client)
    notifier.add_listener(can_listener)

    while not flag.is_set(): #TODO wait
        print("WAITING")
        time.sleep(period)

    notifier.stop(timeout=5)


def read_can_temperature(interface, channel, bitrate, period, broker_address, broker_port, mqtt_username,mqtt_pass, flag):
    bus = can.interface.Bus(interface=interface,
                            channel=channel,
                            bitrate=bitrate)
    customLogger.debug("Temperature CAN sensor started!")
    if period == 0:
        period = 1
    period = abs(round(period))

    print("CONNECTED TO CAN")
    client = MQTTClient("temp-sensor-mqtt-client", transport_protocol=transport_protocol,
                                                        protocol_version=mqtt.MQTTv5,
                                                        mqtt_username=mqtt_username,
                                                        mqtt_pass=mqtt_pass,
                                                        broker_address=broker_address,
                                                        broker_port=broker_port,
                                                        keepalive=period * 3,
                                                        infoLogger=infoLogger,
                                                        errorLogger=errorLogger,
                                                        )
    client.set_on_connect(on_connect_temp_sensor)
    client.set_on_publish(on_publish)
    client.connect()

    listener = CANListener(client)
    notifier = can.Notifier(bus, [listener], timeout=period)

    print("Notifier TEMP started")
    # flag.wait()
    while not flag.is_set():
        time.sleep(period)

    notifier.stop(timeout=5)

def on_publish():
    pass


#TODO same method differed string
def on_connect_temp_sensor(client, userdata, flags, rc, props):
    if rc == 0:
        infoLogger.info("CAN Temperature sensor successfully established connection with MQTT broker!")
        customLogger.debug("CAN Temperature sensor successfully established connection with MQTT broker!")
    else:
        errorLogger.error("CAN Temperature sensor failed to establish connection with MQTT broker!")
        customLogger.critical("CAN Temperature sensor failed to establish connection with MQTT broker!")

def on_connect_load_sensor(client, userdata, flags, rc, props):
    if rc == 0:
        infoLogger.info("CAN Load sensor successfully established connection with MQTT broker!")
        customLogger.debug("CAN Load sensor successfully established connection with MQTT broker!")
    else:
        errorLogger.error("CAN Load sensor failed to establish connection with MQTT broker!")
        customLogger.critical("CAN Load sensor failed to establish connection with MQTT broker!")

def on_connect_fuel_sensor(client, userdata, flags, rc, props):
    if rc == 0:
        infoLogger.info("CAN Fuel sensor successfully established connection with MQTT broker!")
        customLogger.debug("CAN Fuel sensor successfully established connection with MQTT broker!")
    else:
        errorLogger.error("CAN Fuel sensor failed to establish connection with MQTT broker!")
        customLogger.critical("CAN Fuel sensor failed to establish connection with MQTT broker!")


def read_can_load(bus, broker_address, broker_port, mqtt_username, mqtt_pass, flag):

    client = mqtt.Client(client_id="temp-sensor-mqtt-client", transport=transport_protocol, protocol=mqtt.MQTTv5)
    client.username_pw_set(username=mqtt_username, password=mqtt_pass)
    client.on_connect = on_connect_temp_sensor
    client.on_publish = on_publish
    while not client.is_connected():
        try:

            infoLogger.info("CAN Temperature sensor establishing connection with MQTT broker!")
            client.connect(broker_address, port=broker_port, keepalive=2*3) #period
            print("CONNECTED TO MQTT")
            client.loop_start()
            time.sleep(0.2)

        except Exception as e:
            errorLogger.error("CAN Temperature sensor failed to establish connection with MQTT broker!")
            print(e)

    listener = CANListener(client)
    notifier = can.Notifier(bus, [listener])
    print("Notifier LOAD started")
    # flag.wait()
    while not flag.is_set():
        time.sleep(2)

    notifier.stop(timeout=5)


class CANListener (can.Listener):
    def __init__(self, temp_client, load_client, fuel_client):
        if temp_client is not None:
            temp_client.connect()
        self.temp_client = temp_client

        if load_client is not None:
            load_client.connect()
        self.load_client = load_client

        if fuel_client is not None:
            fuel_client.connect()
        self.fuel_client = fuel_client



    def on_message_received(self, msg):

        print("CAN: " + msg.__str__())
        # msg.data is a byte array, need to turn it into a single value

        print(type(msg.data))
        #binary_string = b''.join(msg.data)

        float_value = struct.unpack('<f', msg.data)[0]
        #this is part of CAN transmit ticket
        print(float_value)
        if self.temp_client is not None:
            self.temp_client.try_reconnect()
        if self.load_client is not None:
            self.load_client.try_reconnect()
        if self.fuel_client is not None:
            self.fuel_client.try_reconnect()

        if msg.arbitration_id == "123" and self.temp_client is not None:
            self.temp_client.publish(temp_topic, data_pattern.format("{:.2f}".format(float_value), str(time.strftime(time_format, time.localtime())), celzius), qos=qos)
        elif msg.arbitration_id == "124" and self.load_client is not None:
            self.load_client.publish(load_topic, data_pattern.format("{:.2f}".format(float_value),
                                                                str(time.strftime(time_format, time.localtime())),
                                                                celzius), qos=qos)
        elif msg.arbitration_id == "125" and self.fuel_client is not None:
            self.fuel_client.publish(fuel_topic, data_pattern.format("{:.2f}".format(float_value),
                                                                str(time.strftime(time_format, time.localtime())),
                                                                celzius), qos=qos)