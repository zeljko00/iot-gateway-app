import time
import random
import numpy
import json
from multiprocessing import Process

temp_sensor="temp_sensor"
arm_sensor="arm_sensor"
arm_min_t="min_t"
arm_max_t="max_t"
fuel_sensor= "fuel_sensor"
fuel_consumption="consumption"
fuel_capacity="capacity"
fuel_efficiency="efficiency"
fuel_refill="refill"
interval="period"
max="max_val"
min="min_val"
conf_file_path="sensor_conf.json"
class Sensor_data:
    def __init__(self, data, time):
        self.data = data
        self.time = time


# class SensorConfData:
#     def __init__(self):
# period = measuring interval in sec, min_val/max_val = min/max measured value
def measure_temperature_periodically(period, min_val, max_val):
    print("Temperature sensor conf: interval={}s , min={}˚C , max={}C".format(period, min_val,max_val))
    print("------------------------------------------------------")
    # prevent division by zero
    if period == 0:
        period = 1
    period = abs(round(period))
    # provide sensor with data for 7 days
    values_count = round(7 * 24 * 60 * 60 / period)
    data = numpy.random.uniform(min_val, max_val, values_count)
    counter = 0
    # shut down sensor?
    while True:
        time.sleep(period)
        # create object representing data
        measured_value = Sensor_data(data[counter % values_count],
                                    time.strftime("%d.%m.%Y.  %H:%M:%S", time.localtime()))
        # send data to iot gateway
        print("Engine temperature: {:.2f}^C  ---  {}".format(measured_value.data, measured_value.time))
        counter += 1


# min_t/max_t = min/max measuring period in sec, min_val/max_val = min/max measured value
def measure_weight_randomly(min_t, max_t, min_val, max_val):
    print("Arm sensor conf: min_interval={}s , max_interval={}s , min={}kg , max={}kg".format(min_t, max_t, min_val, max_val))
    print("------------------------------------------------------")
    # parameter validation
    if max_t <= min_t:
        max_t = min_t + random.randint(10)
    min_t = abs(round(min_t))
    max_t = abs(round(max_t))
    # provide sensor with data for at least 7 days
    values_count = round(7 * 24 * 60 * 60 / min_t)
    intervals = numpy.random.uniform(min_t, max_t, values_count)
    data = numpy.random.uniform(min_val, max_val, values_count)
    counter = 0
    # shut down sensor?
    while True:
        time.sleep(round(intervals[counter % values_count]))
        # create object representing data
        measured_value = Sensor_data(data[counter % values_count],
                                    time.strftime("%d.%m.%Y.  %H:%M:%S", time.localtime()))
        # send data to iot gateway
        print("Load weight: {:.2f}kg  ---  {}".format(measured_value.data, measured_value.time))
        counter += 1


# period = measuring interval , capacity = fuel tank capacity , refill = fuel tank refill probability (0-1)
# consumption = fuel usage consumption per working hour, efficiency = machine work efficiency (0-1)
def measure_fuel_periodically(period, capacity, consumption, efficiency, refill):
    print("Fuel sensor conf: period={}s , capacity={}l , consumption={}l/h , efficiency={} , refill={}".format(period,capacity,consumption,efficiency,refill))
    print("------------------------------------------------------")
    # parameter validation
    if period == 0:
        period = 1
    period = abs(round(period))

    # at first fuel tank is randomly filled
    value = random.randint(round(capacity / 2), round(capacity))
    # constant for scaling consumption per hour to per second
    scale = 1 / (60 * 60)
    # shut down sensor?
    refilling = False
    while True:
        time.sleep(period)
        # fuel tank is filling
        if refilling:
            value = capacity
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
        # create object representing data
        measured_value = Sensor_data(value, time.strftime("%d.%m.%Y.  %H:%M:%S", time.localtime()))
        # send data to iot gateway
        print("Fuel level: {:.2f}l  ---  {}".format(measured_value.data, measured_value.time))


# read sensor conf data
def read_conf():
    data = None
    try:
        conf_file = open(conf_file_path)
        data = json.load(conf_file)
        print("Conf file read!")
    except:
        data = {temp_sensor: {interval: 5, min: -10, max: 100},
                arm_sensor: {arm_min_t: 10, arm_max_t: 100, min: 0, max: 800},
                fuel_sensor: {interval: 5, fuel_capacity: 300, fuel_consumption: 3000, fuel_efficiency: 0.6, fuel_refill: 0.02}}
    finally:
        print(data)
        print("------------------------------------------------------")
        return data


# creating sensor processes
def sensors_devices():
    conf_data=read_conf()
    temperature_sensor = Process(target=measure_temperature_periodically, args=(conf_data[temp_sensor][interval], conf_data[temp_sensor][min], conf_data[temp_sensor][max]))
    excavator_arm_sensor = Process(target=measure_weight_randomly, args=(conf_data[arm_sensor][arm_min_t], conf_data[arm_sensor][arm_max_t], conf_data[arm_sensor][min], conf_data[arm_sensor][max]))
    fuel_level_sensor = Process(target=measure_fuel_periodically, args=(conf_data[fuel_sensor][interval], conf_data[fuel_sensor][fuel_capacity], conf_data[fuel_sensor][fuel_consumption], conf_data[fuel_sensor][fuel_efficiency], conf_data[fuel_sensor][fuel_refill]))
    return [temperature_sensor, excavator_arm_sensor, fuel_level_sensor]


def main():
    for sensor in sensors_devices():
        sensor.start()


if __name__ == '__main__':
    main()
