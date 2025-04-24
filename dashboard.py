import dash
from dash import html
import pandas as pd
import yfinance as yf
import ta
import requests
import os

# Charger le webhook Discord si défini
webhook = os.getenv("YOUR_WEBHOOK_URL")

app = dash.Dash(__name__)

# 📡 Récupérer la watchlist depuis l'API Flask
try:
    response = requests.get("https://daytrade-api.onrender.com/tickers")
    watchlist = pd.DataFrame(response.json())
    print("✅ Watchlist chargée :")
    print(watchlist)
except Exception as e:
    print("❌ Erreur lors de la récupération de la watchlist :", e)
    watchlist = pd.DataFrame(columns=['Ticker', 'Date'])

rows = []

# 🔍 Analyse des tickers
for ticker in watchlist['Ticker']:
    try:
        print(f"📊 Analyse de : {ticker}")
        df = yf.download(ticker, period="1d", interval="1m")

        if df is None or df.empty or len(df) < 10:
            print(f"⚠️ Données insuffisantes pour {ticker}")
            rows.append(html.Tr([html.Td(ticker), html.Td("Données insuffisantes")]))
            continue

        df['body'] = abs(df['Close'] - df['Open'])
        df['atr'] = ta.volatility.AverageTrueRange(
            df['High'], df['Low'], df['Close'], window=10
        ).average_true_range()

        df['signal'] = (df['body'] > 1.5 * df['atr']) & (
            (df['Close'] - df['Open']) / df['Open'] > 0.012
        )

        if df['signal'].iloc[-1]:
            print(f"✅ Signal détecté sur {ticker}")
            if webhook:
                requests.post(webhook, json={"content": f"✅ Breakout détecté : {ticker}"})
            rows.append(html.Tr([html.Td(ticker), html.Td("Signal détecté")]))
        else:
            rows.append(html.Tr([html.Td(ticker), html.Td("Rien")]))
    except Exception as e:
        print(f"❌ Erreur avec {ticker} : {e}")
        rows.append(html.Tr([html.Td(ticker), html.Td("Erreur")]))
        continue

# 🧱 Mise en page Dash
app.layout = html.Div([
    html.H1("📈 Watchlist Intraday"),
    html.Table([html.Tr([html.Th("Ticker"), html.Th("Signal")])] + rows)
])

# 🏁 Exécution locale ou Render
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=10000)
