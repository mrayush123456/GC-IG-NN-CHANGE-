from flask import Flask, render_template_string, request, redirect, flash, url_for
from instagrapi import Client
import time

app = Flask(__name__)
app.secret_key = "your_secret_key"

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Group Name Manager</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .container {
            background-color: #ffffff;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
            max-width: 400px;
            width: 100%;
        }
        h1 {
            text-align: center;
            color: #333;
        }
        label {
            display: block;
            font-weight: bold;
            margin: 10px 0 5px;
        }
        input, select, button {
            width: 100%;
            padding: 10px;
            margin-bottom: 15px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        button {
            background-color: #007BFF;
            color: white;
            border: none;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
        .message {
            color: red;
            font-size: 14px;
            text-align: center;
        }
        .success {
            color: green;
            font-size: 14px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Group Name Manager</h1>
        <form action="/" method="POST">
            <label for="username">Instagram Username:</label>
            <input type="text" id="username" name="username" placeholder="Enter your username" required>

            <label for="password">Instagram Password:</label>
            <input type="password" id="password" name="password" placeholder="Enter your password" required>

            <label for="thread_id">Group Thread ID:</label>
            <input type="text" id="thread_id" name="thread_id" placeholder="Enter group thread ID" required>

            <label for="group_name">New Group Name:</label>
            <input type="text" id="group_name" name="group_name" placeholder="Enter new group name" required>

            <label for="lock_group">Lock Group Name:</label>
            <select id="lock_group" name="lock_group" required>
                <option value="no">No</option>
                <option value="yes">Yes</option>
            </select>

            <button type="submit">Apply Changes</button>
        </form>
        {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
        <div>
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

# Lock status dictionary to store locked group names
lock_status = {}

@app.route("/", methods=["GET", "POST"])
def manage_group_name():
    if request.method == "POST":
        try:
            # Get form data
            username = request.form["username"]
            password = request.form["password"]
            thread_id = request.form["thread_id"]
            group_name = request.form["group_name"]
            lock_group = request.form["lock_group"]

            # Check if the group is locked
            if lock_status.get(thread_id, {}).get("locked", False):
                flash("This group name is locked and cannot be changed.", "message")
                return redirect(url_for("manage_group_name"))

            # Login to Instagram
            client = Client()
            client.login(username, password)

            # Change group name
            client.direct_thread_name(thread_id, group_name)
            flash(f"Group name successfully changed to '{group_name}'", "success")

            # Handle locking
            if lock_group == "yes":
                lock_status[thread_id] = {"locked": True, "name": group_name}
                flash("Group name has been locked.", "success")
            else:
                lock_status.pop(thread_id, None)

            return redirect(url_for("manage_group_name"))

        except Exception as e:
            flash(f"Error: {str(e)}", "message")
            return redirect(url_for("manage_group_name"))

    # Render the form
    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run(debug=True)
    
