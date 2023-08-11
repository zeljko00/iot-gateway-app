import requests
import base64

def login(username,password,register,url):
    # creating base64 encoded form of username:password for basih auth
    basic_auth="Basic "+(base64.b64encode((username+":"+password).encode("ascii")).decode("ascii"))
    print(basic_auth)
    login_req=requests.get(url,
                           headers={"Authorization":basic_auth})
    print(login_req.status_code)

login("zex","pass",True,"")
