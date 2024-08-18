import bcrypt
import sqlite3
from typing import Optional, Tuple

DB_NAME = 'wellness.db'

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(stored_password: str, provided_password: str) -> bool:
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))

def register_user(username: str, password: str) -> Tuple[bool, str]:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        hashed_password = hash_password(password)
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return True, "사용자가 성공적으로 등록되었습니다."
    except sqlite3.IntegrityError:
        return False, "이미 존재하는 사용자명입니다."
    finally:
        conn.close()

def authenticate_user(username: str, password: str) -> bool:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    
    if result:
        stored_password = result[0]
        return verify_password(stored_password, password)
    return False

def change_password(username: str, old_password: str, new_password: str) -> Tuple[bool, str]:
    if not authenticate_user(username, old_password):
        return False, "현재 비밀번호가 일치하지 않습니다."
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        hashed_password = hash_password(new_password)
        c.execute("UPDATE users SET password = ? WHERE username = ?", (hashed_password, username))
        conn.commit()
        return True, "비밀번호가 성공적으로 변경되었습니다."
    except Exception as e:
        return False, f"비밀번호 변경 중 오류가 발생했습니다: {str(e)}"
    finally:
        conn.close()

def delete_user(username: str, password: str) -> Tuple[bool, str]:
    if not authenticate_user(username, password):
        return False, "비밀번호가 일치하지 않습니다."
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("DELETE FROM users WHERE username = ?", (username,))
        c.execute("DELETE FROM checklist_items WHERE username = ?", (username,))
        c.execute("DELETE FROM daily_progress WHERE username = ?", (username,))
        c.execute("DELETE FROM reflections WHERE username = ?", (username,))
        c.execute("DELETE FROM notifications WHERE username = ?", (username,))
        conn.commit()
        return True, "사용자 계정이 성공적으로 삭제되었습니다."
    except Exception as e:
        return False, f"계정 삭제 중 오류가 발생했습니다: {str(e)}"
    finally:
        conn.close()