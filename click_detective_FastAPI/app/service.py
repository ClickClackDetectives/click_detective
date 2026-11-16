"""기존 import 경로를 유지한다. 실제 구현은 investigation/service.py에 있다."""

from .investigation.service import GameService

__all__ = ["GameService"]
