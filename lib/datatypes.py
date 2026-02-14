"""
lib/datatypes.py

Custom datatype definitions
"""

import os
import sys

class APConfigurationProfile(object):
    """ Represents a specific access point configuration
    """

    def __init__(self, name, config=None, logger=None):
        """ Initialize the object
        """
        self.config = config
        self.logger = logger
        self.name = name
        if self.config:
            self.hostapd_config_file_handler = HostapdConfigurationFileHandler(config=self.config, logger=self.logger)

    def get_config(self):
        """ Return the profile's configuration settings
        """
        return self.config

    def write_config(self):
        """ Write the configuration settings of the profile to the hostapd configuration file
        """
        hostapd_config_file = self.hostapd_config_file_handler.generate_hostapd_config_file()
        return hostapd_config_file

    def import_config(self, infile):
        """ Import a configuration from a file
        """
        pass

    def export_config(self, outfile):
        """ Export the configuration to a file
        """
        pass


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

    def generate_hostapd_config_file(self):
        """ Dynamically generate the hostapd configuration file
        """

        # Initialize a list to hold configuration file settings
        settings = []

        # Generate the base settings
        for setting in [
            f"interface={self.config['AP']['broadcast_iface']}",
            f"driver={self.config['AP']['driver']}",
            f"ssid={self.config['AP']['essid']}",
            f"hw_mode={self.config['AP']['band']}",
            f"channel={self.config['AP']['channel']}",
            f"ieee80211n=1",
            f"wmm_enabled=1",
            f"auth_algs=1",
            f"ignore_broadcast_ssid=0"
        ]:
            settings.append(setting)

        # Generate the security settings for wpa2-psk and wpa3-personal encryption
        if self.config["AP"]["security"] == "wpa2-psk":
            # WPA2-PSK
            for setting in [
                f"wpa=2",
                f"wpa_key_mgmt=WPA-PSK",
                f"rsn_pairwise=CCMP",
                f"wpa_passphrase={self.config['AP']['passphrase']}"
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
                f"wpa_passphrase={self.config['AP']['passphrase']}"
            ]:
                settings.append(setting)

        if self.config["AP"]["security"] == "wpa2/wpa3":
            # WPA2/WPA3 Transition
            for setting in [
                f"ieee80211w=1",
                f"wpa=2",
                f"wpa_key_mgmt=WPA-PSK SAE",
                f"rsn_pairwise=CCMP",
                f"wpa_passphrase={self.config['AP']['passphrase']}"
            ]:
                settings.append(setting)

        # Write the settings to the specified hostapd configuration file
        with open(self.config["AP"]["hostapd_config_file"], "w") as hostapd_config:
            for line in settings:
                hostapd_config.write(line + "\n")
                print(f"{line}")

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
        self._state = "not running"
        self._interface = self.config["AP"]["broadcast_iface"]
        self._essid = self.config["AP"]["essid"]
        self._band = self.config["AP"]["band"]
        self._channel = self.config["AP"]["channel"]
        self._security = self.config["AP"]["security"]
        self._passphrase = self.config["AP"]["passphrase"]
        self.hostapd_process = None
        self.configuration_profiles = []

    def _write_hostapd_config(self):
        """ Write the hostapd configuration file
        """
        hostapd_config_file_handler = datatypes.HostapdConfigurationFileHandler(config=self.config, logger=self.logger)
        hostapd_config_file = hostapd_config_file_handler.generate_hostapd_config_file()
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
        if self._state == "running":
            raise exceptions.StateChangeError(f"AP host is already started!")
        try:
            self._start_ap_host()
        except Exception as err_msg:
            raise exceptions.StateChangeError(f"Encountered an exception when trying to start the AP host! Error message: {err_msg}")
        return None

    def stop(self):
        """ Stop the AP host
        """
        if self._state == "not running":
            raise exceptions.StateChangeError(f"AP host is already stopped!")
        try:
            self._stop_ap_host()
        except Exception as err_msg:
            raise exceptions.StateChangeError(f"Encountered an exception when trying to stop the AP host! Error message: {err_msg}")
        return None

    def restart(self):
        """ Stop then start the AP host
        """
        if self._state == "not_running":
            raise exceptions.StateChangeError(f"AP host has not been started!")
        try:
            self._restart_ap_host()
        except Exception as err_msg:
            raise exceptions.StateChangeError(f"Encountered an exception when trying to restart the AP host! Error message: {err_msg}")
        return None

    def configure(self, setting, value):
        """ Change the value of a configuration setting
        """
        old_value = self.config["AP"][setting]
        if setting == "broadcast_iface":
            self.config["AP"]["broadcast_iface"] = value
            self._interface = self.config["AP"]["broadcast_iface"]
        elif setting == "driver":
            self.config["AP"]["driver"] = value
        elif setting == "essid":
            self.config["AP"]["essid"] = value
            self._essid = self.config["AP"]["essid"]
        elif setting == "band":
            self.config["AP"]["band"] = value
            self._band = self.config["AP"]["band"]
        elif setting == "channel":
            self.config["AP"]["channel"] = value
            self._channel = self.config["AP"]["channel"]
        elif setting == "security":
            self.config["AP"]["security"] = value
            self._security = self.config["AP"]["security"]
        elif setting == "passphrase":
            self.config["AP"]["passphrase"] = value
            self._passphrase = self.config["AP"]["passphrase"]
        elif setting == "hostapd_executable":
            self.config["AP"]["hostapd_executable"] = value
        elif setting == "hostapd_config_file":
            self.config["AP"]["hostapd_config_file"] = value
        else:
            raise exceptions.ConfigurationError(f"Invalid setting '{setting}'!")

    def save_profile(self, name):
        """ Store the current configuration as an APConfigurationProfile object
        """
        configuration_profile = APConfigurationProfile(name, config=self.config, logger=self.logger)
        self.configuration_profiles.append(configuration_profiles)
        return configuration_profile.name

    def load_profile(self, name, start=False):
        """ Load an AP configuration from an APConfigurationProfile object
        """
        profile_exists = False
        for configuration_profile in self.configuration_profiles:
            if configuration_profile.name == name:
                profile_exists = True
                self.config = configuration_profile.get_config()
                configuration_profile.write_config()
                break
        if not profile_exists:
            raise exceptions.ConfigurationError(f"Configuration profile named '{name}' does not exist!")
        if start:
            if self.state == "not running":
                try:
                    self._start_ap_host()
                except Exception as err_msg:
                    raise exception.StateChangeError(f"Failed to start AP host after loading configuration profile '{configuration_profile.name}'! Error message: {err_msg}")
            else:
                try:
                    self._restart_ap_host()
                except Exception as err_msg:
                    raise exception.StateChangeError(f"Failed to restart AP host after loading configuration profile '{configuration_profile.name}'! Error message: {err_msg}")
        return None


