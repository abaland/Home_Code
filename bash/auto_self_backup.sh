#!/bin/bash
# script to synchronise Pi files to backup. Adapted from http://raspberrypi.stackexchange.com/a/28087

logger "===================\n= Back up started =\n==================="
FILE="/mnt/usbdrive"
mount

if [[ -r ${FILE} && -w ${FILE} ]]; then

    logger "Backup drive detected"
    rsync -avH --delete-during --delete-excluded --exclude-from=/home/pi/Home_Code/bash/rsync-exclude.txt / /mnt/usbdrive/Pi_Backup
    logger "Finished backup"

else

    logger "Backup drive undetected (or missing permissions)"

fi

