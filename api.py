from flask import Flask, request
import pandas as pd
import datetime

app = Flask(__name__)
WATCHLIST_FILE = 'watchlist.csv'

@app.route('/add_ticker', methods=['POST'])
def add_ticker():
    data = request.json
    ticker = data.get('ticker')
    if ticker:
        try:
            watchlist = pd.read_csv(WATCHLIST_FILE)
        except FileNotFoundError:
            watchlist = pd.DataFrame(columns=['Ticker', 'Date'])
        if ticker not in watchlist['Ticker'].values:
            watchlist.loc[len(watchlist)] = [ticker, datetime.datetime.now()]
            watchlist.to_csv(WATCHLIST_FILE, index=False)
            print(f"Ajouté : {ticker}")
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    app.run(debug=True, port=5001)
