from flask import Flask, request, render_template_string, redirect, url_for
from instagrapi import Client
import threading

app = Flask(__name__)

# Global variables for the client and stop flag
INSTAGRAM_CLIENT = None
STOP_FLAG = False

# HTML Template with RGB styling
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Group Chat Manager</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background-color: rgb(245, 245, 245);
            background-image: linear-gradient(to bottom right, rgb(255, 223, 186), rgb(186, 225, 255));
            font-family: Arial, sans-serif;
            padding: 20px;
        }
        .container {
            background-color: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: rgb(34, 34, 59);
        }
        .btn {
            background-color: rgb(102, 153, 255);
            color: white;
        }
        .btn:hover {
            background-color: rgb(51, 102, 204);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="text-center">Instagram Group Chat Manager</h1>
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
                <label for="groupId" class="form-label">Target Group Chat ID:</label>
                <input type="text" class="form-control" id="groupId" name="groupId" required>
            </div>
            <div class="mb-3">
                <label for="newTitle" class="form-label">New Group Title:</label>
                <input type="text" class="form-control" id="newTitle" name="newTitle" required>
            </div>
            <div class="mb-3">
                <label for="nickname" class="form-label">New Nickname for All Members:</label>
                <input type="text" class="form-control" id="nickname" name="nickname" required>
            </div>
            <button type="submit" class="btn w-100">Update Group Chat</button>
        </form>
        <form method="POST" action="/stop">
            <button type="submit" class="btn btn-danger w-100 mt-3">Stop Operation</button>
        </form>
    </div>
</body>
</html>
'''

# Route: Home
@app.route("/", methods=["GET", "POST"])
def home():
    global INSTAGRAM_CLIENT, STOP_FLAG
    STOP_FLAG = False  # Reset stop flag for new sessions

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        group_id = request.form.get("groupId")
        new_title = request.form.get("newTitle")
        nickname = request.form.get("nickname")

        # Login to Instagram in a separate thread
        threading.Thread(target=manage_group_chat, args=(username, password, group_id, new_title, nickname)).start()

        return "<p>Operation started. You can stop it using the 'Stop Operation' button.</p>"

    return render_template_string(HTML_TEMPLATE)

# Route: Stop
@app.route("/stop", methods=["POST"])
def stop():
    global STOP_FLAG
    STOP_FLAG = True
    return redirect(url_for("home"))

# Function: Manage Group Chat
def manage_group_chat(username, password, group_id, new_title, nickname):
    global INSTAGRAM_CLIENT, STOP_FLAG

    try:
        # Login to Instagram
        INSTAGRAM_CLIENT = Client()
        INSTAGRAM_CLIENT.login(username, password)
        print("[INFO] Logged into Instagram successfully!")

        # Update Group Chat Title
        INSTAGRAM_CLIENT.direct_thread_update_title(group_id, new_title)
        print(f"[INFO] Updated group title to: {new_title}")

        # Fetch Group Members
        thread_info = INSTAGRAM_CLIENT.direct_thread(group_id)
        members = thread_info.users

        # Update Nicknames
        for member in members:
            if STOP_FLAG:
                print("[INFO] Operation stopped by user.")
                return

            member_id = member.pk
            INSTAGRAM_CLIENT.direct_thread_update_user_title(group_id, member_id, nickname)
            print(f"[INFO] Updated nickname for user {member.username} to: {nickname}")

        print("[INFO] All operations completed successfully!")

    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    
