"""
lib/datatypes.py

Custom datatype definitions
"""

import os
import sys

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
