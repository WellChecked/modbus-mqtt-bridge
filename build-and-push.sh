# build for current platform
docker build -t wcsi/modbus-mqtt-bridge . --push
# Build for windows platform
docker build --platform linux/amd64 -t wcsi/modbus-mqtt-bridge . --push
