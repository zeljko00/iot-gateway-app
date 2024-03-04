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
    return config.get_temp_settings_interval()


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
    return config.get_load_settings_interval()


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
    return config.get_fuel_settings_level_limit()


class Config:
    """Class for managing configuration.

    Attributes
    ----------
    path: str
       Configuration file path.
    config: dict
       Configuration as dictionary.
    error_logger: logging.Logger
       Error logger for configuration management.
    custom_logger: logging.Logger
       Custom logger for configuration management.

    """

    def __init__(self, path, error_logger=None, custom_logger=None):
        """Create object for configuration management.

        Parameters
        ----------
        path: str
           Configuration file path.
        error_logger: logging.Logger
           Error logger for configuration management.
        custom_logger: logging.Logger
           Custom logger for configuration management.

        """
        self.path = path
        self.config = None
        self.error_logger = error_logger
        self.custom_logger = custom_logger

    def try_open(self):
        """Read configuration.

        Try reading configuration and storing it as a dictionary.
        If it fails, fill up dictionary with predefined values.

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
                    LEVEL_LIMIT: 200, MODE: "SIMULATOR"}, TEMP_SETTINGS: {
                    INTERVAL: 20, MODE: "SIMULATOR"}, LOAD_SETTINGS: {
                    INTERVAL: 20, MODE: "SIMULATOR"}, SERVER_URL: "", MQTT_BROKER: {
                    USERNAME: "", PASSWORD: ""
                }}

    def get_temp_mode(self):
        """Get temperature mode.

        Returns
        -------
        temperature_mode: str
           Read temperature mode.

        """
        return self.config[TEMP_SETTINGS][MODE]

    def get_load_mode(self):
        """Get load mode.

        Returns
        -------
        load_mode: str
           Read load mode.

        """
        return self.config[LOAD_SETTINGS][MODE]

    def get_fuel_mode(self):
        """Get fuel mode.

        Returns
        -------
        fuel_mode: str
           Read fuel mode.

        """
        return self.config[FUEL_SETTINGS][MODE]

    def get_can_interface(self):
        """Get CAN interface.

        Returns
        -------
        can_interface: str
           Read CAN interface.

        """
        return self.config[CAN_GENERAL_SETTINGS][INTERFACE]

    def get_can_channel(self):
        """Get CAN channel.

        Returns
        -------
        can_channel: str
           Read CAN channel.

        """
        return self.config[CAN_GENERAL_SETTINGS][CHANNEL]

    def get_can_bitrate(self):
        """Get CAN bitrate.

        Returns
        -------
        can_bitrate: int
           Read CAN bitrate.

        """
        return self.config[CAN_GENERAL_SETTINGS][BITRATE]

    def get_mqtt_broker_username(self):
        """Get gateway-peripherals broker username.

        Returns
        -------
        broker_username: str
           Read broker username.

        """
        return self.config[MQTT_BROKER][USERNAME]

    def get_mqtt_broker_password(self):
        """Get gateway-peripherals broker password.

        Returns
        -------
        broker_password: str
           Read broker password.

        """
        return self.config[MQTT_BROKER][PASSWORD]

    def get_mqtt_broker_address(self):
        """Get gateway-peripherals broker addres.

        Returns
        -------
        broker_address: str
           Read broker address.

        """
        return self.config[MQTT_BROKER][ADDRESS]

    def get_mqtt_broker_port(self):
        """Get gateway-peripherals broker port.

        Returns
        -------
        broker_port: int
           Read broker port.

        """
        return self.config[MQTT_BROKER][PORT]

    def get_server_url(self):
        """Get cloud server url.

        Returns
        -------
        cloud_url: str
           Read cloud url.

        """
        return self.config[SERVER_URL]

    def get_iot_username(self):
        """Get iot device username.

        Returns
        -------
        iot_username: str
           Read username.

        """
        return self.config[USERNAME]

    def get_iot_password(self):
        """Get iot device password.

        Returns
        -------
        iot_password: str
           Read password.

        """
        return self.config[PASSWORD]

    def get_api_key(self):
        """Get cloud server api key.

        Returns
        -------
        api_key: str
           Read api_key.

        """
        return self.config[API_KEY]

    def get_server_time_format(self):
        """Get cloud time format.

        Returns
        -------
        time_format: str
           Read time format.

        """
        return self.config[SERVER_TIME_FORMAT]

    def get_auth_interval(self):
        """Get cloud authentication interval.

        Returns
        -------
        auth_interval: int
           Read auth interval.

        """
        return self.config[AUTH_INTERVAL]

    def get_temp_settings_interval(self):
        """Get temperature settings interval.

        Returns
        -------
        temp_interval: str
           Read temperature interval.

        """
        return self.config[TEMP_SETTINGS][INTERVAL]

    def get_load_settings_interval(self):
        """Get load settings interval.

        Returns
        -------
        load_interval: str
           Read load interval.

        """
        return self.config[LOAD_SETTINGS][INTERVAL]

    def get_time_format(self):
        """Get gateway time format.

        Returns
        -------
        time_format: str
           Read time format.

        """
        return self.config[TIME_FORMAT]

    def get_fuel_settings_level_limit(self):
        """Get fuel settings level limit.

        Returns
        -------
        fuel_level_limit: str
           Read fuel level limit.

        """
        return self.config[FUEL_SETTINGS][LEVEL_LIMIT]

    def get_gateway_cloud_broker_iot_username(self):
        """Get gateway-cloud broker username.

        Returns
        -------
        username: str
           Read username.

        """
        return self.config[GATEWAY_CLOUD_BROKER][USERNAME]

    def get_gateway_cloud_broker_iot_password(self):
        """Get gateway-cloud broker password.

        Returns
        -------
        password: str
           Read password.

        """
        return self.config[GATEWAY_CLOUD_BROKER][PASSWORD]

    def get_gateway_cloud_broker_address(self):
        """Get gateway-cloud broker address.

        Returns
        -------
        address: str
           Read address.

        """
        return self.config[GATEWAY_CLOUD_BROKER][ADDRESS]

    def get_gateway_cloud_broker_port(self):
        """Get gateway-cloud broker port.

        Returns
        -------
        port: int
           Read port.

        """
        return self.config[GATEWAY_CLOUD_BROKER][PORT]

    def get_temp_settings(self):
        """Get temperature settings.

        Returns
        -------
        temp_settings: dict
           Read temperature settings.

        """
        return self.config[TEMP_SETTINGS]

    def get_load_settings(self):
        """Get load settings.

        Returns
        -------
        load_settings: dict
           Read load settings.

        """
        return self.config[LOAD_SETTINGS]

    def get_fuel_settings(self):
        """Get fuel settings.

        Returns
        -------
        fuel_settings: dict
           Read fuel settings.

        """
        return self.config[FUEL_SETTINGS]

    def set_temp_settings(self, temp_settings_set):
        """Set temp settings.

        Parameters
        ----------
        temp_settings_set: dict
           New temperature settings value.

        """
        self.config[TEMP_SETTINGS] = temp_settings_set

    def set_load_settings(self, load_settings_set):
        """Set load settings.

        Parameters
        ----------
        load_settings_set: dict
           New load settings value.

        """
        self.config[LOAD_SETTINGS] = load_settings_set

    def set_fuel_settings(self, fuel_settings_set):
        """Set fuel settings.

        Parameters
        ----------
        fuel_settings_set: dict
           New fuel settings value.

        """
        self.config[FUEL_SETTINGS] = fuel_settings_set

    def get_rest_api_host(self):
        """Get gateway rest api host.

        Returns
        -------
        rest_api_host: str
           Read rest api host.

        """
        return self.config[REST_API][HOST]

    def get_rest_api_port(self):
        """Get gateway rest api post.

        Returns
        -------
        rest_api_host: int
           Read rest api port.

        """
        return self.config[REST_API][PORT]
