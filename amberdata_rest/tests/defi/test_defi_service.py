import unittest

import pandas as pd

from amberdata_rest.common import ApiKeyGetMode
from amberdata_rest.constants import Blockchain, DexDataVenue, TimeFormat, TimeInterval, ProtocolId, ProtocolAction, StableCoin, SortDirection
from amberdata_rest.defi.service import DefiRestService

drs = DefiRestService(ApiKeyGetMode.LOCAL_FILE, {"local_key_path": "./../../.localKeys"})

class AmberdataSpotRestTest(unittest.TestCase):
    def test_headers(self):
        headers = drs._headers()
        self.assertTrue('x-api-key' in headers.keys(), 'x-api-key not in headers')
        self.assertTrue('accept' in headers.keys(), 'accept not in headers')
        self.assertTrue(headers['accept'] == 'application/json', 'accept != application/json')


    ### 1- DEX TRADES ###
    def test_get_dex_trades_historical_raw_vanilla(self):
        result = drs.get_dex_trades_historical_raw(blockchain=Blockchain.ETHEREUM_MAINNET, start_date="2025-05-01",
                                                   end_date="2025-05-02",
                                                   liquidity_pool_address="0x65a33e74e18c99388f4989c296ab8e860219ee76",
                                                   asset_bought_address="0x4ae149fd6059af772b962efac6bf0236872d6940")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertIn('assetBoughtAddress', result.columns, "assetBoughtAddress not in columns")
        self.assertIn('assetBoughtAmount', result.columns, "assetBoughtAmount not in columns")
        self.assertIn('assetBoughtAmountRaw', result.columns, "assetBoughtAmountRaw not in columns")
        self.assertIn('assetBoughtDecimals', result.columns, "assetBoughtDecimals not in columns")
        self.assertIn('assetBoughtPrice', result.columns, "assetBoughtPrice not in columns")
        self.assertIn('assetBoughtSymbol', result.columns, "assetBoughtSymbol not in columns")
        self.assertIn('assetPair', result.columns, "assetPair not in columns")
        self.assertIn('assetSoldAddress', result.columns, "assetSoldAddress not in columns")
        self.assertIn('assetSoldAmount', result.columns, "assetSoldAmount not in columns")
        self.assertIn('assetSoldAmountRaw', result.columns, "assetSoldAmountRaw not in columns")
        self.assertIn('assetSoldDecimals', result.columns, "assetSoldDecimals not in columns")
        self.assertIn('assetSoldPrice', result.columns, "assetSoldPrice not in columns")
        self.assertIn('assetSoldSymbol', result.columns, "assetSoldSymbol not in columns")
        self.assertIn('blockchain', result.columns, "blockchain not in columns")
        self.assertIn('protocolName', result.columns, "protocolName not in columns")
        self.assertIn('timestamp', result.columns, "timestamp not in columns")

    def test_get_dex_trades_historical_vanilla(self):
        result = drs.get_dex_trades_historical(
            blockchain=Blockchain.ETHEREUM_MAINNET, start_date="2025-05-01", end_date="2025-05-02",
            asset_bought_address="0x4ae149fd6059af772b962efac6bf0236872d6940",
            liquidity_pool_address="0x65a33e74e18c99388f4989c296ab8e860219ee76"
        )

        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['timestamp'], "Index keys are not as expected")

    def test_get_dex_protocols_information_raw_vanilla(self):
        result = drs.get_dex_protocols_information_raw(
            blockchain=Blockchain.ETHEREUM_MAINNET, active_after_date="2025-05-01",
            liquidity_pool_address="0x65a33e74e18c99388f4989c296ab8e860219ee76", protocol_name="uniswap_v2"
        )
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertIn('blockchain', result.columns, "blockchain not in columns")
        self.assertIn('firstKnownTradeDate', result.columns, "firstKnownTradeDate not in columns")
        self.assertIn('lastKnownTradeDate', result.columns, "lastKnownTradeDate not in columns")
        self.assertIn('liquidityPoolAddress', result.columns, "liquidityPoolAddress not in columns")
        self.assertIn('protocolName', result.columns, "protocolName not in columns")

    def test_get_dex_protocols_information_vanilla(self):
        result = drs.get_dex_protocols_information(blockchain=Blockchain.ETHEREUM_MAINNET, protocol_name="uniswap_v2",
                                                   active_after_date="2025-05-01",
                                                   liquidity_pool_address="0x65a33e74e18c99388f4989c296ab8e860219ee76")

        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['protocolName'], "Index keys are not as expected")

    ### 2 - OHLCV ###
    def test_get_ohlcv_information_raw_vanilla(self):
        result = drs.get_ohlcv_information_raw(exchanges=[DexDataVenue.SUSHISWAP], size=25000)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertIn('address', result.columns, "address not in columns")
        self.assertIn('baseAddress', result.columns, "baseAddress not in columns")
        self.assertIn('quoteAddress', result.columns, "quoteAddress not in columns")

    def test_get_ohlcv_information_vanilla(self):
        result = drs.get_ohlcv_information(exchanges=[DexDataVenue.SUSHISWAP], size=25000)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['baseAddress', 'quoteAddress'], "Index keys are not as expected")

    def test_get_ohlcv_latest_raw_vanilla(self):
        result = drs.get_ohlcv_latest_raw(pool="DAI_USDC", exchanges=[DexDataVenue.UNISWAP_V2])
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        for col in ['timestamp', 'open', 'high', 'low', 'close', 'volume']:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_ohlcv_latest_vanilla(self):
        result = drs.get_ohlcv_latest(pool="DAI_USDC", exchanges=[DexDataVenue.UNISWAP_V2])
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        indexNames = ['baseSymbol', 'quoteSymbol', 'exchangeName']
        self.assertListEqual(list(result.index.names), indexNames, "Index keys are not as expected")

    def test_get_ohlcv_historical_raw_vanilla(self):
        result = drs.get_ohlcv_historical_raw(pool="DAI_WETH")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        expected_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'trades', 'exchangeId']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_ohlcv_historical_vanilla(self):
        result = drs.get_ohlcv_historical(pool="DAI_WETH")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        expect_index_keys = ['baseAddress', 'quoteAddress', 'exchangeId', 'timestamp']
        self.assertListEqual(list(result.index.names), expect_index_keys, "Index keys are not as expected")

    ### 3 - LIQUIDITY ###
    # NOT ACCEPTING QUERY PARAMS
    # TODO: Re-enable after 500 ERRORS are resolved
    # def test_get_liquidity_information_raw(self):
    #     result = drs.get_liquidity_information_raw(exchanges=[DexDataVenue.UNISWAP_V2])
    #     self.assertIsNotNone(result, 'result is None')
    #     self.assertFalse(result.empty, 'result is empty')
    #     self.assertIn('exchange', result.columns, 'exchange not in columns')
    #
    # # NOT ACCEPTING QUERY PARAMS
    # TODO: Re-enable after 500 ERRORS are resolved
    # def test_get_liquidity_information(self):
    #     result = drs.get_liquidity_information(exchanges=[DexDataVenue.UNISWAP_V2,DexDataVenue.BALANCER_VAULT])
    #     self.assertIsNotNone(result, 'result is None')
    #     self.assertFalse(result.empty, 'result is empty')
    #     self.assertIn('exchange', result.columns, 'exchange not in columns')

    def test_get_liquidity_latest_raw(self):
        result = drs.get_liquidity_latest_raw(pool='0xBb2b8038a1640196FbE3e38816F3e67Cba72D940', exchanges=[DexDataVenue.UNISWAP_V2])
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        expected_columns = ['exchangeName', 'exchangeId', 'pair', 'pairNormalized', 'pairAddress', 'baseAddress',
                            'quoteAddress',
                            'address', 'timestamp', 'transactionHash', 'transactionIndex', 'logIndex', 'amount',
                            'liquidityPrice',
                            'timeUTC', 'timeEST']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_liquidity_latest(self):
        result = drs.get_liquidity_latest(pool='0xBb2b8038a1640196FbE3e38816F3e67Cba72D940', exchanges=[DexDataVenue.UNISWAP_V2])
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        index_keys = ['exchangeName', 'address']
        self.assertListEqual(list(result.index.names), index_keys, "Index keys are not as expected")

    def test_get_liquidity_historical_raw(self):
        result = drs.get_liquidity_historical_raw(pool='WBTC_WETH', exchanges=[DexDataVenue.UNISWAP_V2])
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        expected_columns = [
            'exchangeId', 'pairAddress', 'address', 'timestamp', 'transactionHash', 'transactionIndex',
            'logIndex', 'amount', 'liquidityPrice', 'startDate', 'endDate', 'dexPairs',
            'timeUTC', 'timeEST'
        ]
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_liquidity_historical(self):
        result = drs.get_liquidity_historical(pool='WBTC_WETH', exchanges=[DexDataVenue.UNISWAP_V2])
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        index_keys = ['exchangeId', 'address']
        self.assertListEqual(list(result.index.names), index_keys, "Index keys are not as expected")

    def test_get_liquidity_snapshots_raw(self):
        result = drs.get_liquidity_snapshots_raw(pool_address='0xa478c2975ab1ea89e8196811f51a7b7ade33eb11')
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        expected_columns = [
            'timestamp', 'blockNumber', 'transactionHash', 'exchangeId', 'exchangeName', 'poolName',
            'poolAddress', 'liquidity', 'poolFee', 'totalPoolValue', 'lpTokenPrice', 'timeUTC', 'timeEST'
        ]
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_liquidity_snapshots(self):
        result = drs.get_liquidity_snapshots(pool_address='0xa478c2975ab1ea89e8196811f51a7b7ade33eb11')
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        index_keys = ['blockNumber', 'exchangeName', 'poolName']
        self.assertListEqual(list(result.index.names), index_keys, "Index keys are not as expected")

    def test_get_uniswap_v3_liquidity_distribution_raw(self):
        result = drs.get_uniswap_v3_liquidity_distribution_raw(
            pool_address='0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640',
            price0_usd_min=float(0.95), price0_usd_max=float(1.05)
        )
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        expected_columns = ['isActiveTick', 'liquidity', 'price0USD', 'price1USD', 'token0AmountLocked',
                            'token1AmountLocked', 'tickIndex']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_uniswap_v3_liquidity_distribution(self):
        result = drs.get_uniswap_v3_liquidity_distribution(
            pool_address='0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640',
            price0_usd_min=float(0.95), price0_usd_max=float(1.05)
        )
        self.assertIsNotNone(result, 'result is None')
        self.assertFalse(result.empty, 'result is empty')
        index_keys = ['isActiveTick', 'tickIndex']
        self.assertListEqual(list(result.index.names), index_keys, "Index keys are not as expected")

    ### 4 - LIQUIDITY PROVIDERS ###
    def test_get_pool_providers_raw_vanilla(self):
        result = drs.get_pool_providers_raw(pair="0xa478c2975ab1ea89e8196811f51a7b7ade33eb11", size=10)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        expected_columns = ['tokenAddress', 'holderAddress', 'timestamp', 'numTokens', 'position', 'timeUTC', 'timeEST']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_pool_providers_vanilla(self):
        result = drs.get_pool_providers(pair="0xa478c2975ab1ea89e8196811f51a7b7ade33eb11", size=10)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['tokenAddress', 'holderAddress'], "Index keys are not as expected")

    def test_get_provider_positions_raw_vanilla(self):
        result = drs.get_provider_positions_raw(address="0x13f89a69d28f5fe9a16ca762f21eb9f5c18fd645", size=10)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        expected_columns = ['tokenAddress', 'holderAddress', 'timestamp', 'numTokens', 'supply', 'position', 'timeUTC', 'timeEST']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_provider_positions_vanilla(self):
        result = drs.get_provider_positions(address="0x13f89a69d28f5fe9a16ca762f21eb9f5c18fd645", size=10)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['holderAddress', 'tokenAddress'], "Index keys are not as expected")

    def test_get_provider_events_raw_vanilla(self):
        result = drs.get_provider_events_raw(provider_address="0x18f3e0c9f3bdd2e79e3eeeb1bcd8e6bb9702095f",
                                             start_date="2022-07-01T01:00:00", end_date="2022-07-15T01:00:00",
                                             include_all_transaction_events=True)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        expected_columns = ['timestamp', 'blockNumber', 'transactionHash', 'liquidityProviderAddress', 'event', 'poolAddress', 'poolTokenBalance', 'poolTokenDelta', 'priceNative', 'timeUTC', 'timeEST']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_provider_events_vanilla(self):
        result = drs.get_provider_events(provider_address="0x18f3e0c9f3bdd2e79e3eeeb1bcd8e6bb9702095f",start_date="2022-07-01T01:00:00", end_date="2022-07-15T01:00:00", include_all_transaction_events=True)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['liquidityProviderAddress', 'event', 'poolAddress'], "Index keys are not as expected")


    ### 5 - DEFI METRICS ###
    def test_get_metrics_exchanges_latest_raw_vanilla(self):
        result = drs.get_metrics_exchanges_latest_raw(exchange=DexDataVenue.UNISWAP_V2)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        expected_columns = [
            'exchangeId', 'timestamp', 'feesUSD', 'liquidityTotalWETH', 'liquidityTotalUSD', 'pairsTradedTotal',
            'pairsCumulativeTotal', 'tradesTotal', 'volumeTotalWETH', 'volumeTotalUSD', 'timeUTC', 'timeEST'
        ]

        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_metrics_exchanges_latest_vanilla(self):
        result = drs.get_metrics_exchanges_latest(exchange=DexDataVenue.UNISWAP_V2)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['exchangeId'], "Index keys are not as expected")

    def test_get_metrics_exchanges_historical_raw_vanilla(self):
        result = drs.get_metrics_exchanges_historical_raw(exchange=DexDataVenue.UNISWAP_V2)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        expected_columns = [
            'exchangeId', 'timestamp', 'feesUSD', 'liquidityTotalWETH', 'liquidityTotalUSD', 'pairsTradedTotal',
            'pairsCumulativeTotal', 'tradesTotal', 'volumeTotalWETH', 'volumeTotalUSD', 'startDate', 'endDate',
            'timeUTC', 'timeEST'
        ]

        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_metrics_exchanges_historical_vanilla(self):
        result = drs.get_metrics_exchanges_historical(exchange=DexDataVenue.UNISWAP_V2)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['exchangeId', 'timestamp'], "Index keys are not as expected")

    def test_get_metrics_assets_latest_raw_vanilla(self):
        result = drs.get_metrics_assets_latest_raw(
            exchange=DexDataVenue.UNISWAP_V2, asset='0x6b175474e89094c44da98b954eedeac495271d0f'
        )
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        expected_columns = ['exchangeId', 'address', 'timestamp', 'liquidityTotalNative', 'liquidityTotalUSD',
                            'timeUTC', 'timeEST']

        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_metrics_assets_latest_vanilla(self):
        result = drs.get_metrics_assets_latest(
            exchange=DexDataVenue.UNISWAP_V2, asset='0x6b175474e89094c44da98b954eedeac495271d0f'
        )
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['exchangeId', 'address'], "Index keys are not as expected")

    def test_get_metrics_assets_historical_raw_vanilla(self):
        result = drs.get_metrics_assets_historical_raw(
            exchange=DexDataVenue.UNISWAP_V2, asset='0x6b175474e89094c44da98b954eedeac495271d0f'
        )
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        expected_columns = ['exchangeId', 'address', 'timestamp', 'liquidityTotalNative', 'liquidityTotalUSD',
                            'startDate', 'endDate', 'timeUTC', 'timeEST']

        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_metrics_assets_historical_vanilla(self):
        result = drs.get_metrics_assets_historical(
            exchange=DexDataVenue.UNISWAP_V2, asset='0x6b175474e89094c44da98b954eedeac495271d0f'
        )
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['exchangeId', 'address', 'timestamp'], "Index keys are not as expected")

    def test_get_metrics_pairs_latest_raw_vanilla(self):
        result = drs.get_metrics_pairs_latest_raw(
            exchange=DexDataVenue.UNISWAP_V2, pair='0xa478c2975ab1ea89e8196811f51a7b7ade33eb11'
        )
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        expected_columns = [
            'exchangeId', 'feesNative', 'feesUSD', 'liquidityTotalNative', 'liquidityTotalUSD', 'volumeTotalUSD',
            'volumeTotalNative', 'pairsTradedTotal', 'tradesTotal', 'timestamp', 'timeUTC', 'timeEST'
        ]

        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_metrics_pairs_latest_vanilla(self):
        result = drs.get_metrics_pairs_latest(
            exchange=DexDataVenue.UNISWAP_V2, pair='0xa478c2975ab1ea89e8196811f51a7b7ade33eb11'
        )
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['exchangeId'], "Index keys are not as expected")

    def test_get_metrics_pairs_historical_raw_vanilla(self):
        result = drs.get_metrics_pairs_historical_raw(
            exchange=DexDataVenue.UNISWAP_V2, pair='0xa478c2975ab1ea89e8196811f51a7b7ade33eb11'
        )
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        expected_columns = [
            'exchangeId', 'feesNative', 'feesUSD', 'liquidityTotalNative', 'liquidityTotalUSD', 'volumeTotalUSD',
            'volumeTotalNative', 'pairsTradedTotal', 'tradesTotal', 'timestamp', 'startDate', 'endDate', 'timeUTC',
            'timeEST'
        ]

        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_metrics_pairs_historical_vanilla(self):
        result = drs.get_metrics_pairs_historical(
            exchange=DexDataVenue.UNISWAP_V2, pair='0xa478c2975ab1ea89e8196811f51a7b7ade33eb11'
        )
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['exchangeId', 'timestamp'], "Index keys are not as expected")

    ### 6 - Price/TWAP/VWAP ###
    def test_get_assets_information_raw_vanilla(self):
        result = drs.get_assets_information_raw()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertIn('address', result.columns, "address not in columns")
        self.assertIn('startDate', result.columns, "startDate not in columns")
        self.assertIn('endDate', result.columns, "endDate not in columns")

    def test_get_assets_information_vanilla(self):
        result = drs.get_assets_information()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['address'], "Index keys are not as expected")

    def test_get_asset_latest_raw_vanilla(self):
        asset = "0x6b175474e89094c44da98b954eedeac495271d0f"  # DAI contract address
        result = drs.get_asset_latest_raw(asset=asset)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        expected_columns = ['timestamp', 'asset', 'price', 'volume']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_asset_latest_raw_with_time_format(self):
        asset = "0x6b175474e89094c44da98b954eedeac495271d0f"
        time_format = TimeFormat.ISO
        result = drs.get_asset_latest_raw(asset=asset, time_format=time_format)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        expected_columns = ['timestamp', 'asset', 'price', 'volume']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")
        # Confirm that the timestamp column is in ISO format
        self.assertTrue(pd.to_datetime(result['timestamp'], format='%Y-%m-%dT%H:%M:%S.%fZ', errors='coerce').notnull().all(), "Timestamp format is not ISO")

    def test_get_asset_latest_vanilla(self):
        asset = "0x6b175474e89094c44da98b954eedeac495271d0f"
        result = drs.get_asset_latest(asset=asset)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        self.assertListEqual(list(result.index.names), ['asset'], "Index keys are not as expected")

    def test_get_asset_historical_raw_vanilla(self):
        asset = "0x6b175474e89094c44da98b954eedeac495271d0f"
        result = drs.get_asset_historical_raw(asset=asset)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        expected_columns = ['timestamp', 'asset', 'price', 'volume']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_asset_historical_raw_with_time_interval(self):
        asset = "0x6b175474e89094c44da98b954eedeac495271d0f"
        time_interval = TimeInterval.HOUR
        result = drs.get_asset_historical_raw(asset=asset, time_interval=time_interval)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        expected_columns = ['timestamp', 'asset', 'price', 'volume']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_asset_historical_with_custom_index_keys(self):
        asset = "0x6b175474e89094c44da98b954eedeac495271d0f"
        index_keys = ['asset']
        result = drs.get_asset_historical(asset=asset, index_keys=index_keys)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        self.assertListEqual(list(result.index.names), ['asset'], "Index keys are not as expected")

    def test_get_asset_historical_vanilla(self):
        asset = "0x6b175474e89094c44da98b954eedeac495271d0f"
        result = drs.get_asset_historical(asset=asset)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        self.assertListEqual(list(result.index.names), ['timestamp'], "Index keys are not as expected")

    def test_get_pairs_information_raw_vanilla(self):
        result = drs.get_pairs_information_raw(size=10000)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        expected_columns = ['baseAddress', 'quoteAddress', 'startDate', 'endDate']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_pairs_information_vanilla(self):
        result = drs.get_pairs_information(size=10000)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        self.assertListEqual(list(result.index.names), ['baseAddress', 'quoteAddress'],
                             "Index keys are not as expected")

    def test_get_pairs_latest_raw_vanilla(self):
        base = "0x6b175474e89094c44da98b954eedeac495271d0f"  # DAI
        quote = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"  # WETH
        result = drs.get_pairs_latest_raw(base=base, quote=quote)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        expected_columns = ['timestamp', 'pair', 'price']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_pairs_latest_vanilla(self):
        base = "0x6b175474e89094c44da98b954eedeac495271d0f"
        quote = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
        result = drs.get_pairs_latest(base=base, quote=quote)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        self.assertListEqual(list(result.index.names), ['pair'], "Index keys are not as expected")

    def test_get_pairs_historical_raw_vanilla(self):
        base = "0x6b175474e89094c44da98b954eedeac495271d0f"
        quote = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
        result = drs.get_pairs_historical_raw(base=base, quote=quote, start_date="2025-05-01", end_date="2025-05-02")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        expected_columns = ['timestamp', 'pair', 'price']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_pairs_historical_vanilla(self):
        base = "0x6b175474e89094c44da98b954eedeac495271d0f"
        quote = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
        result = drs.get_pairs_historical(base=base, quote=quote, start_date="2025-05-01", end_date="2025-05-02")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        self.assertListEqual(list(result.index.names), ['timestamp'], "Index keys are not as expected")

    def test_get_global_twap_assets_information_raw_vanilla(self):
        result = drs.get_global_twap_assets_information_raw()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        expected_columns = ['address', 'startDate', 'endDate']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_global_twap_assets_information_vanilla(self):
        result = drs.get_global_twap_assets_information()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        self.assertListEqual(list(result.index.names), ['address'], "Index keys are not as expected")

    def test_get_global_twap_assets_information_with_custom_index_keys(self):
        index_keys = ['startDate']
        result = drs.get_global_twap_assets_information(index_keys=index_keys)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        self.assertListEqual(list(result.index.names), ['startDate'], "Index keys are not as expected")

    def test_get_global_twap_asset_latest_raw_vanilla(self):
        asset = "0x6b175474e89094c44da98b954eedeac495271d0f"  # Example DAI contract address
        result = drs.get_global_twap_asset_latest_raw(asset=asset)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        expected_columns = ['timestamp', 'asset', 'price', 'volume', 'twap']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_global_twap_asset_latest_vanilla(self):
        asset = "0x6b175474e89094c44da98b954eedeac495271d0f"
        result = drs.get_global_twap_asset_latest(asset=asset)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        self.assertListEqual(list(result.index.names), ['timestamp'], "Index keys are not as expected")

    def test_get_global_twap_asset_latest_with_custom_index_keys(self):
        asset = "0x6b175474e89094c44da98b954eedeac495271d0f"
        index_keys = ['asset']
        result = drs.get_global_twap_asset_latest(asset=asset, index_keys=index_keys)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        self.assertListEqual(list(result.index.names), ['asset'], "Index keys are not as expected")

    def test_get_global_twap_asset_historical_raw_vanilla(self):
        asset = "0x6b175474e89094c44da98b954eedeac495271d0f"  # Example DAI contract address
        result = drs.get_global_twap_asset_historical_raw(asset=asset)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        expected_columns = ['timestamp', 'asset', 'price', 'volume', 'twap']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_global_twap_asset_historical_raw_with_dates(self):
        asset = "0x6b175474e89094c44da98b954eedeac495271d0f"
        start_date = "2023-09-01T00:00:00Z"
        end_date = "2023-09-02T00:00:00Z"
        result = drs.get_global_twap_asset_historical_raw(asset=asset, start_date=start_date, end_date=end_date)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        expected_columns = ['timestamp', 'asset', 'price', 'volume', 'twap']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_global_twap_asset_historical_vanilla(self):
        asset = "0x6b175474e89094c44da98b954eedeac495271d0f"
        result = drs.get_global_twap_asset_historical(asset=asset)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        self.assertListEqual(list(result.index.names), ['timestamp'], "Index keys are not as expected")

    def test_get_global_twap_asset_historical_with_custom_index_keys(self):
        asset = "0x6b175474e89094c44da98b954eedeac495271d0f"
        index_keys = ['asset']
        result = drs.get_global_twap_asset_historical(asset=asset, index_keys=index_keys)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        self.assertListEqual(list(result.index.names), ['asset'], "Index keys are not as expected")

    def test_get_global_twap_pairs_information_raw_vanilla(self):
        result = drs.get_global_twap_pairs_information_raw()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        expected_columns = ['baseAddress', 'quoteAddress', 'startDate', 'endDate']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_global_twap_pairs_information_vanilla(self):
        result = drs.get_global_twap_pairs_information()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        self.assertListEqual(list(result.index.names), ['baseAddress', 'quoteAddress'],
                             "Index keys are not as expected")

    def test_get_global_twap_pairs_information_with_custom_index_keys(self):
        index_keys = ['startDate']
        result = drs.get_global_twap_pairs_information(index_keys=index_keys)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        self.assertListEqual(list(result.index.names), ['startDate'], "Index keys are not as expected")

    def test_get_global_twap_pairs_latest_raw_vanilla(self):
        base = "0x6b175474e89094c44da98b954eedeac495271d0f"  # DAI
        quote = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"  # WETH
        result = drs.get_global_twap_pairs_latest_raw(base=base, quote=quote)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        expected_columns = ['timestamp', 'pair', 'price', 'volume', 'twap']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_global_twap_pairs_latest_vanilla(self):
        base = "0x6b175474e89094c44da98b954eedeac495271d0f"  # DAI
        quote = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"  # WETH
        result = drs.get_global_twap_pairs_latest(base=base, quote=quote)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        self.assertListEqual(list(result.index.names), ['pair'], "Index keys are not as expected")

    def test_get_global_twap_pairs_historical_raw_vanilla(self):
        base = "0x6b175474e89094c44da98b954eedeac495271d0f"  # DAI
        quote = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"  # WETH
        result = drs.get_global_twap_pairs_historical_raw(base=base, quote=quote)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        expected_columns = [
            'timestamp', 'pair', 'price', 'volume', 'twap',
            'baseAddress', 'baseSymbol', 'quoteAddress', 'quoteSymbol'
        ]
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_global_twap_pairs_historical_vanilla(self):
        base = "0x6b175474e89094c44da98b954eedeac495271d0f"  # DAI
        quote = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"  # WETH
        result = drs.get_global_twap_pairs_historical(base=base, quote=quote)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        self.assertListEqual(list(result.index.names), ['pair'], "Index keys are not as expected")

    def test_get_global_vwap_assets_information_raw_vanilla(self):
        result = drs.get_global_vwap_assets_information_raw()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        expected_columns = ['address', 'startDate', 'endDate']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_global_vwap_assets_information_vanilla(self):
        result = drs.get_global_vwap_assets_information()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        self.assertListEqual(list(result.index.names), ['address'], "Index keys are not as expected")

    def test_get_global_vwap_assets_latest_raw_vanilla(self):
        asset = "0x6b175474e89094c44da98b954eedeac495271d0f"  # DAI
        result = drs.get_global_vwap_assets_latest_raw(asset=asset, lookback_period=10)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        expected_columns = ['asset', 'timestamp', 'price', 'volume', 'vwap']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_global_vwap_assets_latest_vanilla(self):
        asset = "0x6b175474e89094c44da98b954eedeac495271d0f"
        result = drs.get_global_vwap_assets_latest(asset=asset, lookback_period=10)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        self.assertListEqual(list(result.index.names), ['asset'], "Index keys are not as expected")

    def test_get_global_vwap_asset_historical_raw_vanilla(self):
        asset = "0x6b175474e89094c44da98b954eedeac495271d0f"  # DAI
        result = drs.get_global_vwap_asset_historical_raw(asset=asset)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        expected_columns = ['timestamp', 'asset', 'price', 'volume', 'vwap', 'startDate', 'endDate']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_global_vwap_asset_historical_raw_with_dates(self):
        asset = "0x6b175474e89094c44da98b954eedeac495271d0f"
        start_date = "2023-09-01T00:00:00Z"
        end_date = "2023-09-02T00:00:00Z"
        result = drs.get_global_vwap_asset_historical_raw(asset=asset, start_date=start_date, end_date=end_date)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        expected_columns = ['timestamp', 'asset', 'price', 'volume', 'vwap', 'startDate', 'endDate']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_global_vwap_asset_historical_vanilla(self):
        asset = "0x6b175474e89094c44da98b954eedeac495271d0f"
        result = drs.get_global_vwap_asset_historical(asset=asset)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        self.assertListEqual(list(result.index.names), ['asset', 'timestamp'], "Index keys are not as expected")

    def test_get_global_vwap_pairs_information_raw_vanilla(self):
        result = drs.get_global_vwap_pairs_information_raw()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        expected_columns = ['baseAddress', 'quoteAddress', 'startDate', 'endDate']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_global_vwap_pairs_information_vanilla(self):
        result = drs.get_global_vwap_pairs_information()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        self.assertListEqual(list(result.index.names), ['baseAddress', 'quoteAddress'],
                             "Index keys are not as expected")

    def test_get_global_vwap_pairs_latest_raw_vanilla(self):
        base = "0x6b175474e89094c44da98b954eedeac495271d0f"  # DAI
        quote = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"  # WETH
        result = drs.get_global_vwap_pairs_latest_raw(base=base, quote=quote)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        expected_columns = ['timestamp', 'pair', 'price', 'volume', 'vwap']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_global_vwap_pairs_latest_vanilla(self):
        base = "0x6b175474e89094c44da98b954eedeac495271d0f"
        quote = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
        result = drs.get_global_vwap_pairs_latest(base=base, quote=quote)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        self.assertListEqual(list(result.index.names), ['pair'], "Index keys are not as expected")

    def test_get_global_vwap_pairs_historical_raw_vanilla(self):
        base = "0x6b175474e89094c44da98b954eedeac495271d0f"  # DAI
        quote = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"  # WETH
        result = drs.get_global_vwap_pairs_historical_raw(
            base=base,
            quote=quote
        )
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        expected_columns = ['timestamp', 'pair', 'price', 'volume', 'vwap', 'baseAddress', 'baseSymbol', 'quoteAddress', 'quoteSymbol', 'startDate', 'endDate']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_global_vwap_pairs_historical_with_dates(self):
        base = "0x6b175474e89094c44da98b954eedeac495271d0f"
        quote = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
        start_date = "2023-09-01T00:00:00Z"
        end_date = "2023-09-02T00:00:00Z"
        result = drs.get_global_vwap_pairs_historical(
            base=base,
            quote=quote,
            start_date=start_date,
            end_date=end_date
        )
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        self.assertListEqual(list(result.index.names), ['pair', 'timestamp'], "Index keys are not as expected")


    ### 7 - DEX ALL TRANSACTIONS ###
    def test_get_protocol_lens_raw_vanilla(self):
        result = drs.get_protocol_lens_raw(protocol_id=ProtocolId.UNISWAP_V3)

        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        expected_columns = [
            'blockNumber', 'transactionHash', 'logIndex', 'timestamp', 'factoryAddress', 'walletAddress', 'event',
            'action', 'fee', 'pool', 'token0', 'token1', 'tickSpacing', 'feeNormalized', 'timeUTC', 'timeEST'
        ]
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_protocol_lens_vanilla(self):
        result = drs.get_protocol_lens(protocol_id=ProtocolId.UNISWAP_V3)

        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        # Check that 'timestamp' is a datetime object
        self.assertListEqual(list(result.index.names), ['action', 'event', 'timestamp'], "Index keys are not as expected")

    def test_get_dex_pool_lens_raw_vanilla(self):
        result = drs.get_dex_pool_lens_raw(
            protocol_id=ProtocolId.UNISWAP_V2, pool_address='0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc',
            start_date='2025-05-01', end_date='2025-05-02'
        )

        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        expected_columns = [
            'action', 'event', 'timestamp', 'blockNumber', 'transactionHash', 'logIndex', 'poolAddress', 'token0',
            'token1', 'sender', 'amount0In', 'amount1In', 'amount0Out', 'amount1Out', 'amount0InNormalized',
            'amount1InNormalized', 'amount0OutNormalized', 'amount1OutNormalized', 'to', 'timeUTC', 'timeEST',
            'amount0', 'amount1', 'amount0Normalized', 'amount1Normalized'
        ]

        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_dex_pool_lens_vanilla(self):
        result = drs.get_dex_pool_lens(
            protocol_id=ProtocolId.UNISWAP_V2, pool_address='0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc',
            start_date='2025-05-01', end_date='2025-05-02'
        )

        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        self.assertListEqual(list(result.index.names), ['action', 'event', 'timestamp'], "Index keys are not as expected")

    def test_get_dex_wallet_lens_raw_vanilla(self):
        # Call the get_wallet_lens_raw function with example values
        result = drs.get_dex_wallet_lens_raw(
            protocol_id=ProtocolId.UNISWAP_V2, wallet_address="0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc",
            start_date="2022-09-01", end_date="2022-09-02"
        )
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        expected_columns = [
            'action', 'event', 'timestamp', 'blockNumber', 'transactionHash', 'logIndex', 'poolAddress', 'token0',
            'token1', 'sender', 'amount0In', 'amount1In', 'amount0Out', 'amount1Out', 'amount0InNormalized',
            'amount1InNormalized', 'amount0OutNormalized', 'amount1OutNormalized', 'to', 'timeUTC', 'timeEST'
        ]
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_dex_wallet_lens_vanilla(self):
        # Call the get_wallet_lens function with example values
        result = drs.get_dex_wallet_lens(
            protocol_id=ProtocolId.UNISWAP_V2, wallet_address="0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc",
            start_date="2022-09-01", end_date="2022-09-02"
        )

        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        self.assertListEqual(list(result.index.names), ['action', 'event', 'timestamp'], "Index keys are not as expected")


    ### 8 - PORTFOLIO & RETURNS ###
    # TODO: Enable when columns metadata is corrected
    # def test_get_liquidity_provider_return_since_inception_raw_vanilla(self):
    #     result = drs.get_liquidity_provider_return_since_inception_raw(
    #         liquidity_pool_address='0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc',
    #         addresses="0x8409daf0d03ea176823b3c7240dc28ce371b1f8d"
    #     )
    #     self.assertIsInstance(result, pd.DataFrame)
    #     self.assertFalse(result.empty, "Dataframe is empty")
    #
    # # TODO: Enable when columns metadata is corrected
    # def test_get_liquidity_provider_return_since_inception_vanilla(self):
    #     result = drs.get_liquidity_provider_return_since_inception(
    #         liquidity_pool_address='0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc',
    #         addresses="0x8409daf0d03ea176823b3c7240dc28ce371b1f8d"
    #     )
    #     self.assertIsInstance(result, pd.DataFrame)
    #     self.assertFalse(result.empty, "Dataframe is empty")

    def test_get_liquidity_provider_historical_return_raw_vanilla(self):
        result = drs.get_liquidity_provider_historical_return_raw(
            liquidity_pool_address='0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc',
            addresses="0x8409daf0d03ea176823b3c7240dc28ce371b1f8d", start_date='2025-05-01', end_date='2025-05-02')
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        expected_columns = [
            'protocol', 'start', 'end', 'poolAddress', 'holderAddress', 'token0Address', 'token1Address', 'token0IfHeld',
            'token1IfHeld', 'token0Lp', 'token1Lp', 'change0', 'change1', 'fees0Total', 'fees1Total', 'fees0Unclaimed',
            'fees1Unclaimed', 'fees0Claimed', 'fees1Claimed', 'fees', 'feesClaimed', 'feesUnclaimed', 'impermanentLoss',
            'return', 'positionOpen'
        ]
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_liquidity_provider_historical_return_vanilla(self):
        result = drs.get_liquidity_provider_historical_return(
            liquidity_pool_address='0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc',
            addresses="0x8409daf0d03ea176823b3c7240dc28ce371b1f8d", start_date='2025-05-01', end_date='2025-05-02')
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['protocol', 'holderAddress'], "Index keys are not as expected")

    # # TODO: Enable when columns metadata is corrected
    # def test_get_liquidity_pool_total_return_raw_vanilla(self):
    #     result = drs.get_liquidity_pool_total_return_raw(
    #         address='0x0d4a11d5eeaac28ec3f61d100daf4d40471f1852',
    #         date='2025-05-01'
    #     )
    #     self.assertIsInstance(result, pd.DataFrame)
    #     self.assertFalse(result.empty, "Dataframe is empty")
    # TODO: Write actual tests
    #
    # # TODO: Enable when columns metadata is corrected
    # def test_get_liquidity_pool_total_return_vanilla(self):
    #     result = drs.get_liquidity_pool_total_return(
    #         address='0x0d4a11d5eeaac28ec3f61d100daf4d40471f1852',
    #         date='2025-05-01'
    #     )
    #     self.assertIsInstance(result, pd.DataFrame)
    #     self.assertFalse(result.empty, "Dataframe is empty")
    # TODO: Write actual tests

    def test_get_track_positions_lending_wallets_raw_vanilla(self):
        result = drs.get_track_positions_lending_wallets_raw(
            protocol_id=ProtocolId.AAVE_V2, address="0x884d6fa3a4b349880486ad4d7c833ca968c785d8"
        )
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        expected_columns = [
            'timestamp', 'totalLiquidityETH', 'totalLiquidityUSD', 'totalCollateralETH', 'totalCollateralUSD',
            'totalBorrowedETH', 'totalBorrowedUSD', 'totalLendInterestETH', 'totalLendInterestUSD', 'totalBorrowInterestETH',
            'totalBorrowInterestUSD', 'cumulativeLendInterestETH', 'cumulativeLendInterestUSD', 'cumulativeBorrowInterestETH',
            'cumulativeBorrowInterestUSD', 'availableToBorrowETH', 'availableToBorrowUSD', 'netWorthETH', 'netWorthUSD',
            'lifetimeRewardsETH', 'lifetimeRewardsUSD', 'unclaimedRewardsETH', 'unclaimedRewardsUSD', 'healthFactor',
            'loanToValueRatio', 'liquidationThresholdRatio', 'positions', 'blockchainId', 'timeUTC', 'timeEST'
        ]
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_track_positions_lending_wallets_vanilla(self):
        result = drs.get_track_positions_lending_wallets(
            protocol_id=ProtocolId.AAVE_V3, address="0x884d6fa3a4b349880486ad4d7c833ca968c785d8"
        )
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['positions'], "Index keys are not as expected")

    def test_get_profit_loss_analytics_in_defi_lending_raw_vanilla(self):
        result = drs.get_profit_loss_analytics_in_defi_lending_raw(
            wallet_address='0x884d6fa3a4b349880486ad4d7c833ca968c785d8'
        )
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        expected_columns = ['metrics', 'blockchainId']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_profit_loss_analytics_in_defi_lending_vanilla(self):
        result = drs.get_profit_loss_analytics_in_defi_lending(
            wallet_address='0x884d6fa3a4b349880486ad4d7c833ca968c785d8'
        )
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['blockchainId'], "Index keys are not as expected")

    def test_get_impermanent_loss_dex_returns_raw_vanilla(self):
        result = drs.get_impermanent_loss_dex_returns_raw(
            wallet_address='0x7e95Cde1B7270155C62450D1931ABe977BfbFe9C',
            liquidity_pool_address='0xCBCdF9626bC03E24f779434178A73a0B4bad62eD',
            protocol_name=ProtocolId.UNISWAP_V3, start_date='2024-01-23'
        )
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        expected_columns = ['timestamp', 'cumulativeFeesClaimedUSD', 'cumulativeFeesUnclaimedUSD',
                            'impermanentLossRatio', 'positions', 'byToken', 'timeUTC', 'timeEST']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_impermanent_loss_dex_returns_vanilla(self):
        result = drs.get_impermanent_loss_dex_returns(
            wallet_address='0x7e95Cde1B7270155C62450D1931ABe977BfbFe9C',
            liquidity_pool_address='0xCBCdF9626bC03E24f779434178A73a0B4bad62eD',
            protocol_name=ProtocolId.UNISWAP_V3, start_date='2024-01-23'
        )
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['timestamp'], "Index keys are not as expected")


    ### 9 - LENDING PROTOCOL METRICS ###
    def test_get_lending_protocol_summary_metrics_raw_vanilla(self):
        result = drs.get_lending_protocol_summary_metrics_raw(protocol_id=ProtocolId.AAVE_V3)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertIn('metrics', result.columns, "metrics not in columns")
        self.assertIn('blockchainId', result.columns, "blockchainId not in columns")

    def test_get_lending_protocol_summary_metrics_vanilla(self):
        result = drs.get_lending_protocol_summary_metrics(protocol_id=ProtocolId.AAVE_V3)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['blockchainId'], "Index keys are not as expected")

    def test_get_lending_asset_summary_metrics_raw_vanilla(self):
        result = drs.get_lending_asset_summary_metrics_raw(protocol_id=ProtocolId.AAVE_V3, asset_id="WETH")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertIn('metrics', result.columns, "metrics not in columns")
        self.assertIn('blockchainId', result.columns, "blockchainId not in columns")

    def test_get_lending_asset_summary_metrics_vanilla(self):
        result = drs.get_lending_asset_summary_metrics(protocol_id=ProtocolId.AAVE_V3, asset_id="WETH")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['blockchainId'], "Index keys are not as expected")


    ### 10 - LENDING ALL TRANSACTIONS ###
    # NOT
    def test_get_lending_protocol_lens_raw_vanilla(self):
        # Call the get_protocol_summary_metrics_raw function with example values
        result = drs.get_lending_protocol_lens_raw(
            protocol_id=ProtocolId.AAVE_V3,
            start_date='1746108142',
            end_date='1746194542',
            action=ProtocolAction.DEPOSIT
        )

        # Check if the result is a DataFrame
        self.assertIsInstance(result, pd.DataFrame)

        # Check if DataFrame is not empty
        self.assertFalse(result.empty, "DataFrame is empty")

        # Check for required columns
        expected_columns = [
            'action', 'timestamp', 'blockNumber', 'transactionHash', 'logIndex', 'assetId', 'assetSymbol', 'marketId',
            'market', 'amountNative', 'amountUSD', 'eMode', 'account', 'caller', 'reserve', 'blockchainId',
            'timeUTC', 'timeEST'
        ]
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_lending_protocol_lens_vanilla(self):
        # Call the get_protocol_summary_metrics function with example values
        result = drs.get_lending_protocol_lens(
            protocol_id=ProtocolId.AAVE_V2,
            start_date='1746108142',
            end_date='1746194542',
            action=ProtocolAction.DEPOSIT
        )

        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        self.assertListEqual(list(result.index.names), ['marketId', 'action'], "Index keys are not as expected")

    def test_get_lending_asset_lens_raw_vanilla(self):
        result = drs.get_lending_asset_lens_raw(
            protocol_id=ProtocolId.AAVE_V2,
            asset='WETH',
            start_date='1746108142',
            end_date='1746194542',
        )

        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")

        expected_columns = [
            'action', 'timestamp', 'blockNumber', 'transactionHash', 'logIndex', 'assetId', 'assetSymbol', 'marketId',
            'market', 'amountNative', 'amountUSD', 'account', 'caller', 'reserve', 'collateralAssetId',
            'collateralAssetSymbol', 'collateralAmountNative', 'collateralAmountUSD', 'profitUSD', 'principalAssetId',
            'principalAssetSymbol', 'principalAmountNative', 'principalAmountUSD', 'liquidatee', 'liquidator',
            'repayer', 'blockchainId', 'timeUTC', 'timeEST'
        ]
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_lending_asset_lens_vanilla(self):
        # Call the get_asset_summary_metrics function with example values
        result = drs.get_lending_asset_lens(
            protocol_id=ProtocolId.AAVE_V2,
            asset='WETH',
            start_date='1746108142',
            end_date='1746194542',
        )

        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        self.assertListEqual(list(result.index.names), ['marketId', 'action'], "Index keys are not as expected")

    def test_get_lending_wallet_lens_raw_vanilla(self):
        result = drs.get_lending_wallet_lens_raw(
            protocol_id=ProtocolId.AAVE_V2,
            wallet_address='0x1ec5878ffc42e6d5d80422bdd06cf0712e5611fd',
            start_date="2022-09-01",
            end_date="2022-10-31"
        )

        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")

        expected_columns = [
            'action', 'timestamp', 'blockNumber', 'transactionHash', 'logIndex', 'assetId', 'assetSymbol', 'marketId',
            'market', 'amountNative', 'amountUSD', 'account', 'caller', 'reserve', 'borrowRate', 'borrowRateMode',
            'repayer', 'blockchainId', 'timeUTC', 'timeEST'
        ]
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_lending_wallet_lens_vanilla(self):
        # Call the get_asset_summary_metrics function with example values
        result = drs.get_lending_wallet_lens(
            protocol_id=ProtocolId.AAVE_V2,
            wallet_address='0x1ec5878ffc42e6d5d80422bdd06cf0712e5611fd',
            start_date="2022-09-01",
            end_date="2022-10-31"
        )

        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")
        self.assertListEqual(list(result.index.names), ['marketId', 'action'], "Index keys are not as expected")

    def test_get_lending_governance_lens_raw_vanilla(self):
        result = drs.get_lending_governance_lens_raw(
            protocol_id=ProtocolId.AAVE_V2,
            start_date="2022-09-01",
            end_date="2022-09-30",
        )

        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")

        expected_columns = [
            'action', 'timestamp', 'transactionHash', 'logIndex', 'voter', 'proposalId', 'proposal', 'votingPower',
            'support', 'supportType', 'governorId', 'proposerId', 'title', 'description', 'shortDescription',
            'creatorId', 'author', 'blockchainId', 'timeUTC', 'timeEST', 'user', 'onBehalf', 'amountRaw',
            'amount', 'assetSymbol', 'powerType'
        ]
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_lending_governance_lens_vanilla(self):
        result = drs.get_lending_governance_lens(
            protocol_id=ProtocolId.AAVE_V2,
            start_date="2022-09-01",
            end_date="2022-09-30",
        )

        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "DataFrame is empty")

        self.assertListEqual(list(result.index.names), ['proposalId', 'governorId'], "Index keys are not as expected")


    ### 11 - STABLECOINS AGGREGATE INSIGHTS ###
    def test_get_stablecoins_in_defi_lending_aggregate_insights_raw_vanilla(self):
        result = drs.get_stablecoins_in_defi_lending_aggregate_insights_raw(
            asset_symbol=StableCoin.USDC
        )
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        expected_columns = ['metrics', 'blockchainId', 'protocols']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_stablecoins_in_defi_lending_aggregate_insights_vanilla(self):
        result = drs.get_stablecoins_in_defi_lending_aggregate_insights(
            asset_symbol=StableCoin.USDC
        )
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['blockchainId'], "Index keys are not as expected")


    ### 12 - INFORMATION - LENDING PROTOCOLS ###
    def test_get_information_lending_protocols_raw_vanilla(self):
        result = drs.get_information_lending_protocols_raw()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        expected_columns = ['protocolId', 'protocolName', 'protocolVersion', 'blockchain', 'numAssets',
                            'totalDepositedUSD', 'totalCollateralUSD', 'totalBorrowedUSD']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_information_lending_protocols_vanilla(self):
        result = drs.get_information_lending_protocols()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['protocolId'], "Index keys are not as expected")


    ### 13 - INFORMATION - ASSETS IN LENDING PROTOCOLS ###
    def test_get_information_assets_in_lending_protocols_raw_vanilla(self):
        result = drs.get_information_assets_in_lending_protocols_raw()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        expected_columns = [
            'protocolId', 'protocolName', 'protocolVersion', 'blockchain', 'assetId', 'assetSymbol', 'market', 'decimals',
            'borrowRateStable', 'borrowRateVariable', 'lendRate', 'totalDepositedUSD', 'totalCollateralUSD', 'totalBorrowedUSD',
            'totalLiquidationsUSD', 'loanToValueRatio', 'isActive', 'marketId'
        ]
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_information_assets_in_lending_protocols_vanilla(self):
        result = drs.get_information_assets_in_lending_protocols()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['protocolId', 'blockchain', 'assetId'], "Index keys are not as expected")

    ### 14 - INFORMATION - DEX PROTOCOLS ###
    def test_get_information_dex_protocols_raw_vanilla(self):
        result = drs.get_information_dex_protocols_raw()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        expected_columns = ['exchangeName', 'exchangeId', 'numPairs']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_information_dex_protocols_vanilla(self):
        result = drs.get_information_dex_protocols()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['exchangeId'], "Index keys are not as expected")

    ### 15 - INFORMATION - PAIRS IN DEX PROTOCOLS ###
    def test_get_information_pairs_in_dex_protocols_raw_vanilla(self):
        result = drs.get_information_pairs_in_dex_protocols_raw(exchange=DexDataVenue.SUSHISWAP)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        expected_columns = [
            'exchangeName', 'exchangeId', 'pairName', 'pairAddress', 'baseAddress', 'baseName', 'baseSymbol',
            'baseDecimals', 'quoteAddress', 'quoteName', 'quoteSymbol', 'quoteDecimals', 'poolFees', 'poolAddresses',
            'poolNames', 'poolSymbols', 'poolDecimals'
        ]
        for col in expected_columns:
            self.assertIn(col, result.columns, f"{col} not in columns")

    def test_get_information_pairs_in_dex_protocols_vanilla(self):
        result = drs.get_information_pairs_in_dex_protocols(
            exchange=DexDataVenue.SUSHISWAP
        )
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Dataframe is empty")
        self.assertListEqual(list(result.index.names), ['exchangeId', 'pairName'], "Index keys are not as expected")