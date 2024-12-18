from flask import Flask, request, render_template_string, redirect, url_for
from instagram_private_api import Client, ClientError
import threading

# Flask app setup
app = Flask(__name__)

# HTML Template for the Flask App
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
            background-color: #f8f9fa;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            margin: 50px auto;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
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
                <label for="nicknames" class="form-label">New Nicknames for All Members (comma-separated):</label>
                <input type="text" class="form-control" id="nicknames" name="nicknames" required>
            </div>
            <div class="mb-3">
                <label for="groupTitle" class="form-label">New Group Chat Title:</label>
                <input type="text" class="form-control" id="groupTitle" name="groupTitle" required>
            </div>
            <button type="submit" class="btn btn-primary w-100">Update Group Chat</button>
        </form>
    </div>
</body>
</html>
'''

# Global stop flag
STOP_FLAG = False

# Route: Home
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Form Data
        username = request.form.get("username")
        password = request.form.get("password")
        group_id = request.form.get("groupId")
        nicknames = request.form.get("nicknames").split(",")
        group_title = request.form.get("groupTitle")

        # Start a thread to handle Instagram API interactions
        threading.Thread(
            target=update_group_chat, args=(username, password, group_id, nicknames, group_title)
        ).start()

        return "<p>Updating group chat... Check logs for updates.</p>"

    return render_template_string(HTML_TEMPLATE)


def login_instagram(username, password):
    """
    Login to Instagram using the private API.
    """
    try:
        api = Client(username, password)
        print("[SUCCESS] Logged into Instagram successfully!")
        return api
    except ClientError as e:
        print(f"[ERROR] Login failed: {e.msg}")
        return None


def update_group_chat(username, password, group_id, nicknames, group_title):
    """
    Update the nicknames of group members and the group chat title.
    """
    try:
        # Login to Instagram
        api = login_instagram(username, password)
        if not api:
            return

        # Fetch group chat details
        print("[INFO] Fetching group chat details...")
        chat = api.direct_v2_thread(group_id)
        participants = chat.get("users", [])

        # Update Nicknames
        for idx, user in enumerate(participants):
            if idx < len(nicknames):
                nickname = nicknames[idx].strip()
                print(f"[INFO] Updating nickname for {user['username']} to '{nickname}'...")
                api.direct_v2_update_user_nickname(group_id, user["pk"], nickname)
            else:
                print(f"[INFO] No nickname provided for {user['username']}. Skipping.")

        # Update Group Chat Title
        print(f"[INFO] Updating group chat title to '{group_title}'...")
        api.direct_v2_update_title(group_id, group_title)

        print("[SUCCESS] Group chat updated successfully!")

    except ClientError as e:
        print(f"[ERROR] Instagram API error: {e.msg}")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
                
