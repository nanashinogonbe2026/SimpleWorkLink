import sqlite3
import datetime
import os

DB_PATH = "attendance.db"

class Database:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                role TEXT NOT NULL
            )
        ''')

        # Records table (Clock-in/out)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                type TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                location TEXT,
                status TEXT DEFAULT '正常',
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Requests table (Applications)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                category TEXT NOT NULL,
                content TEXT,
                amount REAL,
                status TEXT DEFAULT '未承認',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Modification logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS modification_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id INTEGER,
                modified_by INTEGER,
                original_value TEXT,
                new_value TEXT,
                modified_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (record_id) REFERENCES records (id),
                FOREIGN KEY (modified_by) REFERENCES users (id)
            )
        ''')

        # Dummy user for testing if empty
        cursor.execute('SELECT count(*) FROM users')
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO users (name, role) VALUES (?, ?)", ("山田 太郎", "現場"))
            cursor.execute("INSERT INTO users (name, role) VALUES (?, ?)", ("鈴木 一郎", "管理"))
            print("初期ユーザーを追加しました。")

        conn.commit()
        conn.close()

    def add_record(self, user_id, type_str, location):
        conn = self.get_connection()
        cursor = conn.cursor()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO records (user_id, type, timestamp, location, status) VALUES (?, ?, ?, ?, ?)",
            (user_id, type_str, timestamp, location, "正常")
        )
        conn.commit()
        conn.close()
        return timestamp

    def get_all_records(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.id, u.name, r.type, r.timestamp, r.status, r.location 
            FROM records r
            JOIN users u ON r.user_id = u.id
            ORDER BY r.timestamp DESC
        ''')
        records = cursor.fetchall()
        conn.close()
        return records

    def update_record(self, record_id, new_timestamp, new_status, modified_by):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get original record for log
        cursor.execute("SELECT timestamp, status FROM records WHERE id = ?", (record_id,))
        original = cursor.fetchone()
        if not original:
            conn.close()
            return False
        
        original_value = f"Time: {original[0]}, Status: {original[1]}"
        new_val_str = f"Time: {new_timestamp}, Status: {new_status}"
        
        # Update record
        cursor.execute(
            "UPDATE records SET timestamp = ?, status = ? WHERE id = ?",
            (new_timestamp, new_status, record_id)
        )
        
        # Log modification
        cursor.execute(
            "INSERT INTO modification_logs (record_id, modified_by, original_value, new_value) VALUES (?, ?, ?, ?)",
            (record_id, modified_by, original_value, new_val_str)
        )
        
        conn.commit()
        conn.close()
        return True

    def add_request(self, user_id, category, content, amount=0.0):
        conn = self.get_connection()
        cursor = conn.cursor()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO requests (user_id, category, content, amount, status, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, category, content, amount, "未承認", timestamp)
        )
        conn.commit()
        conn.close()
        return True

    def get_monthly_stats(self):
        # Simplified stats for prototype. In real app, filter by year/month.
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get all users
        cursor.execute("SELECT id, name FROM users")
        users = cursor.fetchall()
        
        stats = []
        for u in users:
            uid, name = u
            
            # Calculate work hours (Simplified: Pair Clock-in/out)
            cursor.execute("SELECT type, timestamp FROM records WHERE user_id = ? ORDER BY timestamp ASC", (uid,))
            records = cursor.fetchall()
            
            total_seconds = 0
            last_in = None
            
            for r in records:
                rtype, rtime_str = r
                rtime = datetime.datetime.strptime(rtime_str, "%Y-%m-%d %H:%M:%S")
                
                if rtype == "出勤":
                    last_in = rtime
                elif rtype == "退勤" and last_in:
                    total_seconds += (rtime - last_in).total_seconds()
                    last_in = None
            
            total_hours = round(total_seconds / 3600, 2)
            overtime_hours = max(0, total_hours - 160) # Assuming 160h standard
            
            # Calculate expenses
            cursor.execute("SELECT SUM(amount) FROM requests WHERE user_id = ? AND category = '経費' AND status = '承認済'", (uid,))
            res = cursor.fetchone()
            total_expenses = res[0] if res[0] else 0.0
            
            stats.append({
                "id": uid,
                "name": name,
                "total_hours": total_hours,
                "overtime": overtime_hours,
                "expenses": total_expenses
            })
            
        conn.close()
        return stats

if __name__ == "__main__":
    db = Database()
    print("データベース初期化完了")
