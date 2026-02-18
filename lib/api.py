"""
lib/api.py

Contains the DBus API for the AP host
"""

import os
import sys
import subprocess
import threading
import logging
import configparser
from pydbus import SystemBus
from gi.repository import GLib
from . import datatypes
from . import exceptions

BUS_NAME = "com.aphost.APHost"
OBJECT_PATH = "/com/aphost/APHost"
INTERFACE_XML = """
<node>
    <interface name="com.aphost.APHost">
        <method name="Start"/>
        <method name="Stop"/>
        <method name="Restart"/>
        <method name="Configure">
            <arg type="s" name="setting" direction="in"/>
            <arg type="s" name="value" direction="in"/>
        </method>
        <property name="State" type="s" access="read"/>
    </interface>
</node>
"""

class APHostService(datatypes.APHost):
    """ System-level DBus API service
    """

    def __init__(self):
        """ Initialize the object
        """
        self.version = "0.1"
        config = configparser.ConfigParser()
        config.read(sys.argv[1])
        logger = logging.getLogger()
        super().__init__(config=config, logger=logger)

    ####################
    # DBUS API METHODS #
    ####################
    def Start(self):
        """ Start the AP host
        """
        self.logger.info(f"Got call on DBus API to Start")
        try:
            self.start()
        except exceptions.StateChangeError as err_msg:
            self.logger.error(f"DBus API encoutered a StateChangeError handling call to Start! Error message:  {err_msg}")
        return None


    def Stop(self):
        """ Stop the AP host
        """
        self.logger.info(f"Got call on DBus API to Stop")
        try:
            self.stop()
        except exceptions.StateChangeError as err_msg:
            self.logger.error(f"DBus API encoutered a StateChangeError handling call to Stop! Error message:  {err_msg}")
        return None

    def Restart(self):
        """ Restart the AP host
        """
        self.logger.info(f"Got call on DBus API to Restart")
        try:
            self.restart()
        except exceptions.StateChangeError as err_msg:
            self.logger.error(f"DBus API encoutered a StateChangeError handling call to Restart! Error message:  {err_msg}")
        return None

    def Configure(self, setting, value):
        """ Configure the AP host
        """
        self.logger.info(f"Got call on DBus API to Configure with arguments: {setting}, {value}")
        try:
            self.configure(setting, value)
        except exceptions.ConfigurationError as err_msg:
            self.logger.error(f"DBus API encountered a ConfigurationError handling call to Configure! Error message: {err_msg}")
        return None

    #######################
    # DBUS API PROPERTIES #
    #######################
    @property
    def State(self):
        return self.state

def init_dbus_api(name=BUS_NAME, path=OBJECT_PATH, xml=INTERFACE_XML):
    """ Start the DBus API
    """
    bus = SystemBus()
    bus.publish(name, (path, APHostService(), xml))
    GLib.MainLoop().run()
    return None

