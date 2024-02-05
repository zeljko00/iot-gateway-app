import time

import paho.mqtt.client as mqtt


class MQTTClient:
    def __init__(self, client_id, transport_protocol, protocol_version, mqtt_username, mqtt_pass, broker_address, broker_port, keepalive, infoLogger, errorLogger, flag, sensor_type):
        self.client = mqtt.Client(client_id=client_id, transport=transport_protocol, protocol=protocol_version)
        self.client.username_pw_set(username=mqtt_username, password=mqtt_pass)
        self.broker_address = broker_address
        self.broker_port = broker_port
        self.keepalive = keepalive
        self.infoLogger = infoLogger
        self.errorLogger = errorLogger
        self.flag = flag
        self.sensor_type = sensor_type

    def set_on_connect(self, connect):
        self.client.on_connect = connect

    def set_on_publish(self, publish):
        self.client.on_publish = publish

    def connect(self):
        while not self.client.is_connected() and not self.flag.is_set():
            try:

                self.infoLogger.info("CAN " + self.sensor_type + " sensor establishing connection with MQTT broker!")
                self.client.connect(self.broker_address, port=self.broker_port, keepalive=self.keepalive)
                print("CONNECTED TO MQTT")
                self.client.loop_start()
                time.sleep(0.2)

            except Exception as e:
                self.errorLogger.error("CAN " + self.sensor_type + " sensor failed to establish connection with MQTT broker!")
                print(e)

    def try_reconnect(self):
        while not self.client.is_connected() and not self.flag.is_set():
            self.errorLogger.error(self.sensor_type + " sensor lost connection to MQTT broker!")
            self.client.reconnect()
            time.sleep(0.2)

    def publish(self, topic, payload, qos):
        self.client.publish(topic, payload, qos)
