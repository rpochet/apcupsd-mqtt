FROM python:3.9
LABEL org.opencontainers.image.source="https://github.com/andras-tim/apcupsd-mqtt"

WORKDIR /app

COPY src/requirements.txt ./
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY src/apcupsd-mqtt.py ./
COPY src/config.yml ./

CMD ["python", "/app/apcupsd-mqtt.py"]
