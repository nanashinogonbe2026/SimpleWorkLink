from database import Database
import os

def test_requests():
    print("--- Testing Request Management ---")
    
    db = Database()
    
    # Ensure we have a user
    user = db.authenticate_user("yamada", "1234")
    if not user:
        print("Creating default user for test...")
        db.add_user("TestUser", "現場", "test_req", "pass")
        user = db.authenticate_user("test_req", "pass")
    
    user_id = user[0]
    
    # 1. Add Request
    print("Adding request...")
    db.add_request(user_id, "有給", "Test Vacation", 0)
    db.add_request(user_id, "経費", "Test Expense", 1000)
    
    # 2. Get Requests
    requests = db.get_all_requests()
    assert len(requests) >= 2, "Should have at least 2 requests"
    print(f"Found {len(requests)} requests.")
    
    # 3. Approve Request
    target_req = requests[0] # (id, name, cat, content, amount, status, ...)
    req_id = target_req[0]
    print(f"Approving request ID {req_id}...")
    
    db.update_request_status(req_id, "承認済")
    
    # 4. Verify Status
    updated_requests = db.get_all_requests()
    updated_req = next(r for r in updated_requests if r[0] == req_id)
    assert updated_req[5] == "承認済", "Status should be '承認済'"
    print("Request approval verified.")
    
    print("--- All Request Tests Passed ---")

if __name__ == "__main__":
    test_requests()
