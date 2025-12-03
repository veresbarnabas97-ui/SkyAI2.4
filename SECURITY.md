Biztonsági Irányelvek

A SkyAI csapata kiemelten kezeli kereskedési algoritmusaink és felhasználóink adatainak biztonságát. Mivel a projekt pénzügyi jellegű (Kriptokereskedés, API integrációk és Fizetési kapuk), nagyra értékeljük a biztonsági kutatók és a közösség segítségét ökoszisztémánk védelmében.

📦 Támogatott Verziók

Hivatalosan csak a SkyAI legfrissebb stabil verziója részesül biztonsági frissítésekben.

Verzió

Támogatott

Megjegyzés

v2.4

:white_check_mark:

Jelenlegi Stabil Kiadás (Neon Core)

v2.0 - v2.3

:x:

Támogatás vége (EOL)

v1.x

:x:

Elavult

🐞 Sebezhetőség Jelentése

Kérjük, NE jelentsd a biztonsági réseket nyilvános GitHub Issue-ként!

Ha úgy véled, biztonsági résre bukkantál a SkyAI rendszerében (ProBot, Sniper Bot, Whale Bot vagy a Web3 Dashboardok), kérjük, azonnal jelezd nekünk az alábbi privát csatornák egyikén:

Email: veres.barnabas97@gmail.com

Telegram (Sürgős): @VeresBarnabas1

Kérjük, jelentésedben térj ki az alábbi részletekre:

A sebezhetőség leírása.

Lépések a hiba reprodukálásához.

Potenciális hatás (pl. fizetés megkerülése, VIP felületek jogosulatlan elérése, SQL injection).

Válaszadási Határidők

Célunk, hogy a bejelentést 48 órán belül nyugtázzuk.

Becslést adunk a javítás várható idejéről.

Értesítünk, amint a javítás élesítésre került.

🛡️ Hatókör és Kivételek

Hatókörön Belül (In Scope)

SkyAI Telegram Botok: Logikai hibák a bot.py, sniper_bot.py vagy whale_bot.py fájlokban, amelyek lehetővé teszik parancsok jogosulatlan futtatását.

Hozzáférési Vezérlés: A "Kapuőr" (Gatekeeper) logika megkerülése (pl. Sniper/Whale linkek elérése /approve jóváhagyás nélkül).

Web3 Dashboardok: Sebezhetőségek a SkyAISniper.html vagy SkyAIWhale.html fájlokban (pl. XSS, nem biztonságos API hívások).

Adattárolás: A skyai_users.db integritásával kapcsolatos problémák.

Hatókörön Kívül (Out of Scope)

Harmadik Feles Platformok: A szigorúan a Binance, Revolut vagy Pooolse rendszereit érintő biztonsági hibák a mi hatáskörünkön kívül esnek. Kérjük, ezeket az adott platformoknak jelezd.

Social Engineering: Felhasználók vagy adminok elleni adathalász támadások.

Felhasználói Gondatlanság: A felhasználó saját eszközének biztonsági hiányosságaiból eredő privát kulcs vagy API kulcs szivárgások.

⚠️ Kritikus Figyelmeztetés az API Kulcsokkal kapcsolatban

A SkyAI a python-binance könyvtárat használja piaci adatok olvasására.

SOHA ne töltsd fel (commit) az API_KEY vagy API_SECRET adataidat ebbe a repository-ba vagy bármely nyilvános fork-ba.

Az ai_analyzer.py szkriptet úgy terveztük, hogy CSAK OLVASÁSI (READ-ONLY) jogokkal rendelkező API kulcsokat használjon. Ne adj "Trade" (Kereskedés) vagy "Withdraw" (Kifizetés) jogosultságot a Deep Scanner elemzéshez használt kulcsoknak.

📄 Közzétételi Szabályzat

Kérjük, hogy a sebezhetőség részleteit ne hozd nyilvánosságra addig, amíg nem orvosoltuk a problémát. Hiszünk a koordinált közzétételben, és a rendszer javítása után elismerésben részesítjük a kutatókat a felfedezésükért.

SkyAI Systems Precision. Speed. Dominance.
