from database import Database
import time

def test_requests_v2():
    print("--- Testing Request System V2 ---")
    
    db = Database()
    
    # Ensure TestUser exists
    user = db.authenticate_user("TestUser", "pass")
    if not user:
        db.add_user("TestUser", "現場", "test_req_v2", "pass")
        user = db.authenticate_user("test_req_v2", "pass")
            
    user_id = user[0]
    
    # 1. Add Request with new category format
    print("Adding request '金銭 - 交通費'...")
    db.add_request(user_id, "金銭 - 交通費", "Taxi to site", 5000)
    
    # Get ID of this request
    requests = db.get_user_requests(user_id)
    target_req = requests[0] # Latest
    req_id = target_req[0]
    print(f"Request ID: {req_id}")
    
    # 2. Reject with Reason
    print("Rejecting with reason '領収書不備'...")
    db.update_request_status(req_id, "却下", "領収書不備")
    
    # Verify Rejection
    updated_req = db.get_user_requests(user_id)[0]
    assert updated_req[4] == "却下"
    assert updated_req[6] == "領収書不備"
    print("Rejection verified.")
    
    # 3. Check Notifications
    print("Checking notifications...")
    notifications = db.check_unread_responses(user_id)
    assert len(notifications) > 0
    print(f"Notifications: {notifications}")
    
    # 4. Correct to Approved
    print("Correcting to '承認済'...")
    db.update_request_status(req_id, "承認済", None)
    
    # Verify Correction
    corrected_req = db.get_user_requests(user_id)[0]
    assert corrected_req[4] == "承認済"
    print("Correction verified.")
    
    print("--- All V2 Tests Passed ---")

if __name__ == "__main__":
    test_requests_v2()
