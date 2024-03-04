"""Mqtt utilities.

mqtt_util
=========
Module that contains logic for gateway-cloud communication via mqtt broker.
'gcb' prefix stands for gateway-cloud broker.

Classes
-------

MqttConf
    Wrapper for mqtt configuration that includes address, port, username and password.

Functions
---------

gcb_publisher_on_connect
    Connection event handler for publisher.
gcb_subscriber_on_connect
    Connection event handler for subscriber.
gcb_on_publish
    Publish event handler.
gcb_on_message
    Message event handler.
gcb_init_client
    Create client.
gcb_init_publisher
    Create publisher client.
gcb_init_subscriber
    Create subscriber client.
gcb_connect
    Connect mqtt client to specified broker.
gcb_disconnect
    Disconnect mqtt client from specified broker.

Constants
---------
GCB_TRANSPORT
    Transport layer protocol used by mqtt client.
GCB_PROTOCOL
    Mqtt protocol version.
GCB_QOS
    Mqtt quality of service level.
GCB_KEEPALIVE
    Mqtt keepalive period.
GCB_CONNECTION_ATTEMPT_INTERVAL
    Mqtt interval for retrying connection.

GCB_TEMP_TOPIC
    Temp topic identifier.
GCB_LOAD_TOPIC
    Load topic identifier.
GCB_FUEL_TOPIC
    Fuel topic identifier.
GCB_STATS_TOPIC
    Stats topic identifier.

"""
import time
import logging.config
import paho.mqtt.client as mqtt

logging.config.fileConfig('logging.conf')
infoLogger = logging.getLogger('customInfoLogger')
errorLogger = logging.getLogger('customErrorLogger')
customLogger = logging.getLogger('customConsoleLogger')

GCB_TRANSPORT = "tcp"
GCB_PROTOCOL = mqtt.MQTTv5
GCB_QOS = 2
GCB_KEEPALIVE = 8 * 60 * 60
GCB_CONNECTION_ATTEMPT_INTERVAL = 0.2

GCB_TEMP_TOPIC = "gateway_data/temp"
GCB_LOAD_TOPIC = "gateway_data/load"
GCB_FUEL_TOPIC = "gateway_data/fuel"
GCB_STATS_TOPIC = "gateway_data/stats"


class MQTTConf:
    """Class representing higher level mqtt configuration.

    Attributes
    ----------
    address: str
       Mqtt broker address.
    port: int
       Mqtt broker port.
    username: str
       Mqtt broker username.
    password: str
       Mqtt broker password.

    """

    def __init__(self, address, port, username, password):
        """Create higher level mqtt configuration.

        Parameters
        ----------
        address: str
           Mqtt broker address.
        port: int
           Mqtt broker port.
        username: str
           Mqtt broker username.
        password: str
           Mqtt broker password.
        """
        self.address = address
        self.port = port
        self.username = username
        self.password = password

    @staticmethod
    def from_app_config(config, broker):
        """Get higher level mqtt configuration from gateway configuration.

        Parameters
        ----------
        config: dict
           Configuration to extract from.
        broker: str
           Which broker information to extract.

        Returns
        -------
        mqtt_conf: MQTTConf
           Higher level mqtt configuration or None.

        """
        if broker == "gateway_cloud_broker":
            return MQTTConf(config.gateway_cloud_broker_address,
                            config.gateway_cloud_broker_port,
                            config.gateway_cloud_broker_iot_username,
                            config.gateway_cloud_broker_iot_password)
        return None


def gcb_publisher_on_connect(client, userdata, flags, rc, props):
    """Gateway-cloud published on connect handler.

    Parameters
    ----------
    client: paho.mqtt.client.Client
    userdata
    flags
    rc
    props

    """
    if rc == 0:
        infoLogger.info("Successfully established connection with MQTT broker!")
    else:
        errorLogger.error("Failed to establish connection with MQTT broker!")


def gcb_subscriber_on_connect(client, userdata, flags, rc, props):
    """Gateway-cloud subscriber on connect handler.

    Parameters
    ----------
    client: paho.mqtt.client.Client
    userdata
    flags
    rc
    props

    """
    if rc == 0:
        infoLogger.info("Successfully established connection with MQTT broker!")
    else:
        errorLogger.error("Failed to establish connection with MQTT broker!")


def gcb_on_publish(client, userdata, result):
    """Gateway-cloud publisher on publish handler.

    Parameters
    ----------
    client: paho.mqtt.client.Client
    userdata
    result

    """
    pass


def gcb_on_message(client, userdata, message):
    """Gateway-cloud broker on message handler.

    This function is used for testing whether gateway-cloud broker receives information.

    Parameters
    ----------
    client: paho.mqtt.client.Client
    userdata
    message

    """
    customLogger.debug(f"GATEWAY_CLOUD_BROKER RECEIVED: {str(message.payload.decode('utf-8'))}")


def gcb_init_client(client_id, username, password):
    """Initialize gateway-cloud broker client.

    This function is not intended to be used directly. Instead, it is implicitly called
    when publisher or subscriber are created.

    Parameters
    ----------
    client_id: str
       Mqtt client identifier.
    username: str
       Gateway-cloud broker username.
    password: str
       Gateway-cloud broker password.

    Returns
    -------
    client: paho.mqtt.client.Client
       Created client for gateway-cloud broker.

    """
    client = mqtt.Client(client_id=client_id, transport=GCB_TRANSPORT, protocol=GCB_PROTOCOL)
    client.username_pw_set(username=username, password=password)
    return client


def gcb_init_publisher(client_id, username, password):
    """Initialize gateway-cloud broker publisher.

    Parameters
    ----------
    client_id: str
       Mqtt client identifier.
    username: str
       Gateway-cloud broker username.
    password
       Gateway-cloud broker password

    Returns
    -------
    client: paho.mqtt.client.Client
       Created publisher for gateway-cloud broker.

    """
    client = gcb_init_client(client_id, username, password)
    client.on_connect = gcb_publisher_on_connect
    client.on_publish = gcb_on_publish
    return client


def gcb_init_subscriber(client_id, username, password):
    """Initialize gateway-cloud broker subscriber.

    Parameters
    ----------
    client_id: str
       Mqtt client identifier.
    username: str
       Gateway-cloud broker username.
    password
       Gateway-cloud broker password

    Returns
    -------
    client: paho.mqtt.client.Client
       Created subscriber for gateway-cloud broker.

    """
    client = gcb_init_client(client_id, username, password)
    client.on_connect = gcb_subscriber_on_connect
    client.on_message = gcb_on_message
    return client


def gcb_connect(client, address, port):
    """Connect client to gateway-cloud broker.

    Parameters
    ----------
    client: paho.mqtt.client.Client
       Mqtt client.
    address: str
       Gateway-cloud address.
    port: int
       Gateway-cloud port.

    """
    while not client.is_connected():
        try:
            client.connect(address, port=port, keepalive=GCB_KEEPALIVE)
            client.loop_start()
        except BaseException:
            customLogger.error("Client failed to establish connection with MQTT broker.")
        time.sleep(GCB_CONNECTION_ATTEMPT_INTERVAL)


def gcb_disconnect(client):
    """Disconnect client from gateway-cloud broker.

    Parameters
    ----------
    client: paho.mqtt.client.Client
       Mqtt client.

    """
    client.loop_stop()
    client.disconnect()
