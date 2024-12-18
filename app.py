from flask import Flask, request, render_template_string
from instagrapi import Client
import threading
import time

# Flask App
app = Flask(__name__)

# Global Variables
instagram_client = None
auto_reply_enabled = False
reply_lock = False
reply_messages = []

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Auto Reply</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #f8f9fa;
            background-image: url('https://i.ibb.co/fFqG2rr/Picsart-24-07-11-17-16-03-306.jpg');
            background-size: cover;
            background-position: center;
        }
        .container {
            margin-top: 50px;
            background: rgba(255, 255, 255, 0.9);
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="text-center">Instagram Auto Reply Bot</h1>
        <form method="POST" action="/login">
            <div class="mb-3">
                <label for="username" class="form-label">Instagram Username:</label>
                <input type="text" class="form-control" id="username" name="username" required>
            </div>
            <div class="mb-3">
                <label for="password" class="form-label">Instagram Password:</label>
                <input type="password" class="form-control" id="password" name="password" required>
            </div>
            <button type="submit" class="btn btn-primary w-100">Login</button>
        </form>
        <form method="POST" action="/upload" enctype="multipart/form-data" class="mt-4">
            <div class="mb-3">
                <label for="txtFile" class="form-label">Upload Reply Messages (.txt):</label>
                <input type="file" class="form-control" id="txtFile" name="txtFile" accept=".txt" required>
            </div>
            <div class="mb-3">
                <label for="lockReply" class="form-label">Lock Reply (Yes/No):</label>
                <select class="form-control" id="lockReply" name="lockReply">
                    <option value="Yes">Yes</option>
                    <option value="No">No</option>
                </select>
            </div>
            <button type="submit" class="btn btn-success w-100">Start Auto Reply</button>
        </form>
        <form method="POST" action="/stop" class="mt-4">
            <button type="submit" class="btn btn-danger w-100">Stop Auto Reply</button>
        </form>
    </div>
</body>
</html>
'''

# Login to Instagram
def login_instagram(username, password):
    global instagram_client
    try:
        instagram_client = Client()
        instagram_client.login(username, password)
        print("[SUCCESS] Logged in to Instagram!")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to login: {e}")
        return False

# Auto-Reply Function
def auto_reply():
    global auto_reply_enabled, reply_lock, reply_messages

    replied_users = set()

    while auto_reply_enabled:
        try:
            inbox = instagram_client.direct_threads()

            for thread in inbox:
                user_id = thread.users[0].pk
                last_message = thread.messages[0].text

                if reply_lock and user_id in replied_users:
                    continue

                # Send auto-reply
                reply = reply_messages[0] if reply_messages else "Hello! This is an auto-reply."
                instagram_client.direct_send(reply, [user_id])
                replied_users.add(user_id)

                print(f"[SUCCESS] Replied to {user_id}: {reply}")
                time.sleep(2)  # Avoid spamming

        except Exception as e:
            print(f"[ERROR] Auto-reply failed: {e}")

        time.sleep(10)  # Poll inbox every 10 seconds

# Route: Home
@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_TEMPLATE)

# Route: Login
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    if login_instagram(username, password):
        return "<p>Login successful! Go back to <a href='/'>Home</a> to upload replies.</p>"
    else:
        return "<p>Login failed! Please try again.</p>"

# Route: Upload Reply Messages
@app.route("/upload", methods=["POST"])
def upload():
    global reply_messages, reply_lock, auto_reply_enabled

    txt_file = request.files["txtFile"]
    lock_reply = request.form.get("lockReply")

    # Read reply messages from file
    try:
        reply_messages = txt_file.read().decode("utf-8").splitlines()
        reply_lock = lock_reply.lower() == "yes"
        auto_reply_enabled = True

        # Start auto-reply thread
        threading.Thread(target=auto_reply).start()
        return "<p>Auto-reply started! Go back to <a href='/'>Home</a>.</p>"

    except Exception as e:
        return f"<p>Error reading file: {e}</p>"

# Route: Stop Auto Reply
@app.route("/stop", methods=["POST"])
def stop():
    global auto_reply_enabled
    auto_reply_enabled = False
    return "<p>Auto-reply stopped! Go back to <a href='/'>Home</a>.</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
