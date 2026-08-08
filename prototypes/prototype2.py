# password_manager.py
from textual.app import App, ComposeResult
from textual.widgets import Static, Input, Button
from textual.containers import Vertical
from textual.screen import Screen

passwords = {}

class HomeScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Static("🔐 Password Manager\n", id="title")
        yield Button("Add Entry", id="add")
        yield Button("List Entries", id="list")
        yield Button("Quit", id="quit")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "add": self.app.push_screen(AddEntryScreen())
            case "list": self.app.push_screen(ListEntriesScreen())
            case "quit": self.app.exit()

class AddEntryScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Static("🔑 Add New Entry")
        yield Input(placeholder="Site (e.g., Gmail)", id="site")
        yield Input(placeholder="Username", id="user")
        yield Input(placeholder="Password", password=True, id="pass")
        yield Button("Save", id="save")
        yield Button("Back", id="back")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            site = self.query_one("#site", Input).value
            user = self.query_one("#user", Input).value
            pwd = self.query_one("#pass", Input).value
            if site: passwords[site] = (user, pwd)
        self.app.pop_screen()

class ListEntriesScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Static("📄 Saved Entries:\n")
        for site, (user, _) in passwords.items():
            yield Static(f"{site} → {user}")
        yield Button("Back", id="back")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.app.pop_screen()

class PasswordApp(App):
    CSS_PATH = None
    BINDINGS = [("q", "quit", "Quit")]

    def on_mount(self) -> None:
        self.push_screen(HomeScreen())

if __name__ == "__main__":
    PasswordApp().run()
