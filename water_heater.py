"""Yunmi Kettle for homeassistant

"water_remain_time","flush_time","flush_flag","tds","time","curr_tempe","setup_tempe","custom_tempe1","min_set_tempe","drink_remind","drink_remind_time","run_status","work_mode","drink_time_count"
0,1803,0,212,1561040267,33,63,63,59,0,12,0,1,631
"""
import math
import logging

from homeassistant.components.sensor import DOMAIN
from homeassistant.const import (CONF_NAME, CONF_HOST, CONF_TOKEN, ATTR_TEMPERATURE)
from homeassistant.helpers.entity import Entity
from homeassistant.exceptions import PlatformNotReady
from homeassistant.components.water_heater import (WaterHeaterDevice, SUPPORT_OPERATION_MODE, SUPPORT_TARGET_TEMPERATURE, STATE_ELECTRIC, ATTR_OPERATION_LIST, ATTR_OPERATION_MODE)
from miio import Device, DeviceException
from datetime import timedelta

_LOGGER = logging.getLogger(__name__)

STATE_NORMAL = "normal"
STATE_WARM = "warm"
STATE_BOILED = "boiled"

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Perform the setup for Yunmi kettle."""

    host = config.get(CONF_HOST)
    name = config.get(CONF_NAME)
    token = config.get(CONF_TOKEN)

    _LOGGER.info("Initializing Yunmi Kettle with host %s (token %s...)", host, token[:5])

    devices = []
    try:
        device = Device(host, token)
        yumikettle = YunmiKettle(device, name)
        devices.append(yumikettle)

    except DeviceException:
        _LOGGER.exception('Fail to setup yunmi kettle')
        raise PlatformNotReady

    add_devices(devices)

class YunmiKettle(WaterHeaterDevice):
    """Representation of a YunmiKettle."""

    def __init__(self, device, name):
        """Initialize the YunmiKettle."""
        self._name = name
        self._support_features = SUPPORT_TARGET_TEMPERATURE
        self._min_temp = 40
        self._max_temp = 90
        self._device = device
        self._target_temperature = None
        self._current_temperature = None
        self._current_operation = None
        self._state_attrs = {}

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return 'mdi:water'
    
    @property
    def supported_features(self):
        """Return the list of supported features."""
        return self._support_features
    
    @property
    def operation_list(self):
        return [STATE_NORMAL, STATE_WARM, STATE_BOILED]
    
    @property
    def current_operation(self):
        return self._current_operation
    
    @property
    def should_poll(self):
        return True

    @property
    def temperature_unit(self):
        """Return the unit of measurement of this entity, if any."""
        return '°C'

    @property
    def device_state_attributes(self):
        return self._state_attrs
    
    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._target_temperature
    
    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._current_temperature
    
    @property
    def min_temp(self):
        return self._min_temp

    @property
    def max_temp(self):
        return self._max_temp
    
    def update(self):
        """Get the latest data and updates the states."""
        try:
            target_temperature = self._device.send('get_prop', ["custom_tempe1"])[0]
            current_temperature = self._device.send('get_prop', ["curr_tempe"])[0]
            tds = self._device.send('get_prop', ["tds"])[0]
            water_ramain_time = self._device.send('get_prop', ["water_remain_time"])[0]
            min_set_tempe = self._device.send('get_prop', ["min_set_tempe"])[0]
            work_mode = self._device.send('get_prop', ["work_mode"])[0]

            self._target_temperature = int(target_temperature)
            self._current_temperature = int(current_temperature)
            self._min_temp = min_set_tempe

            if work_mode == 0:
                # 常温，固定水温
                self._current_operation = STATE_NORMAL
            elif work_mode == 1:
                # 温水模式
                self._current_operation = STATE_WARM
            elif work_mode == 2:
                # 开水模式
                self._current_operation = STATE_BOILED

            self._state_attrs.update({
                "tds": '{}ppm'.format(tds),
                "water_ramain_time": '{}hour'.format(water_ramain_time)
            })
        except DeviceException:
            _LOGGER.exception('Fail to get_prop from YunmiKettle')
            raise PlatformNotReady
    
    def set_temperature(self, **kwargs):
        """Set new target temperatures."""
        tempe = int(kwargs[ATTR_TEMPERATURE])
        self._device.send('set_tempe_setup', [1, tempe])
        self._target_temperature = tempe