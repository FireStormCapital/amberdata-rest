from datetime import datetime, timedelta
from typing import List

import pytz
from plotly import graph_objs as go
from plotly.subplots import make_subplots

from amberdata_rest.common import ApiKeyGetMode
from amberdata_rest.constants import TimeFormat, TimeInterval, MarketDataVenue
from amberdata_rest.spot.service import SpotRestService

srs = SpotRestService(ApiKeyGetMode.LOCAL_FILE, {"local_key_path": "../.localKeys"}, 16)

def ohlcv_graph(start_date: datetime, end_date: datetime, instrument: str, exchange: List[MarketDataVenue]):
    ohlcv_df = srs.get_ohlcv_historical(instrument=instrument, exchanges=exchange, start_date=start_date, end_date=end_date, time_interval=TimeInterval.MINUTE, time_format=TimeFormat.HUMAN_READABLE, index_keys=['timestamp'])
    # Draw a candlestick graph displaying ohlcv data
    fig = go.Figure(data=[go.Candlestick(x=ohlcv_df.index,
                                         open=ohlcv_df['open'],
                                         high=ohlcv_df['high'],
                                         low=ohlcv_df['low'],
                                         close=ohlcv_df['close'])])
    layout = {
        'title': f"{instrument.upper()} OHLCV",
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
    # Draw the OHLCV for the given pair
    ohlcv_fig = ohlcv_graph(start_date, end_date, instrument, exchange)
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True,
                        specs=[[{'secondary_y': True}]],
                        subplot_titles=("OHLCV"))

    for trace in ohlcv_fig['data']:
        fig.add_trace(trace, row=1, col=1)

    fig.update_layout(title_text=f"{instrument.upper()} OHLCV")
    fig.show()



if __name__ == '__main__':
    main()