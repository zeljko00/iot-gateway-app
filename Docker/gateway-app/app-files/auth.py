import requests
import base64
import logging.config

logging.config.fileConfig('logging.conf')
errorLogger = logging.getLogger('customErrorLogger')
http_not_found = 404
http_ok = 200

def login(username,password,url):
    # creating base64 encoded username:password token for basic auth
    basic_auth = "Basic "+(base64.b64encode((username+":"+password).encode("ascii")).decode("ascii"))
    try:
        login_req = requests.get(url, headers={"Authorization":basic_auth})
        # print("Login status: ",login_req.status_code)
        # print("Login response: ",login_req.text)
        if login_req.status_code == http_ok:
            return login_req.text
        else:
            errorLogger.error("Problem with auth Cloud service! - Http status code: " + str(login_req.status_code))
            return None
    except:
        errorLogger.error("Authentication Cloud service cant be reached!")
        return None

def check_jwt(jwt,url):
    try:
        login_req = requests.get(url, headers={"Authorization": "Bearer " + jwt})
        if login_req.status_code != http_ok:
            errorLogger.error("Jwt has expired!")
        return login_req.status_code
    except:
        errorLogger.error("Jwt check Cloud service cant be reached!")
        return http_not_found


# sends also device's time format
def register(key, username, password, time_format, url):
    try:
        login_req = requests.post(url, params={"username": username, "password": password, "time_format": time_format},
                                headers={"Authorization": key})
        # print("Signup status: ",login_req.status_code)
        # print("Signup response: ",login_req.text)
        if login_req.status_code == http_ok:
            return login_req.text
        else:
            errorLogger.error("Problem with auth Cloud service! - Http status code: " + str(login_req.status_code))
            return None
    except:
        errorLogger.error("Authentication Cloud service cant be reached!")
        return None
