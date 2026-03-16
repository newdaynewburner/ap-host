"""
lib/datatypes.py

Custom datatype definitions
"""

import os
import sys
import subprocess
import configparser
from . import exceptions

class Station(object):
    """ Represents a station device
    """

    def __init__(self, mac_address, station_table, config=None, logger=None):
        """ Initialize the object
        """
        self.config = config
        self.logger = logger
        self.mac_address = mac_address
        self.station_table = station_table
        self.status = "connected"

    def set_status(self, new_status):
        """ Set the status of the station
        """
        if new_status not in ("connected", "disconnected"):
            raise exceptions.StationError(f"Invalid status '{new_status}'!")
        self.status = new_status
        return None

    def block(self):
        """ Block the station
        """
        if self.mac_address in self.station_table.blocked_stations:
            self.logger.warning(f"Station '{self.mac_address}' is already blocked!")
            return None
        # Blocking logic goes here
        self.station_table.blocked_stations.append(self.mac_address)
        return None

    def unblock(self):
        """ Unblock the station
        """
        if self.mac_address not in self.station_table.blocked_stations:
            self.logger.warning(f"Station '{self.mac_address}' is not blocked!")
            return None
        # Unblocking logic goes here
        self.station_table.blocked_stations.remove(self.mac_address)
        return None

    def deauthenticate(self):
        """ Deauthenticate the station
        """
        pass

class StationTable(object):
    """ Holds all accumulated stations
    """

    def __init__(self, config=None, logger=None):
        """ Initialize the object
        """
        self.config = config
        self.logger = logger
        self.stations = []
        self.blocked_stations = []

    def get_station(self, mac_address):
        """ Check if a station exists or not and return it's object if so
        """
        for station in self.stations:
            if station.mac_address == mac_address:
                return station
        return None

    def new_station(self, mac_address):
        """ Create a new station and add it to the list
        """
        if not self.get_station(mac_address):
            s = Station(mac_address, self)
            self.stations.append(s)
            return s
        else:
            raise exceptions.StationTableError(f"Station '{mac_address}' already exists!")

    def list_active(self):
        """ Return a list of all actively connected stations
        """
        l = []
        for station in self.stations:
            if station.status == "connected":
                l.append(station)
        return l

class HostapdConfigurationFileHandler(object):
    """ Contains methods for dynamically generating the configuration
    file for hostapd
    """

    def __init__(self, config=None, logger=None):
        """ Initialize the object
        """
        # Store arguments locally
        self.config = config
        self.logger = logger

        # Validate some frequently misconfigured configuration file settings
        if self.config["AP"]["band"] not in ("a", "b", "g", "bg", "abg"):
            raise Exception(f"The 'band' option in the config must be either 'a', 'b', 'g', or 'ab'!")
        if self.config["AP"]["security"] not in ("open", "wpa2-psk", "wpa3-personal", "wpa2/wpa3"):
            raise Exception(f"Invalid option for 'security' in config! Must be either 'open', 'wpa2-psk', 'wpa3-personal', or 'wpa2/wpa3'!")
        if not self.config["AP"]["passphrase"] and self.config["AP"]["security"] in ("wpa2-psk", "wpa3-personal"):
            raise Exception(f"The 'passphrase' option is required if 'security' is either 'wpa2-psk' or 'wpa3-personal'!")

        # Create the directory for the hostapd configuration file if it does not already exist
        if not os.path.isdir(os.path.split(self.config["AP"]["hostapd_config_file"])[0]):
            os.makedirs(os.path.split(self.config["AP"]["hostapd_config_file"])[0])

    def generate_hostapd_config_file(self, essid, band, channel, security, passphrase):
        """ Dynamically generate the hostapd configuration file
        """

        # Initialize a list to hold configuration file settings
        settings = []

        # Generate the base settings
        for setting in [
            f"interface={self.config['AP']['broadcast_iface']}",
            f"driver={self.config['AP']['driver']}",
            f"ssid={essid}",
            f"hw_mode={band}",
            f"channel={channel}",
            f"ieee80211n=1",
            f"wmm_enabled=1",
            f"auth_algs=1",
            f"ignore_broadcast_ssid=0",
            f"ctrl_interface=/var/run/hostapd",
            f"ctrl_interface_group=0"
        ]:
            settings.append(setting)

        # Generate the security settings for wpa2-psk and wpa3-personal encryption
        if self.config["AP"]["security"] == "wpa2-psk":
            # WPA2-PSK
            for setting in [
                f"wpa=2",
                f"wpa_key_mgmt=WPA-PSK",
                f"rsn_pairwise=CCMP",
                f"wpa_passphrase={passphrase}"
            ]:
                settings.append(setting)

        if self.config["AP"]["security"] == "wpa3-personal":
            # WPA3-Personal
            for setting in [
                f"ieee80211w=2",
                f"wpa=2",
                f"wpa_key_mgmt=SAE",
                f"rsn_pairwise=CCMP",
                f"sae_require_mfp=1",
                f"wpa_passphrase={passphrase}"
            ]:
                settings.append(setting)

        if self.config["AP"]["security"] == "wpa2/wpa3":
            # WPA2/WPA3 Transition
            for setting in [
                f"ieee80211w=1",
                f"wpa=2",
                f"wpa_key_mgmt=WPA-PSK SAE",
                f"rsn_pairwise=CCMP",
                f"wpa_passphrase={passphrase}"
            ]:
                settings.append(setting)

        # Write the settings to the specified hostapd configuration file
        with open(self.config["AP"]["hostapd_config_file"], "w") as hostapd_config:
            for line in settings:
                hostapd_config.write(line + "\n")

        # Verify the file was written and return its filepath
        if not os.path.isfile(self.config["AP"]["hostapd_config_file"]):
            raise Exception(f"Error writing hostapd configuration file to disk! File not found on filesystem!")
        return self.config["AP"]["hostapd_config_file"]

class APHost(object):
    """ Access point host
    """

    def __init__(self, config=None, logger=None):
        """ Initialize the object
        """
        self.config = config
        self.logger = logger
        self.hostapd_process = None
        self.state = "not running"
        self.essid = self._essid = self.config["AP"]["essid"]
        self.band = self._band = self.config["AP"]["band"]
        self.channel = self._channel = self.config["AP"]["channel"]
        self.security = self._security = self.config["AP"]["security"]
        self.passphrase = self._passphrase = self.config["AP"]["passphrase"]

    def _write_hostapd_config(self):
        """ Write the hostapd configuration file
        """
        hostapd_config_file_handler = HostapdConfigurationFileHandler(config=self.config, logger=self.logger)
        hostapd_config_file = hostapd_config_file_handler.generate_hostapd_config_file(
            self.essid,
            self.band,
            self.channel,
            self.security,
            self.passphrase
        )
        return hostapd_config_file

    def _start_ap_host(self):
        """ Start the hostapd process
        """
        hostapd_config_file = self._write_hostapd_config()
        self.hostapd_process = subprocess.Popen(
            [self.config["AP"]["hostapd_executable"], hostapd_config_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.state = "running"
        return None

    def _stop_ap_host(self):
        """ Stop the hostapd process
        """
        self.hostapd_process.terminate()
        try:
            self.hostapd_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.hostapd_process.kill()
            self.hostapd_process.wait()
        self.state = "not running"
        return None

    def _restart_ap_host(self):
        """ Restart the hostapd process
        """
        self._stop_ap_host()
        self._start_ap_host()
        return None

    def start(self):
        """ Start the AP host
        """
        if self.state == "running":
            raise exceptions.StateChangeError(f"AP host is already started!")
        try:
            self._start_ap_host()
        except Exception as err_msg:
            raise exceptions.StateChangeError(f"Encountered an exception when trying to start the AP host! Error message: {err_msg}")
        return None

    def stop(self):
        """ Stop the AP host
        """
        if self.state == "not running":
            raise exceptions.StateChangeError(f"AP host is already stopped!")
        try:
            self._stop_ap_host()
        except Exception as err_msg:
            raise exceptions.StateChangeError(f"Encountered an exception when trying to stop the AP host! Error message: {err_msg}")
        return None

    def restart(self):
        """ Stop then start the AP host
        """
        if self.state == "not_running":
            raise exceptions.StateChangeError(f"AP host has not been started!")
        try:
            self._restart_ap_host()
        except Exception as err_msg:
            raise exceptions.StateChangeError(f"Encountered an exception when trying to restart the AP host! Error message: {err_msg}")
        return None

    def apply_configuration(self):
        """ Apply configuration changes from current property values
        """
        self.essid = self._essid
        self.band = self._band
        self.channel = self._channel
        self.security = self._security
        self.passphrase = self._passphrase
        return None


