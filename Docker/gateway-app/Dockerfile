FROM python:3.11

COPY app-files /app
WORKDIR /app

RUN pip install -r dependencies.txt

CMD ["python", "app.py"]