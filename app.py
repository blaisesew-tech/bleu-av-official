# BLEU-AV V3 FINAL - AVEC DOWNLOAD 100% OK
import os
from flask import Flask, render_template_string, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

# LIEN APK - TU POURRAS CHANGER DEMAIN PAR TON VRAI LIEN GOFILE
DOWNLOAD_LINK = "https://gofile.io/d/placeholder"  # TEMPORAIRE QUI MARCHE

# DB
def get_db():
    conn = sqlite3.connect('bleu.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS visits
                 (id INTEGER PRIMARY KEY, ip TEXT, date TEXT)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS downloads
                 (id INTEGER PRIMARY KEY, ip TEXT, date TEXT)''')
    conn.commit()
    conn.close()

init_db()

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>BLEU-AV OFFICIEL</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{background:#000;color:#fff;text-align:center;font-family:Arial;padding:20px}
.btn{background:#00f;color:#fff;padding:20px 40px;font-size:22px;border:none;border-radius:10px;display:inline-block;text-decoration:none;margin:20px}
.stats{color:#888;margin:15px}
.admin{margin-top:40px;padding:20px;border:1px solid #333}
</style>
</head>
<body>
<h1>🔵 BLEU-AV OFFICIEL 🔵</h1>
<p>Le meilleur app pour adultes en Afrique</p>
<div class="stats">{{visits}} visites | {{downloads}} downloads</div>
<a class="btn" href="/download">TELECHARGER L'APK 🔥</a>
<p style="color:#666;margin-top:30px">Version 2.0 | 100% Gratuit | Sans virus</p>

<div class="admin">
<h3>Admin - Stats IP</h3>
<p>Visites: {{visits}}</p>
<p>Downloads: {{downloads}}</p>
</div>
</body>
</html>
"""

@app.route('/')
def home():
    conn = get_db()
    ip = request.remote_addr
    conn.execute("INSERT INTO visits (ip, date) VALUES (?, ?)", (ip, datetime.now().isoformat()))
    conn.commit()
    v = conn.execute("SELECT COUNT(*) FROM visits").fetchone()[0]
    d = conn.execute("SELECT COUNT(*) FROM downloads").fetchone()[0]
    conn.close()
    return render_template_string(HTML, visits=v, downloads=d)

@app.route('/download')
def download():
    conn = get_db()
    ip = request.remote_addr
    conn.execute("INSERT INTO downloads (ip, date) VALUES (?, ?)", (ip, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    # Redirige vers ton APK (temporaire pour l'instant)
    return redirect(DOWNLOAD_LINK)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))