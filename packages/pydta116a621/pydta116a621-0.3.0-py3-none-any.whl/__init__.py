#!/usr/bin/env python
#coding=utf-8
import logging

from modbus_client import DaikinModbusClient
from register_area import RegisterAreas
from adapter import Adapter
from indoor_unit import IndoorUnit

from const import (CONST_HAVC_MODE_FAN_ONLY, CONST_HAVC_MODE_HEAT, CONST_HAVC_MODE_COOL, CONST_HAVC_MODE_AUTO, CONST_HAVC_MODE_DRY,
                   CONST_FAN_MODE_AUTO, CONST_FAN_MODE_LOW,CONST_FAN_MODE_MID_LOW,CONST_FAN_MODE_MIDDLE,CONST_FAN_MODE_MID_HIGH,CONST_FAN_MODE_HIGH,
                   CONST_SWING_MODE_AUTO, CONST_SWING_MODE_P1,CONST_SWING_MODE_P2,CONST_SWING_MODE_P3,CONST_SWING_MODE_P4,CONST_SWING_MODE_P5,
                   CONST_HAVC_POWER_ON, CONST_HAVC_POWER_OFF,
                   )

class DaikinAPI:
    def __init__(self, host, port, slave_id):
        self._modbus_client = DaikinModbusClient(host, port, slave_id)
        self._areas = RegisterAreas(self._modbus_client)
        self._areas.update_all()
        self._adapter = Adapter(self._areas)
        self._indoor_units = {}
        self.__init_all_connected_indoor_unit()

    def __init_all_connected_indoor_unit(self):
        connected_unit_list = self._adapter.connected_devices
        for connected_unit_name in connected_unit_list:
            self._indoor_units[connected_unit_name] = IndoorUnit(self._areas, connected_unit_name)

    def get_adapter(self):
        return self._adapter

    def get_indoor_unit(self, indoor_unit_id):
        return self._indoor_units.get(indoor_unit_id)


if __name__ == '__main__':
    api = DaikinAPI('192.168.35.102', 502, 1)

    indoor_unit = api.get_indoor_unit('3-01')
    print('havc_power: ', indoor_unit.havc_power)
    print('supported_cool_temperature: ',indoor_unit.supported_cool_temperature)
    print('supported_heat_temperature: ', indoor_unit.supported_heat_temperature)
    print('real_temperature: ', indoor_unit.real_temperature)
    print('target_temperature: ', indoor_unit.target_temperature)
    print('supported_hvac_modes: ', indoor_unit.supported_hvac_modes)
    print('havc_mode: ', indoor_unit.havc_mode)
    print('supported_fan_modes: ',indoor_unit.supported_fan_modes)
    print('fan_mode: ', indoor_unit.fan_mode)
    print('supported_swing_modes: ', indoor_unit.supported_swing_modes)
    print('swing_mode: ', indoor_unit.swing_mode)
    #indoor_unit.set_havc_power(CONST_HAVC_POWER_OFF)
    #indoor_unit.set_havc_power(CONST_HAVC_POWER_ON)
    #indoor_unit.set_target_temperature(20.2)
    #indoor_unit.set_havc_mode(CONST_HAVC_MODE_HEAT)
    indoor_unit.set_fan_mode(CONST_FAN_MODE_HIGH)



    #client = DTA116A62Client('192.168.35.102', 502, 1)
    #print(client.get_adapter_status())
    #print(client.get_diii_connection_status())
    #print(client.get_connected_devices())
    #print(client.get_communicable_devices())
    #client.set_havc_power('3-01', 1)
    #print(client.get_havc_power('3-01'))
    #client.set_fan_speed('3-01', 5)
    #print(client.get_fan_speed('3-01'))
    #client.set_target_temperature('3-01', 25.3)
    #print(client.get_target_temperature('3-01'))
    #print(client.get_real_temperature('3-01'))
    #print(client.get_havc_mode('3-01'))
    #print(client.set_havc_mode('3-01', 1))
    #print(client.get_support_cool_max_temperature('3-01'))
    #print(client.get_support_cool_min_temperature('3-01'))
    #print(client.get_support_heat_max_temperature('3-01'))
    #print(client.get_support_heat_min_temperature('3-01'))
    #print(client.get_havc_mode_change_permission('3-01'))

