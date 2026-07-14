import sqlite3
import json
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'game.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cases (
            id TEXT PRIMARY KEY,
            case_data TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_saves (
            save_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            create_time TEXT NOT NULL,
            update_time TEXT NOT NULL,
            save_name TEXT NOT NULL,
            case_data TEXT NOT NULL,
            game_state TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            case_id TEXT NOT NULL,
            game_state TEXT NOT NULL,
            create_time TEXT NOT NULL,
            update_time TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    print("数据库初始化完成")

def save_case(case_id, case_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO cases (id, case_data) VALUES (?, ?)
    ''', (case_id, json.dumps(case_data)))
    conn.commit()
    conn.close()

def get_case(case_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT case_data FROM cases WHERE id = ?', (case_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row['case_data'])
    return None

def save_session(session_id, case_id, game_state):
    import time
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO sessions 
        (session_id, case_id, game_state, create_time, update_time)
        VALUES (?, ?, ?, ?, ?)
    ''', (session_id, case_id, json.dumps(game_state), now, now))
    conn.commit()
    conn.close()

def get_session(session_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sessions WHERE session_id = ?', (session_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            'session_id': row['session_id'],
            'case_id': row['case_id'],
            'game_state': json.loads(row['game_state']),
            'create_time': row['create_time'],
            'update_time': row['update_time']
        }
    return None

def save_game_save(save_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO game_saves 
        (save_id, user_id, create_time, update_time, save_name, case_data, game_state)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        save_data['save_id'],
        save_data['user_id'],
        save_data['create_time'],
        save_data['update_time'],
        save_data['save_name'],
        json.dumps(save_data['case_data']),
        json.dumps(save_data['game_state'])
    ))
    conn.commit()
    conn.close()

def get_game_saves(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM game_saves WHERE user_id = ?', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_game_save(save_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM game_saves WHERE save_id = ?', (save_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            'save_id': row['save_id'],
            'user_id': row['user_id'],
            'create_time': row['create_time'],
            'update_time': row['update_time'],
            'save_name': row['save_name'],
            'case_data': json.loads(row['case_data']),
            'game_state': json.loads(row['game_state'])
        }
    return None

def delete_game_save(save_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM game_saves WHERE save_id = ?', (save_id,))
    conn.commit()
    conn.close()
    return True