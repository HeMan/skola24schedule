"""
The "hello world" custom component.

This component implements the bare minimum that a component should implement.

Configuration:

To use the hello_world component you will need to add the following to your
configuration.yaml file.

hello_world_async:
"""
from __future__ import annotations


from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.aiohttp_client import async_get_clientsession

# The domain of your component. Should be equal to the name of your component.
from .const import DOMAIN
from .skola24api import Skola24api


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Setup our skeleton component."""
    # States are in the format DOMAIN.OBJECT_ID.
    hass.data.setdefault(DOMAIN, {})
    hass.states.async_set("skola24schedule.Hello_World", "Works!")

    # Return boolean to indicate that initialization was successfully.
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = dict(entry.data)


    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, Platform.CALENDAR)
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, Platform.CALENDAR):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
