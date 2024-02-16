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
    def __init__(self, address, port, username, password):
        self.address = address
        self.port = port
        self.username = username
        self.password = password

    @staticmethod
    def from_app_config(config, broker):
        return MQTTConf(config[broker]["address"],
                        config[broker]["port"],
                        config[broker]["username"],
                        config[broker]["password"])

# These two are the same for now, but can be extended so that we can have different logic for pubs and subs


def gcb_publisher_on_connect(client, userdata, flags, rc, props):
    if rc == 0:
        infoLogger.info("Successfully established connection with MQTT broker!")
    else:
        errorLogger.error("Failed to establish connection with MQTT broker!")


def gcb_subscriber_on_connect(client, userdata, flags, rc, props):
    if rc == 0:
        infoLogger.info("Successfully established connection with MQTT broker!")
    else:
        errorLogger.error("Failed to establish connection with MQTT broker!")


def gcb_on_publish(client, userdata, result):
    pass


def gcb_on_message(client, userdata, message):
    customLogger.debug(f"GATEWAY_CLOUD_BROKER RECEIVED: {str(message.payload.decode('utf-8'))}")


def gcb_init_client(client_id, username, password):
    client = mqtt.Client(client_id=client_id, transport=gcb_transport, protocol=gcb_protocol)
    client.username_pw_set(username=username, password=password)
    return client


def gcb_init_publisher(client_id, username, password):
    client = gcb_init_client(client_id, username, password)
    client.on_connect = gcb_publisher_on_connect
    client.on_publish = gcb_on_publish
    return client


def gcb_init_subscriber(client_id, username, password):
    client = gcb_init_client(client_id, username, password)
    client.on_connect = gcb_subscriber_on_connect
    client.on_message = gcb_on_message
    return client


def gcb_connect(client, address, port):
    while not client.is_connected():
        try:
            client.connect(address, port=port, keepalive=gcb_keepalive)
            client.loop_start()
        except BaseException:
            customLogger.error("Client failed to establish connection with MQTT broker.")
        time.sleep(gcb_connection_attempt_interval)


def gcb_disconnect(client):
    client.loop_stop()
    client.disconnect()

# result = client.publish("Test", "Message from Python")
# status = result[0]
# print(result)
