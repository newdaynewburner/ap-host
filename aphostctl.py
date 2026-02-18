#!/usr/bin/env python3

"""
aphostctl.py

DBus client for aphostd
"""

import os
import sys
import getopt

__aphostd_version__ = "0.1"
__aphostctl_version__ = "0.1"


class DBusAPIClient(object):
    """ Client object for interacting with DBus API
    """

    def __init__(self, debug=False):
        """ Initialize the object
        """
        self.debug = debug
        if self.debug:
            print(f"[DEBUG] Initialized DBusAPIClient object instance with debugging messages enabled")

    def start(self):
        """ Call the Start endpoint
        """
        if self.debug:
            print(f"[DEBUG] Making API call to: Start (Arguments: )")
        return None

    def stop(self):
        """ Call the Stop endpoint
        """
        if self.debug:
            print(f"[DEBUG] Making API call to: Stop (Arguments: )")
        return None

    def restart(self):
        """ Call the Restart endpoint
        """
        if self.debug:
            print(f"[DEBUG] Making API call to: Restart (Arguments: )")
        return None

    def configure(self, setting, value):
        """ Call the configure endpoint
        """
        if self.debug:
            print(f"[DEBUG] Making API call to: Configure (Arguments: {setting}, {value})")
        return None

def main(debug, operations):
    """ Main function. Core program logic
    """
    client = DBusAPIClient(debug=debug)
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
            print("\tCOMMAND := { start | stop | restart | configure }")
            sys.exit(0)
        elif opt in ("-v", "--version"):
            # Display the version message
            print(f"aphostd version: {__aphostd_version__}")
            print(f"aphostctl version: {__aphostctl_version__}")
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
                    print("\thostapctl start")
                    sys.exit(0)
            operations.append(("start", []))

        elif arg == "stop":
            if (args.index(arg) + 1) < len(args):
                if args[args.index(arg) + 1] == "help":
                    print("Stop the AP host")
                    print("USAGE:")
                    print("\thostapctl stop")
            operations.append(("stop", []))

        elif arg == "restart":
            if (args.index(arg) + 1) < len(args):
                if args[args.index(arg) + 1] == "help":
                    print("Restart the AP host")
                    print("USAGE:")
                    print("\thostapctl restart")
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
                    print(f"Invalid setting '{args[args.index(arg) + 1]}'! See 'hostapctl configure help' for a list of valid settings!")
                    sys.exit(1)
            else:
                print("Error! Invalid usage! See -h or --help for usage information!")
                sys.exit(1)

    main(debug, operations)
