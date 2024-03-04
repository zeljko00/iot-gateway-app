"""
mqtt_utils
============
Module that encapsulates logic related to connection and communication to a specified MQTT broker

Classes
---------
    MQTTClient: A class that encapsulates logic related to connection and communication to a specified MQTT broker
"""

import time
import paho.mqtt.client as mqtt


class MQTTClient:
    """
    A class that encapsulates logic related to connection and communication to a specified MQTT broker
            Methods:
                __init__(client_id, transport_protocol, protocol_version, mqtt_username, mqtt_pass, broker_address,
                         broker_port, keepalive, infoLogger, errorLogger, flag, sensor_type):
                    Class constructor for initializing class objects
                set_on_connect(on_connect): Lambda setter for on_connect method of paho.mqtt.client.Client class
                set_on_publish(on_publish): Lambda setter for on_publish method of paho.mqtt.client.Client class
                set_on_subscribe(on_subscribe): Lambda setter for on_subscribe method of paho.mqtt.client.Client class
                set_on_message(on_message): Lambda setter for on_message method of paho.mqtt.client.Client class
                subscribe(topic, qos): Method that subscribes to a passed topic
                connect(): Method that connects to the configured MQTT broker
                try_reconnect(topic, payload, qos): Method that tries to reconnect to the configured MQTT broker
                publish(): Method that publishes a message to the specified topic
                disconnect(): Method that closes the connection to the configured MQTT broker
        """

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
            sensor_type):
        """
            Constructor that initializes an MQTT object.
                Args:
                    client_id: str
                        ID of the client
                    transport_protocol: str
                        Transport protocol that will be used to transmit message with
                    protocol_version: int
                        Version of the specified protocol
                    mqtt_username: str
                        Username
                    mqtt_pass: str
                        Password
                    broker_address: str:
                        MQTT broker address
                    broker_port: int
                        MQTT broker port
                    keepalive: int
                        The length of time that a connection will be maintained for after ping messages stop
                    infoLogger: Logger
                        Information file logger
                    errorLogger: Logger
                        Console error logger
                    flag: multiprocessing.Event
                        Token used for stopping the client.
                    sensor_type: str
                        Specifies the type of data the client will be attributed to
        """
        self.client = mqtt.Client(
            client_id=client_id,
            transport=transport_protocol,
            protocol=protocol_version)
        self.client.username_pw_set(username=mqtt_username, password=mqtt_pass)
        self.broker_address = broker_address
        self.broker_port = broker_port
        self.keepalive = keepalive
        self.infoLogger = infoLogger
        self.errorLogger = errorLogger
        self.flag = flag
        self.sensor_type = sensor_type

    def set_on_connect(self, on_connect):
        """
        Lambda setter for on_connect method of paho.mqtt.client.Client class
        """
        self.client.on_connect = on_connect

    def set_on_publish(self, on_publish):
        """
        Lambda setter for on_publish method of paho.mqtt.client.Client class
        """
        self.client.on_publish = on_publish

    def set_on_message(self, on_message):
        """
        Lambda setter for on_message method of paho.mqtt.client.Client class
        """
        self.client.on_message = on_message

    def set_on_subscribe(self, on_subscribe):
        """
        Lambda setter for on_subscribe method of paho.mqtt.client.Client class
            Args:
                on_subscribe: callable
                    Lambda for subscribing to an MQTT broker topic
        """
        self.client.on_subscribe = on_subscribe

    def subscribe(self, topic, qos):
        """
        Method that subscribes to a passed topic
            Args:
                topic: str
                    Specified topic to subscribe to
                qos: int
                    Quality of Service of the MQTT broker
        """
        self.client.subscribe(topic, qos=qos)

    def connect(self):
        """
        Method that connects to the configured MQTT broker
        """
        while not self.client.is_connected() and not self.flag.is_set():
            try:
                self.infoLogger.info(
                    self.sensor_type + " sensor establishing connection with MQTT broker!")
                self.client.connect(
                    self.broker_address,
                    port=self.broker_port,
                    keepalive=self.keepalive)
                self.client.loop_start()
                time.sleep(0.2)

            except BaseException as e:
                self.errorLogger.error(
                    self.sensor_type + " sensor failed to establish connection with MQTT broker!")

    def try_reconnect(self):
        """
        Method that tries to reconnect to the configured MQTT broker
        """
        while not self.client.is_connected() and not self.flag.is_set():
            self.errorLogger.error(
                self.sensor_type + " sensor lost connection to MQTT broker!")
            self.client.reconnect()
            time.sleep(0.2)

    def publish(self, topic, payload, qos):
        """
        Method that publishes a message to the specified topic
        """
        self.client.publish(topic, payload, qos)

    def disconnect(self):
        """
        Method that closes the connection to the configured MQTT broker
        """
        self.client.loop_stop()
        self.client.disconnect()
