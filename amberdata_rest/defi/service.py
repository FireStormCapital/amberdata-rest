import logging
from typing import Dict, List

import pandas as pd

from amberdata_rest.common import RestService, ApiKeyGetMode
from amberdata_rest.constants import (
    LendingProtocol, Blockchain, DEXSortBy,
    AMBERDATA_DEFI_REST_DEX_TRADES_HISTORICAL_ENDPOINT, AMBERDATA_DEFI_REST_DEX_PROTOCOLS_INFORMATION_ENDPOINT,
    AMBERDATA_DEFI_REST_OHLCV_INFORMATION_ENDPOINT, AMBERDATA_DEFI_REST_OHLCV_LATEST_ENDPOINT,
    AMBERDATA_DEFI_REST_OHLCV_HISTORICAL_ENDPOINT, AMBERDATA_DEFI_REST_LIQUIDITY_INFORMATION_ENDPOINT,
    AMBERDATA_DEFI_REST_LIQUIDITY_LATEST_ENDPOINT, AMBERDATA_DEFI_REST_LIQUIDITY_HISTORICAL_ENDPOINT,
    AMBERDATA_DEFI_REST_LIQUIDITY_SNAPSHOTS_ENDPOINT, AMBERDATA_DEFI_REST_UNISWAP_V3_LIQUIDITY_DISTRIBUTION_ENDPOINT,
    AMBERDATA_DEFI_REST_DEX_LIQUIDITY_POSITIONS_PAIRS_LATEST_ENDPOINT,
    AMBERDATA_DEFI_REST_DEX_LIQUIDITY_POSITIONS_PROVIDERS_LATEST_ENDPOINT,
    AMBERDATA_DEFI_REST_DEX_LIQUIDITY_PROVIDER_EVENTS_ENDPOINT, AMBERDATA_DEFI_REST_METRICS_EXCHANGES_LATEST_ENDPOINT,
    AMBERDATA_DEFI_REST_METRICS_EXCHANGES_HISTORICAL_ENDPOINT, AMBERDATA_DEFI_REST_METRICS_ASSETS_LATEST_ENDPOINT,
    AMBERDATA_DEFI_REST_METRICS_ASSETS_HISTORICAL_ENDPOINT, AMBERDATA_DEFI_REST_METRICS_PAIRS_LATEST_ENDPOINT,
    AMBERDATA_DEFI_REST_METRICS_PAIRS_HISTORICAL_ENDPOINT, AMBERDATA_DEFI_REST_ASSETS_INFORMATION_ENDPOINT,
    AMBERDATA_DEFI_REST_ASSET_LATEST_ENDPOINT, AMBERDATA_DEFI_REST_ASSET_HISTORICAL_ENDPOINT,
    AMBERDATA_DEFI_REST_PAIRS_INFORMATION_ENDPOINT, AMBERDATA_DEFI_REST_PAIRS_LATEST_ENDPOINT,
    AMBERDATA_DEFI_REST_PAIRS_HISTORICAL_ENDPOINT, AMBERDATA_DEFI_REST_TWAP_ASSETS_INFORMATION_ENDPOINT,
    AMBERDATA_DEFI_REST_TWAP_ASSET_LATEST_ENDPOINT, AMBERDATA_DEFI_REST_TWAP_ASSET_HISTORICAL_ENDPOINT,
    AMBERDATA_DEFI_REST_TWAP_PAIRS_INFORMATION_ENDPOINT, AMBERDATA_DEFI_REST_TWAP_PAIRS_LATEST_ENDPOINT,
    AMBERDATA_DEFI_REST_TWAP_PAIRS_HISTORICAL_ENDPOINT, AMBERDATA_DEFI_REST_VWAP_ASSETS_INFORMATION_ENDPOINT,
    AMBERDATA_DEFI_REST_VWAP_ASSET_LATEST_ENDPOINT, AMBERDATA_DEFI_REST_VWAP_ASSET_HISTORICAL_ENDPOINT,
    AMBERDATA_DEFI_REST_VWAP_PAIRS_INFORMATION_ENDPOINT, AMBERDATA_DEFI_REST_VWAP_PAIRS_LATEST_ENDPOINT,
    AMBERDATA_DEFI_REST_VWAP_PAIRS_HISTORICAL_ENDPOINT, AMBERDATA_DEFI_REST_PROVIDER_RETURN_SINCE_INCEPTION_ENDPOINT,
    AMBERDATA_DEFI_REST_PROVIDER_HISTORICAL_RETURN_ENDPOINT, AMBERDATA_DEFI_REST_POOL_TOTAL_RETURN_ENDPOINT,
    AMBERDATA_DEFI_REST_WALLET_POSITIONS_ENDPOINT, AMBERDATA_DEFI_REST_PROFIT_LOSS_ENDPOINT,
    AMBERDATA_DEFI_REST_IMPERMANENT_LOSS_ENDPOINT, AMBERDATA_DEFI_REST_LENDING_PROTOCOL_METRICS_ENDPOINT,
    AMBERDATA_DEFI_REST_LENDING_ASSET_METRICS_ENDPOINT,
    AMBERDATA_DEFI_REST_LENDING_STABLECOINS_AGGREGATE_INSIGHTS_ENDPOINT,
    AMBERDATA_DEFI_REST_LENDING_PROTOCOLS_INFORMATION_ENDPOINT, AMBERDATA_DEFI_REST_LENDING_ASSETS_INFORMATION_ENDPOINT,
    AMBERDATA_DEFI_REST_DEX_EXCHANGES_ENDPOINT, AMBERDATA_DEFI_REST_DEX_PAIRS_ENDPOINT,
    AMBERDATA_DEFI_REST_DEX_PROTOCOL_LENS_ENDPOINT, AMBERDATA_DEFI_REST_DEX_POOL_LENS_ENDPOINT,
    AMBERDATA_DEFI_REST_DEX_WALLET_LENS_ENDPOINT, AMBERDATA_DEFI_REST_LENDING_PROTOCOL_LENS_ENDPOINT,
    AMBERDATA_DEFI_REST_LENDING_ASSET_LENS_ENDPOINT, AMBERDATA_DEFI_REST_LENDING_WALLET_LENS_ENDPOINT,
    AMBERDATA_DEFI_REST_LENDING_GOVERNANCE_LENS_ENDPOINT, TimeFormat, DexDataVenue, TimeInterval, ProtocolId,
    ProtocolAction, SortDirection, StableCoin
)
from amberdata_rest.utils import convert_timestamp


class DefiRestService(RestService):
    def __init__(self, api_key_get_mode: ApiKeyGetMode, api_key_get_params: Dict, max_threads: int = 8):
        RestService.__init__(self, api_key_get_mode, api_key_get_params, max_threads)


    ### 1- DEX TRADES ###
    def get_dex_trades_historical_raw(self, blockchain: Blockchain, pair: str = None, start_date: str = None,
                                      end_date: str = None, protocol_name: str = None,
                                      liquidity_pool_address: str = None, asset_bought_address: str = None,
                                      asset_sold_address: str = None, wallet_address: str = None) -> pd.DataFrame:
        """
        Raw function that retrieves the historical DEX trades data.

        Args:
            blockchain: Required blockchain filter, defaults to ethereum-mainnet
            exchange: Optional exchange filter
            pair: Optional trading pair filter
            start_date: Optional start date for the time range (ISO 8601 format)
                        Example: 2025-02-05
            end_date: Optional end date for the time range (ISO 8601 format)
                      If not specified but start_date is, returns trades from start_date to now
            protocol_name: Optional filter for trades from a specific protocol
                          Use the DEX Information endpoint to see available protocols
            liquidity_pool_address: Optional filter by the smart contract address of the liquidity pool
            asset_bought_address: Optional filter by the smart contract address of the asset bought in the trade
            asset_sold_address: Optional filter by the smart contract address of the asset sold in the trade
            wallet_address: Optional filter by a specific address that was either the initiator or recipient

        Returns:
            DataFrame containing the historical DEX trades data
        """
        params = {}

        if blockchain:
            params['blockchain'] = blockchain.value
        if pair:
            params['pair'] = pair
        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        if protocol_name:
            params['protocolName'] = protocol_name
        if liquidity_pool_address:
            params['liquidityPoolAddress'] = liquidity_pool_address
        if asset_bought_address:
            params['assetBoughtAddress'] = asset_bought_address
        if asset_sold_address:
            params['assetSoldAddress'] = asset_sold_address
        if wallet_address:
            params['walletAddress'] = wallet_address

        url = AMBERDATA_DEFI_REST_DEX_TRADES_HISTORICAL_ENDPOINT
        description = "DEX Trades Historical Request"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, self._headers(), description)

        logging.info(f"Finished {description}")

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_dex_trades_historical(
            self, blockchain: Blockchain, pair: str = None, start_date: str = None, end_date: str = None,
            protocol_name: str = None,
            liquidity_pool_address: str = None, asset_bought_address: str = None,
            asset_sold_address: str = None, wallet_address: str = None,
            index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes the historical DEX trades data.

        Args:
            blockchain: Required blockchain filter, defaults to ethereum-mainnet
            exchange: Optional exchange filter
            pair: Optional trading pair filter
            start_date: Optional start date for the time range (ISO 8601 format)
                        Example: 2025-02-05
            end_date: Optional end date for the time range (ISO 8601 format)
                      If not specified but start_date is, returns trades from start_date to now
            protocol_name: Optional filter for trades from a specific protocol
                          Use the DEX Information endpoint to see available protocols
            liquidity_pool_address: Optional filter by the smart contract address of the liquidity pool
            asset_bought_address: Optional filter by the smart contract address of the asset bought in the trade
            asset_sold_address: Optional filter by the smart contract address of the asset sold in the trade
            wallet_address: Optional filter by a specific address that was either the initiator or recipient
            index_keys: Optional list of column names to use as index

        Returns:
            DataFrame containing the processed historical DEX trades data
        """
        if index_keys is None:
            index_keys = ['timestamp']

        # Get the raw data
        df = self.get_dex_trades_historical_raw(blockchain=blockchain, pair=pair, start_date=start_date,
                                                end_date=end_date, protocol_name=protocol_name,
                                                liquidity_pool_address=liquidity_pool_address,
                                                asset_bought_address=asset_bought_address,
                                                asset_sold_address=asset_sold_address, wallet_address=wallet_address)

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)

    def get_dex_protocols_information_raw(
            self, blockchain: Blockchain, protocol_name: str = None,
            active_after_date: str = None,
            liquidity_pool_address: str = None, asset_address: str = None,
            asset_symbol: str = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves information about the supported liquidity pools across blockchains and DEX protocols.

        Args:
            blockchain: Optional blockchain filter, defaults to ethereum-mainnet
            protocol_name: Optional filter for a specific protocol
            active_after_date: Optional filter by date to find liquidity pools active after the specified date
                              Example: 2025-02-05
            liquidity_pool_address: Optional filter by the smart contract address of the liquidity pool
            asset_address: Optional filter by the smart contract address for an asset of interest
            asset_symbol: Optional filter by the short-form identifier of an asset

        Returns:
            DataFrame containing the DEX protocols information
        """
        params = {}

        if blockchain:
            params['blockchain'] = blockchain.value
        if protocol_name:
            params['protocolName'] = protocol_name
        if active_after_date:
            params['activeAfterDate'] = active_after_date
        if liquidity_pool_address:
            params['liquidityPoolAddress'] = liquidity_pool_address
        if asset_address:
            params['assetAddress'] = asset_address
        if asset_symbol:
            params['assetSymbol'] = asset_symbol

        url = AMBERDATA_DEFI_REST_DEX_PROTOCOLS_INFORMATION_ENDPOINT
        description = "DEX Protocols Information Request"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, self._headers(), description)

        logging.info(f"Finished {description}")

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_dex_protocols_information(self, blockchain: Blockchain = None, protocol_name: str = None,
                                      active_after_date: str = None, liquidity_pool_address: str = None,
                                      asset_address: str = None, asset_symbol: str = None, index_keys: list = None) -> pd.DataFrame:
        """
        Processed function that retrieves and processes information about DEX protocols.

        Args:
            blockchain: Optional blockchain filter, defaults to ethereum-mainnet
            protocol_name: Optional filter for a specific protocol
            active_after_date: Optional filter by date to find liquidity pools active after the specified date
                              Example: 2025-02-05
            liquidity_pool_address: Optional filter by the smart contract address of the liquidity pool
            asset_address: Optional filter by the smart contract address for an asset of interest
            asset_symbol: Optional filter by the short-form identifier of an asset
            index_keys: Optional list of column names to use as index

        Returns:
            DataFrame containing the processed DEX protocols information
        """
        if index_keys is None:
            index_keys = ['protocolName']

        # Get the raw data
        df = self.get_dex_protocols_information_raw(
            blockchain=blockchain,
            protocol_name=protocol_name,
            active_after_date=active_after_date,
            liquidity_pool_address=liquidity_pool_address,
            asset_address=asset_address,
            asset_symbol=asset_symbol,
        )

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)


    ### 2 - OHLCV ###
    def get_ohlcv_information_raw(self, exchanges: List[DexDataVenue] = None, time_format: TimeFormat = None, size: int = None) -> pd.DataFrame:
        """
            Raw function that retrieves information about supported exchange-pairs for OHLCV.

            Args:
                exchanges: Optional filter for the specified exchange(s) (comma separated)
                         Example: uniswapv3
                time_format: Optional time format of the timestamps in the return payload
                            Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                            Defaults to milliseconds
                size: Optional number of records per page, defaults to 100

            Returns:
                DataFrame containing the OHLCV information
            """
        params = {}

        if exchanges:
            params['exchange'] = ",".join(dexVenue.value for dexVenue in exchanges)
        if time_format:
            params['timeFormat'] = time_format.value
        if size:
            params['size'] = size

        url = AMBERDATA_DEFI_REST_OHLCV_INFORMATION_ENDPOINT
        description = "DeFi OHLCV Information Request"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        response_dict = RestService.get_and_process_response_dict(url, params, self._headers(), description)

        logging.info(f"Finished {description}")

        # Extract the data from the response
        data = response_dict.get('data', {})

        # Check if the data contains the required keys
        if not data:
            logging.error(f"No data found in the response: {response_dict}")
            raise ValueError("No valid data found in the response.")

        # Process the data into a DataFrame
        df = pd.concat({k: pd.DataFrame.from_dict(v, orient='index') for k,v in data.items()})

        return df

    @convert_timestamp
    def get_ohlcv_information(
            self, exchanges: List[DexDataVenue] = None, time_format: TimeFormat = None, size: int = None, index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes information about supported exchange-pairs for OHLCV.

        Args:
            exchanges: Optional filter for the specified exchange(s) (comma separated)
                     Example: uniswapv3
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds
            size: Optional number of records per page, defaults to 100
            index_keys: Optional list of column names to use as index

        Returns:
            DataFrame containing the processed OHLCV information
        """
        if index_keys is None:
            index_keys = ['baseAddress', 'quoteAddress']

        # Get the raw data
        df = self.get_ohlcv_information_raw(exchanges=exchanges, time_format=time_format, size=size)

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)

    def get_ohlcv_latest_raw(
            self, pool: str, exchanges: List[DexDataVenue] = None, time_format: TimeFormat = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves the most current OHLCV data for a specific pool.

        Args:
            pool: Required pool to retrieve the most current data. Can be the pool/pair symbols or address.
                 Example: DAI_USDC
            exchanges: Optional exchange(s) for which to retrieve OHLCV, defaults to uniswapv2
                     Example: uniswapv3
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds

        Returns:
            DataFrame containing the latest OHLCV data
        """
        params = {}

        if exchanges:
            params['exchange'] = ",".join(dexVenue.value for dexVenue in exchanges)
        if time_format:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_DEFI_REST_OHLCV_LATEST_ENDPOINT.format(pool=pool)
        description = f"DeFi OHLCV Latest Request for pool {pool}"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        response_dict = RestService.get_and_process_response_dict(url, params, self._headers(), description)

        logging.info(f"Finished {description}")

        # Extract the data from the response
        data = response_dict.get('data', {})

        # Check if the data contains the required keys
        if not data:
            logging.error(f"No data found in the response: {response_dict}")
            raise ValueError("No valid data found in the response.")

        # Process the data into a DataFrame
        df = pd.DataFrame.from_dict(data, orient='index')
        return df

    @convert_timestamp
    def get_ohlcv_latest(
            self, pool: str, exchanges: List[DexDataVenue] = None, time_format: TimeFormat = None,
            index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes the most current OHLCV data for a specific pool.

        Args:
            pool: Required pool to retrieve the most current data. Can be the pool/pair symbols or address.
                 Example: DAI_USDC
            exchanges: Optional exchange(s) for which to retrieve OHLCV, defaults to uniswapv2
                     Example: uniswapv3
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds
            index_keys: Optional list of column names to use as index

        Returns:
            DataFrame containing the processed latest OHLCV data
        """
        if index_keys is None:
            index_keys = ['baseSymbol','quoteSymbol','exchangeName']

        # Get the raw data
        df = self.get_ohlcv_latest_raw(
            pool=pool,
            exchanges=exchanges,
            time_format=time_format
        )

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)

    def get_ohlcv_historical_raw(
            self, pool: str, exchanges: List[DexDataVenue] = None, start_date: str = None,
            end_date: str = None, time_interval: TimeInterval = None, time_format: TimeFormat = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves historical OHLCV data for a specific pool.

        Args:
            pool: Required pool to retrieve historical data. Can be the pool/pair symbols or address.
                 Example: DAI_USDC
            exchanges: Optional exchange(s) for which to retrieve OHLCV
                     Example: uniswapv2, uniswapv3
            start_date: Optional filter by pairs after this date
            end_date: Optional filter by pairs before this date
            time_interval: Optional time interval
                          Options: minutes | hours | days
                          Defaults to days
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds

        Returns:
            DataFrame containing the historical OHLCV data
        """
        params = {}

        if exchanges:
            params['exchange'] = ",".join(dexVenue.value for dexVenue in exchanges)
        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        if time_interval:
            params['timeInterval'] = time_interval.value
        if time_format:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_DEFI_REST_OHLCV_HISTORICAL_ENDPOINT.format(pool=pool)
        description = f"DeFi OHLCV Historical Request for pool {pool}"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, self._headers(), description)

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_ohlcv_historical(
            self, pool: str, exchanges: List[DexDataVenue] = None, start_date: str = None,
            end_date: str = None, time_interval: TimeInterval = None, time_format: TimeFormat = None,
            index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes historical OHLCV data for a specific pool.

        Args:
            pool: Required pool to retrieve historical data. Can be the pool/pair symbols or address.
                 Example: DAI_USDC
            exchanges: Optional exchange(s) for which to retrieve OHLCV
                     Example: uniswapv2, uniswapv3
            start_date: Optional filter by pairs after this date
            end_date: Optional filter by pairs before this date
            time_interval: Optional time interval
                          Options: minutes | hours | days
                          Defaults to days
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds
            index_keys: Optional list of column names to use as index

        Returns:
            DataFrame containing the processed historical OHLCV data
        """
        if index_keys is None:
            index_keys = ['baseAddress','quoteAddress','exchangeId','timestamp']

        # Get the raw data
        df = self.get_ohlcv_historical_raw(
            pool=pool,
            exchanges=exchanges,
            start_date=start_date,
            end_date=end_date,
            time_interval=time_interval,
            time_format=time_format
        )

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)


    ### 3 - LIQUIDITY ###
    def get_liquidity_information_raw(
            self, exchanges: List[DexDataVenue] = None, include_metadata: bool = None,
            include_dates: bool = None, time_format: TimeFormat = None, size: int = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves information about supported liquidity pools.

        Args:
            exchanges: Optional filter for the specified exchange(s) (comma separated)
                     Example: uniswapv2
            include_metadata: Optional include data for asset pair and pool information
                             Defaults to false
                             NOTE: If using this without specifying an exchange the endpoint will not return data
            include_dates: Optional include date ranges for each record
                          Defaults to false
                          NOTE: include_metadata is required for include_dates to return a valid response
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds
            size: Optional number of records per page, defaults to 100

        Returns:
            DataFrame containing the liquidity information
        """
        params = {}

        if exchanges:
            params['exchange'] = ",".join(dexVenue.value for dexVenue in exchanges)
        if include_metadata is not None:
            params['includeMetadata'] = str(include_metadata).lower()
        if include_dates is not None:
            params['includeDates'] = str(include_dates).lower()
        if time_format:
            params['timeFormat'] = time_format.value
        if size:
            params['size'] = size

        url = AMBERDATA_DEFI_REST_LIQUIDITY_INFORMATION_ENDPOINT
        description = "DeFi Liquidity Information Request"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, self._headers(), description)

        logging.info(f"Finished {description}")

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_liquidity_information(
            self, exchanges: List[DexDataVenue] = None, include_metadata: bool = None,
            include_dates: bool = None, time_format: TimeFormat = None, size: int = None,
            index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes information about supported liquidity pools.

        Args:
            exchanges: Optional filter for the specified exchange(s) (comma separated)
                     Example: uniswapv2
            include_metadata: Optional include data for asset pair and pool information
                             Defaults to false
                             NOTE: If using this without specifying an exchange the endpoint will not return data
            include_dates: Optional include date ranges for each record
                          Defaults to false
                          NOTE: include_metadata is required for include_dates to return a valid response
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds
            size: Optional number of records per page, defaults to 100
            index_keys: Optional list of column names to use as index

        Returns:
            DataFrame containing the processed liquidity information
        """
        if index_keys is None:
            index_keys = ['exchange', 'pair']

        # Get the raw data
        df = self.get_liquidity_information_raw(
            exchanges=exchanges,
            include_metadata=include_metadata,
            include_dates=include_dates,
            time_format=time_format,
            size=size
        )

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)

    def get_liquidity_latest_raw(
            self, pool: str, exchanges: List[DexDataVenue] = None, time_format: TimeFormat = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves the most current liquidity data for a specific pool.

        Args:
            pool: Required pool to retrieve the most current data. Can be the pool/pair symbols or address.
                 Example: 0xBb2b8038a1640196FbE3e38816F3e67Cba72D940 (WBTC-WETH)
            exchanges: Optional exchange(s) for which to retrieve the data, defaults to uniswapv2
                     Example: uniswapv3,curvev1
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds

        Returns:
            DataFrame containing the latest liquidity data
        """
        params = {}

        if exchanges:
            params['exchange'] = ",".join(dexVenue.value for dexVenue in exchanges)
        if time_format:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_DEFI_REST_LIQUIDITY_LATEST_ENDPOINT.format(pool=pool)
        description = f"DeFi Liquidity Latest Request for pool {pool}"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, self._headers(), description)

        logging.info(f"Finished {description}")

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_liquidity_latest(
            self, pool: str, exchanges: List[DexDataVenue] = None, time_format: TimeFormat = None,
            index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes the most current liquidity data for a specific pool.

        Args:
            pool: Required pool to retrieve the most current data. Can be the pool/pair symbols or address.
                 Example: 0xBb2b8038a1640196FbE3e38816F3e67Cba72D940 (WBTC-WETH)
            exchanges: Optional exchange(s) for which to retrieve the data, defaults to uniswapv2
                     Example: uniswapv3,curvev1
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds
            index_keys: Optional list of column names to use as index

        Returns:
            DataFrame containing the processed latest liquidity data
        """
        if index_keys is None:
            index_keys = ['exchangeName', 'address']

        # Get the raw data
        df = self.get_liquidity_latest_raw(
            pool=pool,
            exchanges=exchanges,
            time_format=time_format
        )

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)

    def get_liquidity_historical_raw(
            self, pool: str, exchanges: List[DexDataVenue] = None, start_date: str = None,
            end_date: str = None, time_format: TimeFormat = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves historical liquidity data for a specific pool.

        Args:
            pool: Required pool to retrieve historical data. Can be the pool/pair symbols or address.
                 Example: WBTC_WETH
            exchanges: Optional exchange(s) for which to retrieve the data, defaults to uniswapv2
                     Example: uniswapv3,curvev1
            start_date: Optional filter by pairs after this date
                       Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            end_date: Optional filter by pairs before this date
                     Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds

        Returns:
            DataFrame containing the historical liquidity data
        """
        params = {}

        if exchanges:
            params['exchange'] = ",".join(dexVenue.value for dexVenue in exchanges)
        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        if time_format:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_DEFI_REST_LIQUIDITY_HISTORICAL_ENDPOINT.format(pool=pool)
        description = f"DeFi Liquidity Historical Request for pool {pool}"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, self._headers(), description)

        logging.info(f"Finished {description}")

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_liquidity_historical(
            self, pool: str, exchanges: List[DexDataVenue] = None, start_date: str = None,
            end_date: str = None, time_format: TimeFormat = None,
            index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes historical liquidity data for a specific pool.

        Args:
            pool: Required pool to retrieve historical data. Can be the pool/pair symbols or address.
                 Example: WBTC_WETH
            exchanges: Optional exchange(s) for which to retrieve the data, defaults to uniswapv2
                     Example: uniswapv3,curvev1
            start_date: Optional filter by pairs after this date
                       Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            end_date: Optional filter by pairs before this date
                     Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds
            index_keys: Optional list of column names to use as index

        Returns:
            DataFrame containing the processed historical liquidity data
        """
        if index_keys is None:
            index_keys = ['exchangeId', 'address']

        # Get the raw data
        df = self.get_liquidity_historical_raw(
            pool=pool,
            exchanges=exchanges,
            start_date=start_date,
            end_date=end_date,
            time_format=time_format
        )

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)

    def get_liquidity_snapshots_raw(
            self, pool_address: str, start_date: str = None,
            end_date: str = None, time_format: TimeFormat = None, size: int = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves liquidity snapshots for a specific pool address.

        Args:
            pool_address: Required pool address to retrieve the data for
                         Example: 0xa478c2975ab1ea89e8196811f51a7b7ade33eb11 (DAI/ETH on uniswapv2)
            start_date: Optional filter by pairs after this date
            end_date: Optional filter by pairs before this date
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds
            size: Optional number of records per page, defaults to 50
                 Recommended maximum page size is 50

        Returns:
            DataFrame containing the liquidity snapshots data
        """
        params = {}

        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        if time_format:
            params['timeFormat'] = time_format.value
        if size:
            params['size'] = size

        url = AMBERDATA_DEFI_REST_LIQUIDITY_SNAPSHOTS_ENDPOINT.format(poolAddress=pool_address)
        description = f"DeFi Liquidity Snapshots Request for pool address {pool_address}"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, self._headers(), description)

        logging.info(f"Finished {description}")

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_liquidity_snapshots(
            self, pool_address: str, start_date: str = None,
            end_date: str = None, time_format: TimeFormat = None, size: int = None,
            index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes liquidity snapshots for a specific pool address.

        Args:
            pool_address: Required pool address to retrieve the data for
                         Example: 0xa478c2975ab1ea89e8196811f51a7b7ade33eb11 (DAI/ETH on uniswapv2)
            start_date: Optional filter by pairs after this date
            end_date: Optional filter by pairs before this date
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds
            size: Optional number of records per page, defaults to 50
                 Recommended maximum page size is 50
            index_keys: Optional list of column names to use as index

        Returns:
            DataFrame containing the processed liquidity snapshots data
        """
        if index_keys is None:
            index_keys = ['blockNumber', 'exchangeName', 'poolName']

        # Get the raw data
        df = self.get_liquidity_snapshots_raw(
            pool_address=pool_address,
            start_date=start_date,
            end_date=end_date,
            time_format=time_format,
            size=size
        )

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)

    def get_uniswap_v3_liquidity_distribution_raw(
            self, pool_address: str, active_tick: bool = None,
            price0_usd_min: float = None, price0_usd_max: float = None,
            price1_usd_min: float = None, price1_usd_max: float = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves liquidity distribution data for a Uniswap V3 pool.

        Args:
            pool_address: Required pool address to retrieve the data for
                         Example: 0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640 (USDC/WETH 0.05%)
            active_tick: Optional when set to true, return just the current trading price,
                        tickIndex, and the associated data
                        Cannot be combined with price*USD{Min|Max} filters
            price0_usd_min: Optional minimum (inclusive) price of token 0 in US dollars
                           Defaults to 0.95
            price0_usd_max: Optional maximum (exclusive) price of token 0 in US dollars
                           Defaults to 1.05
            price1_usd_min: Optional minimum (inclusive) price of token 1 in US dollars
            price1_usd_max: Optional maximum (exclusive) price of token 1 in US dollars

        Returns:
            DataFrame containing the Uniswap V3 liquidity distribution data
        """
        params = {}

        if active_tick is not None:
            params['activeTick'] = str(active_tick).lower()
        if price0_usd_min is not None:
            params['price0USDMin'] = price0_usd_min
        if price0_usd_max is not None:
            params['price0USDMax'] = price0_usd_max
        if price1_usd_min is not None:
            params['price1USDMin'] = price1_usd_min
        if price1_usd_max is not None:
            params['price1USDMax'] = price1_usd_max

        url = AMBERDATA_DEFI_REST_UNISWAP_V3_LIQUIDITY_DISTRIBUTION_ENDPOINT.format(poolAddress=pool_address)
        description = f"Uniswap V3 Liquidity Distribution Request for pool address {pool_address}"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, self._headers(), description)

        logging.info(f"Finished {description}")

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_uniswap_v3_liquidity_distribution(
            self, pool_address: str, active_tick: bool = None,
            price0_usd_min: float = None, price0_usd_max: float = None,
            price1_usd_min: float = None, price1_usd_max: float = None,
            index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes liquidity distribution data for a Uniswap V3 pool.

        Args:
            pool_address: Required pool address to retrieve the data for
                         Example: 0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640 (USDC/WETH 0.05%)
            active_tick: Optional when set to true, return just the current trading price,
                        tickIndex, and the associated data
                        Cannot be combined with price*USD{Min|Max} filters
            price0_usd_min: Optional minimum (inclusive) price of token 0 in US dollars
                           Defaults to 0.95
            price0_usd_max: Optional maximum (exclusive) price of token 0 in US dollars
                           Defaults to 1.05
            price1_usd_min: Optional minimum (inclusive) price of token 1 in US dollars
            price1_usd_max: Optional maximum (exclusive) price of token 1 in US dollars
            index_keys: Optional list of column names to use as index

        Returns:
            DataFrame containing the processed Uniswap V3 liquidity distribution data
        """
        if index_keys is None:
            index_keys = ['isActiveTick', 'tickIndex']

        # Get the raw data
        df = self.get_uniswap_v3_liquidity_distribution_raw(
            pool_address=pool_address,
            active_tick=active_tick,
            price0_usd_min=price0_usd_min,
            price0_usd_max=price0_usd_max,
            price1_usd_min=price1_usd_min,
            price1_usd_max=price1_usd_max
        )

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)



    ### 6 - Price/TWAP/VWAP ###
    ## ASSETS ##
    def get_assets_information_raw(self) -> pd.DataFrame:
        """
        Raw function that retrieves the list of available market asset price data sets.
        """
        url = AMBERDATA_DEFI_REST_ASSETS_INFORMATION_ENDPOINT
        description = "DeFi Assets Information Request"
        logging.info(f"Starting {description}")

        df = RestService.get_and_process_response_df(url, {}, self._headers(), description)
        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_assets_information(self, index_keys: list = None) -> pd.DataFrame:
        """
        Processed function that retrieves and processes the list of all available market asset price data sets
        into a structured DataFrame.
        """
        if index_keys is None:
            index_keys = ['address']

        df = self.get_assets_information_raw()
        return df.set_index(index_keys)

    def get_asset_latest_raw(self, asset: str, lookback_period: int = None, time_format: TimeFormat = None) -> pd.DataFrame:
        """
        Raw function that retrieves the latest price for the specified DeFi asset.

        Parameters:
            asset (str): The asset symbol or address (e.g., '0x6b175474e89094c44da98b954eedeac495271d0f' for DAI). Required.
            time_format (str): The format of the timestamp in the response. Defaults to 'milliseconds'.

        Returns:
            pd.DataFrame: DataFrame containing the latest price data for the asset.

        Raises:
            ValueError: If 'asset' parameter is not provided or no valid data is found.
            :param lookback_period:
        """
        if not asset:
            raise ValueError("Parameter 'asset' is required.")

        params = {}
        if time_format:
            params['timeFormat'] = time_format.value
        if lookback_period:
            params['lookbackPeriod'] = lookback_period

        url = AMBERDATA_DEFI_REST_ASSET_LATEST_ENDPOINT.format(asset=asset)
        description = "DeFi Asset Latest Price Request"

        logging.info(f"Starting {description}")

        headers = self._headers()

        # Fetch the response as a dictionary
        response_dict = RestService.get_and_process_response_dict(url, params, headers, description)

        logging.info(f"Finished {description}")

        # Extract the data from the response
        data = response_dict.get('data', {})

        # Check if the data contains the required keys
        if not data:
            logging.error(f"No data found in the response: {response_dict}")
            raise ValueError("No valid data found in the response.")

        # Process the data into a DataFrame
        df = pd.DataFrame([data])

        return df

    @convert_timestamp
    def get_asset_latest(self, asset: str, lookback_period: int = None, time_format: TimeFormat = None, index_keys: list = None) -> pd.DataFrame:
        """
        Processed function that retrieves and processes the latest price data for the specified DeFi asset.

        Parameters:
            asset (str): The asset symbol or address. Required.
            time_format (str): The format of the timestamp in the response. Defaults to 'milliseconds'.
            index_keys (list): List of column names to set as the DataFrame index. Defaults to ['asset'].

        Returns:
            pd.DataFrame: Processed DataFrame containing the latest price data for the asset.

        Raises:
            ValueError: If 'asset' parameter is not provided or no valid data is found.
            :param lookback_period:
        """
        if index_keys is None:
            index_keys = ['asset']

        df = self.get_asset_latest_raw(asset, lookback_period, time_format)
        df = df.set_index(index_keys)

        return df

    def get_asset_historical_raw(self, asset: str, start_date: str = None, end_date: str = None, lookback_period: int = None,
                                 time_interval: TimeInterval = None, time_format: TimeFormat = None) -> pd.DataFrame:
        """
        Raw function that retrieves the historical price data for the specified DeFi asset.

        Parameters:
            asset (str): The asset symbol or address. Required.
            start_date (str): Include data after this date (inclusive). Optional.
            end_date (str): Include data before this date (exclusive). Optional.
            time_interval (str): The time interval for the historical data ('minutes', 'hours', 'days'). Defaults to 'minutes'.
            time_format (str): The format of the timestamp in the response. Defaults to 'milliseconds'.

        Returns:
            pd.DataFrame: DataFrame containing the historical price data for the asset.

        Raises:
            ValueError: If 'asset' parameter is not provided or no valid data is found.
            :param lookback_period:
        """
        if not asset:
            raise ValueError("Parameter 'asset' is required.")

        params = {}
        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        if time_interval:
            params['timeInterval'] = time_interval.value
        if lookback_period:
            params['lookbackPeriod'] = lookback_period
        if time_format:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_DEFI_REST_ASSET_HISTORICAL_ENDPOINT.format(asset=asset)
        description = "DeFi Asset Historical Price Request"

        logging.info(f"Starting {description}")

        headers = self._headers()

        # Fetch the response as a dictionary
        response_dict = RestService.get_and_process_response_dict(url, params, headers, description)

        logging.info(f"Finished {description}")

        # Extract the data directly from the response
        data = response_dict.get('data', [])

        if not data:
            logging.error(f"No data found in the response: {response_dict}")
            raise ValueError("No valid data found in the response.")

        df = pd.DataFrame(data)

        return df

    @convert_timestamp
    def get_asset_historical(self, asset: str, start_date: str = None, end_date: str = None, lookback_period: int = None,
                             time_interval: TimeInterval = None, time_format: TimeFormat = None, index_keys: list = None) -> pd.DataFrame:
        """
        Processed function that retrieves and processes the historical price data for the specified DeFi asset.

        Parameters:
            asset (str): The asset symbol or address. Required.
            start_date (str): Include data after this date (inclusive). Optional.
            end_date (str): Include data before this date (exclusive). Optional.
            time_interval (str): The time interval for the historical data ('minutes', 'hours', 'days'). Defaults to 'minutes'.
            time_format (str): The format of the timestamp in the response. Defaults to 'milliseconds'.
            index_keys (list): List of column names to set as the DataFrame index. Defaults to ['timestamp'].

        Returns:
            pd.DataFrame: Processed DataFrame containing the historical price data for the asset.

        Raises:
            ValueError: If 'asset' parameter is not provided or no valid data is found.
            :param lookback_period:
        """
        if index_keys is None:
            index_keys = ['timestamp']

        df = self.get_asset_historical_raw(asset, start_date, end_date, time_interval=time_interval, lookback_period=lookback_period,
                                           time_format=time_format)
        df = df.set_index(index_keys)

        return df

    ## PAIRS ##
    def get_pairs_information_raw(
            self, size: int = None, time_format: TimeFormat = None,
            base: str = None, quote: str = None, end_date_gte: str = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves the list of all available DeFi pair price data sets.

        Parameters:
            size (int): The number of records to retrieve. Defaults to 1000.
            time_format (str): The format of the timestamp in the response. Defaults to 'milliseconds'.
            base (str): The base asset address. Optional.
            quote (str): The quote asset address. Optional.
            end_date_gte (str): Include pairs with end dates greater than or equal to this date. Optional.

        Returns:
            pd.DataFrame: DataFrame containing the pairs information.

        Raises:
            ValueError: If no valid data is found in the response.
        """
        params = {}

        if time_format:
            params['timeFormat'] = time_format.value
        if size:
            params['size'] = size
        if base:
            params['base'] = base
        if quote:
            params['quote'] = quote
        if end_date_gte:
            params['endDateGte'] = end_date_gte

        url = AMBERDATA_DEFI_REST_PAIRS_INFORMATION_ENDPOINT
        description = "DeFi Pairs Information Request"
        logging.info(f"Starting {description}")

        headers = self._headers()

        df = RestService.get_and_process_response_df(url, params, headers, description)
        logging.info(f"Finished {description}")

        return df

    @convert_timestamp
    def get_pairs_information(
            self, size: int = None, time_format: TimeFormat = None,
            base: str = None, quote: str = None,
            end_date_gte: str = None, index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes the list of all available DeFi pair price data sets
        into a structured DataFrame.

        Parameters:
            size (int): The number of records to retrieve. Defaults to 1000.
            time_format (str): The format of the timestamp in the response. Defaults to 'milliseconds'.
            base (str): The base asset address. Optional.
            quote (str): The quote asset address. Optional.
            end_date_gte (str): Include pairs with end dates greater than or equal to this date. Optional.
            index_keys (list): List of column names to set as the DataFrame index. Defaults to ['baseAddress', 'quoteAddress'].

        Returns:
            pd.DataFrame: Processed DataFrame containing the pairs information.

        Raises:
            ValueError: If no valid data is found in the response.
        """
        if index_keys is None:
            index_keys = ['baseAddress', 'quoteAddress']

        df = self.get_pairs_information_raw(
            size=size,
            time_format=time_format,
            base=base,
            quote=quote,
            end_date_gte=end_date_gte
        )

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)

    def get_pairs_latest_raw(self, base: str, quote: str, time_format: TimeFormat = None) -> pd.DataFrame:
        """
        Raw function that retrieves the latest price for the specified pair.

        Parameters:
            base (str): The base asset address. Required.
            quote (str): The quote asset address. Required.
            time_format (str): The format of the timestamp in the response. Defaults to 'milliseconds'.

        Returns:
            pd.DataFrame: DataFrame containing the latest price data for the pair.

        Raises:
            ValueError: If required parameters are not provided or no valid data is found.
        """
        if not base:
            raise ValueError("Parameter 'base' is required.")
        if not quote:
            raise ValueError("Parameter 'quote' is required.")

        params = {}
        if time_format:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_DEFI_REST_PAIRS_LATEST_ENDPOINT.format(base=base, quote=quote)
        description = "DeFi Pairs Latest Price Request"
        logging.info(f"Starting {description}")

        headers = self._headers()

        # Fetch the response as a dictionary
        response_dict = RestService.get_and_process_response_dict(url, params, headers, description)
        logging.info(f"Finished {description}")

        # Extract the data from the response
        data = response_dict.get('data', {})

        if not data:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

        df = pd.DataFrame([data])

        return df

    @convert_timestamp
    def get_pairs_latest(self, base: str, quote: str, time_format: TimeFormat = None, index_keys: list = None) -> pd.DataFrame:
        """
        Processed function that retrieves and processes the latest price for the specified pair.

        Parameters:
            base (str): The base asset address. Required.
            quote (str): The quote asset address. Required.
            time_format (str): The format of the timestamp in the response. Defaults to 'milliseconds'.
            index_keys (list): List of column names to set as the DataFrame index. Defaults to ['pair'].

        Returns:
            pd.DataFrame: Processed DataFrame containing the latest price data for the pair.

        Raises:
            ValueError: If required parameters are not provided or no valid data is found.
        """
        if index_keys is None:
            index_keys = ['pair']

        df = self.get_pairs_latest_raw(base, quote, time_format)
        df = df.set_index(index_keys)

        return df

    def get_pairs_historical_raw(
            self, base: str, quote: str, start_date: str = None, end_date: str = None,
            time_interval: TimeInterval = None, time_format: TimeFormat = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves the historical price data for the specified pair.

        Parameters:
            base (str): The base asset address. Required.
            quote (str): The quote asset address. Required.
            start_date (str): Include data after this date (inclusive). Optional.
            end_date (str): Include data before this date (exclusive). Optional.
            time_interval (str): The time interval for the historical data ('minutes', 'hours', 'days'). Defaults to 'minutes'.
            time_format (str): The format of the timestamp in the response. Defaults to 'milliseconds'.

        Returns:
            pd.DataFrame: DataFrame containing the historical price data for the pair.

        Raises:
            ValueError: If required parameters are not provided or no valid data is found.
        """
        if not base:
            raise ValueError("Parameter 'base' is required.")
        if not quote:
            raise ValueError("Parameter 'quote' is required.")

        params = {}
        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        if time_interval:
            params['timeInterval'] = time_interval.value
        if time_format:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_DEFI_REST_PAIRS_HISTORICAL_ENDPOINT.format(base=base, quote=quote)
        description = "DeFi Pairs Historical Price Request"
        logging.info(f"Starting {description}")

        headers = self._headers()

        # Fetch the response as a dictionary
        df = RestService.get_and_process_response_df(url, params, headers, description)
        logging.info(f"Finished {description}")

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_pairs_historical(
            self, base: str, quote: str, start_date: str = None, end_date: str = None,
            time_interval: TimeInterval = None, time_format: TimeFormat = None, index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes the historical price data for the specified pair.

        Parameters:
            base (str): The base asset address. Required.
            quote (str): The quote asset address. Required.
            start_date (str): Include data after this date (inclusive). Optional.
            end_date (str): Include data before this date (exclusive). Optional.
            time_interval (str): The time interval for the historical data ('minutes', 'hours', 'days'). Defaults to 'minutes'.
            time_format (str): The format of the timestamp in the response. Defaults to 'milliseconds'.
            index_keys (list): List of column names to set as the DataFrame index. Defaults to ['timestamp'].

        Returns:
            pd.DataFrame: Processed DataFrame containing the historical price data for the pair.

        Raises:
            ValueError: If required parameters are not provided or no valid data is found.
        """
        if index_keys is None:
            index_keys = ['timestamp']

        df = self.get_pairs_historical_raw(
            base=base, quote=quote, start_date=start_date, end_date=end_date,
            time_interval=time_interval, time_format=time_format
        )

        df = df.set_index(index_keys)

        return df

    ## GLOBAL TWAP ###
    def get_global_twap_assets_information_raw(self) -> pd.DataFrame:
        """
        Raw function that retrieves the list of all available market asset TWAP data sets.

        Returns:
            pd.DataFrame: DataFrame containing the assets TWAP information.

        Raises:
            ValueError: If no valid data is found in the response.
        """

        url = AMBERDATA_DEFI_REST_TWAP_ASSETS_INFORMATION_ENDPOINT
        description = "Global TWAP Assets Information Request"

        logging.info(f"Starting {description}")

        headers = self._headers()
        df = RestService.get_and_process_response_df(url, {}, headers, description)

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_global_twap_assets_information(self, index_keys: list = None) -> pd.DataFrame:
        """
        Processed function that retrieves and processes the list of all available market asset TWAP data sets.

        Parameters:
            index_keys (list): List of column names to set as the DataFrame index. Defaults to ['address'].

        Returns:
            pd.DataFrame: Processed DataFrame containing the assets TWAP information.

        Raises:
            ValueError: If no valid data is found in the response.
        """
        if index_keys is None:
            index_keys = ['address']

        df = self.get_global_twap_assets_information_raw()
        df = df.set_index(index_keys)

        return df

    def get_global_twap_asset_latest_raw(
            self, asset: str, lookback_period: int = None, time_format: TimeFormat = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves the latest TWAP for the specified asset.

        Parameters:
            asset (str): The asset address. Required.
            lookback_period (int): The lookback period in minutes. Defaults to 60.
            time_format (str): The format of the timestamp in the response. Defaults to 'milliseconds'.

        Returns:
            pd.DataFrame: DataFrame containing the latest TWAP data for the asset.

        Raises:
            ValueError: If required parameters are not provided or no valid data is found.
        """
        if not asset:
            raise ValueError("Parameter 'asset' is required.")

        params = {
            'lookbackPeriod': lookback_period,
            'timeFormat': time_format
        }

        if lookback_period:
            params['lookbackPeriod'] = lookback_period
        if time_format:
            params['timeFormat'] = time_format.value


        url = AMBERDATA_DEFI_REST_TWAP_ASSET_LATEST_ENDPOINT.format(asset=asset)
        description = "Global TWAP Asset Latest Request"

        logging.info(f"Starting {description}")

        headers = self._headers()
        df = RestService.get_and_process_response_df(url, params, headers, description)

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_global_twap_asset_latest(
            self, asset: str, lookback_period: int = None, time_format: TimeFormat = None, index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes the latest TWAP data for the specified asset.

        Parameters:
            asset (str): The asset address. Required.
            lookback_period (int): The lookback period in minutes. Defaults to 60.
            time_format (str): The format of the timestamp in the response. Defaults to 'milliseconds'.
            index_keys (list): List of column names to set as the DataFrame index. Defaults to ['timestamp'].

        Returns:
            pd.DataFrame: Processed DataFrame containing the latest TWAP data for the asset.

        Raises:
            ValueError: If required parameters are not provided or no valid data is found.
        """
        if index_keys is None:
            index_keys = ['timestamp']

        df = self.get_global_twap_asset_latest_raw(asset, lookback_period, time_format)
        df = df.set_index(index_keys)

        return df

    def get_global_twap_asset_historical_raw(
            self, asset: str, start_date: str = None, end_date: str = None,
            time_interval: TimeInterval = None, lookback_period: int = None, time_format: TimeFormat = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves the historical TWAP data for the specified asset.

        Parameters:
            asset (str): The asset address. Required.
            start_date (str): Include data after this date (inclusive). Optional.
            end_date (str): Include data before this date (exclusive). Optional.
            time_interval (str): The time interval for the historical data ('minutes', 'hours', 'days'). Defaults to 'minutes'.
            lookback_period (int): The lookback period in minutes. Defaults to 60.
            time_format (str): The format of the timestamp in the response. Defaults to 'milliseconds'.

        Returns:
            pd.DataFrame: DataFrame containing the historical TWAP data for the asset.

        Raises:
            ValueError: If required parameters are not provided or no valid data is found.
        """
        if not asset:
            raise ValueError("Parameter 'asset' is required.")

        params = {}

        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        if time_interval:
            params['timeInterval'] = time_interval.value
        if lookback_period:
            params['lookbackPeriod'] = lookback_period
        if time_format:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_DEFI_REST_TWAP_ASSET_HISTORICAL_ENDPOINT.format(asset=asset)
        description = "Global TWAP Asset Historical Request"

        logging.info(f"Starting {description}")

        headers = self._headers()
        df = RestService.get_and_process_response_df(url, params, headers, description)

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_global_twap_asset_historical(
            self, asset: str, start_date: str = None, end_date: str = None, time_interval: TimeInterval = None,
            lookback_period: int = None, time_format: TimeFormat = None, index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes the historical TWAP data for the specified asset.

        Parameters:
            asset (str): The asset address. Required.
            start_date (str): Include data after this date (inclusive). Optional.
            end_date (str): Include data before this date (exclusive). Optional.
            time_interval (str): The time interval for the historical data ('minutes', 'hours', 'days'). Defaults to 'minutes'.
            lookback_period (int): The lookback period in minutes. Defaults to 60.
            time_format (str): The format of the timestamp in the response. Defaults to 'milliseconds'.
            index_keys (list): List of column names to set as the DataFrame index. Defaults to ['timestamp'].

        Returns:
            pd.DataFrame: Processed DataFrame containing the historical TWAP data for the asset.

        Raises:
            ValueError: If required parameters are not provided or no valid data is found.
        """
        if index_keys is None:
            index_keys = ['timestamp']

        df = self.get_global_twap_asset_historical_raw(
            asset, start_date, end_date, time_interval, lookback_period, time_format
        )

        df = df.set_index(index_keys)

        return df

    def get_global_twap_pairs_information_raw(
            self, time_format: TimeFormat = None,
            base: str = None, quote: str = None, size: int = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves the list of all available DeFi pair TWAP data sets.

        Parameters:
            time_format (str): The format of the timestamp in the response. Defaults to 'milliseconds'.
            base (str): The base asset address. Optional.
            quote (str): The quote asset address. Optional.
            size (int): The number of records to retrieve. Defaults to 1000.

        Returns:
            pd.DataFrame: DataFrame containing the pairs TWAP information.

        Raises:
            ValueError: If no valid data is found in the response.
        """
        params = {}
        if time_format:
            params['timeFormat'] = time_format.value
        if size:
            params['size'] = size
        if base:
            params['base'] = base
        if quote:
            params['quote'] = quote

        url = AMBERDATA_DEFI_REST_TWAP_PAIRS_INFORMATION_ENDPOINT
        description = "Global TWAP Pairs Information Request"

        logging.info(f"Starting {description}")

        headers = self._headers()
        df = RestService.get_and_process_response_df(url, params, headers, description)

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_global_twap_pairs_information(
            self, time_format: TimeFormat = None,
            base: str = None, quote: str = None, size: int = None, index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes the list of all available DeFi pair TWAP data sets.

        Parameters:
            time_format (str): The format of the timestamp in the response. Defaults to 'milliseconds'.
            base (str): The base asset address. Optional.
            quote (str): The quote asset address. Optional.
            size (int): The number of records to retrieve. Defaults to 1000.
            index_keys (list): List of column names to set as the DataFrame index. Defaults to ['baseAddress', 'quoteAddress'].

        Returns:
            pd.DataFrame: Processed DataFrame containing the pairs TWAP information.

        Raises:
            ValueError: If no valid data is found in the response.
        """
        if index_keys is None:
            index_keys = ['baseAddress', 'quoteAddress']

        df = self.get_global_twap_pairs_information_raw(time_format, base, quote, size)
        df = df.set_index(index_keys)

        return df

    def get_global_twap_pairs_latest_raw(
            self, base: str, quote: str,
            lookback_period: int = None, time_format: TimeFormat = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves the latest TWAP data for the specified base-quote pair.

        Parameters:
            base (str): The base asset address. Required.
            quote (str): The quote asset address. Required.
            lookback_period (int): The lookback period in minutes. Defaults to 60.
            time_format (str): The format of the timestamp in the response. Defaults to 'milliseconds'.

        Returns:
            pd.DataFrame: DataFrame containing the latest TWAP data for the pair.

        Raises:
            ValueError: If required parameters are not provided or no valid data is found.
        """
        if not base:
            raise ValueError("Parameter 'base' is required.")
        if not quote:
            raise ValueError("Parameter 'quote' is required.")

        params = {}

        if lookback_period:
            params['lookbackPeriod'] = lookback_period
        if time_format:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_DEFI_REST_TWAP_PAIRS_LATEST_ENDPOINT.format(base=base, quote=quote)
        description = "Global TWAP Pairs Latest Request"

        logging.info(f"Starting {description}")

        headers = self._headers()
        df = RestService.get_and_process_response_df(url, params, headers, description)

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_global_twap_pairs_latest(
            self, base: str, quote: str,
            lookback_period: int = None, time_format: TimeFormat = None, index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes the latest TWAP data for the specified base-quote pair.

        Parameters:
            base (str): The base asset address. Required.
            quote (str): The quote asset address. Required.
            lookback_period (int): The lookback period in minutes. Defaults to 60.
            time_format (str): The format of the timestamp in the response. Defaults to 'milliseconds'.
            index_keys (list): List of column names to set as the DataFrame index. Defaults to ['timestamp'].

        Returns:
            pd.DataFrame: Processed DataFrame containing the latest TWAP data for the pair.

        Raises:
            ValueError: If required parameters are not provided or no valid data is found.
        """
        if index_keys is None:
            index_keys = ['pair']

        df = self.get_global_twap_pairs_latest_raw(base, quote, lookback_period, time_format)
        df = df.set_index(index_keys)

        return df

    def get_global_twap_pairs_historical_raw(
            self, base: str, quote: str, start_date: str = None, end_date: str = None,
            time_interval: TimeInterval = None, lookback_period: int = None, time_format: TimeFormat = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves the historical TWAP data for the specified base-quote pair.

        Parameters:
            base (str): The base asset address. Required.
            quote (str): The quote asset address. Required.
            start_date (str): Include data after this date (inclusive). Optional.
            end_date (str): Include data before this date (exclusive). Optional.
            time_interval (str): The time interval for the historical data ('minutes', 'hours', 'days'). Defaults to 'minutes'.
            lookback_period (int): The lookback period in minutes. Defaults to 60.
            time_format (str): The format of the timestamp in the response. Defaults to 'milliseconds'.

        Returns:
            pd.DataFrame: DataFrame containing the historical TWAP data for the pair.

        Raises:
            ValueError: If required parameters are not provided or no valid data is found.
        """
        if not base:
            raise ValueError("Parameter 'base' is required.")
        if not quote:
            raise ValueError("Parameter 'quote' is required.")

        params = {}

        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        if time_interval:
            params['timeInterval'] = time_interval.value
        if lookback_period:
            params['lookbackPeriod'] = lookback_period
        if time_format:
            params['timeFormat'] = time_format.value


        url = AMBERDATA_DEFI_REST_TWAP_PAIRS_HISTORICAL_ENDPOINT.format(base=base, quote=quote)
        description = "Global TWAP Pairs Historical Request"

        logging.info(f"Starting {description}")

        headers = self._headers()
        df = RestService.get_and_process_response_df(url, params, headers, description)

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_global_twap_pairs_historical(
            self, base: str, quote: str, start_date: str = None, end_date: str = None,
            time_interval: TimeInterval = None, lookback_period: int = None, time_format: TimeFormat = None, index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes historical TWAP data for the specified base-quote pair.

        Parameters:
            base (str): The base asset address. Required.
            quote (str): The quote asset address. Required.
            start_date (str): Include data after this date (inclusive). Optional.
            end_date (str): Include data before this date (exclusive). Optional.
            time_interval (str): The time interval for the historical data ('minutes', 'hours', 'days'). Defaults to 'minutes'.
            lookback_period (int): The lookback period in minutes. Defaults to 60.
            time_format (str): The format of the timestamp in the response. Defaults to 'milliseconds'.
            index_keys (list): List of column names to set as the DataFrame index. Defaults to ['timestamp'].

        Returns:
            pd.DataFrame: Processed DataFrame containing the historical TWAP data for the pair.

        Raises:
            ValueError: If required parameters are not provided or no valid data is found.
        """
        if index_keys is None:
            index_keys = ['pair']

        df = self.get_global_twap_pairs_historical_raw(
            base, quote, start_date, end_date, time_interval, lookback_period, time_format
        )

        df = df.set_index(index_keys)

        return df

    ## GLOBAL VWAP ##
    def get_global_vwap_assets_information_raw(self) -> pd.DataFrame:
        """
        Raw function that retrieves the list of all available market asset VWAP data sets.

        Returns:
            pd.DataFrame: DataFrame containing the assets VWAP information.

        Raises:
            ValueError: If no valid data is found in the response.
        """
        url = AMBERDATA_DEFI_REST_VWAP_ASSETS_INFORMATION_ENDPOINT
        description = "Global VWAP Assets Information Request"

        logging.info(f"Starting {description}")

        headers = self._headers()
        df = RestService.get_and_process_response_df(url, {}, headers, description)

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_global_vwap_assets_information(self, index_keys: list = None) -> pd.DataFrame:
        """
        Processed function that retrieves and processes the list of all available market asset VWAP data sets.

        Parameters:
            index_keys (list): List of column names to set as the DataFrame index. Defaults to ['address'].

        Returns:
            pd.DataFrame: Processed DataFrame containing the assets VWAP information.

        Raises:
            ValueError: If no valid data is found in the response.
        """
        if index_keys is None:
            index_keys = ['address']

        df = self.get_global_vwap_assets_information_raw()
        df = df.set_index(index_keys)

        return df

    def get_global_vwap_assets_latest_raw(
            self, asset: str, lookback_period: int = None, time_format: TimeFormat = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves the latest VWAP data for the specified asset.

        Parameters:
            asset (str): The asset address. Required.
            lookback_period (int): The lookback period in minutes. Defaults to 60.
            time_format (str): The format of the timestamp in the response. Defaults to 'milliseconds'.

        Returns:
            pd.DataFrame: DataFrame containing the latest VWAP data for the asset.

        Raises:
            ValueError: If required parameters are not provided or no valid data is found.
        """
        if not asset:
            raise ValueError("Parameter 'asset' is required.")

        params = {}

        if lookback_period:
            params['lookbackPeriod'] = lookback_period
        if time_format:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_DEFI_REST_VWAP_ASSET_LATEST_ENDPOINT.format(asset=asset)
        description = "Global VWAP Asset Latest Request"

        logging.info(f"Starting {description}")

        headers = self._headers()
        df = RestService.get_and_process_response_df(url, params, headers, description)

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_global_vwap_assets_latest(
            self, asset: str, lookback_period: int = None, time_format: TimeFormat = None, index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes the latest VWAP data for the specified asset.

        Parameters:
            asset (str): The asset address. Required.
            lookback_period (int): The lookback period in minutes. Defaults to 60.
            time_format (str): The format of the timestamp in the response. Defaults to 'milliseconds'.
            index_keys (list): List of column names to set as the DataFrame index. Defaults to ['timestamp'].

        Returns:
            pd.DataFrame: Processed DataFrame containing the latest VWAP data for the asset.

        Raises:
            ValueError: If required parameters are not provided or no valid data is found.
        """
        if index_keys is None:
            index_keys = ['asset']

        df = self.get_global_vwap_assets_latest_raw(asset, lookback_period, time_format)
        df = df.set_index(index_keys)

        return df

    def get_global_vwap_asset_historical_raw(
            self, asset: str, start_date: str = None, end_date: str = None,
            time_interval: TimeInterval = None, lookback_period: int = None, time_format: TimeFormat = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves the historical VWAP data for the specified asset.

        Parameters:
            asset (str): The asset address. Required.
            start_date (str): Include data after this date (inclusive). Optional.
            end_date (str): Include data before this date (exclusive). Optional.
            time_interval (str): The time interval for the historical data ('minutes', 'hours', 'days'). Defaults to 'minutes'.
            lookback_period (int): The lookback period in minutes. Defaults to 60.
            time_format (str): The format of the timestamp in the response. Defaults to 'milliseconds'.

        Returns:
            pd.DataFrame: DataFrame containing the historical VWAP data for the asset.

        Raises:
            ValueError: If required parameters are not provided or no valid data is found.
        """
        if not asset:
            raise ValueError("Parameter 'asset' is required.")

        params = {}

        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        if time_interval:
            params['timeInterval'] = time_interval.value
        if lookback_period:
            params['lookbackPeriod'] = lookback_period
        if time_format:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_DEFI_REST_VWAP_ASSET_HISTORICAL_ENDPOINT.format(asset=asset)
        description = "Global VWAP Asset Historical Request"

        logging.info(f"Starting {description}")

        headers = self._headers()
        df = RestService.get_and_process_response_df(url, params, headers, description)

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_global_vwap_asset_historical(
            self, asset: str, start_date: str = None, end_date: str = None,
            time_interval: TimeInterval = None, lookback_period: int = None, time_format: TimeFormat = None, index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes the historical VWAP data for the specified asset.

        Parameters:
            asset (str): The asset address. Required.
            start_date (str): Include data after this date (inclusive). Optional.
            end_date (str): Include data before this date (exclusive). Optional.
            time_interval (str): The time interval for the historical data ('minutes', 'hours', 'days'). Defaults to 'minutes'.
            lookback_period (int): The lookback period in minutes. Defaults to 60.
            time_format (str): The format of the timestamp in the response. Defaults to 'milliseconds'.
            index_keys (list): List of column names to set as the DataFrame index. Defaults to ['timestamp'].

        Returns:
            pd.DataFrame: Processed DataFrame containing the historical VWAP data for the asset.

        Raises:
            ValueError: If required parameters are not provided or no valid data is found.
        """
        if index_keys is None:
            index_keys = ['asset', 'timestamp']

        df = self.get_global_vwap_asset_historical_raw(
            asset, start_date, end_date, time_interval, lookback_period, time_format
        )

        if df.empty:
            logging.warning(
                f"No data found for asset {asset} in the specified time range. Returning an empty DataFrame.")
            return df

        df = df.set_index(index_keys)

        return df

    def get_global_vwap_pairs_information_raw(
            self, time_format: TimeFormat = None, size: int = None, base: str = None, quote: str = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves the list of all available market pair VWAP data sets.

        Parameters:
            time_format (str): The format of the timestamp in the response. Defaults to 'milliseconds'.
            size (int): The number of records to retrieve. Defaults to 1000.
            base (str): The base asset address. Optional.
            quote (str): The quote asset address. Optional.

        Returns:
            pd.DataFrame: DataFrame containing the pairs VWAP information.

        Raises:
            ValueError: If no valid data is found in the response.
        """
        params = {
            'timeFormat': time_format,
            'size': size
        }
        if base:
            params['base'] = base
        if quote:
            params['quote'] = quote

        url = AMBERDATA_DEFI_REST_VWAP_PAIRS_INFORMATION_ENDPOINT
        description = "Global VWAP Pairs Information Request"

        logging.info(f"Starting {description}")

        headers = self._headers()
        df = RestService.get_and_process_response_df(url, params, headers, description)

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_global_vwap_pairs_information(
            self, time_format: TimeFormat = None, size: int = None,
            base: str = None, quote: str = None, index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes the list of all available market pair VWAP data sets.

        Parameters:
            time_format (str): The format of the timestamp in the response. Defaults to 'milliseconds'.
            size (int): The number of records to retrieve. Defaults to 1000.
            base (str): The base asset address. Optional.
            quote (str): The quote asset address. Optional.
            index_keys (list): List of column names to set as the DataFrame index. Defaults to ['baseAddress', 'quoteAddress'].

        Returns:
            pd.DataFrame: Processed DataFrame containing the pairs VWAP information.

        Raises:
            ValueError: If no valid data is found in the response.
        """
        if index_keys is None:
            index_keys = ['baseAddress', 'quoteAddress']

        df = self.get_global_vwap_pairs_information_raw(time_format, size, base, quote)
        df = df.set_index(index_keys)

        return df

    def get_global_vwap_pairs_latest_raw(
            self, base: str, quote: str, lookback_period: int = None, time_format: TimeFormat = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves the latest VWAP data for the specified base-quote pair.

        Parameters:
            base (str): The base asset address. Required.
            quote (str): The quote asset address. Required.
            lookback_period (int): The lookback period in minutes. Defaults to 60.
            time_format (str): The format of the timestamp in the response. Defaults to 'milliseconds'.

        Returns:
            pd.DataFrame: DataFrame containing the latest VWAP data for the pair.

        Raises:
            ValueError: If required parameters are not provided or no valid data is found.
        """
        if not base:
            raise ValueError("Parameter 'base' is required.")
        if not quote:
            raise ValueError("Parameter 'quote' is required.")

        params = {}

        if lookback_period:
            params['lookbackPeriod'] = lookback_period
        if time_format:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_DEFI_REST_VWAP_PAIRS_LATEST_ENDPOINT.format(base=base, quote=quote)
        description = "Global VWAP Pairs Latest Request"

        logging.info(f"Starting {description}")

        headers = self._headers()
        df = RestService.get_and_process_response_df(url, params, headers, description)

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_global_vwap_pairs_latest(
            self, base: str, quote: str,
            lookback_period: int = None, time_format: TimeFormat = None, index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes the latest VWAP data for the specified base-quote pair.

        Parameters:
            base (str): The base asset address. Required.
            quote (str): The quote asset address. Required.
            lookback_period (int): The lookback period in minutes. Defaults to 60.
            time_format (str): The format of the timestamp in the response. Defaults to 'milliseconds'.
            index_keys (list): List of column names to set as the DataFrame index. Defaults to ['timestamp'].

        Returns:
            pd.DataFrame: Processed DataFrame containing the latest VWAP data for the pair.

        Raises:
            ValueError: If required parameters are not provided or no valid data is found.
        """
        if index_keys is None:
            index_keys = ['pair']

        df = self.get_global_vwap_pairs_latest_raw(base, quote, lookback_period, time_format)
        df = df.set_index(index_keys)

        return df

    def get_global_vwap_pairs_historical_raw(
            self, base: str, quote: str, start_date: str = None, end_date: str = None,
            time_interval: TimeInterval = None, lookback_period: int = None, time_format: TimeFormat = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves the historical VWAP data for the specified base-quote pair.

        Parameters:
            base (str): The base asset address. Required.
            quote (str): The quote asset address. Required.
            start_date (str): Include data after this date (inclusive). Optional.
            end_date (str): Include data before this date (exclusive). Optional.
            time_interval (str): The time interval for the historical data ('minutes', 'hours', 'days'). Defaults to 'minutes'.
            lookback_period (int): The lookback period in minutes. Defaults to 60.
            time_format (str): The format of the timestamp in the response. Defaults to 'milliseconds'.

        Returns:
            pd.DataFrame: DataFrame containing the historical VWAP data for the pair.

        Raises:
            ValueError: If required parameters are not provided or no valid data is found.
        """
        if not base:
            raise ValueError("Parameter 'base' is required.")
        if not quote:
            raise ValueError("Parameter 'quote' is required.")

        params = {}

        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        if time_interval:
            params['timeInterval'] = time_interval.value
        if lookback_period:
            params['lookbackPeriod'] = lookback_period
        if time_format:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_DEFI_REST_VWAP_PAIRS_HISTORICAL_ENDPOINT.format(base=base, quote=quote)
        description = "Global VWAP Pairs Historical Request"

        logging.info(f"Starting {description}")

        headers = self._headers()
        df = RestService.get_and_process_response_df(url, params, headers, description)

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_global_vwap_pairs_historical(
            self, base: str, quote: str, start_date: str = None, end_date: str = None, time_interval: TimeInterval = None,
            lookback_period: int = None, time_format: TimeFormat = None, index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes the historical VWAP data for the specified base-quote pair.

        Parameters:
            base (str): The base asset address. Required.
            quote (str): The quote asset address. Required.
            start_date (str): Include data after this date (inclusive). Optional.
            end_date (str): Include data before this date (exclusive). Optional.
            time_interval (str): The time interval for the historical data ('minutes', 'hours', 'days'). Defaults to 'minutes'.
            lookback_period (int): The lookback period in minutes. Defaults to 60.
            time_format (str): The format of the timestamp in the response. Defaults to 'milliseconds'.
            index_keys (list): List of column names to set as the DataFrame index. Defaults to ['timestamp'].

        Returns:
            pd.DataFrame: Processed DataFrame containing the historical VWAP data for the pair.

        Raises:
            ValueError: If required parameters are not provided or no valid data is found.
        """
        if index_keys is None:
            index_keys = ['pair', 'timestamp']

        df = self.get_global_vwap_pairs_historical_raw(
            base, quote, start_date, end_date, time_interval, lookback_period, time_format
        )

        df = df.set_index(index_keys)

        return df


    ### 9 - LENDING PROTOCOL METRICS ###
    def get_lending_protocol_summary_metrics_raw(
            self, protocol_id: ProtocolId, blockchain_id: Blockchain = None,
            start_date: str = None, end_date: str = None, time_format: TimeFormat = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves metrics summary for a lending protocol.

        Args:
            protocol_id: Required ID of the lending protocol (defaults to aavev3)
                        Example: aavev3
            blockchain_id: Optional blockchain ID (defaults to ethereum-mainnet if not specified)
                          Example: polygon-mainnet
            start_date: Optional filter by data after this date (inclusive)
                       Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            end_date: Optional filter by data before this date (exclusive)
                     Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to hr

        Returns:
            DataFrame containing the metrics summary for the specified lending protocol
        """
        params = {}

        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        if time_format:
            params['timeFormat'] = time_format.value

        headers = self._headers()
        if blockchain_id:
            headers['x-amberdata-blockchain-id'] = blockchain_id.value

        url = AMBERDATA_DEFI_REST_LENDING_PROTOCOL_METRICS_ENDPOINT.format(protocolId=protocol_id.value)
        description = f"Lending Protocol Metrics Request for protocol {protocol_id.value}"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, headers, description)

        logging.info(f"Finished {description}")

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_lending_protocol_summary_metrics(
            self, protocol_id: ProtocolId, blockchain_id: Blockchain = None,
            start_date: str = None, end_date: str = None, time_format: TimeFormat = None,
            index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes metrics summary for a lending protocol.

        Args:
            protocol_id: Required ID of the lending protocol (defaults to aavev3)
                        Example: aavev3
            blockchain_id: Optional blockchain ID (defaults to ethereum-mainnet if not specified)
                          Example: polygon-mainnet
            start_date: Optional filter by data after this date (inclusive)
                       Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            end_date: Optional filter by data before this date (exclusive)
                     Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to hr
            index_keys: Optional list of column names to use as index
                       Defaults to ['timestamp']

        Returns:
            DataFrame containing the processed metrics summary for the specified lending protocol
        """
        if index_keys is None:
            index_keys = ['blockchainId']

        # Get the raw data
        df = self.get_lending_protocol_summary_metrics_raw(
            protocol_id=protocol_id,
            blockchain_id=blockchain_id,
            start_date=start_date,
            end_date=end_date,
            time_format=time_format
        )

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)

    def get_lending_asset_summary_metrics_raw(
            self, protocol_id: ProtocolId, asset_id: str,
            blockchain_id: Blockchain = None, start_date: str = None, end_date: str = None,
            time_format: TimeFormat = None, market: str = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves asset summary metrics for a specific asset on a lending protocol.

        Args:
            protocol_id: Required ID of the lending protocol (defaults to aavev3)
                        Example: aavev3
            asset_id: Required ID of the asset (defaults to WETH)
                     Examples: USDC | WETH
                     Note: The requested asset must exist on the specified protocol
            blockchain_id: Optional blockchain ID (defaults to ethereum-mainnet if not specified)
                          Example: polygon-mainnet
            start_date: Optional filter by data after this date (inclusive)
                       Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            end_date: Optional filter by data before this date (exclusive)
                     Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to hr
            market: Optional market to filter by (applies only when protocolId = makerdao)
                   Get only the aggregate data for the specific asset market

        Returns:
            DataFrame containing the asset summary metrics for the specified asset on the lending protocol
        """
        params = {}

        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        if time_format:
            params['timeFormat'] = time_format.value
        if market:
            params['market'] = market

        headers = self._headers()
        if blockchain_id:
            headers['x-amberdata-blockchain-id'] = blockchain_id.value

        url = AMBERDATA_DEFI_REST_LENDING_ASSET_METRICS_ENDPOINT.format(
            protocolId=protocol_id, assetId=asset_id
        )
        description = f"Lending Asset Metrics Request for protocol {protocol_id.value}, asset {asset_id}"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, headers, description)

        logging.info(f"Finished {description}")

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_lending_asset_summary_metrics(
            self, protocol_id: ProtocolId, asset_id: str,
            blockchain_id: Blockchain = None, start_date: str = None, end_date: str = None,
            time_format: TimeFormat = None, market: str = None, index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes asset summary metrics for a specific asset on a lending protocol.

        Args:
            protocol_id: Required ID of the lending protocol (defaults to aavev3)
                        Example: aavev3
            asset_id: Required ID of the asset (defaults to WETH)
                     Examples: USDC | WETH
                     Note: The requested asset must exist on the specified protocol
            blockchain_id: Optional blockchain ID (defaults to ethereum-mainnet if not specified)
                          Example: polygon-mainnet
            start_date: Optional filter by data after this date (inclusive)
                       Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            end_date: Optional filter by data before this date (exclusive)
                     Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to hr
            market: Optional market to filter by (applies only when protocolId = makerdao)
                   Get only the aggregate data for the specific asset market
            index_keys: Optional list of column names to use as index
                       Defaults to ['timestamp']

        Returns:
            DataFrame containing the processed asset summary metrics for the specified asset
        """
        if index_keys is None:
            index_keys = ['blockchainId']

        # Get the raw data
        df = self.get_lending_asset_summary_metrics_raw(
            protocol_id=protocol_id,
            asset_id=asset_id,
            blockchain_id=blockchain_id,
            start_date=start_date,
            end_date=end_date,
            time_format=time_format,
            market=market
        )

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)


    ### 4 - LIQUIDITY PROVIDERS ###
    def get_pool_providers_raw(
                self, pair: str, size: int = None, time_format: TimeFormat = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves the latest liquidity positions for a specific pair.

        Args:
            pair: Required liquidity pool for which to retrieve liquidity positions
                 Example: 0xa478c2975ab1ea89e8196811f51a7b7ade33eb11 (DAI/WETH)
            size: Optional maximum number of positions to return
                 Defaults to all if not specified
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds

        Returns:
            DataFrame containing the latest liquidity positions for the pair
        """
        params = {}

        if size:
            params['size'] = size
        if time_format:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_DEFI_REST_DEX_LIQUIDITY_POSITIONS_PAIRS_LATEST_ENDPOINT.format(pair=pair)
        description = f"DEX Liquidity Positions Pairs Latest Request for pair {pair}"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, self._headers(), description)

        logging.info(f"Finished {description}")

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_pool_providers(
                self, pair: str, size: int = None, time_format: TimeFormat = None,
                index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes the latest liquidity positions for a specific pair.

        Args:
            pair: Required liquidity pool for which to retrieve liquidity positions
                 Example: 0xa478c2975ab1ea89e8196811f51a7b7ade33eb11 (DAI/WETH)
            size: Optional maximum number of positions to return
                 Defaults to all if not specified
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds
            index_keys: Optional list of column names to use as index

        Returns:
            DataFrame containing the processed latest liquidity positions for the pair
        """
        if index_keys is None:
            index_keys = ['tokenAddress', 'holderAddress']

        # Get the raw data
        df = self.get_pool_providers_raw(
            pair=pair,
            size=size,
            time_format=time_format
        )

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)

    def get_provider_positions_raw(
            self, address: str, size: int = None, time_format: TimeFormat = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves the latest liquidity positions for a specific provider address.

        Args:
            address: Required address of the liquidity provider
                    Example: 0x13f89a69d28f5fe9a16ca762f21eb9f5c18fd645
            size: Optional maximum number of positions to return
                 Defaults to all if not specified
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds

        Returns:
            DataFrame containing the latest liquidity positions for the provider
        """
        params = {}

        if size:
            params['size'] = size
        if time_format:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_DEFI_REST_DEX_LIQUIDITY_POSITIONS_PROVIDERS_LATEST_ENDPOINT.format(address=address)
        description = f"DEX Liquidity Positions Providers Latest Request for address {address}"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, self._headers(), description)

        logging.info(f"Finished {description}")

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_provider_positions(
            self, address: str, size: int = None, time_format: TimeFormat = None,
            index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes the latest liquidity positions for a specific provider address.

        Args:
            address: Required address of the liquidity provider
                    Example: 0x13f89a69d28f5fe9a16ca762f21eb9f5c18fd645
            size: Optional maximum number of positions to return
                 Defaults to all if not specified
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds
            index_keys: Optional list of column names to use as index

        Returns:
            DataFrame containing the processed latest liquidity positions for the provider
        """
        if index_keys is None:
            index_keys = ['holderAddress', 'tokenAddress']

        # Get the raw data
        df = self.get_provider_positions_raw(
            address=address,
            size=size,
            time_format=time_format
        )

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)

    def get_provider_events_raw(
            self, provider_address: str, exchange: DexDataVenue = None, size: int = None,
            pair: str = None, time_format: TimeFormat = None, start_date: str = None,
            end_date: str = None, include_metadata: bool = None,
            include_all_transaction_events: bool = None, page: int = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves liquidity provider events for a specific provider address.

        Args:
            provider_address: Required EOA address of the liquidity provider for which to retrieve events
                             Example: 0x18f3e0c9f3bdd2e79e3eeeb1bcd8e6bb9702095f
            exchange: Optional exchange to filter events
            size: Optional maximum number of positions to return
                 Defaults to all if not specified
            pair: Optional liquidity pool (for example DAI/WETH) for which to filter liquidity position events
                 By default, events are not filtered by pool/pair
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds
            start_date: Optional payload only includes data after this date (inclusive)
                       By default, startDate is 24 hours from now
                       Examples: 1578531600 | 1578531600000 | 2022-09-01T01:00:00
            end_date: Optional payload only includes data before this date (exclusive)
                     By default, endDate is now
                     Examples: 1578531600 | 1578531600000 | 2022-09-15T01:00:00
            include_metadata: Optional include data for pool information
                             Defaults to true
            include_all_transaction_events: Optional include all events in transactions containing events
                                           tied to the provider address
                                           Defaults to true
            page: Optional page number to return

        Returns:
            DataFrame containing the liquidity provider events
        """
        params = {}

        if exchange:
            params['exchange'] = exchange.value
        if size:
            params['size'] = size
        if pair:
            params['pair'] = pair
        if time_format:
            params['timeFormat'] = time_format.value
        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        if include_metadata is not None:
            params['includeMetadata'] = str(include_metadata).lower()
        if include_all_transaction_events is not None:
            params['includeAllTransactionEvents'] = str(include_all_transaction_events).lower()
        if page:
            params['page'] = page

        url = AMBERDATA_DEFI_REST_DEX_LIQUIDITY_PROVIDER_EVENTS_ENDPOINT.format(providerAddress=provider_address)
        description = f"DEX Liquidity Provider Events Request for provider address {provider_address}"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, self._headers(), description)

        logging.info(f"Finished {description}")

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_provider_events(
            self, provider_address: str, exchange: DexDataVenue = None, size: int = None,
            pair: str = None, time_format: TimeFormat = None, start_date: str = None,
            end_date: str = None, include_metadata: bool = None,
            include_all_transaction_events: bool = None, page: int = None,
            index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes liquidity provider events for a specific provider address.

        Args:
            provider_address: Required EOA address of the liquidity provider for which to retrieve events
                             Example: 0x18f3e0c9f3bdd2e79e3eeeb1bcd8e6bb9702095f
            exchange: Optional exchange to filter events
            size: Optional maximum number of positions to return
                 Defaults to all if not specified
            pair: Optional liquidity pool (for example DAI/WETH) for which to filter liquidity position events
                 By default, events are not filtered by pool/pair
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds
            start_date: Optional payload only includes data after this date (inclusive)
                       By default, startDate is 24 hours from now
                       Examples: 1578531600 | 1578531600000 | 2022-09-01T01:00:00
            end_date: Optional payload only includes data before this date (exclusive)
                     By default, endDate is now
                     Examples: 1578531600 | 1578531600000 | 2022-09-15T01:00:00
            include_metadata: Optional include data for pool information
                             Defaults to true
            include_all_transaction_events: Optional include all events in transactions containing events
                                           tied to the provider address
                                           Defaults to true
            page: Optional page number to return
            index_keys: Optional list of column names to use as index

        Returns:
            DataFrame containing the processed liquidity provider events
        """
        if index_keys is None:
            index_keys = ['liquidityProviderAddress', 'event', 'poolAddress']

        # Get the raw data
        df = self.get_provider_events_raw(
            provider_address=provider_address,
            exchange=exchange,
            size=size,
            pair=pair,
            time_format=time_format,
            start_date=start_date,
            end_date=end_date,
            include_metadata=include_metadata,
            include_all_transaction_events=include_all_transaction_events,
            page=page
        )

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)


    ### 5 - DEFI METRICS ###
    def get_metrics_exchanges_latest_raw(
            self, exchange: DexDataVenue, time_format: TimeFormat = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves the latest metrics for a specific exchange.

        Args:
            exchange: Required exchange for which to return the global metrics
                     Can be specified as a name (e.g., uniswapv2) or an id (e.g., 0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f)
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds

        Returns:
            DataFrame containing the latest metrics for the exchange
        """
        params = {}

        if time_format:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_DEFI_REST_METRICS_EXCHANGES_LATEST_ENDPOINT.format(exchange=exchange.value)
        description = f"DeFi Metrics Exchanges Latest Request for exchange {exchange.value}"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, self._headers(), description)

        logging.info(f"Finished {description}")

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_metrics_exchanges_latest(
            self, exchange: DexDataVenue, time_format: TimeFormat = None,
            index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes the latest metrics for a specific exchange.

        Args:
            exchange: Required exchange for which to return the global metrics
                     Can be specified as a name (e.g., uniswapv2) or an id (e.g., 0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f)
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds
            index_keys: Optional list of column names to use as index

        Returns:
            DataFrame containing the processed latest metrics for the exchange
        """
        if index_keys is None:
            index_keys = ['exchangeId']

        # Get the raw data
        df = self.get_metrics_exchanges_latest_raw(
            exchange=exchange,
            time_format=time_format
        )

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)

    def get_metrics_exchanges_historical_raw(
            self, exchange: DexDataVenue, start_date: str = None,
            end_date: str = None, time_format: TimeFormat = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves historical metrics for a specific exchange.

        Args:
            exchange: Required exchange for which to return the global metrics
                     Can be specified as a name (e.g., uniswapv2) or an id (e.g., 0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f)
            start_date: Optional filter by data after this date (inclusive)
                       Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            end_date: Optional filter by data before this date (exclusive)
                     Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds

        Returns:
            DataFrame containing the historical metrics for the exchange
        """
        params = {}

        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        if time_format:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_DEFI_REST_METRICS_EXCHANGES_HISTORICAL_ENDPOINT.format(exchange=exchange.value)
        description = f"DeFi Metrics Exchanges Historical Request for exchange {exchange.value}"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, self._headers(), description)

        logging.info(f"Finished {description}")

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_metrics_exchanges_historical(
            self, exchange: DexDataVenue, start_date: str = None,
            end_date: str = None, time_format: TimeFormat = None,
            index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes historical metrics for a specific exchange.

        Args:
            exchange: Required exchange for which to return the global metrics
                     Can be specified as a name (e.g., uniswapv2) or an id (e.g., 0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f)
            start_date: Optional filter by data after this date (inclusive)
                       Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            end_date: Optional filter by data before this date (exclusive)
                     Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds
            index_keys: Optional list of column names to use as index

        Returns:
            DataFrame containing the processed historical metrics for the exchange
        """
        if index_keys is None:
            index_keys = ['exchangeId', 'timestamp']

        # Get the raw data
        df = self.get_metrics_exchanges_historical_raw(
            exchange=exchange,
            start_date=start_date,
            end_date=end_date,
            time_format=time_format
        )

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)

    def get_metrics_assets_latest_raw(
            self, exchange: DexDataVenue, asset: str, time_format: TimeFormat = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves the latest metrics for a specific asset on an exchange.

        Args:
            exchange: Required exchange of the asset for which to return the metrics
                     Can be specified as a name (e.g., uniswapv2) or an id (e.g., 0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f)
            asset: Required asset for which to return the metrics
                  Example: 0x6b175474e89094c44da98b954eedeac495271d0f (DAI)
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds

        Returns:
            DataFrame containing the latest metrics for the asset
        """
        params = {}

        if time_format:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_DEFI_REST_METRICS_ASSETS_LATEST_ENDPOINT.format(exchange=exchange.value, asset=asset)
        description = f"DeFi Metrics Assets Latest Request for asset {asset} on exchange {exchange.value}"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, self._headers(), description)

        logging.info(f"Finished {description}")

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_metrics_assets_latest(
            self, exchange: DexDataVenue, asset: str, time_format: TimeFormat = None,
            index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes the latest metrics for a specific asset on an exchange.

        Args:
            exchange: Required exchange of the asset for which to return the metrics
                     Can be specified as a name (e.g., uniswapv2) or an id (e.g., 0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f)
            asset: Required asset for which to return the metrics
                  Example: 0x6b175474e89094c44da98b954eedeac495271d0f (DAI)
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds
            index_keys: Optional list of column names to use as index

        Returns:
            DataFrame containing the processed latest metrics for the asset
        """
        if index_keys is None:
            index_keys = ['exchangeId', 'address']

        # Get the raw data
        df = self.get_metrics_assets_latest_raw(
            exchange=exchange,
            asset=asset,
            time_format=time_format
        )

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)

    def get_metrics_assets_historical_raw(
            self, exchange: DexDataVenue, asset: str, start_date: str = None,
            end_date: str = None, time_format: TimeFormat = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves historical metrics for a specific asset on an exchange.

        Args:
            exchange: Required exchange of the asset for which to return the metrics
                     Can be specified as a name (e.g., uniswapv2) or an id (e.g., 0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f)
            asset: Required asset for which to return the metrics
                  Example: 0x6b175474e89094c44da98b954eedeac495271d0f (DAI)
            start_date: Optional filter by data after this date (inclusive)
                       Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            end_date: Optional filter by data before this date (exclusive)
                     Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds

        Returns:
            DataFrame containing the historical metrics for the asset
        """
        params = {}

        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        if time_format:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_DEFI_REST_METRICS_ASSETS_HISTORICAL_ENDPOINT.format(exchange=exchange.value, asset=asset)
        description = f"DeFi Metrics Assets Historical Request for asset {asset} on exchange {exchange.value}"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, self._headers(), description)

        logging.info(f"Finished {description}")

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_metrics_assets_historical(
            self, exchange: DexDataVenue, asset: str, start_date: str = None,
            end_date: str = None, time_format: TimeFormat = None,
            index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes historical metrics for a specific asset on an exchange.

        Args:
            exchange: Required exchange of the asset for which to return the metrics
                     Can be specified as a name (e.g., uniswapv2) or an id (e.g., 0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f)
            asset: Required asset for which to return the metrics
                  Example: 0x6b175474e89094c44da98b954eedeac495271d0f (DAI)
            start_date: Optional filter by data after this date (inclusive)
                       Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            end_date: Optional filter by data before this date (exclusive)
                     Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds
            index_keys: Optional list of column names to use as index

        Returns:
            DataFrame containing the processed historical metrics for the asset
        """
        if index_keys is None:
            index_keys = ['exchangeId', 'address', 'timestamp']

        # Get the raw data
        df = self.get_metrics_assets_historical_raw(
            exchange=exchange,
            asset=asset,
            start_date=start_date,
            end_date=end_date,
            time_format=time_format
        )

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)

    def get_metrics_pairs_latest_raw(
            self, exchange: DexDataVenue, pair: str, time_format: TimeFormat = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves the latest metrics for a specific pair on an exchange.

        Args:
            exchange: Required exchange of the pair for which to return the metrics
                     Can be specified as a name (e.g., uniswapv2) or an id (e.g., 0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f)
            pair: Required pair for which to return the metrics
                 Example: 0xa478c2975ab1ea89e8196811f51a7b7ade33eb11 (DAI_WETH)
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds

        Returns:
            DataFrame containing the latest metrics for the pair
        """
        params = {}

        if time_format:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_DEFI_REST_METRICS_PAIRS_LATEST_ENDPOINT.format(exchange=exchange.value, pair=pair)
        description = f"DeFi Metrics Pairs Latest Request for pair {pair} on exchange {exchange.value}"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, self._headers(), description)

        logging.info(f"Finished {description}")

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_metrics_pairs_latest(
            self, exchange: DexDataVenue, pair: str, time_format: TimeFormat = None,
            index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes the latest metrics for a specific pair on an exchange.

        Args:
            exchange: Required exchange of the pair for which to return the metrics
                     Can be specified as a name (e.g., uniswapv2) or an id (e.g., 0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f)
            pair: Required pair for which to return the metrics
                 Example: 0xa478c2975ab1ea89e8196811f51a7b7ade33eb11 (DAI_WETH)
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds
            index_keys: Optional list of column names to use as index

        Returns:
            DataFrame containing the processed latest metrics for the pair
        """
        if index_keys is None:
            index_keys = ['exchangeId']

        # Get the raw data
        df = self.get_metrics_pairs_latest_raw(
            exchange=exchange,
            pair=pair,
            time_format=time_format
        )

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)

    def get_metrics_pairs_historical_raw(
            self, exchange: DexDataVenue, pair: str, start_date: str = None,
            end_date: str = None, time_format: TimeFormat = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves historical metrics for a specific pair on an exchange.

        Args:
            exchange: Required exchange of the pair for which to return the metrics
                     Can be specified as a name (e.g., uniswapv2) or an id (e.g., 0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f)
            pair: Required pair for which to return the metrics
                 Example: 0xa478c2975ab1ea89e8196811f51a7b7ade33eb11 (DAI_WETH)
            start_date: Optional filter by data after this date (inclusive)
                       Examples: 1578531600 | 1578531600000 | 2020-09-01T00:00:00
            end_date: Optional filter by data before this date (exclusive)
                     Examples: 1578531600 | 1578531600000 | 2020-09-02T00:00:00
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds

        Returns:
            DataFrame containing the historical metrics for the pair
        """
        params = {}

        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        if time_format:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_DEFI_REST_METRICS_PAIRS_HISTORICAL_ENDPOINT.format(exchange=exchange.value, pair=pair)
        description = f"DeFi Metrics Pairs Historical Request for pair {pair} on exchange {exchange.value}"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, self._headers(), description)

        logging.info(f"Finished {description}")

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_metrics_pairs_historical(
            self, exchange: DexDataVenue, pair: str, start_date: str = None,
            end_date: str = None, time_format: TimeFormat = None,
            index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes historical metrics for a specific pair on an exchange.

        Args:
            exchange: Required exchange of the pair for which to return the metrics
                     Can be specified as a name (e.g., uniswapv2) or an id (e.g., 0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f)
            pair: Required pair for which to return the metrics
                 Example: 0xa478c2975ab1ea89e8196811f51a7b7ade33eb11 (DAI_WETH)
            start_date: Optional filter by data after this date (inclusive)
                       Examples: 1578531600 | 1578531600000 | 2020-09-01T00:00:00
            end_date: Optional filter by data before this date (exclusive)
                     Examples: 1578531600 | 1578531600000 | 2020-09-02T00:00:00
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds
            index_keys: Optional list of column names to use as index

        Returns:
            DataFrame containing the processed historical metrics for the pair
        """
        if index_keys is None:
            index_keys = ['exchangeId', 'timestamp']

        # Get the raw data
        df = self.get_metrics_pairs_historical_raw(
            exchange=exchange,
            pair=pair,
            start_date=start_date,
            end_date=end_date,
            time_format=time_format
        )

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)


    ### 8 - PORTFOLIO & RETURNS ###

    def get_liquidity_provider_return_since_inception_raw(
            self, liquidity_pool_address: str, addresses: str = None,
            date: str = None, time_format: TimeFormat = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves the return since inception for liquidity providers in a specific pool.

        Args:
            liquidity_pool_address: Required address of the liquidity pool
                                   Example: 0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc
            addresses: Optional comma separated list of liquidity provider addresses (max 10)
                      Example: 0x8409daf0d03ea176823b3c7240dc28ce371b1f8d,0xba7ac1952db308b0a245bdb14440ca321afbb14a
            date: Optional query date (if non-midnight GMT timestamp is provided, defaults to the last one)
                 Example: 2022-09-28
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds

        Returns:
            DataFrame containing the return since inception data for the specified liquidity providers
        """
        params = {}

        if addresses:
            params['addresses'] = addresses
        if date:
            params['date'] = date
        if time_format:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_DEFI_REST_PROVIDER_RETURN_SINCE_INCEPTION_ENDPOINT.format(
            liquidityPoolAddress=liquidity_pool_address
        )
        description = f"Liquidity Provider Return Since Inception Request for pool {liquidity_pool_address}"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, self._headers(), description)

        logging.info(f"Finished {description}")
        return df

    @convert_timestamp
    def get_liquidity_provider_return_since_inception(
            self, liquidity_pool_address: str, addresses: str = None,
            date: str = None, time_format: TimeFormat = None, index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes the return since inception for liquidity providers.

        Args:
            liquidity_pool_address: Required address of the liquidity pool
                                   Example: 0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc
            addresses: Optional comma separated list of liquidity provider addresses (max 10)
                      Example: 0x8409daf0d03ea176823b3c7240dc28ce371b1f8d,0xba7ac1952db308b0a245bdb14440ca321afbb14a
            date: Optional query date (if non-midnight GMT timestamp is provided, defaults to the last one)
                 Example: 2022-09-28
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds
            index_keys: Optional list of column names to use as index
                       Defaults to ['address']

        Returns:
            DataFrame containing the processed return since inception data
        """
        if index_keys is None:
            index_keys = []

        # Get the raw data
        df = self.get_liquidity_provider_return_since_inception_raw(
            liquidity_pool_address=liquidity_pool_address,
            addresses=addresses,
            date=date,
            time_format=time_format
        )

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        # return df.set_index(index_keys)
        return df

    def get_liquidity_provider_historical_return_raw(self, liquidity_pool_address: str, addresses: str, start_date: str,
                                                     end_date: str) -> pd.DataFrame:
        """
        Raw function that retrieves historical return data for liquidity providers in a specific pool.

        Args:
            liquidity_pool_address: Required address of the liquidity pool
                                   Example: 0xbb2b8038a1640196fbe3e38816f3e67cba72d940
            addresses: Required comma separated list of liquidity provider addresses (max 10)
                      Example: 0x0fd0489d5ccf0acc0ccbe8a1f1e638e74cab5bd7
            start_date: Required filter by data after this date (inclusive)
                       Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            end_date: Required filter by data before this date (exclusive)
                     Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds

        Returns:
            DataFrame containing the historical return data for the specified liquidity providers
        """
        params = {
            'addresses': addresses,
            'startDate': start_date,
            'endDate': end_date
        }

        url = AMBERDATA_DEFI_REST_PROVIDER_HISTORICAL_RETURN_ENDPOINT.format(
            liquidityPoolAddress=liquidity_pool_address
        )
        description = f"Liquidity Provider Historical Return Request for pool {liquidity_pool_address}"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, self._headers(), description)

        logging.info(f"Finished {description}")

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_liquidity_provider_historical_return(self, liquidity_pool_address: str, addresses: str, start_date: str,
                                                 end_date: str, index_keys: list = None) -> pd.DataFrame:
        """
        Processed function that retrieves and processes historical return data for liquidity providers.

        Args:
            liquidity_pool_address: Required address of the liquidity pool
                                   Example: 0xbb2b8038a1640196fbe3e38816f3e67cba72d940
            addresses: Required comma separated list of liquidity provider addresses (max 10)
                      Example: 0x0fd0489d5ccf0acc0ccbe8a1f1e638e74cab5bd7
            start_date: Required filter by data after this date (inclusive)
                       Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            end_date: Required filter by data before this date (exclusive)
                     Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds
            index_keys: Optional list of column names to use as index
                       Defaults to ['timestamp', 'address']

        Returns:
            DataFrame containing the processed historical return data
        """
        if index_keys is None:
            index_keys = ['protocol', 'holderAddress']

        # Get the raw data
        df = self.get_liquidity_provider_historical_return_raw(liquidity_pool_address=liquidity_pool_address,
                                                               addresses=addresses, start_date=start_date,
                                                               end_date=end_date)

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)

    def get_liquidity_pool_total_return_raw(
            self, address: str, date: str = None, time_format: TimeFormat = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves the total return data for a specific liquidity pool.

        Args:
            address: Required address of the liquidity pool
                   Example: 0x0d4a11d5eeaac28ec3f61d100daf4d40471f1852
            date: Optional query date (if non-midnight UTC timestamp is provided, defaults to the last one)
                 Example: 2022-08-01
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds

        Returns:
            DataFrame containing the total return data for the specified liquidity pool
        """
        params = {}

        if date:
            params['date'] = date
        if time_format:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_DEFI_REST_POOL_TOTAL_RETURN_ENDPOINT.format(address=address)
        description = f"Liquidity Pool Total Return Request for pool {address}"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, self._headers(), description)
        logging.info(f"Finished {description}")

        return df

    @convert_timestamp
    def get_liquidity_pool_total_return(
            self, address: str, date: str = None, time_format: TimeFormat = None,
            index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes total return data for a liquidity pool.

        Args:
            address: Required address of the liquidity pool
                   Example: 0x0d4a11d5eeaac28ec3f61d100daf4d40471f1852
            date: Optional query date (if non-midnight UTC timestamp is provided, defaults to the last one)
                 Example: 2022-08-01
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds
            index_keys: Optional list of column names to use as index

        Returns:
            DataFrame containing the processed total return data
        """
        if index_keys is None:
            index_keys = ['timestamp']

        # Get the raw data
        df = self.get_liquidity_pool_total_return_raw(
            address=address,
            date=date,
            time_format=time_format
        )

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)

    def get_track_positions_lending_wallets_raw(
            self, protocol_id: ProtocolId, address: str, blockchain_id: Blockchain = None,
            time_format: TimeFormat = None, end_date: str = None, block_number: int = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves lending positions for a specific wallet on a lending protocol.

        Args:
            protocol_id: Required ID of the lending protocol
                        Example: aavev3
            address: Required wallet address to analyze
                    Example: 0x884d6fa3a4b349880486ad4d7c833ca968c785d8
            blockchain_id: Optional blockchain ID (defaults to ethereum-mainnet if not specified)
                          Example: polygon-mainnet
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds
            end_date: Optional returns the balances of the address at this date
                     Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
                     Note: Cannot be combined with block_number
            block_number: Optional returns the balances of the address when this block was finalized
                         Note: Cannot be combined with end_date

        Returns:
            DataFrame containing the lending positions data for the specified wallet
        """
        params = {}

        if time_format:
            params['timeFormat'] = time_format.value
        if end_date:
            params['endDate'] = end_date
        if block_number:
            params['blockNumber'] = block_number

        headers = self._headers()
        if blockchain_id:
            headers['x-amberdata-blockchain-id'] = blockchain_id.value

        url = AMBERDATA_DEFI_REST_WALLET_POSITIONS_ENDPOINT.format(
            protocolId=protocol_id.value, address=address
        )
        description = f"Lending Wallet Positions Request for protocol {protocol_id.value}, address {address}"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, headers, description)

        logging.info(f"Finished {description}")

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_track_positions_lending_wallets(
            self, protocol_id: ProtocolId, address: str, blockchain_id: Blockchain = None,
            time_format: TimeFormat = None, end_date: str = None, block_number: int = None,
            index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes lending positions for a specific wallet.

        Args:
            protocol_id: Required ID of the lending protocol
                        Example: aavev3
            address: Required wallet address to analyze
                    Example: 0x884d6fa3a4b349880486ad4d7c833ca968c785d8
            blockchain_id: Optional blockchain ID (defaults to ethereum-mainnet if not specified)
                          Example: polygon-mainnet
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds
            end_date: Optional returns the balances of the address at this date
                     Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
                     Note: Cannot be combined with block_number
            block_number: Optional returns the balances of the address when this block was finalized
                         Note: Cannot be combined with end_date
            index_keys: Optional list of column names to use as index
                       Defaults to ['symbol']

        Returns:
            DataFrame containing the processed lending positions data
        """
        if index_keys is None:
            index_keys = ['positions']

        # Get the raw data
        df = self.get_track_positions_lending_wallets_raw(
            protocol_id=protocol_id,
            address=address,
            blockchain_id=blockchain_id,
            time_format=time_format,
            end_date=end_date,
            block_number=block_number
        )

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)

    def get_profit_loss_analytics_in_defi_lending_raw(
            self, wallet_address: str, blockchain_id: Blockchain = None,
            start_date: str = None, end_date: str = None, time_format: TimeFormat = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves profit and loss analytics for a wallet in DeFi lending.

        Args:
            wallet_address: Required wallet address to analyze
                          Example: 0x884d6fa3a4b349880486ad4d7c833ca968c785d8
            blockchain_id: Optional blockchain ID (defaults to ethereum-mainnet if not specified)
            start_date: Optional filter by data after this date (inclusive)
                       Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            end_date: Optional filter by data before this date (exclusive)
                     Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds

        Returns:
            DataFrame containing the profit and loss analytics data for the specified wallet
        """
        params = {}

        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        if time_format:
            params['timeFormat'] = time_format.value

        headers = self._headers()
        if blockchain_id:
            headers['x-amberdata-blockchain-id'] = blockchain_id.value

        url = AMBERDATA_DEFI_REST_PROFIT_LOSS_ENDPOINT.format(walletAddress=wallet_address)
        description = f"Lending Profit Loss Request for wallet {wallet_address}"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, headers, description)

        logging.info(f"Finished {description}")

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_profit_loss_analytics_in_defi_lending(
            self, wallet_address: str, blockchain_id: Blockchain = None,
            start_date: str = None, end_date: str = None, time_format: TimeFormat = None,
            index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes profit and loss analytics for a wallet in DeFi lending.

        Args:
            wallet_address: Required wallet address to analyze
                          Example: 0x884d6fa3a4b349880486ad4d7c833ca968c785d8
            blockchain_id: Optional blockchain ID (defaults to ethereum-mainnet if not specified)
            start_date: Optional filter by data after this date (inclusive)
                       Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            end_date: Optional filter by data before this date (exclusive)
                     Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds
            index_keys: Optional list of column names to use as index
                       Defaults to ['timestamp']

        Returns:
            DataFrame containing the processed profit and loss analytics data
        """
        if index_keys is None:
            index_keys = ['blockchainId']

        # Get the raw data
        df = self.get_profit_loss_analytics_in_defi_lending_raw(
            wallet_address=wallet_address,
            blockchain_id=blockchain_id,
            start_date=start_date,
            end_date=end_date,
            time_format=time_format
        )

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)

    def get_impermanent_loss_dex_returns_raw(
            self, wallet_address: str, liquidity_pool_address: str, protocol_name: ProtocolId,
            blockchain_id: Blockchain = None, start_date: str = None, end_date: str = None,
            time_format: TimeFormat = None, position_id: str = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves impermanent loss data for a wallet in a liquidity pool.

        Args:
            wallet_address: Required address of the wallet to analyze
                          Example: 0x7e95Cde1B7270155C62450D1931ABe977BfbFe9C
            liquidity_pool_address: Required address of the liquidity pool
                                   Example: 0xCBCdF9626bC03E24f779434178A73a0B4bad62eD
            protocol_name: Required name of the protocol
                         Example: uniswapv3
            blockchain_id: Optional blockchain ID (defaults to ethereum-mainnet if not specified)
            start_date: Optional filter by data after this date (inclusive)
                       Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            end_date: Optional filter by data before this date (exclusive)
                     Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds
            position_id: Optional filter to only return metrics for a specific position of the wallet

        Returns:
            DataFrame containing the impermanent loss data for the specified wallet and pool
        """
        params = {
            'liquidityPoolAddress': liquidity_pool_address,
            'protocolName': protocol_name.value
        }

        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        if time_format:
            params['timeFormat'] = time_format.value
        if position_id:
            params['positionId'] = position_id

        headers = self._headers()
        if blockchain_id:
            headers['x-amberdata-blockchain-id'] = blockchain_id.value

        url = AMBERDATA_DEFI_REST_IMPERMANENT_LOSS_ENDPOINT.format(walletAddress=wallet_address)
        description = f"Impermanent Loss Request for wallet {wallet_address}, pool {liquidity_pool_address}"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, headers, description)

        logging.info(f"Finished {description}")

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_impermanent_loss_dex_returns(
            self, wallet_address: str, liquidity_pool_address: str, protocol_name: ProtocolId,
            blockchain_id: Blockchain = None, start_date: str = None, end_date: str = None,
            time_format: TimeFormat = None, position_id: str = None, index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes impermanent loss data for a wallet in a liquidity pool.

        Args:
            wallet_address: Required address of the wallet to analyze
                          Example: 0x7e95Cde1B7270155C62450D1931ABe977BfbFe9C
            liquidity_pool_address: Required address of the liquidity pool
                                   Example: 0xCBCdF9626bC03E24f779434178A73a0B4bad62eD
            protocol_name: Required name of the protocol
                         Example: uniswapv3
            blockchain_id: Optional blockchain ID (defaults to ethereum-mainnet if not specified)
            start_date: Optional filter by data after this date (inclusive)
                       Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            end_date: Optional filter by data before this date (exclusive)
                     Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
                        Defaults to milliseconds
            position_id: Optional filter to only return metrics for a specific position of the wallet
            index_keys: Optional list of column names to use as index
                       Defaults to ['timestamp']

        Returns:
            DataFrame containing the processed impermanent loss data
        """
        if index_keys is None:
            index_keys = ['timestamp']

        # Get the raw data
        df = self.get_impermanent_loss_dex_returns_raw(
            wallet_address=wallet_address,
            liquidity_pool_address=liquidity_pool_address,
            protocol_name=protocol_name,
            blockchain_id=blockchain_id,
            start_date=start_date,
            end_date=end_date,
            time_format=time_format,
            position_id=position_id
        )

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)

    ### 11 - STABLECOINS AGGREGATE INSIGHTS ###
    def get_stablecoins_in_defi_lending_aggregate_insights_raw(
            self, asset_symbol: StableCoin, start_date: str = None, end_date: str = None,
            time_interval: TimeInterval = None, protocol: ProtocolId = None, time_format: TimeFormat = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves aggregate insights for stablecoins in DeFi lending.

        Args:
            asset_symbol: Required stablecoin symbol (defaults to USDC)
                         Example: USDC
            start_date: Optional filter by data after this date (inclusive)
                       Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            end_date: Optional filter by data before this date (inclusive)
                     Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            time_interval: Optional interval for metrics aggregation
                          Defaults to 'days'
                          Options: days | hours
            protocol: Optional filter to drill down into stablecoin metrics by specifying a protocol
                     Example: aavev2
            time_format: Optional time format of the timestamps in the return payload
                        Defaults to 'hr'
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable

        Returns:
            DataFrame containing the aggregate insights for stablecoins in DeFi lending
        """
        params = {}

        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        if time_interval:
            params['timeInterval'] = time_interval.value
        if protocol:
            params['protocol'] = protocol.value
        if time_format:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_DEFI_REST_LENDING_STABLECOINS_AGGREGATE_INSIGHTS_ENDPOINT.format(assetSymbol=asset_symbol.value)
        description = f"Lending Stablecoins Aggregate Insights Request for {asset_symbol.value}"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, self._headers(), description)

        logging.info(f"Finished {description}")

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_stablecoins_in_defi_lending_aggregate_insights(
            self, asset_symbol: StableCoin, start_date: str = None, end_date: str = None,
            time_interval: TimeInterval = None, protocol: ProtocolId = None, time_format: TimeFormat = None,
            index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes aggregate insights for stablecoins in DeFi lending.

        Args:
            asset_symbol: Required stablecoin symbol (defaults to USDC)
                         Example: USDC
            start_date: Optional filter by data after this date (inclusive)
                       Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            end_date: Optional filter by data before this date (inclusive)
                     Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            time_interval: Optional interval for metrics aggregation
                          Defaults to 'days'
                          Options: days | hours
            protocol: Optional filter to drill down into stablecoin metrics by specifying a protocol
                     Example: aavev2
            time_format: Optional time format of the timestamps in the return payload
                        Defaults to 'hr'
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
            index_keys: Optional list of column names to use as index
                       Defaults to ['timestamp']

        Returns:
            DataFrame containing the processed aggregate insights for stablecoins in DeFi lending
        """
        if index_keys is None:
            index_keys = ['blockchainId']

        # Get the raw data
        df = self.get_stablecoins_in_defi_lending_aggregate_insights_raw(
            asset_symbol=asset_symbol,
            start_date=start_date,
            end_date=end_date,
            time_interval=time_interval,
            protocol=protocol,
            time_format=time_format
        )

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)

    ### 12 INFORMATION - LENDING PROTOCOLS ###
    def get_information_lending_protocols_raw(
            self,
            blockchain: Blockchain = None,
            protocol: LendingProtocol = None,
            end_date: str = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves the lending protocols information.
        """
        params = {}

        if blockchain:
            params['blockchain'] = blockchain.value
        if protocol:
            params['protocol'] = protocol.value
        if end_date:
            params['endDate'] = end_date

        url = AMBERDATA_DEFI_REST_LENDING_PROTOCOLS_INFORMATION_ENDPOINT
        description = "Lending Protocols Information Request"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, self._headers(), description)

        logging.info(f"Finished {description}")

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_information_lending_protocols(
            self,
            blockchain: Blockchain = None,
            protocol: LendingProtocol = None,
            end_date: str = None,
            index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes the lending protocols information.
        """
        if index_keys is None:
            index_keys = ['protocolId']

        # Use the corrected raw function
        df = self.get_information_lending_protocols_raw(blockchain, protocol, end_date)

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index based on the index_keys provided
        return df.set_index(index_keys)


    ### 13 - INFORMATION - ASSETS IN LENDING PROTOCOLS ###
    def get_information_assets_in_lending_protocols_raw(
                self,
                blockchain: Blockchain = None,
                protocol: LendingProtocol = None,
                asset: str = None,
                market: str = None,
                end_date: str = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves the lending assets information.
        """
        params = {}

        if blockchain:
            params['blockchain'] = blockchain.value
        if protocol:
            params['protocol'] = protocol.value
        if asset:
            params['asset'] = asset
        if market:
            params['market'] = market
        if end_date:
            params['endDate'] = end_date

        url = AMBERDATA_DEFI_REST_LENDING_ASSETS_INFORMATION_ENDPOINT
        description = "Lending Assets Information Request"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, self._headers(), description)

        logging.info(f"Finished {description}")

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_information_assets_in_lending_protocols(
            self,
            blockchain: Blockchain = None,
            protocol: LendingProtocol = None,
            asset: str = None,
            market: str = None,
            end_date: str = None,
            index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes the lending assets information.
        """
        if index_keys is None:
            index_keys = ['protocolId', 'blockchain', 'assetId']

        # Get the raw data
        df = self.get_information_assets_in_lending_protocols_raw(blockchain, protocol, asset, market, end_date)

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)

    ### 14 - INFORMATION - DEX PROTOCOLS ###
    def get_information_dex_protocols_raw(
            self,
            exchange: DexDataVenue = None,
            sort_by: DEXSortBy = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves the list of supported DEX exchanges.
        """
        params = {}

        if sort_by:
            params['sortBy'] = sort_by.value
        if exchange:
            params['exchange'] = exchange.value

        url = AMBERDATA_DEFI_REST_DEX_EXCHANGES_ENDPOINT
        description = "DEX Exchanges Information Request"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, self._headers(), description)

        logging.info(f"Finished {description}")

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_information_dex_protocols(
            self,
            exchange: DexDataVenue = None,
            sort_by: DEXSortBy = None,
            index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes the list of supported DEX exchanges.
        """
        if index_keys is None:
            index_keys = ['exchangeId']

        df = self.get_information_dex_protocols_raw(exchange, sort_by)

        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)

    ### 15 - INFORMATION - PAIRS IN DEX PROTOCOLS ###
    def get_information_pairs_in_dex_protocols_raw(
            self,
            exchange: DexDataVenue,
            pair: str = None,
            asset: str = None,
            size: int = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves supported DEX pairs.

        Parameters:
            exchange (str): The exchange for which to retrieve the data (address or name). Required.
            pair (str): The pair address to filter by. Optional.
            asset (str): The asset address or symbol to filter by. Optional.
            size (int): Maximum number of items in payload.data. Optional.

        Returns:
            pd.DataFrame: DataFrame containing the raw data from the API.

        Raises:
            ValueError: If 'exchange' parameter is not provided or no valid data is found.
        """
        if not exchange:
            raise ValueError("Parameter 'exchange' is required.")

        params = {'exchange': exchange.value}

        if pair:
            params['pair'] = pair
        if asset:
            params['asset'] = asset
        if size:
            params['size'] = size

        url = AMBERDATA_DEFI_REST_DEX_PAIRS_ENDPOINT
        description = "DEX Pairs Information Request"

        logging.info(f"Starting {description}")

        df = RestService.get_and_process_response_df(url, params, self._headers(), description)

        logging.info(f"Finished {description}")

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_information_pairs_in_dex_protocols(
            self,
            exchange: DexDataVenue,
            pair: str = None,
            asset: str = None,
            size: int = None,
            index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes supported DEX pairs.
        """
        df = self.get_information_pairs_in_dex_protocols_raw(exchange, pair, asset, size)

        if index_keys is None:
            index_keys = ['exchangeId', 'pairName']

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)

    ### 7 - DEX ALL TRANSACTIONS ###
    def get_protocol_lens_raw(
            self, protocol_id: ProtocolId, start_date: str = None, end_date: str = None,
            size: int = None, time_format: TimeFormat = None, action: ProtocolAction = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves protocol lens data for a specific DEX protocol.

        Args:
            protocol_id: Required protocol ID for which to retrieve lens data
                        Example: uniswapv3
            start_date: Optional filter by data after this date (inclusive)
                       Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            end_date: Optional filter by data before this date (exclusive)
                     Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            size: Optional number of records per page
                 Defaults to 100 if not specified. Maximum is 1000
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
            action: Optional filter by action

        Returns:
            DataFrame containing the protocol lens data
        """
        params = {}

        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        if size:
            params['size'] = size
        if time_format:
            params['timeFormat'] = time_format.value
        if action:
            params['action'] = action.value

        url = AMBERDATA_DEFI_REST_DEX_PROTOCOL_LENS_ENDPOINT.format(protocolId=protocol_id.value)
        description = f"DEX Protocol Lens Request for protocol {protocol_id.value}"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, self._headers(), description)

        logging.info(f"Finished {description}")

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_protocol_lens(
            self, protocol_id: ProtocolId, start_date: str = None, end_date: str = None,
            size: int = None, time_format: TimeFormat = None, action: ProtocolAction = None,
            index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes protocol lens data for a specific DEX protocol.

        Args:
            protocol_id: Required protocol ID for which to retrieve lens data
                        Example: uniswapv3
            start_date: Optional filter by data after this date (inclusive)
                       Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            end_date: Optional filter by data before this date (exclusive)
                     Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            size: Optional number of records per page
                 Defaults to 100 if not specified. Maximum is 1000
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
            action: Optional filter by action
            index_keys: Optional list of column names to use as index

        Returns:
            DataFrame containing the processed protocol lens data
        """
        if index_keys is None:
            index_keys = ['action', 'event', 'timestamp']

        # Get the raw data
        df = self.get_protocol_lens_raw(
            protocol_id=protocol_id,
            start_date=start_date,
            end_date=end_date,
            size=size,
            time_format=time_format,
            action=action
        )

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)

    def get_dex_pool_lens_raw(
            self, protocol_id: ProtocolId, pool_address: str, start_date: str = None,
            end_date: str = None, size: int = None, time_format: TimeFormat = None,
            action: ProtocolAction = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves pool lens data for a specific pool on a DEX protocol.

        Args:
            protocol_id: Required protocol ID for which to retrieve lens data
                        Example: uniswapv2
            pool_address: Required pool address for which to retrieve lens data
                         Example: 0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc
            start_date: Optional filter by data after this date (inclusive)
                       Defaults to 2022-07-01
                       Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            end_date: Optional filter by data before this date (exclusive)
                     Defaults to 2022-07-10
                     Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            size: Optional number of records per page
                 Defaults to 100 if not specified. Maximum is 1000
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
            action: Optional filter by action

        Returns:
            DataFrame containing the pool lens data
        """
        params = {}

        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        if size:
            params['size'] = size
        if time_format:
            params['timeFormat'] = time_format.value
        if action:
            params['action'] = action.value

        url = AMBERDATA_DEFI_REST_DEX_POOL_LENS_ENDPOINT.format(protocolId=protocol_id.value, poolAddress=pool_address)
        description = f"DEX Pool Lens Request for pool {pool_address} on protocol {protocol_id.value}"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, self._headers(), description)

        logging.info(f"Finished {description}")

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_dex_pool_lens(
            self, protocol_id: ProtocolId, pool_address: str, start_date: str = None,
            end_date: str = None, size: int = None, time_format: TimeFormat = None,
            action: ProtocolAction = None, index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes pool lens data for a specific pool on a DEX protocol.

        Args:
            protocol_id: Required protocol ID for which to retrieve lens data
                        Example: uniswapv2
            pool_address: Required pool address for which to retrieve lens data
                         Example: 0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc
            start_date: Optional filter by data after this date (inclusive)
                       Defaults to 2022-07-01
                       Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            end_date: Optional filter by data before this date (exclusive)
                     Defaults to 2022-07-10
                     Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            size: Optional number of records per page
                 Defaults to 100 if not specified. Maximum is 1000
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
            action: Optional filter by action
            index_keys: Optional list of column names to use as index

        Returns:
            DataFrame containing the processed pool lens data
        """
        if index_keys is None:
            index_keys = ['action', 'event', 'timestamp']

        # Get the raw data
        df = self.get_dex_pool_lens_raw(
            protocol_id=protocol_id,
            pool_address=pool_address,
            start_date=start_date,
            end_date=end_date,
            size=size,
            time_format=time_format,
            action=action
        )

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)

    def get_dex_wallet_lens_raw(
            self, protocol_id: ProtocolId, wallet_address: str, start_date: str = None,
            end_date: str = None, size: int = None, time_format: TimeFormat = None,
            action: ProtocolAction = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves wallet lens data for a specific wallet on a DEX protocol.

        Args:
            protocol_id: Required protocol ID for which to retrieve lens data
                        Example: uniswapv3
            wallet_address: Required wallet address for which to retrieve lens data
                          Example: 0x7ff28d78bffb7b571db98ea48e7a77128bac8456
            start_date: Optional filter by data after this date (inclusive)
                       Defaults to 1663286400000
                       Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            end_date: Optional filter by data before this date (exclusive)
                     Defaults to 1664496000000
                     Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            size: Optional number of records per page
                 Defaults to 100 if not specified. Maximum is 1000
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
            action: Optional filter by action

        Returns:
            DataFrame containing the wallet lens data
        """
        params = {}

        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        if size:
            params['size'] = size
        if time_format:
            params['timeFormat'] = time_format.value
        if action:
            params['action'] = action.value

        url = AMBERDATA_DEFI_REST_DEX_WALLET_LENS_ENDPOINT.format(protocolId=protocol_id.value,
                                                                  walletAddress=wallet_address)
        description = f"DEX Wallet Lens Request for wallet {wallet_address} on protocol {protocol_id.value}"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, self._headers(), description)

        logging.info(f"Finished {description}")

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_dex_wallet_lens(
            self, protocol_id: ProtocolId, wallet_address: str, start_date: str = None,
            end_date: str = None, size: int = None, time_format: TimeFormat = None,
            action: ProtocolAction = None, index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes wallet lens data for a specific wallet on a DEX protocol.

        Args:
            protocol_id: Required protocol ID for which to retrieve lens data
                        Example: uniswapv3
            wallet_address: Required wallet address for which to retrieve lens data
                          Example: 0x7ff28d78bffb7b571db98ea48e7a77128bac8456
            start_date: Optional filter by data after this date (inclusive)
                       Defaults to 1663286400000
                       Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            end_date: Optional filter by data before this date (exclusive)
                     Defaults to 1664496000000
                     Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            size: Optional number of records per page
                 Defaults to 100 if not specified. Maximum is 1000
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
            action: Optional filter by action
            index_keys: Optional list of column names to use as index

        Returns:
            DataFrame containing the processed wallet lens data
        """
        if index_keys is None:
            index_keys = ['action', 'event', 'timestamp']

        # Get the raw data
        df = self.get_dex_wallet_lens_raw(
            protocol_id=protocol_id,
            wallet_address=wallet_address,
            start_date=start_date,
            end_date=end_date,
            size=size,
            time_format=time_format,
            action=action
        )

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)

    ### 10 - LENDING ALL TRANSACTIONS ###
    def get_lending_protocol_lens_raw(
            self, protocol_id: ProtocolId, start_date: str = None, end_date: str = None,
            size: int = None, direction: SortDirection = None, time_format: TimeFormat = None, action: ProtocolAction = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves lens data for a specific lending protocol.

        Args:
            protocol_id: Required ID of the lending protocol (defaults to aavev2)
                        Example: aavev2
            start_date: Optional filter by data after this date (inclusive)
                       Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            end_date: Optional filter by data before this date (exclusive)
                     Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            size: Optional number of records per page
                 If not specified, the API will default to and try to return 1000 actions
            direction: Optional order in which to return the results (ascending or descending)
                      By default, records are returned in ascending order
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
            action: Optional filter data by specific action

        Returns:
            DataFrame containing the lens data for the specified lending protocol
        """
        params = {}

        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        if size:
            params['size'] = size
        if direction:
            params['direction'] = direction.value
        if time_format:
            params['timeFormat'] = time_format.value
        if action:
            params['action'] = action.value

        url = AMBERDATA_DEFI_REST_LENDING_PROTOCOL_LENS_ENDPOINT.format(protocolId=protocol_id.value)
        description = f"Lending Protocol Lens Request for protocol {protocol_id.value}"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, self._headers(), description)

        logging.info(f"Finished {description}")

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_lending_protocol_lens(
            self, protocol_id: ProtocolId, start_date: str = None, end_date: str = None,
            size: int = None, direction: SortDirection = None, time_format: TimeFormat = None, action: ProtocolAction = None,
            index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes lens data for a specific lending protocol.

        Args:
            protocol_id: Required ID of the lending protocol (defaults to aavev2)
                        Example: aavev2
            start_date: Optional filter by data after this date (inclusive)
                       Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            end_date: Optional filter by data before this date (exclusive)
                     Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            size: Optional number of records per page
                 If not specified, the API will default to and try to return 1000 actions
            direction: Optional order in which to return the results (ascending or descending)
                      By default, records are returned in ascending order
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
            action: Optional filter data by specific action
            index_keys: Optional list of column names to use as index
                       Defaults to ['timestamp']

        Returns:
            DataFrame containing the processed lens data for the specified lending protocol
        """
        if index_keys is None:
            index_keys = ['marketId' ,'action']

        # Get the raw data
        df = self.get_lending_protocol_lens_raw(
            protocol_id=protocol_id,
            start_date=start_date,
            end_date=end_date,
            size=size,
            direction=direction,
            time_format=time_format,
            action=action
        )

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)

    def get_lending_asset_lens_raw(
            self, protocol_id: ProtocolId, asset: str,
            start_date: str = None, end_date: str = None, size: int = None,
            direction: SortDirection = None, time_format: TimeFormat = None, action: ProtocolAction = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves lens data for a specific asset on a lending protocol.

        Args:
            protocol_id: Required ID of the lending protocol (defaults to aavev2)
                        Example: aavev2
            asset: Required token symbol (defaults to WETH)
                  Example: WETH
            start_date: Optional filter by data after this date (inclusive)
                       Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            end_date: Optional filter by data before this date (exclusive)
                     Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            size: Optional number of records per page
                 If not specified, the API will default to and try to return 1000 actions
            direction: Optional order in which to return the results (ascending or descending)
                      By default, records are returned in ascending order
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
            action: Optional filter data by specific action
                   Examples: UseReserveAsCollateral|Deposit|Withdraw|LiquidationCall|Repay|Borrow|FlashLoan

        Returns:
            DataFrame containing the lens data for the specified asset on the lending protocol
        """
        params = {}

        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        if size:
            params['size'] = size
        if direction:
            params['direction'] = direction.value
        if time_format:
            params['timeFormat'] = time_format.value
        if action:
            params['action'] = action.value

        url = AMBERDATA_DEFI_REST_LENDING_ASSET_LENS_ENDPOINT.format(
            protocolId=protocol_id.value, asset=asset
        )
        description = f"Lending Asset Lens Request for protocol {protocol_id.value}, asset {asset}"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, self._headers(), description)

        logging.info(f"Finished {description}")

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_lending_asset_lens(
            self, protocol_id: ProtocolId, asset: str,
            start_date: str = None, end_date: str = None, size: int = None,
            direction: SortDirection = None, time_format: TimeFormat = None, action: ProtocolAction = None,
            index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes lens data for a specific asset on a lending protocol.

        Args:
            protocol_id: Required ID of the lending protocol (defaults to aavev2)
                        Example: aavev2
            asset: Required token symbol (defaults to WETH)
                  Example: WETH
            start_date: Optional filter by data after this date (inclusive)
                       Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            end_date: Optional filter by data before this date (exclusive)
                     Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            size: Optional number of records per page
                 If not specified, the API will default to and try to return 1000 actions
            direction: Optional order in which to return the results (ascending or descending)
                      By default, records are returned in ascending order
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
            action: Optional filter data by specific action
                   Examples: UseReserveAsCollateral|Deposit|Withdraw|LiquidationCall|Repay|Borrow|FlashLoan
            index_keys: Optional list of column names to use as index
                       Defaults to ['timestamp']

        Returns:
            DataFrame containing the processed lens data for the specified asset
        """
        if index_keys is None:
            index_keys = ['marketId', 'action']

        # Get the raw data
        df = self.get_lending_asset_lens_raw(
            protocol_id=protocol_id,
            asset=asset,
            start_date=start_date,
            end_date=end_date,
            size=size,
            direction=direction,
            time_format=time_format,
            action=action
        )

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)

    def get_lending_wallet_lens_raw(
            self, protocol_id: ProtocolId, wallet_address: str,
            start_date: str, end_date: str, size: int = None,
            direction: SortDirection = None, time_format: TimeFormat = None, action: ProtocolAction = None,
            blockchain_id: Blockchain = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves lens data for a specific wallet on a lending protocol.

        Args:
            protocol_id: Required ID of the lending protocol (defaults to aavev2)
                        Example: aavev2
            wallet_address: Required wallet address (defaults to 0x1ec5878ffc42e6d5d80422bdd06cf0712e5611fd)
                           Example: 0x1ec5878ffc42e6d5d80422bdd06cf0712e5611fd
            start_date: Optional filter by data after this date (inclusive)
                       Defaults to 2022-09-01
                       Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            end_date: Optional filter by data before this date (exclusive)
                     Defaults to 2022-10-31
                     Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            size: Optional number of records per page
                 If not specified, the API will default to and try to return 1000 actions
            direction: Optional order in which to return the results (ascending or descending)
                      By default, records are returned in ascending order
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
            action: Optional filter data by specific action

        Returns:
            DataFrame containing the lens data for the specified wallet on the lending protocol
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
        }

        if size:
            params['size'] = size
        if direction:
            params['direction'] = direction.value
        if time_format:
            params['timeFormat'] = time_format.value
        if action:
            params['action'] = action.value

        headers = self._headers()
        if blockchain_id:
            headers['x-amberdata-blockchain-id'] = blockchain_id.value

        url = AMBERDATA_DEFI_REST_LENDING_WALLET_LENS_ENDPOINT.format(
            protocolId=protocol_id.value, walletAddress=wallet_address
        )
        description = f"Lending Wallet Lens Request for protocol {protocol_id.value}, wallet {wallet_address}"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, headers, description)

        logging.info(f"Finished {description}")

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_lending_wallet_lens(
            self, protocol_id: ProtocolId, wallet_address: str,
            start_date: str, end_date: str, size: int = None,
            direction: SortDirection = None, time_format: TimeFormat = None, action: ProtocolAction = None,
            index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes lens data for a specific wallet on a lending protocol.

        Args:
            protocol_id: Required ID of the lending protocol (defaults to aavev2)
                        Example: aavev2
            wallet_address: Required wallet address (defaults to 0x1ec5878ffc42e6d5d80422bdd06cf0712e5611fd)
                           Example: 0x1ec5878ffc42e6d5d80422bdd06cf0712e5611fd
            start_date: Optional filter by data after this date (inclusive)
                       Defaults to 2022-09-01
                       Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            end_date: Optional filter by data before this date (exclusive)
                     Defaults to 2022-10-31
                     Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            size: Optional number of records per page
                 If not specified, the API will default to and try to return 1000 actions
            direction: Optional order in which to return the results (ascending or descending)
                      By default, records are returned in ascending order
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
            action: Optional filter data by specific action
            index_keys: Optional list of column names to use as index
                       Defaults to ['timestamp']

        Returns:
            DataFrame containing the processed lens data for the specified wallet
        """
        if index_keys is None:
            index_keys = ['marketId', 'action']

        # Get the raw data
        df = self.get_lending_wallet_lens_raw(
            protocol_id=protocol_id,
            wallet_address=wallet_address,
            start_date=start_date,
            end_date=end_date,
            size=size,
            direction=direction,
            time_format=time_format,
            action=action
        )

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)

    def get_lending_governance_lens_raw(
            self, protocol_id: ProtocolId, start_date: str, end_date: str,
            size: int = None, direction: SortDirection = None, time_format: TimeFormat = None, proposal_id: str = None,
            address: str = None, support: bool = None
    ) -> pd.DataFrame:
        """
        Raw function that retrieves governance lens data for a lending protocol.

        Args:
            protocol_id: Required ID of the lending protocol (defaults to aavev2)
                        Example: aavev2
                        Note: Aave has the same governance regardless of protocol version (v2 vs. v3)
            start_date: Optional filter by data after this date (inclusive)
                       Defaults to 2022-09-01
                       Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            end_date: Optional filter by data before this date (exclusive)
                     Defaults to 2022-09-30
                     Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            size: Optional number of records per page
            direction: Optional order in which to return the results (ascending or descending)
                      By default, records are returned in descending order
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
            proposal_id: Optional proposal ID to filter results by
            address: Optional wallet address to filter results by
            support: Optional filter results by votes for or votes against

        Returns:
            DataFrame containing the governance lens data for the specified lending protocol
        """
        params = {
        }

        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        if size:
            params['size'] = size
        if direction:
            params['direction'] = direction.value
        if time_format:
            params['timeFormat'] = time_format
        if proposal_id:
            params['proposalId'] = proposal_id
        if address:
            params['address'] = address
        if support is not None:
            params['support'] = support

        url = AMBERDATA_DEFI_REST_LENDING_GOVERNANCE_LENS_ENDPOINT.format(protocolId=protocol_id.value)
        description = f"Lending Governance Lens Request for protocol {protocol_id.value}"

        logging.info(f"Starting {description}")

        # Use get_and_process_response_df to get the DataFrame
        df = RestService.get_and_process_response_df(url, params, self._headers(), description)

        logging.info(f"Finished {description}")

        if not df.empty:
            return df
        else:
            logging.error("No valid data found in the response.")
            raise ValueError("No valid data found in the response.")

    @convert_timestamp
    def get_lending_governance_lens(
            self, protocol_id: ProtocolId, start_date: str, end_date: str,
            size: int = None, direction: SortDirection = None, time_format: TimeFormat = None, proposal_id: str = None,
            address: str = None, support: bool = None, index_keys: list = None
    ) -> pd.DataFrame:
        """
        Processed function that retrieves and processes governance lens data for a lending protocol.

        Args:
            protocol_id: Required ID of the lending protocol (defaults to aavev2)
                        Example: aavev2
                        Note: Aave has the same governance regardless of protocol version (v2 vs. v3)
            start_date: Optional filter by data after this date (inclusive)
                       Defaults to 2022-09-01
                       Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            end_date: Optional filter by data before this date (exclusive)
                     Defaults to 2022-09-30
                     Examples: 1578531600 | 1578531600000 | 2020-09-01T01:00:00
            size: Optional number of records per page
            direction: Optional order in which to return the results (ascending or descending)
                      By default, records are returned in descending order
            time_format: Optional time format of the timestamps in the return payload
                        Options: milliseconds | ms | iso | iso8601 | hr | human_readable
            proposal_id: Optional proposal ID to filter results by
            address: Optional wallet address to filter results by
            support: Optional filter results by votes for or votes against
            index_keys: Optional list of column names to use as index
                       Defaults to ['timestamp']

        Returns:
            DataFrame containing the processed governance lens data for the specified lending protocol
        """
        if index_keys is None:
            index_keys = ['proposalId', 'governorId']

        # Get the raw data
        df = self.get_lending_governance_lens_raw(
            protocol_id=protocol_id,
            start_date=start_date,
            end_date=end_date,
            size=size,
            direction=direction,
            time_format=time_format,
            proposal_id=proposal_id,
            address=address,
            support=support
        )

        # Ensure that index_keys exist in the DataFrame
        for key in index_keys:
            if key not in df.columns:
                raise ValueError(f"Key '{key}' not found in DataFrame columns")

        # Set the index using the specified index_keys
        return df.set_index(index_keys)

