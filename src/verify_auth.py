from database import Database
import os

def test_auth():
    print("--- Testing Authentication & User Management ---")
    
    # Remove existing db to start fresh
    if os.path.exists("attendance.db"):
        os.remove("attendance.db")
    
    db = Database()
    print("Database initialized.")

    # Test Default Users
    admin = db.authenticate_user("admin", "admin")
    assert admin is not None, "Admin login failed"
    assert admin[2] == "管理", "Admin role mismatch"
    print("Default Admin login success.")

    worker = db.authenticate_user("yamada", "1234")
    assert worker is not None, "Worker login failed"
    assert worker[2] == "現場", "Worker role mismatch"
    print("Default Worker login success.")

    # Test User Addition
    success, msg = db.add_user("New User", "現場", "newuser", "pass")
    assert success, f"Add user failed: {msg}"
    print("User addition success.")

    # Test New User Login
    new_user = db.authenticate_user("newuser", "pass")
    assert new_user is not None
    print("New user login success.")

    # Test Duplicate ID
    success, msg = db.add_user("Duplicate", "現場", "newuser", "pass")
    assert not success, "Duplicate user check failed"
    print("Duplicate user check passed.")

    # Test Toggle Active
    db.toggle_user_active(new_user[0], False)
    disabled_user = db.authenticate_user("newuser", "pass")
    assert disabled_user is None, "Disabled user should not login"
    print("User disable success.")

    print("--- All Tests Passed ---")

if __name__ == "__main__":
    test_auth()
