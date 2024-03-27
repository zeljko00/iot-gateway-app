## Prerequisites
 - Pyton3 (recommended version 3.11)
 - Install docker-compose [https://docs.docker.com/compose/install/]
 - run `pip install -r requirements.txt` (in order not to have errors in IDE, and for plain run)

## Running:
 - location: Project's root folder
### With docker container
 - For compact run: ```docker-run``` script (for current OS)
 - For manual run:
   - build container: ```docker build -t iot-gateway -f .\Docker\gateway-app\Dockerfile .```
   - create network: ```docker network create iot``` - not needed every time.
   - run container: ```docker run --name iot-gateway -it  --network iot  iot-gateway```
 - run docker compose:
   - ``` bash
     docker.exe compose -f .\Docker\system\docker-compose.yaml -p system up -d iot-gateway
     ```
### Plain run
 ``` bash
   cd src
   python app.py
 ```
  - not finished yet
 
## Developer Documentation
    docs/output/index.html

## Testing
Only once:
```commandline
   pip install pytest
   ```
Every time, from root folder:
```commandline
    pytest
```
