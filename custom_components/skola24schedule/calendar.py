import datetime
from typing import Callable

from homeassistant import core, config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, UNIT_GUID, GROUP_GUID, HOST_NAME

from homeassistant.components.calendar import (
    ENTITY_ID_FORMAT,
    PLATFORM_SCHEMA,
    CalendarEntity,
    CalendarEvent,
    extract_offset,
    is_offset_reached,
)

from .skola24api import Skola24api


class Skola24CalendarEntity(CalendarEntity):
    def __init__(self, skola24api, config):
        self.skola24api = skola24api
        self._event: CalendarEvent | None = None
        self._name = "Jidgo"
        self.config = config
    @property
    def event(self) -> CalendarEvent | None:
        return self._event

    async def async_get_events(
        self,
        hass: core.HomeAssistant,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
    ) -> list[CalendarEvent]:
        return await self.skola24api.async_get_events(start_date, end_date)


async def async_setup_entry(hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    config = hass.data[DOMAIN][config_entry.entry_id]
    session = async_get_clientsession(hass)
    skola24api = Skola24api(session, config[HOST_NAME], config[UNIT_GUID], config[GROUP_GUID])
    calendar = Skola24CalendarEntity(skola24api, config)
    async_add_entities([calendar], update_before_add=True)

