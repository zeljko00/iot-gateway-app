import json
import auth
import time
import logging.config
from multiprocessing import Process, Queue, Event, Value

import sensor_devices
import stats_service
import data_service

logging.config.fileConfig('logging.conf')
infoLogger = logging.getLogger('customInfoLogger')
errorLogger = logging.getLogger('customErrorLogger')

conf_path = "app_conf.json"
username_label = "username"
password_label = "password"
server_url = "server_url"
auth_interval = "auth_interval"
time_format = "time_format"
server_time_format = "server_time_format"
fuel_level_limit = "fuel_level_limit"
temp_interval = "temp_interval"
load_interval = "load_interval"
api_key = "api_key"


# reading app configuration from json file
def read_conf():
    try:
        conf_file = open(conf_path)
        conf = json.load(conf_file)
        return conf
    except:
        errorLogger.critical("Cant read app configuration file - ", conf_path, " !")
        return None


# periodically requesting device signup, returns received jwt
def signup_periodically(key, username, password, time_pattern, url, interval):
    jwt = None
    while jwt is None:
        jwt = auth.register(key, username, password, time_pattern, url)
        time.sleep(interval)
    return jwt


# iot data aggregation and forwarding to cloud
def collect_temperature_data(interval, queue, url, jwt, time_pattern, flag, stats_queue):
    stats = stats_service.Stats()
    while not flag.is_set():
        data = []
        while not queue.empty():
            data.append(queue.get())
        # send request to Cloud only if there is available data
        line = ""
        for i in data:
            line += str(i.value) + "  "
        print("Temperature data read from queue: ", line)
        if len(data) > 0:
            # if data is not sent to cloud, it is returned to queue
            if not data_service.handle_temperature_data(data, url, jwt, time_pattern):
                for i in data:
                    queue.put(i)
            else:
                stats.update_data(len(data) * 4, 4, 1)
        else:
            infoLogger.warning("There is no temperature sensor data to handle!")
        time.sleep(interval)
    stats_queue.put(stats)
    print("Temperature data handler shutdown!")


def collect_load_data(interval, queue, url, jwt, time_pattern, flag, stats_queue):
    stats = stats_service.Stats()
    while not flag.is_set():
        data = []
        while not queue.empty():
            data.append(queue.get())
        # send request to Cloud only if there is available data
        line = ""
        for i in data:
            line += str(i.value) + "  "
        print("Load data read from queue: ", line)
        if len(data) > 0:
            # if data is not sent to cloud, it is returned to queue
            if not data_service.handle_load_data(data, url, jwt, time_pattern):
                for i in data:
                    queue.put(i)
            else:
                stats.update_data(len(data) * 4, 4, 1)
        else:
            infoLogger.warning("There is no arm load sensor data to handle!")
        time.sleep(interval)
    stats_queue.put(stats)
    print("Arm load data handler shutdown!")


def main():
    # stubs
    temp_data = Queue()
    load_data = Queue()
    fuel_data = Queue()
    Process(target=sensor_devices.test, args=(temp_data, load_data, fuel_data)).start()
    time.sleep(6)
    # read app config
    config = read_conf()
    # if config is read successfully, start app logic
    if config is not None:
        infoLogger.info("IoT Gateway app started!")
        # iot cloud platform login
        jwt = auth.login(config[username_label], config[password_label], config[server_url] + "/auth/login")
        # if failed, periodically request signup
        if jwt is None:
            jwt = signup_periodically(config[api_key], config[username_label], config[password_label],
                                      config[server_time_format], config[server_url] + "/auth/signup",
                                      config[auth_interval])
        # now JWT required for Cloud platform auth is stored in jwt var
        print(jwt)
        # starting stats monitoring
        # using shared memory Queue objects for returning stats data from processes
        stats = stats_service.OverallStats(config[server_url] + "/stats", jwt, config[time_format])
        temp_stats_queue = Queue()
        load_stats_queue = Queue()
        fuel_stats_queue = Queue()
        print("Initial stats:")
        print(stats)
        # flags are used for stopping data handlers on app shutdown
        temp_handler_flag = Event()
        load_handler_flag = Event()
        fuel_handler_flag = Event()
        # temperature data handling
        temperature_data_handler = Process(target=collect_temperature_data, args=(config[temp_interval], temp_data,
                                                                                  config[server_url] + "/data/temp",
                                                                                  jwt, config[time_format],
                                                                                  temp_handler_flag, temp_stats_queue))
        temperature_data_handler.start()
        load_data_handler = Process(target=collect_load_data, args=(config[load_interval], load_data,
                                                                    config[server_url] + "/data/load", jwt,
                                                                    config[time_format], load_handler_flag,
                                                                    load_stats_queue))
        load_data_handler.start()
        # just for testing purposes
        fuel_stats_queue.put(stats_service.Stats())
        # waiting for shutdown signal
        input("Press ENTER to stop the app!")
        infoLogger.info("IoT Gateway app shutting down! Please wait")
        # shutting down handler processes
        temp_handler_flag.set()
        load_handler_flag.set()
        temperature_data_handler.join()
        load_data_handler.join()
        print("Temp data requests final: ", stats.tempDataRequests)
        stats.combine_stats(temp_stats_queue.get(), load_stats_queue.get(), fuel_stats_queue.get() )
        stats.send_stats()

        infoLogger.info("IoT Gateway app shutdown!")
    else:
        print("Can't read app config file!")


if __name__ == '__main__':
    main()
