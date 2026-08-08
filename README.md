# SecurePass - Encrypted TUI Password Manager

A modern, secure Terminal User Interface (TUI) Password Manager built with **Python**, **Textual**, and **Cryptography** (PBKDF2HMAC + Fernet AES Encryption).

## Features

- 🔐 **Encrypted Vault Storage**: All passwords, security questions, and credentials are encrypted on disk (`passwords.enc`) using a key derived from your **Master Password** via `PBKDF2HMAC` (SHA-256, 100,000 iterations).
- 🔑 **Master Password Protection**: Protects the vault at launch. Includes screen locking capability.
- 🛡️ **Two-Factor Security Q&A**: Secondary authentication requiring user answers to dual security questions before viewing, editing, or deleting entries.
- 🚚 **Automatic Legacy Import**: Detects legacy unencrypted `passwords.txt` files and automatically migrates entries into your encrypted vault on first setup.
- 🎨 **Modern Textual TUI**: Responsive layout with clean styles (`style.tcss`).

## Requirements

- Python 3.10+
- `textual`
- `cryptography`

## Installation & Running

1. Install dependencies:
   ```bash
   pip install textual cryptography
   ```

2. Run the application:
   ```bash
   python main.py
   ```

## Usage Flow

1. **First Launch**: Set up your Master Password to initialize the encrypted vault.
2. **Add Entry**: Click **Add Password** to store a new entity, password, and security questions.
3. **View Entry**: Click **View Password**, enter the entity name, and answer the security questions to reveal the password.
4. **Manage Entry**: Edit existing passwords or delete entities securely.
5. **Lock Vault**: Click **Lock Vault** at any time to return to the lock screen.
