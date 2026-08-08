from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import (
    Static,
    Button,
    Input,
    Label,
    ListView,
    ListItem,
)
from textual.screen import Screen
from textual.reactive import reactive
import os

PASSWORD_FILE = "passwords.txt"


class PasswordManagerApp(App):
    CSS_PATH = None

    def compose(self) -> ComposeResult:
        yield Label("Password Manager", id="header")
        yield Button("View Password", id="view_password")
        yield Button("Edit Password", id="edit_password")
        yield Button("Delete Password", id="delete_password")
        yield Button("Add Password", id="add_password")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "add_password":
                self.push_screen(AddPasswordScreen())
            case "view_password":
                self.push_screen(ViewEntityScreen(mode="view"))
            case "edit_password":
                self.push_screen(ViewEntityScreen(mode="edit"))
            case "delete_password":
                self.push_screen(ViewEntityScreen(mode="delete"))


class ViewEntityScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Go Back")]

    def __init__(self, mode: str):
        super().__init__()
        self.mode = mode
        self.selected_entity = None

    def compose(self) -> ComposeResult:
        yield Label(f"Select entity to {self.mode}:")
        entity_list = ListView(*[
            ListItem(Label(line.split("|")[0]))
            for line in open(PASSWORD_FILE).readlines()
        ])
        entity_list.id = "entity_list"
        yield entity_list
        yield Button("Select", id="select_entity")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "select_entity":
            list_widget: ListView = self.query_one("#entity_list")
            selected: ListItem = list_widget.get_item_at(list_widget.index)
            if selected:
                self.selected_entity = selected.label.renderable
                if self.mode == "view":
                    self.app.push_screen(ViewPasswordScreen(self.selected_entity))
                else:
                    self.app.push_screen(VerifySecurityScreen(self.selected_entity, self.mode))


class VerifySecurityScreen(Screen):
    def __init__(self, entity: str, mode: str):
        super().__init__()
        self.entity = entity
        self.mode = mode
        self.security_answer = ""
        self.extra_security_answer = ""
        self.stage = reactive("security")

    def compose(self) -> ComposeResult:
        yield Label(f"Security verification for: {self.entity}")
        self.security_input = Input(placeholder="Security Answer", id="security_input")
        yield self.security_input
        yield Button("Verify", id="verify_btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "verify_btn":
            answer = self.security_input.value.strip()
            self.security_answer = answer
            self.security_input.value = ""
            self.security_input.placeholder = "Extra Security Answer"
            event.button.id = "final_verify_btn"
        elif event.button.id == "final_verify_btn":
            extra_answer = self.security_input.value.strip()

            for line in open(PASSWORD_FILE):
                entity, pwd, sec, extra = line.strip().split("|")
                if entity == self.entity and sec == self.security_answer and extra == extra_answer:
                    if self.mode == "edit":
                        self.app.push_screen(EditPasswordScreen(entity))
                    elif self.mode == "delete":
                        self.app.push_screen(DeletePasswordScreen(entity))
                    return
            self.app.pop_screen()
            self.app.push_screen(MessageScreen("Security verification failed!"))


class ViewPasswordScreen(Screen):
    def __init__(self, entity: str):
        super().__init__()
        self.entity = entity

    def compose(self) -> ComposeResult:
        password = "Not found"
        for line in open(PASSWORD_FILE):
            entity, pwd, *_ = line.strip().split("|")
            if entity == self.entity:
                password = pwd
                break
        yield Label(f"Password for {self.entity}: {password}")
        yield Button("Back", id="back_btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.app.pop_screen()


class AddPasswordScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Label("Add New Password")
        self.entity_input = Input(placeholder="Entity")
        self.password_input = Input(placeholder="Password")
        self.security_input = Input(placeholder="Security Answer")
        self.extra_input = Input(placeholder="Extra Security Answer")
        yield self.entity_input
        yield self.password_input
        yield self.security_input
        yield self.extra_input
        yield Button("Save", id="save_btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        entity = self.entity_input.value.strip()
        password = self.password_input.value.strip()
        security = self.security_input.value.strip()
        extra = self.extra_input.value.strip()
        if all([entity, password, security, extra]):
            with open(PASSWORD_FILE, "a") as f:
                f.write(f"{entity}|{password}|{security}|{extra}\n")
            self.app.pop_screen()
            self.app.push_screen(MessageScreen("Password added!"))


class EditPasswordScreen(Screen):
    def __init__(self, entity: str):
        super().__init__()
        self.entity = entity

    def compose(self) -> ComposeResult:
        yield Label(f"Edit Password for: {self.entity}")
        self.input = Input(placeholder="New Password")
        yield self.input
        yield Button("Update", id="update_btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        new_pwd = self.input.value.strip()
        if new_pwd:
            lines = open(PASSWORD_FILE).readlines()
            with open(PASSWORD_FILE, "w") as f:
                for line in lines:
                    parts = line.strip().split("|")
                    if parts[0] == self.entity:
                        f.write(f"{self.entity}|{new_pwd}|{parts[2]}|{parts[3]}\n")
                    else:
                        f.write(line)
            self.app.pop_screen()
            self.app.push_screen(MessageScreen("Password updated!"))


class DeletePasswordScreen(Screen):
    def __init__(self, entity: str):
        super().__init__()
        self.entity = entity

    def compose(self) -> ComposeResult:
        yield Label(f"Are you sure you want to delete password for: {self.entity}?")
        yield Button("Yes", id="yes_btn")
        yield Button("No", id="no_btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes_btn":
            lines = open(PASSWORD_FILE).readlines()
            with open(PASSWORD_FILE, "w") as f:
                for line in lines:
                    if not line.startswith(self.entity + "|"):
                        f.write(line)
            self.app.pop_screen()
            self.app.push_screen(MessageScreen("Password deleted!"))
        else:
            self.app.pop_screen()


class MessageScreen(Screen):
    def __init__(self, message: str):
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        yield Label(self.message)
        yield Button("OK", id="ok_btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.app.pop_screen()


if __name__ == "__main__":
    if not os.path.exists(PASSWORD_FILE):
        open(PASSWORD_FILE, "w").close()
    app = PasswordManagerApp()
    app.run()
