import requests
import time
import sys

# Add API key header for authentication
HEADERS = {'X-API-Key': 'dev-key-12345'}

# Wait for server to start
for i in range(30):
    try:
        r = requests.get('http://localhost:8000/health', headers=HEADERS, timeout=2)
        if r.status_code == 200:
            print('Server is ready!')
            break
    except:
        time.sleep(1)
else:
    print('Server did not start in time')
    sys.exit(1)

print("\n=== Test 1: New session (no session_id) ===")
r = requests.post('http://localhost:8000/chat', json={'message': 'Hello, what is the hotel name?'}, headers=HEADERS, timeout=30)
data = r.json()
session_id = data.get('session_id')
print(f'Session ID: {session_id}')
print(f'Response: {data.get("response")}')
print(f'Message count: {data.get("message_count")}')

print("\n=== Test 2: Follow-up in same session ===")
r = requests.post('http://localhost:8000/chat', json={
    'message': 'What room types do you have?',
    'session_id': session_id
}, headers=HEADERS, timeout=30)
data = r.json()
print(f'Session ID: {data.get("session_id")}')
print(f'Response: {data.get("response")}')
print(f'Message count: {data.get("message_count")}')

print("\n=== Test 3: Follow-up referencing previous context ===")
r = requests.post('http://localhost:8000/chat', json={
    'message': 'Which one is the most expensive?',
    'session_id': session_id
}, headers=HEADERS, timeout=30)
data = r.json()
print(f'Session ID: {data.get("session_id")}')
print(f'Response: {data.get("response")}')
print(f'Message count: {data.get("message_count")}')

print("\n=== Test 4: New session (different session_id) ===")
r = requests.post('http://localhost:8000/chat', json={'message': 'What is the check-in time?'}, headers=HEADERS, timeout=30)
data = r.json()
new_session_id = data.get('session_id')
print(f'New Session ID: {new_session_id}')
print(f'Response: {data.get("response")}')
print(f'Message count: {data.get("message_count")}')

print("\n=== Test 5: Verify session isolation ===")
r = requests.post('http://localhost:8000/chat', json={
    'message': 'What was the hotel name I asked before?',
    'session_id': new_session_id
}, headers=HEADERS, timeout=30)
data = r.json()
print(f'Session ID: {data.get("session_id")}')
print(f'Response: {data.get("response")}')
print(f'Message count: {data.get("message_count")}')

print("\n=== Test 6: Availability follow-up ===")
r = requests.post('http://localhost:8000/chat', json={
    'message': 'Check availability for Deluxe Room on 2026-12-20 to 2026-12-22',
    'session_id': session_id
}, headers=HEADERS, timeout=30)
data = r.json()
print(f'Session ID: {data.get("session_id")}')
print(f'Response: {data.get("response")}')
print(f'Message count: {data.get("message_count")}')

print("\n=== Test 7: Follow-up on availability result ===")
r = requests.post('http://localhost:8000/chat', json={
    'message': 'What about Family Suite for the same dates?',
    'session_id': session_id
}, headers=HEADERS, timeout=30)
data = r.json()
print(f'Session ID: {data.get("session_id")}')
print(f'Response: {data.get("response")}')
print(f'Message count: {data.get("message_count")}')

print("\n=== All memory tests completed! ===")