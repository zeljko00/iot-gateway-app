import time

import paho.mqtt.client as mqtt


class MQTTClient:
    def __init__(
            self,
            client_id,
            transport_protocol,
            protocol_version,
            mqtt_username,
            mqtt_pass,
            broker_address,
            broker_port,
            keepalive,
            infoLogger,
            errorLogger,
            flag,
            sensor_type,
            bus):
        self.client = mqtt.Client(client_id=client_id, transport=transport_protocol, protocol=protocol_version)
        self.client.username_pw_set(username=mqtt_username, password=mqtt_pass)
        self.broker_address = broker_address
        self.broker_port = broker_port
        self.keepalive = keepalive
        self.infoLogger = infoLogger
        self.errorLogger = errorLogger
        self.flag = flag
        self.sensor_type = sensor_type
        self.bus = bus

    def set_on_connect(self, connect):
        self.client.on_connect = connect

    def set_on_publish(self, publish):
        self.client.on_publish = publish

    def set_on_message(self, on_message):
        self.client.on_message = on_message

    def set_on_subscribe(self, on_subscribe):
        self.client.on_subscribe = on_subscribe

    def subscribe(self, topic, qos):
        self.client.subscribe(topic, qos=qos)

    def get_bus(self):
        return self.bus

    def connect(self):
        while not self.client.is_connected() and not self.flag.is_set():
            try:
<<<<<<< HEAD
                self.infoLogger.info(self.sensor_type + " sensor establishing connection with MQTT broker!") #TODO alarm vs sensor
=======
                # TODO alarm vs sensor
                self.infoLogger.info(self.sensor_type + " sensor establishing connection with MQTT broker!")
                print(self.broker_address, self.broker_port)
>>>>>>> 632971ce596b0142eebd14c65c26138b194a9d0c
                self.client.connect(self.broker_address, port=self.broker_port, keepalive=self.keepalive)
                self.client.loop_start()
                time.sleep(0.2)

            except Exception as e:
                self.errorLogger.error(self.sensor_type + " sensor failed to establish connection with MQTT broker!")
                print(e)

    def try_reconnect(self):
        while not self.client.is_connected() and not self.flag.is_set():
            self.errorLogger.error(self.sensor_type + " sensor lost connection to MQTT broker!")
            self.client.reconnect()
            time.sleep(0.2)

    def publish(self, topic, payload, qos):
        self.client.publish(topic, payload, qos)

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
