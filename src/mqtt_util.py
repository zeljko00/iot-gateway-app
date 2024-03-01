"""Gateway-cloud broker utilities."""
import time
import logging.config
import paho.mqtt.client as mqtt

logging.config.fileConfig('logging.conf')
infoLogger = logging.getLogger('customInfoLogger')
errorLogger = logging.getLogger('customErrorLogger')
customLogger = logging.getLogger('customConsoleLogger')

# 'gcb' stands for gateway-cloud broker

gcb_transport = "tcp"
gcb_protocol = mqtt.MQTTv5
gcb_qos = 2
gcb_keepalive = 8 * 60 * 60
gcb_connection_attempt_interval = 0.2

gcb_temp_topic = "gateway_data/temp"
gcb_load_topic = "gateway_data/load"
gcb_fuel_topic = "gateway_data/fuel"
gcb_stats_topic = "gateway_data/stats"


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
            return MQTTConf(config.get_gateway_cloud_broker_address(),
                            config.get_gateway_cloud_broker_port(),
                            config.get_gateway_cloud_broker_iot_username(),
                            config.get_gateway_cloud_broker_iot_password())
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
    client = mqtt.Client(client_id=client_id, transport=gcb_transport, protocol=gcb_protocol)
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
            client.connect(address, port=port, keepalive=gcb_keepalive)
            client.loop_start()
        except BaseException:
            customLogger.error("Client failed to establish connection with MQTT broker.")
        time.sleep(gcb_connection_attempt_interval)


def gcb_disconnect(client):
    """Disconnect client from gateway-cloud broker.

    Parameters
    ----------
    client: paho.mqtt.client.Client
       Mqtt client.

    """
    client.loop_stop()
    client.disconnect()
