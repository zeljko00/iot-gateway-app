"""Simple gateway rest api server."""
import uvicorn
import logging.config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from config_util import *
conf_dir = './configuration'
conf_path = conf_dir + "/app_conf.json"

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
            config = Config(conf_path)
            config.try_open()
            return {temp_settings: config.get_temp_settings(),
                    load_settings: config.get_load_settings(),
                    fuel_settings: config.get_fuel_settings(), }
        except BaseException:
            return None

    @app.put("/config/")
    @app.post("/config/")
    async def config_post(fluid_config: FluidConfig):
        try:
            config = Config(conf_path, errorLogger, customLogger)  # TODO
            config.try_open()
            config.set_fuel_settings(jsonable_encoder(fluid_config.fuel_settings))
            config.set_temp_settings(jsonable_encoder(fluid_config.temp_settings))
            config.set_load_settings(jsonable_encoder(fluid_config.load_settings))
            write_conf(config)
            return {temp_settings: config.get_temp_settings(),
                    load_settings: config.get_load_settings(),
                    fuel_settings: config.get_fuel_settings(), }
        except BaseException:
            return None

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    config = Config(conf_path, errorLogger, customLogger)
    config.try_open()
    start_rest_api(config.get_rest_api_host(), config.get_rest_api_port())
