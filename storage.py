import sqlite3
import os

DB_FILE = 'connections.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS connections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            host TEXT NOT NULL,
            port TEXT NOT NULL,
            user TEXT NOT NULL,
            password TEXT NOT NULL,
            dbname TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def save_connection(name, host, port, user, password, dbname):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''
            INSERT INTO connections (name, host, port, user, password, dbname)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, host, port, user, password, dbname))
        conn.commit()
        return True, "Saved successfully"
    except sqlite3.IntegrityError:
        return False, "Connection name already exists"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_connections():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM connections')
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_connection(conn_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DELETE FROM connections WHERE id = ?', (conn_id,))
    conn.commit()
    conn.close()

# Initialize DB on import
init_db()
