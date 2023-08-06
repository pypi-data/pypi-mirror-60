#! /usr/bin/env python


from ..common.device_base import Device_Base
from .device_insteon_base import Device_Insteon_Base


class Device_Insteon_Siren(Device_Base, Device_Insteon_Base):
    def __init__(self, container, device_info):
        Device_Base.__init__(self, container, 'siren' device_info.name, device_info.address)
        Device_Insteon_Base.__init__(self, device_info)

        self.add_property("siren", 0)
        self.add_property("chime", 0)        

        value = device_info.get_property("ST", "value")
        if value:
            try:
                if int(value) > 0:
                    self.set_property("siren", "on")
                else:
                    self.set_property("siren", "off")
            except:
                pass

    def process_websocket_event(self, event):
        if event.control == "ST":
            if int(event.action) > 0:
                self.set_property("siren", "on")
            else:
                self.set_property("siren", "off")

    def turn_siren_on(self):
        pass

    def turn_siren_off(self):
        pass

