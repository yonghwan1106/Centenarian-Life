import bcrypt
from database import add_user, get_user

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))

def register_user(username, password):
    hashed_password = hash_password(password)
    add_user(username, hashed_password)

def authenticate_user(username, password):
    user = get_user(username)
    if user and verify_password(user[2], password):
        return True
    return False