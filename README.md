# Home_Monitoring

This repository contains all codes related to monitoring and controlling my home environment with the help of Raspberry 
Pis, which includes : 
* Monitor temperature and luminosity;
* Controls TV through android phone from anywhere in the house using a RabbitMQ server to send messages inside the 
network and a Raspberry Pis located next to the TV with an infrared emitter to actually send the instructions.
  
  Future plans : 
  * Extend this to control the lights (also Infrared controlled) : missing android-part
  * Extend this to control aircon system in the house : aircon remote control signal decryption (phase 1) finished.
  * Add iPhone control instead of Android-only : not started.

* Ensures that hardware failure in the Raspberry will not result in data loss with daily automated backups to a mounted
USB

The repository also contains small side projects that were either partially relevant to the main one, or completely 
separate from it : 
* Create a PC GUI interface (Python TKinter) to control the aircon, to make sure sending signals was working before 
moving on the the Android app phase.
* Go through a Facebook-generated (.htm) message history (contain all of a person's conversation history) and return
messages sent by a given individual and contain a given substring.

The following sections detail a bit more the different folders in this repository.

### android_remote

Creates the whole android-GUI to send instruction to a RabbitMQ server.

Only contain the TV remote controls in the current phase. No work has been made on whether the connexion drops or 
anything so the app might crash easily.

Future plans : 
  * Add support for remotes other than the TV : not started.
  * Improve code stability : not started.
  * Remove hard-coded parameters for RabbitMQ connection and replace it by a log-in screen : not started.

### bash

Contains bash-script and data files put in the raspberry pi that relate to pure OS commands.

This includes :
   * All files for the self-backing up of the Pi. (cron job, shell script, config file)
   * The rc.local file to get see what is run on launch.

Future plans : None for now.

### configs

Contains all configuration file use by the Pi for its various purposes.

This includes : 
   * All .conf files used by lirc (Linux Infrared Remote Control) to send infra-red signals.
   * Configuration file to connect to RabbitMQ server.
   * Configuration file listing sensor (temperature, luminosity, ...) connected to Pi, for environment monitoring.

### data

Contains some output files to give examples for using some of the scripts from other folders. Currently includes files
to show how python/miscellaneous/convert_aircon_ir.py works.

### iOS_remote (not started)

Creates iOS interface to send Infrared command.

### python

All python scripts use through this projects.

##### global_libraries

Contains all relatively-general functions used by the other python scripts. This includes : 
* Drivers for all of the supported sensors (luminosity, temperature) that have been implemented.
* Code to handle interaction with RabbitMQ server (initiating connection, consuming, publishing, ...)
* Some small fault-tolerant generic functions.
* A logger function that log any warning/message to /var/log/syslog, /var/log/user.log and the command prompt.

##### instruction_gui

Contains a Python GUI to send commands through RabbitMQ. This was made before starting the Android support, to make sure
the expedition, reception and processing of messages was successfull.

##### miscellanous

Contains various scripts that fit in one relatively small python file but did not deserve a folder. Includes : 
* Script that goes through a Facebook-generated (.htm) message history (contain all of a person's conversation history) and return
messages sent by a given individual and contain a given substring.
* Script that converts raw infra-red signals received (sequence of pulse-lengths and space-lengths) into the binary
signals that it should be interpreted as by the aircon. This is in order to analyze which settings of an aircon command 
correspond to which part of the signal, in order to send custom signals.

##### rabbitmq_instructions

Contains all scripts used by the Pi to receive (worker) RabbitMQ messages, and by a Pi or another machine (master)
to send these messages.

* Worker : a worker connects to the server with a given id and consume from a set of queues that match all of its 
supported instructions. One an instruction is received, it processes it and then sends a response back to the server.
All processing of the instructions are instruction_specific and made in worker_config.

* Master : a worker connects to the server and sends instructions (either through the command prompts or though a GUI
that controls it) to the RabbitMQ server, then waits for a response for a given amount of time. All formatting of 
messages and processing of the responses are instruction-specific and located in master_config

##### temperature_normalizing

Contains all scripts to handles sensor data collection, correction, averaging and output for my house.

All sensors are connected to GPIO pins of a Raspberry Pi.
Sensor currently supported by this code are DHT11, BME280 (I2C), DS18B20 (One-wire), TSL2561 (Luminosity I2C) and 
Sensehat.

For outputting of value, aside from creating files in the Raspberry Pi file system, the data is also sent online to a 
ThingSpeak page.

