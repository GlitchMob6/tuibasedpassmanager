from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import (
    Static,
    Input,
    Button,
    Header,
    Footer,
    Label,
)
import os

DATA_FILE = "passwords.txt"

def load_data():
    data = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            entity = None
            for line in f:
                line = line.strip()
                if line.startswith("ENTITY:"):
                    entity = line.split(":", 1)[1].strip()
                    data[entity] = {}
                elif entity and line and ":" in line:
                    key, value = line.split(":", 1)
                    data[entity][key.strip()] = value.strip()
    return data

def save_data(data):
    with open(DATA_FILE, "w") as f:
        for entity, details in data.items():
            f.write(f"ENTITY: {entity}\n")
            for key, value in details.items():
                f.write(f"{key}: {value}\n")
            f.write("---\n")

class PasswordManager(App):
    CSS_PATH = "style.tcss"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def __init__(self):
        super().__init__()
        self.data = load_data()
        self.current_entity = None
        self.delete_mode = False
        self.update_mode = False

    def compose(self) -> ComposeResult:
        self.log("Composing UI components...")
        yield Header()
        yield Footer()
        # Initialize the main menu and ensure it is visible
        main_menu = Vertical(id="main_menu", visible=True)  # Ensure visibility
        yield main_menu
        # Initialize other screens but keep them hidden
        yield Vertical(id="add_password_screen", visible=False)
        yield Vertical(id="manage_password_screen", visible=False)
        yield Vertical(id="view_password_screen", visible=False)

    def on_mount(self):
        try:
            self.log("Mounting application...")
            # Ensure the main menu is populated and visible on startup
            self.show_main_menu()
        except Exception as e:
            self.log(f"Error during on_mount: {e}")

    def show_main_menu(self):
        try:
            self.log("Displaying main menu...")
            main_menu = self.query_one("#main_menu", Vertical)
            main_menu.remove_all()  # Clear any existing widgets
            self.hide_all_except("main_menu")  # Ensure only the main menu is visible
            # Populate the main menu with buttons
            main_menu.mount(Button("Add Password", id="add"))
            main_menu.mount(Button("Manage Password", id="manage"))
            main_menu.mount(Button("View Password", id="view"))
            self.log("Main menu displayed successfully.")
        except Exception as e:
            self.log(f"Error in show_main_menu: {e}")

    def show_add_password_screen(self):
        screen = self.query_one("#add_password_screen", Vertical)
        screen.remove_all()  # Corrected from remove_children to remove_all
        screen.visible = True
        self.hide_all_except("add_password_screen")
        screen.mount(Label("Add a New Password"))
        screen.mount(Label("Entity Name:"))
        screen.mount(Input(placeholder="e.g., gmail", id="entity_input"))
        screen.mount(Label("Password:"))
        screen.mount(Input(password=True, id="password_input"))
        screen.mount(Label("Security Question:"))
        screen.mount(Input(id="security_question_input"))
        screen.mount(Label("Security Answer:"))
        screen.mount(Input(id="security_answer_input"))
        screen.mount(Label("Extra Security Question:"))
        screen.mount(Input(id="extra_security_question_input"))
        screen.mount(Label("Extra Security Answer:"))
        screen.mount(Input(password=True, id="extra_security_answer_input"))
        screen.mount(Button("Save", id="save_password"))
        screen.mount(Button("Back to Main Menu", id="back_to_main"))

    def show_manage_password_screen(self):
        screen = self.query_one("#manage_password_screen", Vertical)
        screen.remove_all()  # Corrected from remove_children to remove_all
        screen.visible = True
        self.hide_all_except("manage_password_screen")
        screen.mount(Label("Manage Passwords"))
        for entity in self.data.keys():
            screen.mount(Button(entity, id=f"entity_{entity}"))
        screen.mount(Button("Back to Main Menu", id="back_to_main"))

    def show_view_password_screen(self):
        screen = self.query_one("#view_password_screen", Vertical)
        screen.remove_all()  # Corrected from remove_children to remove_all
        screen.visible = True
        self.hide_all_except("view_password_screen")
        screen.mount(Label("View Passwords"))
        for entity in self.data.keys():
            screen.mount(Button(entity, id=f"entity_{entity}"))
        screen.mount(Button("Back to Main Menu", id="back_to_main"))

    def hide_all_except(self, visible_screen_id):
        for screen_id in ["main_menu", "add_password_screen", "manage_password_screen", "view_password_screen"]:
            try:
                screen = self.query_one(f"#{screen_id}", Vertical)
                screen.visible = (screen_id == visible_screen_id)
            except Exception as e:
                self.log(f"Error hiding screen {screen_id}: {e}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "add":
            self.show_add_password_screen()
        elif button_id == "manage":
            self.show_manage_password_screen()
        elif button_id == "view":
            self.show_view_password_screen()
        elif button_id == "save_password":
            self.save_password()
        elif button_id == "back_to_main":
            self.show_main_menu()
        elif button_id.startswith("entity_"):
            self.current_entity = button_id.split("entity_", 1)[1]
            self.show_message(f"Selected Entity: {self.current_entity}")

    def save_password(self):
        screen = self.query_one("#add_password_screen", Vertical)
        entity = screen.query_one("#entity_input", Input).value.strip()
        password = screen.query_one("#password_input", Input).value.strip()
        security_q = screen.query_one("#security_question_input", Input).value.strip()
        security_a = screen.query_one("#security_answer_input", Input).value.strip()
        xsecurity_q = screen.query_one("#extra_security_question_input", Input).value.strip()
        xsecurity_a = screen.query_one("#extra_security_answer_input", Input).value.strip()

        if entity and password and security_q and security_a and xsecurity_q and xsecurity_a:
            self.data[entity] = {
                "PASSWORD": password,
                "SECURITY_Q": security_q,
                "SECURITY_A": security_a,
                "XSECURITY_Q": xsecurity_q,
                "XSECURITY_A": xsecurity_a,
            }
            save_data(self.data)
            self.show_message("Password saved successfully!")
        else:
            self.show_message("All fields are required!")

    def show_message(self, message):
        self.hide_all_except("main_menu")  # Ensure other screens are hidden
        screen = self.query_one("#main_menu", Vertical)
        screen.remove_all()  # Corrected from remove_children to remove_all
        screen.mount(Label(message))
        screen.mount(Button("Back to Main Menu", id="back_to_main"))

if __name__ == "__main__":
    PasswordManager().run()
