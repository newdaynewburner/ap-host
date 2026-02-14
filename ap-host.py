#!/usr/bin/env python3

"""
ap-host.py

AP host component for rouge access point
"""

import os
import sys
import logging
import configparser
from lib import api
from lib.exceptions import *

def main(config, logger):
    """ Main function. Controls program execution
    """
    logger.info(f"[AP Host] Starting the AP host service. DBus API is com.ap-host.APHost")
    dbus_api = api.init_dbus_api()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        logger.info(f"[AP Host] Keyboard interupt recieved, stopping AP host service now")
        return None


# Begin execution
if __name__ == "__main__":
    # Read the configuration file
    config = configparser.ConfigParser()
    config.read(sys.argv[1])

    # Set up the logger
    if bool(config["AP"]["log_file"]):
        log_file = config["AP"]["log_file"]
        if "~" in log_file:
            log_file = os.path.expanduser(log_file)
        if not os.path.isdir(os.path.split(log_file)[0]):
            os.makedirs(os.path.split(log_file)[0])
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s",
            logfile=log_file
        )
    else:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
    logger = logging.getLogger()

    # Enter the main function
    main(config, logger)

    # Start the DBus API
    dbus_api = api.init_dbus_api()





