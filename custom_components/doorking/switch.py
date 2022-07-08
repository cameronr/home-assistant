"""
Support for a Doorking 1812AP using the web api I hacked up
"""
import logging
import voluptuous as vol
import requests

from homeassistant.components.switch import (SwitchEntity)

_LOGGER = logging.getLogger(__name__)

CONF_NAME = 'name'
CONF_HOST = 'host'
CONF_PORT = 'port'

class DoorkingAPI(object):
    def __init__(self, host, port):
        self._host = host
        self._port = port

    def _execute(self, method):
        if method != 'open' and method != 'close' and method != 'status':
            raise RuntimeError('Invalid method: %s' %(method))

        r = requests.get("http://%s:%s/%sGate" %(self._host, self._port, method))
        return r.text

    def openGate(self):
        return self._execute('open');

    def closeGate(self):
        return self._execute('close');

    def gateStatus(self):
        return self._execute('status');


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the switch platform."""
    _LOGGER.info('doorking setup!')
    add_devices([Doorking(config.get(CONF_NAME), config.get(CONF_HOST), config.get(CONF_PORT))])


class Doorking(SwitchEntity):
    def __init__(self, name, host, port):
        """Initialize the sensor."""
        self._name = name
        self._api = DoorkingAPI(host, port)
        self._state = None
        self.update()

    def turn_on(self, **kwargs):
        """Turn device on."""
        self._api.openGate()

    def turn_off(self, **kwargs):
        """Turn device off."""
        self._api.closeGate()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def is_on(self):
        """Return true if sensor is on."""
        return self._state == "open"

    @property
    def should_poll(self):
        """Polling is needed."""
        return True

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = self._api.gateStatus()
