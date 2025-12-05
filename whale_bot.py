from flask import Flask, render_template_string, jsonify, request
import logging

# A Flask logjainak elrejtése, hogy tisztább legyen a terminál
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

# --- HTML FELÜLET (TRUST WALLET TÁMOGATÁSSAL) ---
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SkyAI Private Vault | Institutional Access</title>
    <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@300;500;700&family=Cinzel:wght@500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <script src="https://cdn.jsdelivr.net/npm/web3@1.5.2/dist/web3.min.js"></script>

    <style>
        :root {
            --bg: #050507;
            --purple: #bc13fe;
            --gold: #d4af37;
            --text: #ffffff;
        }
        body {
            background-color: var(--bg);
            color: var(--text);
            font-family: 'Manrope', sans-serif;
            margin: 0; padding: 0;
            display: flex; flex-direction: column;
            min-height: 100vh;
        }
        nav {
            padding: 20px 40px;
            display: flex; justify-content: space-between; align-items: center;
            border-bottom: 1px solid rgba(188, 19, 254, 0.3);
            background: rgba(5,5,7,0.9);
        }
        .brand {
            font-family: 'Cinzel', serif; font-size: 1.5rem;
            color: #fff;
        }
        .brand span { color: var(--purple); text-shadow: 0 0 10px var(--purple); }
        
        .connect-btn {
            background: transparent;
            border: 1px solid var(--purple);
            color: var(--purple);
            padding: 10px 25px;
            font-weight: 700;
            cursor: pointer;
            transition: 0.3s;
            text-transform: uppercase;
        }
        .connect-btn:hover {
            background: var(--purple);
            color: #fff;
            box-shadow: 0 0 20px var(--purple);
        }

        .main-content {
            flex: 1;
            display: flex; justify-content: center; align-items: center;
            text-align: center;
        }
        .status-box {
            padding: 40px;
            border: 1px solid #333;
            border-radius: 10px;
            max-width: 500px;
        }
        .hidden { display: none; }
    </style>
</head>
<body>

    <nav>
        <div class="brand"><i class="fa-solid fa-shield-halved"></i> SkyAI <span>VAULT</span></div>
        <button id="walletBtn" class="connect-btn" onclick="connectWallet()">
            <i class="fa-solid fa-wallet"></i> Connect Wallet
        </button>
    </nav>

    <div class="main-content">
        <div class="status-box">
            <h2 id="statusTitle">Rendszer Zárolva</h2>
            <p id="statusText">Kérlek, csatlakoztasd a hitelesített (Trust/Phantom/Metamask) tárcádat a belépéshez.</p>
            <div id="loader" class="hidden" style="margin-top:20px; color:var(--purple);">
                <i class="fa-solid fa-circle-notch fa-spin fa-2x"></i>
                <p>Hitelesítés folyamatban...</p>
            </div>
        </div>
    </div>

    <script>
        async function connectWallet() {
            const btn = document.getElementById('walletBtn');
            const statusTitle = document.getElementById('statusTitle');
            const statusText = document.getElementById('statusText');
            const loader = document.getElementById('loader');

            // 1. Ellenőrizzük, van-e tárca a böngészőben (Trust Wallet Extension / Phantom / Metamask)
            if (window.ethereum) {
                window.web3 = new Web3(window.ethereum);
                
                try {
                    // Betöltés jelzése
                    btn.innerHTML = "Csatlakozás...";
                    loader.classList.remove('hidden');

                    // 2. Kérjük a felhasználó engedélyét (Popup ablak)
                    const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
                    const account = accounts[0];

                    // 3. Ha sikerült, elküldjük a címet a Python Backendnek
                    sendToBackend(account);

                    // UI Frissítés
                    btn.innerHTML = "Connected: " + account.substring(0,6) + "...";
                    btn.style.borderColor = "#00ff9d";
                    btn.style.color = "#00ff9d";
                    
                    statusTitle.innerText = "Hozzáférés Engedélyezve";
                    statusTitle.style.color = "#00ff9d";
                    statusText.innerText = "Üdvözöllek, Intézményi Partner. A terminálon megkaptad a biztonsági kulcsot.";
                    loader.classList.add('hidden');

                } catch (error) {
                    console.error("User denied account access");
                    btn.innerHTML = "Hiba! Próbáld újra";
                    loader.classList.add('hidden');
                }
            } else {
                alert("Nem találtam tárcát! Kérlek telepítsd a Trust Wallet vagy Phantom bővítményt a böngésződhöz.");
            }
        }

        function sendToBackend(address) {
            fetch('/connect_success', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ wallet: address })
            })
            .then(response => response.json())
            .then(data => {
                console.log("Backend válasz:", data);
            });
        }
    </script>
</body>
</html>
"""

# --- BACKEND LOGIKA ---

@app.route('/')
def home():
    return render_template_string(HTML_INTERFACE)

@app.route('/connect_success', methods=['POST'])
def connect_success():
    data = request.json
    wallet_address = data.get('wallet', 'Ismeretlen')
    
    # ITT TÖRTÉNIK A MÁGIA A TERMINÁLBAN
    print("\n" + "█"*60)
    print(f" [SKYAI SECURITY] TÁRCA HITELESÍTVE!")
    print(f" 🔗 Csatlakoztatott cím: {wallet_address}")
    print(f" ✅ Hozzáférés: ENGEDÉLYEZVE")
    print(f" ⚠️  FIGYELEM: Ez a cím mostantól jogosult a Bálna tranzakciókra.")
    print("█"*60 + "\n")
    
    return jsonify({"status": "verified", "message": "SkyAI Security Logged"})

if __name__ == '__main__':
    print("--------------------------------------------------")
    print(" SKYAI WHALE VAULT (WEB 3.0) INDÍTÁSA...")
    print(" Nyisd meg a böngészőben: http://127.0.0.1:5000")
    print("--------------------------------------------------")
    app.run(port=5000)
