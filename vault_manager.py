import os
import json
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class VaultManager:
    def __init__(self, vault_file="passwords.enc", legacy_file="passwords.txt"):
        self.vault_file = vault_file
        self.legacy_file = legacy_file
        self.fernet = None
        self.salt = None
        self.data = {}

    def exists(self) -> bool:
        return os.path.exists(self.vault_file)

    def _derive_key(self, master_password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(master_password.encode('utf-8')))

    def create_vault(self, master_password: str):
        self.salt = os.urandom(16)
        key = self._derive_key(master_password, self.salt)
        self.fernet = Fernet(key)
        self.data = {}
        self._import_legacy_if_any()
        self._save()

    def unlock_vault(self, master_password: str) -> bool:
        if not self.exists():
            return False
        try:
            with open(self.vault_file, "rb") as f:
                content = f.read()
            if len(content) < 16:
                return False
            self.salt = content[:16]
            encrypted_payload = content[16:]
            key = self._derive_key(master_password, self.salt)
            self.fernet = Fernet(key)
            decrypted_bytes = self.fernet.decrypt(encrypted_payload)
            self.data = json.loads(decrypted_bytes.decode('utf-8'))
            return True
        except (InvalidToken, Exception):
            self.fernet = None
            self.salt = None
            self.data = {}
            return False

    def _save(self):
        if not self.fernet or not self.salt:
            raise RuntimeError("Vault is locked or uninitialized.")
        raw_bytes = json.dumps(self.data).encode('utf-8')
        encrypted_payload = self.fernet.encrypt(raw_bytes)
        with open(self.vault_file, "wb") as f:
            f.write(self.salt + encrypted_payload)

    def add_entry(self, entity: str, entry_dict: dict):
        self.data[entity.strip()] = entry_dict
        self._save()

    def get_entry(self, entity: str):
        return self.data.get(entity.strip())

    def delete_entry(self, entity: str) -> bool:
        entity = entity.strip()
        if entity in self.data:
            del self.data[entity]
            self._save()
            return True
        return False

    def update_entry(self, entity: str, new_entry_dict: dict):
        self.data[entity.strip()] = new_entry_dict
        self._save()

    def list_entities(self):
        return sorted(list(self.data.keys()))

    def _import_legacy_if_any(self):
        if os.path.exists(self.legacy_file):
            try:
                with open(self.legacy_file, "r", encoding="utf-8") as f:
                    content = f.read()
                blocks = content.split("---\n")
                for block in blocks:
                    if block.strip():
                        lines = block.strip().splitlines()
                        entry = {}
                        for line in lines:
                            if ": " in line:
                                k, v = line.split(": ", 1)
                                entry[k.strip()] = v.strip()
                        entity_name = entry.get("ENTITY_NAME")
                        if entity_name:
                            self.data[entity_name] = entry
            except Exception:
                pass
