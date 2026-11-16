"""기존 import 경로를 유지한다. 실제 구현은 investigation/schemas.py에 있다."""

from .investigation.schemas import (
    DTO,
    Accuse,
    Advance,
    Command,
    Examine,
    Infer,
    Interrogate,
    Key,
    NewGame,
    Notes,
    Source,
)

__all__ = [
    "Key",
    "DTO",
    "NewGame",
    "Command",
    "Examine",
    "Interrogate",
    "Source",
    "Infer",
    "Advance",
    "Notes",
    "Accuse",
]
