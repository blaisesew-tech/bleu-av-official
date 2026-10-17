# BLEU-AV V7 - ADMIN BEAU 2027
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
    return request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()

HOME_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>BLEU-AV 2027</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{background:#000;color:#fff;text-align:center;font-family:Arial;padding:30px}
.btn{background:#0055ff;color:#fff;padding:22px 45px;font-size:22px;border-radius:15px;display:inline-block;text-decoration:none;margin:25px;font-weight:bold;box-shadow:0 0 25px #0055ff}
.sub{color:#888;margin-top:25px}
</style>
</head>
<body>
<h1>🔵 BLEU-AV OFFICIEL 🔵</h1>
<p>Plate-forme de sécurisation</p>
<a class="btn" href="/download">TELECHARGER L'APK 🔥</a>
<p class="sub">Version 2027 | 100% Gratuit</p>
</body>
</html>
"""

ADMIN_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{background:#0a0a0a;color:#fff;font-family:Arial;padding:15px}
.card{background:#1a1a1a;padding:15px;border-radius:12px;margin:10px 0;border:1px solid #333}
h2{color:#0055ff}
.badge{background:#0055ff;padding:5px 12px;border-radius:20px;font-weight:bold}
.ip{font-size:12px;color:#0f0;background:#000;padding:5px;margin:3px 0;border-radius:5px;word-break:break-all}
</style>
</head>
<body>
<h2>🔵 Admin BLEU-AV 2027</h2>
<div class="card">
Visites: <span class="badge">{{v}}</span> | Downloads: <span class="badge">{{d}}</span>
</div>

<div class="card">
<h3>👁️ Visites (8 dernières)</h3>
{% for r in visits %}<div class="ip">{{r['ip']}}<br><small>{{r['date'][:19]}}</small></div>{% endfor %}
</div>

<div class="card">
<h3>📥 Downloads (8 dernières)</h3>
{% for r in downloads %}<div class="ip" style="color:#ff0">{{r['ip']}}<br><small>{{r['date'][:19]}}</small></div>{% endfor %}
</div>
</body>
</html>
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
    dummy = io.BytesIO(b"BLEU-AV APK 2027 - REMPLACE PAR VRAI APK")
    return send_file(dummy, as_attachment=True, download_name="Bleu-AV-2027.apk")

@app.route('/admin')
def admin():
    if request.args.get('pass') != ADMIN_PASS:
        return "<h1 style='color:red;text-align:center;margin-top:50px'>Acces Refuse<br><small>Ajoute ?pass=bleu2027</small></h1>"
    conn = get_db()
    v = conn.execute("SELECT COUNT(*) FROM visits").fetchone()[0]
    d = conn.execute("SELECT COUNT(*) FROM downloads").fetchone()[0]
    visits = conn.execute("SELECT * FROM visits ORDER BY id DESC LIMIT 20").fetchall()
    downloads = conn.execute("SELECT * FROM downloads ORDER BY id DESC LIMIT 20").fetchall()
    conn.close()
    return render_template_string(ADMIN_HTML, v=v, d=d, visits=visits, downloads=downloads)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))