import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List

import pandas as pd
from loguru import logger as lg

from amberdata_rest.common import RestService, NoDataReturned, ApiKeyGetMode
from amberdata_rest.constants import MarketDataVenue, AMBERDATA_SPOT_REST_EXCHANGES_ENDPOINT, AMBERDATA_SPOT_REST_PAIRS_ENDPOINT, \
    AMBERDATA_SPOT_REST_EXCHANGES_REFERENCE_ENDPOINT, AMBERDATA_SPOT_REST_PRICES_ENDPOINT, TimeInterval, BatchPeriod, \
    AMBERDATA_SPOT_REST_REFERENCE_RATES_ENDPOINT, TimeFormat, AMBERDATA_SPOT_REST_TWAP_ENDPOINT, \
    AMBERDATA_SPOT_REST_OHLCV_ENDPOINT, AMBERDATA_SPOT_REST_TRADES_ENDPOINT, AMBERDATA_SPOT_REST_TICKERS_ENDPOINT, \
    AMBERDATA_SPOT_REST_ORDER_BOOK_SNAPSHOTS_ENDPOINT, AMBERDATA_SPOT_REST_VWAP_ENDPOINT, \
    AMBERDATA_SPOT_REST_LEGACY_OHLCV_ENDPOINT, SortDirection, DailyTime


class SpotRestService(RestService):

    def __init__(self, api_key_get_mode: ApiKeyGetMode, api_key_get_params: Dict, max_threads: int = 32):
        RestService.__init__(self, api_key_get_mode, api_key_get_params, max_threads)

    def get_exchanges_information(self, exchanges: List[MarketDataVenue] = None, instruments: List[str] = None,
                                  time_format: TimeFormat = None) -> Dict:
        params = {}
        if exchanges is not None and len(exchanges) > 0:
            params['exchange'] = ",".join(exchange.value for exchange in exchanges)
        if instruments is not None and len(instruments) > 0:
            params['instrument'] = ",".join(instrument for instrument in instruments)
        if time_format is not None:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_SPOT_REST_EXCHANGES_ENDPOINT
        description = "SPOT Exchanges Request"
        lg.info(f"Starting {description}")
        return_dict = RestService.get_and_process_response_dict(url, params, self._headers(), description)
        lg.info(f"Finished {description}")
        return return_dict

    def get_pairs_information(self, pair: str = None, time_format: TimeFormat = None, include_inactive: bool = None) -> Dict:
        params = {}
        if pair is not None:
            params['pair'] = pair
        if include_inactive is not None:
            params['includeInactive'] = str(include_inactive).lower()
        if time_format is not None:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_SPOT_REST_PAIRS_ENDPOINT
        description = "SPOT Pairs Request"
        lg.info(f"Starting {description}")
        return_dict = self.get_and_process_response_dict(url, params, self._headers(), description)
        lg.info(f"Finished {description}")
        return return_dict

    def get_exhanges_reference(self, exchanges: List[MarketDataVenue] = None, instruments: List[str] = None,
                               include_inactive: bool = None, include_original_reference: bool = None) -> Dict:
        params = {}
        if exchanges is not None and len(exchanges) > 0:
            params['exchange'] = ",".join(exchange.value for exchange in exchanges)
        if instruments is not None and len(instruments) > 0:
            params['instrument'] = ",".join(instrument for instrument in instruments)
        if include_inactive is not None:
            params['includeInactive'] = str(include_inactive).lower()
        if include_original_reference is not None:
            params['includeOriginalReference'] = str(include_original_reference).lower()

        url = AMBERDATA_SPOT_REST_EXCHANGES_REFERENCE_ENDPOINT
        description = "SPOT Reference Request"
        lg.info(f"Starting {description}")
        return_dict = self.get_and_process_response_dict(url, params, self._headers(), description)
        lg.info(f"Finished {description}")
        return return_dict


    def get_prices_assets_information_raw(self, asset: str = None, time_format: TimeFormat = None,
                                          include_inactive: bool = None) -> pd.DataFrame:
        params = {}
        if asset is not None:
            params['asset'] = asset
        if time_format is not None:
            params['timeFormat'] = time_format.value if isinstance(time_format, TimeFormat) else time_format
        if include_inactive is not None:
            params['includeInactive'] = str(include_inactive).lower()

        url = AMBERDATA_SPOT_REST_PRICES_ENDPOINT + "assets/information"
        description = "SPOT Prices Asset Information Request"
        lg.info(f"Starting {description} with URL: {url} and params: {params}")

        return_df = RestService.get_and_process_response_df(url, params, self._headers(), description)
        lg.info(f"Finished {description}")
        return return_df

    def get_prices_assets_information(self, asset: str = None, time_format: TimeFormat = None,
                                      include_inactive: bool = False, index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['asset']
        return self.get_prices_assets_information_raw(asset, time_format, include_inactive).set_index(index_keys)

    def get_prices_assets_latest_raw(self, asset: str, time_format: TimeFormat = None) -> pd.DataFrame:
        params = {}
        if time_format is not None:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_SPOT_REST_PRICES_ENDPOINT + f"assets/{asset}/latest"
        description = "SPOT Prices Latest By Asset Request"
        lg.info(f"Starting {description}")
        return_df = RestService.get_and_process_response_df(url, params, self._headers(), description)
        lg.info(f"Finished {description}")
        return return_df

    def get_prices_assets_latest(self, asset: str, time_format: TimeFormat = None,
                                 index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['asset']
        return self.get_prices_assets_latest_raw(asset, time_format).set_index(index_keys)

    def get_prices_assets_historical_raw(self, asset: str, start_date: datetime = None, end_date: datetime = None,
                                         time_interval: TimeInterval = None, time_format: TimeFormat = None,
                                         batch_period: timedelta = BatchPeriod.HOUR_8.value, parallel_execution=False) -> pd.DataFrame:
        params = {}
        if start_date is not None:
            params['startDate'] = start_date.isoformat()
        if end_date is not None:
            params['endDate'] = end_date.isoformat()
        if time_interval is not None:
            params['timeInterval'] = time_interval.value if isinstance(time_interval, TimeInterval) else time_interval
        if time_format is not None:
            params['timeFormat'] = time_format.value if isinstance(time_format, TimeFormat) else time_format

        url = AMBERDATA_SPOT_REST_PRICES_ENDPOINT + f"assets/{asset}/historical/"
        description = "SPOT Prices Historical By Asset Request"
        lg.info(f"Starting {description}")
        if parallel_execution:
            _df = self._process_parallel(start_date, end_date, batch_period, self._headers(), url, params, description,
                                         self._get_max_threads())
            # Check if timestamp or exchangeTimestamp + exchangeTimestampNano is present and sort by it otherwise skip sorting
            if 'timestamp' in _df.columns:
                _df.sort_values('timestamp', inplace=True)
            elif 'exchangeTimestamp' in _df.columns and 'exchangeTimestampNano' in _df.columns:
                _df.sort_values(['exchangeTimestamp', 'exchangeTimestampNano'], inplace=True)

        else:
            current_batch_time = start_date
            _df = None
            while current_batch_time < end_date:
                batch_end_time = min(current_batch_time + batch_period, end_date)
                params['startDate'] = current_batch_time.isoformat(timespec='milliseconds')
                params['endDate'] = batch_end_time.isoformat(timespec='milliseconds')
                lg.debug(f"Getting data for startDate:{params['startDate']} and endDate:{params['endDate']}")
                _batch = RestService.get_and_process_response_df(url, params, self._headers(), description)
                lg.debug(f"Finished data for startDate:{params['startDate']} and endDate:{params['endDate']}")
                if not _batch.empty:
                    _df = _batch.reset_index() if _df is None else pd.concat([_df, _batch.reset_index()],
                                                                             ignore_index=True)
                current_batch_time = batch_end_time
        if _df is None:
            lg.warning("No data was returned! Please check your query and/or time range")
        elif 'index' in _df.columns:
            _df.drop(['index'], axis=1, inplace=True)
        lg.info(f"Finished {description}")
        return _df

    def get_prices_assets_historical(self, asset: str, start_date: datetime = None, end_date: datetime = None,
                                     time_interval: TimeInterval = None, time_format: TimeFormat = None,
                                     index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['asset', 'timestamp']
        return self.get_prices_assets_historical_raw(asset, start_date, end_date, time_interval, time_format).set_index(
            index_keys)

    def get_prices_pairs_information_raw(self, pair: str, time_format: TimeFormat = None,
                                         include_inactive: bool = False) -> pd.DataFrame:
        params = {}
        params['pair'] = pair
        if time_format is not None:
            params['timeFormat'] = time_format.value if isinstance(time_format, TimeFormat) else time_format
        if include_inactive is not None:
            params['includeInactive'] = str(include_inactive).lower()

        url = AMBERDATA_SPOT_REST_PRICES_ENDPOINT + "pairs/information"
        description = "SPOT Prices Pair Information Request"
        lg.info(f"Starting {description}")
        response_dict = RestService.get_and_process_response_dict(url, params, self._headers(), description)
        lg.info(f"Finished {description}")

        # Extract the payload data
        data = response_dict.get('data', [])

        # Convert to DataFrame
        return_df = pd.DataFrame(data)
        return return_df

    def get_prices_pairs_information(self, pair: str = "btc_usd", time_format: TimeFormat = None,
                                     include_inactive: bool = False, index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['pair']
        return self.get_prices_pairs_information_raw(pair, time_format, include_inactive).set_index(index_keys)

    def get_prices_pairs_latest_raw(self, pair: str, exchange: MarketDataVenue = None,
                                    include_cross_rates: bool = False, time_format: TimeFormat = None) -> pd.DataFrame:
        params = {}
        if exchange is not None:
            params['exchange'] = exchange.value
        params['includeCrossRates'] = str(include_cross_rates).lower()  # This should always be included
        if time_format is not None:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_SPOT_REST_PRICES_ENDPOINT + f"pairs/{pair}/latest"
        description = "SPOT Prices Latest By Pair Request"
        lg.info(f"Starting {description}")

        response_dict = RestService.get_and_process_response_dict(url, params, self._headers(), description)
        lg.info(f"Finished {description}")

        # Extract the payload
        data = response_dict.get('data', {})

        # Check if the data contains the required keys
        if not data:
            raise ValueError(f"No data found in the response: {json.dumps(response_dict, indent=2)}")

        # Process the data into a DataFrame
        processed_data = {
            'timestamp': [data['timestamp']],
            'pair': [data['pair']],
            'price': [data['price']],
            'volume': [data['volume']],
            'exchange': [params['exchange']] if 'exchange' in params else [None]
        }
        df = pd.DataFrame(processed_data)
        return df

    def get_prices_pairs_latest(self, pair: str, exchange: MarketDataVenue = None,
                                include_cross_rates: bool = False, time_format: TimeFormat = None,
                                index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['pair']
        df = self.get_prices_pairs_latest_raw(pair, exchange, include_cross_rates, time_format)
        return df.set_index(index_keys)

    def get_prices_pairs_historical_raw(self, pair: str, exchange: MarketDataVenue = None,
                                        start_date: datetime = None, end_date: datetime = None,
                                        include_cross_rates: bool = False, time_interval: TimeInterval = None,
                                        time_format: TimeFormat = None,
                                        batch_period: timedelta = BatchPeriod.HOUR_1.value,
                                        parallel_execution: bool = False) -> pd.DataFrame:
        params = {}
        if time_interval is not None:
            params['timeInterval'] = time_interval.value if isinstance(time_interval, TimeInterval) else time_interval
        if exchange is not None:
            params['exchange'] = exchange.value
        if include_cross_rates is not None:
            params['includeCrossRates'] = str(include_cross_rates).lower()
        if start_date is not None:
            params['startDate'] = start_date.isoformat(timespec='milliseconds')
        if end_date is not None:
            params['endDate'] = end_date.isoformat(timespec='milliseconds')
        if time_format is not None:
            params['timeFormat'] = time_format.value if isinstance(time_format, TimeFormat) else time_format

        url = AMBERDATA_SPOT_REST_PRICES_ENDPOINT + f"pairs/{pair}/historical/"
        description = "SPOT Prices Historical By Pair Request"
        lg.info(f"Starting {description}")
        if parallel_execution:
            _df = self._process_parallel(start_date, end_date, batch_period, self._headers(), url, params, description,
                                         self._get_max_threads())
            # Check if timestamp or exchangeTimestamp + exchangeTimestampNano is present and sort by it otherwise skip sorting
            if 'timestamp' in _df.columns:
                _df.sort_values('timestamp', inplace=True)
            elif 'exchangeTimestamp' in _df.columns and 'exchangeTimestampNano' in _df.columns:
                _df.sort_values(['exchangeTimestamp', 'exchangeTimestampNano'], inplace=True)
        else:
            current_batch_time = start_date
            _df = None
            while current_batch_time < end_date:
                batch_end_time = min(current_batch_time + batch_period, end_date)
                params['startDate'] = current_batch_time.isoformat(timespec='milliseconds')
                params['endDate'] = batch_end_time.isoformat(timespec='milliseconds')
                lg.debug(f"Getting data for startDate:{params['startDate']} and endDate:{params['endDate']}")
                _batch = RestService.get_and_process_response_df(url, params, self._headers(), description)
                lg.debug(f"Finished data for startDate:{params['startDate']} and endDate:{params['endDate']}")
                if not _batch.empty:
                    _df = _batch.reset_index() if _df is None else pd.concat([_df, _batch.reset_index()],
                                                                             ignore_index=True)
                current_batch_time = batch_end_time

        if _df is None:
            lg.warning("No data was returned! Please check your query and/or time range")
        elif 'index' in _df.columns:
            _df.drop(['index'], axis=1, inplace=True)
        lg.info(f"Finished {description}")
        return _df

    def get_prices_pairs_historical(self, pair: str, exchanges: MarketDataVenue = None, start_date: datetime = None,
                                    end_date: datetime = None, include_cross_rates: bool = False,
                                    time_interval: TimeInterval = None, time_format: TimeFormat = None,
                                    batch_period: timedelta = BatchPeriod.HOUR_1.value, index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['pair', 'timestamp']
        return self.get_prices_pairs_historical_raw(pair, exchanges, start_date, end_date, include_cross_rates,
                                                    time_interval, time_format, batch_period).set_index(index_keys)

    def get_reference_rates_raw(self, assetId: str, start_date: datetime, end_date: datetime,
                                time_format: TimeFormat = None, time_interval: TimeInterval = None,
                                daily_time: DailyTime = None, sort_direction: SortDirection = None,
                                batch_period: timedelta = BatchPeriod.HOUR_1.value, parallel_execution: bool = False) -> pd.DataFrame:
        params = {}
        if time_format is not None:
            params['timeFormat'] = time_format.value
        if time_interval is not None:
            params['timeInterval'] = time_interval.value
        if daily_time is not None:
            params['dailyTime'] = daily_time.value
        if sort_direction is not None:
            params['direction'] = sort_direction.value
        url = AMBERDATA_SPOT_REST_REFERENCE_RATES_ENDPOINT + f"{assetId}"
        description = "SPOT Reference Quites Historical By Pair Request"
        lg.info(f"Starting {description}")
        if parallel_execution:
            _df = self._process_parallel(start_date, end_date, batch_period, self._headers(), url, params, description,
                                         self._get_max_threads())
            # Check if timestamp or exchangeTimestamp + exchangeTimestampNano is present and sort by it otherwise skip sorting
            if 'timestamp' in _df.columns:
                _df.sort_values('timestamp', inplace=True)
            elif 'exchangeTimestamp' in _df.columns and 'exchangeTimestampNano' in _df.columns:
                _df.sort_values(['exchangeTimestamp', 'exchangeTimestampNano'], inplace=True)
        else:
            current_batch_time = start_date
            _df = None
            while current_batch_time < end_date:
                batch_end_time = min(current_batch_time + batch_period, end_date)
                params['startDate'] = current_batch_time.isoformat(timespec='milliseconds')
                params['endDate'] = batch_end_time.isoformat(timespec='milliseconds')
                lg.debug(f"Getting data for startDate:{params['startDate']} and endDate:{params['endDate']}")
                _batch = RestService.get_and_process_response_df(url, params, self._headers(),
                                                                 description)
                lg.debug(f"Finished data for startDate:{params['startDate']} and endDate:{params['endDate']}")
                if not _batch.empty:
                    _df = _batch.reset_index() if _df is None else pd.concat([_df, _batch.reset_index()],
                                                                             ignore_index=True)
                current_batch_time = batch_end_time

        if _df is None:
            lg.warning("No data was returned! Please check your query and/or time range")
        elif 'index' in _df.columns:
            _df.drop(['index'], axis=1, inplace=True)
        lg.info(f"Finished {description}")
        return _df

    def get_reference_rates(self, asset_id: str, start_date: datetime = None, end_date: datetime = None,
                            time_format: TimeFormat = None, time_interval: TimeInterval = None,
                            daily_time: DailyTime = None, sort_direction: SortDirection = None,
                            batch_period: timedelta = BatchPeriod.HOUR_1.value, index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['pair', 'timestamp']
        raw_data = self.get_reference_rates_raw(asset_id, start_date, end_date, time_format, time_interval, daily_time, sort_direction, batch_period)
        return raw_data.set_index(index_keys)

    def get_ticker_information_raw(self, exchanges: List[MarketDataVenue] = None, include_inactive: bool = None,
                                   time_format: TimeFormat = None) -> pd.DataFrame:
        params = {}
        if exchanges is not None and len(exchanges) > 0:
            params['exchange'] = ",".join(exchange.value for exchange in exchanges)
        if include_inactive is not None:
            params['includeInactive'] = str(include_inactive).lower()
        if time_format is not None:
            params['timeFormat'] = time_format.value if isinstance(time_format, TimeFormat) else time_format

        url = AMBERDATA_SPOT_REST_TICKERS_ENDPOINT + "information"
        description = "SPOT Ticker Information Request"
        lg.info(f"Starting {description}")
        raw_response = RestService.get_and_process_response_dict(url, params, self._headers(), description)
        lg.info(f"Finished {description}")

        # Process raw data into DataFrame
        processed_data = []
        if 'data' in raw_response:
            for item in raw_response['data']:
                processed_data.append(item)

        return pd.DataFrame(processed_data)

    def get_ticker_information(self, exchanges: List[MarketDataVenue] = None, include_inactive: bool = None,
                               time_format: TimeFormat = None, index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['exchange']
        return self.get_ticker_information_raw(exchanges, include_inactive, time_format).set_index(index_keys)

    def get_historical_ticker_raw(self, instrument: str, exchange: MarketDataVenue, start_date: datetime = None,
                                  end_date: datetime = None, time_format: TimeFormat = None,
                                  batch_period: BatchPeriod = BatchPeriod.HOUR_8, parallel_exec: bool = False) -> pd.DataFrame:
        params = {
            'exchange': exchange.value,
        }
        if start_date is not None:
            params['startDate'] = start_date.isoformat(timespec='milliseconds')
        if end_date is not None:
            params['endDate'] = end_date.isoformat(timespec='milliseconds')
        if time_format is not None:
            params['timeFormat'] = time_format.value
        url = AMBERDATA_SPOT_REST_TICKERS_ENDPOINT + f"{instrument}"
        description = f"SPOT Historical Ticker Request for {instrument}"
        lg.info(f"Starting {description}")
        if parallel_exec:
            return_df = RestService._process_parallel(start_date, end_date, batch_period.value, self._headers(), url,
                                                      params, description, self._get_max_threads())
        else:
            return_df = RestService.get_and_process_response_df(url, params, self._headers(), description)
        lg.info(f"Finished {description}")
        return return_df

    def get_historical_ticker(self, instrument: str, exchange: MarketDataVenue = None, start_date: datetime = None,
                              end_date: datetime = None, time_format: TimeFormat = None,
                              index_keys: List[str] = None, batch_period: BatchPeriod = BatchPeriod.HOUR_8,
                              parallel_exec: bool = False) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['timestamp', 'instrument', 'exchange']
        return self.get_historical_ticker_raw(instrument, exchange, start_date, end_date,
                                              time_format, batch_period=batch_period,
                                              parallel_exec=parallel_exec).set_index(index_keys)


    def get_order_book_information_raw(self, exchanges: List[MarketDataVenue] = None, include_inactive: bool = None,
                                       time_format: TimeFormat = None) -> pd.DataFrame:
        params = {}
        if exchanges is not None and len(exchanges) > 0:
            params['exchange'] = ",".join(exchange.value for exchange in exchanges)
        if include_inactive is not None:
            params['includeInactive'] = str(include_inactive).lower()
        if time_format is not None:
            params['timeFormat'] = time_format.value if isinstance(time_format, TimeFormat) else time_format

        url = AMBERDATA_SPOT_REST_ORDER_BOOK_SNAPSHOTS_ENDPOINT + "information"
        description = "SPOT Order Book Information Request"
        lg.info(f"Starting {description}")
        return_df = RestService.get_and_process_response_df(url, params, self._headers(), description)
        lg.info(f"Finished {description}")
        return return_df

    def get_order_book_information(self, exchanges: List[MarketDataVenue] = None, include_inactive: bool = None,
                                   time_format: TimeFormat = None, index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['exchange', 'instrument']
        return self.get_order_book_information_raw(exchanges, include_inactive, time_format).set_index(index_keys)

    def get_order_book_snapshots_historical_raw(self, instrument: str, exchange: MarketDataVenue,
                                                start_date: datetime = None, end_date: datetime = None, max_level: int = None,
                                                timestamp: datetime = None, time_format: TimeFormat = None,
                                                batch_period: timedelta = BatchPeriod.HOUR_8.value,
                                                parallel_execution: bool = False) -> pd.DataFrame:
        params = {'exchange': exchange.value}
        if max_level is not None:
            params['maxLevel'] = max_level
        if timestamp is not None:
            params['timestamp'] = timestamp.isoformat()
        if time_format is not None:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_SPOT_REST_ORDER_BOOK_SNAPSHOTS_ENDPOINT + f"{instrument}"
        description = f"SPOT Order Book Snapshots Historical Request for {instrument}"
        lg.info(f"Starting {description}")

        if parallel_execution:
            _df = self._process_parallel(start_date, end_date, batch_period, self._headers(), url, params, description, self._get_max_threads())
            # Check if timestamp or exchangeTimestamp + exchangeTimestampNano is present and sort by it otherwise skip sorting
            if 'timestamp' in _df.columns:
                _df.sort_values('timestamp', inplace=True)
            elif 'exchangeTimestamp' in _df.columns and 'exchangeTimestampNano' in _df.columns:
                _df.sort_values(['exchangeTimestamp', 'exchangeTimestampNano'], inplace=True)
        else:
            if start_date is not None and end_date is not None:
                current_batch_time = start_date
                _df = None
                while current_batch_time < end_date:
                    batch_end_time = min(current_batch_time + batch_period, end_date)
                    params['startDate'] = current_batch_time.isoformat(timespec='milliseconds')
                    params['endDate'] = batch_end_time.isoformat(timespec='milliseconds')
                    lg.debug(f"Getting data for startDate:{params['startDate']} and endDate:{params['endDate']}")
                    _batch = RestService.get_and_process_response_df(url, params, self._headers(), description)
                    lg.debug(f"Finished data for startDate:{params['startDate']} and endDate:{params['endDate']}")
                    if not _batch.empty:
                        _df = _batch if _df is None else pd.concat([_df, _batch], ignore_index=True)
                    current_batch_time = batch_end_time
            else:
                _df = RestService.get_and_process_response_df(url, params, self._headers(), description)

        if _df is None:
            lg.warning("No data was returned! Please check your query and/or time range")
        elif 'index' in _df.columns:
            _df.drop(['index'], axis=1, inplace=True)
        lg.info(f"Finished {description}")
        return _df

    def get_order_book_snapshots_historical(self, instrument: str, exchange: MarketDataVenue = None, start_date: datetime = None,
                                            end_date: datetime = None, max_level: int = None, timestamp: datetime = None,
                                            time_format: TimeFormat = None, index_keys: List[str] = None,
                                            batch_period: timedelta = BatchPeriod.HOUR_8.value,
                                            parallel_execution: bool = False) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['timestamp', 'instrument', 'exchange']
        processed_df = self.get_order_book_snapshots_historical_raw(
            instrument, exchange, start_date, end_date, max_level, timestamp, time_format,
            batch_period, parallel_execution
        )
        return processed_df.set_index(index_keys)


    def get_order_book_events_historical_raw(self, instrument: str, exchange: MarketDataVenue, start_date: datetime = None,
                                             end_date: datetime = None, time_format: TimeFormat = None) -> pd.DataFrame:
        params = {'exchange': exchange.value}
        if start_date is not None:
            params['startDate'] = start_date.isoformat()
        if end_date is not None:
            params['endDate'] = end_date.isoformat()
        if time_format is not None:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_SPOT_REST_ORDER_BOOK_SNAPSHOTS_ENDPOINT + f"{instrument}"
        description = f"SPOT Order Book Events Historical Request for {instrument}"
        lg.info(f"Starting {description}")
        raw_data = RestService.get_and_process_response_dict(url, params, self._headers(), description)
        lg.info(f"Finished {description}")

        # Process the raw data into a more structured format
        processed_data = []
        if 'data' in raw_data:
            for entry in raw_data['data']:
                timestamp = entry.get('exchangeTimestamp')
                instrument = entry.get('instrument')
                exchangeStr = entry.get('exchange')
                asks = entry.get('ask', [])
                bids = entry.get('bid', [])

                for ask in asks:
                    processed_data.append({
                        'timestamp': timestamp,
                        'instrument': instrument,
                        'exchange': exchangeStr,
                        'side': 'ask',
                        'price': ask.get('price'),
                        'volume': ask.get('volume'),
                        'numOrders': ask.get('numOrders')
                    })
                for bid in bids:
                    processed_data.append({
                        'timestamp': timestamp,
                        'instrument': instrument,
                        'exchange': exchangeStr,
                        'side': 'bid',
                        'price': bid.get('price'),
                        'volume': bid.get('volume'),
                        'numOrders': bid.get('numOrders')
                    })

        # Convert processed data into DataFrame
        processed_df = pd.DataFrame(processed_data)
        return processed_df

    def get_order_book_events_historical(self, instrument: str, exchange: MarketDataVenue, start_date: datetime = None,
                                         end_date: datetime = None, time_format: TimeFormat = None,
                                         index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['timestamp', 'instrument', 'exchange', 'side']
        processed_df = self.get_order_book_events_historical_raw(instrument, exchange, start_date, end_date, time_format)
        return processed_df.set_index(index_keys)


    def get_trades_information_raw(self, exchange: List[MarketDataVenue] = None, include_inactive: bool = None,
                                   time_format: TimeFormat = None) -> pd.DataFrame:
        params = {}
        if include_inactive is not None:
            params['includeInactive'] = str(include_inactive).lower()
        if time_format is not None:
            params['timeFormat'] = time_format.value
        if exchange:
            params['exchange'] = exchange

        url = AMBERDATA_SPOT_REST_TRADES_ENDPOINT + "information"
        description = "SPOT Trades Information Request"
        lg.info(f"Starting {description}")
        return_df = RestService.get_and_process_response_df(url, params, self._headers(), description)
        lg.info(f"Finished {description}")
        return return_df

    def get_trades_information(self, exchange: List[MarketDataVenue] = None, include_inactive: bool = None, time_format: TimeFormat = None,
                               index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['exchange', 'instrument']
        return self.get_trades_information_raw(exchange, include_inactive, time_format).set_index(index_keys)

    def get_trades_historical_raw(self, instrument: str, exchange: MarketDataVenue, start_date: datetime = None, end_date: datetime = None,
                                  time_format: TimeFormat = None, batch_period: timedelta = BatchPeriod.HOUR_8.value,
                                  parallel_execution: bool = False) -> pd.DataFrame:
        params = {'exchange': exchange.value}
        if start_date is not None:
            params['startDate'] = start_date.isoformat()
        if end_date is not None:
            params['endDate'] = end_date.isoformat()
        if time_format is not None:
            params['timeFormat'] = time_format.value if isinstance(time_format, TimeFormat) else time_format

        url = AMBERDATA_SPOT_REST_TRADES_ENDPOINT + f"{instrument}"
        description = "SPOT Trades Historical Request"
        lg.info(f"Starting {description}")

        if parallel_execution:
            _df = self._process_parallel(start_date, end_date, batch_period, self._headers(), url, params, description,
                                         self._get_max_threads())
            # Check if timestamp or exchangeTimestamp + exchangeTimestampNano is present and sort by it otherwise skip sorting
            if 'timestamp' in _df.columns:
                _df.sort_values('timestamp', inplace=True)
            elif 'exchangeTimestamp' in _df.columns and 'exchangeTimestampNano' in _df.columns:
                _df.sort_values(['exchangeTimestamp', 'exchangeTimestampNano'], inplace=True)
        else:
            if start_date is not None and end_date is not None:
                current_batch_time = start_date
                _df = None
                while current_batch_time < end_date:
                    batch_end_time = min(current_batch_time + batch_period, end_date)
                    params['startDate'] = current_batch_time.isoformat(timespec='milliseconds')
                    params['endDate'] = batch_end_time.isoformat(timespec='milliseconds')
                    lg.debug(f"Getting data for startDate:{params['startDate']} and endDate:{params['endDate']}")
                    _batch = RestService.get_and_process_response_df(url, params, self._headers(), description)
                    lg.debug(f"Finished data for startDate:{params['startDate']} and endDate:{params['endDate']}")
                    if not _batch.empty:
                        _df = _batch if _df is None else pd.concat([_df, _batch], ignore_index=True)
                    current_batch_time = batch_end_time
            else:
                _df = RestService.get_and_process_response_df(url, params, self._headers(), description)

        if _df is None:
            lg.warning("No data was returned! Please check your query and/or time range")
        elif 'index' in _df.columns:
            _df.drop(['index'], axis=1, inplace=True)
        lg.info(f"Finished {description}")
        return _df

    def get_trades_historical(self, instrument: str, exchange: MarketDataVenue, start_date: datetime = None, end_date: datetime = None,
                              time_format: TimeFormat = None, batch_period = BatchPeriod.HOUR_8.value, parallel_execution: bool = False,
                              index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['exchangeTimestamp', 'exchangeTimestampNanoseconds', 'instrument', 'exchange']
        raw_df = self.get_trades_historical_raw(instrument, exchange, start_date, end_date, time_format,
                                                batch_period, parallel_execution)
        return raw_df.set_index(index_keys)

    def get_ohlcv_information_raw(self, exchanges: List[MarketDataVenue] = None, include_inactive: bool = False,
                                  time_interval: TimeInterval = None, time_format: TimeFormat = None) -> pd.DataFrame:
        params = {}
        if exchanges is not None and len(exchanges) > 0:
            params['exchange'] = ",".join(exchange.value for exchange in exchanges)
        if include_inactive:
            params['includeInactive'] = str(include_inactive).lower()
        if time_interval is not None:
            params['timeInterval'] = time_interval.value
        if time_format is not None:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_SPOT_REST_OHLCV_ENDPOINT + f"information"
        description = "SPOT OHLCV Information Request"
        lg.info(f"Starting {description}")
        raw_data = RestService.get_and_process_response_dict(url, params, self._headers(), description)
        lg.info(f"Finished {description}")

        # Process the raw data into a more structured format
        processed_data = []
        for entry in raw_data['data']:
            row = {
                'exchange': entry['exchange'],
                'pair': entry['instrument'],
                'address': entry['address'],
                'startDate': entry['startDate'],
                'endDate': entry['endDate']
            }
            processed_data.append(row)

        # Convert processed data into DataFrame
        processed_df = pd.DataFrame(processed_data)
        return processed_df

    def get_ohlcv_information(self, exchanges: List[MarketDataVenue] = None, include_inactive: bool = False,
                              time_interval: TimeInterval = None, time_format: TimeFormat = None,
                              index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['exchange', 'pair']
        processed_df = self.get_ohlcv_information_raw(exchanges, include_inactive, time_interval, time_format)
        return processed_df.set_index(index_keys)

    def get_ohlcv_historical_raw(self, instrument: str, exchanges: List[MarketDataVenue], start_date: datetime = None,
                                 end_date: datetime = None, time_interval: TimeInterval = None,
                                 time_format: TimeFormat = None) -> pd.DataFrame:
        all_processed_data = []

        for exchange in exchanges:
            params = {'exchange': exchange.value}
            if start_date is not None:
                params['startDate'] = start_date.isoformat()
            if end_date is not None:
                params['endDate'] = end_date.isoformat()
            if time_interval is not None:
                params['timeInterval'] = time_interval.value
            if time_format is not None:
                params['timeFormat'] = time_format.value

            url = AMBERDATA_SPOT_REST_OHLCV_ENDPOINT + f"{instrument}"
            description = f"SPOT OHLCV Historical Request for {instrument} on {exchange.value}"
            logging.info(f"Starting {description} with URL: {url} and params: {params}")

            raw_data = RestService.get_and_process_response_dict(url, params, self._headers(), description)
            logging.info(f"Finished {description}")

            # Check if 'data' key exists
            if not raw_data:
                logging.error("Raw response is empty.")
                raise NoDataReturned("Raw response is empty.")
            if 'data' not in raw_data:
                logging.error(f"Key 'data' not found in the response. Raw response: {json.dumps(raw_data, indent=2)}")
                raise NoDataReturned(
                    f"Key 'data' not found in the response. Raw response: {json.dumps(raw_data, indent=2)}")

            # Process the raw data into a more structured format
            processed_data = []
            for ohlcv in raw_data['data']:
                processed_data.append({
                    'timestamp': ohlcv['exchangeTimestamp'],
                    'open': ohlcv['open'],
                    'high': ohlcv['high'],
                    'low': ohlcv['low'],
                    'close': ohlcv['close'],
                    'volume': ohlcv['volume'],
                    'exchange': exchange.value,
                    'instrument': ohlcv['instrument']
                })

            all_processed_data.extend(processed_data)

        # Convert processed data into DataFrame
        processed_df = pd.DataFrame(all_processed_data)
        return processed_df

    def get_ohlcv_historical(self, instrument: str, exchanges: List[MarketDataVenue], start_date: datetime = None,
                             end_date: datetime = None, time_interval: TimeInterval = None,
                             time_format: TimeFormat = None,
                             index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['exchange', 'timestamp']
        processed_df = self.get_ohlcv_historical_raw(instrument, exchanges, start_date, end_date, time_interval,
                                                     time_format)
        return processed_df.set_index(index_keys)

    def get_ohlcv_by_exchange_historical_raw(self, exchange: List[MarketDataVenue], pairs: List[str],
                                             start_date: datetime = None,
                                             end_date: datetime = None, time_interval: TimeInterval = None,
                                             time_format: TimeFormat = None) -> pd.DataFrame:
        params = {'pair': ",".join(pairs)}
        if start_date is not None:
            params['startDate'] = start_date.isoformat()
        if end_date is not None:
            params['endDate'] = end_date.isoformat()
        if time_interval is not None:
            params['timeInterval'] = time_interval.value
        if time_format is not None:
            params['timeFormat'] = time_format.value

        exchange_str = ",".join([e.value for e in exchange])
        url = AMBERDATA_SPOT_REST_LEGACY_OHLCV_ENDPOINT + f"exchange/{exchange_str}/historical"
        description = f"SPOT OHLCV Batch Historical Request for {exchange_str}"
        lg.info(f"Starting {description}")
        raw_data = RestService.get_and_process_response_dict(url, params, self._headers(), description)
        lg.info(f"Finished {description}")

        # Check if 'data' key exists
        if 'data' not in raw_data:
            raise NoDataReturned(f"Key 'data' not found in the response. Raw response: {str(raw_data)}")

        # Process the raw data into a more structured format
        processed_data = []
        metadata = raw_data.get('metadata', {})
        columns = metadata.get('columns', ['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        for pair, ohlcv_list in raw_data['data'].items():
            for ohlcv in ohlcv_list:
                processed_row = {col: val for col, val in zip(columns, ohlcv)}
                processed_row['exchange'] = exchange_str
                processed_row['pair'] = pair
                processed_data.append(processed_row)

        # Convert processed data into DataFrame
        processed_df = pd.DataFrame(processed_data)
        return processed_df

    def get_ohlcv_by_exchange_historical(self, exchange: List[MarketDataVenue], pairs: List[str],
                                         start_date: datetime = None,
                                         end_date: datetime = None, time_interval: TimeInterval = None,
                                         time_format: TimeFormat = None,
                                         index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['exchange', 'pair', 'timestamp']
        processed_df = self.get_ohlcv_by_exchange_historical_raw(exchange, pairs, start_date, end_date, time_interval,
                                                                 time_format)
        return processed_df.set_index(index_keys)

    def get_twap_assets_information_raw(self, asset: str = None, time_format: TimeFormat = None) -> pd.DataFrame:
        params = {}
        if asset is not None:
            params['asset'] = asset
        if time_format is not None:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_SPOT_REST_TWAP_ENDPOINT + f"assets/information"
        description = "Global TWAP Assets Information Request"
        lg.info(f"Starting {description}")
        raw_data = RestService.get_and_process_response_dict(url, params, self._headers(), description)
        lg.info(f"Finished {description}")

        # Check if 'data' key exists
        if 'data' not in raw_data:
            raise NoDataReturned(f"Key 'data' not found in the response. Raw response: {str(raw_data)}")

        # Process the raw data into a more structured format
        processed_data = []
        for entry in raw_data['data']:
            asset = entry['asset']
            start_date = entry['startDate']
            end_date = entry['endDate']
            for reference in entry['marketDataReference']:
                processed_data.append({
                    'asset': asset,
                    'startDate': start_date,
                    'endDate': end_date,
                    'exchange': reference['exchange'],
                    'assetSymbol': reference['assetSymbol']
                })

        # Convert processed data into DataFrame
        processed_df = pd.DataFrame(processed_data)
        return processed_df

    def get_twap_assets_information(self, asset: str = None, time_format: TimeFormat = None,
                                    index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['asset', 'exchange']
        processed_df = self.get_twap_assets_information_raw(asset, time_format)
        return processed_df.set_index(index_keys)

    def get_twap_asset_latest_raw(self, asset: str, lookback_period: int = None,
                                  time_format: TimeFormat = None) -> pd.DataFrame:
        params = {}
        if lookback_period is not None:
            params['lookbackPeriod'] = lookback_period
        if time_format is not None:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_SPOT_REST_TWAP_ENDPOINT + f"assets/{asset}/latest"
        description = f"Global TWAP Asset Latest Request for {asset}"
        lg.info(f"Starting {description}")
        raw_data = RestService.get_and_process_response_dict(url, params, self._headers(), description)
        lg.info(f"Finished {description}")

        # Check if 'data' key exists
        if 'data' not in raw_data:
            raise NoDataReturned(f"Key 'data' not found in the response. Raw response: {str(raw_data)}")

        # Convert data into DataFrame
        payload = raw_data['data']
        processed_data = [{
            'timestamp': payload['timestamp'],
            'asset': payload['asset'],
            'price': payload['price'],
            'twap': payload['twap'],
            'volume': payload['volume']
        }]

        processed_df = pd.DataFrame(processed_data)
        return processed_df

    def get_twap_asset_latest(self, asset: str, lookback_period: int = None, time_format: TimeFormat = None,
                              index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['asset', 'timestamp']
        processed_df = self.get_twap_asset_latest_raw(asset, lookback_period, time_format)
        return processed_df.set_index(index_keys)

    def get_twap_asset_historical_raw(self, asset: str, start_date: datetime = None, end_date: datetime = None,
                                      time_interval: TimeInterval = None, lookback_period: int = None,
                                      time_format: TimeFormat = None) -> pd.DataFrame:
        params = {}
        if start_date is not None:
            params['startDate'] = start_date.isoformat()
        if end_date is not None:
            params['endDate'] = end_date.isoformat()
        if time_interval is not None:
            params['timeInterval'] = time_interval.value
        if lookback_period is not None:
            params['lookbackPeriod'] = lookback_period
        if time_format is not None:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_SPOT_REST_TWAP_ENDPOINT + f"assets/{asset}/historical"
        description = f"Global TWAP Asset Historical Request for {asset}"
        headers = self._headers()

        lg.info(f"Starting {description}")

        success, raw_data = RestService._get_response(url, params, headers, description)
        if not success:
            raise NoDataReturned(
                f"Failed to fetch data for request: {description}, url: {url}, params: {params}, headers: {headers} after 5 retries.")

        lg.info(f"Finished {description}")

        # Check if 'payload' key exists
        if 'payload' not in raw_data or 'data' not in raw_data['payload']:
            raise NoDataReturned(f"Key 'payload' or 'data' not found in the response. Raw response: {str(raw_data)}")

        # Convert data into DataFrame
        processed_data = [{
            'timestamp': entry['timestamp'],
            'asset': entry['asset'],
            'price': entry['price'],
            'twap': entry['twap'],
            'volume': entry.get('volume')  # Use get to avoid KeyError if 'volume' is missing
        } for entry in raw_data['payload']['data']]

        processed_df = pd.DataFrame(processed_data)
        return processed_df

    def get_twap_asset_historical(self, asset: str, start_date: datetime = None, end_date: datetime = None,
                                  time_interval: TimeInterval = None, lookback_period: int = None,
                                  time_format: TimeFormat = None, index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['asset', 'timestamp']
        processed_df = self.get_twap_asset_historical_raw(asset, start_date, end_date, time_interval, lookback_period,
                                                          time_format)
        return processed_df.set_index(index_keys)

    def get_twap_pairs_information_raw(self, pair: str = None, time_format: TimeFormat = None) -> pd.DataFrame:
        params = {}
        if pair is not None:
            params['pair'] = pair
        if time_format is not None:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_SPOT_REST_TWAP_ENDPOINT + "pairs/information"
        description = "Global TWAP Pairs Information Request"
        headers = self._headers()

        lg.info(f"Starting {description}")

        success, raw_data = RestService._get_response(url, params, headers, description)
        if not success:
            raise NoDataReturned(
                f"Failed to fetch data for request: {description}, url: {url}, params: {params}, headers: {headers} after 5 retries.")

        lg.info(f"Finished {description}")

        # Check if 'payload' key exists
        if 'payload' not in raw_data or 'data' not in raw_data['payload']:
            raise NoDataReturned(f"Key 'payload' or 'data' not found in the response. Raw response: {str(raw_data)}")

        # Convert data into DataFrame
        processed_data = [{
            'pair': entry['pair'],
            'startDate': entry['startDate'],
            'endDate': entry['endDate']
        } for entry in raw_data['payload']['data']]

        processed_df = pd.DataFrame(processed_data)
        return processed_df

    def get_twap_pairs_information(self, pair: str = None, time_format: TimeFormat = None,
                                   index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['pair']
        processed_df = self.get_twap_pairs_information_raw(pair, time_format)
        return processed_df.set_index(index_keys)

    def get_twap_pairs_latest_raw(self, pair: str, exchange: MarketDataVenue = None, include_cross_rates: bool = None,
                                  lookback_period: int = None, time_format: TimeFormat = None) -> pd.DataFrame:
        params = {}
        if exchange is not None:
            params['exchange'] = exchange.value
        if include_cross_rates is not None:
            params['includeCrossRates'] = str(include_cross_rates).lower()
        if lookback_period is not None:
            params['lookbackPeriod'] = lookback_period
        if time_format is not None:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_SPOT_REST_TWAP_ENDPOINT + f"pairs/{pair}/latest"
        description = f"Global TWAP Pairs Latest Request for {pair}"
        headers = self._headers()

        lg.info(f"Starting {description}")

        success, raw_data = RestService._get_response(url, params, headers, description)
        if not success:
            raise NoDataReturned(
                f"Failed to fetch data for request: {description}, url: {url}, params: {params}, headers: {headers} after 5 retries.")

        lg.info(f"Finished {description}")

        # Check if 'payload' key exists
        if 'payload' not in raw_data:
            raise NoDataReturned(f"Key 'payload' not found in the response. Raw response: {str(raw_data)}")

        # Convert data into DataFrame
        payload = raw_data['payload']
        processed_data = [{
            'timestamp': payload['timestamp'],
            'pair': payload['pair'],
            'price': payload['price'],
            'volume': payload['volume'],
            'twap': payload['twap']
        }]

        processed_df = pd.DataFrame(processed_data)
        return processed_df

    def get_twap_pairs_latest(self, pair: str, exchange: MarketDataVenue = None, include_cross_rates: bool = None,
                              lookback_period: int = None, time_format: TimeFormat = None,
                              index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['pair', 'timestamp']
        processed_df = self.get_twap_pairs_latest_raw(pair, exchange, include_cross_rates, lookback_period, time_format)
        return processed_df.set_index(index_keys)

    def get_twap_pairs_historical_raw(self, pair: str, exchange: MarketDataVenue = None, include_cross_rates: bool = None,
                                      start_date: datetime = None, end_date: datetime = None, time_interval: TimeInterval = None,
                                      lookback_period: int = None, time_format: TimeFormat = None) -> pd.DataFrame:
        params = {}
        if exchange is not None:
            params['exchange'] = exchange.value
        if include_cross_rates is not None:
            params['includeCrossRates'] = str(include_cross_rates).lower()
        if start_date is not None:
            params['startDate'] = start_date.isoformat()
        if end_date is not None:
            params['endDate'] = end_date.isoformat()
        if time_interval is not None:
            params['timeInterval'] = time_interval.value
        if lookback_period is not None:
            params['lookbackPeriod'] = lookback_period
        if time_format is not None:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_SPOT_REST_TWAP_ENDPOINT + f"pairs/{pair}/historical"
        description = f"Global TWAP Pairs Historical Request for {pair}"
        headers = self._headers()

        lg.info(f"Starting {description}")

        success, raw_data = RestService._get_response(url, params, headers, description)
        if not success:
            raise NoDataReturned(
                f"Failed to fetch data for request: {description}, url: {url}, params: {params}, headers: {headers} after 5 retries.")

        lg.info(f"Finished {description}")

        # Check if 'payload' key exists
        if 'payload' not in raw_data:
            raise NoDataReturned(f"Key 'payload' not found in the response. Raw response: {str(raw_data)}")

        # Process the raw data into a more structured format
        payload = raw_data['payload']
        data = payload['data']

        processed_data = []
        for entry in data:
            processed_data.append({
                'timestamp': entry['timestamp'],
                'pair': entry['pair'],
                'price': entry.get('price'),
                'volume': entry.get('volume'),
                'twap': entry['twap']
            })

        # Convert processed data into DataFrame
        processed_df = pd.DataFrame(processed_data)
        return processed_df

    def get_twap_pairs_historical(self, pair: str, exchange: MarketDataVenue = None, include_cross_rates: bool = None,
                                  start_date: datetime = None, end_date: datetime = None, time_interval: TimeInterval = None,
                                  lookback_period: int = None, time_format: TimeFormat = None,
                                  index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['pair', 'timestamp']
        processed_df = self.get_twap_pairs_historical_raw(pair, exchange, include_cross_rates, start_date, end_date,
                                                          time_interval, lookback_period, time_format)
        return processed_df.set_index(index_keys)

    def get_vwap_assets_information_raw(self, asset: str = None, time_format: TimeFormat = None) -> pd.DataFrame:
        params = {}
        if asset is not None:
            params['asset'] = asset
        if time_format is not None:
            params['timeFormat'] = time_format.value if isinstance(time_format, TimeFormat) else time_format

        url = AMBERDATA_SPOT_REST_VWAP_ENDPOINT + "assets/information"
        description = "Global VWAP Assets Information Request"
        lg.info(f"Starting {description}")
        raw_data = self.get_and_process_response_dict(url, params, self._headers(), description)
        lg.info(f"Finished {description}")

        # Process the raw data into a more structured format
        processed_data = []
        if 'data' in raw_data:
            for entry in raw_data['data']:
                asset = entry.get('asset', None)
                start_date = entry.get('startDate', None)
                end_date = entry.get('endDate', None)
                if 'marketDataReference' in entry:
                    for reference in entry['marketDataReference']:
                        processed_data.append({
                            'asset': asset,
                            'startDate': start_date,
                            'endDate': end_date,
                            'assetSymbol': reference.get('assetSymbol', None),
                            'exchange': reference.get('exchange', None)
                        })
                else:
                    processed_data.append({
                        'asset': asset,
                        'startDate': start_date,
                        'endDate': end_date,
                        'assetSymbol': None,
                        'exchange': None
                    })

        # Convert processed data into DataFrame
        processed_df = pd.DataFrame(processed_data)
        return processed_df

    def get_vwap_assets_information(self, asset: str = None, time_format: TimeFormat = None,
                                    index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['asset', 'exchange']
        processed_df = self.get_vwap_assets_information_raw(asset, time_format)
        if not processed_df.empty:
            return processed_df.set_index(index_keys)
        return processed_df

    def get_vwap_asset_latest_raw(self, asset: str, lookback_period: int = None,
                                  time_format: TimeFormat = None) -> pd.DataFrame:
        params = {}
        if lookback_period is not None and lookback_period <= 90:
            params['lookbackPeriod'] = lookback_period
        if time_format is not None:
            params['timeFormat'] = time_format.value if isinstance(time_format, TimeFormat) else time_format

        url = AMBERDATA_SPOT_REST_VWAP_ENDPOINT + f"assets/{asset}/latest"
        description = f"Global VWAP Asset Latest Request for {asset}"
        lg.info(f"Starting {description}")
        raw_data = self.get_and_process_response_dict(url, params, self._headers(), description)
        lg.info(f"Finished {description}")

        # Process the raw data into a more structured format
        processed_data = []
        if 'data' in raw_data:
            entry = raw_data['data']
            processed_data.append({
                'timestamp': entry.get('timestamp'),
                'asset': entry.get('asset'),
                'price': entry.get('price'),
                'vwap': entry.get('vwap'),
                'volume': entry.get('volume')
            })

        # Convert processed data into DataFrame
        processed_df = pd.DataFrame(processed_data)
        return processed_df

    def get_vwap_asset_latest(self, asset: str, lookback_period: int = None, time_format: TimeFormat = None,
                              index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['asset', 'timestamp']
        processed_df = self.get_vwap_asset_latest_raw(asset, lookback_period, time_format)
        if not processed_df.empty:
            return processed_df.set_index(index_keys)
        return processed_df

    def get_vwap_asset_historical_raw(self, asset: str, start_date: datetime = None, end_date: datetime = None,
                                      time_interval: TimeInterval = None, lookback_period: int = None,
                                      time_format: TimeFormat = None) -> pd.DataFrame:
        params = {}
        if start_date is not None:
            params['startDate'] = start_date.isoformat(timespec='seconds')
        if end_date is not None:
            params['endDate'] = end_date.isoformat(timespec='seconds')
        if time_interval is not None:
            params['timeInterval'] = time_interval.value if isinstance(time_interval, TimeInterval) else time_interval
        if lookback_period is not None:
            params['lookbackPeriod'] = lookback_period
        if time_format is not None:
            params['timeFormat'] = time_format.value if isinstance(time_format, TimeFormat) else time_format

        url = AMBERDATA_SPOT_REST_VWAP_ENDPOINT + f"assets/{asset}/historical"
        description = f"Global VWAP Asset Historical Request for {asset}"
        lg.info(f"Starting {description}")
        raw_data = self.get_and_process_response_dict(url, params, self._headers(), description)
        lg.info(f"Finished {description}")

        # Process the raw data into a more structured format
        processed_data = []
        if 'data' in raw_data:
            for entry in raw_data['data']:
                processed_data.append({
                    'timestamp': entry.get('timestamp'),
                    'asset': entry.get('asset'),
                    'price': entry.get('price'),
                    'vwap': entry.get('vwap'),
                    'volume': entry.get('volume')
                })

        # Convert processed data into DataFrame
        processed_df = pd.DataFrame(processed_data)
        return processed_df

    def get_vwap_asset_historical(self, asset: str, start_date: datetime = None, end_date: datetime = None,
                                  time_interval: TimeInterval = None, lookback_period: int = None,
                                  time_format: TimeFormat = None, index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['asset', 'timestamp']
        processed_df = self.get_vwap_asset_historical_raw(asset, start_date, end_date, time_interval, lookback_period,
                                                          time_format)
        if not processed_df.empty:
            return processed_df.set_index(index_keys)
        return processed_df

    def get_vwap_pairs_information_raw(self, pair: str = None, time_format: TimeFormat = None) -> pd.DataFrame:
        params = {}
        if pair is not None:
            params['pair'] = pair
        if time_format is not None:
            params['timeFormat'] = time_format.value if isinstance(time_format, TimeFormat) else time_format

        url = AMBERDATA_SPOT_REST_VWAP_ENDPOINT + "pairs/information"
        description = "Global VWAP Pairs Information Request"
        lg.info(f"Starting {description}")
        raw_data = self.get_and_process_response_dict(url, params, self._headers(), description)
        lg.info(f"Finished {description}")

        # Process the raw data into a more structured format
        processed_data = []
        if 'data' in raw_data:
            for entry in raw_data['data']:
                pair = entry.get('pair', None)
                start_date = entry.get('startDate', None)
                end_date = entry.get('endDate', None)
                if 'marketDataReference' in entry:
                    for reference in entry['marketDataReference']:
                        processed_data.append({
                            'pair': pair,
                            'startDate': start_date,
                            'endDate': end_date,
                            'assetSymbol': reference.get('assetSymbol', None),
                            'exchange': reference.get('exchange', None)
                        })
                else:
                    processed_data.append({
                        'pair': pair,
                        'startDate': start_date,
                        'endDate': end_date,
                        'assetSymbol': None,
                        'exchange': None
                    })

        # Convert processed data into DataFrame
        processed_df = pd.DataFrame(processed_data)
        return processed_df

    def get_vwap_pairs_information(self, pair: str = None, time_format: TimeFormat = None,
                                   index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['pair', 'exchange']
        processed_df = self.get_vwap_pairs_information_raw(pair, time_format)
        if not processed_df.empty:
            return processed_df.set_index(index_keys)
        return processed_df
    def get_vwap_pair_latest_raw(self, pair: str, exchange: MarketDataVenue = None, include_cross_rates: bool = None,
                                 lookback_period: int = None, time_format: TimeFormat = None) -> pd.DataFrame:
        params = {}
        if exchange is not None:
            params['exchange'] = exchange.value
        if include_cross_rates is not None and exchange is None:
            params['includeCrossRates'] = str(include_cross_rates).lower()
        if lookback_period is not None and lookback_period <= 90:
            params['lookbackPeriod'] = lookback_period
        if time_format is not None:
            params['timeFormat'] = time_format.value if isinstance(time_format, TimeFormat) else time_format

        url = AMBERDATA_SPOT_REST_VWAP_ENDPOINT + f"pairs/{pair}/latest"
        description = f"Global VWAP Pair Latest Request for {pair}"
        lg.info(f"Starting {description}")
        raw_data = self.get_and_process_response_dict(url, params, self._headers(), description)
        lg.info(f"Finished {description}")

        # Process the raw data into a more structured format
        processed_data = []
        if 'data' in raw_data:
            entry = raw_data['data']
            processed_data.append({
                'timestamp': entry.get('timestamp'),
                'pair': entry.get('pair'),
                'price': entry.get('price'),
                'vwap': entry.get('vwap'),
                'volume': entry.get('volume')
            })

        # Convert processed data into DataFrame
        processed_df = pd.DataFrame(processed_data)
        return processed_df

    def get_vwap_pair_latest(self, pair: str, exchange: MarketDataVenue = None, include_cross_rates: bool = None,
                             lookback_period: int = None, time_format: TimeFormat = None,
                             index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['pair', 'timestamp']
        processed_df = self.get_vwap_pair_latest_raw(pair, exchange, include_cross_rates, lookback_period, time_format)
        if not processed_df.empty:
            return processed_df.set_index(index_keys)
        return processed_df

    def get_vwap_pair_historical_raw(self, pair: str, exchange: MarketDataVenue = None, include_cross_rates: bool = None,
                                     start_date: datetime = None, end_date: datetime = None, time_interval: TimeInterval = None,
                                     lookback_period: int = None, time_format: TimeFormat = None) -> pd.DataFrame:
        params = {}
        if exchange is not None:
            params['exchange'] = exchange.value
        if include_cross_rates is not None and exchange is None:
            params['includeCrossRates'] = str(include_cross_rates).lower()
        if start_date is not None:
            params['startDate'] = start_date.isoformat(timespec='seconds')
        if end_date is not None:
            params['endDate'] = end_date.isoformat(timespec='seconds')
        if time_interval is not None:
            params['timeInterval'] = time_interval.value if isinstance(time_interval, TimeInterval) else time_interval
        if lookback_period is not None and lookback_period <= 90:
            params['lookbackPeriod'] = lookback_period
        if time_format is not None:
            params['timeFormat'] = time_format.value if isinstance(time_format, TimeFormat) else time_format

        url = AMBERDATA_SPOT_REST_VWAP_ENDPOINT + f"pairs/{pair}/historical"
        description = f"Global VWAP Pair Historical Request for {pair}"
        lg.info(f"Starting {description}")
        raw_data = self.get_and_process_response_dict(url, params, self._headers(), description)
        lg.info(f"Finished {description}")

        # Process the raw data into a more structured format
        processed_data = []
        if 'data' in raw_data:
            for entry in raw_data['data']:
                processed_data.append({
                    'timestamp': entry.get('timestamp'),
                    'pair': entry.get('pair'),
                    'price': entry.get('price'),
                    'vwap': entry.get('vwap'),
                    'volume': entry.get('volume')
                })

        # Convert processed data into DataFrame
        processed_df = pd.DataFrame(processed_data)
        return processed_df

    def get_vwap_pair_historical(self, pair: str, exchange: List[MarketDataVenue] = None, include_cross_rates: bool = None,
                                 start_date: datetime = None, end_date: datetime = None, time_interval: TimeInterval = None,
                                 lookback_period: int = None, time_format: TimeFormat = None,
                                 index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['pair', 'timestamp']
        processed_df = self.get_vwap_pair_historical_raw(pair, exchange, include_cross_rates, start_date, end_date,
                                                         time_interval, lookback_period, time_format)
        if not processed_df.empty:
            return processed_df.set_index(index_keys)
        return processed_df

