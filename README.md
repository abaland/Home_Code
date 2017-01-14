# Home_Monitoring

####temperature_normalizing

This is a code to handles sensor data collection, correction, averaging and output for my house.
All sensors are connected to GPIO pins of a Raspberry Pi.
Sensor currently supported by this code are DHT11, BME280 (I2C), DS18B20 (One-wire), TSL2561 (Luminosity I2C) and Sensehat.

For outputting of value, aside from creating files i nthe Raspberry Pi file system, the data can also be sent online, but
the online supported website at the moment is ThingSpeak.

####global_libraries
Contains all necessary functions to collect measurements from these sensors, as
well as a function that handles all error logging to /var/log/syslog, and more generic functions

####rabbitmq_instructions
Contains functions to install on the pis (worker) to receive instruction through rabbitmq server.
Currently the code contains remote control for my tv.

####instruction_gui
Creates a remote control GUI to send rabbitmq commands to control tv

####general
Configuration for code is made with a .ini file, following format found in configs/****.ini format.

Do not forget to update the PYTHONPATH to include the folder.