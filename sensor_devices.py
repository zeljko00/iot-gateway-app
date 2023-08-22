import time
import random
import numpy
import json
import paho.mqtt.client as mqtt
from multiprocessing import Process, Event
import logging.config

logging.config.fileConfig('logging.conf')
infoLogger = logging.getLogger('customInfoLogger')
errorLogger = logging.getLogger('customErrorLogger')

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
max = "max_val"
min = "min_val"
conf_file_path = "sensor_conf.json"
time_format = "%d.%m.%Y.  %H:%M:%S"
celzius = "C"
kg = "kg"
liter = "l"
mqtt_broker="mqtt_broker"
address="address"
port="port"
transport_protocol="tcp"
temp_topic="sensors/temperature"
load_topic="sensors/arm-load"
fuel_topic="sensors/fuel-level"


# period = measuring interval in sec, min_val/max_val = min/max measured value
def measure_temperature_periodically(period, min_val, max_val, broker_address, broker_port, flag):
    print("Temperature sensor conf: interval={}s , min={}˚C , max={}C".format(period, min_val,max_val))
    print("------------------------------------------------------")
    # prevent division by zero
    if period == 0:
        period = 1
    period = abs(round(period))
    # initializing mqtt client
    client = mqtt.Client(client_id="temp-sensor-mqtt-client", transport=transport_protocol, protocol=mqtt.MQTTv5)
    client.connect(broker_address, port=broker_port, keepalive=period*3)
    # provide sensor with data for 7 days
    values_count = round(7 * 24 * 60 * 60 / period)
    data = numpy.random.uniform(min_val, max_val, values_count)
    counter = 0
    # shut down sensor depending on set flag
    while not flag.is_set():
        time.sleep(period)
        # check connection to mqtt broker
        while not client.is_connected():
            errorLogger.error("Temperature sensor lost connection to MQTT broker!")
            client.reconnect()
        try:
            # send data to MQTT broker
            client.publish(temp_topic, str(data[counter % values_count])+"#"+str(time.strftime(time_format, time.localtime()))+"#"+celzius)
        except:
            errorLogger.error("Temperature sensor can't connect to MQTT broker!")
        counter += 1
    client.disconnect()
    print("Temperature sensor shutdown!")


# min_t/max_t = min/max measuring period in sec, min_val/max_val = min/max measured value
def measure_load_randomly(min_t, max_t, min_val, max_val, broker_address, broker_port, flag):
    print("Arm sensor conf: min_interval={}s , max_interval={}s , min={}kg , max={}kg".format(min_t, max_t, min_val, max_val))
    print("------------------------------------------------------")
    # parameter validation
    if max_t <= min_t:
        max_t = min_t + random.randint(10)
    min_t = abs(round(min_t))
    max_t = abs(round(max_t))
    # initializing mqtt client
    client = mqtt.Client(client_id="arm-load-sensor-mqtt-client", transport=transport_protocol, protocol=mqtt.MQTTv5)
    client.connect(broker_address, port=broker_port, keepalive=max_t*3)
    # provide sensor with data for at least 7 days
    values_count = round(7 * 24 * 60 * 60 / min_t)
    intervals = numpy.random.uniform(min_t, max_t, values_count)
    data = numpy.random.uniform(min_val, max_val, values_count)
    counter = 0
    # shut down sensor depending on set flag
    while not flag.is_set():
        time.sleep(round(intervals[counter % values_count]))
        # check connection to mqtt broker
        while not client.is_connected():
            errorLogger.error("Arm load sensor lost connection to MQTT broker!")
            client.reconnect()
        try:
            # send data to MQTT broker
            client.publish(load_topic, str(data[counter % values_count])+"#"+str(time.strftime(time_format, time.localtime()))+"#"+kg)
        except:
            errorLogger.error("Arm load sensor can't connect to MQTT broker!")
        counter += 1
    client.disconnect()
    print("Arm load sensor shutdown!")


# period = measuring interval , capacity = fuel tank capacity , refill = fuel tank refill probability (0-1)
# consumption = fuel usage consumption per working hour, efficiency = machine work efficiency (0-1)
def measure_fuel_periodically(period, capacity, consumption, efficiency, refill, broker_address, broker_port, flag):
    print("Fuel sensor conf: period={}s , capacity={}l , consumption={}l/h , efficiency={} , refill={}".
          format(period, capacity, consumption, efficiency, refill))
    print("------------------------------------------------------")
    # parameter validation
    if period == 0:
        period = 1
    period = abs(round(period))
    # initializing mqtt client
    client = mqtt.Client(client_id="fuel-sensor-mqtt-client", transport=transport_protocol, protocol=mqtt.MQTTv5)
    client.connect(broker_address, port=broker_port, keepalive=period*3)
    # at first fuel tank is randomly filled
    value = random.randint(round(capacity / 2), round(capacity))
    # constant for scaling consumption per hour to per second
    scale = 1 / (60 * 60)
    # shut down sensor depending on set flag
    refilling = False
    while not flag.is_set():
        time.sleep(period)
        # fuel tank is filling
        if refilling:
            value = random.randint(round(value), round(capacity))
            refilling = False
        else:
            # deciding whether fuel tank should be refilled based on refill probability
            refilling = random.random() < refill
            # amount of consumed fuel is determined based on fuel consumption, time elapsed
            # from previous measuring and machine state (on/of)
            consumed = period * consumption * scale * (1 + 1 - efficiency)
            value -= consumed;
            if value <= 0:
                value = 0
                refilling = True
        # check connection to mqtt broker
        while not client.is_connected():
            errorLogger.error("Fuel level sensor lost connection to MQTT broker!")
            client.reconnect()
        try:
            # send data to MQTT broker
            client.publish(fuel_topic,
                           str(value) + "#" + str(time.strftime(time_format, time.localtime())) + "#" + liter)
        except:
            errorLogger.error("Fuel level sensor can't connect to MQTT broker!")
    client.disconnect()
    print("Fuel level sensor shutdown!")


# read sensor conf data
def read_conf():
    data = None
    try:
        conf_file = open(conf_file_path)
        data = json.load(conf_file)
    except:
        errorLogger.critical("Using default config! Can't read sensor config file - ", conf_file_path, " !")
        data = {temp_sensor: {interval: 5, min: -10, max: 100},
                arm_sensor: {arm_min_t: 10, arm_max_t: 100, min: 0, max: 800},
                fuel_sensor: {interval: 5, fuel_capacity: 300, fuel_consumption: 3000, fuel_efficiency: 0.6,
                              fuel_refill: 0.02},
                mqtt_broker: { address: "localhost", port:1883}}
    finally:
        print("Sensors config:")
        print(data)
        print("------------------------------------------------------")
        return data


# creating sensor processes
def sensors_devices(temp_flag, load_flag, fuel_flag):
    conf_data = read_conf()
    temperature_sensor = Process(target=measure_temperature_periodically, args=(conf_data[temp_sensor][interval],
                                                                                conf_data[temp_sensor][min],
                                                                                conf_data[temp_sensor][max],
                                                                                conf_data[mqtt_broker][address],
                                                                                conf_data[mqtt_broker][port],
                                                                                temp_flag, ))
    excavator_arm_sensor = Process(target=measure_load_randomly, args=(conf_data[arm_sensor][arm_min_t],
                                                                         conf_data[arm_sensor][arm_max_t],
                                                                         conf_data[arm_sensor][min],
                                                                         conf_data[arm_sensor][max],
                                                                         conf_data[mqtt_broker][address],
                                                                         conf_data[mqtt_broker][port],
                                                                         load_flag,))
    fuel_level_sensor = Process(target=measure_fuel_periodically, args=(conf_data[fuel_sensor][interval],
                                                                        conf_data[fuel_sensor][fuel_capacity],
                                                                        conf_data[fuel_sensor][fuel_consumption],
                                                                        conf_data[fuel_sensor][fuel_efficiency],
                                                                        conf_data[fuel_sensor][fuel_refill],
                                                                        conf_data[mqtt_broker][address],
                                                                        conf_data[mqtt_broker][port],
                                                                        fuel_flag,))
    return [temperature_sensor, excavator_arm_sensor, fuel_level_sensor]


def main():
    temp_flag = Event()
    load_flag = Event()
    fuel_flag = Event()
    sensors = sensors_devices(temp_flag, load_flag, fuel_flag)
    infoLogger.info("Sensor system started!")
    for sensor in sensors:
        sensor.start()
        time.sleep(0.1)
    # waiting for shutdown signal
    input("Press ENTER to stop the app!")
    infoLogger.info("Sensor system shutting down! Please wait")
    # shutting down sensor processes
    temp_flag.set()
    load_flag.set()
    fuel_flag.set()
    for sensor in sensors:
        sensor.join()
    infoLogger.info("Sensor system shutdown!")

if __name__ == '__main__':
    main()


