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
    """A wrapper class for the configuration file JSON

            Methods:
                __init__(path, error_logger, custom_logger): Class constructor for initializing class objects
                try_open(): Method for reading the configuration from a configuration file
                get_temp_mode(): Getter for temperature mode
                get_load_mode(): Getter for load mode
                get_fuel_mode(): Getter for fuel mode
                get_can_interface(): Getter for CAN interface
                get_can_channel(): Getter for CAN channel
                get_can_bitrate(): Getter for CAN bitrate
                get_mqtt_broker_username(): Getter for MQTT broker client username
                get_mqtt_broker_password(): Getter for MQTT broker client password
                get_mqtt_broker_address(): Getter for MQTT broker client address
                get_mqtt_broker_port(): Getter for MQTT broker client port
                get_server_url(): Getter for cloud service url
                get_iot_username(): Getter for the username that an IoT device uses
                get_iot_password(): Getter for the password that an IoT device uses
                get_api_key(): Getter for cloud api key
                get_server_time_format(): Getter for cloud service time format
                get_auth_interval(): Getter for cloud service authentication period
                get_temp_settings_interval(): Getter for temperature period
                get_load_settings_interval(): Getter for load period
                get_fuel_settings_interval(): Getter for fuel period
                get_time_format(): Getter for time format
                get_fuel_settings_level_limit(): Getter for fuel level limit
                get_gateway_cloud_broker_iot_username(): Getter for cloud MQTT broker username
                get_gateway_cloud_broker_iot_password(): Getter for cloud MQTT broker password
                get_gateway_cloud_broker_address(): Getter for cloud MQTT broker address
                get_gateway_cloud_broker_port(): Getter for cloud MQTT broker port
                get_temp_settings(): Getter for temperature settings
                get_load_settings(): Getter for load settings
                get_fuel_settings(): Getter for fuel_settings
                set_temp_settings(): Setter for temperature settings
                set_load_settings(): Setter for load settings
                set_fuel_settings(): Setter for fuel settings
                get_rest_api_host(): Getter for REST API hostname
                get_rest_api_port(): Getter for REST API port

    """
    def __init__(self, path, error_logger=None, custom_logger=None):
        """
            Constructor that initializes a Config object.
                Args:
                    path: File path to the configuration file
                    error_logger: An error logger
                    custom_logger: A standard output (console) logger
        """
        self.path = path
        self.config = None
        self.error_logger = error_logger
        self.custom_logger = custom_logger

    def try_open(self):
        """
            Method that tries to open and read the configuration from the configuration file.
        """
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
                    level_limit: 200, mode: "SIMULATOR"}, temp_settings: {
                    interval: 20, mode: "SIMULATOR"}, load_settings: {
                    interval: 20, mode: "SIMULATOR"}, server_url: "", mqtt_broker: {
                    username: "", password: ""
                }}

    @property
    def temp_mode(self):
        return self.config[temp_settings][mode]

    @property
    def load_mode(self):
        return self.config[load_settings][mode]

    @property
    def fuel_mode(self):
        return self.config[fuel_settings][mode]

    @property
    def can_interface(self):
        return self.config[can_general_settings][interface]

    @property
    def can_channel(self):
        return self.config[can_general_settings][channel]

    @property
    def can_bitrate(self):
        return self.config[can_general_settings][bitrate]

    @property
    def mqtt_broker_username(self):
        return self.config[mqtt_broker][username]

    @property
    def mqtt_broker_password(self):
        return self.config[mqtt_broker][password]

    @property
    def mqtt_broker_address(self):
        return self.config[mqtt_broker][address]

    @property
    def mqtt_broker_port(self):
        return self.config[mqtt_broker][port]

    @property
    def server_url(self):
        return self.config[server_url]

    @property
    def iot_username(self):
        return self.config[username]

    @property
    def iot_password(self):
        return self.config[password]

    @property
    def api_key(self):
        return self.config[api_key]

    @property
    def server_time_format(self):
        return self.config[server_time_format]

    @property
    def auth_interval(self):
        return self.config[auth_interval]

    @property
    def temp_settings_interval(self):
        return self.config[temp_settings][interval]

    @property
    def load_settings_interval(self):
        return self.config[load_settings][interval]

    @property
    def time_format(self):
        return self.config[time_format]

    @property
    def fuel_settings_level_limit(self):
        return self.config[fuel_settings][level_limit]

    @property
    def gateway_cloud_broker_iot_username(self):
        return self.config[gateway_cloud_broker][username]

    @property
    def gateway_cloud_broker_iot_password(self):
        return self.config[gateway_cloud_broker][password]

    @property
    def gateway_cloud_broker_address(self):
        return self.config[gateway_cloud_broker][address]

    @property
    def gateway_cloud_broker_port(self):
        return self.config[gateway_cloud_broker][port]

    @property
    def temp_settings(self):
        return self.config[temp_settings]

    @property
    def load_settings(self):
        return self.config[load_settings]

    @property
    def fuel_settings(self):
        return self.config[fuel_settings]

    @temp_settings.setter
    def temp_settings(self, temp_settings_set):
        self.config[temp_settings] = temp_settings_set

    @load_settings.setter
    def load_settings(self, load_settings_set):
        self.config[load_settings] = load_settings_set

    @fuel_settings.setter
    def fuel_settings(self, fuel_settings_set):
        self.config[fuel_settings] = fuel_settings_set

    @property
    def get_rest_api_host(self):
        return self.config[rest_api][host]

    @property
    def get_rest_api_port(self):
        return self.config[rest_api][port]
