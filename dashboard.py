import dash
from dash import html
import pandas as pd
import yfinance as yf
import ta
import requests
import os

# Charger l'URL Discord depuis la variable d'environnement
webhook = os.getenv("YOUR_WEBHOOK_URL")

app = dash.Dash(__name__)

# Appel API Flask pour récupérer la watchlist
response = requests.get("https://daytrade-api.onrender.com/tickers")
data = response.json()

# Sécurisation du format
if isinstance(data, dict):
    data = [data]
watchlist = pd.DataFrame(data)

rows = []

for ticker in watchlist['Ticker']:
    try:
        print(f"🔍 Téléchargement de : {ticker}")
        df = yf.download(ticker, period="1d", interval="1m")

        if df.empty or len(df) < 10:
            raise ValueError("Pas assez de données")

        df['body'] = abs(df['Close'] - df['Open'])
        df['atr'] = ta.volatility.AverageTrueRange(
            df['High'], df['Low'], df['Close'], window=10
        ).average_true_range()
        df['signal'] = (df['body'] > 1.5 * df['atr']) & (
            (df['Close'] - df['Open']) / df['Open'] > 0.012
        )

        if df['signal'].iloc[-1]:
            # Alerte Discord
            if webhook:
                requests.post(webhook, json={"content": f"✅ Breakout détecté : {ticker}"})
            rows.append(html.Tr([html.Td(ticker), html.Td("✅ Signal détecté")]))
        else:
            rows.append(html.Tr([html.Td(ticker), html.Td("Rien à signaler")]))
    except Exception as e:
        print(f"❌ Erreur pour {ticker} : {e}")
        rows.append(html.Tr([html.Td(ticker), html.Td("❌ Erreur données")]))

# Layout Dash
app.layout = html.Div([
    html.H1("📈 Watchlist Intraday"),
    html.Table([
        html.Tr([html.Th("Ticker"), html.Th("Signal")])
    ] + rows)
])

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=10000)
