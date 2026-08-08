import os
from textual.app import App, ComposeResult
from textual.widgets import Button, Input, Static
from textual.screen import Screen

DATA_FILE = "passwords.txt"

class Main_Window(App):
    CSS_PATH = "style.tcss"
    def compose(self):
        yield Static("Password Manager", id="title")
        yield Button("Add Password", id="add_btn")
        yield Button("View Password", id="view_btn")
        yield Button("Manage Password", id="manage_btn")
        yield Static("", id="output")
    def on_button_pressed(self, e):
        match e.button.id:
            case "add_btn": self.push_screen(Add_Screen())
            case "view_btn": self.push_screen(View_Screen())
          #  case "manage_btn": self.push_screen(Manage_Screen())

class Add_Screen(Screen):
    def compose(self):
        yield Static("Add New Password", id="title")
        self.inputs = {k: Input(placeholder=k.replace("_", " ").title(), password="PASSWORD" in k)
                       for k in ["ENTITY_NAME", "PASSWORD", "SECURITY_Q", "SECURITY_A", "XSECURITY_Q", "XSECURITY_A"]} #added password = PASSWORD as it showed mulitple errors - Tinesh
        yield from self.inputs.values()
        yield Button("Save", id="save_btn")
        yield Button("Back", id="back_btn")
    def on_button_pressed(self, e):
        if e.button.id == "save_btn":
            with open(DATA_FILE, "a") as f:
                f.write('\n'.join(f"{k}: {v.value}" for k, v in self.inputs.items()) + "\n---\n")
            self.app.pop_screen()
        elif e.button.id == "back_btn": self.app.pop_screen()

class View_Screen(Screen):
    def compose(self):
        yield Static("View Password - Enter Entity", id="title")
        yield Input(placeholder="Entity Name", id="entity_input")
        yield Button("Next", id="next_btn")
        yield Button("Back", id="back_btn")
        yield Static("", id="status")
    def on_button_pressed(self, e):
        match e.button.id:
            case "next_btn":
                entity = self.query_one("#entity_input", Input).value.strip()
                if entity: self.app.push_screen(VerifyScreen(entity))
                else: self.query_one("#status", Static).update("Enter entity name.")
            case "back_btn": self.app.pop_screen()

class VerifyScreen(Screen):
    def __init__(self, entity):
        super().__init__()
        self.entity = entity
        self.q = "" # q is used to refer question - Pushkar
    def compose(self):
        yield Static(f"Verify: {self.entity}", id="title")
        yield Static("Loading Question...", id="question")
        yield Input(placeholder="Answer", id="answer")
        yield Button("Verify", id="verify_btn")
        yield Button("Back", id="back_btn")
        yield Static("", id="status") # advised by the friend, so as to avoid the error we catched.
    def on_mount(self): self._load_q()
    def _load_q(self):
        try:
            with open(DATA_FILE, "r") as f:
                for block in f.read().split("---\n"):
                    if block.strip() and f"ENTITY_NAME: {self.entity}" in block:
                        for line in block.splitlines():
                            if line.startswith("SECURITY_Q:"):
                                self.q = line[len("SECURITY_Q:"):].strip()
                                self.query_one("#question", Static).update(f"Q: {self.q}")
                                return
                self.query_one("#status", Static).update(f"Entity '{self.entity}' not found.")
                self.app.pop_screen() # ain't working anyways though let's keep it - Pushkar
        except FileNotFoundError:
            self.query_one("#status", Static).update("No passwords found.")
            self.app.pop_screen()
    def on_button_pressed(self, e):
        if e.button.id == "verify_btn":
            ans = self.query_one("#answer", Input).value.strip()
            try:
                with open(DATA_FILE, "r") as f:
                    for block in f.read().split("---\n"):
                        if block.strip() and f"ENTITY_NAME: {self.entity}" in block:
                            data = dict(line.split(': ', 1) for line in block.splitlines())
                            if data.get("SECURITY_A") == ans:
                                self.app.push_screen(Display_Screen(self.entity, data.get("PASSWORD", "")))
                                return
                            else:
                                self.query_one("#status", Static).update("Incorrect answer.")
                                return
                self.query_one("#status", Static).update(f"Entity '{self.entity}' not found.")
            except FileNotFoundError:
                self.query_one("#status", Static).update("No passwords found.")
        elif e.button.id == "back_btn": self.app.pop_screen()

class Display_Screen(Screen):
    def __init__(self, entity, password, **kwargs):
        super().__init__(**kwargs)
        self.entity = entity
        self.passw = password
    def compose(self):
        yield Static(f"Password for {self.entity}", id="title")
        yield Static(f"Password: {self.passw}", id="password_output")
        yield Button("Back", id="back_btn")
    def on_button_pressed(self, e):
        if e.button.id == "back_btn": self.app.pop_screen()

    if __name__ == "__main__":
        Main_Window().run()