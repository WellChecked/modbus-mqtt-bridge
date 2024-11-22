setup(
    name="modbus-mqtt-bridge",
    version="1.0.0",
    description="Modbus to MQTT bridge",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/WellChecked/modbus-mqtt-bridge.git",
    author="WellChecked",
    author_email="hankhaines@wellchecked.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
    packages=[
        "app"
    ],
    include_package_data=True,
    install_requires=[
        "pydantic~=2.10.0",
        "modbus-tcp-server",
        "jsonpath-ng~=1.7.0",
        "paho-mqtt~=2.1.0",
        "numpy~=2.1.3",
        "click~=8.1.7",
        "psutil~=6.1.0"
    ],
    entry_points={"console_scripts": ["wellchecked=bridge.__main__:bridge"]},
)
