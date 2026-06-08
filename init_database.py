import sqlite3
from werkzeug.security import generate_password_hash

def initialize_system_database():
    # Connect to local SQLite database engine
   conn = sqlite3.connect('/data/collaboration.db')
    cursor = conn.cursor()
    
    print("[*] Building infrastructure schema tables...")

    # 1. Create Users Table (RBAC Core)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # 2. Create Projects Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            duration TEXT NOT NULL,
            required_role TEXT NOT NULL,
            created_by TEXT NOT NULL
        )
    ''')

    # 3. Create Contributions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contributions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            staff_name TEXT NOT NULL,
            staff_role TEXT NOT NULL,
            task_title TEXT NOT NULL,
            code_submission TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    ''')

    # Seed User Credentials Dataset safely using Werkzeug security hashes
    # Clear old data to prevent duplication conflicts during setup
    cursor.execute("DELETE FROM users")
    
    default_users = [
        ("Dr. Ekruyota", "Project Administrator", "admin", generate_password_hash("admin123")),
        ("Sarah Connor", "Project Manager", "manager", generate_password_hash("manager123")),
        ("Alex Mercer", "Senior Developer", "developer1", generate_password_hash("dev123")),
        ("Elena Rostova", "UI/UX Designer", "designer1", generate_password_hash("design123"))
    ]
    
    cursor.executemany('''
        INSERT INTO users (name, role, username, password_hash)
        VALUES (?, ?, ?, ?)
    ''', default_users)
    
    # Seed a baseline project record
    cursor.execute("DELETE FROM projects")
    cursor.execute('''
        INSERT INTO projects (title, duration, required_role, created_by)
        VALUES ('Enterprise Cloud Migration Architecture', '12 Weeks', 'Senior Developer', 'Sarah Connor')
    ''')
    
    # Seed a baseline contribution record
    cursor.execute("DELETE FROM contributions")
    cursor.execute('''
        INSERT INTO contributions (project_id, staff_name, staff_role, task_title, code_submission)
        VALUES (1, 'Alex Mercer', 'Senior Developer', 'Setup Core API Gateways', 'def init_api(): print("Gateway Active")')
    ''')

    conn.commit()
    conn.close()
    print("[+] Database compiled successfully with secure pre-seeded staff dataset!")

if __name__ == '__main__':
    initialize_system_database()
