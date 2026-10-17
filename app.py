from flask import Flask, render_template, request, redirect, abort
import sqlite3, os, datetime

app = Flask(__name__)
SECRET_KEY = 'bleu-av-2026-secret-key'
DB = 'bleuav.db'

def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("CREATE TABLE IF NOT EXISTS visites (id INTEGER PRIMARY KEY, ip TEXT, pays TEXT, date TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS downloads (id INTEGER PRIMARY KEY, ip TEXT, date TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY, titre TEXT, contenu TEXT, date TEXT)")
    conn.commit()
    conn.close()
init_db()

@app.route('/')
def index():
    conn = sqlite3.connect(DB)
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    pays = request.headers.get('Cf-Ipcountry', 'Togo')
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("INSERT INTO visites (ip, pays, date) VALUES (?, ?, ?)", (ip, pays, date))
    conn.commit()
    conn.close()
    return render_template('index.html')

@app.route('/download')
def download():
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
    visites = conn.execute("SELECT COUNT(*) FROM visites").fetchone()[0]
    downloads = conn.execute("SELECT COUNT(*) FROM downloads").fetchone()[0]
    conn.close()
    html = f"""
    <h1>BLEU-AV ADMIN - LÉGENDE</h1>
    <p>Visites: {visites} | Downloads: {downloads}</p>
    <form method='POST' action='/admin-bleu-av/add?key={SECRET_KEY}'>
    <input name='titre' placeholder='Titre' required><br>
    <textarea name='contenu' placeholder='Contenu' required></textarea><br>
    <button>Publier</button>
    </form><hr>
    """
    for p in posts:
        html += f"<div><b>{p[1]}</b> - {p[2]} <a href='/admin-bleu-av/delete/{p[0]}?key={SECRET_KEY}'>Supprimer</a></div><hr>"
    return html

@app.route('/admin-bleu-av/add', methods=['POST'])
def add_post():
    if request.args.get('key') != SECRET_KEY:
        abort(403)
    titre = request.form.get('titre')
    contenu = request.form.get('contenu')
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB)
    conn.execute("INSERT INTO posts (titre, contenu, date) VALUES (?, ?, ?)", (titre, contenu, date))
    conn.commit()
    conn.close()
    return redirect(f'/admin-bleu-av?key={SECRET_KEY}')

@app.route('/admin-bleu-av/delete/<int:id>')
def delete_post(id):
    if request.args.get('key') != SECRET_KEY:
        abort(403)
    conn = sqlite3.connect(DB)
    conn.execute("DELETE FROM posts WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(f'/admin-bleu-av?key={SECRET_KEY}')