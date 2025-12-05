# whale_vault_server.py (PÉLDA)
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    # Itt kell lennie a HTML kódnak, ami a SkyAI Whale Dashboardot jeleníti meg.
    # Pl. ha van egy 'index.html' fájl a 'templates' mappában:
    # return render_template('index.html') 
    return "SKYAI WHALE VAULT (WEB 3.0) Fut!"

if __name__ == '__main__':
    # A megadott logból ez a futtatási mód látszik:
    print("--------------------------------------------------")
    print(" SKYAI WHALE VAULT (WEB 3.0) INDÍTÁSA...")
    print(" Nyisd meg a böngészőben: http://127.0.0.1:5000")
    print("--------------------------------------------------")
    app.run(host='127.0.0.1', port=5000, debug=False)
