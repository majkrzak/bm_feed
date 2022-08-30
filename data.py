from dataclasses import dataclass


@dataclass
class Caller:
    id: int
    callsign: str


@dataclass
class Callee:
    id: int
    callsign: str
    is_group: bool


@dataclass
class Call:
    caller: Caller
    callee: Callee
