"""
client.py

DBus API client
"""

from pydbus import SystemBus

bus = SystemBus()
service = bus.get("com.aphost.APHost")

input("Press [ENTER] to start")
service.Start()
input("Press [ENTER] to stop")
service.Stop()
