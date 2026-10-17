from flask import Flask, render_template, request, redirect, abort
import sqlite3
import os
app = Flask(__name__)
SECRET_KEY = "bleu-av-2026-secret-key"
DOWNLOAD_SEUIL_PAYANT = 100
DB = 'bleuav.db'
def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("CREATE TABLE IF NOT EXISTS visites (id INTEGER PRIMARY KEY, ip TEXT, date TEXT, pays TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS downloads (id INTEGER PRIMARY KEY, ip TEXT, date TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY, titre TEXT, contenu TEXT, date TEXT)")
    conn.commit()
    conn.close()
init_db()
@app.route('/')
def index():
    import datetime
    conn = sqlite3.connect(DB)
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    pays = request.headers.get('Cf-Ipcountry', 'Togo')
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("INSERT INTO visites (ip, date, pays) VALUES (?, ?, ?)", (ip, date, pays))
    conn.commit()
    conn.close()
    return render_template('index.html')
@app.route('/download')
def download():
    import datetime
    conn = sqlite3.connect(DB)
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("INSERT INTO downloads (ip, date) VALUES (?, ?)", (ip, date))
    conn.commit()
    conn.close()
    return redirect('/')
@app.route('/admin-bleu-av')
def admin():
    if request.args.get('key') != SECRET_KEY:
        abort(403)
    conn = sqlite3.connect(DB)
    posts = conn.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
    conn.close()
    return f"<html><body style='background:#0a192f;color:white;padding:20px'><h1>Admin</h1><form action='/admin-bleu-av/post?key={SECRET_KEY}' method='POST'><input name='titre' placeholder='Titre' style='width:100%;padding:10px'><br><br><textarea name='contenu' placeholder='Contenu' style='width:100%;height:100px'></textarea><br><br><button>Publier</button></form><hr><pre>{posts}</pre></body></html>"
@app.route('/admin-bleu-av/post', methods=['POST'])
def admin_post():
    if request.args.get('key') != SECRET_KEY:
        abort(403)
    titre = request.form.get('titre', '')[:100]
    contenu = request.form.get('contenu', '')[:500]
    if titre:
        conn = sqlite3.connect(DB)
        conn.execute("INSERT INTO posts (titre, contenu) VALUES (?, ?)", (titre, contenu))
        conn.commit()
        conn.close()
    return redirect(f'/admin-bleu-av?key={SECRET_KEY}')
@app.route('/admin-secret-blaise-2026')
def admin_secret():
    conn = sqlite3.connect(DB)
    total_v = conn.execute("SELECT COUNT(*) FROM visites").fetchone()[0]
    total_d = conn.execute("SELECT COUNT(*) FROM downloads").fetchone()[0]
    visites = conn.execute("SELECT * FROM visites ORDER BY id DESC LIMIT 30").fetchall()
    dls = conn.execute("SELECT * FROM downloads ORDER BY id DESC LIMIT 30").fetchall()
    conn.close()
    return f"<html><body style='background:#0a192f;color:white;padding:20px;font-family:Arial'><h1>🔐 D
