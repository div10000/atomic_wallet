import threading
import requests
import time

# Configuration
BASE_URL = "http://127.0.0.1:8000"

def make_transfer(thread_id):
    payload = {
        "sender_username": "alice",
        "receiver_username": "bob",
        "amount_dollars": 10.0  # Sending $10
    }
    try:
        response = requests.post(f"{BASE_URL}/transfer", json=payload)
        print(f"Thread {thread_id}: Status {response.status_code} - {response.json().get('detail', 'Success')}")
    except Exception as e:
        print(f"Thread {thread_id}: Failed - {e}")

def run_test():
    # 1. Setup: Create users
    print("--- Setting up Wallets ---")
    requests.post(f"{BASE_URL}/create_wallet", json={"username": "alice"}) # Starts with $100
    requests.post(f"{BASE_URL}/create_wallet", json={"username": "bob"})   # Starts with $100
    
    initial_balance = requests.get(f"{BASE_URL}/balance/alice").json()['balance']
    print(f"Alice Initial Balance: ${initial_balance}")

    # 2. Attack: Launch 5 threads at once
    print("\n--- Starting Concurrency Attack (5 x $10 transfers) ---")
    threads = []
    for i in range(5):
        t = threading.Thread(target=make_transfer, args=(i,))
        threads.append(t)
        t.start()

    # Wait for all to finish
    for t in threads:
        t.join()

    # 3. Verify Result
    final_balance = requests.get(f"{BASE_URL}/balance/alice").json()['balance']
    print(f"\n--- Result ---")
    print(f"Alice Final Balance: ${final_balance}")
    
    expected = initial_balance - 50.0
    if final_balance == expected:
        print("✅ SUCCESS: Balance is correct. Race conditions handled.")
    else:
        print(f"❌ FAILURE: Expected ${expected}, but got ${final_balance}. Race condition occurred!")

if __name__ == "__main__":
    # Give the server a second to ensure it's up if you run them close together
    time.sleep(1)
    run_test()