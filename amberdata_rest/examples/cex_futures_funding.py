from datetime import datetime, timedelta
from typing import List

import pytz
from plotly import graph_objs as go
from plotly.subplots import make_subplots

from amberdata_rest.common import ApiKeyGetMode
from amberdata_rest.constants import TimeFormat, MarketDataVenue
from amberdata_rest.futures.service import FuturesRestService

frs = FuturesRestService(ApiKeyGetMode.LOCAL_FILE, {"local_key_path": "../.localKeys"})


def get_funding_figs(instrumentList: List[str], start_date: datetime, end_date: datetime, exchanges: List[MarketDataVenue]):
    for instrument in instrumentList:
        fig = make_subplots(rows=1, cols=1, shared_xaxes=True,
                            specs=[[{}]])
        for exchange in exchanges:
            try:
                funding_df = frs.get_funding_rates(instrument, exchange, start_date, end_date, TimeFormat.MILLISECONDS)
            except Exception as e:
                print(f"Failed to get funding rates for {instrument} on {exchange.name}")
                continue
            if len(funding_df) == 0:
                print(f"No funding rates for {instrument} on {exchange.name}")
                continue
            funding_df['fundingRateApr'] = funding_df['fundingRate'] * 3 * 365 * 100
            line = go.Scatter(x=funding_df['exchangeTimestamp'], y=funding_df['fundingRateApr'], name=f'{exchange.name} Funding Rate', mode='lines')
            fig.add_trace(line)

        layout = {
            'title': f"{instrument} Funding %",
            'showlegend': True,
            'xaxis': {"title": "Time (UTC)"},
            'yaxis': {"title": "Funding %"},
        }
        fig.update_layout(layout)
        fig.show()


def main():
    assetList = ["BTC", "ETH", "SOL", "AVAX", "SUI", "SEI", "LINK"]
    instrumentList = [f"{asset}USDT" for asset in assetList]
    end_date = datetime.now(tz=pytz.utc) - timedelta(minutes=10)
    lookback = timedelta(days=30)
    start_date = end_date - lookback
    exchanges = [MarketDataVenue.BINANCE, MarketDataVenue.BYBIT, MarketDataVenue.BITMEX, MarketDataVenue.DERIBIT, MarketDataVenue.HUOBI, MarketDataVenue.KRAKEN, MarketDataVenue.OKEX ]
    # Draw a price & volume graph for a given asset
    get_funding_figs(instrumentList, start_date, end_date, exchanges)



if __name__ == '__main__':
    main()