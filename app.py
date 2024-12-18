from flask import Flask, request, render_template_string, redirect, url_for
from instagrapi import Client
import threading
import time

app = Flask(__name__)

# Global variables
INSTAGRAM_CLIENT = None
STOP_FLAG = False
REPLY_MESSAGES = []  # Stores replies from the uploaded TXT file
LOCKED_REPLY = False  # Determines if replies are locked per user
REPLIED_USERS = set()  # Keeps track of users already replied to

# HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Auto-Reply Bot</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #f8f9fa;
            color: #343a40;
        }
        .container {
            margin-top: 50px;
            background: #ffffff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .btn-stop {
            background-color: #dc3545;
            color: #fff;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="text-center">Instagram Auto-Reply Bot</h1>
        <form method="POST" action="/" enctype="multipart/form-data">
            <div class="mb-3">
                <label for="username" class="form-label">Instagram Username:</label>
                <input type="text" class="form-control" id="username" name="username" required>
            </div>
            <div class="mb-3">
                <label for="password" class="form-label">Instagram Password:</label>
                <input type="password" class="form-control" id="password" name="password" required>
            </div>
            <div class="mb-3">
                <label for="txtFile" class="form-label">Upload Reply Messages File (.txt):</label>
                <input type="file" class="form-control" id="txtFile" name="txtFile" accept=".txt" required>
            </div>
            <div class="mb-3">
                <label for="lockedReply" class="form-label">Locked Reply Mode:</label>
                <select class="form-select" id="lockedReply" name="lockedReply" required>
                    <option value="yes">Yes (Reply once per user)</option>
                    <option value="no">No (Always reply)</option>
                </select>
            </div>
            <button type="submit" class="btn btn-primary w-100">Start Auto-Reply</button>
        </form>
        <form method="POST" action="/stop">
            <button type="submit" class="btn btn-stop w-100 mt-3">Stop</button>
        </form>
    </div>
</body>
</html>
'''

# Flask Routes
@app.route("/", methods=["GET", "POST"])
def home():
    global INSTAGRAM_CLIENT, REPLY_MESSAGES, LOCKED_REPLY, REPLIED_USERS, STOP_FLAG

    if request.method == "POST":
        # Reset previous session variables
        STOP_FLAG = False
        REPLIED_USERS = set()

        # Form Data
        username = request.form.get("username")
        password = request.form.get("password")
        locked_reply = request.form.get("lockedReply")
        LOCKED_REPLY = True if locked_reply == "yes" else False

        # Load reply messages from TXT file
        txt_file = request.files["txtFile"]
        try:
            REPLY_MESSAGES = txt_file.read().decode("utf-8").splitlines()
        except Exception as e:
            return f"<p>Error reading file: {e}</p>"

        # Login to Instagram
        try:
            INSTAGRAM_CLIENT = Client()
            INSTAGRAM_CLIENT.login(username, password)
        except Exception as e:
            return f"<p>Login failed: {e}</p>"

        # Start the auto-reply thread
        threading.Thread(target=auto_reply_thread).start()
        return "<p>Auto-reply is running. You can stop the process using the 'Stop' button.</p>"

    return render_template_string(HTML_TEMPLATE)

@app.route("/stop", methods=["POST"])
def stop():
    global STOP_FLAG
    STOP_FLAG = True
    return redirect(url_for("home"))

# Auto-reply Thread
def auto_reply_thread():
    global INSTAGRAM_CLIENT, STOP_FLAG, REPLY_MESSAGES, LOCKED_REPLY, REPLIED_USERS

    print("[INFO] Auto-reply started.")
    while not STOP_FLAG:
        try:
            inbox = INSTAGRAM_CLIENT.direct_threads()
            for thread in inbox:
                if STOP_FLAG:
                    print("[INFO] Auto-reply stopped.")
                    return

                user_id = thread.users[0].pk if thread.users else None
                if not user_id:
                    continue

                # Skip already replied users if locked mode is enabled
                if LOCKED_REPLY and user_id in REPLIED_USERS:
                    continue

                # Send a reply message
                reply_message = REPLY_MESSAGES[0] if REPLY_MESSAGES else "Hello, how can I help you?"
                INSTAGRAM_CLIENT.direct_send(reply_message, thread_id=thread.id)

                # Log the reply and add to replied users
                print(f"[INFO] Replied to {user_id}: {reply_message}")
                REPLIED_USERS.add(user_id)

                # Simulate delay
                time.sleep(2)
        except Exception as e:
            print(f"[ERROR] Auto-reply encountered an error: {e}")
            time.sleep(5)

    print("[INFO] Auto-reply thread exited.")

# Run Flask App
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    
