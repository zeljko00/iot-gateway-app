"""Configuration utilities.

config_util
===========

Module that contains simple gateway rest api server.

Classes
-------
ConfFlags
    Wrapper class for all tracked flags used within processes/threads.
ConfHandler
    Handler for configuration file changes.
Config
    Class for managing configuration.

Functions
---------
start_config_observer
    Start observer that monitors configuration changes.
read_conf
    Read configuration directly as dictionary.
write_conf
    Write configuration directly as dictionary.
get_temp_interval
    Extract temp interval from configuration.
get_load_interval
    Extract load interval from configuration.
get_fuel_level_limit
    Extract fuel level limit from configuration.

Constants
---------
CONF_DIR
    Configuration directory path.
CONF_PATH
    Configuration file path.

Variable name to string mapping constants.
TEMP_SETTINGS
LOAD_SETTINGS
FUEL_SETTINGS
MODE
CAN_GENERAL_SETTINGS
INTERFACE
CHANNEL
BITRATE
MQTT_BROKER
USERNAME
PASSWORD
ADDRESS
PORT
SERVER_URL
SERVER_TIME_FORMAT
API_KEY
AUTH_INTERVAL
INTERVAL
TIME_FORMAT
LEVEL_LIMIT
GATEWAY_CLOUD_BROKER
REST_API
HOST

"""
import json
from multiprocessing import Event
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler

CONF_DIR = './configuration'
CONF_PATH = CONF_DIR + "/app_conf.json"

TEMP_SETTINGS = 'temp_settings'
LOAD_SETTINGS = 'load_settings'
FUEL_SETTINGS = 'fuel_settings'

MODE = "mode"
CAN_GENERAL_SETTINGS = "can_general_settings"
INTERFACE = "interface"
CHANNEL = "channel"
BITRATE = "bitrate"
MQTT_BROKER = "mqtt_broker"
USERNAME = "username"
PASSWORD = "password"
ADDRESS = "address"
PORT = "port"
SERVER_URL = "server_url"
SERVER_TIME_FORMAT = "server_time_format"
API_KEY = "api_key"
AUTH_INTERVAL = "auth_interval"
INTERVAL = "interval"
TIME_FORMAT = "time_format"
LEVEL_LIMIT = "level_limit"
GATEWAY_CLOUD_BROKER = "gateway_cloud_broker"
REST_API = "rest_api"
HOST = "host"


class ConfFlags:
    """Class representing all tracked configuration flags.

    Attributes
    ----------
    fuel_flag: multiprocessing.Event
       Change indicator for fuel process.
    temp_flag: multiprocessing.Event
       Change indicator for temp process.
    load_flag: multiprocessing.Event
       Change indicator for load process.
    can_flag: multiprocessing.Event
       Indicator for sensors mode change.
    execution_flag: multiprocessing.Event
       Indicator for sensors execution context change.

    """

    def __init__(self):
        """Create configuration flags object.

        Initializes all flags as new events.

        """
        self.fuel_flag = Event()
        self.temp_flag = Event()
        self.load_flag = Event()
        self.can_flag = Event()
        self.execution_flag = Event()

    def set_all(self):
        """Set all flags.

        Sets all flags.

        """
        self.fuel_flag.set()
        self.temp_flag.set()
        self.load_flag.set()
        self.can_flag.set()
        self.execution_flag.set()


class ConfHandler(FileSystemEventHandler):
    """Class representing configuration handler.

    Attributes
    ----------
    conf_flags: ConfFlags
       All managed configuration flags.

    """

    def __init__(self, conf_flags: ConfFlags):
        """Create configuration handler object.

        Initializes configuration flags managed by handler.

        Parameters
        ----------
        conf_flags: ConfFlags
           All managed configuration flags.

        """
        super()
        self.conf_flags = conf_flags

    def on_modified(self, event):
        """Set flags on modification event.

        Sets all flags when configuration file change happens.

        Parameters
        ----------
        event: watchdog.events.FileSystemEvent
           Caught filesystem event.

        """
        self.conf_flags.set_all()

    def on_any_event(self, event):
        """Ignore filesystem event.

        Acts like explicit /dev/null for filesystem events.

        Parameters
        ----------
        event: watchdog.events.FileSystemEvent
           Caught filesystem event.

        """
        return


def start_config_observer(conf_flags):
    """Start configuration change observer.

    Starts observer for monitoring file changes in configuration directory. After this function call,
    given observer will set all tracked flags every time file changes happen.

    Parameters
    ----------
    conf_flags: ConfFlags
       Flags that will be set every time configuration changes.

    """
    event_handler = ConfHandler(conf_flags)
    observer = PollingObserver()
    observer.schedule(event_handler, path=CONF_DIR, recursive=False)
    observer.start()
    return observer


def read_conf():
    """Read configuration file.

    Reads configuration file and returns configuration in the form of dictionary
    representing configuration json file.

    Returns
    -------
    conf: dict
       Dictionary representing configuration parameters or
       None in the case of failure to read.

    """
    try:
        conf_file = open(CONF_PATH)
        conf = json.load(conf_file)
        return conf
    except BaseException:
        return None


def write_conf(config):
    """Write configuration file.

    Writes passed dictionary to configuration file and returns new configuration in the
    form of dictionary.

    Parameters
    ----------
    config: dict
       Configuration to be written represented as dictionary.

    Returns
    -------
    config: dict
       Dictionary representing new configuration parameters or
       None in the case of failure to write.

    """
    try:
        conf_file = open(CONF_PATH, "w")
        conf_file.write(json.dumps(config, indent=4))
        return config
    except BaseException:
        return None


def get_temp_interval(config):
    """Extract temperature interval.

    Extract temperature interval value from configuration passed as dictionary.

    Parameters
    ----------
    config: dict
       Configuration dictionary from which to extract temperature interval.

    Returns
    -------
    temp_interval: int
       Extracted temperature interval value.

    """
    return config.temp_settings_interval


def get_load_interval(config):
    """Extract load interval.

    Extract load interval value from configuration passed as dictionary.

    Parameters
    ----------
    config: dict
       Configuration dictionary from which to extract load interval.

    Returns
    -------
    load_interval: int
       Extracted load interval value.

    """
    return config.load_settings_interval


def get_fuel_level_limit(config):
    """Extract fuel level limit.

    Extract fuel level limit value from configuration passed as dictionary.

    Parameters
    ----------
    config: dict
       Configuration dictionary from which to extract fuel level limit.

    Returns
    -------
    fuel_level_limit: int
       Extracted fuel level limit value.

    """
    return config.fuel_settings_level_limit


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
        ----
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
                FUEL_SETTINGS: {
                    LEVEL_LIMIT: 200, MODE: "SIMULATOR", INTERVAL: 20}, TEMP_SETTINGS: {
                    INTERVAL: 20, MODE: "SIMULATOR"}, LOAD_SETTINGS: {
                    INTERVAL: 20, MODE: "SIMULATOR"}, SERVER_URL: "", MQTT_BROKER: {
                    USERNAME: "", PASSWORD: ""
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
        -------
            temp_mode: str
        """
        return self.config[TEMP_SETTINGS][MODE]

    @property
    def load_mode(self):
        """
        Load mode. Indicates the source of the load data.

        Returns:
        -------
            load_mode: str
        """
        return self.config[LOAD_SETTINGS][MODE]

    @property
    def fuel_mode(self):
        """
        Fuel mode. Indicates the source of the fuel data.

        Returns:
        -------
            fuel_mode: str
        """
        return self.config[FUEL_SETTINGS][MODE]

    @property
    def can_interface(self):
        """
        CAN interface name.

        Returns:
        -------
            interface: str
        """
        return self.config[CAN_GENERAL_SETTINGS][INTERFACE]

    @property
    def can_channel(self):
        """
        CAN channel name.

        Returns:
        -------
            channel: str
        """
        return self.config[CAN_GENERAL_SETTINGS][CHANNEL]

    @property
    def can_bitrate(self):
        """
        CAN bitrate

        Returns:
        -------
            bitrate: int
        """
        return self.config[CAN_GENERAL_SETTINGS][BITRATE]

    @property
    def mqtt_broker_username(self):
        """
        MQTT broker client username

        Returns:
        -------
            username: str
        """
        return self.config[MQTT_BROKER][USERNAME]

    @property
    def mqtt_broker_password(self):
        """
        MQTT broker client password

        Returns:
        -------
            password: str
        """
        return self.config[MQTT_BROKER][PASSWORD]

    @property
    def mqtt_broker_address(self):
        """
        MQTT broker client address

        Returns:
        -------
            address: str
        """
        return self.config[MQTT_BROKER][ADDRESS]

    @property
    def mqtt_broker_port(self):
        """
        MQTT broker client port

        Returns:
        -------
            port: int
        """
        return self.config[MQTT_BROKER][PORT]

    @property
    def server_url(self):
        """
        Cloud service URL

        Returns:
        -------
            server_url: str
        """
        return self.config[SERVER_URL]

    @property
    def iot_username(self):
        """
        IoT device username

        Returns:
        -------
            username: str
        """
        return self.config[USERNAME]

    @property
    def iot_password(self):
        """
        IoT device password

        Returns:
        -------
            password: str
        """
        return self.config[PASSWORD]

    @property
    def api_key(self):
        """
        Cloud service API key

        Returns:
        -------
            api_key: str
        """
        return self.config[API_KEY]

    @property
    def server_time_format(self):
        """
        Cloud service time format

        Returns:
        -------
            server_time_format: str
        """
        return self.config[SERVER_TIME_FORMAT]

    @property
    def auth_interval(self):
        """
        Interval for cloud service authentication attempts

        Returns:
        -------
            interval: int
        """
        return self.config[AUTH_INTERVAL]

    @property
    def temp_settings_interval(self):
        """
        Interval for sending temperature messages

        Returns:
        -------
            temperature_interval: int
        """
        return self.config[TEMP_SETTINGS][INTERVAL]

    @property
    def load_settings_interval(self):
        """
        Interval for sending load messages

        Returns:
        -------
            load_interval: int
        """
        return self.config[LOAD_SETTINGS][INTERVAL]

    @property
    def fuel_settings_interval(self):
        """
        Interval for sending fuel messages

        Returns:
        -------
            fuel_interval: int
        """
        return self.config[FUEL_SETTINGS][INTERVAL]

    @property
    def time_format(self):
        """
        Time format

        Returns:
        -------
            time_format: str
        """
        return self.config[TIME_FORMAT]

    @property
    def fuel_settings_level_limit(self):
        """
        Fuel level limit

        Returns:
        -------
            fuel_level_limit: int
        """
        return self.config[FUEL_SETTINGS][LEVEL_LIMIT]

    @property
    def gateway_cloud_broker_iot_username(self):
        """
        Gateway cloud MQTT broker username

        Returns:
        -------
            username: str
        """
        return self.config[GATEWAY_CLOUD_BROKER][USERNAME]

    @property
    def gateway_cloud_broker_iot_password(self):
        """
        Gateway cloud MQTT broker password

        Returns:
        -------
            password: str
        """
        return self.config[GATEWAY_CLOUD_BROKER][PASSWORD]

    @property
    def gateway_cloud_broker_address(self):
        """
        Gateway cloud MQTT broker address

        Returns:
        -------
            address: str
        """
        return self.config[GATEWAY_CLOUD_BROKER][ADDRESS]

    @property
    def gateway_cloud_broker_port(self):
        """
        Gateway cloud MQTT broker port

        Returns:
        -------
            port: int
        """
        return self.config[GATEWAY_CLOUD_BROKER][PORT]

    @property
    def temp_settings(self):
        """
        Temperature settings

        Returns:
        -------
            temp_settings: str
        """
        return self.config[TEMP_SETTINGS]

    @property
    def load_settings(self):
        """
        Load settings

        Returns:
        -------
            load_settings: str
        """
        return self.config[LOAD_SETTINGS]

    @property
    def fuel_settings(self):
        """
        Fuel settings

        Returns:
        -------
            fuel_settings: str
        """
        return self.config[FUEL_SETTINGS]

    @temp_settings.setter
    def temp_settings(self, temp_settings_set):
        """
        Setter for temperature settings

        Args:
        ----
            temp_settings_set: str
                New temperature settings
        """
        self.config[TEMP_SETTINGS] = temp_settings_set

    @load_settings.setter
    def load_settings(self, load_settings_set):
        """
        Setter for load settings

        Args:
        ----
            load_settings_set: str
                 New load settings
        """
        self.config[LOAD_SETTINGS] = load_settings_set

    @fuel_settings.setter
    def fuel_settings(self, fuel_settings_set):
        """
        Setter for fuel settings

        Args:
        ----
            fuel_settings_set: str
                New fuel settings
        """
        self.config[FUEL_SETTINGS] = fuel_settings_set

    @property
    def rest_api_host(self):
        """
        Gateway REST API hostname

        Returns:
        -------
            hostname: str
        """
        return self.config[REST_API][HOST]

    @property
    def rest_api_port(self):
        """
        Gateway REST API port

        Returns:
        -------
            port: int
        """
        return self.config[REST_API][PORT]
