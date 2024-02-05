import contextlib
import time
import threading
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from config_util import *

class FuelSettings(BaseModel):
    level_limit: int
    mode: str


class TempSettings(BaseModel):
    interval: int
    mode: str


class LoadSettings(BaseModel):
    interval: int
    mode: str


class FluidConfig(BaseModel):
    fuel_settings: FuelSettings
    temp_settings: TempSettings
    load_settings: LoadSettings

def start_rest_api(host, port):
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
            config = read_conf()
            return { temp_settings: config[temp_settings],
                     load_settings: config[load_settings],
                     fuel_settings: config[fuel_settings], }
        except:
            return None

    @app.put("/config/")
    @app.post("/config/")
    async def config_post(fluid_config: FluidConfig):
        try:
            config = read_conf()
            config[fuel_settings] = jsonable_encoder(fluid_config.fuel_settings)
            config[temp_settings] = jsonable_encoder(fluid_config.temp_settings)
            config[load_settings] = jsonable_encoder(fluid_config.load_settings)
            write_conf(config)
            return { temp_settings: config[temp_settings],
                     load_settings: config[load_settings],
                     fuel_settings: config[fuel_settings], }
        except:
            return None

    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    config = read_conf()
    start_rest_api(config['rest_api']['host'], config['rest_api']['port'])
