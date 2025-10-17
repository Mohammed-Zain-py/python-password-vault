# main.py
import mysql.connector
from cryptography.fernet import Fernet
import random
import string
import hashlib
import getpass
import os
from dotenv import load_dotenv

# NEW: Load all the variables from the .env file
load_dotenv() 

# --- DATABASE CONFIGURATION ---
# NEW: Read all values from the .env file using os.getenv()
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASS'),
    'database': os.getenv('DB_NAME')
}

# --- MASTER PASSWORD HASH ---
# NEW: Read the hash from the .env file
MASTER_PASSWORD_HASH = os.getenv('MASTER_HASH')


# --- KEY & ENCRYPTION FUNCTIONS ---
def load_key():
    try:
        with open("key.key", "rb") as key_file:
            key = key_file.read()
        return key
    except FileNotFoundError:
        print("Error: key.key not found! Please run 'utils/generate_key.py' first.")
        exit()

key = load_key()
fer = Fernet(key)

# --- PASSWORD GENERATOR ---
def generate_password(min_length, numbers=True, special_characters=True):
    letters = string.ascii_letters
    digits = string.digits
    special = string.punctuation
    characters = letters
    if numbers:
        characters += digits
    if special_characters:
        characters += special

    pwd = "".join(random.choice(characters) for _ in range(min_length))
    return pwd

# --- LOGIN FUNCTION ---
def login():
    """Asks for the master password and verifies it against the stored hash."""
    if not MASTER_PASSWORD_HASH:
        print("Error: MASTER_PASSWORD_HASH not set in .env file.")
        return False

    print("--- Secure Vault Login ---")
    entered_password = getpass.getpass("Enter your master password: ")

    entered_hash = hashlib.sha256(entered_password.encode()).hexdigest()

    if entered_hash == MASTER_PASSWORD_HASH:
        print("Login successful!\n")
        return True
    else:
        print("Incorrect password. Access denied.")
        return False

# --- DATABASE CRUD FUNCTIONS ---
def view():
    try:
        with mysql.connector.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT account_name, encrypted_password FROM passwords")
                results = cursor.fetchall()
                if not results:
                    print("\nNo passwords saved yet.")
                    return
                print("\n--- Saved Passwords ---")
                for account, enc_pass in results:
                    decrypted_pass = fer.decrypt(enc_pass.encode()).decode()
                    print(f"  Account: {account} | Password: {decrypted_pass}")
                print("-----------------------")
    except mysql.connector.Error as err:
        print(f"Database error: {err}")

def add():
    account = input('Account Name: ')
    gen_choice = input("Generate a random password? (y/n): ").lower()

    if gen_choice == 'y':
        try:
            length = int(input("Enter desired password length (min 8) [default 12]: ") or "12")
            if length < 8: length = 8

            has_numbers_choice = input("Include numbers? (y/n) [default y]: ").lower()
            has_numbers = has_numbers_choice != 'n'

            has_special_choice = input("Include special characters? (y/n) [default y]: ").lower()
            has_special = has_special_choice != 'n'

        except ValueError:
            length = 12
            has_numbers = True
            has_special = True

        pwd = generate_password(length, has_numbers, has_special)
        print(f"Generated Password: {pwd}")
    else:
        pwd = input("Enter the Password: ")

    encrypted_pwd = fer.encrypt(pwd.encode()).decode()

    try:
        with mysql.connector.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                sql = "INSERT INTO passwords (account_name, encrypted_password) VALUES (%s, %s)"
                val = (account, encrypted_pwd)
                cursor.execute(sql, val)
                conn.commit()
                print(f"\nPassword for '{account}' saved successfully!")
    except mysql.connector.Error as err:
        print(f"\nDatabase error: {err}")

def update():
    account = input("Enter the name of the account to update: ")
    new_pwd = input("Enter the new password (or leave blank to generate one): ")

    if not new_pwd:
        try:
            length = int(input("Enter desired password length (min 8) [default 12]: ") or "12")
            if length < 8: length = 8

            has_numbers_choice = input("Include numbers? (y/n) [default y]: ").lower()
            has_numbers = has_numbers_choice != 'n'

            has_special_choice = input("Include special characters? (y/n) [default y]: ").lower()
            has_special = has_special_choice != 'n'

        except ValueError:
            length = 12
            has_numbers = True
            has_special = True

        new_pwd = generate_password(length, has_numbers, has_special)
        print(f"Generated New Password: {new_pwd}")

    encrypted_new_pwd = fer.encrypt(new_pwd.encode()).decode()

    try:
        with mysql.connector.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                sql = "UPDATE passwords SET encrypted_password = %s WHERE account_name = %s"
                val = (encrypted_new_pwd, account)
                cursor.execute(sql, val)
                conn.commit()
                if cursor.rowcount == 0:
                    print(f"\nAccount '{account}' not found.")
                else:
                    print(f"\nPassword for '{account}' updated successfully!")
    except mysql.connector.Error as err:
        print(f"\nDatabase error: {err}")

def delete():
    account = input("Enter the name of the account to delete: ")
    confirm = input(f"Are you sure you want to delete '{account}'? (y/n): ").lower()

    if confirm != 'y':
        print("Deletion cancelled.")
        return

    try:
        with mysql.connector.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                sql = "DELETE FROM passwords WHERE account_name = %s"
                val = (account,)
                cursor.execute(sql, val)
                conn.commit()
                if cursor.rowcount == 0:
                    print(f"\nAccount '{account}' not found.")
                else:
                    print(f"\nPassword for '{account}' has been deleted.")
    except mysql.connector.Error as err:
        print(f"\nDatabase error: {err}")

# --- MAIN EXECUTION BLOCK ---
if __name__ == "__main__":
    # First, run the login function to verify the user
    if login():
        # If login is successful, show the main menu
        while True:
            mode = input(
                "\n--- Password Vault Menu ---\n"
                " (1) Add a new password\n"
                " (2) View existing passwords\n"
                " (3) Update a password\n"
                " (4) Delete a password\n"
                " (q) Quit\n"
                " > "
            ).lower()

            if mode == "q":
                break
            elif mode == "1":
                add()
            elif mode == "2":
                view()
            elif mode == "3":
                update()
            elif mode == "4":
                delete()
            else:
                print("\nInvalid option. Please try again.")