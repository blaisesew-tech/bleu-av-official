from flask import Flask, request, redirect, abort
import sqlite3, datetime, os

app = Flask(__name__)
SECRET_KEY = 'bleu-av-2026-secret-key'
DB = 'bleuav.db'

# SUPPRIME L'ANCIENNE BASE SI ELLE A UN BUG
if os.path.exists(DB):
    try:
        conn = sqlite3.connect(DB)
        conn.execute("SELECT ville FROM visites LIMIT 1")
        conn.close()
    except:
        os.remove(DB)

def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("CREATE TABLE IF NOT EXISTS visites (id INTEGER PRIMARY KEY, ip TEXT, pays TEXT, date TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS downloads (id INTEGER PRIMARY KEY, ip TEXT, pays TEXT, date TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY, titre TEXT, contenu TEXT, date TEXT)")
    conn.commit()
    conn.close()
init_db()

@app.route('/')
def index():
    try:
        conn = sqlite3.connect(DB)
        ip = request.headers.get('X-Forwarded-For', request.remote_addr) or 'inconnu'
        ip = ip.split(',')[0][:20]
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute("INSERT INTO visites (ip, pays, date) VALUES (?, ?, ?)", (ip, 'TG', date))
        conn.commit()
        count = conn.execute("SELECT COUNT(*) FROM visites").fetchone()[0]
        dcount = conn.execute("SELECT COUNT(*) FROM downloads").fetchone()[0]
        posts = conn.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
        conn.close()
    except Exception as e:
        return f"Init en cours... recharge dans 5 sec: {e}<script>setTimeout(()=>location.reload(),2000)</script>"
    
    html = f"""
    <html><head><title>BLEU-AV</title><meta name='viewport' content='width=device-width'>
    <style>body{{font-family:Arial;background:#000e2a;color:white;text-align:center;padding:15px}}
    .box{{background:white;color:black;padding:15px;border-radius:12px;margin:10px auto;max-width:600px}}
    a.btn{{background:#0066ff;color:white;padding:12px 25px;border-radius:8px;text-decoration:none;display:inline-block;font-weight:bold}}
    </style></head><body>
    <h1>🔥 BLEU-AV OFFICIAL 🔥</h1>
    <p>{count} visites | {dcount} downloads</p>
    <div class='box'><a class='btn' href='/download'>📥 TELECHARGER</a></div>
    <h2>ACTUS</h2>
    """
    for p in posts:
        html += f"<div class='box'><b>{p[1]}</b><br>{p[2]}<br><small>{p[3]}</small></div>"
    return html+"</body></html>"

@app.route('/download')
def download():
    conn = sqlite3.connect(DB)
    ip = request.headers.get('X-Forwarded-For', request.remote_addr) or 'inconnu'
    ip = ip.split(',')[0][:20]
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("INSERT INTO downloads (ip, pays, date) VALUES (?, ?, ?)", (ip, 'TG', date))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/admin-bleu-av')
def admin():
    if request.args.get('key') != SECRET_KEY:
        abort(403)
    conn = sqlite3.connect(DB)
    posts = conn.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
    visites = conn.execute("SELECT * FROM visites ORDER BY id DESC LIMIT 50").fetchall()
    downloads = conn.execute("SELECT * FROM downloads ORDER BY id DESC LIMIT 50").fetchall()
    vcount = conn.execute("SELECT COUNT(*) FROM visites").fetchone()[0]
    dcount = conn.execute("SELECT COUNT(*) FROM downloads").fetchone()[0]
    conn.close()
    html = f"""
    <html><body style='font-family:Arial;padding:15px'>
    <h1>🔒 ADMIN - {vcount} visites / {dcount} downloads</h1>
    <form method='POST' action='/admin-bleu-av/add?key={SECRET_KEY}' style='background:#eee;padding:10px'>
    <input name='titre' placeholder='Titre' required style='width:100%'><br><br>
    <textarea name='contenu' placeholder='Contenu' required style='width:100%'></textarea><br><br>
    <button>Publier</button></form>
    <h3>Downloads</h3>
    """
    for d in downloads:
        html += f"{d[1]} | {d[2]} | {d[3]}<br>"
    html += "<h3>Visites</h3>"
    for v in visites:
        html += f"{v[1]} | {v[2]} | {v[3]}<br>"
    html += "<h3>Posts</h3>"
    for p in posts:
        html += f"<b>{p[1]}</b> <a href='/admin-bleu-av/delete/{p[0]}?key={SECRET_KEY}'>Suppr</a><br>"
    return html

@app.route('/admin-bleu-av/add', methods=['POST'])
def add_post():
    if request.args.get('key') != SECRET_KEY:
        abort(403)
    conn = sqlite3.connect(DB)
    conn.execute("INSERT INTO posts (titre, contenu, date) VALUES (?, ?, ?)", (request.form.get('titre'), request.form.get('contenu'), datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
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