"""
lib/exceptions.py

Custom exception definitions
"""

import warnings

class FailedToStartHostapdError(Exception):
    """ Raised if the hostapd daemon process fails to start properly
    """
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
