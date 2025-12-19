import sqlite3
import os

# Ensure data directory exists
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Database path in data directory for Docker volume persistence
DB_FILE = os.path.join(DATA_DIR, 'connections.db')

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Create table with environment field
    c.execute('''
        CREATE TABLE IF NOT EXISTS connections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            environment TEXT NOT NULL DEFAULT 'Production',
            host TEXT NOT NULL,
            port TEXT NOT NULL,
            user TEXT NOT NULL,
            password TEXT NOT NULL,
            dbname TEXT NOT NULL
        )
    ''')
    
    # Migration: Add environment column to existing databases
    try:
        c.execute("ALTER TABLE connections ADD COLUMN environment TEXT NOT NULL DEFAULT 'Production'")
        conn.commit()
    except sqlite3.OperationalError:
        # Column already exists
        pass
    
    conn.commit()
    conn.close()

def save_connection(name, host, port, user, password, dbname, environment='Production'):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''
            INSERT INTO connections (name, environment, host, port, user, password, dbname)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, environment, host, port, user, password, dbname))
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
    c.execute('SELECT * FROM connections ORDER BY environment, name')
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_connections_by_environment():
    """Get connections grouped by environment"""
    connections = get_connections()
    grouped = {}
    for conn in connections:
        env = conn.get('environment', 'Production')
        if env not in grouped:
            grouped[env] = []
        grouped[env].append(conn)
    return grouped

def delete_connection(conn_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DELETE FROM connections WHERE id = ?', (conn_id,))
    conn.commit()
    conn.close()

# Initialize DB on import
init_db()
