# SecurePass — Encrypted TUI Password Manager

**A terminal-based password manager with an encrypted local vault.**

SecurePass is a Python **Textual** application that stores credentials in an encrypted vault protected by a master password. It also adds a second verification layer using security questions before sensitive entries can be viewed or managed.

## Features

- 🔐 **Encrypted vault storage** using Fernet encryption
- 🔑 **Master password protection** for the vault
- 🛡️ **Security-question verification** before sensitive entry access
- 🔒 **Vault locking** from the application
- 🚚 **Legacy import** for existing unencrypted `passwords.txt` data
- 🖥️ **Terminal UI** built with Textual
- ✏️ Add, view, edit, and delete stored credentials

## Security model

The project uses **PBKDF2HMAC with SHA-256** to derive key material from the master password and **Fernet** for authenticated symmetric encryption.

Conceptually:

```text
Master Password
      │
      ▼
 PBKDF2HMAC
      │
      ▼
Derived encryption key
      │
      ▼
 Fernet
      │
      ▼
Encrypted local vault
```

The application keeps the decrypted vault available only while the vault is unlocked; locking clears the active Fernet/data state.

> This is an educational/local password-manager project. Do not treat it as a production-grade password manager without independently auditing the implementation and threat model.

## Requirements

- Python 3.10+
- Textual
- Cryptography

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running

```bash
python main.py
```

## Usage flow

1. Launch SecurePass.
2. Create a master password on first use.
3. Unlock the vault on subsequent launches.
4. Add credentials to the encrypted vault.
5. Verify the security questions before accessing protected entries.
6. Lock the vault when finished.

## Project structure

```text
tuibasedpassmanager/
├── main.py
├── vault_manager.py
├── style.tcss
├── requirements.txt
└── README.md
```

## Status

✅ **Complete / functional project**

## License

The repository contains a license file. Check the repository's license metadata for the exact terms.
