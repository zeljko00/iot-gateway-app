import json
import auth
import time
import logging.config
import paho.mqtt.client as mqtt
from multiprocessing import Process, Queue, Event
from threading import Thread
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
mqtt_broker = "mqtt_broker"
address = "address"
port = "port"
transport_protocol = "tcp"
temp_topic = "sensors/temperature"
load_topic = "sensors/arm-load"
fuel_topic = "sensors/fuel-level"
http_unauthorized = 401
http_ok = 200
http_no_content = 204

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

def shutdown_controller(temp_handler_flag,load_handler_flag, fuel_handler_flag):
    # waiting for shutdown signal
    input("Press ENTER to stop the app!")
    infoLogger.info("IoT Gateway app shutting down! Please wait")
    print("IoT Gateway app shutting down! Please wait")
    # shutting down handler processes
    temp_handler_flag.set()
    load_handler_flag.set()
    fuel_handler_flag.set()
    print("Shutdown controller stoped!")
def on_connect_temp_handler(client, userdata, flags, rc,props):
    if rc == 0:
        infoLogger.info("Temperature data handler successfully established connection with MQTT broker!")
        client.subscribe(temp_topic, qos=0)
    else:
        errorLogger.error("Temperature data handler failed to establish connection with MQTT broker!")
def on_connect_load_handler(client, userdata, flags, rc,props):
    if rc == 0:
        infoLogger.info("Arm load data handler successfully established connection with MQTT broker!")
        client.subscribe(load_topic, qos=0)
    else:
        errorLogger.error("Arm load data handler failed to establish connection with MQTT broker!")
def on_connect_fuel_handler(client, userdata, flags, rc,props):
    if rc == 0:
        infoLogger.info("Fuel data handler successfully established connection with MQTT broker!")
        client.subscribe(fuel_topic, qos=0)
    else:
        errorLogger.error("Fuel data handler failed to establish connection with MQTT broker!")

# iot data aggregation and forwarding to cloud
def collect_temperature_data(interval, url, jwt, time_pattern, mqtt_address, mqtt_port, flag, stats_queue):
    new_data = []
    old_data = []
    # called when there is new message in temp_topic topic
    def on_message_handler(client, userdata, message):
        if not flag.is_set():
            new_data.append(str(message.payload.decode("utf-8")))
            print("temperature: ",new_data)
    # initializing stats object
    stats = stats_service.Stats()
    # initializing mqtt client for collecting sensor data from broker
    client = mqtt.Client(client_id="temp-data-handler-mqtt-client", transport=transport_protocol,
                         protocol=mqtt.MQTTv5)
    client.on_connect = on_connect_temp_handler
    client.on_message=on_message_handler
    while not client.is_connected():
        try:
            infoLogger.info("Temperature data handler establishing connection with MQTT broker!")
            client.connect(mqtt_address, port=mqtt_port,
                           keepalive=abs(round(interval)) * 3)
            client.loop_start()
        except:
            errorLogger.error("Temperature data handler failed to establish connection with MQTT broker!")
        time.sleep(0.2)
    while not flag.is_set():
        # copy data from list that is populated with newly arrived data and clear that list
        data=new_data.copy()
        new_data.clear()
        # append data that is not sent in previous iterations due to connection problem
        for i in old_data:
            data.append(i)
        old_data.clear()
        # send request to Cloud only if there is available data
        if len(data) > 0:
            code = data_service.handle_temperature_data(data, url, jwt, time_pattern)
            # if data is not sent to cloud, it is returned to queue
            if code != http_ok:
                old_data = data.copy()
            else:
                stats.update_data(len(data) * 4, 4, 1)
            # jwt has expired
            if code == http_unauthorized:
                break
        else:
            infoLogger.warning("There is no temperature sensor data to handle!")
        time.sleep(interval)
    stats_queue.put(stats)
    client.disconnect()
    print("Temperature data handler shutdown!")


def collect_load_data(interval, url, jwt, time_pattern, mqtt_address, mqtt_port, flag, stats_queue):
    new_data = []
    old_data = []
    # called when there is new message in load_topic topic
    def on_message_handler(client, userdata, message):
        if not flag.is_set():
            new_data.append(str(message.payload.decode("utf-8")))
            print("load: ",new_data)

    # initializing stats object
    stats = stats_service.Stats()
    # initializing mqtt client for collecting sensor data from broker
    client = mqtt.Client(client_id="load-data-handler-mqtt-client", transport=transport_protocol,
                         protocol=mqtt.MQTTv5)
    client.on_connect = on_connect_load_handler
    client.on_message = on_message_handler
    while not client.is_connected():
        try:
            infoLogger.info("Arm load data handler establishing connection with MQTT broker!")
            client.connect(mqtt_address, port=mqtt_port,
                           keepalive=abs(round(interval)) * 3)
            client.loop_start()
        except:
            errorLogger.error("Arm load data handler failed to establish connection with MQTT broker!")
        time.sleep(0.2)

    while not flag.is_set():
        # copy data from list that is populated with newly arrived data and clear that list
        data = new_data.copy()
        new_data.clear()
        # append data that is not sent in previous iterations due to connection problem
        for i in old_data:
            data.append(i)
        old_data.clear()
        # send request to Cloud only if there is available data
        if len(data) > 0:
            code = data_service.handle_load_data(data, url, jwt, time_pattern)
            # if data is not sent to cloud, it is returned to queue
            if code != http_ok :
                old_data = data.copy()
            else:
                stats.update_data(len(data) * 4, 4, 1)
            # jwt has expired
            if code == http_unauthorized:
                break
        else:
            infoLogger.warning("There is no arm load sensor data to handle!")
        time.sleep(interval)
    stats_queue.put(stats)
    client.disconnect()
    print("Arm load data handler shutdown!")

def collect_fuel_data(limit, url, jwt, time_pattern, mqtt_address, mqtt_port, flag, stats_queue):
    # initializing stats object
    stats = stats_service.Stats()
    # called when there is new message in load_topic topic
    def on_message_handler(client, userdata, message):
        # making sure that flag is not set in mean time
        if not flag.is_set():
            print("fuel: ",str(message.payload.decode("utf-8")))
            code=data_service.handle_fuel_data(str(message.payload.decode("utf-8")), limit, url, jwt, time_pattern)
            if code == http_ok:
                stats.update_data(4, 4, 1)
            elif code == http_no_content:
                stats.update_data(4, 4, 0)
            # jwt has expired - handler will be stopped, and started again after app restart
            if code == http_unauthorized:
                flag.set()
    # initializing mqtt client for collecting sensor data from broker
    client = mqtt.Client(client_id="fuel-data-handler-mqtt-client", transport=transport_protocol,
                         protocol=mqtt.MQTTv5)
    client.on_connect = on_connect_fuel_handler
    client.on_message = on_message_handler
    while not client.is_connected():
        try:
            infoLogger.info("Fuel level data handler establishing connection with MQTT broker!")
            client.connect(mqtt_address, port=mqtt_port, keepalive=abs(8 * 60 * 60))
            client.loop_start()
        except :
            errorLogger.error("Fuel level data handler failed to establish connection with MQTT broker!")
        time.sleep(0.2)
    # must do like this to be able to stop thread acquired for incoming messages(on_message) after flag is set
    while not flag.is_set():
        time.sleep(2)
    stats_queue.put(stats)
    client.disconnect()
    print("Fuel level data handler shutdown!")

def main():
    # used for restarting device due to jwt expiration
    reset = True
    while reset:
        # read app config
        config = read_conf()
        # if config is read successfully, start app logic
        if config is not None:
            infoLogger.info("IoT Gateway app started!")
            print("IoT Gateway app started!")
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
            # flags are used for stopping data handlers on app shutdown
            temp_handler_flag = Event()
            load_handler_flag = Event()
            fuel_handler_flag = Event()
            # shutdown thread
            shutdown_controller_worker = Thread(target=shutdown_controller,
                                                args=(temp_handler_flag, load_handler_flag, fuel_handler_flag))
            shutdown_controller_worker.start()
            # data handling workers
            temperature_data_handler = Process(target=collect_temperature_data, args=(config[temp_interval],
                                                                                      config[server_url] + "/data/temp",
                                                                                      jwt, config[time_format],
                                                                                      config[mqtt_broker][address],
                                                                                      config[mqtt_broker][port],
                                                                                      temp_handler_flag,
                                                                                      temp_stats_queue))
            temperature_data_handler.start()
            load_data_handler = Process(target=collect_load_data, args=(config[load_interval],
                                                                        config[server_url] + "/data/load", jwt,
                                                                        config[time_format],
                                                                        config[mqtt_broker][address],
                                                                        config[mqtt_broker][port],
                                                                        load_handler_flag, load_stats_queue))
            load_data_handler.start()
            fuel_data_handler = Process(target=collect_fuel_data, args=(config[fuel_level_limit],
                                                                        config[server_url] + "/data/fuel", jwt,
                                                                        config[time_format],
                                                                        config[mqtt_broker][address],
                                                                        config[mqtt_broker][port],
                                                                        fuel_handler_flag, fuel_stats_queue,))
            fuel_data_handler.start()
            temperature_data_handler.join()
            load_data_handler.join()
            fuel_data_handler.join()
            stats.combine_stats(temp_stats_queue.get(), load_stats_queue.get(), fuel_stats_queue.get() )
            stats.send_stats()
            # checking jwt, if jwt has expired  app will restart
            jwt_code=auth.check_jwt(jwt, config[server_url] + "/auth/jwt-check")
            if jwt_code == http_ok:
                reset = False
                infoLogger.info("IoT Gateway app shutdown!")
                print("IoT Gateway app shutdown!")
            else:
                reset = True
                infoLogger.info("IoT Gateway app restart!")
                print("IoT Gateway app restart!")
        else:
            print("Can't read app config file!")


if __name__ == '__main__':
    main()
