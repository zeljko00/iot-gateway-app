import can
import logging.config
import paho.mqtt.client as mqtt
import logging
import time
import struct

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

transport_protocol="tcp"
qos = 2


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
                                                        errorLogger=errorLogger)
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


def on_connect_temp_sensor(client, userdata, flags, rc, props):
    if rc == 0:
        infoLogger.info("CAN Temperature sensor successfully established connection with MQTT broker!")
        customLogger.debug("CAN Temperature sensor successfully established connection with MQTT broker!")
    else:
        errorLogger.error("CAN Temperature sensor failed to establish connection with MQTT broker!")
        customLogger.critical("CAN Temperature sensor failed to establish connection with MQTT broker!")


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
def read_can_fuel(bus, period, capacity, consumption, efficiency, refill, broker_address, broker_port,mqtt_username, mqtt_pass, flag):
    pass
class CANListener (can.Listener):
    def __init__(self, client):
        self.client = client

    def on_message_received(self, msg):

        #this is part of CAN transmit ticket
        while not self.client.is_connected():
            errorLogger.error("Temperature sensor lost connection to MQTT broker!")
            self.client.reconnect()
            time.sleep(0.2)
        print("CAN: " + msg.__str__())

        # msg.data is a byte array, need to turn it into a single value

        # convert byte array into single float value
        binary_string = b''.join(msg.data)
        float_value = struct.unpack('<f', binary_string)[0]

        self.client.publish(temp_topic, data_pattern.format("{:.2f}".format(float_value), str(time.strftime(time_format, time.localtime())), celzius), qos=qos)
        