import datetime
import json
from typing import List, Dict

import pandas as pd
from loguru import logger as lg

from amberdata_rest.common import RestService, NoDataReturned, ApiKeyGetMode
from amberdata_rest.constants import \
    AMBERDATA_FUTURES_REST_FUNDING_RATES_ENDPOINT, AMBERDATA_FUTURES_REST_LIQUIDATIONS_ENDPOINT, \
    AMBERDATA_FUTURES_REST_LONG_SHORT_RATIO_ENDPOINT, \
    TimeInterval, MarketDataVenue, TimeFormat, AMBERDATA_FUTURES_REST_INSURANCE_FUNDS_ENDPOINT, \
    SortDirection, AMBERDATA_FUTURES_REST_BATCH_FUNDING_RATES_ENDPOINT, AMBERDATA_FUTURES_REST_OHLCV_ENDPOINT, \
    AMBERDATA_FUTURES_REST_BATCH_OHLCV_ENDPOINT, AMBERDATA_FUTURES_REST_OPEN_INTEREST_ENDPOINT, \
    AMBERDATA_FUTURES_REST_BATCH_OPEN_INTEREST_ENDPOINT, AMBERDATA_FUTURES_REST_ORDER_BOOK_SNAPSHOTS_ENDPOINT, \
    AMBERDATA_FUTURES_REST_ORDER_BOOK_EVENTS_ENDPOINT, AMBERDATA_FUTURES_REST_TICKERS_ENDPOINT, \
    AMBERDATA_FUTURES_REST_TRADES_ENDPOINT, AMBERDATA_FUTURES_REST_EXCHANGES_REFERENCE_ENDPOINT, BatchPeriod


class FuturesRestService(RestService):

    def __init__(self, api_key_get_mode: ApiKeyGetMode, api_key_get_params: Dict, max_threads: int = 32):
        RestService.__init__(self, api_key_get_mode, api_key_get_params, max_threads)

    def get_funding_information_raw(self, exchanges: List[MarketDataVenue] = None, include_inactive: bool = None,
                                    time_format: TimeFormat = None) -> pd.DataFrame:
        params = {}
        if exchanges is not None and len(exchanges) > 0:
            params['exchange'] = ",".join(
                [exchange.value for exchange in exchanges])
        if include_inactive is not None:
            params['includeInactive'] = str(include_inactive).lower()
        if time_format is not None:
            params['timeFormat'] = time_format.value
        url = AMBERDATA_FUTURES_REST_FUNDING_RATES_ENDPOINT + "information"
        description = "FUTURES Funding Information Request"
        lg.info(f"Starting {description}")
        return_df = RestService.get_and_process_response_df(url, params, self._headers(), description)

        lg.info(f"Finished {description}")
        return return_df

    def get_funding_information(self, exchanges: List[MarketDataVenue] = None, include_inactive: bool = None,
                                time_format: TimeFormat = None, index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['exchange']
        return self.get_funding_information_raw(exchanges, include_inactive, time_format).set_index(index_keys)

    def get_funding_rates_raw(self, instrument: str, exchange: MarketDataVenue, start_date: datetime = None,
                              end_date: datetime = None, time_format: TimeFormat = None,
                              batch_period: datetime.timedelta = BatchPeriod.HOUR_1.value,
                              parallel_execution: bool = False) -> pd.DataFrame:
        params = {'exchange': exchange.value}
        if start_date is not None:
            params['startDate'] = start_date.isoformat(timespec='milliseconds')
        if end_date is not None:
            params['endDate'] = end_date.isoformat(timespec='milliseconds')
        if time_format is not None:
            params['timeFormat'] = time_format.value
        url = AMBERDATA_FUTURES_REST_FUNDING_RATES_ENDPOINT + f"{instrument}"
        description = "FUTURES Funding Rates Request"
        lg.info(f"Starting {description}")
        if parallel_execution:
            if start_date is None or end_date is None:
                raise ValueError("Start and end date must be provided for parallel execution!")
            else:
                return_df = RestService._process_parallel(start_date, end_date, batch_period, self._headers(), url,
                                                          params, description, self._get_max_threads())
                # Check if timestamp or exchangeTimestamp + exchangeTimestampNano is present and sort by it otherwise skip sorting
                if 'timestamp' in return_df.columns:
                    return_df.sort_values('timestamp', inplace=True)
                elif 'exchangeTimestamp' in return_df.columns and 'exchangeTimestampNano' in return_df.columns:
                    return_df.sort_values(['exchangeTimestamp', 'exchangeTimestampNano'], inplace=True)
        else:
            return_df = RestService.get_and_process_response_df(url, params, self._headers(),
                                                                description)
        lg.info(f"Finished {description}")
        return return_df

    def get_funding_rates(self, instrument: str, exchange: MarketDataVenue, start_date: datetime = None,
                          end_date: datetime = None, time_format: TimeFormat = None,
                          batch_period: datetime.timedelta = BatchPeriod.HOUR_12.value, index_keys: List[str] = None,
                          parallel_execution: bool = False) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['exchange']
        return self.get_funding_rates_raw(instrument, exchange, start_date, end_date, time_format, batch_period, parallel_execution).set_index(index_keys)

    def get_funding_batch_historical_raw(self, exchange: MarketDataVenue, instruments: List[str],
                                         start_date: datetime = None,
                                         end_date: datetime = None, time_interval: TimeInterval = None,
                                         time_format: TimeFormat = None):
        params = {'exchange': exchange.value, 'instrument': ",".join(instrument for instrument in instruments)}
        if start_date is not None:
            params['startDate'] = start_date.isoformat(timespec='milliseconds')
        if end_date is not None:
            params['endDate'] = end_date.isoformat(timespec='milliseconds')
        if time_interval is not None:
            params['timeInterval'] = time_interval.value
        if time_format is not None:
            params['timeFormat'] = time_format.value
        url = AMBERDATA_FUTURES_REST_BATCH_FUNDING_RATES_ENDPOINT + f"exchange/{exchange.value}/" + "historical"
        description = "FUTURES Funding Rates Batch Historical Request"
        lg.info(f"Starting {description}")
        return_df = RestService.get_and_process_response_df(url, params, self._headers(),
                                                            description)
        lg.info(f"Finished {description}")
        return return_df

    def get_funding_batch_historical(self, exchange: MarketDataVenue, instruments: List[str],
                                     start_date: datetime = None,
                                     end_date: datetime = None, time_interval: TimeInterval = None,
                                     time_format: TimeFormat = None,
                                     index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['instrument']
        return self.get_funding_batch_historical_raw(exchange, instruments, start_date, end_date, time_interval,
                                                     time_format).set_index(index_keys)

    def get_insurance_funds_information_raw(self, exchanges: List[MarketDataVenue] = None,
                                            include_inactive: bool = None,
                                            time_format: TimeFormat = None) -> pd.DataFrame:
        params = {}
        if exchanges is not None and len(exchanges) > 0:
            params['exchange'] = ",".join(
                [exchange.value for exchange in exchanges])
        if include_inactive is not None:
            params['includeInactive'] = str(include_inactive).lower()
        if time_format is not None:
            params['timeFormat'] = time_format.value
        url = AMBERDATA_FUTURES_REST_INSURANCE_FUNDS_ENDPOINT + "information"
        description = "FUTURES Insurance Funds Information Request"
        lg.info(f"Starting {description}")
        return_df = RestService.get_and_process_response_df(url, params, self._headers(), description)

        lg.info(f"Finished {description}")
        return return_df

    def get_insurance_funds_information(self, exchanges: List[MarketDataVenue] = None, include_inactive: bool = None,
                                        time_format: TimeFormat = None, index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['exchange']
        return self.get_insurance_funds_information_raw(exchanges, include_inactive, time_format).set_index(index_keys)

    def get_insurance_funds_raw(self, instrument: str, exchange: MarketDataVenue, start_date: datetime = None,
                                end_date: datetime = None, time_format: TimeFormat = None,
                                sort_direction: SortDirection = None):
        params = {'exchange': exchange.value}
        if start_date is not None:
            params['startDate'] = start_date.isoformat(timespec='milliseconds')
        if end_date is not None:
            params['endDate'] = end_date.isoformat(timespec='milliseconds')
        if time_format is not None:
            params['timeFormat'] = time_format.value
        if sort_direction is not None:
            params['sortDirection'] = sort_direction.value
        url = AMBERDATA_FUTURES_REST_INSURANCE_FUNDS_ENDPOINT + f"{instrument}"
        description = "FUTURES Insurance Funds Request"
        lg.info(f"Starting {description}")
        return_df = RestService.get_and_process_response_df(url, params, self._headers(),
                                                            description)
        lg.info(f"Finished {description}")
        return return_df

    def get_insurance_funds(self, instrument: str, exchange: MarketDataVenue, start_date: datetime = None,
                            end_date: datetime = None, time_format: TimeFormat = None,
                            sort_direction: SortDirection = None, index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['exchange']
        return self.get_insurance_funds_raw(instrument, exchange, start_date, end_date, time_format,
                                            sort_direction).set_index(index_keys)

    def get_liquidations_information_raw(self, exchanges: List[MarketDataVenue] = None, include_inactive: bool = None,
                                         time_format: TimeFormat = None) -> pd.DataFrame:
        params = {}
        if exchanges is not None and len(exchanges) > 0:
            params['exchange'] = ",".join(
                [exchange.value for exchange in exchanges])
        if include_inactive is not None:
            params['includeInactive'] = str(include_inactive).lower()
        if time_format is not None:
            params['timeFormat'] = time_format.value
        url = AMBERDATA_FUTURES_REST_LIQUIDATIONS_ENDPOINT + "information"
        description = "FUTURES Liquidations Information"
        lg.info(f"Starting {description}")
        return_df = RestService.get_and_process_response_df(url, params, self._headers(),
                                                            description)
        lg.info(f"Finished {description}")
        return return_df

    def get_liquidations_information(self, exchanges: List[MarketDataVenue] = None, include_inactive: bool = None,
                                     time_format: TimeFormat = None, index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['exchange']
        return self.get_liquidations_information_raw(exchanges, include_inactive, time_format).set_index(index_keys)

    def get_liquidations_raw(self, instrument: str, exchange: MarketDataVenue, start_date: datetime = None,
                             end_date: datetime = None, time_format: TimeFormat = None,
                             sort_direction: SortDirection = None,
                             batch_period: datetime.timedelta = BatchPeriod.HOUR_12.value,
                             parallel_execution: bool = False) -> pd.DataFrame:
        params = {'exchange': exchange.value}
        if start_date is not None:
            params['startDate'] = start_date.isoformat(timespec='milliseconds')
        if end_date is not None:
            params['endDate'] = end_date.isoformat(timespec='milliseconds')
        if time_format is not None:
            params['timeFormat'] = time_format.value
        if sort_direction is not None:
            params['sortDirection'] = sort_direction.value
        url = AMBERDATA_FUTURES_REST_LIQUIDATIONS_ENDPOINT + f"{instrument}"
        description = "FUTURES Liquidations Request"
        lg.info(f"Starting {description}")

        if parallel_execution:
            if start_date is None or end_date is None:
                raise ValueError("Start and end date must be provided for parallel execution!")
            else:
                return_df = RestService._process_parallel(start_date, end_date, batch_period, self._headers(), url,
                                                          params, description, self._get_max_threads())
                # Check if timestamp or exchangeTimestamp + exchangeTimestampNano is present and sort by it otherwise skip sorting
                if 'timestamp' in return_df.columns:
                    return_df.sort_values('timestamp', inplace=True)
                elif 'exchangeTimestamp' in return_df.columns and 'exchangeTimestampNano' in return_df.columns:
                    return_df.sort_values(['exchangeTimestamp', 'exchangeTimestampNano'], inplace=True)
        else:
            return_df = RestService.get_and_process_response_df(url, params, self._headers(),
                                                                description)
        lg.info(f"Finished {description}")
        return return_df

    def get_liquidations(self, instrument: str, exchange: MarketDataVenue, start_date: datetime = None,
                         end_date: datetime = None, time_format: TimeFormat = None,
                         sort_direction: SortDirection = None, index_keys: List[str] = None,
                         batch_period: datetime.timedelta = BatchPeriod.HOUR_12.value,
                         parallel_execution: bool = False) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['exchange', 'instrument']
        return self.get_liquidations_raw(instrument,
                                         exchange, start_date, end_date, time_format, sort_direction,
                                         batch_period, parallel_execution).set_index(index_keys)

    def get_long_short_ratio_information_raw(self, exchanges: [MarketDataVenue] = None, include_inactive: bool = None,
                                             time_format: TimeFormat = None) -> pd.DataFrame:
        params = {}
        if exchanges is not None and len(exchanges) > 0:
            params['exchange'] = ",".join(
                [exchange.name for exchange in exchanges])
        if include_inactive is not None:
            params['includeInactive'] = str(include_inactive).lower()
        if time_format is not None:
            params['timeFormat'] = time_format.value
        url = AMBERDATA_FUTURES_REST_LONG_SHORT_RATIO_ENDPOINT + "information"
        description = "FUTURES Long Short Information Request"
        lg.info(f"Starting {description}")
        return_df = RestService.get_and_process_response_df(url, params, self._headers(),
                                                            description)
        lg.info(f"Finished {description}")
        return return_df

    def get_long_short_ratio_information(self, exchanges: [MarketDataVenue] = None, include_inactive: bool = None,
                                         time_format: TimeFormat = None, index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['exchange']
        return self.get_long_short_ratio_information_raw(exchanges, include_inactive, time_format).set_index(index_keys)

    def get_long_short_ratio_raw(self, instrument: str, exchange: MarketDataVenue = None, start_date: datetime = None,
                                 end_date: datetime = None, time_format: TimeFormat = None, time_interval: TimeInterval = None,
                                 sort_direction: SortDirection = None, batch_period: datetime.timedelta = BatchPeriod.HOUR_1.value,
                                 parallel_execution: bool = False) -> pd.DataFrame:
        params = {'exchange': exchange.value}
        if start_date is not None:
            params['startDate'] = start_date.isoformat(timespec='milliseconds')
        if end_date is not None:
            params['endDate'] = end_date.isoformat(timespec='milliseconds')
        if time_format is not None:
            params['timeFormat'] = time_format.value
        if time_interval is not None:
            params['timeInterval'] = time_interval.value
        if sort_direction is not None:
            params['sortDirection'] = sort_direction.value

        url = AMBERDATA_FUTURES_REST_LONG_SHORT_RATIO_ENDPOINT + f"{instrument}"
        description = "FUTURES Long Short Request"
        lg.info(f"Starting {description}")

        if parallel_execution:
            if start_date is None or end_date is None:
                raise ValueError("Start and end date must be provided for parallel execution!")
            else:
                return_df = RestService._process_parallel(start_date, end_date, batch_period, self._headers(), url,
                                                          params, description, self._get_max_threads())
                # Check if timestamp or exchangeTimestamp + exchangeTimestampNano is present and sort by it otherwise skip sorting
                if 'timestamp' in return_df.columns:
                    return_df.sort_values('timestamp', inplace=True)
                elif 'exchangeTimestamp' in return_df.columns and 'exchangeTimestampNano' in return_df.columns:
                    return_df.sort_values(['exchangeTimestamp', 'exchangeTimestampNano'], inplace=True)
        else:
            return_df = RestService.get_and_process_response_df(url, params, self._headers(), description)

        if not return_df.empty and 'timestamp' in return_df.columns:
            return_df['timestamp'] = pd.to_datetime(return_df["timestamp"], unit="ms", utc=True)
        lg.info(f"Finished {description}")
        return return_df

    def get_long_short_ratio(self, instrument: str, exchange: MarketDataVenue = None, start_date: datetime = None,
                             end_date: datetime = None,
                             time_format: TimeFormat = None, time_interval: TimeInterval = None,
                             sort_direction: SortDirection = None,
                             index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['exchange']
        return self.get_long_short_ratio_raw(instrument, exchange, start_date, end_date, time_format, time_interval,
                                             sort_direction).set_index(index_keys)

    def get_ohlcv_information_raw(self, exchanges: List[MarketDataVenue] = None, include_inactive: bool = False,
                                  time_format: TimeFormat = None) -> pd.DataFrame:
        params = {}
        if exchanges is not None and len(exchanges) > 0:
            params['exchange'] = ",".join(exchange.value for exchange in exchanges)
        if include_inactive:
            params['includeInactive'] = str(include_inactive).lower()
        if time_format is not None:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_FUTURES_REST_OHLCV_ENDPOINT + f"information"
        description = "FUTURES OHLCV Information Request"
        lg.info(f"Starting {description}")
        raw_data = RestService.get_and_process_response_dict(url, params, self._headers(), description)
        lg.info(f"Finished {description}")

        # Process the raw data into a more structured format
        processed_data = []
        for entry in raw_data['data']:
            row = {
                'exchange': entry['exchange'],
                'instrument': entry['instrument'],
                'startDate': entry['startDate'],
                'endDate': entry['endDate']
            }
            processed_data.append(row)

        # Convert processed data into DataFrame
        processed_df = pd.DataFrame(processed_data)
        return processed_df

    def get_ohlcv_information(self, exchanges: List[MarketDataVenue] = None, include_inactive: bool = None,
                              time_format: TimeFormat = None,
                              index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['exchange', 'instrument']
        processed_df = self.get_ohlcv_information_raw(exchanges, include_inactive, time_format)
        return processed_df.set_index(index_keys)

    def get_ohlcv_raw(self, instrument: str, exchanges: List[MarketDataVenue], start_date: datetime = None,
                      end_date: datetime = None, time_interval: TimeInterval = None,
                      time_format: TimeFormat = None, sort_direction: SortDirection = None) -> pd.DataFrame:
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
            if sort_direction is not None:
                params['sortDirection'] = sort_direction.value

            url = AMBERDATA_FUTURES_REST_OHLCV_ENDPOINT + f"{instrument}"
            description = f"FUTURES OHLCV Request for {instrument} on {exchange.value}"
            lg.info(f"Starting {description} with URL: {url} and params: {params}")

            raw_data = RestService.get_and_process_response_dict(url, params, self._headers(), description)
            lg.info(f"Finished {description}")

            # Check if 'data' key exists
            if not raw_data:
                lg.error("Raw response is empty.")
                raise NoDataReturned("Raw response is empty.")
            if 'data' not in raw_data:
                lg.error(f"Key 'data' not found in the response. Raw response: {json.dumps(raw_data, indent=2)}")
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

    def get_ohlcv(self, instrument: str, exchanges: List[MarketDataVenue], start_date: datetime = None,
                  end_date: datetime = None, time_interval: TimeInterval = None,
                  time_format: TimeFormat = None, sort_direction: SortDirection = None,
                  index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['exchange', 'timestamp']
        processed_df = self.get_ohlcv_raw(instrument, exchanges, start_date, end_date, time_interval,
                                          time_format, sort_direction)
        return processed_df.set_index(index_keys)

    def get_ohlcv_batch_raw(self, exchanges: List[MarketDataVenue], instruments: List[str], start_date: datetime = None,
                            end_date: datetime = None, time_interval: TimeInterval = None,
                            time_format: TimeFormat = None) -> pd.DataFrame:
        all_processed_data = []

        for exchange in exchanges:
            params = {'instrument': ",".join(instrument for instrument in instruments)}
            if start_date is not None:
                params['startDate'] = start_date.isoformat()
            if end_date is not None:
                params['endDate'] = end_date.isoformat()
            if time_interval is not None:
                params['timeInterval'] = time_interval.value
            if time_format is not None:
                params['timeFormat'] = time_format.value

            url = AMBERDATA_FUTURES_REST_BATCH_OHLCV_ENDPOINT + f"exchange/{exchange}/historical"
            instrumentStr = ",".join(instrument for instrument in instruments)
            description = f"FUTURES OHLCV Request for {exchange} for {instrumentStr}"
            lg.info(f"Starting {description} with URL: {url} and params: {params}")

            raw_data = RestService.get_and_process_response_dict(url, params, self._headers(), description)
            lg.info(f"Finished {description}")

            # Check if 'data' key exists
            if not raw_data:
                lg.error("Raw response is empty.")
                raise NoDataReturned("Raw response is empty.")
            if 'data' not in raw_data:
                lg.error(f"Key 'data' not found in the response. Raw response: {json.dumps(raw_data, indent=2)}")
                raise NoDataReturned(
                    f"Key 'data' not found in the response. Raw response: {json.dumps(raw_data, indent=2)}")

            # Process the raw data into a more structured format
            processed_data = []
            for ohlcv in raw_data['data']:
                processed_data.append({
                    'timestamp': ohlcv['timestamp'],
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

    def get_ohlcv_batch(self, exchanges: List[MarketDataVenue], instruments: List[str], start_date: datetime = None,
                        end_date: datetime = None, time_interval: TimeInterval = None, time_format: TimeFormat = None,
                        index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['exchange']
        processed_df = self.get_ohlcv_batch_raw(exchanges, instruments, start_date, end_date, time_interval,
                                                time_format)
        return processed_df.set_index(index_keys)

    def get_open_interest_information_raw(self, exchanges: List[MarketDataVenue] = None, include_inactive: bool = None,
                                          time_format: TimeFormat = None) -> pd.DataFrame:
        params = {}
        if exchanges is not None and len(exchanges) > 0:
            params['exchange'] = ",".join(
                [exchange.value for exchange in exchanges])
        if include_inactive is not None:
            params['includeInactive'] = str(include_inactive).lower()
        if time_format is not None:
            params['timeFormat'] = time_format.value
        url = AMBERDATA_FUTURES_REST_OPEN_INTEREST_ENDPOINT + "information"
        description = "FUTURES Open Interest Information Request"
        lg.info(f"Starting {description}")
        return_df = RestService.get_and_process_response_df(url, params, self._headers(), description)
        lg.info(f"Finished {description}")
        return return_df

    def get_open_interest_information(self, exchanges: List[MarketDataVenue] = None, include_inactive: bool = None,
                                      time_format: TimeFormat = None, index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['exchange']
        return self.get_open_interest_information_raw(exchanges, include_inactive, time_format).set_index(index_keys)

    def get_open_interest_raw(self, instrument: str, exchange: MarketDataVenue, start_date: datetime = None,
                              end_date: datetime = None, time_format: TimeFormat = None,
                              sort_direction: SortDirection = None,
                              batch_period: datetime.timedelta = BatchPeriod.HOUR_1.value,
                              parallel_execution: bool = False) -> pd.DataFrame:
        params = {'exchange': exchange.value}
        if start_date is not None:
            params['startDate'] = start_date.isoformat(timespec='milliseconds')
        if end_date is not None:
            params['endDate'] = end_date.isoformat(timespec='milliseconds')
        if time_format is not None:
            params['timeFormat'] = time_format.value
        if sort_direction is not None:
            params['sortDirection'] = sort_direction.value
        url = AMBERDATA_FUTURES_REST_OPEN_INTEREST_ENDPOINT + f"{instrument}"
        description = "FUTURES Open Interest Request"
        lg.info(f"Starting {description}")

        if parallel_execution:
            if start_date is None or end_date is None:
                raise ValueError("Start and end date must be provided for parallel execution!")
            else:
                return_df = RestService._process_parallel(start_date, end_date, batch_period, self._headers(), url,
                                                          params, description, self._get_max_threads())
                # Check if timestamp or exchangeTimestamp + exchangeTimestampNano is present and sort by it otherwise skip sorting
                if 'timestamp' in return_df.columns:
                    return_df.sort_values('timestamp', inplace=True)
                elif 'exchangeTimestamp' in return_df.columns and 'exchangeTimestampNano' in return_df.columns:
                    return_df.sort_values(['exchangeTimestamp', 'exchangeTimestampNano'], inplace=True)
        else:
            return_df = RestService.get_and_process_response_df(url, params, self._headers(),
                                                                description)
        lg.info(f"Finished {description}")
        return return_df

    def get_open_interest(self, instrument: str, exchange: MarketDataVenue, start_date: datetime = None,
                          end_date: datetime = None, time_format: TimeFormat = None,
                          sort_direction: SortDirection = None, index_keys: List[str] = None,
                          batch_period: datetime.timedelta = BatchPeriod.HOUR_1.value,
                          parallel_execution: bool = False) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['exchange']
        return self.get_open_interest_raw(instrument, exchange, start_date, end_date, time_format,
                                          sort_direction, batch_period, parallel_execution).set_index(index_keys)

    def get_open_interest_batch_raw(self, exchanges: List[MarketDataVenue], instruments: List[str],
                                    start_date: datetime = None,
                                    end_date: datetime = None, time_interval: TimeInterval = None,
                                    time_format: TimeFormat = None) -> pd.DataFrame:
        all_processed_data = []

        for exchange in exchanges:
            params = {'instrument': ",".join(instrument for instrument in instruments)}
            if start_date is not None:
                params['startDate'] = start_date.isoformat()
            if end_date is not None:
                params['endDate'] = end_date.isoformat()
            if time_interval is not None:
                params['timeInterval'] = time_interval.value
            if time_format is not None:
                params['timeFormat'] = time_format.value

            url = AMBERDATA_FUTURES_REST_BATCH_OPEN_INTEREST_ENDPOINT + f"exchange/{exchange}/historical"
            instrumentStr = ",".join(instrument for instrument in instruments)
            description = f"FUTURES Open Interest Batch Request for {exchange} for {instrumentStr}"
            lg.info(f"Starting {description} with URL: {url} and params: {params}")

            raw_data = RestService.get_and_process_response_dict(url, params, self._headers(), description)
            lg.info(f"Finished {description}")

            # Check if 'data' key exists
            if not raw_data:
                lg.error("Raw response is empty.")
                raise NoDataReturned("Raw response is empty.")
            if 'data' not in raw_data:
                lg.error(f"Key 'data' not found in the response. Raw response: {json.dumps(raw_data, indent=2)}")
                raise NoDataReturned(
                    f"Key 'data' not found in the response. Raw response: {json.dumps(raw_data, indent=2)}")

            # Process the raw data into a more structured format
            processed_data = []
            for ohlcv in raw_data['data']:
                processed_data.append({
                    'timestamp': ohlcv['timestamp'],
                    'type': ohlcv['type'],
                    'value': ohlcv['value'],
                    'exchange': exchange.value,
                    'instrument': ohlcv['instrument']
                })

            all_processed_data.extend(processed_data)

        # Convert processed data into DataFrame
        processed_df = pd.DataFrame(all_processed_data)
        return processed_df

    def get_open_interest_batch(self, exchanges: List[MarketDataVenue], instruments: List[str],
                                start_date: datetime = None,
                                end_date: datetime = None, time_interval: TimeInterval = None,
                                time_format: TimeFormat = None,
                                index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['exchange']
        processed_df = self.get_open_interest_batch_raw(exchanges, instruments, start_date, end_date, time_interval,
                                                        time_format)
        return processed_df.set_index(index_keys)

    def get_order_book_information_raw(self, exchanges: List[MarketDataVenue] = None, include_inactive: bool = None,
                                       time_format: TimeFormat = None) -> pd.DataFrame:
        params = {}
        if exchanges is not None and len(exchanges) > 0:
            params['exchange'] = ",".join(exchange.value for exchange in exchanges)
        if include_inactive is not None:
            params['includeInactive'] = str(include_inactive).lower()
        if time_format is not None:
            params['timeFormat'] = time_format.value if isinstance(time_format, TimeFormat) else time_format

        url = AMBERDATA_FUTURES_REST_ORDER_BOOK_SNAPSHOTS_ENDPOINT + "information"
        description = "FUTURES Order Book Information Request"
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
                                                start_date: datetime = None, end_date: datetime = None,
                                                timestamp: datetime = None, time_format: TimeFormat = None,
                                                sort_direction: SortDirection = None) -> pd.DataFrame:
        params = {}
        params['exchange'] = exchange.value
        if start_date is not None:
            params['startDate'] = start_date.isoformat()
        if end_date is not None:
            params['endDate'] = end_date.isoformat()
        if sort_direction is not None:
            params['sortDirection'] = sort_direction
        if timestamp is not None:
            params['timestamp'] = timestamp.isoformat()
        if time_format is not None:
            params['timeFormat'] = time_format.value

        url = AMBERDATA_FUTURES_REST_ORDER_BOOK_SNAPSHOTS_ENDPOINT + f"{instrument}"
        description = f"FUTURES Order Book Snapshots Historical Request for {instrument}"
        lg.info(f"Starting {description}")
        raw_data = RestService.get_and_process_response_dict(url, params, self._headers(), description)
        lg.info(f"Finished {description}")

        # Process the raw data into a more structured format
        processed_data = []
        if 'data' in raw_data:
            for entry in raw_data['data']:
                timestamp = entry.get('timestamp')
                instrument = entry.get('instrument')
                exchange = entry.get('exchange')
                if 'ask' in entry:
                    for ask in entry['ask']:
                        processed_data.append({
                            'timestamp': timestamp,
                            'instrument': instrument,
                            'exchange': exchange,
                            'side': 'ask',
                            'price': ask.get('price'),
                            'volume': ask.get('volume'),
                            'numOrders': ask.get('numOrders')
                        })
                if 'bid' in entry:
                    for bid in entry['bid']:
                        processed_data.append({
                            'timestamp': timestamp,
                            'instrument': instrument,
                            'exchange': exchange,
                            'side': 'bid',
                            'price': bid.get('price'),
                            'volume': bid.get('volume'),
                            'numOrders': bid.get('numOrders')
                        })

        # Convert processed data into DataFrame
        processed_df = pd.DataFrame(processed_data)
        return processed_df

    def get_order_book_snapshots_historical(self, instrument: str, exchange: MarketDataVenue,
                                            start_date: datetime = None,
                                            end_date: datetime = None, timestamp: datetime = None,
                                            time_format: TimeFormat = None, sort_direction: SortDirection = None,
                                            index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['timestamp', 'instrument', 'exchange', 'side']
        processed_df = self.get_order_book_snapshots_historical_raw(instrument, exchange, start_date, end_date,
                                                                    timestamp, time_format, sort_direction)
        return processed_df.set_index(index_keys)

    def get_order_book_events_historical_raw(self, instrument: str, exchange: MarketDataVenue,
                                             start_date: datetime = None,
                                             end_date: datetime = None, time_format: TimeFormat = None,
                                             sort_direction: SortDirection = None) -> pd.DataFrame:
        params = {'exchange': exchange.value}
        if start_date is not None:
            params['startDate'] = start_date.isoformat()
        if end_date is not None:
            params['endDate'] = end_date.isoformat()
        if time_format is not None:
            params['timeFormat'] = time_format.value
        if sort_direction is not None:
            params['sortDirection'] = sort_direction.value

        url = AMBERDATA_FUTURES_REST_ORDER_BOOK_EVENTS_ENDPOINT + f"{instrument}"
        description = f"FUTURES Order Book Events Historical Request for {instrument}"
        lg.info(f"Starting {description}")
        raw_data = RestService.get_and_process_response_dict(url, params, self._headers(), description)
        lg.info(f"Finished {description}")

        # Process the raw data into a more structured format
        processed_data = []
        if 'data' in raw_data:
            for entry in raw_data['data']:
                timestamp = entry.get('exchangeTimestamp')
                instrument = entry.get('instrument')
                exchange = entry.get('exchange')
                asks = entry.get('ask', [])
                bids = entry.get('bid', [])

                for ask in asks:
                    processed_data.append({
                        'timestamp': timestamp,
                        'instrument': instrument,
                        'exchange': exchange,
                        'side': 'ask',
                        'price': ask.get('price'),
                        'volume': ask.get('volume'),
                        'numOrders': ask.get('numOrders')
                    })
                for bid in bids:
                    processed_data.append({
                        'timestamp': timestamp,
                        'instrument': instrument,
                        'exchange': exchange,
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
                                         sort_direction: SortDirection = None,
                                         index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['timestamp', 'instrument', 'exchange', 'side']
        processed_df = self.get_order_book_events_historical_raw(instrument, exchange, start_date, end_date,
                                                                 time_format, sort_direction)
        return processed_df.set_index(index_keys)

    def get_tickers_information_raw(self, exchanges: List[MarketDataVenue] = None, include_inactive: bool = None,
                                    time_format: TimeFormat = None) -> pd.DataFrame:
        params = {}
        if exchanges is not None and len(exchanges) > 0:
            params['exchange'] = ",".join(exchange.value for exchange in exchanges)
        if include_inactive is not None:
            params['includeInactive'] = str(include_inactive).lower()
        if time_format is not None:
            params['timeFormat'] = time_format.value if isinstance(time_format, TimeFormat) else time_format

        url = AMBERDATA_FUTURES_REST_TICKERS_ENDPOINT + "information"
        description = "FUTURES Ticker Information Request"
        lg.info(f"Starting {description}")
        raw_response = RestService.get_and_process_response_dict(url, params, self._headers(), description)
        lg.info(f"Finished {description}")

        # Process raw data into DataFrame
        processed_data = []
        if 'data' in raw_response:
            for item in raw_response['data']:
                processed_data.append(item)

        return pd.DataFrame(processed_data)

    def get_tickers_information(self, exchanges: List[MarketDataVenue] = None, include_inactive: bool = None,
                                time_format: TimeFormat = None, index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['exchange']
        return self.get_tickers_information_raw(exchanges, include_inactive, time_format).set_index(index_keys)

    def get_tickers_raw(self, instrument: str, exchange: MarketDataVenue,
                        start_date: datetime = None, end_date: datetime = None,
                        time_format: TimeFormat = None, sort_direction: SortDirection = None) -> pd.DataFrame:
        params = {
            'exchange': exchange.value,
        }
        if start_date is not None:
            params['startDate'] = start_date.isoformat(timespec='milliseconds')
        if end_date is not None:
            params['endDate'] = end_date.isoformat(timespec='milliseconds')
        if time_format is not None:
            params['timeFormat'] = time_format.value
        if sort_direction is not None:
            params['sortDirection'] = sort_direction.value
        url = AMBERDATA_FUTURES_REST_TICKERS_ENDPOINT + f"{instrument}"
        description = f"FUTURES Historical Ticker Request for {instrument}"
        lg.info(f"Starting {description}")
        return_df = RestService.get_and_process_response_df(url, params, self._headers(), description)
        lg.info(f"Finished {description}")
        return return_df

    def get_tickers(self, instrument: str, exchange: MarketDataVenue = None, start_date: datetime = None,
                    end_date: datetime = None, time_format: TimeFormat = None, sort_direction: SortDirection = None,
                    index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['exchangeTimestamp', 'instrument', 'exchange']
        return self.get_tickers_raw(instrument, exchange, start_date, end_date, time_format, sort_direction).set_index(
            index_keys)

    def get_trades_information_raw(self, exchanges: List[MarketDataVenue] = None, include_inactive: bool = None,
                                   time_format: TimeFormat = None) -> pd.DataFrame:
        params = {}
        if include_inactive is not None:
            params['includeInactive'] = str(include_inactive).lower()
        if time_format is not None:
            params['timeFormat'] = time_format.value
        if exchanges is not None and len(exchanges) > 0:
            params['exchange'] = ",".join([exchange.value for exchange in exchanges])

        url = AMBERDATA_FUTURES_REST_TRADES_ENDPOINT + "information"
        description = "FUTURES Trades Information Request"
        lg.info(f"Starting {description}")
        return_df = RestService.get_and_process_response_df(url, params, self._headers(), description)
        lg.info(f"Finished {description}")
        return return_df

    def get_trades_information(self, exchanges: List[MarketDataVenue] = None, include_inactive: bool = None,
                               time_format: TimeFormat = None,
                               index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['exchange', 'instrument']
        return self.get_trades_information_raw(exchanges, include_inactive, time_format).set_index(index_keys)

    def get_trades_raw(self, instrument: str, exchange: MarketDataVenue, start_date: datetime = None,
                       end_date: datetime = None,
                       time_format: TimeFormat = None, sort_direction: SortDirection = None) -> pd.DataFrame:
        params = {'exchange': exchange.value}
        if start_date is not None:
            params['startDate'] = start_date.isoformat()
        if end_date is not None:
            params['endDate'] = end_date.isoformat()
        if time_format is not None:
            params['timeFormat'] = time_format.value if isinstance(time_format, TimeFormat) else time_format
        if sort_direction is not None:
            params['sortDirection'] = sort_direction.value

        url = AMBERDATA_FUTURES_REST_TRADES_ENDPOINT + f"{instrument}"
        description = "FUTURES Trades Historical Request"
        lg.info(f"Starting {description}")
        raw_data = RestService.get_and_process_response_dict(url, params, self._headers(), description)
        lg.info(f"Finished {description}")

        # Process raw data into DataFrame
        processed_data = []
        if 'data' in raw_data:
            for entry in raw_data['data']:
                processed_data.append({
                    'timestamp': entry.get('exchangeTimestamp'),
                    'timestampNano': entry.get('exchangeTimestampNanoseconds'),
                    'instrument': instrument,
                    'side': "BUY" if entry.get('isBuySide') else "SELL",
                    'price': entry.get('price'),
                    'volume': entry.get('volume'),
                    'tradeId': entry.get('tradeId'),
                    'numOrders': entry.get('numOrders', 'unknown'),
                    'exchange': entry.get('exchange', 'unknown')  # Default to 'unknown' if exchange is missing
                })

        # Convert processed data into DataFrame
        processed_df = pd.DataFrame.from_records(processed_data)
        return processed_df

    def get_trades(self, instrument: str, exchange: MarketDataVenue, start_date: datetime = None,
                   end_date: datetime = None,
                   time_format: TimeFormat = None, sort_direction: SortDirection = None,
                   index_keys: List[str] = None) -> pd.DataFrame:
        if index_keys is None:
            index_keys = ['timestamp', 'instrument', 'exchange']
        return self.get_trades_raw(instrument, exchange, start_date, end_date, time_format, sort_direction).set_index(
            index_keys)

    def get_exchanges_reference(self, exchanges: List[MarketDataVenue] = None,
                                include_inactive: bool = None) -> Dict:
        """
        Fetch futures instrument listings from /markets/futures/exchanges/.

        Returns raw dict with 'data' key containing instrument entries per exchange.

        Args:
            exchanges: Filter to specific exchanges.
            include_inactive: Include delisted/inactive instruments.

        Returns:
            Dict with 'data' list of instrument entries.
        """
        params = {}
        if exchanges is not None and len(exchanges) > 0:
            params['exchange'] = ",".join(exchange.value for exchange in exchanges)
        if include_inactive is not None:
            params['includeInactive'] = str(include_inactive).lower()

        url = AMBERDATA_FUTURES_REST_EXCHANGES_REFERENCE_ENDPOINT
        description = "FUTURES Exchanges Reference Request"
        lg.info(f"Starting {description}")
        return_dict = self.get_and_process_response_dict(url, params, self._headers(), description)
        lg.info(f"Finished {description}")
        return return_dict
