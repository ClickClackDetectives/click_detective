"""기존 import 경로를 유지한다. 실제 구현은 investigation/presentation.py에 있다."""

from .investigation.presentation import Presenter

__all__ = ["Presenter"]
