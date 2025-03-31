from datetime import datetime, timedelta
from typing import List

import sys
import pytz
from plotly import graph_objs as go
from plotly.subplots import make_subplots

from amberdata_rest.common import ApiKeyGetMode
from amberdata_rest.constants import TimeFormat, MarketDataVenue
from amberdata_rest.futures.service import FuturesRestService
from loguru import logger as lg

frs = FuturesRestService(ApiKeyGetMode.LOCAL_FILE, {"local_key_path": "../.localKeys"})

lg.remove()
lg.add(sys.stdout, level="INFO")


def get_open_interest_figs(instrumentList: List[str], start_date: datetime, end_date: datetime,
                           exchanges: List[MarketDataVenue]):
    for instrument in instrumentList:
        fig = make_subplots(rows=1, cols=1, shared_xaxes=True,
                            specs=[[{"secondary_y": True}]])
        for exchange in exchanges:
            try:
                open_interest_df = frs.get_open_interest_raw(instrument, exchange, start_date, end_date,
                                                             time_format=TimeFormat.MILLISECONDS, batch_period=timedelta(days=7),
                                                             parallel_execution=True)
            except Exception as e:
                print(f"Failed to get open interest for {instrument} on {exchange.name}")
                continue
            if len(open_interest_df) == 0:
                print(f"No open interest data for {instrument} on {exchange.name}")
                continue

            line = go.Scatter(x=open_interest_df['exchangeTimestamp'], y=open_interest_df['value'],
                              name=f'{exchange.name} Open Interest', mode='lines')
            fig.add_trace(line, secondary_y=False)

        layout = {
            'title': f"{instrument} Open Interest",
            'showlegend': True,
            'xaxis': {"title": "Time (UTC)"},
            'yaxis': {"title": "Open Interest"},
        }
        fig.update_layout(layout)
        fig.show()


def main():
    assetList = ["AVAX", "SOL"]
    instrumentList = [f"{asset}USDT" for asset in assetList]
    end_date = datetime.now(tz=pytz.utc)
    start_date = end_date - timedelta(days=90)
    exchanges = [MarketDataVenue.BINANCE, MarketDataVenue.BYBIT]
    # Draw an open interest graph for given assets
    get_open_interest_figs(instrumentList, start_date, end_date, exchanges)


if __name__ == '__main__':
    main()
