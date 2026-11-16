"""기존 import 경로를 유지한다. 실제 구현은 investigation/repository.py에 있다."""

from .investigation.repository import Repository, digest

__all__ = ["Repository", "digest"]
