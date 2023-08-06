import logging

from bit_tool import pick_value, fill_field
from const import (REGISTER_TYPE_INPUT, REGISTER_TYPE_HOLDING,
                   CONST_MAX_BATCH_READ_SIZE, CONST_MAX_INDOOR_UNIT_COUNT, CONST_CELL_BIT_SIZE,
                   INDOOR_UNIT_ID_INDEX, indoor_unit_id2index, indoor_unit_index2id,
                   CONST_REGISTER_AREA_ADAPTER_STATUS, CONST_REGISTER_AREA_INDOOR_UNIT_CONNECTION_STATE, CONST_REGISTER_AREA_INDOOR_UNIT_COMMUNICATION_STATE,
                   CONST_REGISTER_AREA_INDOOR_UNIT_ABILITY_1, CONST_REGISTER_AREA_INDOOR_UNIT_ABILITY_2,
                   CONST_REGISTER_AREA_INDOOR_UNIT_STATE_1,CONST_REGISTER_AREA_INDOOR_UNIT_STATE_2,CONST_REGISTER_AREA_INDOOR_UNIT_STATE_3,
                   CONST_REGISTER_AREA_INDOOR_UNIT_CONTROL_1,CONST_REGISTER_AREA_INDOOR_UNIT_CONTROL_2,CONST_REGISTER_AREA_INDOOR_UNIT_CONTROL_3,
                   CONST_HAVC_MODE_FAN_ONLY, CONST_HAVC_MODE_HEAT, CONST_HAVC_MODE_COOL, CONST_HAVC_MODE_AUTO, CONST_HAVC_MODE_DRY, CONST_HAVC_MODE_MAPPING,
                   CONST_FAN_MODE_AUTO, CONST_FAN_MODE_LOW,CONST_FAN_MODE_MID_LOW,CONST_FAN_MODE_MIDDLE,CONST_FAN_MODE_MID_HIGH,CONST_FAN_MODE_HIGH,CONST_FAN_MODE_MAPPING,CONST_FAN_MODE_SEG_DEF,
                   CONST_SWING_MODE_AUTO, CONST_SWING_MODE_P1,CONST_SWING_MODE_P2,CONST_SWING_MODE_P3,CONST_SWING_MODE_P4,CONST_SWING_MODE_P5,CONST_SWING_MODE_MAPPING,CONST_SWING_MODE_SEG_DEF,
                   CONST_HAVC_POWER_ON, CONST_HAVC_POWER_OFF, CONST_HAVC_POWER_MAPPING,
                   )
from proxy import IndoorUnitInfoProxy
from register_area import RegisterAreas

_LOGGER = logging.getLogger(__name__)

class IndoorUnit:
    def __init__(self, areas : RegisterAreas, indoor_unit_id : str):
        self._areas = areas
        self._indoor_unit_id = indoor_unit_id

    def _get_value_from_cell(self, cell, bit_start, bit_stop):
        return pick_value(cell, bit_start, (bit_stop - bit_start) + 1)

    def _make_cell_with_value(self, old_cell, bit_start, bit_stop, value):
        return fill_field(old_cell, bit_start, (bit_stop - bit_start) + 1, value)

    # update all area for this indoor unit
    def update_all(self):
        for area in self._areas.all_areas.values():
            if(type(area) == IndoorUnitInfoProxy):
                area.update_indoor_unit(self._indoor_unit_id)

    def _get_cell(self, area_name, offset):
        area = self._areas.get_area(area_name)
        cell = area.get_cell_by_indoor_unit_offset(self._indoor_unit_id, offset)
        return cell

    def _get_value(self, area_name, offset, bit_start, bit_stop):
        area = self._areas.get_area(area_name)
        value = area.get_value_by_indoor_unit_offset(self._indoor_unit_id, offset, bit_start, bit_stop)
        return value

    def _write_cell(self, area_name, offset, cell):
        area = self._areas.get_area(area_name)
        area.write_cell_by_indoor_unit_offset(self._indoor_unit_id, offset, cell)

    def _write_value(self, area_name, offset, bit_start, bit_stop, value):
        area = self._areas.get_area(area_name)
        area.write_value_by_indoor_unit_offset(self._indoor_unit_id, offset, bit_start, bit_stop, value)

    @property
    def havc_power(self):
        value = self._get_value(area_name=CONST_REGISTER_AREA_INDOOR_UNIT_STATE_1, offset=0,
                                bit_start=0, bit_stop=0)
        return CONST_HAVC_POWER_MAPPING.inverse.get(value)

    @property
    def havc_mode(self):
        value = self._get_value(area_name=CONST_REGISTER_AREA_INDOOR_UNIT_STATE_1, offset=1,
                                bit_start=0, bit_stop=3)
        return CONST_HAVC_MODE_MAPPING.inverse.get(value)

    @property
    def fan_mode(self):
        value = self._get_value(area_name=CONST_REGISTER_AREA_INDOOR_UNIT_STATE_1, offset=0,
                                bit_start=12, bit_stop=14)
        return CONST_FAN_MODE_MAPPING.inverse.get(value)

    @property
    def swing_mode(self):
        value = self._get_value(area_name=CONST_REGISTER_AREA_INDOOR_UNIT_STATE_1, offset=0,
                                bit_start=8, bit_stop=10)
        return CONST_SWING_MODE_MAPPING.inverse.get(value)

    @property
    def target_temperature(self):
        return self._get_cell(CONST_REGISTER_AREA_INDOOR_UNIT_STATE_1, 2) / 10

    @property
    def real_temperature(self):
        return self._get_cell(CONST_REGISTER_AREA_INDOOR_UNIT_STATE_1, 4) / 10

    @property
    def havc_mode_change_permission(self):
        return self._get_value(area_name=CONST_REGISTER_AREA_INDOOR_UNIT_STATE_1, offset=1,
                               bit_start=14, bit_stop=15)

    # min, max
    @property
    def supported_cool_temperature(self):
        max_temp = self._get_value(area_name=CONST_REGISTER_AREA_INDOOR_UNIT_ABILITY_1, offset=1,
                                   bit_start=0, bit_stop=7)
        min_temp = self._get_value(area_name=CONST_REGISTER_AREA_INDOOR_UNIT_ABILITY_1, offset=1,
                                   bit_start=8, bit_stop=15)
        return min_temp, max_temp

    # min, max
    @property
    def supported_heat_temperature(self):
        max_temp = self._get_value(area_name=CONST_REGISTER_AREA_INDOOR_UNIT_ABILITY_1, offset=2,
                                   bit_start=0, bit_stop=7)
        min_temp = self._get_value(area_name=CONST_REGISTER_AREA_INDOOR_UNIT_ABILITY_1, offset=2,
                                   bit_start=8, bit_stop=15)
        return min_temp, max_temp

    @property
    def supported_hvac_modes(self):
        def get_support_hvac_mode_value(bit_pos):
            return self._get_value(area_name=CONST_REGISTER_AREA_INDOOR_UNIT_ABILITY_1, offset=0,
                                   bit_start=bit_pos, bit_stop=bit_pos)
        all_support_modes= {
            CONST_HAVC_MODE_FAN_ONLY: get_support_hvac_mode_value(0),
            CONST_HAVC_MODE_HEAT: get_support_hvac_mode_value(1),
            CONST_HAVC_MODE_COOL: get_support_hvac_mode_value(2),
            CONST_HAVC_MODE_AUTO: get_support_hvac_mode_value(3),
            CONST_HAVC_MODE_DRY: get_support_hvac_mode_value(4),
        }
        return [key for key, value in all_support_modes.items() if value]

    @property
    def supported_fan_modes(self):
        support_fan_modes_value = self._get_value(area_name=CONST_REGISTER_AREA_INDOOR_UNIT_ABILITY_1, offset=0,
                                                  bit_start=12, bit_stop=14)
        return CONST_FAN_MODE_SEG_DEF[support_fan_modes_value]

    @property
    def supported_swing_modes(self):
        support_fan_modes_value = self._get_value(area_name=CONST_REGISTER_AREA_INDOOR_UNIT_ABILITY_1, offset=0,
                                                  bit_start=8, bit_stop=10)
        return CONST_SWING_MODE_SEG_DEF[support_fan_modes_value]

    def set_havc_power(self, value):
        self._write_value(area_name=CONST_REGISTER_AREA_INDOOR_UNIT_CONTROL_1, offset=0,
                          bit_start=0, bit_stop=0,
                          value=CONST_HAVC_POWER_MAPPING.get(value))

    def set_havc_mode(self, value):
        self._write_value(area_name=CONST_REGISTER_AREA_INDOOR_UNIT_CONTROL_1, offset=1,
                          bit_start=0, bit_stop=3,
                          value=CONST_HAVC_MODE_MAPPING.get(value))

    def _set_fan_swing_havc_mode(self, value):
        self._write_value(area_name=CONST_REGISTER_AREA_INDOOR_UNIT_CONTROL_1, offset=0,
                          bit_start=4, bit_stop=7,
                          value=CONST_HAVC_MODE_MAPPING.get(value))

    def set_fan_mode(self, value):
        area = self._areas.get_area(area_name=CONST_REGISTER_AREA_INDOOR_UNIT_CONTROL_1)
        address = area.get_device_start_address(self._indoor_unit_id)
        cell = area.get_cell(address)
        cell = fill_field(cell,12, 14-12+1,CONST_FAN_MODE_MAPPING.get(value))
        cell = fill_field(cell,4, 7-4+1,CONST_HAVC_MODE_MAPPING.get(self.havc_mode))
        area.write_cell(address, cell)

    def set_swing_mode(self, value):
        area = self._areas.get_area(area_name=CONST_REGISTER_AREA_INDOOR_UNIT_CONTROL_1)
        address = area.get_device_start_address(self._indoor_unit_id)
        cell = area.get_cell(address)
        cell = fill_field(cell,4, 7-4+1,CONST_HAVC_MODE_MAPPING.get(self.havc_mode))
        cell = fill_field(cell,8, 10-8+1,CONST_SWING_MODE_MAPPING.get(value))
        area.write_cell(address, cell)

    def set_target_temperature(self, value):
        self._write_cell(area_name=CONST_REGISTER_AREA_INDOOR_UNIT_CONTROL_1, offset=2,
                         cell=int(value * 10))
