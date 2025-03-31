from datetime import datetime, timedelta

import pytz
from plotly import graph_objs as go

from amberdata_rest.common import ApiKeyGetMode
from amberdata_rest.constants import TimeFormat, MarketDataVenue
from amberdata_rest.spot.service import SpotRestService

srs = SpotRestService(ApiKeyGetMode.LOCAL_FILE, {"local_key_path": "../.localKeys"}, 16)

def trades_graph(start_date: datetime, end_date: datetime, instrument: str, exchange: MarketDataVenue):
    trades_df = srs.get_trades_historical_raw(instrument=instrument, exchange=exchange, start_date=start_date, end_date=end_date,time_format=TimeFormat.MILLISECONDS)
    # Draw a scatter plot of the trades where buys are green and sells are red, otherwise anything else is blue
    fig = go.Figure()
    trades_df['side'] = trades_df['isBuySide'].apply(lambda x: 'BUY' if x else 'SELL')  # Determine the side based on isBuySide
    trades_df['color'] = trades_df['side'].apply(lambda x : 'green' if x == 'BUY' else 'red' if x == 'SELL' else 'blue')
    fig.add_trace(go.Scatter(x=trades_df['exchangeTimestamp'], y=trades_df['price'], mode='markers', marker=dict(color=trades_df['color'])))
    layout = {
        'title': f"{instrument.upper()} Trades",
        'showlegend': False,
        'xaxis': {"title": "Time (UTC)"},
        'yaxis': {"title": "Price"},
    }
    fig.update_layout(layout)
    return fig

def main():
    asset = "btc"
    instrument = f"{asset}_usdt"
    exchange = [MarketDataVenue.BINANCE]
    end_date = datetime.now(tz=pytz.utc) - timedelta(minutes=10)
    lookback = timedelta(minutes=30) + timedelta(minutes=10)
    start_date = end_date - lookback
    # Draw the trades
    fig = trades_graph(start_date, end_date, instrument, exchange[0])
    fig.update_layout(title_text=f"{instrument.upper()} Trades")
    fig.show()



if __name__ == '__main__':
    main()