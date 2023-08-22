import paho.mqtt.client as mqtt
transport_protocol="tcp"

def on_connect_handle(client, userdata, flags, rc,props):
    print("Connected with result code "+str(rc))



def on_message_handle(client, userdata, message, tmp=None):
    print(" Received message " + str(message.payload)
          + " on topic '" + message.topic
          + "' with QoS " + str(message.qos))

from paho.mqtt.properties import Properties
from paho.mqtt.packettypes import PacketTypes


client = mqtt.Client(client_id="sensor-mqtt-client",
                     transport=transport_protocol,
                     protocol=mqtt.MQTTv5)
client.on_connect=on_connect_handle
client.on_message=on_message_handle
print("Connecting!")
client.connect("localhost",
               port=1883,
               keepalive=60)
client.publish("sensors/temp",payload="vefdfalue")
