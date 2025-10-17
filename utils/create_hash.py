# File: create_hash.py
import hashlib

# Your desired master password
master_password = "replace this thing with the master password u want to create"

# Hash the password using the SHA-256 algorithm
hashed_password = hashlib.sha256(master_password.encode()).hexdigest()

print("Your hashed master password is:")
print(hashed_password)