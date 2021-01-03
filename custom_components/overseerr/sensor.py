"""Support for Overseerr."""
from datetime import timedelta
import logging

from pyoverseerr import OverseerrError

from homeassistant.helpers.entity import Entity

from .const import DOMAIN, SENSOR_TYPES

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=60)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Overseerr sensor platform."""
    if discovery_info is None:
        return

    sensors = []

    overseerr = hass.data[DOMAIN]["instance"]

    for sensor in SENSOR_TYPES:
        sensor_label = sensor
        sensor_type = SENSOR_TYPES[sensor]["type"]
        sensor_icon = SENSOR_TYPES[sensor]["icon"]
        sensors.append(OverseerrSensor(sensor_label, sensor_type, overseerr, sensor_icon))

    add_entities(sensors, True)


class OverseerrSensor(Entity):
    """Representation of an Overseerr sensor."""

    def __init__(self, label, sensor_type, overseerr, icon):
        """Initialize the sensor."""
        self._state = None
        self._label = label
        self._type = sensor_type
        self._overseerr = overseerr
        self._icon = icon
        self._last_item = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"Overseerr {self._type}"

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def last_item(self):
        """Return the state of the sensor."""
        return self._last_item

    def update(self):
        """Update the sensor."""
        try:
            if self._label == "movies":
                self._state = self._overseerr.movie_requests
                self._last_item = self._overseerr.last_movie_request
            elif self._label == "total":
                self._state = self._overseerr.total_requests
                self._last_item = self._overseerr.last_total_request
            elif self._label == "tv":
                self._state = self._overseerr.tv_requests
                self._last_item = self._overseerr.last_tv_request
            elif self._label == "music":
                self._state = self._overseerr.music_requests
            elif self._label == "pending":
                self._last_item = self._overseerr.last_pending_request
                self._state = self._overseerr.pending_requests
            elif self._label == "approved":
                self._state = self._overseerr.approved_requests
            elif self._label == "available":
                self._state = self._overseerr.available_requests
        except OverseerrError as err:
            _LOGGER.warning("Unable to update Overseerr sensor: %s", err)
            self._state = None
