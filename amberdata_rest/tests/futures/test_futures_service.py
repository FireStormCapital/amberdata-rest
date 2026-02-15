import os
import unittest
from datetime import datetime, timedelta

import numpy
import pandas as pd
import pytz

from amberdata_rest.common import ApiKeyGetMode
from amberdata_rest.constants import MarketDataVenue, TimeFormat
from amberdata_rest.futures.service import FuturesRestService

# Determine the directory of the current file
current_dir = os.path.dirname(__file__)
local_key_path = os.path.join(current_dir, "../../.localKeys")

frs = FuturesRestService(ApiKeyGetMode.LOCAL_FILE, {"local_key_path": local_key_path})

class FuturesRestTest(unittest.TestCase):

    def test_headers(self):
        headers = frs._headers()
        self.assertTrue('x-api-key' in headers.keys(), 'x-api-key not in headers')
        self.assertTrue('accept' in headers.keys(), 'accept not in headers')
        self.assertTrue(headers['accept'] == 'application/json', 'accept != application/json')

    def test_get_exchanges_information_vanilla(self):
        funding_data = frs.get_funding_information()
        self.assertTrue(len(funding_data) > 0, 'no exchanges information returned')
        self.assertTrue('exchange' in funding_data.index.names, 'exchange not in exchanges data keys')
        self.assertTrue('instrument' in funding_data.columns, 'instrument not in exchanges data keys')
        self.assertTrue('startDate' in funding_data.columns, 'startDate not in exchanges data keys')
        self.assertTrue('endDate' in funding_data.columns, 'endDate not in exchanges data keys')
        exchange_set = funding_data.index.unique().values
        instrument_set = funding_data['instrument'].unique()
        self.assertTrue('binance' in exchange_set, 'binance not in exchanges')
        self.assertTrue('bybit' in exchange_set, 'bybit not in exchanges')
        self.assertTrue('deribit' in exchange_set, 'deribit not in exchanges')
        self.assertTrue('BTCUSDT' in instrument_set, 'btc_usdt not in instruments')
        self.assertTrue('ETHUSDT' in instrument_set, 'eth_usdt not in instruments')
        self.assertTrue('BTCUSD' in instrument_set, 'btc_usd not in instruments')
        self.assertTrue('ETHUSD' in instrument_set, 'eth_usd not in instruments')

    def test_get_exchanges_information_specific_exchange(self):
        exchange_data = frs.get_funding_information_raw(exchanges=[MarketDataVenue.BINANCE, MarketDataVenue.BYBIT])
        self.assertTrue('data' in exchange_data.keys(), 'data not in exchange')
        self.assertTrue(len(exchange_data['data']) > 0, 'no exchanges returned')
        exchange_set = set()
        instrument_set = set()
        for row in exchange_data['data']:
            exchange_set.add(row['exchange'])
            instrument_set.add(row['instrument'])
        self.assertTrue('binance' in exchange_set, 'binance not in exchanges')
        self.assertTrue('bybit' in exchange_set, 'bybit not in exchanges')
        self.assertFalse('huobi' in exchange_set , 'huobi is incorrectly in exchanges')
        self.assertTrue('BTCUSDT' in instrument_set, 'btc_usdt not in instruments')
        self.assertTrue('ETHUSDT' in instrument_set, 'eth_usdt not in instruments')
        self.assertTrue('BTCUSD' in instrument_set, 'btc_usd not in instruments')
        self.assertTrue('ETHUSD' in instrument_set, 'eth_usd not in instruments')

    def test_get_funding_rates_vanilla(self):
        instrument = "BTCUSDT"
        funding_rates_data = frs.get_funding_rates(instrument, MarketDataVenue.BINANCE)
        self.assertTrue('binance' in funding_rates_data.index.values)
        self.assertTrue(instrument in funding_rates_data['instrument'].values)
        self.assertTrue('fundingRate' in funding_rates_data.columns)
        self.assertTrue(funding_rates_data['fundingRate'].dtype == numpy.float64)

    def test_get_funding_rates_with_params(self):
        instrument = "BTCUSDT"
        utc_tz = pytz.UTC
        start_date = datetime(2024, 3, 1, 0, 0, tzinfo=utc_tz)
        end_date = datetime(2024, 3, 1, 1, 0, tzinfo=utc_tz)
        funding_rates_data = frs.get_funding_rates(instrument, MarketDataVenue.BINANCE, start_date, end_date, TimeFormat.ISO)
        funding_rates_data['timestamp'] = pd.to_datetime(funding_rates_data['exchangeTimestamp'])
        self.assertTrue('binance' in funding_rates_data.index.values)
        self.assertTrue(instrument in funding_rates_data['instrument'].values)
        self.assertTrue('fundingRate' in funding_rates_data.columns)
        self.assertTrue(funding_rates_data['fundingRate'].dtype == numpy.float64)
        # Confirm the data sent is within start_date and end date
        self.assertTrue(funding_rates_data['timestamp'].min() >= start_date)
        self.assertTrue(funding_rates_data['timestamp'].max() <= end_date)

    def test_get_funding_rates_batch_historical_vanilla(self):
        exchange = MarketDataVenue.BINANCE
        instruments = ["BTCUSDT", "ETHUSDT"]
        funding_rates_data = frs.get_funding_batch_historical(exchange, instruments)
        self.assertTrue('BTCUSDT' in funding_rates_data.index.get_level_values('instrument'), "BTC-USDT missing from the data!")
        self.assertTrue('ETHUSDT' in funding_rates_data.index.get_level_values('instrument'), "ETH-USDT missing from the data!")
        self.assertTrue('fundingRate' in funding_rates_data.columns, "fundingRate missing from the data!")

    def test_get_insurance_funds_information(self):
        insurance_funds_data = frs.get_insurance_funds_information()
        self.assertTrue(len(insurance_funds_data) > 0, 'no insurance funds information returned')
        self.assertTrue('exchange' in insurance_funds_data.index.names, 'exchange not in insurance funds data keys')
        self.assertTrue('instrument' in insurance_funds_data.columns, 'instrument not in insurance funds data keys')
        self.assertTrue('underlying' in insurance_funds_data.columns, 'underlying not in insurance funds data keys')
        self.assertTrue('startDate' in insurance_funds_data.columns, 'startDate not in insurance funds data keys')
        self.assertTrue('endDate' in insurance_funds_data.columns, 'endDate not in insurance funds data keys')
        exchange_set = insurance_funds_data.index.unique().values
        instrument_set = insurance_funds_data['instrument'].unique()
        self.assertTrue('huobi' in exchange_set, 'binance not in insurance funds')
        self.assertTrue('okex' in exchange_set, 'binance not in insurance funds')
        self.assertTrue('bybit' in exchange_set, 'bybit not in insurance funds')
        self.assertTrue('bitmex' in exchange_set, 'bybit not in insurance funds')
        self.assertTrue('BTC' in instrument_set, 'btc_usdt not in instruments')
        self.assertTrue('USDT' in instrument_set, 'btc_usdt not in instruments')
        self.assertTrue('ETH' in instrument_set, 'btc_usdt not in instruments')
        self.assertTrue('BTC-USDT' in instrument_set, 'btc_usdt not in instruments')
        self.assertTrue('ETH-USDT' in instrument_set, 'eth_usdt not in instruments')

    def test_get_insurance_funds_vanilla(self):
        instrument = "BTC-USDT"
        insurance_funds_data = frs.get_insurance_funds(instrument, MarketDataVenue.HUOBI)
        self.assertTrue('huobi' in insurance_funds_data.index.values)
        self.assertTrue(instrument in insurance_funds_data['instrument'].values)
        self.assertTrue('fund' in insurance_funds_data.columns)

    def test_get_liquidations_information(self):
        liquidations_info = frs.get_liquidations_information()
        self.assertTrue(len(liquidations_info) > 0, 'no liquidations information returned')
        self.assertTrue('exchange' in liquidations_info.index.names, 'exchange not in liquidations data keys')
        self.assertTrue('instrument' in liquidations_info.columns, 'instrument not in liquidations data keys')
        self.assertTrue('startDate' in liquidations_info.columns, 'startDate not in liquidations data keys')
        self.assertTrue('endDate' in liquidations_info.columns, 'endDate not in liquidations data keys')
        exchange_set = liquidations_info.index.unique().values
        instrument_set = liquidations_info['instrument'].unique()
        self.assertTrue('huobi' in exchange_set, 'huobi not in liquidations')
        self.assertTrue('binance' in exchange_set, 'okex not in liquidations')
        self.assertTrue('BTC-USDT' in instrument_set, 'btc_usdt not in instruments')
        self.assertTrue('ETH-USDT' in instrument_set, 'eth_usdt not in instruments')

    def test_get_liquidations_vanilla(self):
        instrument = "BTCUSDT"
        liquidations_data = frs.get_liquidations(instrument, MarketDataVenue.BINANCE)
        self.assertTrue(('binance', instrument) in liquidations_data.index.unique())
        self.assertTrue('price' in liquidations_data.columns)
        self.assertTrue('volume' in liquidations_data.columns)
        self.assertTrue('base_asset' in liquidations_data.columns)
        self.assertTrue('positionType' in liquidations_data.columns)

    def test_get_long_short_ratio_information(self):
        long_short_info = frs.get_long_short_ratio_information()
        self.assertTrue(len(long_short_info) > 0, 'no long short information returned')
        self.assertTrue('exchange' in long_short_info.index.names, 'exchange not in long short data keys')
        self.assertTrue('instrument' in long_short_info.columns, 'instrument not in long short data keys')
        self.assertTrue('startDate' in long_short_info.columns, 'startDate not in long short data keys')
        self.assertTrue('endDate' in long_short_info.columns, 'endDate not in long short data keys')
        exchange_set = long_short_info.index.unique().values
        instrument_set = long_short_info['instrument'].unique()
        self.assertTrue('bybit' in exchange_set, 'bybit not in long short')
        self.assertTrue('binance' in exchange_set, 'okex not in long short')
        self.assertTrue('BTCUSDT' in instrument_set, 'btc_usdt not in instruments')
        self.assertTrue('ETHUSDT' in instrument_set, 'eth_usdt not in instruments')

    def test_get_long_short_ratio_vanilla(self):
        instrument = "BTCUSDT"
        long_short_ratio_data = frs.get_long_short_ratio(instrument, MarketDataVenue.BINANCE)
        self.assertTrue('binance' in long_short_ratio_data.index.values, "binance missing from the data!")
        self.assertTrue('longAccount' in long_short_ratio_data.columns, "longAccount missing from the data!")
        self.assertTrue('shortAccount' in long_short_ratio_data.columns, "longAccount missing from the data!")
        self.assertTrue('ratio' in long_short_ratio_data.columns, "longAccount missing from the data!")
        self.assertTrue(instrument in long_short_ratio_data['instrument'].unique())

    def test_get_long_short_ratio_with_parallel_execution(self):
        instrument = "BTCUSDT"
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()
        long_short_ratio_data = frs.get_long_short_ratio_raw(
            instrument,
            MarketDataVenue.BINANCE,
            start_date,
            end_date,
            parallel_execution=True
        )
        long_short_ratio_data['exchangeTimestamp'] = pd.to_datetime(long_short_ratio_data['exchangeTimestamp'], unit='ms', utc=True)
        self.assertTrue('binance' in long_short_ratio_data['exchange'].values)
        self.assertTrue(instrument in long_short_ratio_data['instrument'].values)
        self.assertTrue('longAccount' in long_short_ratio_data.columns)
        self.assertTrue('shortAccount' in long_short_ratio_data.columns)
        self.assertTrue('ratio' in long_short_ratio_data.columns)

    def test_get_open_interest_with_parallel_execution(self):
        instrument = "BTCUSD_PERP"
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()
        open_interest_data = frs.get_open_interest_raw(
            instrument,
            MarketDataVenue.BINANCE,
            start_date,
            end_date,
            parallel_execution=True
        )
        open_interest_data['exchangeTimestamp'] = pd.to_datetime(open_interest_data['exchangeTimestamp'], unit='ms', utc=True)
        self.assertTrue('binance' in open_interest_data['exchange'].values)
        self.assertTrue(instrument in open_interest_data['instrument'].values)
        self.assertTrue('type' in open_interest_data.columns)
        self.assertTrue('value' in open_interest_data.columns)

    def test_get_ohlcv_information(self):
        ohlcv_information_data = frs.get_ohlcv_information()
        self.assertIsNotNone(ohlcv_information_data, 'result is None')
        self.assertFalse(ohlcv_information_data.empty, 'result is empty')

    def test_get_ohlcv_vanilla(self):
        instrument = "BTCUSDT"
        ohlcv_data = frs.get_ohlcv(instrument, [MarketDataVenue.BINANCE])
        self.assertTrue('open' in ohlcv_data.columns)
        self.assertTrue('high' in ohlcv_data.columns)
        self.assertTrue('low' in ohlcv_data.columns)
        self.assertTrue('close' in ohlcv_data.columns)
        self.assertTrue('volume' in ohlcv_data.columns)
        self.assertTrue('timestamp' in ohlcv_data.index.names)
        self.assertTrue('timestamp' in ohlcv_data.index.names)
        self.assertTrue('instrument' in ohlcv_data.columns)
        self.assertTrue(instrument in ohlcv_data['instrument'].unique())

    def test_get_ohlcv_batch_vanilla(self):
        instruments = ["BTCUSDT", "ETHUSDT"]
        ohlcv_data = frs.get_ohlcv_batch([MarketDataVenue.BINANCE, MarketDataVenue.BYBIT], instruments)
        self.assertTrue('open' in ohlcv_data.columns)
        self.assertTrue('high' in ohlcv_data.columns)
        self.assertTrue('low' in ohlcv_data.columns)
        self.assertTrue('close' in ohlcv_data.columns)
        self.assertTrue('volume' in ohlcv_data.columns)
        self.assertTrue('timestamp' in ohlcv_data.columns)
        self.assertTrue('instrument' in ohlcv_data.columns)
        self.assertTrue('BTCUSDT' in ohlcv_data['instrument'].unique())
        self.assertTrue('ETHUSDT' in ohlcv_data['instrument'].unique())
        self.assertTrue('binance' in ohlcv_data.index.unique().values)
        self.assertTrue('bybit' in ohlcv_data.index.unique().values)

    def test_get_open_interest_information_vanilla(self):
        open_interest_information = frs.get_open_interest_information()
        self.assertTrue(len(open_interest_information) > 0, 'no long short information returned')
        self.assertTrue('exchange' in open_interest_information.index.names, 'exchange not in long short data keys')
        self.assertTrue('instrument' in open_interest_information.columns, 'instrument not in long short data keys')
        self.assertTrue('startDate' in open_interest_information.columns, 'startDate not in long short data keys')
        self.assertTrue('endDate' in open_interest_information.columns, 'endDate not in long short data keys')
        exchange_set = open_interest_information.index.unique().values
        instrument_set = open_interest_information['instrument'].unique()
        self.assertTrue('bybit' in exchange_set, 'bybit not in long short')
        self.assertTrue('binance' in exchange_set, 'okex not in long short')
        self.assertTrue('BTCUSDT' in instrument_set, 'btc_usdt not in instruments')
        self.assertTrue('ETHUSDT' in instrument_set, 'eth_usdt not in instruments')

    def test_get_open_interest_vanilla(self):
        instrument = "BTCUSD_PERP"
        open_interest = frs.get_open_interest(instrument, MarketDataVenue.BINANCE)
        print(open_interest)
        self.assertTrue('binance' in open_interest.index.unique().values, "binance missing from the data!")
        self.assertTrue('instrument' in open_interest.columns, "instrument missing from the data!")
        self.assertTrue('exchangeTimestamp' in open_interest.columns, "exchangeTimestamp missing from the data!")
        self.assertTrue('instrument' in open_interest.columns, "instrument missing from the data!")
        self.assertTrue('type' in open_interest.columns, "type missing from the data!")
        self.assertTrue('value' in open_interest.columns, "value missing from the data!")

    def test_get_open_interest_batch_vanilla(self):
        instruments = ["BTCUSDT", "ETHUSDT"]
        open_interest_data = frs.get_open_interest_batch([MarketDataVenue.BINANCE, MarketDataVenue.BYBIT], instruments)
        self.assertTrue('timestamp' in open_interest_data.columns)
        self.assertTrue('type' in open_interest_data.columns)
        self.assertTrue('value' in open_interest_data.columns)
        self.assertTrue('instrument' in open_interest_data.columns)
        self.assertTrue('BTCUSDT' in open_interest_data['instrument'].unique())
        self.assertTrue('ETHUSDT' in open_interest_data['instrument'].unique())
        self.assertTrue('binance' in open_interest_data.index.unique().values)
        self.assertTrue('bybit' in open_interest_data.index.unique().values)

    def test_get_order_book_information_vanilla(self):
        order_book_info = frs.get_order_book_information()
        self.assertTrue(len(order_book_info) > 0, 'no order book information returned')
        self.assertTrue('startDate' in order_book_info.columns, 'startDate not in order book data keys')
        self.assertTrue('endDate' in order_book_info.columns, 'endDate not in order book data keys')
        instrument_set = set()
        exchange_set = set()
        for exchange, instrument in order_book_info.index.values:
            exchange_set.add(exchange)
            instrument_set.add(instrument)
        self.assertTrue('binance' in exchange_set, 'binance not in order book data keys')
        self.assertTrue('bybit' in exchange_set, 'bybit not in order book data keys')
        self.assertTrue('BTCUSDT' in instrument_set, 'btc_usdt not in order book data keys')
        self.assertTrue('AVAXUSDT' in instrument_set, 'avax_usdt not in order book data keys')

    def test_get_order_book_snapshots_vanilla(self):
        exchange = MarketDataVenue.BINANCE
        start_date = datetime(2024, 8, 1, 0, 0, 0)
        end_date = datetime(2024, 8, 1, 0, 15, 0)
        instrument = "BTCUSDT"
        order_book_snapshot_data = frs.get_order_book_snapshots_historical(instrument, exchange, start_date, end_date)
        self.assertTrue('price' in order_book_snapshot_data.columns, 'price not in order book data keys')
        self.assertTrue('volume' in order_book_snapshot_data.columns, 'volume not in order book data keys')
        self.assertTrue('numOrders' in order_book_snapshot_data.columns, 'numOrders not in order book data keys')
        self.assertTrue('timestamp' in order_book_snapshot_data.index.names, 'timestamp not in order book data keys')
        self.assertTrue('instrument' in order_book_snapshot_data.index.names, 'instrument not in order book data keys')
        self.assertTrue('exchange' in order_book_snapshot_data.index.names, 'exchange not in order book data keys')
        self.assertTrue('side' in order_book_snapshot_data.index.names, 'side not in order book data keys')

    def test_get_order_book_events_vanilla(self):
        instrument = "BTCUSDT"
        exchange = MarketDataVenue.BINANCE
        start_date = datetime(2024, 8, 1, 0, 0, 0)
        end_date = datetime(2024, 8, 1, 0, 5, 0)
        order_book_events_data = frs.get_order_book_events_historical(instrument, exchange, start_date, end_date)
        self.assertTrue(len(order_book_events_data) > 0, 'no order book events information returned')
        self.assertTrue('price' in order_book_events_data.columns, 'price not in order book events data keys')
        self.assertTrue('volume' in order_book_events_data.columns, 'volume not in order book events data keys')
        self.assertTrue('numOrders' in order_book_events_data.columns, 'numOrders not in order book events data keys')
        self.assertTrue('timestamp' in order_book_events_data.index.names, 'timestamp not in order book events data keys')
        self.assertTrue('instrument' in order_book_events_data.index.names, 'instrument not in order book events data keys')
        self.assertTrue('exchange' in order_book_events_data.index.names, 'exchange not in order book events data keys')
        self.assertTrue('side' in order_book_events_data.index.names, 'side not in order book events data keys')

    def test_get_tickers_information(self):
        tickers_info = frs.get_tickers_information()
        self.assertTrue(len(tickers_info) > 0, 'no tickers information returned')
        self.assertTrue('exchange' in tickers_info.index.names, 'exchange not in tickers data keys')
        self.assertTrue('instrument' in tickers_info.columns, 'instrument not in tickers data keys')
        self.assertTrue('startDate' in tickers_info.columns, 'startDate not in tickers data keys')
        self.assertTrue('endDate' in tickers_info.columns, 'endDate not in tickers data keys')
        exchange_set = tickers_info.index.unique().values
        instrument_set = tickers_info['instrument'].unique()
        self.assertTrue('binance' in exchange_set, 'binance not in tickers')
        self.assertTrue('bybit' in exchange_set, 'bybit not in tickers')
        self.assertTrue('okex' in exchange_set, 'okex not in tickers')
        self.assertTrue('BTCUSDT' in instrument_set, 'btc_usdt not in instruments')
        self.assertTrue('ETHUSDT' in instrument_set, 'eth_usdt not in instruments')

    def test_get_tickers_vanilla(self):
        exchange = MarketDataVenue.BINANCE
        instrument = "BTCUSDT"
        start_date = datetime(2024, 8, 1, 0, 0, 0)
        end_date = datetime(2024, 8, 1, 0, 5, 0)
        tickers_data = frs.get_tickers(instrument, exchange, start_date, end_date)
        self.assertTrue('bid' in tickers_data.columns, 'bid not in tickers data keys')
        self.assertTrue('ask' in tickers_data.columns, 'volume not in tickers data keys')
        self.assertTrue('mid' in tickers_data.columns, 'timestamp not in tickers data keys')
        self.assertTrue('bidVolume' in tickers_data.columns, 'instrument not in tickers data keys')
        self.assertTrue('askVolume' in tickers_data.columns, 'exchange not in tickers data keys')
        self.assertTrue('markPrice' in tickers_data.columns, 'exchange not in tickers data keys')
        self.assertTrue('indexPrice' in tickers_data.columns, 'exchange not in tickers data keys')
        self.assertTrue('exchangeTimestamp' in tickers_data.index.names, 'exchangeTimestamp not in tickers data keys')
        self.assertTrue('instrument' in tickers_data.index.names, 'instrument not in tickers data keys')
        self.assertTrue('exchange' in tickers_data.index.names, 'exchange not in tickers data keys')
        exchange_set = tickers_data.index.get_level_values('exchange').unique()
        instrument_set = tickers_data.index.get_level_values('instrument').unique()
        self.assertTrue(exchange in exchange_set, 'exchange not in tickers index')
        self.assertTrue(instrument in instrument_set, 'instrument not in tickers index')

    def test_get_trades_information(self):
        trades_info = frs.get_trades_information()
        self.assertTrue(len(trades_info) > 0, 'no trades information returned')
        self.assertTrue('exchange' in trades_info.index.names, 'exchange not in trades data keys')
        self.assertTrue('instrument' in trades_info.index.names, 'instrument not in trades data keys')
        self.assertTrue('startDate' in trades_info.columns, 'startDate not in trades data keys')
        self.assertTrue('endDate' in trades_info.columns, 'endDate not in trades data keys')
        exchange_set = trades_info.index.get_level_values('exchange').unique()
        instrument_set = trades_info.index.get_level_values('instrument').unique()
        self.assertTrue('binance' in exchange_set, 'binance not in trades')
        self.assertTrue('bybit' in exchange_set, 'bybit not in trades')
        self.assertTrue('okex' in exchange_set, 'okex not in trades')
        self.assertTrue('BTCUSDT' in instrument_set, 'btc_usdt not in instruments')
        self.assertTrue('ETHUSDT' in instrument_set, 'eth_usdt not in instruments')

    def test_get_trades_vanilla(self):
        exchange = MarketDataVenue.BINANCE
        instrument = "BTCUSDT"
        start_date = datetime(2024, 8, 1, 0, 0, 0)
        end_date = datetime(2024, 8, 1, 0, 5, 0)
        trades_data = frs.get_trades(instrument, exchange, start_date, end_date)
        self.assertTrue('price' in trades_data.columns, 'price not in trades data keys')
        self.assertTrue('volume' in trades_data.columns, 'volume not in trades data keys')
        self.assertTrue('side' in trades_data.columns, 'volume not in trades data keys')
        self.assertTrue('tradeId' in trades_data.columns, 'volume not in trades data keys')
        self.assertTrue('numOrders' in trades_data.columns, 'volume not in trades data keys')
        self.assertTrue('timestamp' in trades_data.index.names, 'timestamp not in trades data keys')
        self.assertTrue('instrument' in trades_data.index.names, 'instrument not in trades data keys')
        self.assertTrue('exchange' in trades_data.index.names, 'exchange not in trades data keys')
        exchange_set = trades_data.index.get_level_values('exchange').unique()
        instrument_set = trades_data.index.get_level_values('instrument').unique()
        self.assertTrue(exchange in exchange_set, 'exchange not in trades index')
        self.assertTrue(instrument in instrument_set, 'instrument not in trades index')

    def test_get_exchanges_reference_vanilla(self):
        result = frs.get_exchanges_reference()
        self.assertIsInstance(result, dict, 'result is not a dict')
        self.assertIn('data', result, 'data key not in result')
        self.assertTrue(len(result['data']) > 0, 'no exchanges reference data returned')
        # Verify entries have expected fields
        first_entry = result['data'][0]
        self.assertIn('exchange', first_entry, 'exchange not in entry')
        self.assertIn('instrument', first_entry, 'instrument not in entry')

    def test_get_exchanges_reference_filtered_by_exchange(self):
        result = frs.get_exchanges_reference(exchanges=[MarketDataVenue.BINANCE])
        self.assertIsInstance(result, dict, 'result is not a dict')
        self.assertIn('data', result, 'data key not in result')
        self.assertTrue(len(result['data']) > 0, 'no exchanges reference data for binance')
        # All entries should be binance
        for entry in result['data']:
            self.assertEqual(entry['exchange'].lower(), 'binance', f'unexpected exchange: {entry["exchange"]}')
