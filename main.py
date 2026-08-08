import os
from textual.app import App, ComposeResult
from textual.widgets import Button, Input, Static, Header, Footer
from textual.screen import Screen

from vault_manager import VaultManager

class MasterPasswordScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_new_vault = False

    def on_mount(self) -> None:
        self.is_new_vault = not self.app.vault.exists()
        if self.is_new_vault:
            self.query_one("#title", Static).update("🔐 Create Master Password")
            self.query_one("#subtitle", Static).update("Welcome! Set up a Master Password for your encrypted vault.")
            self.query_one("#confirm_input", Input).display = True
            self.query_one("#submit_btn", Button).label = "Create Vault"
        else:
            self.query_one("#title", Static).update("🔐 SecurePass Vault Locked")
            self.query_one("#subtitle", Static).update("Enter your Master Password to unlock.")
            self.query_one("#confirm_input", Input).display = False
            self.query_one("#submit_btn", Button).label = "Unlock Vault"

    def compose(self) -> ComposeResult:
        yield Static("", id="title")
        yield Static("", id="subtitle")
        yield Input(placeholder="Master Password", password=True, id="pass_input")
        yield Input(placeholder="Confirm Master Password", password=True, id="confirm_input")
        yield Button("Submit", id="submit_btn")
        yield Static("", id="status")

    def on_button_pressed(self, e) -> None:
        if e.button.id == "submit_btn":
            pwd = self.query_one("#pass_input", Input).value.strip()
            status = self.query_one("#status", Static)
            if not pwd:
                status.update("Master password cannot be empty.")
                return

            if self.is_new_vault:
                confirm_pwd = self.query_one("#confirm_input", Input).value.strip()
                if pwd != confirm_pwd:
                    status.update("Passwords do not match!")
                    return
                self.app.vault.create_vault(pwd)
                self.app.pop_screen()
            else:
                if self.app.vault.unlock_vault(pwd):
                    self.app.pop_screen()
                else:
                    status.update("Incorrect Master Password!")

class Main_Window(App):
    CSS_PATH = "style.tcss"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vault = VaultManager()

    def on_mount(self) -> None:
        self.push_screen(MasterPasswordScreen())

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("🔐 SecurePass Password Manager", id="title")
        yield Static("Select an action below:", id="subtitle")
        yield Button("Add Password", id="add_btn")
        yield Button("View Password", id="view_btn")
        yield Button("Manage Password", id="manage_btn")
        yield Button("Lock Vault", id="lock_btn")
        yield Button("Exit", id="exit_btn")
        yield Static("", id="output")
        yield Footer()

    def on_button_pressed(self, e):
        match e.button.id:
            case "add_btn": self.push_screen(Add_Screen())
            case "view_btn": self.push_screen(View_Screen())
            case "manage_btn": self.push_screen(Manage_Screen())
            case "lock_btn":
                self.vault.fernet = None
                self.vault.data = {}
                self.push_screen(MasterPasswordScreen())
            case "exit_btn": self.exit()

class Add_Screen(Screen):
    def compose(self):
        yield Static("Add New Password Entry", id="title")
        self.inputs = {
            "ENTITY_NAME": Input(placeholder="Entity Name (e.g., Gmail)"),
            "PASSWORD": Input(placeholder="Password", password=True),
            "SECURITY_Q": Input(placeholder="Security Question"),
            "SECURITY_A": Input(placeholder="Answer to Security Question"),
            "XSECURITY_Q": Input(placeholder="Extra Security Question"),
            "XSECURITY_A": Input(placeholder="Answer to Extra Security Question")
        }
        yield from self.inputs.values()
        yield Button("Save", id="save_btn")
        yield Button("Back", id="back_btn")
        yield Static("", id="status")

    def on_button_pressed(self, e):
        if e.button.id == "save_btn":
            entry = {k: v.value.strip() for k, v in self.inputs.items()}
            entity = entry.get("ENTITY_NAME")
            if not entity:
                self.query_one("#status", Static).update("Entity Name is required.")
                return
            if not entry.get("PASSWORD"):
                self.query_one("#status", Static).update("Password is required.")
                return

            self.app.vault.add_entry(entity, entry)
            self.app.pop_screen()
        elif e.button.id == "back_btn":
            self.app.pop_screen()

class View_Screen(Screen):
    def compose(self):
        yield Static("View Password - Select Entity", id="title")
        yield Input(placeholder="Entity Name", id="entity_input")
        yield Button("Next", id="next_btn")
        yield Button("Back", id="back_btn")
        yield Static("", id="status")

    def on_button_pressed(self, e):
        match e.button.id:
            case "next_btn":
                entity = self.query_one("#entity_input", Input).value.strip()
                if not entity:
                    self.query_one("#status", Static).update("Entity name is required.")
                    return
                if not self.app.vault.get_entry(entity):
                    self.query_one("#status", Static).update(f"Entity '{entity}' not found in vault.")
                    return
                self.app.push_screen(Verify(entity, "view"))
            case "back_btn":
                self.app.pop_screen()

class Verify(Screen):
    def __init__(self, entity, action, **kwargs):
        super().__init__(**kwargs)
        self.entity = entity
        self.action = action
        self.entry_data = {}

    def compose(self):
        yield Static(f"Verify Access: {self.entity}", id="title")
        yield Static("Security Question:", id="question1_label")
        yield Static("", id="question1")
        yield Input(placeholder="Answer to Security Question", id="answer1")
        yield Static("Extra Security Question:", id="question2_label")
        yield Static("", id="question2")
        yield Input(placeholder="Answer to Extra Security Question", id="answer2")
        yield Button("Verify", id="verify_btn")
        yield Button("Back", id="back_btn")
        yield Static("", id="status")

    def on_mount(self):
        self.entry_data = self.app.vault.get_entry(self.entity) or {}
        if not self.entry_data:
            self.query_one("#status", Static).update(f"Entity '{self.entity}' not found.")
            return

        self.query_one("#question1", Static).update(self.entry_data.get("SECURITY_Q", "None"))
        self.query_one("#question2", Static).update(self.entry_data.get("XSECURITY_Q", "None"))

    def on_button_pressed(self, e):
        if e.button.id == "verify_btn":
            ans1 = self.query_one("#answer1", Input).value.strip()
            ans2 = self.query_one("#answer2", Input).value.strip()

            expected1 = self.entry_data.get("SECURITY_A", "").strip()
            expected2 = self.entry_data.get("XSECURITY_A", "").strip()

            if ans1.lower() == expected1.lower() and ans2.lower() == expected2.lower():
                if self.action == "delete":
                    self.app.vault.delete_entry(self.entity)
                    self.app.pop_screen()
                elif self.action == "edit":
                    self.app.push_screen(Edit_Screen(self.entity, self.entry_data))
                elif self.action == "view":
                    self.app.push_screen(Display_Screen(self.entity, self.entry_data.get("PASSWORD", "")))
            else:
                self.query_one("#status", Static).update("Security answers do not match!")
        elif e.button.id == "back_btn":
            self.app.pop_screen()

class Display_Screen(Screen):
    def __init__(self, entity, password, **kwargs):
        super().__init__(**kwargs)
        self.entity = entity
        self.password = password

    def compose(self):
        yield Static(f"Password for {self.entity}", id="title")
        yield Static(f"Password: {self.password}", id="password_output")
        yield Button("Back to Main Menu", id="back_btn")

    def on_button_pressed(self, e):
        if e.button.id == "back_btn":
            self.app.pop_screen()

class Manage_Screen(Screen):
    def compose(self):
        yield Static("Manage Entry - Enter Entity", id="title")
        yield Input(placeholder="Entity Name", id="entity_input")
        yield Button("Edit Password", id="edit_btn")
        yield Button("Delete Entity", id="del_btn")
        yield Button("Back", id="back_btn")
        yield Static("", id="status")

    def on_button_pressed(self, e):
        entity = self.query_one("#entity_input", Input).value.strip()
        status = self.query_one("#status", Static)
        if not entity:
            status.update("Entity name is required.")
            return

        if not self.app.vault.get_entry(entity):
            status.update(f"Entity '{entity}' not found in vault.")
            return

        match e.button.id:
            case "del_btn":
                self.app.push_screen(Verify(entity, "delete"))
            case "edit_btn":
                self.app.push_screen(Verify(entity, "edit"))
            case "back_btn":
                self.app.pop_screen()

class Edit_Screen(Screen):
    def __init__(self, entity, entry_data, **kwargs):
        super().__init__(**kwargs)
        self.entity = entity
        self.entry_data = entry_data

    def compose(self):
        yield Static(f"Edit Password for: {self.entity}", id="title")
        yield Input(placeholder="New Password", value=self.entry_data.get("PASSWORD", ""), password=True, id="pass_input")
        yield Button("Update", id="update_btn")
        yield Button("Back", id="back_btn")
        yield Static("", id="status")

    def on_button_pressed(self, e):
        if e.button.id == "update_btn":
            new_pass = self.query_one("#pass_input", Input).value.strip()
            if not new_pass:
                self.query_one("#status", Static).update("Password cannot be empty!")
                return

            self.entry_data["PASSWORD"] = new_pass
            self.app.vault.update_entry(self.entity, self.entry_data)
            self.app.pop_screen()
        elif e.button.id == "back_btn":
            self.app.pop_screen()

if __name__ == "__main__":
    Main_Window().run()
