import json
from multiprocessing import Event
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler

conf_dir = './configuration'
conf_path = conf_dir + "/app_conf.json"

temp_settings = 'temp_settings'
load_settings = 'load_settings'
fuel_settings = 'fuel_settings'

mode = "mode"
can_general_settings = "can_general_settings"
interface = "interface"
channel = "channel"
bitrate = "bitrate"
mqtt_broker = "mqtt_broker"
username = "username"
password = "password"
address = "address"
port = "port"
server_url = "server_url"
server_time_format = "server_time_format"
api_key = "api_key"
auth_interval = "auth_interval"
interval = "interval"
time_format = "time_format"
level_limit = "level_limit"
gateway_cloud_broker = "gateway_cloud_broker"
rest_api = "rest_api"
host = "host"
port = "port"


class ConfFlags:
    def __init__(self):
        self.fuel_flag = Event()
        self.temp_flag = Event()
        self.load_flag = Event()
        self.can_flag = Event()
        self.execution_flag = Event()

    def set_all(self):
        self.fuel_flag.set()
        self.temp_flag.set()
        self.load_flag.set()
        self.can_flag.set()
        self.execution_flag.set()


class ConfHandler(FileSystemEventHandler):
    def __init__(self, conf_flags: ConfFlags):
        super()
        self.conf_flags = conf_flags

    def on_modified(self, event):
        self.conf_flags.set_all()

    def on_any_event(self, event):
        return


def start_config_observer(conf_flags):
    event_handler = ConfHandler(conf_flags)
    observer = PollingObserver()
    observer.schedule(event_handler, path=conf_dir, recursive=False)
    observer.start()
    return observer


# POSSIBLY MODIFY READ AND WRITE FOR CONFIGURATION SO THAT THEY PRIMARILY OPERATE ON
# MEMORY STORED CONFIGURATION INSTEAD OF FILE, AND ONLY TOUCH FILE WHEN NECESSARY.
# SAME CAN BE DONE FOR PROCESSES.
# THIS IS JUST FOR EFFICIENCY AND IS NOT NEEDED FOR OPERATION.
def read_conf():
    try:
        conf_file = open(conf_path)
        conf = json.load(conf_file)
        return conf
    except BaseException:
        return None


def write_conf(config):
    try:
        conf_file = open(conf_path, "w")
        conf_file.write(json.dumps(config, indent=4))
        return config
    except BaseException:
        return None


def get_temp(config):
    return config['temp']


def get_load(config):
    return config['load']


def get_fuel(config):
    return config['fuel']


def get_temp_interval(config):
    return config.get_temp_settings_interval()


def get_load_interval(config):
    return config.get_load_settings_interval()


def get_fuel_level_limit(config):
    return config.get_fuel_settings_level_limit()


class Config:
    def __init__(self, path, error_logger=None, custom_logger=None):
        self.path = path
        self.config = None
        self.error_logger = error_logger
        self.custom_logger = custom_logger

    def try_open(self):
        try:
            conf_file = open(self.path)
            self.config = json.load(conf_file)
        except BaseException:
            self.error_logger.critical(
                "Using default config! Can't read app config file - ", self.path, " !")
            self.custom_logger.critical(
                "Using default config! Can't read app config file - ", self.path, " !")

            self.config = {
                fuel_settings: {
                    "fuel_level_limit": 200, "mode": "SIMULATOR"}, temp_settings: {
                    "temp_interval": 20, "mode": "SIMULATOR"}, load_settings: {
                    "load_interval": 20, "mode": "SIMULATOR"}, }

    def get_temp_mode(self):
        return self.config[temp_settings][mode]

    def get_load_mode(self):
        return self.config[load_settings][mode]

    def get_fuel_mode(self):
        return self.config[fuel_settings][mode]

    def get_can_interface(self):
        return self.config[can_general_settings][interface]

    def get_can_channel(self):
        return self.config[can_general_settings][channel]

    def get_can_bitrate(self):
        return self.config[can_general_settings][bitrate]

    def get_mqtt_broker_username(self):
        return self.config[mqtt_broker][username]

    def get_mqtt_broker_password(self):
        return self.config[mqtt_broker][password]

    def get_mqtt_broker_address(self):
        return self.config[mqtt_broker][address]

    def get_mqtt_broker_port(self):
        return self.config[mqtt_broker][port]

    def get_server_url(self):
        return self.config[server_url]

    def get_iot_username(self):
        return self.config[username]

    def get_iot_password(self):
        return self.config[password]

    def get_api_key(self):
        return self.config[api_key]

    def get_server_time_format(self):
        return self.config[server_time_format]

    def get_auth_interval(self):
        return self.config[auth_interval]

    def get_temp_settings_interval(self):
        return self.config[temp_settings][interval]

    def get_load_settings_interval(self):
        return self.config[load_settings][interval]

    def get_time_format(self):
        return self.config[time_format]

    def get_fuel_settings_level_limit(self):
        return self.config[fuel_settings][level_limit]

    def get_gateway_cloud_broker_iot_username(self):
        return self.config[gateway_cloud_broker][username]

    def get_gateway_cloud_broker_iot_password(self):
        return self.config[gateway_cloud_broker][password]

    def get_gateway_cloud_broker_address(self):
        return self.config[gateway_cloud_broker][address]

    def get_gateway_cloud_broker_port(self):
        return self.config[gateway_cloud_broker][port]

    def get_temp_settings(self):
        return self.config[temp_settings]

    def get_load_settings(self):
        return self.config[load_settings]

    def get_fuel_settings(self):
        return self.config[fuel_settings]

    def set_temp_settings(self, temp_settings_set):
        self.config[temp_settings] = temp_settings_set

    def set_load_settings(self, load_settings_set):
        self.config[load_settings] = load_settings_set

    def set_fuel_settings(self, fuel_settings_set):
        self.config[fuel_settings] = fuel_settings_set

    def get_rest_api_host(self):
        return self.config[rest_api][host]

    def get_rest_api_port(self):
        return self.config[rest_api][port]
