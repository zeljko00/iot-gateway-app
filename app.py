import json

conf_path="app_conf.json"

# reading app configuration from json file
def read_conf():
    try:
        conf_file=open(conf_path)
        conf=json.load(conf_file)
        return conf
    except:
        return None
