"""Authentication utilities.

auth
============
Module that provides functions for iot-gateway authentication on cloud

Functions
---------
login(username,password,url)
    User login with provided credentials.

check_jwt(jwt,url)
    Checks  validity of current jwt.

register(key, username, password, time_format, url)
    Registers new iot-gateway device.
"""

import requests
import base64
import logging.config

logging.config.fileConfig('logging.conf')
errorLogger = logging.getLogger('customErrorLogger')
customLogger = logging.getLogger('customConsoleLogger')

HTTP_NOT_FOUND = 404
HTTP_OK = 200


def login(username, password, url):
    """
    Sign in iot-gateway to its account on cloud platform.

    If login is successful, returns jwt for accessing cloud REST API.

    Parameters
    ----------
    username : str
    password : str
    url: str
         Cloud auth services url.

    Returns
    -------
    jwt: string
        Base64 encoded JSON Web token that contains validity period, role and device username.If register process
        fails, function returns None.
    """
    # creating base64 encoded username:password token for basic auth
    basic_auth = "Basic " + (base64.b64encode((username + ":" + password).encode("ascii")).decode("ascii"))
    try:
        login_req = requests.get(url, headers={"Authorization": basic_auth})
        if login_req.status_code == HTTP_OK:
            return login_req.text
        else:
            errorLogger.error("Problem with auth Cloud service! - Http status code: " + str(login_req.status_code))
            customLogger.critical("Problem with auth Cloud service! - Http status code: " + str(login_req.status_code))
            return None
    except BaseException:
        errorLogger.error("Authentication Cloud service cant be reached!")
        customLogger.critical("Authentication Cloud service cant be reached!")
        return None


def check_jwt(jwt, url):
    """
    Check jwt validity.

    Parameters
    ----------
    jwt : str
        JWT to check.
    url: str
         Cloud auth services url.

    Returns
    -------
    status: int
         Function returns status 0 if JWT is invalid, otherwise returns 1.
    """
    try:
        login_req = requests.get(url, headers={"Authorization": "Bearer " + jwt})
        if login_req.status_code != HTTP_OK:
            errorLogger.error("Jwt has expired!")
        return login_req.status_code
    except BaseException:
        errorLogger.error("Jwt check Cloud service cant be reached!")
        return HTTP_NOT_FOUND


# sends also device's time format
# register requires API key
def register(key, username, password, time_format, url):
    """
    Create new account on cloud platform for iot-gateway device.

    If login is successful, returns jwt for accessing cloud REST API.

    Parameters
    ----------
    key: str
        API key required for creating new account.
    username : str
    password : str
    time_format: str
        Time format used by iot-gateway device.
    url: str
        Cloud auth services' url.

    Returns
    -------
    jwt: string
        Base64 encoded JSON Web token that contains validity period, role and device username. If register process
        fails, function returns None.
    """
    try:
        login_req = requests.post(url, params={"username": username, "password": password, "time_format": time_format},
                                  headers={"Authorization": key})
        if login_req.status_code == HTTP_OK:
            return login_req.text
        else:
            errorLogger.error("Problem with auth Cloud service! - Http status code: " + str(login_req.status_code))
            customLogger.critical("Problem with auth Cloud service! - Http status code: " + str(login_req.status_code))
            return None
    except BaseException:
        errorLogger.error("Authentication Cloud service cant be reached!")
        customLogger.critical("Authentication Cloud service cant be reached!")
        return None
