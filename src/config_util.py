"""Configuration utilities."""
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
    observer.schedule(event_handler, path=conf_dir, recursive=False)
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
        conf_file = open(conf_path)
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
        conf_file = open(conf_path, "w")
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
                fuel_settings: {
                    level_limit: 200, mode: "SIMULATOR"}, temp_settings: {
                    interval: 20, mode: "SIMULATOR"}, load_settings: {
                    interval: 20, mode: "SIMULATOR"}, server_url: "", mqtt_broker: {
                    username: "", password: ""
                }}

    def get_temp_mode(self):
        """Get temperature mode.

        Returns
        -------
        temperature_mode: str
           Read temperature mode.

        """
        return self.config[temp_settings][mode]

    def get_load_mode(self):
        """Get load mode.

        Returns
        -------
        load_mode: str
           Read load mode.

        """
        return self.config[load_settings][mode]

    def get_fuel_mode(self):
        """Get fuel mode.

        Returns
        -------
        fuel_mode: str
           Read fuel mode.

        """
        return self.config[fuel_settings][mode]

    def get_can_interface(self):
        """Get CAN interface.

        Returns
        -------
        can_interface: str
           Read CAN interface.

        """
        return self.config[can_general_settings][interface]

    def get_can_channel(self):
        """Get CAN channel.

        Returns
        -------
        can_channel: str
           Read CAN channel.

        """
        return self.config[can_general_settings][channel]

    def get_can_bitrate(self):
        """Get CAN bitrate.

        Returns
        -------
        can_bitrate: int
           Read CAN bitrate.

        """
        return self.config[can_general_settings][bitrate]

    def get_mqtt_broker_username(self):
        """Get gateway-peripherals broker username.

        Returns
        -------
        broker_username: str
           Read broker username.

        """
        return self.config[mqtt_broker][username]

    def get_mqtt_broker_password(self):
        """Get gateway-peripherals broker password.

        Returns
        -------
        broker_password: str
           Read broker password.

        """
        return self.config[mqtt_broker][password]

    def get_mqtt_broker_address(self):
        """Get gateway-peripherals broker addres.

        Returns
        -------
        broker_address: str
           Read broker address.

        """
        return self.config[mqtt_broker][address]

    def get_mqtt_broker_port(self):
        """Get gateway-peripherals broker port.

        Returns
        -------
        broker_port: int
           Read broker port.

        """
        return self.config[mqtt_broker][port]

    def get_server_url(self):
        """Get cloud server url.

        Returns
        -------
        cloud_url: str
           Read cloud url.

        """
        return self.config[server_url]

    def get_iot_username(self):
        """Get iot device username.

        Returns
        -------
        iot_username: str
           Read username.

        """
        return self.config[username]

    def get_iot_password(self):
        """Get iot device password.

        Returns
        -------
        iot_password: str
           Read password.

        """
        return self.config[password]

    def get_api_key(self):
        """Get cloud server api key.

        Returns
        -------
        api_key: str
           Read api_key.

        """
        return self.config[api_key]

    def get_server_time_format(self):
        """Get cloud time format.

        Returns
        -------
        time_format: str
           Read time format.

        """
        return self.config[server_time_format]

    def get_auth_interval(self):
        """Get cloud authentication interval.

        Returns
        -------
        auth_interval: int
           Read auth interval.

        """
        return self.config[auth_interval]

    def get_temp_settings_interval(self):
        """Get temperature settings interval.

        Returns
        -------
        temp_interval: str
           Read temperature interval.

        """
        return self.config[temp_settings][interval]

    def get_load_settings_interval(self):
        """Get load settings interval.

        Returns
        -------
        load_interval: str
           Read load interval.

        """
        return self.config[load_settings][interval]

    def get_time_format(self):
        """Get gateway time format.

        Returns
        -------
        time_format: str
           Read time format.

        """
        return self.config[time_format]

    def get_fuel_settings_level_limit(self):
        """Get fuel settings level limit.

        Returns
        -------
        fuel_level_limit: str
           Read fuel level limit.

        """
        return self.config[fuel_settings][level_limit]

    def get_gateway_cloud_broker_iot_username(self):
        """Get gateway-cloud broker username.

        Returns
        -------
        username: str
           Read username.

        """
        return self.config[gateway_cloud_broker][username]

    def get_gateway_cloud_broker_iot_password(self):
        """Get gateway-cloud broker password.

        Returns
        -------
        password: str
           Read password.

        """
        return self.config[gateway_cloud_broker][password]

    def get_gateway_cloud_broker_address(self):
        """Get gateway-cloud broker address.

        Returns
        -------
        address: str
           Read address.

        """
        return self.config[gateway_cloud_broker][address]

    def get_gateway_cloud_broker_port(self):
        """Get gateway-cloud broker port.

        Returns
        -------
        port: int
           Read port.

        """
        return self.config[gateway_cloud_broker][port]

    def get_temp_settings(self):
        """Get temperature settings.

        Returns
        -------
        temp_settings: dict
           Read temperature settings.

        """
        return self.config[temp_settings]

    def get_load_settings(self):
        """Get load settings.

        Returns
        -------
        load_settings: dict
           Read load settings.

        """
        return self.config[load_settings]

    def get_fuel_settings(self):
        """Get fuel settings.

        Returns
        -------
        fuel_settings: dict
           Read fuel settings.

        """
        return self.config[fuel_settings]

    def set_temp_settings(self, temp_settings_set):
        """Set temp settings.

        Parameters
        ----------
        temp_settings_set: dict
           New temperature settings value.

        """
        self.config[temp_settings] = temp_settings_set

    def set_load_settings(self, load_settings_set):
        """Set load settings.

        Parameters
        ----------
        load_settings_set: dict
           New load settings value.

        """
        self.config[load_settings] = load_settings_set

    def set_fuel_settings(self, fuel_settings_set):
        """Set fuel settings.

        Parameters
        ----------
        fuel_settings_set: dict
           New fuel settings value.

        """
        self.config[fuel_settings] = fuel_settings_set

    def get_rest_api_host(self):
        """Get gateway rest api host.

        Returns
        -------
        rest_api_host: str
           Read rest api host.

        """
        return self.config[rest_api][host]

    def get_rest_api_port(self):
        """Get gateway rest api post.

        Returns
        -------
        rest_api_host: int
           Read rest api port.

        """
        return self.config[rest_api][port]
