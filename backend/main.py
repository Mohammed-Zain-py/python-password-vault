import os
import random
import string
import hashlib
import mysql.connector
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from typing import List

# --- CONFIGURATION ---
load_dotenv()

db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASS'),
    'database': os.getenv('DB_NAME')
}

MASTER_PASSWORD_HASH = os.getenv('MASTER_HASH')

# --- INITIALIZATION ---
app = FastAPI(title="Secure Password Vault API", version="1.0")

def load_key():
    try:
        # Dynamic absolute pathing
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        key_path = os.path.join(BASE_DIR, "..", "key.key")
        
        with open(key_path, "rb") as key_file:
            return key_file.read()
    except FileNotFoundError:
        raise RuntimeError(f"key.key not found! Expected it at: {key_path}")

key = load_key()
fer = Fernet(key)

# --- PYDANTIC MODELS (Data Validation) ---
class LoginRequest(BaseModel):
    master_password: str

class PasswordAddRequest(BaseModel):
    account_name: str
    email: str = ""  
    password: str = "" 
    generate_random: bool = False
    length: int = 12
    use_numbers: bool = True
    use_special: bool = True

class PasswordUpdateRequest(BaseModel):
    email: str = ""  
    password: str = ""
    generate_random: bool = False
    length: int = 12
    use_numbers: bool = True
    use_special: bool = True

class VaultRecord(BaseModel):
    account_name: str
    email: str = ""
    encrypted_password: str

class ImportRequest(BaseModel):
    records: List[VaultRecord]

# --- HELPER FUNCTIONS ---
def generate_password(min_length: int, numbers: bool, special_characters: bool) -> str:
    characters = string.ascii_letters
    if numbers: characters += string.digits
    if special_characters: characters += string.punctuation
    return "".join(random.choice(characters) for _ in range(min_length))

def get_db_connection():
    try:
        return mysql.connector.connect(**db_config)
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database connection failed:")

# --- API ENDPOINTS ---
@app.post("/api/login")
def login(request: LoginRequest):
    if not MASTER_PASSWORD_HASH:
        raise HTTPException(status_code=500, detail="Server misconfiguration: Master hash missing.")
    
    entered_hash = hashlib.sha256(request.master_password.encode()).hexdigest()
    if entered_hash == MASTER_PASSWORD_HASH:
        return {"status": "success", "message": "Authentication successful"}
    
    raise HTTPException(status_code=401, detail="Incorrect master password")

@app.get("/api/passwords")
def view_passwords():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT account_name, email, encrypted_password FROM passwords")
        results = cursor.fetchall()
        
        decrypted_results = []
        for row in results:
            decrypted_pass = fer.decrypt(row['encrypted_password'].encode()).decode()
            decrypted_results.append({
                "account_name": row['account_name'],
                "email": row.get('email', ''), 
                "password": decrypted_pass
            })
        return {"status": "success", "data": decrypted_results}
    finally:
        cursor.close()
        conn.close()

@app.post("/api/passwords")
def add_password(request: PasswordAddRequest):
    if request.generate_random or not request.password:
        pwd = generate_password(request.length, request.use_numbers, request.use_special)
    else:
        pwd = request.password

    encrypted_pwd = fer.encrypt(pwd.encode()).decode()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = "INSERT INTO passwords (account_name, email, encrypted_password) VALUES (%s, %s, %s)"
        cursor.execute(sql, (request.account_name, request.email, encrypted_pwd))
        conn.commit()
        return {"status": "success", "message": f"Saved {request.account_name}", "generated_password": pwd if request.generate_random else None}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=str(err))
    finally:
        cursor.close()
        conn.close()

@app.put("/api/passwords/{account_name}")
def update_password(account_name: str, request: PasswordUpdateRequest):
    if request.generate_random or not request.password:
        new_pwd = generate_password(request.length, request.use_numbers, request.use_special)
    else:
        new_pwd = request.password

    encrypted_new_pwd = fer.encrypt(new_pwd.encode()).decode()

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = "UPDATE passwords SET email = %s, encrypted_password = %s WHERE account_name = %s"
        cursor.execute(sql, (request.email, encrypted_new_pwd, account_name))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Account not found")
        return {"status": "success", "message": f"Updated {account_name}", "new_password": new_pwd if request.generate_random else None}
    finally:
        cursor.close()
        conn.close()

@app.delete("/api/passwords/{account_name}")
def delete_password(account_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = "DELETE FROM passwords WHERE account_name = %s"
        cursor.execute(sql, (account_name,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Account not found")
        return {"status": "success", "message": f"Deleted {account_name}"}
    finally:
        cursor.close()
        conn.close()

@app.get("/api/backup/export")
def export_vault():
    """Fetches all raw encrypted data for backup."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT account_name, email, encrypted_password FROM passwords")
        results = cursor.fetchall()
        for r in results:
            if r['email'] is None: r['email'] = ""
        return {"status": "success", "data": results}
    finally:
        cursor.close()
        conn.close()

@app.post("/api/backup/import")
def import_vault(request: ImportRequest):
    """Restores encrypted data into the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
            INSERT INTO passwords (account_name, email, encrypted_password) 
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE email=VALUES(email), encrypted_password=VALUES(encrypted_password)
        """
        values = [(rec.account_name, rec.email, rec.encrypted_password) for rec in request.records]
        cursor.executemany(sql, values)
        conn.commit()
        return {"status": "success", "message": f"Imported {cursor.rowcount} records."}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=str(err))
    finally:
        cursor.close()
        conn.close()