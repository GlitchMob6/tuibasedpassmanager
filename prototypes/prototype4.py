# prototype4.py
import os
from textual.app import App, ComposeResult
from textual.widgets import Button, Input, Static
from textual.screen import Screen

DATA_FILE = "passwords.txt"

def read_data_file():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return f.read().split("---\n")

def write_data_file(blocks):
    with open(DATA_FILE, "w") as f:
        f.write("---\n".join(filter(None, blocks)))

class PM(App):
    CSS_PATH = "style.tcss"
    def compose(self):
        yield Static("Password Manager", id="title")
        yield Button("Add", id="add_btn")
        yield Button("View", id="view_btn")
        yield Button("Manage", id="manage_btn")
        yield Static("", id="output")
    def on_button_pressed(self, e):
        match e.button.id:
            case "add_btn": self.push_screen(AddScreen())
            case "view_btn": self.push_screen(ViewScreen())
            case "manage_btn": self.push_screen(ManageScreen())

class AddScreen(Screen):
    def compose(self):
        yield Static("Add New Password", id="title")
        self.inputs = {k: Input(placeholder=k.replace("_", " ").title(), password="PASSWORD" in k)
                       for k in ["ENTITY_NAME", "PASSWORD", "SECURITY_Q", "SECURITY_A", "XSECURITY_Q", "XSECURITY_A"]}
        yield from self.inputs.values()
        yield Button("Save", id="save_btn")
        yield Button("Back", id="back_btn")
    def on_button_pressed(self, e):
        if e.button.id == "save_btn":
            with open(DATA_FILE, "a") as f:
                f.write('\n'.join(f"{k}: {v.value}" for k, v in self.inputs.items()) + "\n---\n")
            self.app.pop_screen()
        elif e.button.id == "back_btn": self.app.pop_screen()

class ManageScreen(Screen):
    def compose(self):
        yield Static("Manage - Enter Entity", id="title")
        yield Input(placeholder="Entity Name", id="entity_input")
        yield Button("Delete", id="del_btn")
        yield Button("Edit", id="edit_btn")
        yield Button("Back", id="back_btn")
        yield Static("", id="status")
    def on_button_pressed(self, e):
        entity = self.query_one("#entity_input", Input).value.strip()
        status = self.query_one("#status", Static)
        match e.button.id:
            case "del_btn":
                if not os.path.exists(DATA_FILE): status.update("No data.")
                else:
                    self.app.push_screen(VerifyBothScreen(entity, "delete"))
                    #yield Static("Entity Deleted Successfully!")
            case "edit_btn":
                if not os.path.exists(DATA_FILE): status.update("No data.")
                else:
                    self.app.push_screen(VerifyBothScreen(entity, "edit"))
            case "back_btn": self.app.pop_screen()

class ViewScreen(Screen):
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
                if entity:
                    self.app.push_screen(VerifyBothScreen(entity, "view"))
                else:
                    self.query_one("#status", Static).update("Entity name is required.")
            case "back_btn":
                self.app.pop_screen()

class VerifyBothScreen(Screen):
    def __init__(self, entity, action, **kwargs):
        super().__init__(**kwargs)
        self.entity = entity
        self.action = action
        self.q1 = ""    
        self.q2 = ""
    def compose(self):
        yield Static(f"Verify: {self.entity}", id="title")
        yield Static("Security Question:", id="question1_label")
        yield Static("", id="question1")  # Placeholder for the first question
        yield Input(placeholder="Answer to Security Question", id="answer1")
        yield Static("Extra Security Question:", id="question2_label")
        yield Static("", id="question2")  # Placeholder for the second question
        yield Input(placeholder="Answer to Extra Security Question", id="answer2")
        yield Button("Verify", id="verify_btn")
        yield Button("Back", id="back_btn")
        yield Static("", id="status")
    def on_mount(self): self._load_questions()
    def _load_questions(self):
        try:
            with open(DATA_FILE, "r") as f:
                for block in f.read().split("---\n"):
                    if block.strip() and f"ENTITY_NAME: {self.entity}" in block:
                        data = dict(line.split(': ', 1) for line in block.splitlines())
                        self.q1 = data.get("SECURITY_Q", "")
                        self.q2 = data.get("XSECURITY_Q", "")
                        self.query_one("#question1", Static).update(self.q1)
                        self.query_one("#question2", Static).update(self.q2)
                        return
                self.query_one("#status", Static).update(f"Entity '{self.entity}' not found.")
                self.app.pop_screen()
        except FileNotFoundError:
            self.query_one("#status", Static).update("No passwords found.")
            self.app.pop_screen()
    def on_button_pressed(self, e):
        if e.button.id == "verify_btn":
            ans1 = self.query_one("#answer1", Input).value.strip()
            ans2 = self.query_one("#answer2", Input).value.strip()
            try:
                with open(DATA_FILE, "r") as f:
                    for block in f.read().split("---\n"):
                        if block.strip() and f"ENTITY_NAME: {self.entity}" in block:
                            data = dict(line.split(': ', 1) for line in block.splitlines())
                            if data.get("SECURITY_A") == ans1 and data.get("XSECURITY_A") == ans2:
                                if self.action == "delete":
                                    self._delete_entity()
                                    
                                elif self.action == "edit":
                                    self.app.push_screen(EditScreen(block))
                                elif self.action == "view":
                                    self._view_entity(data)
                                return
                            else:
                                self.query_one("#status", Static).update("Incorrect answers.")
                                return
                self.query_one("#status", Static).update(f"Entity '{self.entity}' not found.")
            except FileNotFoundError:
                self.query_one("#status", Static).update("No passwords found.")
        elif e.button.id == "back_btn": self.app.pop_screen()
    def _delete_entity(self):
        blocks = read_data_file()
        new_blocks = [b for b in blocks if b.strip() and f"ENTITY_NAME: {self.entity}" not in b]
        write_data_file(new_blocks)
        self.app.pop_screen()
        self.query_one("#status", Static).update("Entity Deleted Successfully!")
    def _view_entity(self, data):
        # Display only the password
        password = data.get("PASSWORD", "Password not found.")
        self.query_one("#status", Static).update(f"Password: {password}")

class EditScreen(Screen):
    def __init__(self, block, **kwargs):
        super().__init__(**kwargs)
        self.data = dict(line.split(": ", 1) for line in block.splitlines())
        self.password_input = None

    def compose(self):
        yield Static(f"Edit Password for: {self.data.get('ENTITY_NAME', '')}", id="title")
        yield Static(f"Entity Name: {self.data.get('ENTITY_NAME', '')}")
        yield Static(f"Security Question: {self.data.get('SECURITY_Q', '')}")
        yield Static(f"Extra Security Question: {self.data.get('XSECURITY_Q', '')}")
        self.password_input = Input(placeholder="New Password", value=self.data.get("PASSWORD", ""), password=True)
        yield self.password_input
        yield Button("Update", id="update_btn")
        yield Button("Back", id="back_btn")
        yield Static("", id="status")

    def on_button_pressed(self, e):
        if e.button.id == "update_btn":
            new_password = self.password_input.value.strip()
            if new_password:
                blocks = read_data_file()
                new_blocks = []
                for block in blocks:
                    if f"ENTITY_NAME: {self.data['ENTITY_NAME']}" in block:
                        updated_block = []
                        for line in block.splitlines():
                            if line.startswith("PASSWORD:"):
                                updated_block.append(f"PASSWORD: {new_password}")
                            else:
                                updated_block.append(line)
                        new_blocks.append("\n".join(updated_block))
                    else:
                        new_blocks.append(block)
                write_data_file(new_blocks)
                self.app.pop_screen()
            else:
                self.query_one("#status", Static).update("Password cannot be empty!")
        elif e.button.id == "back_btn":
            self.app.pop_screen()

if __name__ == "__main__":
    PM().run()