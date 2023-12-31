'''
app
============
Module that contains main iot gateway logic.

Functions
---------
read_conf()
    Reads iot gateway config file.
signup_periodically(key, username, password, time_pattern, url, interval)
    Periodically initiates device signup on cloud services.
shutdown_controller(temp_handler_flag,load_handler_flag, fuel_handler_flag):
    Shuts down all sensors.
on_connect_temp_handler(client, userdata, flags, rc,props)
    Logic executed after successfully connecting temperature sensor to MQTT broker.
on_connect_load_handler(client, userdata, flags, rc,props)
    Logic executed after successfully connecting load sensor to MQTT broker.
on_connect_fuel_handler(client, userdata, flags, rc,props)
    Logic executed after successfully connecting fuel sensor to MQTT broker.
collect_temperature_data(interval, url, jwt, time_pattern, mqtt_address, mqtt_port, mqtt_user,mqtt_pass, flag, stats_queue)
    Collects temperature data and periodically initiates data processing and forwarding.
collect_load_data(interval, url, jwt, time_pattern, mqtt_address, mqtt_port, mqtt_user,mqtt_pass,flag, stats_queue)
    Collects load data and periodically initiates data processing and forwarding.
collect_fuel_data(limit, url, jwt, time_pattern, mqtt_address, mqtt_port, mqtt_user,mqtt_pass, flag, stats_queue)
    Collects temperature data and initiates data filtering and forwarding.
main()
    Iot gateway app entrypoint.

Constants
---------
conf_path: str
    App config file path.
user: str
    Device username.
password: str
    Device password.
server_url: str
    Cloud services' URL.
auth_interval: int
    Time lapse between signup requests.
time_format: str
    Time format.
server_time_format: str
    Server's time format.
fuel_level_limit:
    Critical level of fuel.
temp_interval: int
    Time lapse between temperature cloud service requests.
load_interval = "load_interval"
    Time lapse between load cloud service requests.
api_key: str
    Cloud platform API key.
transport_protocol: str
    Transport protocol for MQTT.
temp_topic: str
    MQTT topic for  temperature data.
load_topic: str
    MQTT topic for load data.
fuel_topic: str
    MQTT topic for fuel data.
http_unauthorized: int
    Http status code.
http_ok: int
    Http status code.
http_no_content: int
    Http status code.
qos: int
    Quality of service of MQTT.
'''

import json
import auth
import stats_service
import data_service
import time
import logging.config
import paho.mqtt.client as mqtt
from multiprocessing import Process, Queue, Event
from threading import Thread

logging.config.fileConfig('logging.conf')
infoLogger = logging.getLogger('customInfoLogger')
errorLogger = logging.getLogger('customErrorLogger')
customLogger = logging.getLogger('customConsoleLogger')

conf_path = "app_conf.json"
user = "username"
password = "password"
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
qos=2

def read_conf():
    '''
    Reads app config file.

    Parameters
    ----------
    Returns
    -------
    conf: dict
        Configuration data parsed from json config file.
    '''
    try:
        conf_file = open(conf_path)
        conf = json.load(conf_file)
        return conf
    except:
        errorLogger.critical("Cant read app configuration file - ", conf_path, " !")
        return None

# def signup_periodically(key, username, password, time_pattern, url, interval):
#     '''
#     Periodically requests device signup.
#
#     Parameters
#     ----------
#     key: str
#         API key.
#     username: str
#         Device's username,
#     password: str
#         Device's password,
#     time_pattern: str
#         Device's time pattern.
#     url: str
#         Cloud services URL.
#     interval: int
#         Time lapse between consecutive requests.
#
#     Returns
#     -------
#     jwt: str
#         JSON web token for accessing cloud services.
#     '''
#     jwt = None
#     while jwt is None:
#         customLogger.debug("Trying to sign up!")
#         jwt = auth.register(key, username, password, time_pattern, url)
#         time.sleep(interval)
#     customLogger.debug("Successful sign up!")
#     return jwt

def shutdown_controller(temp_handler_flag,load_handler_flag, fuel_handler_flag):
    '''
    Handles user request for sensor shutdown.

    When user requests shutdown, sets sensor processes' stop tokens.

    Parameters
    ----------
    temp_handler_flag: multiprocessing.Event
        Token used for stopping temperature sensor process.
    load_handler_flag: multiprocessing.Event
        Token used for stopping load sensor process.
    fuel_handler_flag: multiprocessing.Event
        Token used for stopping fuel sensor process.

    Returns
    -------
    '''
    # waiting for shutdown signal
    input("")
    infoLogger.info("IoT Gateway app shutting down! Please wait")
    customLogger.debug("IoT Gateway app shutting down! Please wait")
    # shutting down handler processes
    temp_handler_flag.set()
    load_handler_flag.set()
    fuel_handler_flag.set()
def on_connect_temp_handler(client, userdata, flags, rc,props):
    '''
    Logic executed after successfully connecting temperature sensor to MQTT broker.

    Parameters
    ----------
    client: mqtt.client
    userdata: object
    flags:
    rc: int
    props:

    Returns
    -------
    '''
    if rc == 0:
        infoLogger.info("Temperature data handler successfully established connection with MQTT broker!")
        client.subscribe(temp_topic, qos=qos)
    else:
        errorLogger.error("Temperature data handler failed to establish connection with MQTT broker!")
        customLogger.critical("Temperature data handler failed to establish connection with MQTT broker!")
def on_connect_load_handler(client, userdata, flags, rc,props):
    '''
    Logic executed after successfully connecting arm load sensor to MQTT broker.

    Parameters
    ----------
    client: mqtt.client
    userdata: object
    flags:
    rc: int
    props:

    Returns
    -------
    '''
    if rc == 0:
        infoLogger.info("Arm load data handler successfully established connection with MQTT broker!")
        client.subscribe(load_topic, qos=qos)
    else:
        errorLogger.error("Arm load data handler failed to establish connection with MQTT broker!")
        customLogger.critical("Arm load data handler failed to establish connection with MQTT broker!")
def on_connect_fuel_handler(client, userdata, flags, rc,props):
    '''
    Logic executed after successfully connecting fuel level sensor to MQTT broker.

    Parameters
    ----------
    client: mqtt.client
    userdata: object
    flags:
    rc: int
    props:

    Returns
    -------
    '''
    if rc == 0:
        infoLogger.info("Fuel data handler successfully established connection with MQTT broker!")
        client.subscribe(fuel_topic, qos=qos)
    else:
        errorLogger.error("Fuel data handler failed to establish connection with MQTT broker!")
        customLogger.critical("Fuel data handler failed to establish connection with MQTT broker!")

# iot data aggregation and forwarding to cloud
def collect_temperature_data(interval, url, jwt, time_pattern, mqtt_address, mqtt_port, mqtt_user,mqtt_pass, flag, stats_queue):
    '''
    Temperature data handler logic.

    Establishes connection with MQTT broker. Listens for incoming messages. Handles received temperature messages and
    periodically initiates data processing.

    Parameters
    ----------
    interval: int
         Measuring interval.
    url: str
        Cloud services' URL.
    jwt: str
        JSON web auth token.
    time_pattern: str
        Time pattern/format.
    mqtt_address: str
        MQTT broker's URL.
    mqtt_port: int
        MQTT broker's port.
    mqtt_user: str
         Username required for establishing connection with MQTT broker.
    mqtt_pass: str
         Password required for establishing connection with MQTT broker.
    flag: multiprocessing.Event
        Object used for stopping temperature sensor process.
    stats_queue: multiprocessing.Queue
        Stats data wrapper.
    Returns
    -------
    '''
    new_data = []
    old_data = []
    # called when there is new message in temp_topic topic
    def on_message_handler(client, userdata, message):
        '''
         Handles received mqtt message.

         After receiving mqtt message, locally stores temperature data.

         Parameters
         ----------
         client: mqtt.client
         userdata: object
         message: object

         Returns
         -------
        '''
        if not flag.is_set():
            new_data.append(str(message.payload.decode("utf-8")))
            customLogger.info("Received temperature data: " + str(message.payload.decode("utf-8")))
    # initializing stats object
    stats = stats_service.Stats()
    # initializing mqtt client for collecting sensor data from broker
    client = mqtt.Client(client_id="temp-data-handler-mqtt-client", transport=transport_protocol,
                         protocol=mqtt.MQTTv5)
    client.username_pw_set(username=mqtt_user, password=mqtt_pass)
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
    # periodically processes collected data and forwards result to cloud services
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
                customLogger.error("JWT has expired!")
                break
        else:
            infoLogger.warning("There is no temperature sensor data to handle!")
        time.sleep(interval)
    # shutting down temperature sensor
    stats_queue.put(stats)
    client.loop_stop()
    client.disconnect()
    customLogger.debug("Temperature data handler shutdown!")


def collect_load_data(interval, url, jwt, time_pattern, mqtt_address, mqtt_port, mqtt_user,mqtt_pass,flag, stats_queue):
    '''
    Load data handler logic.

    Establishes connection with MQTT broker. Listens for incoming messages. Handles received load messages and
    periodically initiates data processing.

    Parameters
    ----------
    interval: int
        Measuring interval.
    url: str
       Cloud services' URL.
    jwt: str
       JSON web auth token.
    time_pattern: str
       Time pattern/format.
    mqtt_address: str
       MQTT broker's URL.
    mqtt_port: int
       MQTT broker's port.
    mqtt_user: str
        Username required for establishing connection with MQTT broker.
    mqtt_pass: str
        Password required for establishing connection with MQTT broker.
    flag: multiprocessing.Event
       Object used for stopping temperature sensor process.
    stats_queue: multiprocessing.Queue
        Stats data wrapper.

    Returns
    -------
   '''
    new_data = []
    old_data = []
    # called when there is new message in load_topic topic
    def on_message_handler(client, userdata, message):
        '''
         Handles received mqtt message.

         After receiving mqtt message, locally stores load data.

         Parameters
         ----------
         client: mqtt.client
         userdata: object
         message: object

         Returns
         -------
        '''
        if not flag.is_set():
            new_data.append(str(message.payload.decode("utf-8")))
            customLogger.info("Received load data: "+str(message.payload.decode("utf-8")))

    # initializing stats object
    stats = stats_service.Stats()
    # initializing mqtt client for collecting sensor data from broker
    client = mqtt.Client(client_id="load-data-handler-mqtt-client", transport=transport_protocol,
                         protocol=mqtt.MQTTv5)
    client.username_pw_set(username=mqtt_user, password=mqtt_pass)
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
    # periodically processes collected data and forwards result to cloud services
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
                customLogger.error("JWT has expired!")
                break
        else:
            infoLogger.warning("There is no arm load sensor data to handle!")
        time.sleep(interval)
    # shutting down load sensor
    stats_queue.put(stats)
    client.loop_stop()
    client.disconnect()
    customLogger.debug("Arm load data handler shutdown!")

def collect_fuel_data(limit, url, jwt, time_pattern, mqtt_address, mqtt_port, mqtt_user,mqtt_pass, flag, stats_queue):
    '''
    Fuel data handler logic.

    Establishes connection with MQTT broker. Listens for incoming messages. Handles received fuel messages and
    initiates data filtering and forwarding.

    Parameters
    ----------
    limit: int
       Critical fuel level.
    url: str
      Cloud services' URL.
    jwt: str
      JSON web auth token.
    time_pattern: str
      Time pattern/format.
    mqtt_address: str
      MQTT broker's URL.
    mqtt_port: int
      MQTT broker's port.
    mqtt_user: str
       Username required for establishing connection with MQTT broker.
    mqtt_pass: str
       Password required for establishing connection with MQTT broker.
    flag: multiprocessing.Event
      Object used for stopping temperature sensor process.
    stats_queue: multiprocessing.Queue
       Stats data wrapper.

    Returns
    -------
    '''
    # initializing stats object
    stats = stats_service.Stats()
    # called when there is new message in load_topic topic
    def on_message_handler(client, userdata, message):
        '''
            Handles received mqtt message.

            After receiving mqtt message, initiates fuel data processing.

            Parameters
            ----------
            client: mqtt.client
            userdata: object
            message: object

            Returns
            -------
        '''
        # making sure that flag is not set in meantime
        if not flag.is_set():
            customLogger.info("Received fuel data: "+str(message.payload.decode("utf-8")))
            code= data_service.handle_fuel_data(str(message.payload.decode("utf-8")), limit, url, jwt, time_pattern)
            if code == http_ok:
                stats.update_data(4, 4, 1)
            elif code == http_no_content:
                stats.update_data(4, 0, 0)
            # jwt has expired - handler will be stopped, and started again after app restart
            elif code == http_unauthorized:
                customLogger.error("JWT has expired!")
                flag.set()
    # initializing mqtt client for collecting sensor data from broker
    client = mqtt.Client(client_id="fuel-data-handler-mqtt-client", transport=transport_protocol,
                         protocol=mqtt.MQTTv5)
    client.username_pw_set(username=mqtt_user, password=mqtt_pass)
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
    # shutting down temperature sensor
    stats_queue.put(stats)
    client.loop_stop()
    client.disconnect()
    customLogger.debug("Fuel level data handler shutdown!")

def main():
    '''
    IoT gateway app entrypoint.

    Parameters
    ----------

    Returns
    -------
    '''
    # used for restarting device due to jwt expiration
    reset = True
    while reset:
        # read app config
        config = read_conf()
        # if config is read successfully, start app logic
        if config is not None:
            infoLogger.info("IoT Gateway app started!")
            customLogger.debug("IoT Gateway app started!")
            # iot cloud platform login
            jwt = auth.login(config[user], config[password], config[server_url] + "/auth/login")
            # if failed, periodically request signup
            if jwt is None:
                customLogger.error("Login failed! Trying to sign up periodically!")
                jwt = signup_periodically(config[api_key], config[user], config[password],
                                          config[server_time_format], config[server_url] + "/auth/signup",
                                          config[auth_interval])
            else:
                customLogger.debug("Login successful!")
            # now JWT required for Cloud platform auth is stored in jwt var
            customLogger.info("Received JWT: " +jwt)
            # starting stats collecting
            # using shared memory Queue objects for returning stats data from processes
            customLogger.debug("Initializing devices stats data!")
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
            customLogger.debug("Starting workers!")
            # creates and starts data handling workers
            temperature_data_handler = Process(target=collect_temperature_data, args=(config[temp_interval],
                                                                                      config[server_url] + "/data/temp",
                                                                                      jwt, config[time_format],
                                                                                      config[mqtt_broker][address],
                                                                                      config[mqtt_broker][port],
                                                                                      config[mqtt_broker][user],
                                                                                      config[mqtt_broker][password],
                                                                                      temp_handler_flag,
                                                                                      temp_stats_queue))
            temperature_data_handler.start()
            load_data_handler = Process(target=collect_load_data, args=(config[load_interval],
                                                                        config[server_url] + "/data/load", jwt,
                                                                        config[time_format],
                                                                        config[mqtt_broker][address],
                                                                        config[mqtt_broker][port],
                                                                        config[mqtt_broker][user],
                                                                        config[mqtt_broker][password],
                                                                        load_handler_flag, load_stats_queue))
            load_data_handler.start()
            fuel_data_handler = Process(target=collect_fuel_data, args=(config[fuel_level_limit],
                                                                        config[server_url] + "/data/fuel", jwt,
                                                                        config[time_format],
                                                                        config[mqtt_broker][address],
                                                                        config[mqtt_broker][port],
                                                                        config[mqtt_broker][user],
                                                                        config[mqtt_broker][password],
                                                                        fuel_handler_flag, fuel_stats_queue,))
            fuel_data_handler.start()
            # waiting fow workers to stop
            temperature_data_handler.join()
            load_data_handler.join()
            fuel_data_handler.join()
            customLogger.debug("Workers stopped!")

            # finalizing stats
            stats.combine_stats(temp_stats_queue.get(), load_stats_queue.get(), fuel_stats_queue.get() )
            customLogger.debug("Sending device stats data!")
            stats.send_stats()
            # checking jwt, if jwt has expired  app will restart
            jwt_code= auth.check_jwt(jwt, config[server_url] + "/auth/jwt-check")
            if jwt_code == http_ok:
                reset = False
                infoLogger.info("IoT Gateway app shutdown!")
                customLogger.debug("IoT Gateway app shutdown!")
            else:
                reset = True
                infoLogger.info("IoT Gateway app restart!")
                customLogger.debug("IoT Gateway app restart!")
        else:
            customLogger.critical("Cant read config file! Aborting...")


if __name__ == '__main__':
    main()
