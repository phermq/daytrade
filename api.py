from flask import Flask, request
import pandas as pd
import datetime
import json

app = Flask(__name__)
WATCHLIST_FILE = 'watchlist.csv'

@app.route('/add_ticker', methods=['POST'])
def add_ticker():
    data = request.json
    print("✅ Requête reçue :", data)  # 🔍 LOG ICI
    raw_ticker = data.get('ticker')
    if raw_ticker:
        ticker = raw_ticker.strip('"').strip()
    else:
        ticker = None

    if ticker:
        try:
            watchList = pd.read_csv(WATCHLIST_FILE)
        except FileNotFoundError:
            watchList = pd.DataFrame(columns=['Ticker', 'Date'])

        if ticker not in watchList['Ticker'].values:
            watchList.loc[len(watchList)] = [ticker, datetime.datetime.now().isoformat()]
            watchList.to_csv(WATCHLIST_FILE, index=False)
            print(f"➕ Ajouté : {ticker}")
        else:
            print(f"ℹ️ Déjà présent : {ticker}")

        return {'status': 'ok'}, 200

    return {'status': 'no ticker provided'}, 400
@app.route('/tickers', methods=['GET'])

def get_tickers():
    try:
        watchList = pd.read_csv(WATCHLIST_FILE)
    except FileNotFoundError:
        watchList = pd.DataFrame(columns=['Ticker', 'Date'])
    return watchList.to_json(orient='records')
    
if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')  # 🔥 Nécessaire pour Render
