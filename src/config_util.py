import json
from multiprocessing import Event
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver
from watchdog.observers.inotify import InotifyObserver
from watchdog.events import FileSystemEventHandler

conf_dir = './configuration'
conf_path = conf_dir + "/app_conf.json"

temp_settings = 'temp_settings'
load_settings = 'load_settings'
fuel_settings = 'fuel_settings'


class ConfFlags:
    def __init__(self):
        self.fuel_flag = Event()
        self.temp_flag = Event()
        self.load_flag = Event()

    def set_all(self):
        self.fuel_flag.set()
        self.temp_flag.set()
        self.load_flag.set()


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
    return config[temp_settings]['interval']


def get_load_interval(config):
    return config[load_settings]['interval']


def get_fuel_level_limit(config):
    return config[fuel_settings]['level_limit']
