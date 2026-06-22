# Secure Password Vault

A self-hosted password vault built to securely generate, store, manage, and recover credentials locally.

This project was built to solve a personal problem: using different passwords across platforms improves security, but remembering all of them becomes difficult over time. Instead of storing credentials in third-party password managers, this project keeps encrypted credentials under local control while providing quick access through a simple interface.

The application separates the frontend and backend, encrypts stored credentials before persistence, supports encrypted backup and restore, and is containerized for reproducible setup.

---

## Motivation

Reusing passwords across multiple platforms increases risk.

Using unique passwords is safer, but managing and remembering them becomes difficult.

This project was built to:

* Generate unique passwords quickly
* Store credentials locally instead of relying on third-party services
* Keep stored credentials encrypted
* Make retrieval convenient while maintaining access control
* Understand how secure storage systems work internally

---

## Features

* Master password authentication
* Secure credential storage using Fernet encryption
* Password generation utility
* Manual custom password creation
* Add / View / Update / Delete credentials
* Search stored credentials
* Encrypted JSON backup
* Restore from encrypted backups
* Environment-based configuration
* Dockerized deployment

---

## Architecture

```text
Streamlit Frontend
        ↓
FastAPI Backend
        ↓
Authentication Layer
        ↓
Encryption Layer
        ↓
MySQL Database
```

---

## Tech Stack

### Frontend

* Streamlit

### Backend

* FastAPI
* Uvicorn

### Database

* MySQL

### Security

* Fernet Encryption
* SHA-256 Hashing

### Deployment

* Docker
* Docker Compose

---

## Project Structure

```text
python-password-vault/

├── backend/
│   ├── Dockerfile
│   └── main.py
│
├── frontend/
│   ├── app.py
│   ├── Dockerfile
│   └── .streamlit/
│       └── config.toml
│
├── utils/
│   ├── create_hash.py
│   └── generate_key.py
│
├── .dockerignore
├── .gitignore
├── docker-compose.yml
├── requirements.txt
├── Vault.bat
├── README.md
└── LICENSE
```

---

## How It Works

1. User enters the master password.
2. The password is hashed and validated.
3. Credentials are encrypted before storage.
4. Encrypted data is stored in MySQL.
5. Credentials are decrypted only during retrieval.
6. Backups export encrypted data instead of plaintext values.

---

## Local Setup

Clone repository

```bash
git clone <https://github.com/Mohammed-Zain-py/python-password-vault.git>
cd python-password-vault
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create environment configuration

```env
DB_HOST=
DB_USER=
DB_PASS=
DB_NAME=
MASTER_HASH=
```

Generate encryption key

```bash
python utils/generate_key.py
```

Generate master password hash

```bash
python utils/create_hash.py
```

Start backend

```bash
uvicorn backend.main:app --reload
```

Start frontend

```bash
streamlit run frontend/app.py
```

---

## Docker Setup

Build and run

```bash
docker-compose up --build
```

---

## Security Notes

The following files should never be committed:

```text
.env
key.key
vault backups
```

Stored credentials are encrypted before persistence.

This project is intended for local self-hosted usage.

---

## Future Improvements

This project currently solves my personal use case.

Future updates will focus on improving usability, local backup workflows, vault search optimization, password history tracking, and overall vault management while keeping credentials self-hosted and encrypted.
