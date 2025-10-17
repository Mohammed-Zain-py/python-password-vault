# Python Secure Password Vault

A command-line password manager built with Python. This project uses MySQL for secure database storage and the `cryptography` library to encrypt all passwords. A master password (using hashing) protects access to the vault.

## Features
- **Secure Login:** Protected by a hashed master password.
- **Full CRUD:** Create, Read, Update, and Delete passwords.
- **Encryption:** All passwords are encrypted using Fernet (AES-128) before being stored.
- **Password Generator:** Includes a built-in generator for strong, random passwords.
- **Secure Configuration:** All secrets (database credentials, master hash, encryption key) are stored in a `.env` file and are not hard-coded.

## How to Set Up (Local)

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/Mohammed-Zain-py/python-password-vault.git
    cd python-password-vault
    ```
2.  **Create and activate a virtual environment:**
    ```sh
    python -m venv venv
    .\venv\Scripts\activate
    ```
3.  **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```
4.  **Set up your MySQL Database:**
    * Create a database (e.g., `vault_db`).
    * Run the following SQL to create the table:
        ```sql
        CREATE TABLE passwords (
            id INT AUTO_INCREMENT PRIMARY KEY,
            account_name VARCHAR(255) NOT NULL UNIQUE,
            encrypted_password TEXT NOT NULL
        );
        ```
5.  **Create your secret files:**
    * **Generate Encryption Key:** Run `python utils/generate_key.py`. This will create your private `key.key` file.
    * **Generate Master Hash:** Edit `utils/create_hash.py` to set your desired master password, then run it. Copy the output hash.
    * **Create `.env` File:** Create a `.env` file and fill it with your credentials:
        ```
        DB_HOST=localhost
        DB_USER=your_db_user
        DB_PASS=your_db_password
        DB_NAME=vault_db
        MASTER_HASH=your_copied_hash_from_the_step_above
        ```
6.  **Run the application!**
    ```sh
    python main.py
    ```