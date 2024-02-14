## Prerequisites
 - Pyton3 (recommended version 3.11)
 - Install docker-compose [https://docs.docker.com/compose/install/]
 - run `pip install -r requirements.txt` (in order not to have errors in IDE, and for plain run)

## Running:
 - location: Project's root folder
### With docker container
 - build container: ```docker build -t iot-gateway -f .\Docker\gateway-app\Dockerfile .```
 - run container: ``` docker run ...```
 - run docker compose:
   - ```docker.exe compose -f .\Docker\system\docker-compose.yaml -p system up -d iot-gateway```
### Plain run
 - ```python ./src/app.py``` - not finished yet
 
## Developer Documentation
    docs/output/index.html
