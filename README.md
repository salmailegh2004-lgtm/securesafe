# SecureSafe

SecureSafe is a desktop password manager created with Python and Tkinter. It lets users create an account, log in with a master password, store credentials for different services, and manage them securely from a local interface.

## Features

- User account creation and authentication
- Master password hashing
- Encryption of stored credentials with AES-GCM
- Local secure data storage under the user's profile folder
- Backup creation for the main data file
- Password list, add, edit, and delete operations via a graphical interface

## Project structure

- `backend.py` – encryption, user management, storage, and business logic
- `gui.py` – Tkinter interface for the application
- `securesafe.py` – main entry point that launches the GUI

## Requirements

Install the Python dependencies before running the application:

```bash
pip install cryptography argon2-cffi
```

## Run the app

From the project folder, launch:

```bash
python securesafe.py
```

On Windows, you can also run:

```powershell
py securesafe.py
```

## Notes

- The application stores user data in a folder under the current user's profile, such as `%APPDATA%\SecureSafe` on Windows.
- Backups are created in a separate folder under the user's Documents directory on Windows or under the home directory on Unix-like systems.
- This project is intended for local use and is not a production-grade multi-user online password manager.

## Security note

The project uses AES-GCM for encrypting stored passwords and Argon2id for key derivation. Keep your master password safe and do not share the local data files with others.
