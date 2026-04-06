import flet as ft


class InboxAlertsPage:
    def build(self):
        return ft.Column([
            ft.Text("Inbox alerts", size=22, weight=ft.FontWeight.W_600),
            ft.Divider(),
            ft.Switch(label="Show badges on taskbar", value=True),
            ft.Switch(label="Play notification sound", value=False),
        ], expand=True)
class FocusAssistPage:
    def build(self):
        return ft.Column([
            ft.Text("Focus assist", size=22, weight=ft.FontWeight.W_600),
            ft.Divider(),
            ft.RadioGroup(content=ft.Column([
                ft.Radio(value="off", label="Off"),
                ft.Radio(value="priority", label="Priority only"),
                ft.Radio(value="alarms", label="Alarms only"),
            ]), value="priority"),
        ], expand=True)