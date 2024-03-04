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
    """
    A wrapper class for the configuration file JSON

            Properties:
                temp_mode: Property for temperature mode
                load_mode: Property for load mode
                fuel_mode: Property for fuel mode
                can_interface: Property for CAN interface
                can_channel: Property for CAN channel
                can_bitrate: Property for CAN bitrate
                mqtt_broker_username: Property for MQTT broker client username
                mqtt_broker_password: Property for MQTT broker client password
                mqtt_broker_address: Property for MQTT broker client address
                mqtt_broker_port: Property for MQTT broker client port
                server_url: Property for cloud service url
                iot_username: Property for the username that an IoT device uses
                iot_password: Property for the password that an IoT device uses
                api_key: Property for cloud api key
                server_time_format: Property for cloud service time format
                auth_interval: Property for cloud service authentication period
                temp_settings_interval: Property for temperature period
                load_settings_interval: Property for load period
                fuel_settings_interval: Property for fuel period
                time_format: Property for time format
                fuel_settings_level_limit: Property for fuel level limit
                gateway_cloud_broker_iot_username: Property for cloud MQTT broker username
                gateway_cloud_broker_iot_password: Property for cloud MQTT broker password
                gateway_cloud_broker_address: Property for cloud MQTT broker address
                gateway_cloud_broker_port: Property for cloud MQTT broker port
                temp_settings: Property for temperature settings
                load_settings: Property for load settings
                fuel_settings: Property for fuel_settings
                rest_api_host: Property for REST API hostname
                rest_api_port: Property for REST API port
            Methods:
                __init__(path, error_logger, custom_logger): Class constructor for initializing class objects
                try_open(): Method for reading the configuration from a configuration file
                write(): Write the current configuration to the configuration file
                temp_settings(temp_settings_set): Setter for temperature settings
                load_settings(load_settings_set): Setter for load settings
                fuel_settings(fuel_settings_set): Setter for fuel settings

    """
    def __init__(self, path, error_logger=None, custom_logger=None):
        """
            Constructor that initializes a Config object.
                Args:
                    path: str
                        File path to the configuration file
                    error_logger: Logger
                        An error logger
                    custom_logger: Logger
                        A standard output (console) logger
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
                    level_limit: 200, mode: "SIMULATOR", interval: 20}, temp_settings: {
                    interval: 20, mode: "SIMULATOR"}, load_settings: {
                    interval: 20, mode: "SIMULATOR"}, server_url: "", mqtt_broker: {
                    username: "", password: ""
                }}

    def write(self):
        """
            Method that writes the current configuration to the configuration file
        """
        try:
            with open(self.path, 'w') as json_file:
                json.dump(self.config, json_file)
        except BaseException:
            self.error_logger.critical(
                "Can't write to app config file - ", self.path, " !")
            self.custom_logger.critical(
                "Can't read app config file - ", self.path, " !")

    @property
    def temp_mode(self):
        """
        Temperature mode. Indicates the source of the temperature data.
            Returns:
                temp_mode: str
        """
        return self.config[temp_settings][mode]

    @property
    def load_mode(self):
        """
        Load mode. Indicates the source of the load data.
            Returns:
                load_mode: str
        """
        return self.config[load_settings][mode]

    @property
    def fuel_mode(self):
        """
        Fuel mode. Indicates the source of the fuel data.
            Returns:
                fuel_mode: str
        """
        return self.config[fuel_settings][mode]

    @property
    def can_interface(self):
        """
        CAN interface name.
            Returns:
                interface: str
        """
        return self.config[can_general_settings][interface]

    @property
    def can_channel(self):
        """
        CAN channel name.
            Returns:
                channel: str
        """
        return self.config[can_general_settings][channel]

    @property
    def can_bitrate(self):
        """
        CAN bitrate
            Returns:
                bitrate: int
        """
        return self.config[can_general_settings][bitrate]

    @property
    def mqtt_broker_username(self):
        """
        MQTT broker client username
            Returns:
                username: str
        """
        return self.config[mqtt_broker][username]

    @property
    def mqtt_broker_password(self):
        """
        MQTT broker client password
            Returns:
                password: str
        """
        return self.config[mqtt_broker][password]

    @property
    def mqtt_broker_address(self):
        """
        MQTT broker client address
            Returns:
                address: str
        """
        return self.config[mqtt_broker][address]

    @property
    def mqtt_broker_port(self):
        """
        MQTT broker client port
            Returns:
                port: int
        """
        return self.config[mqtt_broker][port]

    @property
    def server_url(self):
        """
        Cloud service URL
            Returns:
                server_url: str
        """
        return self.config[server_url]

    @property
    def iot_username(self):
        """
        IoT device username
            Returns:
                username: str
        """
        return self.config[username]

    @property
    def iot_password(self):
        """
        IoT device password
            Returns:
                password: str
        """
        return self.config[password]

    @property
    def api_key(self):
        """
        Cloud service API key
            Returns:
                api_key: str
        """
        return self.config[api_key]

    @property
    def server_time_format(self):
        """
        Cloud service time format
            Returns:
                server_time_format: str
        """
        return self.config[server_time_format]

    @property
    def auth_interval(self):
        """
        Interval for cloud service authentication attempts
            Returns:
                interval: int
        """
        return self.config[auth_interval]

    @property
    def temp_settings_interval(self):
        """
        Interval for sending temperature messages
            Returns:
                temperature_interval: int
        """
        return self.config[temp_settings][interval]

    @property
    def load_settings_interval(self):
        """
        Interval for sending load messages
            Returns:
                load_interval: int
        """
        return self.config[load_settings][interval]

    @property
    def fuel_settings_interval(self):
        """
        Interval for sending fuel messages
            Returns:
                fuel_interval: int
        """
        return self.config[fuel_settings][interval]

    @property
    def time_format(self):
        """
        Time format
            Returns:
                time_format: str
        """
        return self.config[time_format]

    @property
    def fuel_settings_level_limit(self):
        """
        Fuel level limit
            Returns:
                fuel_level_limit: int
        """
        return self.config[fuel_settings][level_limit]

    @property
    def gateway_cloud_broker_iot_username(self):
        """
        Gateway cloud MQTT broker username
            Returns:
                username: str
        """
        return self.config[gateway_cloud_broker][username]

    @property
    def gateway_cloud_broker_iot_password(self):
        """
        Gateway cloud MQTT broker password
            Returns:
                password: str
        """
        return self.config[gateway_cloud_broker][password]

    @property
    def gateway_cloud_broker_address(self):
        """
        Gateway cloud MQTT broker address
            Returns:
                address: str
        """
        return self.config[gateway_cloud_broker][address]

    @property
    def gateway_cloud_broker_port(self):
        """
        Gateway cloud MQTT broker port
            Returns:
                port: int
        """
        return self.config[gateway_cloud_broker][port]

    @property
    def temp_settings(self):
        """
        Temperature settings
            Returns:
                temp_settings: str
        """
        return self.config[temp_settings]

    @property
    def load_settings(self):
        """
        Load settings
            Returns:
                load_settings: str
        """
        return self.config[load_settings]

    @property
    def fuel_settings(self):
        """
        Fuel settings
            Returns:
                fuel_settings: str
        """
        return self.config[fuel_settings]

    @temp_settings.setter
    def temp_settings(self, temp_settings_set):
        """
        Setter for temperature settings
            Args:
                temp_settings_set: str
                    New temperature settings
        """
        self.config[temp_settings] = temp_settings_set

    @load_settings.setter
    def load_settings(self, load_settings_set):
        """
        Setter for load settings
            Args:
                load_settings_set: str
                    New load settings
        """
        self.config[load_settings] = load_settings_set

    @fuel_settings.setter
    def fuel_settings(self, fuel_settings_set):
        """
        Setter for fuel settings
            Args:
                fuel_settings_set: str
                    New fuel settings
        """
        self.config[fuel_settings] = fuel_settings_set

    @property
    def get_rest_api_host(self):
        """
        Gateway REST API hostname
            Returns:
                hostname: str
        """
        return self.config[rest_api][host]

    @property
    def get_rest_api_port(self):
        """
        Gateway REST API port
            Returns:
                port: int
        """
        return self.config[rest_api][port]
