import time
import requests


# aggregating temperature data and forwarding to Cloud service
def handle_temperature_data(data, url, jwt, time_format):
    # data aggregation
    data_sum = 0.0
    for item in data:
        data_sum += item.value
    time_value = time.strftime(time_format, time.localtime())
    unit = data[0].unit
    # request payload
    payload = {"value": (data_sum / len(data)), "time": time_value, "unit": unit}
    print("Aggregated temp data: ", str(payload))
    try:
        post_req = requests.post(url, json=payload, headers={"Authorization": "Bearer " + jwt})
        if post_req.status_code == 200:
            return True
        else:
            return False
    except:
        return False


# aggregating arm load data and forwarding to Cloud service
def handle_load_data(data, url, jwt, time_format):
    # data aggregation
    data_sum = 0.0
    for item in data:
        data_sum += item.value
    time_value = time.strftime(time_format, time.localtime())
    unit = data[0].unit
    if data_sum > 0:
        # request payload
        payload = {"value": data_sum, "time": time_value, "unit": unit}
        print("Aggregated load data: ", str(payload))
        try:
            post_req = requests.post(url, json=payload, headers={"Authorization": "Bearer " + jwt})
            if post_req.status_code == 200:
                return True
            else:
                return False
        except:
            return False

