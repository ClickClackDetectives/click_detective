"""기존 import 경로를 유지한다. 실제 구현은 cases/catalog.py에 있다."""

from .cases.catalog import Catalog

__all__ = ["Catalog"]
