"""Support for Egardia locks."""
from __future__ import annotations

import logging

from homeassistant.components.lock import LockEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from . import DOMAIN
_LOGGER = logging.getLogger(__name__)



def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the Egardia lock platform."""
    device = hass.data[DOMAIN]
    
    try:
        # Get all locks from the device
        locks = device.getlocks()
        
        # Create a list to hold all lock entities
        lock_entities = []
        
        # Iterate through all locks and create an EgardiaLock entity for each
        for lock_id, lock_info in locks.items():
            lock_name = lock_info.get('name', f"Egardia Lock {lock_id}")
            lock_entities.append(EgardiaLock(device, lock_id, lock_name))
        
        # Add all lock entities
        add_entities(lock_entities, True)
    except Exception as e:
        _LOGGER.error(f"Error setting up Egardia lock platform: {str(e)}")



class EgardiaLock(LockEntity):
    """Representation of an Egardia lock."""

    def __init__(self, device, lock_id, name):
        """Initialize the lock."""
        self._device = device
        self._lock_id = lock_id
        self._name = name
        self._state = None

    @property
    def should_poll(self):
        """Return True if entity has to be polled for state."""
        return True

    @property
    def name(self):
        """Return the name of the lock."""
        return self._name

    @property
    def is_locked(self):
        """Return true if lock is locked."""
        return self._state == "locked"

    def lock(self, **kwargs):
        """Lock the device."""
        self._device.set_lock_state(self._lock_id, "lock")

    def unlock(self, **kwargs):
        """Unlock the device."""
        self._device.set_lock_state(self._lock_id, "unlock")

    def update(self):
        """Get the latest data."""
        try:
            new_state = self._device.getlockstate(self._lock_id)
            if new_state != self._state:
                self._state = new_state
                _LOGGER.info(f"Lock {self._name} state changed to {self._state}")
        except Exception as e:
            _LOGGER.error(f"Error updating lock {self._name}: {str(e)}")
    

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"egardialock_{self._lock_id}"