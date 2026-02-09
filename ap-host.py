#!/usr/bin/env python3

"""
ap-host.py

AP host component for rouge access point
"""

import os
import sys
import logging
import configparser
import subprocess
from lib.datatypes import HostapdConfigurationFileHandler
from lib.exceptions import *

class ComponentAPHost(object):
    """ Access point host controller
    """

    def __init__(self, config=None, logger=None):
        """ Initialize the object
        """
        self.config = config
        self.logger = logger
        self.hostapd_process = None

    def generate_configuration(self):
        """ Generate the hostapd configuration file
        """

        # Initialize a new HostapdConfigurationFileHandler object and generate the hostapd config file
        hostapd_config_file_handler = HostapdConfigurationFileHandler(config=self.config, logger=self.logger)
        hostapd_config_file = hostapd_config_file_handler.generate_hostapd_config_file()

        # Return the new filepath
        return hostapd_config_file

    def start(self, hostapd_config_file):
        """ Start hostapd and monitor the process
        """
        try:
            self.hostapd_process = subprocess.Popen(
                [self.config["AP"]["hostapd_executable"], hostapd_config_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            return True
        except Exception as err_msg:
            self.logger.error(f"[AP Host] Encountered an exception when trying to start hostapd! Error message: {err_msg}")
            raise FailedToStartHostapdError(f"Encountered an exception when trying to start hostapd! Error message: {err_msg}")

    def stop(self):
        """ Stop hostapd
        """
        self.hostapd_process.terminate()
        try:
            self.hostapd_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.hostapd_process.kill()
            self.hostapd_process.wait()
        return None

# Begin execution
if __name__ == "__main__":
    # Read the configuration file
    config = configparser.ConfigParser()
    config.read(sys.argv[1])

    # Set up the logger
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger()
    logger.info(f"[AP Host] Initializing AP host component...")

    # Genetate the hostapd configuration file and start the AP host
    ap_host = ComponentAPHost(config=config, logger=logger)
    hostapd_config_file = ap_host.generate_configuration()
    logger.info(f"[AP Host] Generated hostapd config file at '{hostapd_config_file}'")
    ap_host.start(hostapd_config_file)
    logger.info(f"[AP Host] Started hostapd subprocess, AP host is now running")

    # Run until CTRL-C recieved
    try:
        while True:
            pass
    except KeyboardInterrupt:
        logger.info(f"[AP Host] Keyboard interupt recieved, stopping AP host now.")
        ap_host.stop()



