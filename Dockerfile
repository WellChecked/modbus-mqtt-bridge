FROM python:3.10
LABEL maintainer="SEQTEK <hankhaines@seqtek.com>"

EXPOSE 502

RUN mkdir -p /app/app
RUN mkdir -p /app/config

COPY requirements.txt /app
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --no-cache-dir -r /app/requirements.txt && rm -rf /root/.cache/pip/*

COPY app/ /app/app
COPY config/ /app/config
COPY main.py /app
COPY bridge.py /app
COPY bridge-test_data.py /app

WORKDIR /app

CMD [ "python3", "main.py" ]