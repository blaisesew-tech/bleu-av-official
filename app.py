# BLEU-AV V6 - TELECHARGEMENT DIRECT 2027
import os
from flask import Flask, render_template_string, request, send_file
import sqlite3
from datetime import datetime
import io

app = Flask(__name__)
ADMIN_PASS = "bleu2027"

def get_db():
    conn = sqlite3.connect('bleu.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('CREATE TABLE IF NOT EXISTS visits (id INTEGER PRIMARY KEY, ip TEXT, date TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS downloads (id INTEGER PRIMARY KEY, ip TEXT, date TEXT)')
    conn.commit()
    conn.close()
init_db()

def get_ip():
    # Corrige l'IP sur Render
    return request.headers.get('X-Forwarded-For', request.remote_addr)

HOME_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>BLEU-AV 2027</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{background:#000;color:#fff;text-align:center;font-family:Arial;padding:30px}
.btn{background:#0055ff;color:#fff;padding:22px 45px;font-size:22px;border:none;border-radius:15px;display:inline-block;text-decoration:none;margin:25px;font-weight:bold;box-shadow:0 0 25px #0055ff}
.sub{color:#888;margin-top:25px;font-size:14px}
</style>
</head>
<body>
<h1>🔵 BLEU-AV OFFICIEL 🔵</h1>
<p style="font-size:18px;color:#ccc;">Plate-forme de sécurisation</p>
<a class="btn" href="/download">TELECHARGER L'APK 🔥</a>
<p class="sub">Version 2027 | 100% Gratuit | Sécurisé & Privé</p>
</body>
</html>
"""

ADMIN_HTML = """
<body style="background:#111;color:#fff;font-family:Arial;padding:20px">
<h2>Admin BLEU-AV 2027</h2>
<p>Visites: {{v}} | Downloads: {{d}}</p>
<h3>Visites IP:</h3>
{% for r in visits %}<div>{{r['ip']}} - {{r['date']}}</div>{% endfor %}
<h3 style="margin-top:20px">Downloads IP:</h3>
{% for r in downloads %}<div>{{r['ip']}} - {{r['date']}}</div>{% endfor %}
</body>
"""

@app.route('/')
def home():
    conn = get_db()
    conn.execute("INSERT INTO visits (ip, date) VALUES (?, ?)", (get_ip(), datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return render_template_string(HOME_HTML)

@app.route('/download')
def download():
    conn = get_db()
    conn.execute("INSERT INTO downloads (ip, date) VALUES (?, ?)", (get_ip(), datetime.now().isoformat()))
    conn.commit()
    conn.close()
    # Crée un faux APK temporaire pour tester - tu le remplaceras après
    dummy = io.BytesIO(b"BLEU-AV APK 2027 - REMPLACE PAR VRAI APK")
    return send_file(dummy, as_attachment=True, download_name="Bleu-AV-2027.apk")

@app.route('/admin')
def admin():
    if request.args.get('pass') != ADMIN_PASS:
        return "Acces refuse"
    conn = get_db()
    v = conn.execute("SELECT COUNT(*) FROM visits").fetchone()[0]
    d = conn.execute("SELECT COUNT(*) FROM downloads").fetchone()[0]
    visits = conn.execute("SELECT * FROM visits ORDER BY id DESC LIMIT 100").fetchall()
    downloads = conn.execute("SELECT * FROM downloads ORDER BY id DESC LIMIT 100").fetchall()
    conn.close()
    return render_template_string(ADMIN_HTML, v=v, d=d, visits=visits, downloads=downloads)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))