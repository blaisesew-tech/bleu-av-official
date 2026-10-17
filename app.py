from flask import Flask, request, redirect, abort, jsonify
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
SECRET_KEY = "BLEU-AV-2026-LOME-SECRET"
DOWNLOAD_SEUIL_PAYANT = 100  # Gratuit jusqu'à 100 visiteurs

def init():
    conn = sqlite3.connect('bleuav.db')
    conn.execute("CREATE TABLE IF NOT EXISTS visites (id INTEGER PRIMARY KEY, ip TEXT, date TEXT, pays TEXT, nav TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS downloads (id INTEGER PRIMARY KEY, ip TEXT, date TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS commentaires (id INTEGER PRIMARY KEY, nom TEXT, message TEXT, date TEXT, ip TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY, titre TEXT, contenu TEXT, date TEXT)")
    # Post par défaut
    c = conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
    if c == 0:
        conn.execute("INSERT INTO posts (titre,contenu,date) VALUES (?,?,?)", 
        ("🔥 BLEU-AV OFFICIAL - Lancement Mondial Lomé", "L'antivirus le plus rapide d'Afrique est né à Lomé! Protection en 2 secondes, batterie économisée, 100% gratuit pour les premiers utilisateurs. Télécharge maintenant!", datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit(); conn.close()
init()

def get_stats():
    conn = sqlite3.connect('bleuav.db')
    total = conn.execute("SELECT COUNT(*) FROM visites").fetchone()[0]
    today = datetime.now().strftime("%Y-%m-%d")
    today_c = conn.execute("SELECT COUNT(*) FROM visites WHERE date LIKE ?", (f"{today}%",)).fetchone()[0]
    dl_total = conn.execute("SELECT COUNT(*) FROM downloads").fetchone()[0]
    dl_today = conn.execute("SELECT COUNT(*) FROM downloads WHERE date LIKE ?", (f"{today}%",)).fetchone()[0]
    conn.close()
    return total, today_c, dl_total, dl_today

@app.route('/')
def home():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0]
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nav = request.headers.get('User-Agent','')[:70]
    pays = request.headers.get('Cf-Ipcountry', 'TG')
    
    conn = sqlite3.connect('bleuav.db')
    conn.execute("INSERT INTO visites (ip,date,pays,nav) VALUES (?,?,?,?)", (ip,date,pays,nav))
    conn.commit()
    
    posts = conn.execute("SELECT titre,contenu,date FROM posts ORDER BY id DESC").fetchall()
    comms = conn.execute("SELECT nom,message,date FROM commentaires ORDER BY id DESC LIMIT 20").fetchall()
    conn.close()
    
    total, today_c, dl_total, dl_today = get_stats()
    gratuit = total < DOWNLOAD_SEUIL_PAYANT
    
    posts_html = "".join([f"<div style='background:#0a2a4a;padding:15px;border-radius:10px;margin:10px 0'><h3>{p[0]}</h3><p>{p[1]}</p><small>{p[2]}</small></div>" for p in posts])
    comms_html = "".join([f"<div style='background:#111;padding:10px;margin:5px 0;border-left:3px solid #00ccff'><b>{c[0]}</b>: {c[1]} <br><small style='color:#666'>{c[2]}</small></div>" for c in comms])
    
    btn = f"<a href='/download' style='background:lime;color:black;padding:18px 40px;text-decoration:none;border-radius:12px;font-weight:bold;font-size:18px;display:inline-block'>⬇️ TÉLÉCHARGER GRATUIT</a>" if gratuit else f"<div style='background:gold;color:black;padding:18px;border-radius:12px'><h3>🔒 {DOWNLOAD_SEUIL_PAYANT} téléchargements atteints!</h3><p>Paiement activé: 2$ / 2€ / 1200 FCFA</p><a href='/pay' style='background:black;color:gold;padding:12px 25px;text-decoration:none;border-radius:8px'>PAYER ET TÉLÉCHARGER</a></div>"

    return f"""
    <html><head><meta name='viewport' content='width=device-width, initial-scale=1'><title>BLEU-AV Official - Antivirus Afrique</title></head>
    <body style='background:#001a33;color:white;font-family:sans-serif;padding:15px;max-width:800px;margin:auto'>
    <div style='text-align:center;padding:20px'>
    <h1 style='color:#00ccff'>💙 BLEU-AV OFFICIAL</h1>
    <p style='color:yellow'>L'Antivirus Officiel Créé à Lomé - Mondial</p>
    {btn}
    </div>
    <h2>📢 Actualités Officielles</h2>
    {posts_html}
    <h2>💬 Avis des Utilisateurs ({len(comms)})</h2>
    <form action='/comment' method='post' style='background:#002244;padding:15px;border-radius:10px'>
    <input name='nom' placeholder='Ton nom' required style='width:100%;padding:10px;margin:5px 0'>
    <textarea name='message' placeholder='Ton avis sur BLEU-AV...' required style='width:100%;padding:10px;margin:5px 0'></textarea>
    <button style='background:#00ccff;padding:10px 20px;border:none;border-radius:5px'>Envoyer avis</button>
    </form>
    {comms_html}
    <p style='text-align:center;color:#555;margin-top:30px'>© BLEU-AV Lomé Togo | {total} visiteurs mondiaux</p>
    </body></html>
    """

@app.route('/download')
def download():
    total,_,_,_ = get_stats()
    if total >= DOWNLOAD_SEUIL_PAYANT:
        return redirect('/pay')
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0]
    conn = sqlite3.connect('bleuav.db')
    conn.execute("INSERT INTO downloads (ip,date) VALUES (?,?)", (ip, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit(); conn.close()
    return """
    <html style='background:#001a33;color:white;text-align:center;padding:40px;font-family:sans-serif'>
    <h1 style='color:lime'>✅ Téléchargement Lancé!</h1>
    <p>Ton BLEU-AV arrive...</p>
    <p style='color:#888'>Merci de Lomé!</p>
    <a href='/' style='color:#00ccff'>Retour</a>
    </html>
    """

@app.route('/comment', methods=['POST'])
def comment():
    nom = request.form.get('nom','Anonyme')[:20]
    msg = request.form.get('message','')[:200]
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0]
    conn = sqlite3.connect('bleuav.db')
    conn.execute("INSERT INTO commentaires (nom,message,date,ip) VALUES (?,?,?,?)", (nom,msg,datetime.now().strftime("%Y-%m-%d %H:%M"),ip))
    conn.commit(); conn.close()
    return redirect('/')

@app.route('/pay')
def pay():
    return """
    <html style='background:#001a33;color:white;text-align:center;padding:30px;font-family:sans-serif'>
    <h1>💳 Paiement BLEU-AV</h1>
    <p>Mode gratuit terminé après 100 utilisateurs!</p>
    <p>Choisis ta monnaie:</p>
    <div style='display:flex;flex-direction:column;gap:10px;max-width:300px;margin:auto'>
    <button style='padding:15px;background:gold'>2$ USD - PayPal</button>
    <button style='padding:15px;background:#00ccff'>2€ EUR - Carte</button>
    <button style='padding:15px;background:lime'>1200 FCFA - Mobile Money (Togo/Benin/Ghana)</button>
    </div>
    <p style='color:yellow;margin-top:20px'>Paiement réel à activer après 100 visiteurs</p>
    <a href='/' style='color:white'>Retour</a>
    </html>
    """

@app.route('/admin-bleu-av')
def admin():
    if request.args.get('key') != SECRET_KEY:
        abort(404)
    total, today_c, dl_total, dl_today = get_stats()
    conn = sqlite3.connect('bleuav.db')
    visites = conn.execute("SELECT date,ip,pays FROM visites ORDER BY id DESC LIMIT 100").fetchall()
    comms = conn.execute("SELECT date,nom,message,ip FROM commentaires ORDER BY id DESC LIMIT 50").fetchall()
    conn.close()
    
    vis_html = "<br>".join([f"{v[0]} | {v[1]} | {v[2]}" for v in visites])
    comm_html = "<br>".join([f"{c[0]} | {c[1]}: {c[2]} | {c[3]}" for c in comms])
    
    return f"""
    <html><body style='font-family:monospace;padding:20px;background:#000;color:#0f0'>
    <h1>🔒 DASHBOARD SECRET - BLEU-AV (Toi seul)</h1>
    <h2>VISITEURS: Total {total} | Aujourd'hui {today_c}</h2>
    <h2>TELECHARGEMENTS: Total {dl_total} | Aujourd'hui {dl_today}</h2>
    <p>Seuil payant: {DOWNLOAD_SEUIL_PAYANT} visiteurs | Mode actuel: {'GRATUIT' if total < DOWNLOAD_SEUIL_PAYANT else 'PAYANT'}</p>
    <hr><h3>Poster une actu:</h3>
    <form action='/admin-bleu-av/post?key={SECRET_KEY}' method='post'>
    <input name='titre' placeholder='Titre' style='width:100%;padding:8px'><br>
    <textarea name='contenu' placeholder='Contenu...' style='width:100%;padding:8px'></textarea><br>
    <button>Poster</button></form>
    <hr><h3>Dernières visites (100):</h3>{vis_html}
    <hr><h3>Commentaires (50):</h3>{comm_html}
    </body></html>
    """

@app.route('/admin-bleu-av/post', methods=['POST'])
def admin_post():
    if request.args.get('key') != SECRET_KEY: abort(404)
    titre = request.form.get('titre','')[:100]
    contenu = request.form.get('contenu','')[:500]
    if titre:
        conn = sqlite3.connect('bleuav.db')
        conn.execute("INSERT INTO posts (titre,contenu,date) VALUES (?,?,?)", (titre,contenu,datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit(); conn.close()
    return redirect(f'/admin-bleu-av?key={SECRET_KEY}')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT",5000)))
