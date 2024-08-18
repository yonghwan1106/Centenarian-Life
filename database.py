import sqlite3
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

DB_NAME = 'wellness.db'

def init_db() -> None:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS checklist_items
                 (id INTEGER PRIMARY KEY, username TEXT, category TEXT, item TEXT, 
                 UNIQUE(username, category, item))''')
    c.execute('''CREATE TABLE IF NOT EXISTS daily_progress
                 (id INTEGER PRIMARY KEY, username TEXT, date TEXT, category TEXT, 
                 item TEXT, completed INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS reflections
                 (id INTEGER PRIMARY KEY, username TEXT, date TEXT, achievements TEXT, 
                 improvements TEXT, tomorrow_goals TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS notifications
                 (id INTEGER PRIMARY KEY, username TEXT, item TEXT, time TEXT)''')
    conn.commit()
    conn.close()

def get_checklist_items(username: str) -> Dict[str, List[str]]:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT category, item FROM checklist_items WHERE username = ?", (username,))
    items = c.fetchall()
    conn.close()
    checklist: Dict[str, List[str]] = {}
    for category, item in items:
        if category not in checklist:
            checklist[category] = []
        checklist[category].append(item)
    return checklist

def add_checklist_item(username: str, category: str, item: str) -> None:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO checklist_items (username, category, item) VALUES (?, ?, ?)",
              (username, category, item))
    conn.commit()
    conn.close()

def remove_checklist_item(username: str, category: str, item: str) -> None:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM checklist_items WHERE username = ? AND category = ? AND item = ?",
              (username, category, item))
    conn.commit()
    conn.close()

def save_daily_progress(username: str, date: str, progress: Dict[str, Dict[str, bool]]) -> None:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    for category, items in progress.items():
        for item, completed in items.items():
            c.execute("""INSERT OR REPLACE INTO daily_progress 
                         (username, date, category, item, completed) 
                         VALUES (?, ?, ?, ?, ?)""", 
                      (username, date, category, item, int(completed)))
    conn.commit()
    conn.close()

def get_daily_progress(username: str, date: str) -> Dict[str, Dict[str, bool]]:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""SELECT category, item, completed 
                 FROM daily_progress 
                 WHERE username = ? AND date = ?""", (username, date))
    progress = c.fetchall()
    conn.close()
    result: Dict[str, Dict[str, bool]] = {}
    for category, item, completed in progress:
        if category not in result:
            result[category] = {}
        result[category][item] = bool(completed)
    return result

def get_progress_history(username: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""SELECT date, category, AVG(completed) as completion_rate
                 FROM daily_progress 
                 WHERE username = ? AND date BETWEEN ? AND ?
                 GROUP BY date, category""", 
              (username, start_date, end_date))
    history = c.fetchall()
    conn.close()
    return [{"date": date, "category": category, "completion_rate": rate} for date, category, rate in history]

def save_reflection(username: str, date: str, achievements: str, improvements: str, tomorrow_goals: str) -> None:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""INSERT OR REPLACE INTO reflections 
                 (username, date, achievements, improvements, tomorrow_goals) 
                 VALUES (?, ?, ?, ?, ?)""", 
              (username, date, achievements, improvements, tomorrow_goals))
    conn.commit()
    conn.close()

def get_recent_reflection(username: str) -> Optional[Dict[str, str]]:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""SELECT date, achievements, improvements, tomorrow_goals 
                 FROM reflections 
                 WHERE username = ? 
                 ORDER BY date DESC LIMIT 1""", (username,))
    reflection = c.fetchone()
    conn.close()
    if reflection:
        return {
            "date": reflection[0],
            "achievements": reflection[1],
            "improvements": reflection[2],
            "tomorrow_goals": reflection[3]
        }
    return None

def save_notification(username: str, item: str, time: str) -> None:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO notifications (username, item, time) VALUES (?, ?, ?)",
              (username, item, time))
    conn.commit()
    conn.close()

def get_notifications(username: str) -> List[Dict[str, str]]:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT item, time FROM notifications WHERE username = ?", (username,))
    notifications = c.fetchall()
    conn.close()
    return [{"item": item, "time": time} for item, time in notifications]

def remove_notification(username: str, item: str) -> None:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM notifications WHERE username = ? AND item = ?", (username, item))
    conn.commit()
    conn.close()

def export_user_data(username: str) -> str:
    data = {
        "checklist_items": get_checklist_items(username),
        "daily_progress": {},
        "reflections": [],
        "notifications": get_notifications(username)
    }
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 일일 진행 상황 내보내기
    c.execute("SELECT date, category, item, completed FROM daily_progress WHERE username = ?", (username,))
    for date, category, item, completed in c.fetchall():
        if date not in data["daily_progress"]:
            data["daily_progress"][date] = {}
        if category not in data["daily_progress"][date]:
            data["daily_progress"][date][category] = {}
        data["daily_progress"][date][category][item] = bool(completed)
    
    # 성찰 내보내기
    c.execute("SELECT date, achievements, improvements, tomorrow_goals FROM reflections WHERE username = ?", (username,))
    data["reflections"] = [
        {
            "date": date,
            "achievements": achievements,
            "improvements": improvements,
            "tomorrow_goals": tomorrow_goals
        }
        for date, achievements, improvements, tomorrow_goals in c.fetchall()
    ]
    
    conn.close()
    return json.dumps(data, indent=2)

def import_user_data(username: str, data: str) -> None:
    parsed_data = json.loads(data)
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 체크리스트 항목 가져오기
    for category, items in parsed_data["checklist_items"].items():
        for item in items:
            c.execute("INSERT OR IGNORE INTO checklist_items (username, category, item) VALUES (?, ?, ?)",
                      (username, category, item))
    
    # 일일 진행 상황 가져오기
    for date, categories in parsed_data["daily_progress"].items():
        for category, items in categories.items():
            for item, completed in items.items():
                c.execute("""INSERT OR REPLACE INTO daily_progress 
                             (username, date, category, item, completed) 
                             VALUES (?, ?, ?, ?, ?)""", 
                          (username, date, category, item, int(completed)))
    
    # 성찰 가져오기
    for reflection in parsed_data["reflections"]:
        c.execute("""INSERT OR REPLACE INTO reflections 
                     (username, date, achievements, improvements, tomorrow_goals) 
                     VALUES (?, ?, ?, ?, ?)""", 
                  (username, reflection["date"], reflection["achievements"],
                   reflection["improvements"], reflection["tomorrow_goals"]))
    
    # 알림 가져오기
    for notification in parsed_data["notifications"]:
        c.execute("INSERT INTO notifications (username, item, time) VALUES (?, ?, ?)",
                  (username, notification["item"], notification["time"]))
    
    conn.commit()
    conn.close()