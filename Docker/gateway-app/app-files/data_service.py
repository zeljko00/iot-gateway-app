import time
import requests
import logging.config

logging.config.fileConfig('logging.conf')
errorLogger = logging.getLogger('customErrorLogger')

data_pattern = "[ value={} , time={} , unit={} ]"
http_not_found = 404
http_ok = 200
http_no_content = 204

# aggregating temperature data and forwarding to Cloud service
def handle_temperature_data(data, url, jwt, time_format):
    # data aggregation
    data_sum = 0.0
    for item in data:
        try:
            tokens=item.split(" ")
            data_sum += float(tokens[1].split("=")[1])
        except:
            errorLogger.error("Invalid temperature data format! - "+item)
    time_value = time.strftime(time_format, time.localtime())
    unit="unknown"
    try:
        unit = data[0].split(" ")[6].split("=")[1]
    except:
        errorLogger.error("Invalid temperature data format! - "+data[0])
    # request payload
    payload = {"value": (data_sum / len(data)), "time": time_value, "unit": unit}
    print("Aggregated temp data: ", str(payload))
    try:
        post_req = requests.post(url, json=payload, headers={"Authorization": "Bearer " + jwt})
        if post_req.status_code != http_ok:
            errorLogger.error("Problem with temperature Cloud service! - Http status code: "+ str(post_req.status_code))
        return post_req.status_code
    except:
        errorLogger.error("Temperature Cloud service cant be reached!")
        return http_not_found


# aggregating arm load data and forwarding to Cloud service
def handle_load_data(data, url, jwt, time_format):
    # data aggregation
    data_sum = 0.0
    for item in data:
        try:
            tokens = item.split(" ")
            data_sum += float(tokens[1].split("=")[1])
        except:
            errorLogger.error("Invalid load data format! - "+ item)
    time_value = time.strftime(time_format, time.localtime())
    unit = "unknown"
    try:
        unit = data[0].split(" ")[6].split("=")[1]
    except:
        errorLogger.error("Invalid load data format! - "+data[0])
    # request payload
    payload = {"value": data_sum, "time": time_value, "unit": unit}
    print("Aggregated load data: ", str(payload))
    try:
        post_req = requests.post(url, json=payload, headers={"Authorization": "Bearer " + jwt})
        if post_req.status_code != http_ok:
            errorLogger.error("Problem with arm load Cloud service! - Http status code: " + str(post_req.status_code))
        return post_req.status_code
    except:
        errorLogger.error("Arm load Cloud service cant be reached!")
        return http_not_found


# aggregating fuel level data and forwarding to Cloud service
# return value True means that there was request sent to cloud service
def handle_fuel_data(data, limit, url, jwt, time_format):
    try:
        tokens = data.split(" ")
        value=float(tokens[1].split("=")[1])
        if value<=limit:
            unit = "unknown"
            try:
                unit = tokens[6].split("=")[1]
            except:
                errorLogger.error("Invalid fuel data format! - " + data)
            time_value = time.strftime(time_format, time.localtime())
            # request payload
            payload = {"value": value, "time": time_value, "unit": unit}
            print("Aggregated fuel data: ", str(payload))
            try:
                post_req = requests.post(url, json=payload, headers={"Authorization": "Bearer " + jwt})
                if post_req.status_code != http_ok:
                    errorLogger.error("Problem with fuel Cloud service! - Http status code: " + str(post_req.status_code))
                return post_req.status_code
            except:
                errorLogger.error("Fuel Cloud service cant be reached!")
                return http_not_found
        else:
            # data is handled but is not sent because fuel level is over the limit
            return http_no_content
    except:
        errorLogger.error("Invalid fuel data format! - " + data)
        # data can not be parsed, trying again to parse it and send in next iteration is redundant
        return http_no_content
