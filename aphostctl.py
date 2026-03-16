#!/usr/bin/env python3.11

"""
aphostctl.py

DBus client for aphostd
"""

import os
import sys
import getopt
from pydbus import SystemBus
from gi.repository import GLib

__project_repository__ = "https://github.com/newdaynewburner/ap-host"
__aphostd_version__ = "0.1"
__aphostctl_version__ = "0.1"


class DBusAPIClient(object):
    """ Client object for interacting with DBus API
    """

    def __init__(self, bus_name, object_path, debug=False):
        """ Initialize the object
        """
        self.debug = debug
        self.bus = SystemBus()
        self.api = self.bus.get(bus_name, object_path)
        if self.debug:
            print(f"[DEBUG] Connected to system bus '{bus_name}' at path '{object_path}'")

    def start(self):
        """ Call the Start endpoint
        """
        if self.debug:
            print(f"[DEBUG] Making API call to: Start (Arguments: )")
        try:
            self.api.Start()
        except Exception as err_msg:
            print(f"[ERROR] DBus error: {err_msg}")
        return None

    def stop(self):
        """ Call the Stop endpoint
        """
        if self.debug:
            print(f"[DEBUG] Making API call to: Stop (Arguments: )")
        try:
            self.api.Stop()
        except Exception as err_msg:
            print(f"[ERROR] DBus error: {err_msg}")
        return None

    def restart(self):
        """ Call the Restart endpoint
        """
        if self.debug:
            print(f"[DEBUG] Making API call to: Restart (Arguments: )")
        try:
            self.api.Restart()
        except Exception as err_msg:
            print(f"[ERROR] DBus error: {err_msg}")
        return None

    def configure(self, setting, value):
        """ Call the configure endpoint
        """
        if self.debug:
            print(f"[DEBUG] Making API call to: Configure (Arguments: {setting}, {value})")
        try:
            self.api.Configure(setting, value)
        except Exception as err_msg:
            print(f"[ERROR] DBus error: {err_msg}")
        return None

    def _set(self, setting, value):
        """ Set the value of a property
        """
        if self.debug:
            print(f"[DEBUG] Setting value of property: {setting} to: {value}")
        try:
            if setting == "essid":
                self.api.ESSID = value
            elif setting == "band":
                self.api.Band = value
            elif setting == "channel":
                self.api.Channel = value
            elif setting == "security":
                self.api.Security = value
            elif setting == "passphrase":
                self.api.Passphrase = value
        except Exception as err_msg:
            print(f"[ERROR] DBus error: {err_msg}")
        return None

    def _apply(self):
        """ Apply changes
        """
        if self.debug:
            print(f"[DEBUG] Making API call to: ApplyConfiguration")
        try:
            self.api.ApplyConfiguration()
        except Exception as err_msg:
            print(f"[ERROR] DBus error: {err_msg}")
        return None

    def monitor(self):
        """ Monitor for signals
        """
        def on_state_changed(old_state, new_state):
            print("StateChanged signal received")
            print((old_state, new_state))
        def on_configuration_changed(prop, old, new):
            print("ConfigurationChanged signal received")
            print((prop, old, new))
        def on_configuration_applied(d):
            print("ConfigurationApplied signal received")
            print(d)
        def on_station_connected(d):
            print("StationConnected signal received")
            print(d)
        def on_station_disconnected(d):
            print("StationDisconnected signal recieved")
            print(d)

        self.api.onStateChanged = on_state_changed
        self.api.onConfigurationChanged = on_configuration_changed
        self.api.onConfigurationApplied = on_configuration_applied
        self.api.onStationConnected = on_station_connected
        self.api.onStationDisconnected = on_station_disconnected
        loop = GLib.MainLoop()
        try:
            loop.run()
        except KeyboardInterrupt:
            loop.quit()

def main(debug, operations):
    """ Main function. Core program logic
    """
    client = DBusAPIClient(
        "com.aphost.APHost",
        "/com/aphost/APHost",
        debug=debug
    )
    for operation in operations:
        if debug:
            print(f"[DEBUG] Current operation: {operation}")

        if operation[0] == "start":
            client.start()
        elif operation[0] == "stop":
            client.stop()
        elif operation[0] == "restart":
            client.restart()
        elif operation[0] == "configure":
            client.configure(operation[1][0], operation[1][1])
        elif operation[0] == "set":
            client._set(operation[1][0], operation[1][1])
        elif operation[0] == "apply":
            client._apply()
        elif operation[0] == "monitor":
            client.monitor()
        else:
            raise Exception(f"Function main() encountered an invalid operation name: {operation[0]}")

    return None

# Begin execution
if __name__ == "__main__":
    # Parse command line arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvd", [
            "help",
            "version",
            "debug"
        ])
    except getopt.GetoptError as err_msg:
        raise Exception(f"Encountered an exception while parsing command line arguments! Error message: {err_msg}")

    debug = False
    operations = []

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            # Display the help message
            print(f"USAGE:")
            print("\taphostctl [ OPTIONS ] COMMAND { COMMAND_ARGS | help }")
            print("WHERE:")
            print("\tOPTIONS := { -h, --help | -v, --version | -d, --debug }")
            print("\tCOMMAND := { start | stop | restart | configure | set | apply | monitor }")
            sys.exit(0)
        elif opt in ("-v", "--version"):
            # Display the version message
            print(f"aphostctl ({__project_repository__})")
            print(f"aphostctl version: {__aphostctl_version__}")
            print(f"aphostd version: {__aphostd_version__}")
            sys.exit(0)
        elif opt in ("-d", "--debug"):
            # Enable debugging output
            debug = True

    for arg in args:
        if arg == "start":
            if (args.index(arg) + 1) < len(args):
                if args[args.index(arg) + 1] == "help":
                    print("Start the AP host")
                    print("USAGE:")
                    print("\taphostctl start")
                    sys.exit(0)
            operations.append(("start", []))

        elif arg == "stop":
            if (args.index(arg) + 1) < len(args):
                if args[args.index(arg) + 1] == "help":
                    print("Stop the AP host")
                    print("USAGE:")
                    print("\taphostctl stop")
            operations.append(("stop", []))

        elif arg == "restart":
            if (args.index(arg) + 1) < len(args):
                if args[args.index(arg) + 1] == "help":
                    print("Restart the AP host")
                    print("USAGE:")
                    print("\taphostctl restart")
            operations.append(("restart", []))

        elif arg == "configure":
            if (args.index(arg) + 2) <= (len(args) - 1) or (args.index(arg) + 1) == (len(args) - 1):
                if args[args.index(arg) + 1] == "help":
                    print("Change the value of a configuration setting")
                    print("USAGE:")
                    print("\taphostctl [ OPTIONS ] configure { SETTING | help } VALUE")
                    print("WHERE:")
                    print("\tOPTIONS := { -h, --help | -v, --version | -d, --debug }")
                    print("\tSETTING := { broadcast_iface | driver | essid | band | channel | security | passphrase | hostapd_executable | hostapd_config_file }")
                    sys.exit(0)
                elif args[args.index(arg) + 1] in ("broadcast_iface", "driver", "essid", "band", "channel", "security", "passphrase", "hostapd_executable", "hostapd_config_file"):
                    operations.append(("configure", [args[args.index(arg) + 1], args[args.index(arg) + 2]]))
                else:
                    print(f"Invalid setting '{args[args.index(arg) + 1]}'! See 'aphostctl configure help' for a list of valid settings!")
                    sys.exit(1)
            else:
                print("Error! Invalid usage! See -h or --help for usage information!")
                sys.exit(1)

        elif arg == "set":
            if args[args.index(arg) + 1] == "help":
                print("Set the value of a property belonging to the service")
                print("USAGE:")
                print("\taphostctl [ OPTIONS ] set { PROPERTY | help } VALUE")
                print("WHERE:")
                print("\tOPTIONS := { -h, --help | -v, --version | -d, --debug }")
                print("\tPROPERTY := { essid | band | channel | security | passphrase }")
                sys.exit(0)
            elif args[args.index(arg) + 1] in ("essid", "band", "channel", "security", "passphrase"):
                value = ""
                for p in args[args.index(arg) + 2:]:
                    value = value + p + " "
                operations.append(("set", [args[args.index(arg) + 1], value.rstrip(" ")]))
            else:
                print(f"Invalid property '{args[args.index(arg) + 1]}'! See 'aphostctl set help' for a list of valid properties!")
                sys.exit(1)

        elif arg == "apply":
            if (args.index(arg) + 1) < len(args):
                if args[args.index(arg) + 1] == "help":
                    print("Applies configuration changes made to properties with the set command")
                    print("USAGE:")
                    print("\taphostctl apply")
                    sys.exit(0)
            operations.append(("apply", []))

        elif arg == "monitor":
            if (args.index(arg) + 1) < len(args):
                if args[args.index(arg) + 1] == "help":
                    print("Monitor for signals until CTRL-C")
                    print("USAGE:")
                    print("\taphostctl monitor")
                    sys.exit(0)
            operations.append(("monitor", []))

    main(debug, operations)
