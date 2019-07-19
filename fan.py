import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.exceptions import (PlatformNotReady)
from homeassistant.components.fan import (SPEED_OFF, SPEED_LOW, SPEED_MEDIUM, SPEED_HIGH,
                                          FanEntity, SUPPORT_SET_SPEED,
                                          SUPPORT_OSCILLATE, SUPPORT_DIRECTION)
from homeassistant.const import (STATE_UNKNOWN, ATTR_ENTITY_ID, CONF_NAME, CONF_HOST, CONF_TOKEN, )
from datetime import timedelta
from miio import Device, DeviceException
from . import DOMAIN

import logging
_LOGGER = logging.getLogger(__name__)

SERVICE_SET_LIGHT_ON = "set_light_on"
SERVICE_SET_LIGHT_OFF = "set_light_off"
SET_LIGHT_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.entity_id
})
YUNMI_FAN_DEVICES = "yunmi_fan_devices"

def setup_platform(hass, config, add_devices, discovery_info=None):
    host = config.get(CONF_HOST)
    name = config.get(CONF_NAME)
    token = config.get(CONF_TOKEN)

    _LOGGER.info("Initializing Yunmi Hood with host %s (token %s...)", host, token[:5])

    devices = []
    try:
        device = Device(host, token)
        yumihood = YunmiHood(device, name)
        devices.append(yumihood)
    except DeviceException:
        _LOGGER.exception('Fail to setup yunmi hood')
        raise PlatformNotReady

    add_devices(devices)
    hass.data[YUNMI_FAN_DEVICES] = devices

    def service_handle(service):
        entity_id = service.data[ATTR_ENTITY_ID]
        device = next((fan for fan in hass.data[YUNMI_FAN_DEVICES] if
                           fan.entity_id == entity_id), None)
        if device is None:
            _LOGGER.warning("Unable to find yunmi fan device %s",
                            str(entity_id))
            return

        if service.service == SERVICE_SET_LIGHT_ON:
            device.set_light_on()

        if service.service == SERVICE_SET_LIGHT_OFF:
            device.set_light_off()

    hass.services.register(DOMAIN, SERVICE_SET_LIGHT_ON, service_handle, schema=SET_LIGHT_SCHEMA)
    hass.services.register(DOMAIN, SERVICE_SET_LIGHT_OFF, service_handle, schema=SET_LIGHT_SCHEMA)

class YunmiHood(FanEntity):

    def __init__(self, device, name) -> None:
        self._device = device
        self._name = name
        self._supported_features = SUPPORT_SET_SPEED
        self._is_on = False
        self._wind_state = 0
        self._is_light_on = False
        self._state_attrs = {}

    @property
    def name(self) -> str:
        return self._name

    @property
    def supported_features(self) -> int:
        return self._supported_features

    @property
    def should_poll(self):
        return True

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        return self._state_attrs

    @property
    def speed_list(self) -> list:
        return [SPEED_OFF, SPEED_LOW, SPEED_MEDIUM, SPEED_HIGH]

    def update(self):
        try:
            power_state = self._device.send('get_prop', ["power_state"])[0]
            wind_state = self._device.send('get_prop', ["wind_state"])[0]
            light_state = self._device.send('get_prop', ["light_state"])[0]
            stove1_data = self._device.send('get_prop', ["stove1_data"])[0]
            stove2_data = self._device.send('get_prop', ["stove2_data"])[0]

            _LOGGER.debug('update yunmi hood status: %s %s %s %s %s', power_state, wind_state, light_state, stove1_data, stove2_data)

            self._is_on = power_state != 0
            self._wind_state = wind_state
            self._is_light_on = light_state != 0
            self._state_attrs.update({
                "stove1_is_on": stove1_data,
                "stove2_is_on": stove2_data,
            })

        except DeviceException:
            _LOGGER.exception('Fail to get_prop from Yunmi Hood')
            raise PlatformNotReady

    @property
    def speed(self) -> str:
        if not self._is_on:
            return SPEED_OFF
            
        if self._wind_state == 4:
            return SPEED_HIGH
        if self._wind_state == 16:
            return SPEED_MEDIUM
        if self._wind_state == 1:
            return SPEED_LOW
        if self._wind_state == 0:
            return SPEED_OFF
    
    def set_speed(self, speed: str) -> None:
        if speed == SPEED_OFF:
            self.turn_off()
            return

        if speed == SPEED_LOW:
            self._device.send('set_wind', [1])
            self._wind_state = 1
        elif speed == SPEED_MEDIUM:
            self._device.send('set_wind', [16])
            self._wind_state = 16
        elif speed == SPEED_HIGH:
            self._device.send('set_wind', [4])
            self._wind_state = 4
    
    def set_light_on(self) -> None:
        if not self._is_light_on:
            self._device.send('set_light', [1])
            self._is_light_on = True

    def set_light_off(self) -> None:
        if self._is_light_on:
            self._device.send('set_light', [0])
            self._is_light_on = False

    def turn_on(self, speed: str = None, **kwargs) -> None:
        if not self._is_on:
            self._device.send('set_power', [2])
            self._is_on = True

        if speed:
            self.set_speed(speed)

    def turn_off(self, **kwargs) -> None:
        if self._is_on:
            self._device.send('set_power', [0])
            self._is_on = False
