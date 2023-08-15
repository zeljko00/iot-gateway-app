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

#iot data aggregation and forwarding to cloud
def collect_temperature_data(interval,queue, url, jwt, time_format):
    while True:
        data=[]
        while not queue.empty():
            data.append(queue.get())
        # send request to Cloud only if there is availaable data
        line = ""
        for i in data:
            line += str(i.value)+"  "
        print("Temperature data read from queue: ", line)
        if len(data)>0:
            # if data is not sent to cloud, it is returned to queue
            if not data_service.handle_temperature_data(data,url,jwt,time_format):
                for i in data:
                    queue.put(i)
        time.sleep(interval)

def collect_load_data(interval,queue, url, jwt, time_format):
    while True:
        data=[]
        while not queue.empty():
            data.append(queue.get())
        # send request to Cloud only if there is available data
        line=""
        for i in data:
            line+=str(i.value)+"  "
        print("Load data read from queue: ",line)
        if len(data)>0:
            # if data is not sent to cloud, it is returned to queue
            if not data_service.handle_load_data(data,url,jwt,time_format):
                for i in data:
                    queue.put(i)
        time.sleep(interval)

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
        # temperature data handling
        temperature_data_handler = Process(target=collect_temperature_data, args=(config[temp_interval],temp_data,config[server_url]+"/data/temp",jwt,config[time_format]))
        temperature_data_handler.start()
        load_data_handler = Process(target=collect_load_data, args=(
        config[load_interval], load_data, config[server_url] + "/data/load", jwt, config[time_format]))
        load_data_handler.start()

    else:
        print("Can't read app config file!")

if __name__ == '__main__':
    main()