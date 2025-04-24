import dash
from dash import html
import pandas as pd
import yfinance as yf
import ta
import requests

app = dash.Dash(__name__)
watchlist = pd.read_csv('watchlist.csv')
rows = []

for ticker in watchlist['Ticker']:
    try:
        df = yf.download(ticker, period="1d", interval="1m")
        if len(df) < 10:
            continue
        df['body'] = abs(df['Close'] - df['Open'])
        df['atr'] = ta.volatility.AverageTrueRange(df['High'], df['Low'], df['Close'], window=10).average_true_range()
        df['signal'] = (df['body'] > 1.5 * df['atr']) & ((df['Close'] - df['Open']) / df['Open'] > 0.012)

        if df['signal'].iloc[-1]:
            requests.post("https://discord.com/api/webhooks/YOUR_WEBHOOK_URL", json={"content": f"✅ Breakout détecté : {ticker}"})
            rows.append(html.Tr([html.Td(ticker), html.Td("Signal détecté")]))
        else:
            rows.append(html.Tr([html.Td(ticker), html.Td("Rien")]))
    except:
        continue

app.layout = html.Div([
    html.H1("📈 Watchlist Intraday"),
    html.Table([html.Tr([html.Th("Ticker"), html.Th("Signal")])] + rows)
])

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
