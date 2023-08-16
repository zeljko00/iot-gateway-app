import time
import requests
import logging.config

logging.config.fileConfig('logging.conf')
errorLogger = logging.getLogger('customErrorLogger')


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
            errorLogger.error("Problem with temperature Cloud service! - Http status code: ", post_req.status_code)
            return False
    except:
        errorLogger.error("Temperature Cloud service cant be reached!")
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
                errorLogger.error("Problem with arm load Cloud service! - Http status code: ", post_req.status_code)
                return False
        except:
            errorLogger.error("Arm load Cloud service cant be reached!")
            return False

