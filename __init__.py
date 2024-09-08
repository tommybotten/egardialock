import logging

from . import egardiadevice
import requests
import voluptuous as vol

from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
    EVENT_HOMEASSISTANT_STOP,
    Platform,
)

from homeassistant.helpers import discovery
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)
CONF_VERSION = "version"

DEFAULT_NAME = "Egardia"
DEFAULT_PORT = 80
DEFAULT_VERSION = "GATE-01"

DOMAIN = "egardialock"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_HOST): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
                vol.Required(CONF_USERNAME): cv.string,
                vol.Optional(CONF_VERSION, default=DEFAULT_VERSION): cv.string,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Egardia platform."""

    conf = config[DOMAIN]
    username = conf[CONF_USERNAME]
    password = conf[CONF_PASSWORD]
    host = conf[CONF_HOST]
    port = conf[CONF_PORT]
    version = conf[CONF_VERSION]

    try:
        device = hass.data[DOMAIN] = egardiadevice.EgardiaDevice(
            host, port, username, password, "", version
        )
    except egardiadevice.UnauthorizedError:
        _LOGGER.error("Unable to authorize. Wrong password or username")
        return False

    # Load the lock platform
    discovery.load_platform(hass, Platform.LOCK, DOMAIN, {}, config)

    return True