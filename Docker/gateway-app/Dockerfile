FROM python:3.11

COPY ./requirements.txt ./dependencies.txt
RUN pip install -r dependencies.txt
ADD src/ ./app/
WORKDIR /app


CMD ["python", "app.py"]