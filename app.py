from flask import Flask, render_template_string, request, flash, redirect, url_for
from instagrapi import Client
import time

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key"

# HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Group Automation</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #1e90ff;
            color: #fff;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            background-color: #333;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5);
            max-width: 400px;
            width: 100%;
        }
        h1 {
            text-align: center;
            color: #ffa500;
        }
        label {
            display: block;
            margin-top: 10px;
            font-weight: bold;
        }
        input, button {
            width: 100%;
            padding: 10px;
            margin-top: 10px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
        }
        input {
            background-color: #444;
            color: #fff;
        }
        input:focus {
            outline: none;
            background-color: #555;
        }
        button {
            background-color: #ffa500;
            color: #000;
            font-weight: bold;
            cursor: pointer;
        }
        button:hover {
            background-color: #ff7f50;
        }
        .message {
            margin-top: 20px;
            text-align: center;
        }
        .success {
            color: #32cd32;
        }
        .error {
            color: #ff4500;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Instagram Group Nickname Automation</h1>
        <form action="/" method="POST">
            <label for="username">Instagram Username:</label>
            <input type="text" id="username" name="username" placeholder="Enter Instagram username" required>
            
            <label for="password">Instagram Password:</label>
            <input type="password" id="password" name="password" placeholder="Enter Instagram password" required>

            <label for="group_id">Target Group Chat ID:</label>
            <input type="text" id="group_id" name="group_id" placeholder="Enter group chat ID" required>
            
            <label for="nickname">New Nickname:</label>
            <input type="text" id="nickname" name="nickname" placeholder="Enter new nickname for members" required>

            <label for="delay">Delay (seconds):</label>
            <input type="number" id="delay" name="delay" placeholder="Enter delay between changes" required>

            <button type="submit">Change Nicknames</button>
        </form>
        {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <div class="message">
            {% for category, message in messages %}
                <p class="{{ category }}">{{ message }}</p>
            {% endfor %}
            </div>
        {% endif %}
        {% endwith %}
    </div>
</body>
</html>
'''

# Route to render form and process input
@app.route("/", methods=["GET", "POST"])
def change_group_nicknames():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        group_id = request.form["group_id"]
        new_nickname = request.form["nickname"]
        delay = int(request.form["delay"])

        try:
            # Login to Instagram
            client = Client()
            client.login(username, password)
            flash("Successfully logged into Instagram.", "success")

            # Fetch group chat members
            group_thread = client.direct_thread(group_id)
            if not group_thread:
                flash("Group not found. Please check the group ID.", "error")
                return redirect(url_for("change_group_nicknames"))

            members = group_thread.users
            flash(f"Found {len(members)} members in the group.", "success")

            # Change nickname for each member
            for member in members:
                try:
                    client.direct_thread_set_title(group_id, new_nickname)
                    flash(f"Nickname changed for {member.username} to {new_nickname}.", "success")
                except Exception as e:
                    flash(f"Failed to change nickname for {member.username}: {str(e)}", "error")
                time.sleep(delay)

            flash("All nicknames changed successfully.", "success")
        except Exception as e:
            flash(f"Error: {str(e)}", "error")

        return redirect(url_for("change_group_nicknames"))

    return render_template_string(HTML_TEMPLATE)


# Run Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
      
