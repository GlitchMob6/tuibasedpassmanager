
import os
from textual.app import App, ComposeResult
from textual.widgets import Button, Input, Static
from textual.containers import Vertical
from textual.screen import Screen

DATA_FILE = "passwords.txt"

class PasswordManager(App):
    CSS_PATH = "app.tcss"

    def compose(self) -> ComposeResult:
        yield Static("Password Manager", id="title")
        yield Button("Add Password", id="add_btn")
        yield Button("View Passwords", id="view_btn")
        yield Button("Manage Passwords", id="manage_btn")
        yield Static("", id="output")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "add_btn":
            self.push_screen(AddPasswordScreen())
        elif button_id == "view_btn":
            self.push_screen(RequestEntityScreen())
        elif button_id == "manage_btn":
            self.push_screen(ManagePasswordScreen())

class AddPasswordScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Static("Add New Password", id="title")
        self.inputs = {
            "ENTITY_NAME": Input(placeholder="Entity Name"),
            "PASSWORD": Input(placeholder="Password", password=True),
            "SECURITY_Q": Input(placeholder="Security Question"),
            "SECURITY_A": Input(placeholder="Security Answer"),
            "XSECURITY_Q": Input(placeholder="Extra Security Question"),
            "XSECURITY_A": Input(placeholder="Extra Security Answer"),
        }
        for input_widget in self.inputs.values():
            yield input_widget
        yield Button("Save", id="save_btn")
        yield Button("Back", id="back_btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save_btn":
            with open(DATA_FILE, "a") as f:
                for label, widget in self.inputs.items():
                    f.write(f"{label}: {widget.value}\n")
                f.write("---\n")
            self.app.pop_screen()
        elif event.button.id == "back_btn":
            self.app.pop_screen()

class RequestEntityScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Static("Enter Entity Name to View Password", id="title")
        self.entity_input = Input(placeholder="Entity Name")
        yield self.entity_input
        yield Button("Next", id="next_btn")
        yield Button("Back", id="back_btn")
        yield Static("", id="status")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "next_btn":
            entity_name = self.entity_input.value.strip()
            if entity_name:
                self.app.push_screen(VerifySecurityScreen(entity_name))
            else:
                self.query_one("#status", Static).update("Please enter an entity name.")
        elif event.button.id == "back_btn":
            self.app.pop_screen()

class VerifySecurityScreen(Screen):
    def __init__(self, entity_name: str, **kwargs):
        super().__init__(**kwargs)
        self.entity_name = entity_name
        self.security_question = ""

    def compose(self) -> ComposeResult:
        yield Static(f"Verification for: {self.entity_name}", id="title")
        yield Static("Loading Security Question...", id="question")
        yield Input(placeholder="Your Answer", id="answer_input")
        yield Button("Verify", id="verify_btn")
        yield Button("Back", id="back_btn")
        yield Static("", id="status")

    def on_mount(self) -> None:
        self.load_security_question()

    def load_security_question(self):
        if not os.path.exists(DATA_FILE):
            self.query_one("#status", Static).update("No passwords found.")
            return

        with open(DATA_FILE, "r") as f:
            blocks = f.read().split("---\n")
            for block in blocks:
                if block.strip():
                    lines = block.strip().split("\n")
                    entity_found = False
                    for line in lines:
                        if line.startswith("ENTITY_NAME:") and line.split(": ")[1] == self.entity_name:
                            entity_found = True
                            break
                    if entity_found:
                        for line in lines:
                            if line.startswith("SECURITY_Q:"):
                                security_q_part = line[len("SECURITY_Q:"):].strip()
                                self.security_question = security_q_part
                                self.query_one("#question", Static).update(f"Security Question: {self.security_question}")
                                return
                        self.query_one("#status", Static).update(f"Security question not found for '{self.entity_name}'.")
                        self.app.pop_screen()
                        return

        self.query_one("#status", Static).update(f"Entity '{self.entity_name}' not found.")
        self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "verify_btn":
            user_answer = self.query_one("#answer_input", Input).value.strip()
            if not os.path.exists(DATA_FILE):
                self.query_one("#status", Static).update("No passwords found.")
                return

            with open(DATA_FILE, "r") as f:
                blocks = f.read().split("---\n")
                for block in blocks:
                    if block.strip():
                        lines = block.strip().split("\n")
                        for line in lines:
                            if line.startswith("ENTITY_NAME:") and line.split(": ")[1] == self.entity_name:
                                for l in lines:
                                    if l.startswith("SECURITY_A:"):
                                        stored_answer = l.split(": ")[1]
                                        if user_answer == stored_answer:
                                            password = ""
                                            for l in lines:
                                                if l.startswith("PASSWORD:"):
                                                    password = l.split(": ")[1]
                                                    break
                                            self.app.push_screen(DisplayPasswordScreen(self.entity_name, password))
                                            return
                                        else:
                                            self.query_one("#status", Static).update("Incorrect security answer.")
                                            return
            self.query_one("#status", Static).update(f"Entity '{self.entity_name}' not found.")
            self.app.pop_screen()

        elif event.button.id == "back_btn":
            self.app.pop_screen()

class DisplayPasswordScreen(Screen):
    def __init__(self, entity_name: str, password: str, **kwargs):
        super().__init__(**kwargs)
        self.entity_name = entity_name
        self.password = password

    def compose(self) -> ComposeResult:
        yield Static(f"Password for {self.entity_name}", id="title")
        yield Static(f"Password: {self.password}", id="password_output")
        yield Button("Back", id="back_btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back_btn":
            self.app.pop_screen()

class ManagePasswordScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Static("Enter Entity Name to Modify/Delete", id="title")
        self.input_entity = Input(placeholder="Entity Name")
        yield self.input_entity
        yield Button("Delete", id="delete_btn")
        yield Button("Edit", id="edit_btn")
        yield Button("Back", id="back_btn")
        yield Static("", id="status")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        status = self.query_one("#status", Static)
        entity_to_manage = self.input_entity.value.strip()

        if event.button.id == "delete_btn":
            if not os.path.exists(DATA_FILE):
                status.update("No data to modify.")
                return

            with open(DATA_FILE, "r") as f:
                blocks = f.read().split("---\n")

            new_blocks = []
            found = False
            for block in blocks:
                if block.strip():
                    lines = block.strip().split("\n")
                    entity_name = ""
                    for line in lines:
                        if line.startswith("ENTITY_NAME:") and line.split(": ")[1] == entity_to_manage:
                            found = True
                            break
                    else:
                        new_blocks.append(block)

            if found:
                with open(DATA_FILE, "w") as f:
                    f.write("---\n".join(filter(None, new_blocks)))
                status.update(f"Deleted entry for: {entity_to_manage}")
            else:
                status.update("Entity not found.")

        elif event.button.id == "edit_btn":
            if not os.path.exists(DATA_FILE):
                status.update("No data to modify.")
                return

            with open(DATA_FILE, "r") as f:
                content = f.read()
                blocks = content.split("---\n")

            entry_data = None
            for block in blocks:
                if block.strip():
                    lines = block.strip().split("\n")
                    entity_name = ""
                    data = {}
                    for line in lines:
                        if line.startswith("ENTITY_NAME:"):
                            entity_name = line.split(": ")[1]
                        data[line.split(": ")[0]] = line.split(": ")[1]
                    if entity_name == entity_to_manage:
                        entry_data = data
                        break

            if entry_data:
                self.app.push_screen(EditPasswordScreen(entry_data))
            else:
                status.update("Entity not found.")

        elif event.button.id == "back_btn":
            self.app.pop_screen()

class EditPasswordScreen(Screen):
    def __init__(self, data: dict, **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self.inputs = {}

    def compose(self) -> ComposeResult:
        yield Static(f"Edit Password for: {self.data['ENTITY_NAME']}", id="title")
        self.inputs = {
            "ENTITY_NAME": Input(placeholder="Entity Name", value=self.data.get("ENTITY_NAME", "")),
            "PASSWORD": Input(placeholder="Password", password=True, value=self.data.get("PASSWORD", "")),
            "SECURITY_Q": Input(placeholder="Security Question", value=self.data.get("SECURITY_Q", "")),
            "SECURITY_A": Input(placeholder="Security Answer", value=self.data.get("SECURITY_A", "")),
            "XSECURITY_Q": Input(placeholder="Extra Security Question", value=self.data.get("XSECURITY_Q", "")),
            "XSECURITY_A": Input(placeholder="Extra Security Answer", value=self.data.get("XSECURITY_A", "")),
        }
        for input_widget in self.inputs.values():
            yield input_widget
        yield Button("Update", id="update_btn")
        yield Button("Back", id="back_btn")
        yield Static("", id="status")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "update_btn":
            updated_data = {label: widget.value for label, widget in self.inputs.items()}
            entity_to_update = updated_data.get("ENTITY_NAME")

            if entity_to_update:
                with open(DATA_FILE, "r") as f:
                    blocks = f.read().split("---\n")

                new_blocks = []
                found = False
                for block in blocks:
                    if block.strip():
                        lines = block.strip().split("\n")
                        entity_name = ""
                        for line in lines:
                            if line.startswith("ENTITY_NAME:") and line.split(": ")[1] == self.data["ENTITY_NAME"]:
                                found = True
                                new_block_lines = [f"{key}: {value}" for key, value in updated_data.items()]
                                new_blocks.append("\n".join(new_block_lines))
                                break
                        else:
                            new_blocks.append(block)
                    else:
                        new_blocks.append("")

                if found:
                    with open(DATA_FILE, "w") as f:
                        f.write("---\n".join(filter(None, new_blocks)))
                    self.app.pop_screen()
                else:
                    self.query_one("#status", Static).update("Error: Entity not found during update.")

            else:
                self.query_one("#status", Static).update("Error: Entity Name cannot be empty.")

        elif event.button.id == "back_btn":
            self.app.pop_screen()

if __name__ == "__main__":
    app = PasswordManager()
    app.run()