from flask import Flask, render_template, redirect, url_for
from datetime import datetime
import os
import chatbot_app as bot

# path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

print("BASE_DIR =", BASE_DIR)
print("TEMPLATES_DIR =", TEMPLATES_DIR)

app = Flask(__name__, template_folder=TEMPLATES_DIR)

@app.get("/")
def root():
    return redirect(url_for("admin_home"))

@app.get("/admin")
def admin_home():
    return render_template("admin_home.html", now=datetime.now())

@app.get("/admin/questions")
def admin_questions():
    csv_path = os.path.join(BASE_DIR, "intents.csv")
    ok = bot.load_intents_from_csv(csv_path)

    items = bot.intents.get("intents", [])
    error = None if ok else f"Could not load CSV: {csv_path}"

    return render_template(
        "admin_questions.html",
        now=datetime.now(),
        items=items,
        error=error,
        csv_path=csv_path
    )

@app.get("/admin/logs")
def admin_logs():
    return render_template("admin_logs.html", now=datetime.now())

@app.get("/admin/users")
def admin_users():
    return render_template("admin_users.html", now=datetime.now())

@app.get("/admin/activity")
def admin_activity():
    return render_template("admin_activity.html", now=datetime.now())

def run_admin_web(host: str = "127.0.0.1", port: int = 5000) -> None:
    app.run(host=host, port=port, debug=False)

if __name__ == "__main__":
    run_admin_web()
