"""기존 import 경로를 유지한다. 실제 구현은 investigation/screen_views.py에 있다."""

from .investigation.screen_views import ScreenViews

__all__ = ["ScreenViews"]
