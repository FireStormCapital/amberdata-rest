from datetime import datetime, timedelta

import pytz
from plotly import graph_objs as go
from plotly.subplots import make_subplots

from amberdata_rest.common import ApiKeyGetMode
from amberdata_rest.constants import TimeFormat, TimeInterval, MarketDataVenue
from amberdata_rest.spot.service import SpotRestService

srs = SpotRestService(ApiKeyGetMode.LOCAL_FILE, {"local_key_path": "../.localKeys"}, 16)


def asset_price_and_volume_graph(start_date: datetime, end_date: datetime, asset: str):
    price_df = srs.get_prices_assets_historical(asset=asset, start_date=start_date, end_date=end_date, time_interval=TimeInterval.MINUTE, time_format=TimeFormat.MILLISECONDS)
    # Draw a graph of the data where:
    # x-axis is the timeEST Column
    # y-axis is the price and the line is the progression of the price column
    # and teh line is overlaid on top of a volume bar chart where the x-axis is the timeEST column
    # secondary y-axis is the volumne column
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True,
                        specs=[[{'secondary_y': True}]])
    bar = go.Bar(x=price_df['timeEST'], y=price_df['volume'], name='Volume')
    line = go.Scatter(x=price_df['timeEST'], y=price_df['price'], name='Price', mode='lines')
    fig.add_trace(line)
    fig.add_trace(bar, secondary_y=True)
    layout = {
        'title': f"{asset.upper()} Price (USD)",
        'showlegend': False,
        'xaxis': {"title": "Time (Eastern)"},
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
    # Draw a price & volume graph for a given asset
    px_and_volume_fig = asset_price_and_volume_graph(start_date, end_date, asset)
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True,
                        specs=[[{'secondary_y': True}]])

    fig.add_trace(px_and_volume_fig['data'][0], row=1, col=1, secondary_y=False)
    fig.add_trace(px_and_volume_fig['data'][1], row=1, col=1, secondary_y=True)
    fig.update_layout(title_text=f"{instrument.upper()} Px & Volume")
    fig.show()



if __name__ == '__main__':
    main()