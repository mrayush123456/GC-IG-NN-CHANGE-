from flask import Flask, request, render_template_string, flash, redirect, url_for
from instagrapi import Client

app = Flask(__name__)
app.secret_key = "your_secret_key"

# HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Group Title Updater</title>
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
            margin-bottom: 20px;
        }
        label {
            display: block;
            font-weight: bold;
            margin: 10px 0 5px;
            color: #333;
        }
        input, button {
            width: 100%;
            padding: 10px;
            margin-bottom: 15px;
            border: 1px solid #ccc;
            border-radius: 5px;
            font-size: 16px;
        }
        input:focus, button:focus {
            outline: none;
            border-color: #007BFF;
            box-shadow: 0 0 5px rgba(0, 123, 255, 0.5);
        }
        button {
            background-color: #007BFF;
            color: white;
            border: none;
            cursor: pointer;
            font-weight: bold;
        }
        button:hover {
            background-color: #0056b3;
        }
        .message {
            text-align: center;
            margin-top: 10px;
            font-size: 14px;
        }
        .success {
            color: green;
        }
        .error {
            color: red;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Instagram Group Title Updater</h1>
        <form action="/" method="POST">
            <label for="username">Instagram Username:</label>
            <input type="text" id="username" name="username" placeholder="Enter your username" required>

            <label for="password">Instagram Password:</label>
            <input type="password" id="password" name="password" placeholder="Enter your password" required>

            <label for="thread_id">Group Thread ID:</label>
            <input type="text" id="thread_id" name="thread_id" placeholder="Enter group thread ID" required>

            <label for="new_title">New Title:</label>
            <input type="text" id="new_title" name="new_title" placeholder="Enter new title for the group" required>

            <label for="lock_title">Lock Title (yes/no):</label>
            <input type="text" id="lock_title" name="lock_title" placeholder="yes or no" required>

            <button type="submit">Update Title</button>
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

# Endpoint to handle requests
@app.route("/", methods=["GET", "POST"])
def update_group_title():
    if request.method == "POST":
        try:
            # Get form data
            username = request.form["username"]
            password = request.form["password"]
            thread_id = request.form["thread_id"]
            new_title = request.form["new_title"]
            lock_title = request.form["lock_title"].lower()

            # Validate lock_title input
            if lock_title not in ["yes", "no"]:
                flash("Lock Title must be either 'yes' or 'no'.", "error")
                return redirect(url_for("update_group_title"))

            # Login to Instagram
            cl = Client()
            cl.login(username, password)
            flash("[SUCCESS] Logged into Instagram!", "success")

            # Update group thread title
            cl.direct_thread_update_title(thread_id=thread_id, title=new_title)
            flash(f"[SUCCESS] Group title updated to: {new_title}", "success")

            # Lock title if required
            if lock_title == "yes":
                # Simulate a "locked" feature (custom implementation)
                # Actual Instagram API does not support locking titles
                # Logic can be extended as per business needs
                flash("[INFO] Title has been 'locked' (custom feature simulated).", "info")

            return redirect(url_for("update_group_title"))

        except Exception as e:
            flash(f"[ERROR] {str(e)}", "error")
            return redirect(url_for("update_group_title"))

    # Render HTML form
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
