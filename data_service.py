import time
import requests


class Sensor_data:
    def __init__(self, value, time, unit):
        self.value = value
        self.time = time
        self.unit = unit


def handle_temperature_data(data, url, jwt, time_format):
    # data aggregation
    sum = 0.0
    for item in data:
        sum += item.value
    time_value = time.strftime(time_format, time.localtime())
    unit = data[0].unit
    # request payload
    payload = {"value": (sum / len(data)), "time": time_value, "unit": unit}
    print("Aggregated temp data: ", str(payload))
    try:
        post_req = requests.post(url, json=payload, headers={"Authorization": "Bearer " + jwt})
        return (True if post_req.status_code == 200 else False)
    except:
        return False


def handle_load_data(data, url, jwt, time_format):
    # data aggregation
    sum = 0.0
    for item in data:
        sum += item.value
    time_value = time.strftime(time_format, time.localtime())
    unit = data[0].unit
    if sum > 0:
        # request payload
        payload = {"value": sum, "time": time_value, "unit": unit}
        print("Aggregated load data: ", str(payload))
        try:
            post_req = requests.post(url, json=payload, headers={"Authorization": "Bearer " + jwt})
            return (True if post_req.status_code == 200 else False)
        except:
            return False
