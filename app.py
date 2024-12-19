from instagrapi import Client
from flask import Flask, request, jsonify
import threading
import time

app = Flask(__name__)

# Global variables
client = Client()
chatbot_running = False
stop_flag = False

# Login to Instagram
def login_instagram(username, password):
    try:
        client.login(username, password)
        print("[SUCCESS] Logged in to Instagram!")
        return True
    except Exception as e:
        print(f"[ERROR] Login failed: {e}")
        return False

# Fetch all group chats
def fetch_group_chats():
    try:
        inbox = client.direct_threads()
        groups = [
            thread for thread in inbox if thread.thread_type == "group"
        ]
        return groups
    except Exception as e:
        print(f"[ERROR] Failed to fetch group chats: {e}")
        return []

# Check if group name is locked
def is_group_name_locked(thread_id):
    try:
        thread_info = client.direct_thread(thread_id)
        return thread_info.is_name_locked
    except Exception as e:
        print(f"[ERROR] Could not check group lock status: {e}")
        return True  # Assume locked if error occurs

# Update group chat name
def update_group_name(thread_id, new_name):
    try:
        if not is_group_name_locked(thread_id):
            client.direct_thread_update_title(thread_id, new_name)
            print(f"[SUCCESS] Group chat name updated to '{new_name}'!")
        else:
            print("[INFO] Group chat name is locked. Cannot update.")
    except Exception as e:
        print(f"[ERROR] Failed to update group chat name: {e}")

# Chatbot function to monitor and update group name
def chatbot_function(thread_id, delay, new_name):
    global stop_flag
    while not stop_flag:
        update_group_name(thread_id, new_name)
        time.sleep(delay)
    print("[INFO] Chatbot stopped.")

# Flask routes
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if login_instagram(username, password):
        return jsonify({"message": "Login successful!"}), 200
    return jsonify({"message": "Login failed!"}), 400

@app.route("/groups", methods=["GET"])
def groups():
    groups = fetch_group_chats()
    group_list = [{"id": g.thread_id, "name": g.title} for g in groups]
    return jsonify(group_list), 200

@app.route("/start-chatbot", methods=["POST"])
def start_chatbot():
    global chatbot_running, stop_flag
    data = request.json
    thread_id = data.get("thread_id")
    new_name = data.get("new_name")
    delay = data.get("delay", 60)

    if chatbot_running:
        return jsonify({"message": "Chatbot is already running!"}), 400

    chatbot_running = True
    stop_flag = False
    threading.Thread(target=chatbot_function, args=(thread_id, delay, new_name)).start()
    return jsonify({"message": "Chatbot started!"}), 200

@app.route("/stop-chatbot", methods=["POST"])
def stop_chatbot():
    global chatbot_running, stop_flag
    stop_flag = True
    chatbot_running = False
    return jsonify({"message": "Chatbot stopped!"}), 200

@app.route("/check-lock", methods=["POST"])
def check_lock():
    data = request.json
    thread_id = data.get("thread_id")
    locked = is_group_name_locked(thread_id)
    return jsonify({"locked": locked}), 200

# Run Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
