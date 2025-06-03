import logging
import os
import time
import unittest
from datetime import datetime, timedelta

import numpy
import pandas as pd

from amberdata_rest.common import NoDataReturned, ApiKeyGetMode
from amberdata_rest.constants import MarketDataVenue, TimeFormat, TimeInterval, BatchPeriod
from amberdata_rest.spot.service import SpotRestService

# Determine the directory of the current file
current_dir = os.path.dirname(__file__)
local_key_path = os.path.join(current_dir, "../../.localKeys")

srs = SpotRestService(ApiKeyGetMode.LOCAL_FILE, {"local_key_path": local_key_path}, 32)


class SpotRestTest(unittest.TestCase):

    def test_headers(self):
        headers = srs._headers()
        self.assertTrue('x-api-key' in headers.keys(), 'x-api-key not in headers')
        self.assertTrue('accept' in headers.keys(), 'accept not in headers')
        self.assertTrue(headers['accept'] == 'application/json', 'accept != application/json')

    def test_get_exchanges_information_vanilla(self):
        exchange_data = srs.get_exchanges_information()
        self.assertTrue('data' in exchange_data.keys(), 'data not in exchanges')
        self.assertTrue(len(exchange_data['data']) > 0, 'no exchanges returned')
        self.assertTrue('exchange' in exchange_data['data'][0].keys(), 'exchange not in exchanges data keys')
        self.assertTrue('instrument' in exchange_data['data'][0].keys(), 'instrument not in exchanges data keys')

        exchange_set = set()
        instrument_set = set()
        for row in exchange_data['data']:
            exchange_set.add(row['exchange'])
            instrument_set.add(row['instrument'])

        self.assertTrue('binance' in exchange_set, 'binance not in exchanges')
        self.assertTrue('gdax' in exchange_set, 'gdax not in exchanges')
        self.assertTrue('binanceus' in exchange_set, 'binanceus not in exchanges')
        self.assertTrue('btc_usdt' in instrument_set, 'btc_usdt not in instruments')
        self.assertTrue('eth_usdt' in instrument_set, 'eth_usdt not in instruments')
        self.assertTrue('btc_usd' in instrument_set, 'btc_usd not in instruments')
        self.assertTrue('eth_usd' in instrument_set, 'eth_usd not in instruments')

    def test_get_exchanges_information_specific_exchange(self):
        exchange_data = srs.get_exchanges_information(exchanges=[MarketDataVenue.BINANCE, MarketDataVenue.COINBASE])
        self.assertTrue('data' in exchange_data.keys(), 'data not in exchange')
        self.assertTrue(len(exchange_data['data']) > 0, 'no exchanges returned')
        exchange_set = set()
        instrument_set = set()
        for row in exchange_data['data']:
            exchange_set.add(row['exchange'])
            instrument_set.add(row['instrument'])
        self.assertTrue('binance' in exchange_set, 'binance not in exchanges')
        self.assertTrue('gdax' in exchange_set, 'gdax not in exchanges')
        self.assertTrue('btc_usdt' in instrument_set, 'btc_usdt not in instruments')
        self.assertTrue('eth_usdt' in instrument_set, 'eth_usdt not in instruments')
        self.assertTrue('btc_usd' in instrument_set, 'btc_usd not in instruments')
        self.assertTrue('eth_usd' in instrument_set, 'eth_usd not in instruments')

    def test_get_exchanges_information_specific_pair(self):
        exchange_data = srs.get_exchanges_information(instruments=['btc_usdt'])
        self.assertTrue('data' in exchange_data.keys(), 'data not in exchanges')
        self.assertTrue(len(exchange_data['data']) > 0, 'no exchanges returned')
        exchange_set = set()
        for row in exchange_data['data']:
            exchange_set.add(row['exchange'])
        self.assertTrue('binanceus' in exchange_set, 'binanceus not in exchanges')
        self.assertTrue('bitstamp' in exchange_set, 'bitstamp not in exchanges')

        exchange_data = srs.get_exchanges_information(instruments=['avax_usdt', 'avax_usdc'])
        self.assertTrue('data' in exchange_data.keys(), 'data not in exchanges')
        self.assertTrue(len(exchange_data['data']) > 0, 'no exchanges returned')
        exchange_set = set()
        instrument_set = set()
        for row in exchange_data['data']:
            exchange_set.add(row['exchange'])
            instrument_set.add(row['instrument'])
        self.assertTrue('binance' in exchange_set, 'binance not in exchanges')
        self.assertTrue('binanceus' in exchange_set, 'binanceus not in exchanges')
        self.assertTrue('bybit' in exchange_set, 'bybit not in exchanges')
        self.assertTrue('gdax' in exchange_set, 'gdax not in exchanges')
        self.assertTrue('avax_usdc' in instrument_set, 'avax_usdc not in instruments')
        self.assertTrue('avax_usdt' in instrument_set, 'avax_usdt not in instruments')

    def test_get_pairs_vanilla(self):
        pairs_data = srs.get_pairs_information()
        self.assertTrue('data' in pairs_data.keys(), 'data not in pairs')
        self.assertTrue(len(pairs_data['data']) > 0, 'no pairs returned')
        pair_set = set()
        for row in pairs_data['data']:
            pair_set.add(row['pair'])
        self.assertTrue('btc_usd' in pair_set, 'btc_usd not in pairs')
        self.assertTrue('eth_usd' in pair_set, 'eth_usd not in pairs')
        self.assertTrue('btc_usdt' in pair_set, 'btc_usdt not in pairs')
        self.assertTrue('btc_usdc' in pair_set, 'btc_usdc not in pairs')
        self.assertTrue('avax_usdt' in pair_set, 'avax_usdt not in pairs')

    def test_get_pairs_specific_pair(self):
        pairs_data = srs.get_pairs_information(pair='btc_usd')
        self.assertTrue('data' in pairs_data.keys(), 'data not in pair')
        self.assertTrue(len(pairs_data['data']) > 0, 'no pairs returned')
        pair_set = set()
        for row in pairs_data['data']:
            pair_set.add(row['pair'])
        self.assertTrue('btc_usd' in pair_set, 'btc_usd not in pair')

        pairs_data = srs.get_pairs_information(pair='avax_usdt')
        self.assertTrue('data' in pairs_data.keys(), 'data not in pair')
        self.assertTrue(len(pairs_data['data']) > 0, 'no pairs returned')
        pair_set = set()
        for row in pairs_data['data']:
            pair_set.add(row['pair'])
        self.assertTrue('avax_usdt' in pair_set, 'avax_usdt not in pair')

    def test_get_exchanges_reference_vanilla(self):
        reference_data = srs.get_exhanges_reference()
        self.assertTrue('data' in reference_data.keys(), 'data not in reference')
        exchange_set = set()
        binance_instrument_set = set()
        for row in reference_data['data']:
            exchange_set.add(row['exchange'])
            if row['exchange'] == 'binance':
                binance_instrument_set.add(row['instrument'])
        self.assertTrue('binance' in exchange_set, 'exchanges not in reference')
        self.assertTrue('btc_usdt' in binance_instrument_set, 'pairs not in reference')
        self.assertTrue('eth_usdt' in binance_instrument_set, 'pairs not in reference')
        self.assertTrue('avax_usdt' in binance_instrument_set, 'pairs not in reference')

    def test_test_get_exchanges_reference_specific_exchange(self):
        reference_data = srs.get_exhanges_reference(exchanges=[MarketDataVenue.BINANCE, MarketDataVenue.COINBASE])
        self.assertTrue('data' in reference_data.keys(), 'data not in reference')
        exchange_set = set()
        binance_instrument_set = set()
        for row in reference_data['data']:
            exchange_set.add(row['exchange'])
            if row['exchange'] == 'binance':
                binance_instrument_set.add(row['instrument'])
        self.assertTrue('binance' in exchange_set, 'exchanges not in reference')
        self.assertTrue('btc_usdt' in binance_instrument_set, 'pairs not in reference')
        self.assertTrue('eth_usdt' in binance_instrument_set, 'pairs not in reference')
        self.assertTrue('avax_usdt' in binance_instrument_set, 'pairs not in reference')

    def test_test_get_exhanges_reference_specific_pair(self):
        reference_data = srs.get_exhanges_reference(instruments=['btc_usdt', 'avax_usdt'])
        self.assertTrue('data' in reference_data.keys(), 'data not in reference')
        exchange_set = set()
        instrument_set = set()
        for row in reference_data['data']:
            exchange_set.add(row['exchange'])
            instrument_set.add(row['instrument'])
        self.assertTrue('binance' in exchange_set, 'exchanges not in reference')
        self.assertTrue('avax_usdt' in instrument_set, 'pairs not in reference')
        self.assertTrue('btc_usdt' in instrument_set, 'pairs not in reference')

    def test_get_prices_assets_information_raw(self):
        # Test with default parameters
        info = srs.get_prices_assets_information_raw()
        self.assertIsNotNone(info, 'Info is None')
        self.assertGreater(len(info), 0, 'No data returned in info')
        self.assertIn('asset', info.columns, 'Asset column not in info')

        # Test with specific parameters
        info = srs.get_prices_assets_information_raw(asset='btc', time_format=TimeFormat.ISO, include_inactive=True)
        self.assertIsNotNone(info, 'Info is None with parameters')
        self.assertGreater(len(info), 0, 'No data returned in info with parameters')
        self.assertIn('asset', info.columns, 'Asset column not in info with parameters')
        self.assertIn('btc', info['asset'].values, 'BTC not in info with parameters')

        # Test with another set of parameters
        info = srs.get_prices_assets_information_raw(asset='eth', time_format=TimeFormat.HUMAN_READABLE,
                                                     include_inactive=False)
        self.assertIsNotNone(info, 'Info is None with another set of parameters')
        self.assertGreater(len(info), 0, 'No data returned in info with another set of parameters')
        self.assertIn('asset', info.columns, 'Asset column not in info with another set of parameters')
        self.assertIn('eth', info['asset'].values, 'ETH not in info with another set of parameters')

    def test_get_prices_assets_information(self):
        # Test with default parameters
        info = srs.get_prices_assets_information()
        self.assertIsNotNone(info, 'Info is None')
        self.assertGreater(len(info), 0, 'No data returned in info')

        # Test with specific asset
        asset = 'avax'
        info = srs.get_prices_assets_information(asset='avax')
        self.assertIn(asset, info.index.values, f'{asset} not in info')

        # Test with specific parameters
        info = srs.get_prices_assets_information(asset='btc', time_format=TimeFormat.ISO, include_inactive=True)
        self.assertIsNotNone(info, 'Info is None with parameters')
        self.assertGreater(len(info), 0, 'No data returned in info with parameters')
        self.assertIn('btc', info.index.values, 'BTC not in info with parameters')

        # Test with another set of parameters
        info = srs.get_prices_assets_information(asset='eth', time_format=TimeFormat.HUMAN_READABLE,
                                                 include_inactive=False)
        self.assertIsNotNone(info, 'Info is None with another set of parameters')
        self.assertGreater(len(info), 0, 'No data returned in info with another set of parameters')
        self.assertIn('eth', info.index.values, 'ETH not in info with another set of parameters')

    def test_get_prices_assets_latest_raw(self):
        asset = 'avax'
        latest = srs.get_prices_assets_latest_raw(asset)
        self.assertTrue(latest is not None, 'latest is None')
        self.assertTrue(len(latest) == 1, 'Unexpected data returned in latest')
        self.assertTrue('asset' in latest.columns.values, 'asset not in latest columns')
        self.assertTrue('price' in latest.columns.values, 'price not in latest columns')
        self.assertTrue('timestamp' in latest.columns.values, 'timestamp not in latest columns')
        self.assertTrue(type(latest.loc[0, 'asset']) == str, f'asset is not a string {type(latest.loc[0, "asset"])}')
        self.assertTrue(type(latest.loc[0, 'price']) == numpy.float64,
                        f'price is not a float but {type(latest.loc[0, "price"])}')
        self.assertTrue(type(latest.loc[0, 'timestamp']) == numpy.int64,
                        f'timestamp is not an int but {type(latest.loc[0, "timestamp"])}')

    def test_get_prices_assets_latest(self):
        asset = 'avax'
        latest = srs.get_prices_assets_latest(asset)
        self.assertTrue(latest is not None, 'latest is None')
        self.assertTrue(len(latest) == 1, 'Unexpected data returned in latest')
        self.assertTrue('avax' in latest.index, 'avax not in latest')
        self.assertTrue(type(latest.loc['avax', 'price']) == numpy.float64,
                        f'price is not a float but {type(latest.loc["avax", "price"])}')
        self.assertTrue(type(latest.loc['avax', 'timestamp']) == numpy.int64,
                        f'timestamp is not an int but {type(latest.loc["avax", "timestamp"])}')

    def test_get_prices_pairs_historical_raw_vanilla(self):
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()
        pair = 'btc_usdt'
        result = srs.get_prices_pairs_historical_raw(pair, start_date=start_date, end_date=end_date)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertIn('timestamp', result.columns, "timestamp not in columns")
        self.assertIn('price', result.columns, "price not in columns")

    def test_get_prices_pairs_historical_raw_with_exchanges(self):
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()
        pair = 'btc_usdt'
        exchange = MarketDataVenue.BINANCE
        result = srs.get_prices_pairs_historical_raw(pair, exchange=exchange, start_date=start_date, end_date=end_date)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertIn('timestamp', result.columns, "timestamp not in columns")
        self.assertIn('price', result.columns, "price not in columns")

    def test_get_prices_pairs_historical_raw_with_time_interval(self):
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()
        pair = 'btc_usdt'
        result = srs.get_prices_pairs_historical_raw(pair, start_date=start_date, end_date=end_date,
                                                     time_interval=TimeInterval.HOUR)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertIn('timestamp', result.columns, "timestamp not in columns")
        self.assertIn('price', result.columns, "price not in columns")

    def test_get_prices_pairs_historical_raw_parallel_execution(self):
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()
        pair = 'btc_usdt'
        result = srs.get_prices_pairs_historical_raw(pair, start_date=start_date, end_date=end_date,
                                                     parallel_execution=True)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertIn('timestamp', result.columns, "timestamp not in columns")
        self.assertIn('price', result.columns, "price not in columns")

    def test_get_prices_pairs_historical_raw_with_batch_period(self):
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()
        pair = 'btc_usdt'
        batch_period = timedelta(hours=1)
        result = srs.get_prices_pairs_historical_raw(pair, start_date=start_date, end_date=end_date,
                                                     batch_period=batch_period)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertIn('timestamp', result.columns, "timestamp not in columns")
        self.assertIn('price', result.columns, "price not in columns")

    def test_get_prices_pairs_historical_vanilla(self):
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()
        pair = 'btc_usdt'
        result = srs.get_prices_pairs_historical(pair, start_date=start_date, end_date=end_date)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['pair', 'timestamp'], "Index keys are not as expected")

    def test_get_prices_pairs_historical_with_exchanges(self):
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()
        pair = 'btc_usdt'
        exchange = MarketDataVenue.BINANCE
        result = srs.get_prices_pairs_historical(pair, exchanges=exchange, start_date=start_date, end_date=end_date)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['pair', 'timestamp'], "Index keys are not as expected")

    def test_get_prices_pairs_historical_with_time_interval(self):
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()
        pair = 'btc_usdt'
        result = srs.get_prices_pairs_historical(pair, start_date=start_date, end_date=end_date,
                                                 time_interval=TimeInterval.HOUR)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['pair', 'timestamp'], "Index keys are not as expected")

    def test_get_prices_pairs_historical_with_batch_period(self):
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()
        pair = 'btc_usdt'
        batch_period = timedelta(hours=1)
        result = srs.get_prices_pairs_historical(pair, start_date=start_date, end_date=end_date,
                                                 batch_period=batch_period)
        self.assertIsInstance(result, pd.DataFrame)

    ''' TODO: Disabled as these tsts can't work if the API key isnt provisioned for this feature
    def test_get_reference_rates_pairs_historical_raw_vanilla(self):
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()
        pair = 'btc_usdt'
        result = srs.get_reference_rates_raw(pair, start_date, end_date)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertIn('timestamp', result.columns, "timestamp not in columns")
        self.assertIn('price', result.columns, "price not in columns")

    def test_get_reference_rates_pairs_historical_raw_with_sources(self):
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()
        pair = 'btc_usdt'
        result = srs.get_reference_rates_raw(pair, start_date, end_date)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertIn('timestamp', result.columns, "timestamp not in columns")
        self.assertIn('price', result.columns, "price not in columns")

    def test_get_reference_rates_pairs_historical_raw_with_include_sources(self):
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()
        pair = 'btc_usdt'
        include_sources = True
        result = srs.get_reference_rates_raw(pair, start_date, end_date)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertIn('timestamp', result.columns, "timestamp not in columns")
        self.assertIn('price', result.columns, "price not in columns")

    def test_get_reference_rates_pairs_historical_raw_parallel_execution(self):
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()
        pair = 'btc_usdt'
        result = srs.get_reference_rates_raw(pair, start_date, end_date, parallel_execution=True)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertIn('timestamp', result.columns, "timestamp not in columns")
        self.assertIn('price', result.columns, "price not in columns")

    def test_get_reference_rates_pairs_historical_raw_with_batch_period(self):
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()
        pair = 'btc_usdt'
        batch_period = timedelta(hours=1)
        result = srs.get_reference_rates_raw(pair, start_date, end_date, batch_period=batch_period)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertIn('timestamp', result.columns, "timestamp not in columns")
        self.assertIn('price', result.columns, "price not in columns")

    def test_get_reference_rates_pairs_historical_vanilla(self):
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()
        pair = 'btc_usdt'
        result = srs.get_reference_rates(pair, start_date, end_date)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['pair', 'timestamp'], "Index keys are not as expected")

    def test_get_reference_rates_pairs_historical_with_sources(self):
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()
        pair = 'btc_usdt'
        sources = [MarketDataVenue.BINANCE, MarketDataVenue.COINBASE]
        result = srs.get_reference_rates(pair, start_date, end_date)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['pair', 'timestamp'], "Index keys are not as expected")

    def test_get_reference_rates_pairs_historical_with_include_sources(self):
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()
        pair = 'btc_usdt'
        include_sources = True
        result = srs.get_reference_rates(pair, start_date, end_date)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['pair', 'timestamp'], "Index keys are not as expected")

    def test_get_reference_rates_pairs_historical_with_batch_period(self):
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()
        pair = 'btc_usdt'
        batch_period = timedelta(hours=1)
        result = srs.get_reference_rates(pair, start_date, end_date, batch_period=batch_period)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['pair', 'timestamp'], "Index keys are not as expected")

    def test_get_reference_rates_pairs_historical_with_custom_index_keys(self):
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()
        pair = 'btc_usdt'
        index_keys = ['timestamp']
        result = srs.get_reference_rates(pair, start_date, end_date, index_keys=index_keys)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['timestamp'], "Index keys are not as expected")
    '''

    def test_get_ticker_information_raw_vanilla(self):
        info = srs.get_ticker_information_raw()
        self.assertIsInstance(info, pd.DataFrame)
        self.assertFalse(info.empty, "DataFrame is empty")
        self.assertIn('exchange', info.columns, "Exchange column not in info")

    def test_get_ticker_information_with_params(self):
        info = srs.get_ticker_information(exchanges=[MarketDataVenue.BINANCE], include_inactive=True,
                                          time_format=TimeFormat.ISO)
        self.assertIsInstance(info, pd.DataFrame)
        self.assertFalse(info.empty, "DataFrame is empty")
        if 'exchange' in info.index.names:
            self.assertIn('binance', info.index.get_level_values('exchange').values, "binance not in info")
        else:
            self.fail("Exchange column not in info")

    def test_get_historical_ticker_raw_vanilla(self):
        instrument = 'eth_usd'
        result = srs.get_historical_ticker_raw(instrument, exchange=MarketDataVenue.GDAX)
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')

    def test_get_historical_ticker_raw_parallel_execution(self):
        instrument = 'eth_usd'
        exchange = MarketDataVenue.GDAX
        start_date = datetime(2024, 8, 1, 10, 0, 0)  # June 1, 2023, 10:00:00 AM
        end_date = datetime(2024, 8, 1, 12, 0, 0)  # June 1, 2023, 12:00:00 PM
        batch_period = BatchPeriod.HOUR_1

        # Get results with parallel execution
        parallel_result = srs.get_historical_ticker_raw(
            instrument=instrument,
            exchange=exchange,
            start_date=start_date,
            end_date=end_date,
            batch_period=batch_period,
            parallel_exec=True
        )

        # Get results without parallel execution
        sequential_result = srs.get_historical_ticker_raw(
            instrument=instrument,
            exchange=exchange,
            start_date=start_date,
            end_date=end_date,
            batch_period=batch_period,
            parallel_exec=False
        )

        # Check that both results are not None and not empty
        self.assertIsNotNone(parallel_result, 'Parallel result is None')
        self.assertIsNotNone(sequential_result, 'Sequential result is None')
        self.assertFalse(parallel_result.empty, 'Parallel result is empty')
        self.assertFalse(sequential_result.empty, 'Sequential result is empty')

        # Check that both results have the same shape
        self.assertEqual(parallel_result.shape, sequential_result.shape, 'Results have different shapes')

        # Check that both results have the same columns
        self.assertListEqual(list(parallel_result.columns), list(sequential_result.columns),
                             'Results have different columns')

        # Check that both results have the same data (ignoring order)
        pd.testing.assert_frame_equal(parallel_result.sort_values(by=['exchangeTimestamp']).reset_index(drop=True),
                                      sequential_result.sort_values(by=['exchangeTimestamp']).reset_index(drop=True),
                                      check_like=True)

    def test_get_order_book_information_raw_vanilla(self):
        result = srs.get_order_book_information_raw()
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')

    def test_get_order_book_information_vanilla(self):
        result = srs.get_order_book_information()
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertTrue('exchange' in result.index.names, 'exchange not in index')
        self.assertTrue('instrument' in result.index.names, 'instrument not in index')

    def test_get_order_book_information_raw_with_params(self):
        result = srs.get_order_book_information_raw(
            exchanges=[MarketDataVenue.BITFINEX],
            include_inactive=True,
            time_format=TimeFormat.ISO
        )
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertIn('exchange', result.columns, 'exchange not in columns')
        self.assertIn('instrument', result.columns, 'instrument not in columns')
        self.assertIn('startDate', result.columns, 'startDate not in columns')
        self.assertIn('endDate', result.columns, 'endDate not in columns')
        self.assertIn('address', result.columns, 'address not in columns')

    def test_get_order_book_information_with_params(self):
        result = srs.get_order_book_information(
            exchanges=[MarketDataVenue.BITFINEX],
            include_inactive=True,
            time_format=TimeFormat.ISO,
            index_keys=['exchange', 'instrument']
        )
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertTrue('exchange' in result.index.names, 'exchange not in index')
        self.assertTrue('instrument' in result.index.names, 'instrument not in index')

    def test_get_order_book_information_raw_with_exchanges(self):
        result = srs.get_order_book_information_raw(
            exchanges=[MarketDataVenue.BITFINEX, MarketDataVenue.BITSTAMP]
        )
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')

    def test_get_order_book_information_with_exchanges(self):
        result = srs.get_order_book_information(
            exchanges=[MarketDataVenue.BITFINEX, MarketDataVenue.BITSTAMP],
            index_keys=['exchange', 'instrument']
        )
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertTrue('exchange' in result.index.names, 'exchange not in index')
        self.assertTrue('instrument' in result.index.names, 'instrument not in index')

    def test_get_order_book_information_raw_include_inactive(self):
        result = srs.get_order_book_information_raw(include_inactive=True)
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')

    def test_get_order_book_information_include_inactive(self):
        result = srs.get_order_book_information(include_inactive=True)
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertTrue('exchange' in result.index.names, 'exchange not in index')
        self.assertTrue('instrument' in result.index.names, 'instrument not in index')

    def test_get_order_book_snapshots_historical_raw_vanilla(self):
        result = srs.get_order_book_snapshots_historical_raw('eth_usd', MarketDataVenue.BITFINEX)
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')

    def test_get_order_book_snapshots_historical_vanilla(self):
        result = srs.get_order_book_snapshots_historical('eth_usd', MarketDataVenue.BITFINEX)
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertIn('bid', result.columns, 'bid not in columns')
        self.assertIn('ask', result.columns, 'ask not in columns')

    def test_get_order_book_snapshots_historical_raw_with_params(self):
        start_date = datetime(2024, 7, 15, 0, 0, 0)
        end_date = datetime(2024, 7, 15, 0, 15, 0)
        result = srs.get_order_book_snapshots_historical_raw(
            'eth_usdt', MarketDataVenue.BINANCE, start_date=start_date, end_date=end_date, max_level=10
        )
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')

    def test_get_order_book_snapshots_historical_with_params(self):
        start_date = datetime(2024, 7, 15, 0, 0, 0)
        end_date = datetime(2024, 7, 15, 0, 15, 0)
        result = srs.get_order_book_snapshots_historical(
            'eth_usdt', MarketDataVenue.BINANCE, start_date=start_date, end_date=end_date, max_level=10
        )
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertIn('bid', result.columns, 'bid not in columns')
        self.assertIn('ask', result.columns, 'ask not in columns')

    def test_get_order_book_events_historical_raw_vanilla(self):
        start_date = datetime.fromisoformat("2024-03-01T00:00:00")
        end_date = datetime.fromisoformat("2024-03-01T01:00:00")
        result = srs.get_order_book_events_historical_raw('btc_usd', MarketDataVenue.GDAX, start_date=start_date,
                                                          end_date=end_date)
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')

    def test_get_order_book_events_historical_vanilla(self):
        start_date = datetime.fromisoformat("2024-03-01T00:00:00")
        end_date = datetime.fromisoformat("2024-03-01T01:00:00")
        result = srs.get_order_book_events_historical('btc_usd', MarketDataVenue.GDAX, start_date=start_date,
                                                      end_date=end_date)
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertIn('price', result.columns, 'price not in columns')
        self.assertIn('volume', result.columns, 'volume not in columns')
        self.assertIn('numOrders', result.columns, 'numOrders not in columns')

    def test_get_order_book_events_historical_raw_with_params(self):
        start_date = datetime(2024, 3, 1, 0, 0, 0)
        end_date = datetime(2024, 3, 1, 0, 1, 0)
        result = srs.get_order_book_events_historical_raw(
            'btc_usd', MarketDataVenue.GDAX, start_date=start_date, end_date=end_date
        )
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')

    def test_get_order_book_events_historical_with_params(self):
        start_date = datetime(2024, 3, 1, 0, 0, 0)
        end_date = datetime(2024, 3, 1, 0, 1, 0)
        result = srs.get_order_book_events_historical(
            'btc_usd', MarketDataVenue.GDAX, start_date=start_date, end_date=end_date
        )
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertIn('price', result.columns, 'price not in columns')
        self.assertIn('volume', result.columns, 'volume not in columns')
        self.assertIn('numOrders', result.columns, 'numOrders not in columns')

    def test_get_trades_information_raw_vanilla(self):
        result = srs.get_trades_information_raw()
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')

    def test_get_trades_information_vanilla(self):
        result = srs.get_trades_information()
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertTrue('exchange' in result.index.names, 'exchange not in index')
        self.assertTrue('instrument' in result.index.names, 'instrument not in index')

    def test_get_trades_historical_raw_vanilla(self):
        instrument = 'eth_usd'
        exchange = MarketDataVenue.GDAX
        result = srs.get_trades_historical_raw(instrument, exchange)
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')

    def test_get_trades_historical_raw_parallel_execution(self):
        instrument = 'btc_usd'
        exchange = MarketDataVenue.GDAX
        start_date = datetime(2024, 3, 1, 0, 0)
        end_date = datetime(2024, 3, 1, 2, 0)
        batch_period = timedelta(hours=1)

        # Execute without parallelization
        start_time = time.time()
        result_sequential = srs.get_trades_historical_raw(
            instrument, exchange, start_date, end_date,
            batch_period=batch_period, parallel_execution=False
        )
        sequential_time = time.time() - start_time

        # Execute with parallelization
        start_time = time.time()
        result_parallel = srs.get_trades_historical_raw(
            instrument, exchange, start_date, end_date,
            batch_period=batch_period, parallel_execution=True
        )
        parallel_time = time.time() - start_time

        # Assert that both results are not None and not empty
        self.assertIsNotNone(result_sequential, 'Sequential result is None')
        self.assertIsNotNone(result_parallel, 'Parallel result is None')
        self.assertFalse(result_sequential.empty, 'Sequential result is empty')
        self.assertFalse(result_parallel.empty, 'Parallel result is empty')

        # Assert that both results have the same shape and content
        self.assertEqual(result_sequential.shape, result_parallel.shape,
                         'Sequential and parallel results have different shapes')
        # Check that the column values are the same of the two dataframes, index is not important
        pd.testing.assert_frame_equal(
            result_sequential.sort_values(['exchangeTimestamp', 'exchangeTimestampNanoseconds']),
            result_sequential.sort_values(['exchangeTimestamp', 'exchangeTimestampNanoseconds']),
            check_dtype=False, check_exact=False, check_index_type=False)

        # Print execution times for reference
        print(f"Sequential execution time: {sequential_time:.2f} seconds")
        print(f"Parallel execution time: {parallel_time:.2f} seconds")

    def test_get_trades_historical_vanilla(self):
        instrument = 'eth_usd'
        exchange = MarketDataVenue.GDAX
        result = srs.get_trades_historical(instrument, exchange)
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertIn('price', result.columns, 'price not in columns')
        self.assertIn('volume', result.columns, 'volume not in columns')

    def test_get_trades_historical_raw_with_params(self):
        instrument = 'eth_usd'
        exchange = MarketDataVenue.GDAX
        start_date = datetime(2024, 3, 1, 0, 0)
        end_date = datetime(2024, 3, 1, 1, 0)
        result = srs.get_trades_historical_raw(instrument, exchange, start_date, end_date)
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')

    def test_get_trades_historical_with_params(self):
        instrument = 'eth_usd'
        exchange = MarketDataVenue.GDAX
        start_date = datetime(2024, 3, 1, 0, 0)
        end_date = datetime(2024, 3, 1, 1, 0)
        result = srs.get_trades_historical(instrument, exchange, start_date, end_date)
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertIn('price', result.columns, 'price not in columns')
        self.assertIn('volume', result.columns, 'volume not in columns')

    def test_get_ohlcv_information_raw_vanilla(self):
        result = srs.get_ohlcv_information_raw()
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')

    def test_get_ohlcv_information_raw_with_params(self):
        result = srs.get_ohlcv_information_raw(exchanges=[MarketDataVenue.BITFINEX])
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')

    def test_get_ohlcv_information_vanilla(self):
        result = srs.get_ohlcv_information()
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertTrue('exchange' in result.index.names, 'exchange not in index')
        self.assertTrue('pair' in result.index.names, 'pair not in index')

    def test_get_ohlcv_information_with_params(self):
        result = srs.get_ohlcv_information(exchanges=[MarketDataVenue.BITFINEX, MarketDataVenue.BINANCE])
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertTrue('exchange' in result.index.names, 'exchange not in index')
        self.assertTrue('pair' in result.index.names, 'pair not in index')

    def test_get_ohlcv_historical_raw_vanilla(self):
        result = srs.get_ohlcv_historical_raw(instrument='eth_usdt',
                                              exchanges=[MarketDataVenue.BINANCE, MarketDataVenue.BYBIT])
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertIn('timestamp', result.columns, 'timestamp column is missing')
        self.assertIn('open', result.columns, 'open column is missing')
        self.assertIn('high', result.columns, 'high column is missing')
        self.assertIn('low', result.columns, 'low column is missing')
        self.assertIn('close', result.columns, 'close column is missing')
        self.assertIn('volume', result.columns, 'volume column is missing')
        self.assertIn('exchange', result.columns, 'exchange column is missing')

    def test_get_ohlcv_historical_raw_with_params(self):
        try:
            result = srs.get_ohlcv_historical_raw(
                instrument='btc_usdt',
                exchanges=[MarketDataVenue.BINANCE],
                start_date=datetime(2023, 1, 1, 0, 0),
                end_date=datetime(2023, 2, 1, 0, 0),
                time_interval=TimeInterval.DAY,
                time_format=TimeFormat.ISO
            )
            self.assertIsNotNone(result, 'result is None')
            self.assertFalse(result.empty, 'result is empty')
            self.assertIn('timestamp', result.columns, 'timestamp column is missing')
            self.assertIn('open', result.columns, 'open column is missing')
            self.assertIn('high', result.columns, 'high column is missing')
            self.assertIn('low', result.columns, 'low column is missing')
            self.assertIn('close', result.columns, 'close column is missing')
            self.assertIn('volume', result.columns, 'volume column is missing')
            self.assertIn('exchange', result.columns, 'exchange column is missing')
            self.assertTrue((result['exchange'] == 'binance').all(),
                            'Returned exchange does not match the requested exchange')
        except NoDataReturned as e:
            logging.error(f"No data returned: {str(e)}")
            raise e
        except Exception as e:
            logging.error(f"Test failed: {str(e)}")
            raise e

    def test_get_ohlcv_historical_vanilla(self):
        result = srs.get_ohlcv_historical(instrument='eth_usdt',
                                          exchanges=[MarketDataVenue.BINANCE, MarketDataVenue.BYBIT])
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertTrue('exchange' in result.index.names, 'exchange not in index')
        self.assertTrue('timestamp' in result.index.names, 'timestamp not in index')

    def test_get_ohlcv_historical_with_params(self):
        result = srs.get_ohlcv_historical(instrument='eth_usd', exchanges=[MarketDataVenue.BITFINEX],
                                          start_date=datetime(2023, 1, 1, 0, 0),
                                          end_date=datetime(2023, 2, 1, 0, 0),
                                          time_interval=TimeInterval.DAY, time_format=TimeFormat.ISO)
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertTrue('exchange' in result.index.names, 'exchange not in index')
        self.assertTrue('timestamp' in result.index.names, 'timestamp not in index')
        self.assertTrue(result.index.get_level_values('exchange').isin(['bitfinex']).all(),
                        'Returned exchange does not match the requested exchange')

    def test_get_ohlcv_by_exchange_historical_raw_vanilla(self):
        result = srs.get_ohlcv_by_exchange_historical_raw(exchange=[MarketDataVenue.BINANCE], pairs=['btc_usdt',
                                                                                                     'eth_usdt'])
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertIn('timestamp', result.columns, 'timestamp column is missing')
        self.assertIn('open', result.columns, 'open column is missing')
        self.assertIn('high', result.columns, 'high column is missing')
        self.assertIn('low', result.columns, 'low column is missing')
        self.assertIn('close', result.columns, 'close column is missing')
        self.assertIn('volume', result.columns, 'volume column is missing')
        self.assertIn('exchange', result.columns, 'exchange column is missing')
        self.assertIn('pair', result.columns, 'pair column is missing')

    def test_get_ohlcv_by_exchange_historical_raw_with_params(self):
        result = srs.get_ohlcv_by_exchange_historical_raw(exchange=[MarketDataVenue.BINANCE],
                                                          pairs=['btc_usdt', 'eth_usdt'],
                                                          start_date=datetime(2023, 1, 1, 0, 0),
                                                          end_date=datetime(2023, 2, 1, 0, 0),
                                                          time_interval=TimeInterval.HOUR, time_format=TimeFormat.ISO)
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertIn('timestamp', result.columns, 'timestamp column is missing')
        self.assertIn('open', result.columns, 'open column is missing')
        self.assertIn('high', result.columns, 'high column is missing')
        self.assertIn('low', result.columns, 'low column is missing')
        self.assertIn('close', result.columns, 'close column is missing')
        self.assertIn('volume', result.columns, 'volume column is missing')
        self.assertIn('exchange', result.columns, 'exchange column is missing')
        self.assertIn('pair', result.columns, 'pair column is missing')
        self.assertTrue((result['exchange'] == 'binance').all(),
                        'Returned exchange does not match the requested exchange')
        self.assertTrue(result['pair'].isin(['btc_usdt', 'eth_usdt']).all(),
                        'Returned pairs do not match the requested pairs')

    def test_get_ohlcv_by_exchange_historical_vanilla(self):
        result = srs.get_ohlcv_by_exchange_historical(exchange=[MarketDataVenue.BINANCE],
                                                      pairs=['btc_usdt', 'eth_usdt'])
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertTrue('exchange' in result.index.names, 'exchange not in index')
        self.assertTrue('pair' in result.index.names, 'pair not in index')
        self.assertTrue('timestamp' in result.index.names, 'timestamp not in index')

    def test_get_ohlcv_by_exchange_historical_with_params(self):
        result = srs.get_ohlcv_by_exchange_historical(exchange=[MarketDataVenue.BINANCE],
                                                      pairs=['btc_usdt', 'eth_usdt'],
                                                      start_date=datetime(2023, 1, 1, 0, 0),
                                                      end_date=datetime(2023, 2, 1, 0, 0),
                                                      time_interval=TimeInterval.DAY, time_format=TimeFormat.ISO)
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertTrue('exchange' in result.index.names, 'exchange not in index')
        self.assertTrue('pair' in result.index.names, 'pair not in index')
        self.assertTrue('timestamp' in result.index.names, 'timestamp not in index')
        self.assertTrue(result.index.get_level_values('exchange').isin(['binance']).all(),
                        'Returned exchange does not match the requested exchange')
        self.assertTrue(result.index.get_level_values('pair').isin(['btc_usdt', 'eth_usdt']).all(),
                        'Returned pairs do not match the requested pairs')

    def test_get_twap_assets_information_raw_vanilla(self):
        result = srs.get_twap_assets_information_raw()
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertIn('asset', result.columns, 'asset column is missing')
        self.assertIn('startDate', result.columns, 'startDate column is missing')
        self.assertIn('endDate', result.columns, 'endDate column is missing')
        self.assertIn('exchange', result.columns, 'exchange column is missing')
        self.assertIn('assetSymbol', result.columns, 'assetSymbol column is missing')

    def test_get_twap_assets_information_raw_with_params(self):
        result = srs.get_twap_assets_information_raw(asset='btc', time_format=TimeFormat.ISO)
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertIn('asset', result.columns, 'asset column is missing')
        self.assertIn('startDate', result.columns, 'startDate column is missing')
        self.assertIn('endDate', result.columns, 'endDate column is missing')
        self.assertIn('exchange', result.columns, 'exchange column is missing')
        self.assertIn('assetSymbol', result.columns, 'assetSymbol column is missing')
        self.assertTrue((result['asset'] == 'btc').all(), 'Returned asset does not match the requested asset')

    def test_get_twap_assets_information_vanilla(self):
        result = srs.get_twap_assets_information()
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertTrue('asset' in result.index.names, 'asset not in index')
        self.assertTrue('exchange' in result.index.names, 'exchange not in index')

    def test_get_twap_assets_information_with_params(self):
        result = srs.get_twap_assets_information(asset='btc', time_format=TimeFormat.ISO)
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertTrue('asset' in result.index.names, 'asset not in index')
        self.assertTrue('exchange' in result.index.names, 'exchange not in index')
        self.assertTrue(result.index.get_level_values('asset').isin(['btc']).all(),
                        'Returned asset does not match the requested asset')

    def test_get_twap_asset_latest_raw_vanilla(self):
        result = srs.get_twap_asset_latest_raw(asset='btc')
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertIn('timestamp', result.columns, 'timestamp column is missing')
        self.assertIn('asset', result.columns, 'asset column is missing')
        self.assertIn('price', result.columns, 'price column is missing')
        self.assertIn('twap', result.columns, 'twap column is missing')
        self.assertIn('volume', result.columns, 'volume column is missing')

    def test_get_twap_asset_latest_vanilla(self):
        result = srs.get_twap_asset_latest(asset='btc')
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertTrue('asset' in result.index.names, 'asset not in index')
        self.assertTrue('timestamp' in result.index.names, 'timestamp not in index')

    def test_get_twap_asset_historical_raw_vanilla(self):
        result = srs.get_twap_asset_historical_raw(asset='btc')
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertIn('timestamp', result.columns, 'timestamp column is missing')
        self.assertIn('asset', result.columns, 'asset column is missing')
        self.assertIn('price', result.columns, 'price column is missing')
        self.assertIn('twap', result.columns, 'twap column is missing')
        self.assertIn('volume', result.columns, 'volume column is missing')

    def test_get_twap_asset_historical_raw_with_params(self):
        start_date = datetime(2023, 6, 1, 0, 0, 0)
        end_date = datetime(2023, 6, 2, 0, 0, 0)
        result = srs.get_twap_asset_historical_raw(asset='btc', start_date=start_date, end_date=end_date,
                                                   time_interval=TimeInterval.HOUR, lookback_period=24,
                                                   time_format=TimeFormat.ISO)
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertIn('timestamp', result.columns, 'timestamp column is missing')
        self.assertIn('asset', result.columns, 'asset column is missing')
        self.assertIn('price', result.columns, 'price column is missing')
        self.assertIn('twap', result.columns, 'twap column is missing')
        self.assertIn('volume', result.columns, 'volume column is missing')
        self.assertTrue((result['asset'] == 'btc').all(), 'Returned asset does not match the requested asset')

    def test_get_twap_asset_historical_vanilla(self):
        result = srs.get_twap_asset_historical(asset='btc')
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertTrue('asset' in result.index.names, 'asset not in index')
        self.assertTrue('timestamp' in result.index.names, 'timestamp not in index')

    def test_get_twap_asset_historical_with_params(self):
        start_date = datetime(2023, 6, 1, 0, 0, 0)
        end_date = datetime(2023, 6, 2, 0, 0, 0)
        result = srs.get_twap_asset_historical(asset='btc', start_date=start_date, end_date=end_date,
                                               time_interval=TimeInterval.HOUR, lookback_period=24,
                                               time_format=TimeFormat.ISO)
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertTrue('asset' in result.index.names, 'asset not in index')
        self.assertTrue('timestamp' in result.index.names, 'timestamp not in index')
        self.assertTrue(result.index.get_level_values('asset').isin(['btc']).all(),
                        'Returned asset does not match the requested asset')

    def test_get_twap_pairs_information_raw_vanilla(self):
        result = srs.get_twap_pairs_information_raw()
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertIn('pair', result.columns, 'pair column is missing')
        self.assertIn('startDate', result.columns, 'startDate column is missing')
        self.assertIn('endDate', result.columns, 'endDate column is missing')

    def test_get_twap_pairs_information_raw_with_params(self):
        result = srs.get_twap_pairs_information_raw(pair='btc_usd', time_format=TimeFormat.ISO)
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertIn('pair', result.columns, 'pair column is missing')
        self.assertIn('startDate', result.columns, 'startDate column is missing')
        self.assertIn('endDate', result.columns, 'endDate column is missing')
        self.assertTrue((result['pair'] == 'btc_usd').all(), 'Returned pair does not match the requested pair')

    def test_get_twap_pairs_information_vanilla(self):
        result = srs.get_twap_pairs_information()
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertTrue('pair' in result.index.names, 'pair not in index')

    def test_get_twap_pairs_information_with_params(self):
        result = srs.get_twap_pairs_information(pair='btc_usd', time_format=TimeFormat.ISO)
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertTrue('pair' in result.index.names, 'pair not in index')
        self.assertTrue(result.index.get_level_values('pair').isin(['btc_usd']).all(),
                        'Returned pair does not match the requested pair')

    def test_get_twap_pairs_latest_raw_vanilla(self):
        result = srs.get_twap_pairs_latest_raw(pair='btc_usd')
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertIn('timestamp', result.columns, 'timestamp column is missing')
        self.assertIn('pair', result.columns, 'pair column is missing')
        self.assertIn('price', result.columns, 'price column is missing')
        self.assertIn('twap', result.columns, 'twap column is missing')
        self.assertIn('volume', result.columns, 'volume column is missing')

    def test_get_twap_pairs_latest_vanilla(self):
        result = srs.get_twap_pairs_latest(pair='btc_usd')
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertTrue('pair' in result.index.names, 'pair not in index')
        self.assertTrue('timestamp' in result.index.names, 'timestamp not in index')

    def test_get_twap_pairs_historical_raw_vanilla(self):
        result = srs.get_twap_pairs_historical_raw(pair='btc_usd')
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertIn('timestamp', result.columns, 'timestamp column is missing')
        self.assertIn('pair', result.columns, 'pair column is missing')
        self.assertIn('price', result.columns, 'price column is missing')
        self.assertIn('twap', result.columns, 'twap column is missing')
        self.assertIn('volume', result.columns, 'volume column is missing')

    def test_get_twap_pairs_historical_raw_with_params(self):
        start_date = datetime(2024, 1, 1, 0, 0)
        end_date = datetime(2024, 1, 2, 0, 0)
        result = srs.get_twap_pairs_historical_raw(pair='btc_usd', exchange=MarketDataVenue.BITFINEX,
                                                   start_date=start_date, end_date=end_date,
                                                   time_interval=TimeInterval.HOUR, time_format=TimeFormat.ISO)
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertIn('timestamp', result.columns, 'timestamp column is missing')
        self.assertIn('pair', result.columns, 'pair column is missing')
        self.assertIn('price', result.columns, 'price column is missing')
        self.assertIn('twap', result.columns, 'twap column is missing')
        self.assertIn('volume', result.columns, 'volume column is missing')
        self.assertTrue((result['pair'] == 'btc_usd').all(), 'Returned pair does not match the requested pair')

    def test_get_twap_pairs_historical_vanilla(self):
        result = srs.get_twap_pairs_historical(pair='btc_usd')
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertTrue('pair' in result.index.names, 'pair not in index')
        self.assertTrue('timestamp' in result.index.names, 'timestamp not in index')

    def test_get_twap_pairs_historical_with_params(self):
        start_date = datetime(2024, 1, 1, 0, 0)
        end_date = datetime(2024, 1, 2, 0, 0)
        result = srs.get_twap_pairs_historical(pair='btc_usd', exchange=MarketDataVenue.BITFINEX,
                                               start_date=start_date, end_date=end_date,
                                               time_interval=TimeInterval.HOUR, time_format=TimeFormat.ISO)
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertTrue('pair' in result.index.names, 'pair not in index')
        self.assertTrue('timestamp' in result.index.names, 'timestamp not in index')
        self.assertTrue(result.index.get_level_values('pair').isin(['btc_usd']).all(),
                        'Returned pair does not match the requested pair')

    def test_get_vwap_assets_information_raw_vanilla(self):
        result = srs.get_vwap_assets_information_raw()
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertIn('asset', result.columns, 'asset column is missing')
        self.assertIn('startDate', result.columns, 'startDate column is missing')
        self.assertIn('endDate', result.columns, 'endDate column is missing')
        self.assertIn('assetSymbol', result.columns, 'assetSymbol column is missing')
        self.assertIn('exchange', result.columns, 'exchange column is missing')

    def test_get_vwap_assets_information_raw_with_params(self):
        result = srs.get_vwap_assets_information_raw(asset='btc', time_format=TimeFormat.ISO)
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertIn('asset', result.columns, 'asset column is missing')
        self.assertIn('startDate', result.columns, 'startDate column is missing')
        self.assertIn('endDate', result.columns, 'endDate column is missing')
        self.assertIn('assetSymbol', result.columns, 'assetSymbol column is missing')
        self.assertIn('exchange', result.columns, 'exchange column is missing')
        self.assertTrue((result['asset'] == 'btc').all(), 'Returned asset does not match the requested asset')

    def test_get_vwap_assets_information_vanilla(self):
        result = srs.get_vwap_assets_information()
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertTrue('asset' in result.index.names, 'asset not in index')
        self.assertTrue('exchange' in result.index.names, 'exchange not in index')

    def test_get_vwap_assets_information_with_params(self):
        result = srs.get_vwap_assets_information(asset='btc', time_format=TimeFormat.ISO)
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertTrue('asset' in result.index.names, 'asset not in index')
        self.assertTrue('exchange' in result.index.names, 'exchange not in index')
        self.assertTrue(result.index.get_level_values('asset').isin(['btc']).all(),
                        'Returned asset does not match the requested asset')

    def test_get_vwap_asset_latest_raw_vanilla(self):
        result = srs.get_vwap_asset_latest_raw(asset='btc')
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertIn('timestamp', result.columns, 'timestamp column is missing')
        self.assertIn('asset', result.columns, 'asset column is missing')
        self.assertIn('price', result.columns, 'price column is missing')
        self.assertIn('vwap', result.columns, 'vwap column is missing')
        self.assertIn('volume', result.columns, 'volume column is missing')

    def test_get_vwap_asset_latest_with_params(self):
        result = srs.get_vwap_asset_latest(asset='btc', lookback_period=60, time_format=TimeFormat.ISO)
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertTrue('asset' in result.index.names, 'asset not in index')
        self.assertTrue('timestamp' in result.index.names, 'timestamp not in index')
        self.assertTrue(result.index.get_level_values('asset').isin(['btc']).all(),
                        'Returned asset does not match the requested asset')

    def test_get_vwap_asset_historical_raw_vanilla(self):
        result = srs.get_vwap_asset_historical_raw(asset='btc')
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertIn('timestamp', result.columns, 'timestamp column is missing')
        self.assertIn('asset', result.columns, 'asset column is missing')
        self.assertIn('price', result.columns, 'price column is missing')
        self.assertIn('vwap', result.columns, 'vwap column is missing')
        self.assertIn('volume', result.columns, 'volume column is missing')

    def test_get_vwap_asset_historical_with_params(self):
        start_date = datetime(2020, 9, 1, 1, 0, 0)
        end_date = datetime(2020, 9, 1, 2, 0, 0)
        result = srs.get_vwap_asset_historical(asset='btc', start_date=start_date, end_date=end_date,
                                               time_interval=TimeInterval.MINUTE, lookback_period=60,
                                               time_format=TimeFormat.ISO)
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertTrue('asset' in result.index.names, 'asset not in index')
        self.assertTrue('timestamp' in result.index.names, 'timestamp not in index')
        self.assertTrue(result.index.get_level_values('asset').isin(['btc']).all(),
                        'Returned asset does not match the requested asset')

    def test_get_vwap_pairs_information_raw_vanilla(self):
        result = srs.get_vwap_pairs_information_raw()
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertIn('pair', result.columns, 'pair column is missing')
        self.assertIn('startDate', result.columns, 'startDate column is missing')
        self.assertIn('endDate', result.columns, 'endDate column is missing')
        self.assertIn('assetSymbol', result.columns, 'assetSymbol column is missing')
        self.assertIn('exchange', result.columns, 'exchange column is missing')

    def test_get_vwap_pairs_information_with_params(self):
        result = srs.get_vwap_pairs_information(pair='btc_usd', time_format=TimeFormat.ISO)
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertTrue('pair' in result.index.names, 'pair not in index')
        self.assertTrue('exchange' in result.index.names, 'exchange not in index')
        self.assertTrue(result.index.get_level_values('pair').isin(['btc_usd']).all(),
                        'Returned pair does not match the requested pair')

    def test_get_vwap_pair_latest_raw_vanilla(self):
        result = srs.get_vwap_pair_latest_raw(pair='btc_usd')
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertIn('timestamp', result.columns, 'timestamp column is missing')
        self.assertIn('pair', result.columns, 'pair column is missing')
        self.assertIn('price', result.columns, 'price column is missing')
        self.assertIn('vwap', result.columns, 'vwap column is missing')
        self.assertIn('volume', result.columns, 'volume column is missing')

    def test_get_vwap_pair_latest_with_params(self):
        result = srs.get_vwap_pair_latest(pair='btc_usd', lookback_period=60, time_format=TimeFormat.ISO)
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertTrue('pair' in result.index.names, 'pair not in index')
        self.assertTrue('timestamp' in result.index.names, 'timestamp not in index')
        self.assertTrue(result.index.get_level_values('pair').isin(['btc_usd']).all(),
                        'Returned pair does not match the requested pair')

    def test_get_vwap_pair_historical_raw_vanilla(self):
        result = srs.get_vwap_pair_historical_raw(pair='btc_usd')
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertIn('timestamp', result.columns, 'timestamp column is missing')
        self.assertIn('pair', result.columns, 'pair column is missing')
        self.assertIn('price', result.columns, 'price column is missing')
        self.assertIn('vwap', result.columns, 'vwap column is missing')
        self.assertIn('volume', result.columns, 'volume column is missing')

    def test_get_vwap_pair_historical_with_params(self):
        start_date = datetime(2020, 1, 1, 0, 0, 0)
        end_date = datetime(2020, 1, 2, 0, 0, 0)
        result = srs.get_vwap_pair_historical(pair='btc_usd', start_date=start_date, end_date=end_date,
                                              time_format=TimeFormat.ISO)
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        self.assertTrue('pair' in result.index.names, 'pair not in index')
        self.assertTrue('timestamp' in result.index.names, 'timestamp not in index')
        self.assertTrue(result.index.get_level_values('pair').isin(['btc_usd']).all(),
                        'Returned pair does not match the requested pair')

    def test_get_prices_assets_historical_raw_vanilla(self):
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()
        asset = 'btc'
        result = srs.get_prices_assets_historical_raw(asset, start_date=start_date, end_date=end_date)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertIn('timestamp', result.columns, "timestamp not in columns")
        self.assertIn('asset', result.columns, "asset not in columns")

    def test_get_prices_assets_historical_raw_with_time_interval(self):
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()
        asset = 'btc'
        time_interval = TimeInterval.HOUR
        result = srs.get_prices_assets_historical_raw(asset, start_date, end_date, time_interval=time_interval)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertIn('timestamp', result.columns, "timestamp not in columns")
        self.assertIn('asset', result.columns, "asset not in columns")

    def test_get_prices_assets_historical_raw_parallel_execution(self):
        start_date = datetime.now() - timedelta(days=3)
        end_date = datetime.now()
        asset = 'btc'
        result = srs.get_prices_assets_historical_raw(asset, start_date=start_date, end_date=end_date,
                                                      parallel_execution=True)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertIn('timestamp', result.columns, "timestamp not in columns")
        self.assertIn('price', result.columns, "price not in columns")

    def test_get_prices_assets_historical_vanilla(self):
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()
        asset = 'btc'
        result = srs.get_prices_assets_historical(asset, start_date, end_date)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['asset', 'timestamp'],
                             "Index keys are not as expected")

    def test_get_prices_assets_historical_with_time_interval(self):
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()
        asset = 'btc'
        time_interval = TimeInterval.HOUR
        result = srs.get_prices_assets_historical(asset, start_date, end_date, time_interval=time_interval)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['asset', 'timestamp'],
                             "Index keys are not as expected")

    def test_get_prices_pairs_information_raw_vanilla(self):
        result = srs.get_prices_pairs_information_raw(pair="btc_usd")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertIn('pair', result.columns, "pair not in columns")

    def test_get_prices_pairs_information_raw_with_pair(self):
        pair = 'btc_usdt'
        result = srs.get_prices_pairs_information_raw(pair=pair)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertIn('pair', result.columns, "pair not in columns")
        self.assertIn(pair, result['pair'].values, f"{pair} not in pair values")

    def test_get_prices_pairs_information_vanilla(self):
        result = srs.get_prices_pairs_information()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['pair'], "Index keys are not as expected")

    def test_get_prices_pairs_information_with_pair(self):
        pair = 'btc_usdt'
        result = srs.get_prices_pairs_information(pair=pair)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['pair'], "Index keys are not as expected")
        self.assertIn(pair, result.index.values, f"{pair} not in index values")

    def test_get_prices_pairs_information_with_custom_index_keys(self):
        pair = 'btc_usdt'
        index_keys = ['pair']
        result = srs.get_prices_pairs_information(pair=pair, index_keys=index_keys)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), index_keys, "Index keys are not as expected")

    def test_get_prices_pairs_latest_raw_vanilla(self):
        result = srs.get_prices_pairs_latest_raw(pair="btc_usd")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertIn('pair', result.columns, "pair not in columns")

    def test_get_prices_pairs_latest_raw_with_pair(self):
        pair = 'btc_usdt'
        result = srs.get_prices_pairs_latest_raw(pair=pair)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertIn('pair', result.columns, "pair not in columns")
        self.assertIn(pair, result['pair'].values, f"{pair} not in pair values")

    def test_get_prices_pairs_latest_raw_with_exchanges(self):
        pair = 'btc_usdt'
        exchange = MarketDataVenue.BINANCE
        result = srs.get_prices_pairs_latest_raw(pair=pair, exchange=exchange)

        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertIn('pair', result.columns, "pair not in columns")
        self.assertIn(pair, result['pair'].values, f"{pair} not in pair values")
        self.assertIn(exchange.value, result['exchange'].values, "Exchanges not in result")
        self.assertIn('exchange', result.columns, "exchange not in columns")

    def test_get_prices_pairs_latest_vanilla(self):
        result = srs.get_prices_pairs_latest(pair="btc_usd")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['pair'], "Index keys are not as expected")

    def test_get_prices_pairs_latest_with_pair(self):
        pair = 'btc_usdt'
        result = srs.get_prices_pairs_latest(pair=pair)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['pair'], "Index keys are not as expected")
        self.assertIn(pair, result.index.values, f"{pair} not in index values")

    def test_get_prices_pairs_latest_with_exchanges(self):
        pair = 'btc_usdt'
        exchange = MarketDataVenue.BINANCE
        result = srs.get_prices_pairs_latest(pair=pair, exchange=exchange)

        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['pair'], "Index keys are not as expected")
        self.assertIn(pair, result.index.values, f"{pair} not in index values")
        self.assertIn(exchange.value, result['exchange'].values, "Exchanges not in result")

    def test_get_prices_pairs_latest_with_custom_index_keys(self):
        pair = 'btc_usdt'
        index_keys = ['timestamp']
        result = srs.get_prices_pairs_latest(pair=pair, index_keys=index_keys)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['timestamp'], "Index keys are not as expected")
