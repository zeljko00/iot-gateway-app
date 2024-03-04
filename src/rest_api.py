"""Rest api utilities.

rest_api
========
Module that contains simple gateway rest api server.

Classes
-------

FuelSettings
    Class representing fuel settings relevant for requests from cloud dashboard.
TempSettings
    Class representing temp settings relevant for requests from cloud dashboard.
LoadSettings
    Class representing load settings relevant for requests from cloud dashboard.
FluidConfig
    Class representing part of configuration that can be changed.

Functions
---------
start_rest_api
    Defines rest api server endpoints and starts running the server.

Constants
---------

"""
import uvicorn
import logging.config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from config_util import Config, write_conf, TEMP_SETTINGS, LOAD_SETTINGS, FUEL_SETTINGS, CONF_PATH

logging.config.fileConfig('logging.conf')
infoLogger = logging.getLogger('customInfoLogger')
errorLogger = logging.getLogger('customErrorLogger')
customLogger = logging.getLogger('customConsoleLogger')


class FuelSettings(BaseModel):
    """Class representing fuel settings that can be received.

    Attributes
    ----------
    level_limit: int
       Fuel level limit.
    mode: str
       Fuel sensor mode of operation.

    """

    level_limit: int
    mode: str


class TempSettings(BaseModel):
    """Class representing temp settings that can be received.

    Attributes
    ----------
    interval: int
       Temperature interval.
    mode: str
       Temperature sensor mode of operation.

    """

    interval: int
    mode: str


class LoadSettings(BaseModel):
    """Class representing load settings that can be received.

    Attributes
    ----------
    interval: int
       Load interval.
    mode: str
       Load sensor mode of operation.

    """

    interval: int
    mode: str


class FluidConfig(BaseModel):
    """Wrapper class for all configuration options that are subject to change.

    This class is used for the possible case where transferred information contains
    parts subject to change and those that must not change.

    Attributes
    ----------
    fuel_settings: FuelSettings
       Fuel settings.
    temp_settings: TempSettings
       Fuel settings.
    load_settings: LoadSettings
       Fuel settings.

    """

    fuel_settings: FuelSettings
    temp_settings: TempSettings
    load_settings: LoadSettings


def start_rest_api(host, port):
    """Start gateway rest api server.

    Setup properties and endpoints and start simple gateway rest api server.

    Parameters
    ----------
    host: str
       Rest api host.
    port: int
       Rest api port.

    """
    app = FastAPI()

    origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/config/")
    async def config_get():
        try:
            config = Config(CONF_PATH)
            config.try_open()
            return {TEMP_SETTINGS: config.temp_settings,
                    LOAD_SETTINGS: config.load_settings,
                    FUEL_SETTINGS: config.fuel_settings, }
        except BaseException:
            return None

    @app.put("/config/")
    @app.post("/config/")
    async def config_post(fluid_config: FluidConfig):
        try:
            config = Config(CONF_PATH, errorLogger, customLogger)
            config.try_open()
            config.fuel_settings(jsonable_encoder(fluid_config.fuel_settings))
            config.temp_settings(jsonable_encoder(fluid_config.temp_settings))
            config.load_settings(jsonable_encoder(fluid_config.load_settings))
            config.write()
            return {TEMP_SETTINGS: config.temp_settings,
                    LOAD_SETTINGS: config.load_settings,
                    FUEL_SETTINGS: config.fuel_settings, }
        except BaseException:
            return None

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    config = Config(CONF_PATH, errorLogger, customLogger)
    config.try_open()
    start_rest_api(config.rest_api_host, config.rest_api_port)
