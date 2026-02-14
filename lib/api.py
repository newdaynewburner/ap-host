"""
lib/api.py

Contains the DBus API for the AP host
"""

import os
import sys
import subprocess
import threading
from pydbus import SystemBus
from gi.repository import GLib
from . import datatypes
from . import exceptions

BUS_NAME = "com.ap-host.APHost"
OBJECT_PATH = "/com/ap-host/APHost"
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
        <method name="SaveProfile"/>
        <method name="LoadProfile"/>
        <property name="State" type="s" access="read"/>
        <property name="Interface" type="s" access="read"/>
        <property name="ESSID" type="s" access="read"/>
        <property name="Band" type="s" access="read"/>
        <property name="Channel" type="s" access="read"/>
        <property name="Security" type="s" access="read"/>
        <property name="Passphrase" type="s" access="read"/>
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
        self.logger.info(f"[AP Host] Got call on DBus API to Start")
        try:
            self.start()
        except exceptions.StateChangeError as err_msg:
            self.logger.error(f"[AP Host] DBus API encoutered a StateChangeError handling call to Start! Error message:  {err_msg}")
        return None


    def Stop(self):
        """ Stop the AP host
        """
        self.logger.info(f"[AP Host] Got call on DBus API to Stop")
        try:
            self.stop()
        except exceptions.StateChangeError as err_msg:
            self.logger.error(f"[AP Host] DBus API encoutered a StateChangeError handling call to Stop! Error message:  {err_msg}")
        return None

    def Restart(self):
        """ Restart the AP host
        """
        self.logger.info(f"[AP Host] Got call on DBus API to Restart")
        try:
            self.restart()
        except exceptions.StateChangeError as err_msg:
            self.logger.error(f"[AP Host] DBus API encoutered a StateChangeError handling call to Restart! Error message:  {err_msg}")
        return None

    def Configure(self, setting, value):
        """ Configure the AP host
        """
        self.logger.info(f"[AP Host] Got call on DBus API to Configure with arguments: {setting}, {value}")
        try:
            self.configure(setting, value)
        except exceptions.ConfigurationError as err_msg:
            self.logger.error(f"[AP Host] DBus API encountered a ConfigurationError handling call to Configure! Error message: {err_msg}")
        return None

    def SaveProfile(self, name):
        """ Save the current configuration as a profile
        """
        self.logger.info(f"[AP Host] Got call on DBus API to SaveProfile with arguments: {name}")
        self.save_profile(name)
        return None

    def LoadProfile(self, name, start=False):
        """ Load a configuration profile
        """
        self.logger.info(f"[AP Host] Got call on DBuS API to LoadProfile with arguments: {name}, {start}")
        try:
            self.load_profile(name, start=start)
        except exceptions.ConfigurationError as err_msg:
            self.logger.error(f"[AP Host] DBus API encountered a ConfigurationError handling call to LoadProfile! Error message: {err_msg}")
        except exceptions.StateChangeError as err_msg:
            self.logger.error(f"[AP Host] DBus API encountered a StateChangeError handling call to LoadProfile! Error message: {err_nsg}")
        return None

    #######################
    # DBUS API PROPERTIES #
    #######################
    @property
    def State(self):
        return self._state

    @property
    def Interface(self):
        return self.config["AP"]["interface"]

    @property
    def ESSID(self):
        return self.config["AP"]["essid"]

    @property
    def Band(self):
        return self.config["AP"]["band"]

    @property
    def Channel(self):
        return self.config["AP"]["channel"]

    @property
    def Security(self):
        return self.config["AP"]["security"]

    @property
    def Passphrase(self):
        return self.config["AP"]["passphrase"]

def init_dbus_api():
    """ Start the DBus API
    """
    def _start_thread():
        """ API runner thread
        """
        bus = SystemBus()
        bus.publish(BUS_NAME, (OBJECT_PATH, APHostService, INTERFACE_XML))
        GLib.MainLoop().run()

    thread = threading.Thread(target=_start_thread, args=())
    thread.start()
    return None

