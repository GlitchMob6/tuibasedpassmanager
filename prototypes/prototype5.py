# Textual-based Password Manager with Encrypted Plaintext Storage

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Input, Static
from textual.containers import Vertical
from textual.screen import Screen
from cryptography.fernet import Fernet
import os

APP_DIR = os.path.expanduser("~/.password_manager")
PASSWORD_FILE = os.path.join(APP_DIR, "passwords.txt")
KEY_FILE = os.path.join(APP_DIR, "secret.key")

if not os.path.exists(APP_DIR):
    os.makedirs(APP_DIR)

# --- Encryption Key Management ---
def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)

def load_key():
    if not os.path.exists(KEY_FILE):
        generate_key()
        global fernet  # Reinitialize fernet with the new key
        fernet = Fernet(load_key())
    with open(KEY_FILE, "rb") as f:
        return f.read()

fernet = Fernet(load_key())

# --- File Handling ---
def load_passwords():
    if not os.path.exists(PASSWORD_FILE):
        return []
    with open(PASSWORD_FILE, "rb") as f:
        data = f.read()
        if not data:
            return []
        try:
            decrypted = fernet.decrypt(data).decode()
        except Exception:
            return []  # Return an empty list if decryption fails
        entries = decrypted.strip().split("\n\n")
        return [parse_entry(e) for e in entries]

def save_passwords(passwords):
    text = "\n\n".join(format_entry(p) for p in passwords)
    encrypted = fernet.encrypt(text.encode())
    with open(PASSWORD_FILE, "wb") as f:
        f.write(encrypted)

def format_entry(entry):
    return f"Entity: {entry['entity']}\nPassword: {entry['password']}\nSecurity Question: {entry['security_question']}\nSecurity Answer: {entry['security_answer']}\nExtra Security Question: {entry['extra_security_question']}\nExtra Security Answer: {entry['extra_security_answer']}"

def parse_entry(block):
    lines = block.splitlines()
    return {
        'entity': lines[0].split(": ", 1)[1],
        'password': lines[1].split(": ", 1)[1],
        'security_question': lines[2].split(": ", 1)[1],
        'security_answer': lines[3].split(": ", 1)[1],
        'extra_security_question': lines[4].split(": ", 1)[1],
        'extra_security_answer': lines[5].split(": ", 1)[1],
    }

# --- Textual Screens ---
class Home(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Button("Add Password", id="add"),
            Button("View Passwords", id="view"),
            Button("Edit Password", id="edit"),
            Button("Delete Password", id="delete")
        )
        yield Footer()

    def on_button_pressed(self, event):
        self.app.push_screen(event.button.id)

class AddPassword(Screen):
    def compose(self):
        self.inputs = {
            'entity': Input(placeholder="Entity"),
            'password': Input(placeholder="Password"),
            'security_question': Input(placeholder="Security Question"),
            'security_answer': Input(placeholder="Security Answer"),
            'extra_security_question': Input(placeholder="Extra Security Question"),
            'extra_security_answer': Input(placeholder="Extra Security Answer"),
        }
        yield Header()
        for input_field in self.inputs.values():
            yield input_field
        yield Button("Save", id="save")
        yield Button("Back", id="back")
        yield Footer()

    def on_button_pressed(self, event):
        if event.button.id == "save":
            entry = {k: v.value.strip() for k, v in self.inputs.items()}
            if not all(entry.values()):
                self.app.pop_screen()
                return
            passwords = load_passwords()
            passwords.append(entry)
            save_passwords(passwords)
            self.app.push_screen()
            self.app.pop_screen()
        elif event.button.id == "back":
            self.app.pop_screen()

# Add additional screens here: View, Edit, Delete, Security Verification etc.

class PasswordManagerApp(App):
    def on_mount(self):
        self.push_screen(Home())

    def on_ready(self):
        self.install_screen(AddPassword(), name="add")
        # Screens for view, edit, delete should also be installed here

if __name__ == "__main__":
    PasswordManagerApp().run()
