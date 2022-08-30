"""BrandMeister Event Feed"""
from dataclasses import asdict
from json import loads as json_loads

from socketio import AsyncClient

from homeassistant.core import HomeAssistant
from .data import Callee, Caller, Call
from .trigger import Trigger

DOMAIN = "bm_feed"


async def async_setup(hass: HomeAssistant, config: dict):
    triggers = (
        [Trigger(query) for query in config[DOMAIN]["triggers"]]
        if "triggers" in config[DOMAIN]
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
                    Call(
                        Caller(
                            int(payload["SourceID"]),
                            str(payload["SourceCall"]),
                        ),
                        Callee(
                            int(payload["DestinationID"]),
                            str(payload["DestinationCall"]),
                            "Group" in payload["CallTypes"],
                        ),
                    ),
                )
        if event:
            if triggers is None:
                hass.bus.async_fire(f"{DOMAIN}/{event[0]}", event[1])
            else:
                triggered = [str(trigger) for trigger in triggers if trigger(event[1])]
                if triggered:
                    hass.bus.async_fire(
                        f"{DOMAIN}/{event[0]}",
                        {**asdict(event[1]), "triggers": triggered},
                    )

    hass.loop.create_task(sio.wait())
    return True
