# =============================
# components/content_router.py
# =============================
import flet as ft
from pages.general_page import GeneralAppearancePage, GeneralFilesPage
from pages.notifications_page import InboxAlertsPage, FocusAssistPage

class ContentRouter:
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self._placeholder = ft.Container(expand=True, alignment=ft.alignment.center, content=ft.Text("Select a setting from the left", size=16, color=ft.colors.ON_SURFACE_VARIANT))
        self._current = self._placeholder

    def build(self):
        return ft.Container(content=self._current, expand=True, padding=20)

    def show(self, key: str):
        mapping = {
            "general.appearance": GeneralAppearancePage,
            "general.files": GeneralFilesPage,
            "notif.inbox": InboxAlertsPage,
            "notif.focus": FocusAssistPage,
        }
        cls = mapping.get(key)
        if cls:
            self._current = cls()
        else:
            self._current = ft.Container(content=ft.Text(f"No page bound to key: {key}"), expand=True)
        self.update()