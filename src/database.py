import sqlite3
import datetime
import os
import hashlib

DB_PATH = "attendance.db"

class Database:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def _hash_password(self, password):
        # In a real app, use salt + pbkdf2_hmac. For prototype, simple sha256 is enough.
        return hashlib.sha256(password.encode()).hexdigest()

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Users table (Updated schema)
        # Check if table exists first to handle migration
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        table_exists = cursor.fetchone()

        if not table_exists:
            cursor.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    login_id TEXT UNIQUE,
                    password TEXT,
                    is_active INTEGER DEFAULT 1
                )
            ''')
        else:
            # Migration: Add columns if they don't exist
            cursor.execute("PRAGMA table_info(users)")
            columns = [info[1] for info in cursor.fetchall()]
            
            if "login_id" not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN login_id TEXT UNIQUE")
            if "password" not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN password TEXT")
            if "is_active" not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1")

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
                rejection_reason TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Requests migration
        cursor.execute("PRAGMA table_info(requests)")
        req_columns = [info[1] for info in cursor.fetchall()]
        if "rejection_reason" not in req_columns:
            cursor.execute("ALTER TABLE requests ADD COLUMN rejection_reason TEXT")

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

        # 既存ユーザーのマイグレーション（login_idがNULLのユーザーを更新）
        cursor.execute("SELECT id, name, role FROM users WHERE login_id IS NULL AND is_active = 1")
        legacy_users = cursor.fetchall()
        for uid, name, role in legacy_users:
            # デフォルトのlogin_idとパスワードを生成
            if role == "管理":
                new_login = "admin"
                new_pass = self._hash_password("admin")
            else:
                new_login = f"user{uid}"
                new_pass = self._hash_password("1234")
            
            try:
                cursor.execute("UPDATE users SET login_id = ?, password = ? WHERE id = ?", (new_login, new_pass, uid))
                print(f"ユーザー移行完了 {name}: ID={new_login}")
            except sqlite3.IntegrityError:
                new_login = f"user{uid}_{datetime.datetime.now().strftime('%M%S')}"
                cursor.execute("UPDATE users SET login_id = ?, password = ? WHERE id = ?", (new_login, new_pass, uid))

        # テーブルが空の場合、初期ユーザーを作成
        cursor.execute('SELECT count(*) FROM users')
        if cursor.fetchone()[0] == 0:
            # 管理者ユーザー
            cursor.execute(
                "INSERT INTO users (name, role, login_id, password) VALUES (?, ?, ?, ?)", 
                ("鈴木 一郎", "管理", "admin", self._hash_password("admin"))
            )
            # 現場スタッフ
            cursor.execute(
                "INSERT INTO users (name, role, login_id, password) VALUES (?, ?, ?, ?)", 
                ("山田 太郎", "現場", "yamada", self._hash_password("1234"))
            )
            print("初期ユーザーを追加しました (admin/admin, yamada/1234)")

        conn.commit()
        conn.close()

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

    def get_all_requests(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.id, u.name, r.category, r.content, r.amount, r.status, r.timestamp, r.rejection_reason
            FROM requests r
            JOIN users u ON r.user_id = u.id
            ORDER BY r.timestamp DESC
        ''')
        requests = cursor.fetchall()
        conn.close()
        return requests

    def get_user_requests(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, category, content, amount, status, timestamp, rejection_reason
            FROM requests
            WHERE user_id = ?
            ORDER BY timestamp DESC
        ''', (user_id,))
        requests = cursor.fetchall()
        conn.close()
        return requests

    def update_request_status(self, request_id, new_status, reason=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE requests SET status = ?, rejection_reason = ? WHERE id = ?", 
            (new_status, reason, request_id)
        )
        conn.commit()
        conn.close()
        return True

    def check_unread_responses(self, user_id):
        # Simplified logic: Check for any Approved/Rejected requests in the last 24 hours
        # In a real app, we would have a 'read' flag.
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check for recent status changes (Simulated by checking recent timestamp + status not Pending)
        # Actually, since we don't have 'updated_at', we use 'timestamp' which is created_at.
        # This is not perfect for 'unread' checks. 
        # Better: Just return the count of non-pending requests for now to show "You have X processed requests".
        # Or better yet, since we didn't implement 'is_read', let's just fetch the last 3 non-pending requests.
        cursor.execute('''
            SELECT category, status, rejection_reason FROM requests 
            WHERE user_id = ? AND status != '未承認' 
            ORDER BY timestamp DESC LIMIT 3
        ''', (user_id,))
        
        recent = cursor.fetchall()
        conn.close()
        return recent

    # --- User Management Methods ---

    def authenticate_user(self, login_id, password):
        conn = self.get_connection()
        cursor = conn.cursor()
        hashed = self._hash_password(password)
        
        cursor.execute("SELECT id, name, role FROM users WHERE login_id = ? AND password = ? AND is_active = 1", (login_id, hashed))
        user = cursor.fetchone()
        conn.close()
        return user # (id, name, role) or None

    def add_user(self, name, role, login_id, password):
        conn = self.get_connection()
        cursor = conn.cursor()
        hashed = self._hash_password(password)
        try:
            cursor.execute(
                "INSERT INTO users (name, role, login_id, password, is_active) VALUES (?, ?, ?, ?, 1)",
                (name, role, login_id, hashed)
            )
            conn.commit()
            return True, "ユーザーを追加しました"
        except sqlite3.IntegrityError:
            return False, "ログインIDが既に存在します"
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def get_all_users(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, role, login_id, is_active FROM users ORDER BY id")
        users = cursor.fetchall()
        conn.close()
        return users

    def update_user_password(self, user_id, new_password):
        conn = self.get_connection()
        cursor = conn.cursor()
        hashed = self._hash_password(new_password)
        cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed, user_id))
        conn.commit()
        conn.close()
        return True

    def toggle_user_active(self, user_id, is_active):
        conn = self.get_connection()
        cursor = conn.cursor()
        val = 1 if is_active else 0
        cursor.execute("UPDATE users SET is_active = ? WHERE id = ?", (val, user_id))
        conn.commit()
        conn.close()
        return True

    # --- Record Methods ---

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

    def get_all_requests(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.id, u.name, r.category, r.content, r.amount, r.status, r.timestamp, r.rejection_reason
            FROM requests r
            JOIN users u ON r.user_id = u.id
            ORDER BY r.timestamp DESC
        ''')
        requests = cursor.fetchall()
        conn.close()
        return requests

    def get_user_requests(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, category, content, amount, status, timestamp, rejection_reason
            FROM requests
            WHERE user_id = ?
            ORDER BY timestamp DESC
        ''', (user_id,))
        requests = cursor.fetchall()
        conn.close()
        return requests

    def update_request_status(self, request_id, new_status, reason=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE requests SET status = ?, rejection_reason = ? WHERE id = ?", 
            (new_status, reason, request_id)
        )
        conn.commit()
        conn.close()
        return True

    def check_unread_responses(self, user_id):
        # Simplified logic: fetch the last 3 non-pending requests.
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT category, status, rejection_reason FROM requests 
            WHERE user_id = ? AND status != '未承認' 
            ORDER BY timestamp DESC LIMIT 3
        ''', (user_id,))
        recent = cursor.fetchall()
        conn.close()
        return recent

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
