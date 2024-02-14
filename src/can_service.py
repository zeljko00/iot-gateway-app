import json

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

conf_file_path = "configuration/sensor_conf.json"
app_conf_file_path = "configuration/app_conf.json"

transport_protocol="tcp"
temp_topic="sensors/temperature"
load_topic="sensors/arm-load"
fuel_topic="sensors/fuel-level"

data_pattern ="[ value={} , time={} , unit={} ]"
time_format = "%d.%m.%Y %H:%M:%S"
celzius = "C"
kg = "kg"
l = "l"

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
temp_alarm_topic = "alarms/temperature"
load_alarm_topic = "alarms/load"
fuel_alarm_topic = "alarms/fuel"


def read_can(interface, channel, bitrate, is_can_temp, is_can_load, is_can_fuel, conf_data, flag, config_flag, init_flags, can_lock):

    customLogger.debug("CAN process started!")

    period = 2

    initial = True
    notifier = None
    temp_client = None
    load_client = None
    fuel_client = None
    while not flag.is_set():  # TODO wait
        if config_flag.is_set() or initial:
            conf_data = read_app_conf()
            bus = can.interface.Bus(interface=interface,
                                    channel=channel,
                                    bitrate=bitrate)
            temp_client, load_client, fuel_client = init_mqtt_clients(bus, is_can_temp, is_can_load, is_can_fuel,
                                                                      conf_data, flag)
            notifier = can.Notifier(bus, [], timeout=period)
            can_listener = CANListener(temp_client, load_client, fuel_client)
            notifier.add_listener(can_listener)
            initial = False
            config_flag.clear()  # TODO

        time.sleep(period)

    can_lock.acquire()
    init_flags.can_flag = False  # TODO suss
    can_lock.release()

    notifier.stop(timeout=5)
    if temp_client is not None:
        temp_client.disconnect()
    if load_client is not None:
        load_client.disconnect()
    if fuel_client is not None:
        fuel_client.disconnect()
    # TODO on_disconnect


def init_mqtt_clients(bus, is_can_temp, is_can_load, is_can_fuel, conf_data, flag):
    temp_client = None
    load_client = None
    fuel_client = None

    if is_can_temp:
        temp_client = MQTTClient("temp-can-sensor-mqtt-client", transport_protocol=transport_protocol,
                                 protocol_version=mqtt.MQTTv5,
                                 mqtt_username=conf_data[mqtt_broker][mqtt_user],
                                 mqtt_pass=conf_data[mqtt_broker][mqtt_password],
                                 broker_address=conf_data[mqtt_broker][address],
                                 broker_port=conf_data[mqtt_broker][port],
                                 keepalive=2 * 3,
                                 infoLogger=infoLogger,
                                 errorLogger=errorLogger,
                                 flag=flag,
                                 sensor_type="TEMP",
                                 bus=bus)

        def on_message_temp_alarm(client, userdata, msg):
            can_message = can.Message(arbitration_id=0x120,
                                      data=[bool(msg.payload)],  # TODO if anything else is sent instead of True/False
                                      is_extended_id=False,
                                      is_remote_frame=False)
            bus.send(msg=can_message, timeout=5)
            customLogger.info("Temperature alarm registered! Forwarding to CAN!")

        temp_client.set_on_connect(on_connect_temp_sensor)
        temp_client.set_on_publish(on_publish)
        temp_client.set_on_subscribe(on_subscribe_temp_alarm)
        temp_client.set_on_message(on_message_temp_alarm)
        temp_client.connect()

    if is_can_load:
        load_client = MQTTClient("load-can-sensor-mqtt-client", transport_protocol=transport_protocol,
                                 protocol_version=mqtt.MQTTv5,
                                 mqtt_username=conf_data[mqtt_broker][mqtt_user],
                                 mqtt_pass=conf_data[mqtt_broker][mqtt_password],
                                 broker_address=conf_data[mqtt_broker][address],
                                 broker_port=conf_data[mqtt_broker][port],
                                 keepalive=2 * 3,
                                 infoLogger=infoLogger,
                                 errorLogger=errorLogger,
                                 flag=flag,
                                 sensor_type="LOAD",
                                 bus=bus)

        def on_message_load_alarm(client, userdata, msg):
            can_message = can.Message(arbitration_id=0x121,
                                      data=[bool(msg.payload)],  # TODO if anything else is sent instead of True/False
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
        fuel_client = MQTTClient("fuel-can-sensor-mqtt-client", transport_protocol=transport_protocol,
                                 protocol_version=mqtt.MQTTv5,
                                 mqtt_username=conf_data[mqtt_broker][mqtt_user],
                                 mqtt_pass=conf_data[mqtt_broker][mqtt_password],
                                 broker_address=conf_data[mqtt_broker][address],
                                 broker_port=conf_data[mqtt_broker][port],
                                 keepalive=2 * 3,
                                 infoLogger=infoLogger,
                                 errorLogger=errorLogger,
                                 flag=flag,
                                 sensor_type="FUEL",
                                 bus=bus)

        def on_message_fuel_alarm(client, userdata, msg):
            can_message = can.Message(arbitration_id=0x122,
                                      data=[bool(msg.payload)],  # TODO if anything else is sent instead of True/False
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


def read_app_conf():
    data = None
    try:
        conf_file = open(app_conf_file_path)
        data = json.load(conf_file)
    except:
        errorLogger.critical("Using default config! Can't read app config file - ", app_conf_file_path, " !")
        customLogger.critical("Using default config! Can't read app config file - ", app_conf_file_path, " !")

        data = {fuel_settings: {"fuel_level_limit": 200, mode: "SIMULATOR"},
                temp_settings: {"temp_interval": 20, mode: "SIMULATOR"},
                load_settings: {"load_interval": 20, mode: "SIMULATOR"}, }
    return data


def on_publish(topic, payload, qos):
    pass


def on_subscribe_temp_alarm(client, userdata, flags, rc, props):
    if rc == 0:
        infoLogger.info("CAN Temperature alarm client successfully established connection with MQTT broker!")
        customLogger.debug("CAN Temperature alarm client successfully established connection with MQTT broker!")
    else:
        errorLogger.error("CAN Temperature alarm client failed to establish connection with MQTT broker!")
        customLogger.critical("CAN Temperature alarm client failed to establish connection with MQTT broker!")


def on_subscribe_load_alarm(client, userdata, flags, rc, props):
    if rc == 0:
        infoLogger.info("CAN Load alarm client successfully established connection with MQTT broker!")
        customLogger.debug("CAN Load alarm client successfully established connection with MQTT broker!")
    else:
        errorLogger.error("CAN Load alarm client failed to establish connection with MQTT broker!")
        customLogger.critical("CAN Load alarm client failed to establish connection with MQTT broker!")


def on_subscribe_fuel_alarm(client, userdata, flags, rc, props):
    if rc == 0:
        infoLogger.info("CAN Load alarm client successfully established connection with MQTT broker!")
        customLogger.debug("CAN Load alarm client successfully established connection with MQTT broker!")
        client.subscribe(fuel_alarm_topic, qos=qos)
    else:
        errorLogger.error("CAN Load alarm client failed to establish connection with MQTT broker!")
        customLogger.critical("CAN Load alarm client failed to establish connection with MQTT broker!")


#TODO same method differed string
def on_connect_temp_sensor(client, userdata, flags, rc, props):
    if rc == 0:
        infoLogger.info("CAN Temperature sensor successfully established connection with MQTT broker!")
        customLogger.debug("CAN Temperature sensor successfully established connection with MQTT broker!")
        client.subscribe(temp_alarm_topic, qos=qos)
    else:
        errorLogger.error("CAN Temperature sensor failed to establish connection with MQTT broker!")
        customLogger.critical("CAN Temperature sensor failed to establish connection with MQTT broker!")


def on_connect_load_sensor(client, userdata, flags, rc, props):
    if rc == 0:
        infoLogger.info("CAN Load sensor successfully established connection with MQTT broker!")
        customLogger.debug("CAN Load sensor successfully established connection with MQTT broker!")
        client.subscribe(load_alarm_topic, qos=qos)
    else:
        errorLogger.error("CAN Load sensor failed to establish connection with MQTT broker!")
        customLogger.critical("CAN Load sensor failed to establish connection with MQTT broker!")


def on_connect_fuel_sensor(client, userdata, flags, rc, props):
    if rc == 0:
        infoLogger.info("CAN Fuel sensor successfully established connection with MQTT broker!")
        customLogger.debug("CAN Fuel sensor successfully established connection with MQTT broker!")
        client.subscribe(fuel_alarm_topic, qos=qos)
    else:
        errorLogger.error("CAN Fuel sensor failed to establish connection with MQTT broker!")
        customLogger.critical("CAN Fuel sensor failed to establish connection with MQTT broker!")


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

    def set_temp_client(self, client):
        if client is None:
            if self.temp_client is not None:
                self.temp_client.disconnect()
        self.temp_client = client

    def set_load_client(self, client):
        if client is None:
            if self.temp_client is not None:
                self.temp_client.disconnect()
        self.load_client = client

    def set_fuel_client(self, client):
        if client is None:
            if self.temp_client is not None:
                self.temp_client.disconnect()
        self.fuel_client = client

    def on_message_received(self, msg):
        # msg.data is a byte array, need to turn it into a single value

        float_value = struct.unpack('d', msg.data)[0]

        # this is part of CAN transmit ticket

        if self.temp_client is not None:
            self.temp_client.try_reconnect()
        if self.load_client is not None:
            self.load_client.try_reconnect()
        if self.fuel_client is not None:
            self.fuel_client.try_reconnect()
        try:
            if hex(msg.arbitration_id) == "0x123" and self.temp_client is not None:
                self.temp_client.publish(temp_topic, data_pattern.format("{:.2f}".format(float_value), str(time.strftime(time_format, time.localtime())), celzius), qos)
                customLogger.info("Temperature: " + data_pattern.format("{:.2f}".format(float_value),
                                                                 str(time.strftime(time_format, time.localtime())), celzius))
            elif hex(msg.arbitration_id) == "0x124" and self.load_client is not None:
                self.load_client.publish(load_topic, data_pattern.format("{:.2f}".format(float_value),
                                                                    str(time.strftime(time_format, time.localtime())),
                                                                    celzius), qos)
                customLogger.info("Load: " + data_pattern.format("{:.2f}".format(float_value),
                                                                        str(time.strftime(time_format, time.localtime())),
                                                                        kg))
            elif hex(msg.arbitration_id) == "0x125" and self.fuel_client is not None:
                self.fuel_client.publish(fuel_topic, data_pattern.format("{:.2f}".format(float_value),
                                                                    str(time.strftime(time_format, time.localtime())),
                                                                    celzius), qos)
                customLogger.info("Fuel: " + data_pattern.format("{:.2f}".format(float_value),
                                                                        str(time.strftime(time_format, time.localtime())),
                                                                         l))
        except:
            errorLogger.error("Error has occurred while sending data to gateway. Check the MQTT clients!")
