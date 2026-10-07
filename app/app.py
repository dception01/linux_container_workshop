import os
import socket
from pathlib import Path
import psycopg
from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__, template_folder=str(Path(__file__).parent / "templates"))
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
INSTANCE = os.getenv("INSTANCE_NAME", socket.gethostname())
TEAM = os.getenv("TEAM_NAME", "Campus Builders")

def connect():
    return psycopg.connect(host=os.getenv("DB_HOST", "db"),
        dbname=os.getenv("POSTGRES_DB", "campus"),
        user=os.getenv("POSTGRES_USER", "campus"),
        password=os.getenv("POSTGRES_PASSWORD", ""), connect_timeout=3)

@app.after_request
def no_cache(response):
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Served-By"] = INSTANCE
    return response

@app.get("/healthz")
def health():
    return jsonify(status="ok", instance=INSTANCE)

@app.get("/readyz")
def ready():
    try:
        with connect() as conn:
            conn.execute("SELECT 1 FROM feedback LIMIT 1")
        return jsonify(status="ready", instance=INSTANCE)
    except psycopg.Error:
        return jsonify(status="database unavailable", instance=INSTANCE), 503

@app.get("/")
def index():
    rows, total, average, connected = [], 0, 0, True
    try:
        with connect() as conn:
            rows = conn.execute("SELECT team, rating, comment, created_at FROM feedback ORDER BY id DESC LIMIT 30").fetchall()
            total, average = conn.execute("SELECT count(*), coalesce(round(avg(rating), 1), 0) FROM feedback").fetchone()
    except psycopg.Error:
        connected = False
    return render_template("index.html", rows=rows, total=total, average=average,
        connected=connected, instance=INSTANCE, team=TEAM)

@app.post("/feedback")
def feedback():
    team = request.form.get("team", "").strip()
    comment = request.form.get("comment", "").strip()
    try:
        rating = int(request.form.get("rating", ""))
    except ValueError:
        return "Rating must be an integer from 1 to 5.", 400
    if not 1 <= len(team) <= 60 or not 1 <= len(comment) <= 500 or not 1 <= rating <= 5:
        return "Provide a team (1–60 characters), comment (1–500), and rating (1–5).", 400
    try:
        with connect() as conn:
            conn.execute("INSERT INTO feedback (team, rating, comment) VALUES (%s, %s, %s)", (team, rating, comment))
    except psycopg.Error:
        return "Database unavailable. Check the database container and configuration, then try again.", 503
    return redirect(url_for("index"), code=303)
