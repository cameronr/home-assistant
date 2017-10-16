"""
Sensor for reading solar production from an Enphase Envoy through their developer API
"""

import datetime
import json
import logging
import requests
import traceback
import voluptuous as vol

import homeassistant.util.dt as dt_util

from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
from homeassistant.const import CONF_NAME

_LOGGER = logging.getLogger(__name__)

API_URL = 'https://api.enphaseenergy.com/api/v2'
CONF_API_KEY = 'api_key'
CONF_SYSTEM_ID = 'system_id'
CONF_USER_ID = 'user_id'

MIN_TIME_BETWEEN_UPDATES = datetime.timedelta(minutes=10)


class EnphaseAPI(object):
    def __init__(self, api_key, user_id, system_id):
        self._api_key = api_key
        self._user_id = user_id
        self._system_id = system_id

    def fetch_summary(self, date=None):
        try:
            if not date:
                date = dt_util.as_local(dt_util.utcnow()).strftime("%Y-%m-%d")

            _LOGGER.info('enphase fetching date: %s' %(date))
            url = "%s/systems/%s/summary?summary_date=%s&key=%s&user_id=%s" %(API_URL, self._system_id, date, self._api_key, self._user_id)

            r = requests.get(url)

            return json.loads(r.text)
        except:
            exc = traceback.format_exc()
            _LOGGER.info('enphase: %s' %(exc))

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the solar sensor"""
    _LOGGER.info('enphase setup!')

    api = EnphaseAPI(config.get(CONF_API_KEY), config.get(CONF_USER_ID), config.get(CONF_SYSTEM_ID))
    add_devices([EnphaseSensor(config.get(CONF_NAME), api)])


class EnphaseSensor(Entity):
    def __init__(self, name, api):
        """Initialize the sensor."""
        self._name = name
        self._api = api
        self._data = None
        self._summary_date = None
        self.update()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Power produced today."""
        if not self._data:
            return 0

        return round(int(self._data['energy_today']) / 1000, 2)

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement: Watts"""
        return 'kW'

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._data

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        # call to api and get power produced today
        # if current date has changed since last update, fetch power produced yesterday too
        data = self._api.fetch_summary()
        # _LOGGER.info('enphase data: %s' %(data))
        if not data:
            self._data = None
            return

        if data['summary_date'] != self._summary_date:
            # fetch yesterday's power produced
            _LOGGER.info('new day: %s' %(data['summary_date']))
            self._summary_date = data['summary_date']
            today = dt_util.as_local(dt_util.utcnow());
            yesterday = today - datetime.timedelta(days=1)
            data_yesterday = self._api.fetch_summary(yesterday.strftime('%Y-%m-%d'))
            data['energy_yesterday'] = data_yesterday['energy_today']
        else:
            data['energy_yesterday'] = self._data['energy_yesterday']

        self._data = data
