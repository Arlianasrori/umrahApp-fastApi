import bcrypt

# Function to create a hashed password
def create_hash_password(password: str) -> str:
    """
    Creates a hashed password using bcrypt.

    Args:
        password (str): The plain text password to be hashed.

    Returns:
        str: The hashed password as a UTF-8 encoded string.
    """
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hash_password = bcrypt.hashpw(pwd_bytes, salt)
    return hash_password.decode('utf-8')

# Function to verify a hashed password
def verify_hash_password(password: str, hashPassword: str) -> bool:
    """
    Verifies a plain text password against a hashed password.

    Args:
        password (str): The plain text password to be verified.
        hashPassword (str): The hashed password to compare against.

    Returns:
        bool: True if the password matches the hash, False otherwise.
    """
    plain_password_byte = password.encode('utf-8')
    hash_password_byte = hashPassword.encode('utf-8')
    print(plain_password_byte, hash_password_byte)
    isPassword = bcrypt.checkpw(plain_password_byte, hash_password_byte)
    return isPassword