FROM python:3

WORKDIR /app

COPY src/requirements.txt ./
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY src/apcupsd-mqtt.py ./

CMD ["python", "/app/apcupsd-mqtt.py"]
