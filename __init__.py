"""BrandMeister Event Feed"""
from homeassistant.core import HomeAssistant
from socketio import AsyncClient
from json import loads as json_loads

DOMAIN = "bm_feed"


class Trigger:
    query: str

    def __init__(self, query: str):
        self.query = query

    def __call__(self, event: dict):
        if self.query[0] == "<":
            if self.query[1] == "#":
                if self.query[2:] == event["caller"]["id"]:
                    return True
            else:
                if self.query[1:] == event["caller"]["callsign"]:
                    return True
        elif self.query[0] == ">":
            if self.query[1] == "@":
                if self.query[2] == "#":
                    if self.query[3:] == event["callee"]["id"]:
                        return True
            else:
                if self.query[1] == "#":
                    if self.query[2:] == event["callee"]["id"]:
                        return True
                else:
                    if self.query[1:] == event["callee"]["callsign"]:
                        return True

        return False

    def __str__(self):
        return self.query


async def async_setup(hass: HomeAssistant, config: dict):
    triggers = (
        [Trigger(trigger) for trigger in config[DOMAIN]["triggers"]]
        if config[DOMAIN]["triggers"]
        else None
    )

    sio = AsyncClient()
    await sio.connect(
        url="https://api.brandmeister.network",
        socketio_path="lh/socket.io",
        transports="websocket",
    )

    @sio.on("mqtt")
    async def _handler(data: dict):
        event = None
        if data["topic"] == "LH":
            payload = json_loads(data["payload"])
            if payload["Event"] == "Session-Start" and "Call" in payload["CallTypes"]:
                event = (
                    "call",
                    {
                        "caller": {
                            "id": payload["SourceID"],
                            "callsign": payload["SourceCall"],
                        },
                        "callee": {
                            "id": payload["DestinationID"],
                            "callsign": payload["DestinationCall"],
                            "is_group": "Group" in payload["CallTypes"],
                        },
                    },
                )
        if event:
            if triggers is None:
                hass.bus.async_fire(f"{DOMAIN}/{event[0]}", event[1])
            else:
                triggered = [str(trigger) for trigger in triggers if trigger(event[1])]
                if triggered:
                    hass.bus.async_fire(
                        f"{DOMAIN}/{event[0]}", {**event[1], "triggers": triggered}
                    )

    hass.async_create_task(sio.wait())
    return True
