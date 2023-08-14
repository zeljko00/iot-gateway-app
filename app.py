import json
import auth
import time

conf_path="app_conf.json"
username_label="username"
password_label="password"
server_url="server_url"
auth_interval="auth_interval"

# reading app configuration from json file
def read_conf():
    try:
        conf_file=open(conf_path)
        conf=json.load(conf_file)
        return conf
    except:
        return None
def signup_periodically(username,password,url,interval):
    jwt=None
    while jwt==None:
        jwt=auth.register(username,password,url)
        time.sleep(interval)
    return jwt

def handle_data(jwt):
    print("handling data")

def main():
    #read app config
    config=read_conf()
    #if config is read successfully, start app logic
    if config!=None:
        #iot cloud platform login
        jwt=auth.login(config[username_label],config[password_label],config[server_url])
        #if failed, periodically request signup
        if jwt==None:
            jwt=signup_periodically(config[username_label],config[password_label],config[server_url],config[auth_interval])
        #now JWT required for Cloud platform authorization is stored in jwt var
        handle_data(jwt)
    else:
        print("Can't read app config file!")

if __name__ == '__main__':
    main()