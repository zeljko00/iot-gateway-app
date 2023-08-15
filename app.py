import json
import auth
import time
import sensor_devices
from multiprocessing import Process,Queue
import data_service

conf_path="app_conf.json"
username_label="username"
password_label="password"
server_url="server_url"
auth_interval="auth_interval"
time_format="time_format"
server_time_format="server_time_format"
fuel_level_limit="fuel_level_limit"
temp_interval="temp_interval"
load_interval="load_interval"

# reading app configuration from json file
def read_conf():
    try:
        conf_file=open(conf_path)
        conf=json.load(conf_file)
        return conf
    except:
        return None
#periodically requesting device signup, returns received jwt
def signup_periodically(username,password,server_time_format,url,interval):
    jwt=None
    while jwt==None:
        jwt=auth.register(username,password,server_time_format,url)
        time.sleep(interval)
    return jwt




def main():
    # stubs
    temp_data = Queue()
    load_data = Queue()
    fuel_data = Queue()
    Process(target=sensor_devices.test, args=(temp_data,load_data,fuel_data)).start()
    time.sleep(6)
    #read app config
    config=read_conf()
    #if config is read successfully, start app logic
    if config!=None:
        #iot cloud platform login
        jwt=auth.login(config[username_label],config[password_label],config[server_url]+"/auth/login")
        #if failed, periodically request signup
        if jwt==None:
            jwt=signup_periodically(config[username_label],config[password_label],config[server_time_format],config[server_url]+"/auth/signup",config[auth_interval])
        # now JWT required for Cloud platform auth is stored in jwt var
        print(jwt)

    else:
        print("Can't read app config file!")

if __name__ == '__main__':
    main()