FROM openjdk:17.0.2-slim
WORKDIR /app
RUN mkdir /logs
COPY app-files/logback.xml .
COPY app-files/iot-cloud-platform-0.0.1-SNAPSHOT.jar ./app.jar

ENTRYPOINT ["java","-jar","app.jar"]