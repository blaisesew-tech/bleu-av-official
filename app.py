from flask import Flask, request, redirect, abort
import sqlite3, datetime, os

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
    ip = request.headers.get('X-Forwarded-For', request.remote_addr) or 'inconnu'
    pays = request.headers.get('Cf-Ipcountry', 'Togo')
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("INSERT INTO visites (ip, pays, date) VALUES (?, ?, ?)", (ip, pays, date))
    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM visites").fetchone()[0]
    posts = conn.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
    conn.close()
    html = f"""
    <html><head><title>BLEU-AV OFFICIAL</title>
    <style>body{{font-family:Arial;background:#001122;color:white;text-align:center;padding:20px}}
    .box{{background:white;color:black;padding:20px;border-radius:10px;margin:10px}}
    a{{background:blue;color:white;padding:10px 20px;border-radius:5px;text-decoration:none}}
    </style></head><body>
    <h1>🔥 BLEU-AV OFFICIAL 🔥</h1>
    <p>Site de la LÉGENDE</p>
    <p>Visites: {count}</p>
    <div class='box'><a href='/download'>TELECHARGER L'APPLI</a></div>
    <h2>ACTUS</h2>
    """
    for p in posts:
        html += f"<div class='box'><b>{p[1]}</b><br>{p[2]}<br><small>{p[3]}</small></div>"
    html += "</body></html>"
    return html

@app.route('/download')
def download():
    conn = sqlite3.connect(DB)
    ip = request.headers.get('X-Forwarded-For', request.remote_addr) or 'inconnu'
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
    <html><body style='font-family:Arial;padding:20px'>
    <h1>BLEU-AV ADMIN - LÉGENDE</h1>
    <p><b>Visites:</b> {visites} | <b>Downloads:</b> {downloads}</p>
    <form method='POST' action='/admin-bleu-av/add?key={SECRET_KEY}' style='background:#eee;padding:15px'>
    <input name='titre' placeholder='Titre du post' required style='width:100%;padding:8px'><br><br>
    <textarea name='contenu' placeholder='Contenu' required style='width:100%;height:100px'></textarea><br><br>
    <button style='background:blue;color:white;padding:10px'>Publier</button>
    </form><hr>
    """
    for p in posts:
        html += f"<div><b>{p[1]}</b> - {p[2]} <a href='/admin-bleu-av/delete/{p[0]}?key={SECRET_KEY}' style='color:red'>[Supprimer]</a></div><hr>"
    html += "</body></html>"
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

if __name__ == '__main__':
    app.run()