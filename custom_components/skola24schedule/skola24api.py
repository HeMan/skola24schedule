import datetime
from typing import Optional

import aiohttp

X_SCOPE = "8a22163c-8662-4535-9050-bc5e1923df48"


# FIXME: getTimetable

class Skola24api:
    def __init__(self, client_session: aiohttp.ClientSession, skola24_host: str, unitguid: Optional[str] = None, groupguid: Optional[str] = None):
        self._skola24_host = skola24_host
        self._client_session = client_session
        self._unitguid = unitguid
        self._groupguid = groupguid
        self._headers = {"x-scope": X_SCOPE}

    async def _async_get_key(selfs) -> str:
        async with await self._client_session.post(
            "https://web.skola24.se/api/get/timetable/render/key",
            headers=self._headers
        ) as response:
            key = await response.json()
            return key["data"]["key"]
        
    async def async_get_schools(self) -> list[dict]:
        async with await self._client_session.post(
            "https://web.skola24.se/api/services/skola24/get/timetable/viewer/units",
            headers=self._headers,
            json={"getTimetableViewerUnitsRequest": {"hostName": self._skola24_host}},
        ) as response:
            schools = await response.json()
            if schools["data"]["validationErrors"]:
                raise ValueError("Unknown hostname")
            return schools["data"]["getTimetableViewerUnitsResponse"]["units"]

    async def async_get_classes(self, unitguid=None) -> list[dict]:
        if unitguid:
            self._unitguid = unitguid
        if not self._unitguid:
            raise ValueError("Unknownd guid")
        async with await self._client_session.post(
            "https://web.skola24.se/api/get/timetable/selection",
            headers=self._headers,
            json={
                "hostName": self._skola24_host,
                "unitGuid": self._unitguid,
                "filters": {
                    "class": True,
                    "course": False,
                    "group": False,
                    "period": False,
                    "room": False,
                    "student": False,
                    "subject": False,
                    "teacher": False,
                },
            },
        ) as response:
            classes = await response.json()
            if classes["error"]:
                raise ValueError("Unknown unitGuid")
            return classes["data"]["classes"]

    async def async_get_schedule(self, groupguid=None):
        if groupguid:
            self._groupguid = groupguid
        if not self._groupguid:
            raise ValueError("Unknow groupGuid")

    async def async_get_events(self, start_date: Optional[datetime.datetime]=None, end_date: Optional[datetime.datetime]=None):
        pass
