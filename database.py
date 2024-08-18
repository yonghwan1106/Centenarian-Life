import sqlite3
import pandas as pd
from datetime import datetime

def init_db():
    conn = sqlite3.connect('wellness.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS checklist_items
                 (id INTEGER PRIMARY KEY, username TEXT, category TEXT, item TEXT, UNIQUE(username, category, item))''')
    c.execute('''CREATE TABLE IF NOT EXISTS daily_progress
                 (id INTEGER PRIMARY KEY, username TEXT, date TEXT, category TEXT, item TEXT, completed INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS notifications
                 (id INTEGER PRIMARY KEY, username TEXT, item TEXT, time TEXT)''')
    conn.commit()
    conn.close()

def add_user(username, password):
    conn = sqlite3.connect('wellness.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

def get_user(username):
    conn = sqlite3.connect('wellness.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    return user

def get_checklist_items(username):
    conn = sqlite3.connect('wellness.db')
    df = pd.read_sql_query("SELECT * FROM checklist_items WHERE username = ?", conn, params=(username,))
    conn.close()
    return df.groupby('category')['item'].apply(list).to_dict()

def add_checklist_item(username, category, item):
    conn = sqlite3.connect('wellness.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO checklist_items (username, category, item) VALUES (?, ?, ?)", (username, category, item))
    conn.commit()
    conn.close()

def remove_checklist_item(username, category, item):
    conn = sqlite3.connect('wellness.db')
    c = conn.cursor()
    c.execute("DELETE FROM checklist_items WHERE username = ? AND category = ? AND item = ?", (username, category, item))
    conn.commit()
    conn.close()

def save_daily_progress(username, date, progress):
    conn = sqlite3.connect('wellness.db')
    c = conn.cursor()
    for category, items in progress.items():
        for item, completed in items.items():
            c.execute("""INSERT OR REPLACE INTO daily_progress 
                         (username, date, category, item, completed) 
                         VALUES (?, ?, ?, ?, ?)""", 
                      (username, date, category, item, int(completed)))
    conn.commit()
    conn.close()

def get_daily_progress(username, date):
    conn = sqlite3.connect('wellness.db')
    df = pd.read_sql_query("""SELECT category, item, completed 
                              FROM daily_progress 
                              WHERE username = ? AND date = ?""", 
                           conn, params=(username, date))
    conn.close()
    return df.groupby('category').apply(lambda x: x.set_index('item')['completed'].to_dict()).to_dict()

def get_progress_history(username, start_date, end_date):
    conn = sqlite3.connect('wellness.db')
    df = pd.read_sql_query("""SELECT date, category, AVG(completed) as completion_rate
                              FROM daily_progress 
                              WHERE username = ? AND date BETWEEN ? AND ?
                              GROUP BY date, category""", 
                           conn, params=(username, start_date, end_date))
    conn.close()
    return df

def save_notification(username, item, time):
    conn = sqlite3.connect('wellness.db')
    c = conn.cursor()
    c.execute("INSERT INTO notifications (username, item, time) VALUES (?, ?, ?)", (username, item, time))
    conn.commit()
    conn.close()

def get_notifications(username):
    conn = sqlite3.connect('wellness.db')
    df = pd.read_sql_query("SELECT item, time FROM notifications WHERE username = ?", conn, params=(username,))
    conn.close()
    return df.to_dict('records')

def remove_notification(username, item):
    conn = sqlite3.connect('wellness.db')
    c = conn.cursor()
    c.execute("DELETE FROM notifications WHERE username = ? AND item = ?", (username, item))
    conn.commit()
    conn.close()