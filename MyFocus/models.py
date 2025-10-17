# ...existing code...
import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')

def _connect(dbfile=None):
    # resolve relative paths to project folder to avoid multiple DB files
    if not dbfile:
        dbfile = DB_PATH
    elif not os.path.isabs(dbfile):
        dbfile = os.path.join(BASE_DIR, dbfile)
    conn = sqlite3.connect(dbfile, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def db_init(dbfile=None):
    conn = _connect(dbfile)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        category TEXT,
        date TEXT,
        status TEXT DEFAULT 'Pending'
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        datetime TEXT NOT NULL,
        location TEXT
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        target_date TEXT
    )""")
    conn.commit()
    conn.close()

# Task helpers
class tasks:
    DBFILE = DB_PATH
    @staticmethod
    def _conn():
        return _connect(tasks.DBFILE)

    @staticmethod
    def create(title, description=None, category=None, date=None, status='Pending'):
        conn = tasks._conn(); cur = conn.cursor()
        cur.execute("INSERT INTO tasks (title,description,category,date,status) VALUES (?,?,?,?,?)",
                    (title, description, category, date, status))
        conn.commit(); conn.close()

    @staticmethod
    def list(search=None, range_filter=None, filter_by=None):
        conn = tasks._conn(); cur = conn.cursor()
        q = "SELECT * FROM tasks"
        clauses = []
        params = []
        if search:
            clauses.append("(title LIKE ? OR description LIKE ? OR category LIKE ?)")
            s = f"%{search}%"
            params.extend([s,s,s])
        if range_filter:
            clauses.append("date BETWEEN ? AND ?")
            params.extend([range_filter[0], range_filter[1]])
        if filter_by:
            if 'date' in filter_by:
                clauses.append("date = ?"); params.append(filter_by['date'])
        if clauses:
            q += " WHERE " + " AND ".join(clauses)
        q += " ORDER BY date(date) ASC"
        cur.execute(q, params)
        rows = [dict(r) for r in cur.fetchall()]
        conn.close(); return rows

    @staticmethod
    def get(item_id):
        conn = tasks._conn(); cur = conn.cursor()
        cur.execute("SELECT * FROM tasks WHERE id=?", (item_id,))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def update(item_id, **fields):
        conn = tasks._conn(); cur = conn.cursor()
        cols = []
        vals = []
        for k,v in fields.items():
            cols.append(f"{k}=?"); vals.append(v)
        vals.append(item_id)
        cur.execute(f"UPDATE tasks SET {', '.join(cols)} WHERE id=?", vals)
        conn.commit(); conn.close()

    @staticmethod
    def delete(item_id):
        conn = tasks._conn(); cur = conn.cursor()
        cur.execute("DELETE FROM tasks WHERE id=?", (item_id,))
        conn.commit(); conn.close()

    @staticmethod
    def toggle_status(item_id):
        t = tasks.get(item_id)
        if not t:
            return
        new = 'Done' if t['status'] != 'Done' else 'Pending'
        tasks.update(item_id, status=new)

# Events helpers
class events:
    DBFILE = DB_PATH
    @staticmethod
    def _conn():
        return _connect(events.DBFILE)

    @staticmethod
    def create(title, description=None, dt=None, location=None):
        conn = events._conn(); cur = conn.cursor()
        cur.execute("INSERT INTO events (title,description,datetime,location) VALUES (?,?,?,?)",
                    (title, description, dt, location))
        conn.commit(); conn.close()

    @staticmethod
    def list(filter_by=None):
        conn = events._conn(); cur = conn.cursor()
        q = "SELECT * FROM events ORDER BY datetime(datetime) ASC"
        cur.execute(q)
        rows = [dict(r) for r in cur.fetchall()]
        # convenience: allow date-only filter
        if filter_by and 'date_only' in filter_by:
            d = filter_by['date_only']
            rows = [r for r in rows if r.get('datetime') and r['datetime'][:10] == d]
        conn.close(); return rows

    @staticmethod
    def delete(item_id):
        conn = events._conn(); cur = conn.cursor()
        cur.execute("DELETE FROM events WHERE id=?", (item_id,))
        conn.commit(); conn.close()

# Notes helpers
class notes:
    DBFILE = DB_PATH
    @staticmethod
    def _conn():
        return _connect(notes.DBFILE)

    @staticmethod
    def create(content):
        conn = notes._conn(); cur = conn.cursor()
        cur.execute("INSERT INTO notes (content,created_at) VALUES (?,?)", (content, datetime.utcnow().isoformat()))
        conn.commit(); conn.close()

    @staticmethod
    def list():
        conn = notes._conn(); cur = conn.cursor()
        cur.execute("SELECT * FROM notes ORDER BY datetime(created_at) DESC")
        rows = [dict(r) for r in cur.fetchall()]
        conn.close(); return rows

    @staticmethod
    def get(item_id):
        conn = notes._conn(); cur = conn.cursor()
        cur.execute("SELECT * FROM notes WHERE id=?", (item_id,))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def update(item_id, content):
        conn = notes._conn(); cur = conn.cursor()
        cur.execute("UPDATE notes SET content=? WHERE id=?", (content, item_id))
        conn.commit(); conn.close()

    @staticmethod
    def delete(item_id):
        conn = notes._conn(); cur = conn.cursor()
        cur.execute("DELETE FROM notes WHERE id=?", (item_id,))
        conn.commit(); conn.close()

# Plans helpers
class plans:
    DBFILE = DB_PATH
    @staticmethod
    def _conn():
        return _connect(plans.DBFILE)

    @staticmethod
    def create(title, description=None, target_date=None):
        conn = plans._conn(); cur = conn.cursor()
        cur.execute("INSERT INTO plans (title,description,target_date) VALUES (?,?,?)", (title, description, target_date))
        conn.commit(); conn.close()

    @staticmethod
    def list():
        conn = plans._conn(); cur = conn.cursor()
        cur.execute("SELECT * FROM plans ORDER BY CASE WHEN target_date IS NULL THEN 1 ELSE 0 END, target_date ASC")
        rows = [dict(r) for r in cur.fetchall()]
        conn.close(); return rows

    @staticmethod
    def get(item_id):
        conn = plans._conn(); cur = conn.cursor()
        cur.execute("SELECT * FROM plans WHERE id=?", (item_id,))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def update(item_id, title, description=None, target_date=None):
        conn = plans._conn(); cur = conn.cursor()
        cur.execute("UPDATE plans SET title=?, description=?, target_date=? WHERE id=?", (title, description, target_date, item_id))
        conn.commit(); conn.close()

    @staticmethod
    def delete(item_id):
        conn = plans._conn(); cur = conn.cursor()
        cur.execute("DELETE FROM plans WHERE id=?", (item_id,))
        conn.commit(); conn.close()
# ...existing code...