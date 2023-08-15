import requests
import base64

def login(username,password,url):
    # creating base64 encoded username:password token for basic auth
    basic_auth="Basic "+(base64.b64encode((username+":"+password).encode("ascii")).decode("ascii"))
    try:
        login_req=requests.get(url,
                               headers={"Authorization":basic_auth})
        # print("Login status: ",login_req.status_code)
        # print("Login response: ",login_req.text)
        return login_req.text if login_req.status_code==200 else None
    except:
        return None

#sends also device's time format
def register(username,password,time_format,url):
    try:
        login_req=requests.post(url,
                               params={"username":username,"password": password, "time_format": time_format},
                                )
        # print("Signup status: ",login_req.status_code)
        # print("Signup response: ",login_req.text)
        return (login_req.text if login_req.status_code == 200 else None)
    except:
        return None
