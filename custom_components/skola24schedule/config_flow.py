import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant import config_entries, exceptions
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import selector

from .const import DOMAIN, HOST_NAME, UNIT_GUID, GROUP_GUID
from .skola24api import Skola24api

_LOGGER = logging.getLogger(__name__)

# FIXME: async_setup_entry


class Skola24scheduleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Skola24schedule config flow."""

    skola24api: Skola24api
    schools: list[dict]
    classes: list[dict]
    data: Optional[Dict[str, Any]]

    async def async_step_user(self, user_input=None):
        errors: Dict[str, str] = {}
        if user_input is not None:
            try:
                web_session = async_get_clientsession(self.hass)
                self.skola24api = Skola24api(web_session, user_input[HOST_NAME])
                self.schools = await self.skola24api.async_get_schools()

            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidDomain:
                # The error string is set here, and should be translated.
                # This example does not currently cover translations, see the
                # comments on `DATA_SCHEMA` for further details.
                # Set the error on the `host` field, not the entire form.
                errors["host"] = "cannot_connect"
            except Exception as exc:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception {0}".format(exc))
                errors["base"] = "unknown"
            if not errors:
                self.data = user_input
                return await self.async_step_select_school()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({(HOST_NAME): str}),
            errors=errors,
        )

    async def async_step_select_school(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input:
            self.data[UNIT_GUID] = user_input["unit"]
            self.classes = await self.skola24api.async_get_classes(self.data[UNIT_GUID])
            return await self.async_step_select_class()
        schools = [
            {"label": school["unitId"], "value": school["unitGuid"]}
            for school in self.schools
        ]

        data_units = {}
        data_units["unit"] = selector({"select": {"options": schools}})
        return self.async_show_form(
            step_id="select_school", data_schema=vol.Schema(data_units)
        )

    async def async_step_select_class(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input:
            self.data[GROUP_GUID] = user_input["class"]
            for s in self.schools:
                if s["unitGuid"] == self.data[UNIT_GUID]:
                    sname = s["unitId"]
            for k in self.classes:
                if k["groupGuid"] == self.data[GROUP_GUID]:
                    cname = k["groupName"]
            return self.async_create_entry(
                title=f"Skola24 ({sname}, {cname})", data=self.data
            )
        classes = [
            {"label": klass["groupName"], "value": klass["groupGuid"]}
            for klass in self.classes
        ]
        data_classes = {}
        data_classes["class"] = selector({"select": {"options": classes}})
        return self.async_show_form(
            step_id="select_class", data_schema=vol.Schema(data_classes)
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidDomain(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid hostname."""
