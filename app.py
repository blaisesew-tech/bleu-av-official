from flask import Flask, request, redirect, abort
import sqlite3, datetime, os

app = Flask(__name__)
SECRET_KEY = 'bleu-av-2026-secret-key'
DB = 'bleuav.db'

def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("CREATE TABLE IF NOT EXISTS visites (id INTEGER PRIMARY KEY, ip TEXT, pays TEXT, ville TEXT, date TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS downloads (id INTEGER PRIMARY KEY, ip TEXT, pays TEXT, ville TEXT, date TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY, titre TEXT, contenu TEXT, date TEXT)")
    conn.commit()
    conn.close()
init_db()

def get_info():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr) or 'inconnu'
    ip = ip.split(',')[0].strip()
    pays = request.headers.get('CF-IPCountry', request.headers.get('X-Country', 'TG'))
    ville = request.headers.get('CF-IPCity', 'Lome')
    # Si Render ne donne pas pays, on met Togo par défaut
    if not pays or pays == 'XX':
        pays = 'TG (Togo?)'
    return ip, pays, ville

@app.route('/')
def index():
    conn = sqlite3.connect(DB)
    ip, pays, ville = get_info()
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("INSERT INTO visites (ip, pays, ville, date) VALUES (?, ?, ?, ?)", (ip, pays, ville, date))
    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM visites").fetchone()[0]
    dcount = conn.execute("SELECT COUNT(*) FROM downloads").fetchone()[0]
    posts = conn.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
    conn.close()
    html = f"""
    <html><head><title>BLEU-AV OFFICIAL</title><meta name='viewport' content='width=device-width'>
    <style>body{{font-family:Arial;background:#000e2a;color:white;text-align:center;padding:15px}}
    .box{{background:white;color:black;padding:15px;border-radius:12px;margin:10px auto;max-width:600px}}
    a.btn{{background:#0066ff;color:white;padding:12px 25px;border-radius:8px;text-decoration:none;display:inline-block;font-weight:bold}}
    </style></head><body>
    <h1>🔥 BLEU-AV OFFICIAL 🔥</h1>
    <p>Site de la LÉGENDE - L'antivirus le plus rapide d'Afrique</p>
    <p>👁️ {count} Visites | 📥 {dcount} Téléchargements</p>
    <div class='box'><a class='btn' href='/download'>📥 TELECHARGER L'APPLI</a></div>
    <h2>📰 ACTUS</h2>
    """
    for p in posts:
        html += f"<div class='box'><b>{p[1]}</b><br><br>{p[2]}<br><small>{p[3]}</small></div>"
    if not posts:
        html += "<div class='box'>Aucun post encore</div>"
    html += "<p style='margin-top:30px;font-size:12px'>© 2026 BLEU-AV</p></body></html>"
    return html

@app.route('/download')
def download():
    conn = sqlite3.connect(DB)
    ip, pays, ville = get_info()
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("INSERT INTO downloads (ip, pays, ville, date) VALUES (?, ?, ?, ?)", (ip, pays, ville, date))
    conn.commit()
    conn.close()
    # ICI MET TON LIEN APK PLUS TARD
    return redirect('/')

@app.route('/admin-bleu-av')
def admin():
    if request.args.get('key') != SECRET_KEY:
        abort(403)
    conn = sqlite3.connect(DB)
    posts = conn.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
    visites = conn.execute("SELECT * FROM visites ORDER BY id DESC LIMIT 100").fetchall()
    downloads = conn.execute("SELECT * FROM downloads ORDER BY id DESC LIMIT 100").fetchall()
    vcount = conn.execute("SELECT COUNT(*) FROM visites").fetchone()[0]
    dcount = conn.execute("SELECT COUNT(*) FROM downloads").fetchone()[0]
    conn.close()
    
    html = f"""
    <html><head><meta name='viewport' content='width=device-width'><title>ADMIN BLEU-AV</title></head>
    <body style='font-family:Arial;padding:15px;background:#f5f5f5'>
    <h1>🔒 BLEU-AV ADMIN - LÉGENDE</h1>
    <div style='display:flex;gap:10px'>
    <div style='background:#0066ff;color:white;padding:15px;border-radius:10px;flex:1;text-align:center'><h2>{vcount}</h2>VISITES</div>
    <div style='background:#00aa44;color:white;padding:15px;border-radius:10px;flex:1;text-align:center'><h2>{dcount}</h2>DOWNLOADS</div>
    </div>
    
    <h3>➕ Ajouter Post</h3>
    <form method='POST' action='/admin-bleu-av/add?key={SECRET_KEY}' style='background:white;padding:15px;border-radius:10px'>
    <input name='titre' placeholder='Titre' required style='width:100%;padding:10px'><br><br>
    <textarea name='contenu' placeholder='Contenu actualité...' required style='width:100%;height:80px;padding:10px'></textarea><br><br>
    <button style='background:blue;color:white;padding:10px 20px;border:none;border-radius:5px'>Publier</button>
    </form>

    <h3>📥 Derniers Téléchargements ({dcount})</h3>
    <div style='background:white;padding:10px;border-radius:10px;max-height:200px;overflow:auto'>
    <table border=1 style='width:100%;border-collapse:collapse;font-size:12px'><tr><th>IP</th><th>Pays</th><th>Date</th></tr>
    """
    for d in downloads:
        html += f"<tr><td>{d[1]}</td><td>{d[2]} / {d[3]}</td><td>{d[4]}</td></tr>"
    html += "</table></div>"

    html += f"""
    <h3>👁️ Dernières Visites ({vcount})</h3>
    <div style='background:white;padding:10px;border-radius:10px;max-height:200px;overflow:auto'>
    <table border=1 style='width:100%;border-collapse:collapse;font-size:12px'><tr><th>IP</th><th>Pays</th><th>Date</th></tr>
    """
    for v in visites:
        html += f"<tr><td>{v[1]}</td><td>{v[2]} / {v[3]}</td><td>{v[4]}</td></tr>"
    html += "</table></div>"

    html += "<h3>📰 Posts</h3>"
    for p in posts:
        html += f"<div style='background:white;padding:10px;margin:5px;border-radius:5px'><b>{p[1]}</b> - {p[2][:100]} <a href='/admin-bleu-av/delete/{p[0]}?key={SECRET_KEY}' style='color:red;float:right'>Supprimer</a><br><small>{p[3]}</small></div>"
    
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