# backend.py
# Remarque : installer argon2-cffi -> pip install argon2-cffi

import json
import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import hashlib
import platform
import datetime
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from argon2.low_level import hash_secret_raw, Type


class SecureSafeBackend:
    def __init__(self, data_file=None):
        # Emplacement utilisateur sans admin
        if platform.system() == "Windows":
            appdata = os.getenv("APPDATA") or os.path.expanduser(r"~\\AppData\\Roaming")
            base_dir = os.path.join(appdata, "SecureSafe")
        else:
            base_dir = os.path.expanduser("~/.config/.securesafe")

        os.makedirs(base_dir, exist_ok=True)

        # Rendre le dossier caché sous Windows (optionnel)
        if platform.system() == "Windows":
            try:
                os.system(f'attrib +h "{base_dir}"')
            except:
                pass

        self.data_file = data_file or os.path.join(base_dir, "securesafe_data.json")
        # ----- BACKUP DANS UN EMPLACEMENT SÉPARÉ -----
        if platform.system() == "Windows":
         documents = os.path.join(os.path.expanduser("~"), "Documents")
         backup_base = os.path.join(documents, "SecureSafe_Backups")
        else:
         backup_base = os.path.expanduser("~/securesafe_backups")

        os.makedirs(backup_base, exist_ok=True)
        self.backup_dir = backup_base


        # État interne
        self.users = {}
        self.current_user = None
        self.master_key = None

    # ------------------ CRYPTO ------------------

    def derive_key(self, master_password, salt):
        """Dérive une clé 32 octets avec Argon2id"""
        return hash_secret_raw(
            secret=master_password.encode(),
            salt=salt,
            time_cost=3,
            memory_cost=64 * 1024,  # 64 MB
            parallelism=2,
            hash_len=32,
            type=Type.ID
        )

    def hash_password(self, password):
        """Hash simple SHA-256 pour le mot de passe maître"""
        return hashlib.sha256(password.encode()).hexdigest()

    def encrypt_data(self, data, key):
     aesgcm = AESGCM(key)          # AES-256
     nonce = os.urandom(12)        # 96 bits recommandé
     encrypted = aesgcm.encrypt(nonce, data.encode(), None)
     return base64.b64encode(nonce + encrypted).decode()

    def decrypt_data(self, encrypted_data, key):
     try:
        raw = base64.b64decode(encrypted_data)
        nonce = raw[:12]
        ciphertext = raw[12:]
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, ciphertext, None).decode()
     except:
        return None

    # ------------------ FICHIERS ------------------

    def _write_backup(self):
        """Crée une sauvegarde du fichier principal"""
        if os.path.exists(self.data_file):
            ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            backup_path = os.path.join(self.backup_dir, f"backup_{ts}.bak")
            try:
                with open(self.data_file, "r") as src, open(backup_path, "w") as dst:
                    dst.write(src.read())
            except:
                pass

    def load_data(self):
        """Charge les données JSON non chiffrées"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    self.users = json.load(f)
                return True
            except:
                return False
        self.users = {}
        return True

    def save_data(self):
        """Sauvegarde les données JSON (non chiffrées globalement)"""
        self._write_backup()
        with open(self.data_file, "w") as f:
            json.dump(self.users, f, indent=4)

    # ------------------ UTILISATEURS ------------------

    def create_account(self, username, master_password):
        """Créer un compte utilisateur"""
        self.load_data()

        if username in self.users:
            return False, "Utilisateur déjà existant."

        salt = os.urandom(16)
        salt_b64 = base64.b64encode(salt).decode()

        self.users[username] = {
            "password_hash": self.hash_password(master_password),
            "salt": salt_b64,
            "passwords": {}
            
        }

        self.save_data()
        return True, "Compte créé avec succès."

    def login(self, username, master_password):
        """Connexion utilisateur"""
        self.load_data()

        if username not in self.users:
            return False, "Utilisateur introuvable."

        user = self.users[username]
        if self.hash_password(master_password) != user["password_hash"]:
            return False, "Mot de passe maître incorrect."

        salt = base64.b64decode(user["salt"])
        self.master_key = self.derive_key(master_password, salt)
        self.current_user = username
        return True, f"Bienvenue {username}."

    def logout(self):
        """Déconnexion"""
        self.current_user = None
        self.master_key = None
        self.users = {}

    # ------------------ MOTS DE PASSE ------------------

    def add_password(self, service, username, password):
        """Ajoute un mot de passe chiffré pour un service"""
        if not self.current_user:
            return False, "Non connecté."

        enc_u = self.encrypt_data(username, self.master_key)
        enc_p = self.encrypt_data(password, self.master_key)

        self.users[self.current_user]["passwords"][service] = {
            "username": enc_u,
            "password": enc_p
        }

        self.save_data()
        return True, "Mot de passe ajouté."

    def get_all_passwords(self):
        """Retourne tous les mots de passe déchiffrés"""
        if not self.current_user:
            return []

        result = []
        for service, data in self.users[self.current_user]["passwords"].items():
            result.append({
                "service": service,
                "username": self.decrypt_data(data["username"], self.master_key),
                "password": self.decrypt_data(data["password"], self.master_key),
            })
        return result

    def delete_password(self, service):
        """Supprime un mot de passe"""
        if not self.current_user:
            return False, "Erreur."

        if service in self.users[self.current_user]["passwords"]:
            del self.users[self.current_user]["passwords"][service]
            self.save_data()
            return True, "Supprimé."

        return False, "Service introuvable."

    def modify_password(self, service, new_username, new_password):
        """Modifie un mot de passe existant"""
        if not self.current_user:
            return False, "Non connecté."

        if service not in self.users[self.current_user]["passwords"]:
            return False, "Service introuvable."

        old = self.users[self.current_user]["passwords"][service]

        username = new_username or self.decrypt_data(old["username"], self.master_key)
        password = new_password or self.decrypt_data(old["password"], self.master_key)

        self.users[self.current_user]["passwords"][service] = {
            "username": self.encrypt_data(username, self.master_key),
            "password": self.encrypt_data(password, self.master_key),
        }

        self.save_data()
        return True, "Modifié."

    # ------------------ MODIFICATION DU COMPTE ------------------

    def modify_user_account(self, new_username, new_master_password):
        """Permet de changer le nom ou le mot de passe maître"""
        if not self.current_user:
            return False, "Non connecté."

        user = self.users[self.current_user]

        # Modifier mot de passe maître
        if new_master_password:
            salt = base64.b64decode(user["salt"])
            new_key = self.derive_key(new_master_password, salt)

            # Déchiffrer toutes les données avec l'ancienne clé
            decrypted = {
                s: {
                    "username": self.decrypt_data(d["username"], self.master_key),
                    "password": self.decrypt_data(d["password"], self.master_key)
                }
                for s, d in user["passwords"].items()
            }

            # Réencrypter avec la nouvelle clé
            user["passwords"] = {
                s: {
                    "username": self.encrypt_data(d["username"], new_key),
                    "password": self.encrypt_data(d["password"], new_key)
                }
                for s, d in decrypted.items()
            }

            user["password_hash"] = self.hash_password(new_master_password)
            self.master_key = new_key

        # Modifier nom utilisateur
        if new_username and new_username != self.current_user:
            if new_username in self.users:
                return False, "Nom déjà utilisé."

            self.users[new_username] = user
            del self.users[self.current_user]
            self.current_user = new_username

        self.save_data()
        return True, "Compte mis à jour."

    def delete_current_account(self):
        """Supprime le compte connecté"""
        if not self.current_user:
            return False
        try:
            del self.users[self.current_user]
            self.save_data()
            self.logout()
            return True
        except:
            return False
