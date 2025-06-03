import json
import multiprocessing
import time
from abc import ABC
from datetime import datetime, timedelta
from enum import Enum
from functools import partial
from typing import Dict, Any, Tuple, List

import boto3
import pandas as pd
import pytz
import requests
from botocore.exceptions import ClientError
from loguru import logger as lg
import os


class SecretManager:
    _secretClient: boto3.client

    def __init__(self, region: str = 'us-east-1'):
        self._secretClient = boto3.client('secretsmanager', region_name=region)

    def get_secret(self, secretName: str):
        try:
            secretResponse = self._secretClient.get_secret_value(SecretId=secretName)
        except ClientError as e:
            # For a list of exceptions thrown, see
            # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
            raise e

        secretString = secretResponse['SecretString']
        return secretString


class ApiKeyGetMode(Enum):
    LOCAL_FILE = "local_file"
    AWS_SECRET_MANAGER = "aws_secret_manager"


class NoDataReturned(Exception):
    def __init__(self, message="No data returned from the API"):
        self.message = message
        super().__init__(self.message)


class RestService(ABC):
    _key_get_mode: ApiKeyGetMode
    _local_keys_path: str
    _aws_secret_name: str
    _aws_secret_key: str
    _max_threads: int

    def __init__(self, api_key_get_mode: ApiKeyGetMode, key_get_params: Dict, max_threads: int = 32):
        self._key_get_mode = api_key_get_mode
        if api_key_get_mode == ApiKeyGetMode.LOCAL_FILE:
            self._local_keys_path = key_get_params['local_key_path']
            self._aws_secret_name = None
            self._aws_secret_key = None
        elif api_key_get_mode == ApiKeyGetMode.AWS_SECRET_MANAGER:
            self._local_keys_path = None
            self._aws_secret_name = key_get_params['aws_secret_name']
            self._aws_secret_key = key_get_params['aws_secret_key']
        else:
            raise ValueError(f"Invalid API Key Get Mode: {api_key_get_mode}")
        self._max_threads = max_threads

    def _headers(self) -> Dict[str, str]:
        if self._key_get_mode == ApiKeyGetMode.LOCAL_FILE:
            amberdata_api_key = get_amberdata_api_key_from_local_file(self._local_keys_path)
        elif self._key_get_mode == ApiKeyGetMode.AWS_SECRET_MANAGER:
            amberdata_api_key = get_amberdata_api_key_from_aws_secret_manager(self._aws_secret_name, self._aws_secret_key)
        else:
            raise ValueError(f"Invalid API Key Get Mode: {self._key_get_mode}")
        return {'accept': 'application/json', 'x-api-key': f'{amberdata_api_key}'}

    def _get_max_threads(self) -> int:
        return self._max_threads

    @staticmethod
    def _get_date_ranges_for_parallel(start_date: datetime, end_date: datetime, batch_period: timedelta) -> List[Tuple[datetime, datetime]]:
        date_ranges = []
        batch_start_date = start_date
        batch_end_date = min(batch_start_date + batch_period, end_date)
        while batch_start_date < end_date:
            date_ranges.append((batch_start_date, batch_end_date))
            batch_start_date = batch_end_date
            batch_end_date = min(batch_start_date + batch_period, end_date)

        return date_ranges

    @staticmethod
    def _validate_response(response: dict, request_description: str, url: str, params: Dict) -> bool:
        if 'status' not in response:
            lg.error(f"Error on request: {request_description}, url: {url}, params: {params}")
            lg.error(f"No 'status' found in response: {response}")
        elif 'title' not in response:
            lg.error(f"Error on request: {request_description}, url: {url}, params: {params}")
            lg.error(f"No 'title' found in response: {response}")
        elif 'description' not in response:
            lg.error(f"Error on request: {request_description}, url: {url}, params: {params}")
            lg.error(f"No 'description' found in response: {response}")
        else:
            status = response['status']
            title = response['title']
            description = response['description']
            if status != 200 or title != "OK" or description != "Successful request":
                error = "N/A"
                if 'error' in response:
                    error = response['error']
                message = response['message']
                lg.error(f"Error on request: {request_description}, url: {url}, params: {params}")
                lg.error(
                    f"{request_description} failed.\nStatus:{status}, Title:{title},"
                    f" Desc:{description}, Error:{error}, Message:{message}")
                return False
            else:
                return True
        return False

    @classmethod
    def _get_response(cls, url: str, params: Dict[str, str], headers: Dict[str, str], description: str,
                      retry_count: int = 5, sleep_duration: float = 10.0) -> [bool, object]:
        while retry_count > 0:
            lg.debug(f"Executing request with url:{url}, params={params}, retryCount:{retry_count}")
            with requests.session() as session:
                try:
                    if "?" in url:
                        response_raw = session.get(url, headers=headers)
                    else:
                        response_raw = session.get(url, headers=headers, params=params)
                    response_raw.raise_for_status()
                    response_data = json.loads(response_raw.text)
                    clean_response = cls._validate_response(response_data, description, url, params)
                    if not clean_response:
                        retry_count -= 1
                        time.sleep(sleep_duration)
                    else:
                        return clean_response, response_data
                except requests.exceptions.ContentDecodingError as e:
                    lg.error(f"Decoding error: {e}")
                    retry_count -= 1
                    time.sleep(sleep_duration)
                except requests.exceptions.RequestException as e:
                    lg.error(f"Request failed: {e}")
                    retry_count -= 1
                    time.sleep(sleep_duration)
        return False, None

    @classmethod
    def _process_response(cls, response: dict) -> Dict[str, Any]:
        # Process payload with metadata
        return_dict = {}
        if (type(response['payload']) is dict) and ('metadata' in response['payload'].keys()):
            return_dict['metadata'] = response['payload']['metadata']
            return_dict['data'] = response['payload']['data']
            return return_dict
        else:
            return_dict['data'] = response['payload']
        return return_dict

    @staticmethod
    def _detect_key_to_list_structure(sub_payload, metadata) -> bool:
        """
        Auto-detect if this is a key-to-list structure where:
        - sub_payload is a dict with string keys (e.g., hash addresses, IDs)
        - each key maps to a list of records (lists)
        - metadata contains 'columns' definition
        """
        if not isinstance(sub_payload, dict) or len(sub_payload) == 0:
            return False

        if 'columns' not in metadata:
            return False

        # Check if all keys are strings and all values are lists
        for key, value in sub_payload.items():
            if not isinstance(key, str) or not isinstance(value, list):
                return False

            # Check if this key has records and if first record is a list (multiple values)
            if len(value) > 0:
                first_record = value[0]
                if isinstance(first_record, list) and len(first_record) == len(metadata['columns']):
                    continue
                else:
                    return False

        return True

    @staticmethod
    def _process_key_to_list_structure(sub_payload, metadata) -> pd.DataFrame:
        """
        Process key-to-list structure into DataFrame with keys as index.

        Structure:
        {
          "key1": [[record1_values], [record2_values], ...],
          "key2": [[record1_values], [record2_values], ...],
          ...
        }

        Result: DataFrame with keys as index, multiple rows per key
        """
        columns = metadata['columns']
        processed_data = []

        for key_identifier, records in sub_payload.items():
            for record in records:
                if len(record) == len(columns):
                    # Create a row with key as index identifier
                    row_data = dict(zip(columns, record))
                    row_data['_key_index'] = key_identifier  # Temporary column for index
                    processed_data.append(row_data)

        if not processed_data:
            return pd.DataFrame()

        # Create DataFrame
        _df = pd.DataFrame(processed_data)

        # Set key as index and remove the temporary column
        _df.set_index('_key_index', inplace=True)
        _df.index.name = None  # Remove index name for cleaner appearance

        # Add any additional metadata as columns (excluding 'columns')
        for key in metadata.keys():
            if key != "columns":
                _df[key] = str(metadata[key])

        return _df

    @staticmethod
    def _detect_nested_dict_structure(sub_payload, metadata, max_levels: int = 5) -> tuple[bool, int]:
        """
        Auto-detect nested dictionary structure and return actual depth.

        Detects patterns like:
        - 2-level: category → items → {properties}
        - 3-level: exchange → pools → {properties}
        - 4-level: country → state → city → {properties}

        Args:
            sub_payload: The data payload to analyze
            metadata: Metadata dict (excluded from nesting analysis)
            max_levels: Maximum allowed nesting depth

        Returns:
            tuple: (is_nested_dict_structure, actual_depth)
        """
        if not isinstance(sub_payload, dict) or len(sub_payload) == 0:
            return False, 0

        # Exclude metadata from structure analysis
        data_keys = [k for k in sub_payload.keys() if k != 'metadata']
        if len(data_keys) == 0:
            return False, 0

        def _get_depth_to_primitives(obj, current_depth=0):
            """Recursively find depth until we hit primitive values"""
            if not isinstance(obj, dict):
                return current_depth

            if len(obj) == 0:
                return current_depth

            # Check first item to determine depth
            first_key = next(iter(obj.keys()))
            first_value = obj[first_key]

            if isinstance(first_value, dict):
                return _get_depth_to_primitives(first_value, current_depth + 1)
            else:
                # Hit primitive values
                return current_depth + 1

        # Detect depth from first data key
        first_data_key = data_keys[0]
        detected_depth = _get_depth_to_primitives(sub_payload[first_data_key])

        # Validate depth is within limits
        if detected_depth < 2 or detected_depth > max_levels:
            return False, 0

        # Validate consistency across all data keys
        for key in data_keys:
            key_depth = _get_depth_to_primitives(sub_payload[key])
            if key_depth != detected_depth:
                return False, 0

            # Validate structure consistency at each level
            def _validate_structure_consistency(obj, target_depth, current_depth=0):
                if current_depth == target_depth - 1:
                    # At the deepest level before primitives, ensure all values are dicts with primitives
                    if not isinstance(obj, dict):
                        return False
                    for sub_key, sub_value in obj.items():
                        if isinstance(sub_value, dict):
                            # This dict should contain only primitives
                            for prop_key, prop_value in sub_value.items():
                                if isinstance(prop_value, (dict, list)):
                                    return False
                        else:
                            return False
                    return True
                else:
                    # Not at deepest level yet, ensure all values are dicts
                    if not isinstance(obj, dict):
                        return False
                    for sub_key, sub_value in obj.items():
                        if not isinstance(sub_value, dict):
                            return False
                        if not _validate_structure_consistency(sub_value, target_depth, current_depth + 1):
                            return False
                    return True

            if not _validate_structure_consistency(sub_payload[key], detected_depth):
                return False, 0

        return True, detected_depth

    @staticmethod
    def _process_nested_dict_structure(sub_payload, metadata, actual_depth: int) -> pd.DataFrame:
        """
        Process nested dictionary structure into DataFrame with multi-level index.

        Args:
            sub_payload: The nested dictionary data
            metadata: Metadata dict
            actual_depth: The actual depth of nesting detected

        Returns:
            DataFrame with multi-level index from all levels except deepest,
            and columns from deepest level properties
        """
        processed_data = []

        # Exclude metadata from processing
        data_keys = [k for k in sub_payload.keys() if k != 'metadata']

        def _flatten_nested_dict(obj, index_path=[], current_depth=0):
            """Recursively flatten nested dict structure"""
            if current_depth == actual_depth - 1:
                # At the level containing the final objects
                for key, properties in obj.items():
                    if isinstance(properties, dict):
                        # Create full index path
                        full_index = index_path + [key]

                        # Create row with index information and properties
                        row_data = properties.copy()

                        # Add index levels as temporary columns for later multi-index creation
                        for i, index_value in enumerate(full_index):
                            row_data[f'_index_level_{i}'] = index_value

                        processed_data.append(row_data)
            else:
                # Continue traversing deeper
                for key, nested_obj in obj.items():
                    if isinstance(nested_obj, dict):
                        _flatten_nested_dict(nested_obj, index_path + [key], current_depth + 1)

        # Process all data keys
        for data_key in data_keys:
            _flatten_nested_dict(sub_payload[data_key], [data_key])

        if not processed_data:
            return pd.DataFrame()

        # Create DataFrame
        _df = pd.DataFrame(processed_data)

        # Extract index columns and create multi-level index
        index_columns = [col for col in _df.columns if col.startswith('_index_level_')]
        index_columns.sort()  # Ensure proper order

        if index_columns:
            # Extract index values
            index_values = []
            for _, row in _df.iterrows():
                index_tuple = tuple(row[col] for col in index_columns)
                index_values.append(index_tuple)

            # Create multi-level index
            if len(index_columns) > 1:
                _df.index = pd.MultiIndex.from_tuples(index_values)
            else:
                _df.index = [idx[0] for idx in index_values]

            # Remove temporary index columns
            _df.drop(columns=index_columns, inplace=True)

        # Add any additional metadata as columns (excluding those used for structure)
        for key in metadata.keys():
            if key not in ["columns", "next"]:  # Skip structural metadata
                _df[key] = str(metadata[key])

        return _df

    @staticmethod
    def _process_payload_df(payload) -> pd.DataFrame:
        if 'metadata' in payload.keys():
            # We are processing a historical data payload, handle metadata
            # Separate the actual data first
            sub_payload = payload['data']
            # If no data, return empty data frame
            if len(sub_payload) == 0:
                return pd.DataFrame()

            # Check for nested dictionary structure first
            is_nested, actual_depth = RestService._detect_nested_dict_structure(sub_payload, payload['metadata'])
            if is_nested:
                _df = RestService._process_nested_dict_structure(sub_payload, payload['metadata'], actual_depth)

            elif RestService._detect_key_to_list_structure(sub_payload, payload['metadata']):
                _df = RestService._process_key_to_list_structure(sub_payload, payload['metadata'])

            elif 'columns' in payload['metadata']:
                columns = payload['metadata']['columns']
                _df = pd.DataFrame.from_dict(sub_payload)
                _df.columns = columns

                for key in payload['metadata'].keys():
                    # Columns would have been handled earlier
                    if key == "columns":
                        continue
                    _df[key] = str(payload['metadata'][key])  # casting to str since metadata is not always a string
            else:
                _df = pd.DataFrame.from_dict(sub_payload)

                for key in payload['metadata'].keys():
                    # Columns would have been handled earlier
                    if key == "columns":
                        continue
                    _df[key] = str(payload['metadata'][key])  # casting to str since metadata is not always a string
        else:
            if type(payload['data']) == dict:
                _df = pd.DataFrame.from_records(payload['data'], index=[0])
            else:
                _df = pd.DataFrame.from_dict(payload['data'])

        tz_local = pytz.timezone('US/Eastern')
        # Add UTC & EST Time Columns
        if not _df.empty and 'timestamp' in _df.columns:
            try:
                _df['timeUTC'] = pd.to_datetime(pd.to_numeric(_df["timestamp"]), unit="ms", utc=True)
                _df['timeEST'] = _df['timeUTC'].dt.tz_convert(tz_local)
            except ValueError as e:
                lg.error(f"Error converting timestamp to datetime, not numeric: {e}")
                _df['timeUTC'] = pd.to_datetime(_df["timestamp"], utc=True)
                _df['timeEST'] = _df['timeUTC'].dt.tz_convert(tz_local)
            except Exception as e:
                lg.error(f"Error converting timestamp to datetime: {e}")
                lg.error(f"Please contact administrators from github.com")
        elif not _df.empty and 'exchangeTimestamp' in _df.columns:
            _df['timeUTC'] = pd.to_datetime(pd.to_numeric(_df["exchangeTimestamp"]), unit="ms", utc=True)
            _df['timeEST'] = _df['timeUTC'].dt.tz_convert(tz_local)
        return _df

    @staticmethod
    def _process_payload_dict(payload) -> Dict:
        return_dict = {}
        sub_payload = payload['data']
        if len(sub_payload) == 0:
            return return_dict
        elif 'metadata' in payload.keys():
            for key in payload['metadata']:
                return_dict[key] = payload['metadata'][key]
        return_dict['data'] = sub_payload
        return return_dict

    @staticmethod
    def _process_batch(date_tuple: Tuple[datetime, datetime],
                       headers: Dict[str, str],
                       url: str,
                       params: Dict,
                       description: str):
        params['startDate'] = date_tuple[0].isoformat(timespec='milliseconds')
        params['endDate'] = date_tuple[1].isoformat(timespec='milliseconds')
        lg.info(f"Starting request for Start:{params['startDate']} to End: {params['endDate']}")
        _df = RestService.get_and_process_response_df(url, params, headers, description)
        lg.info(f"Finished request for Start:{params['startDate']} to End: {params['endDate']}")
        if not _df.empty:
            _df.reset_index(inplace=True)
            # drop the index column
            if 'index' in _df.columns:
                _df.drop(columns=['index'], inplace=True)
        return _df

    @staticmethod
    def _process_parallel(start_date: datetime, end_date: datetime, batch_period: timedelta, headers: Dict[str, str],
                          url: str, params: Dict, description: str, max_threads: int):
        # Use 1 less CPU Than available for safety
        cpu_count = min(max_threads, multiprocessing.cpu_count())
        lg.debug(f"Will use {cpu_count} threads")
        date_ranges = RestService._get_date_ranges_for_parallel(start_date, end_date, batch_period)
        partial_process_batch = partial(RestService._process_batch,
                                        headers=headers, url=url,
                                        params=params, description=description)
        p = multiprocessing.Pool(cpu_count)
        lg.debug("Starting multi threaded requests...")
        result_dfs = p.map(partial_process_batch, date_ranges)
        lg.debug("Finished multi threaded requests...")
        result_df = pd.concat([pd.DataFrame()] + result_dfs, ignore_index=True)
        if result_df.empty:
            lg.warning("No data returned from any of the parallel requests.")
        return result_df

    @classmethod
    def get_and_process_response_df(cls, url: str, params: Dict[str, Any], headers: Dict[str, str], description: str,
                                    retryCount: int = 5) -> pd.DataFrame:
        more_data_to_fetch = True
        next_url = url
        paged_data = pd.DataFrame()
        while more_data_to_fetch:
            success, res = cls._get_response(next_url, params, headers, description, retryCount)
            if success:
                raw_data = cls._process_payload_df(cls._process_response(res))
                # If 'next' is in the raw data, and it contains a URL, it implies the data is paginated, run in a loop until all data is received.
                if 'next' in raw_data.columns and raw_data['next'].unique()[0] not in [None, 'None']:
                    next_url = raw_data['next'].unique()[0]
                    lg.debug(f"Fetching next page from: {next_url}")
                else:
                    more_data_to_fetch = False
                if not raw_data.empty:
                    paged_data = pd.concat([paged_data, raw_data], ignore_index=True)
                else:
                    continue
            else:
                raise ValueError(
                    f"Failed to fetch data for request:{description}, url:{url}, params:{params} after {retryCount} retries.")

        if 'next' in paged_data.columns:
            paged_data.drop(columns=['next'], inplace=True)
        return paged_data

    @classmethod
    def get_and_process_response_dict(cls, url: str, params: Dict[str, str], headers: Dict[str, str], description: str,
                                      retry_count: int = 5) -> Dict:
        more_data_to_fetch = True
        next_url = url
        paged_data = []
        while more_data_to_fetch:
            success, res = cls._get_response(next_url, params, headers, description, retry_count)
            if success:
                raw_data = cls._process_payload_dict(cls._process_response(res))
                # If 'next' is in the raw data, and it contains a URL, it implies the data is paginated, run in a loop until all data is received.
                if 'next' in raw_data.keys() and raw_data['next'] is not None:
                    next_url = raw_data['next']
                    lg.debug(f"Fetching next page from: {next_url}")
                else:
                    more_data_to_fetch = False
                if len(raw_data) > 0 and 'data' in raw_data.keys():
                    paged_data.append(raw_data['data'])
                else:
                    continue
            else:
                raise ValueError(
                    f"Failed to fetch data for request:{description}, url:{url}, params:{params} after {retry_count} retries.")

        # paged_data contains paginated data, we need to merge them properly but:
        # each page could be a list, at which point we'd simply do an append OR
        # each page could be a dict, at which point we need to merge each key in the dict
        ret_data = {}
        for page_data in paged_data:
            if type(page_data) == list:
                if 'data' not in ret_data.keys():
                    ret_data['data'] = page_data
                else:
                    ret_data['data'] = ret_data['data'] + page_data
            elif type(page_data) == dict:
                if 'data' not in ret_data.keys():
                    ret_data['data'] = {}
                for key in page_data.keys():
                    if key not in ret_data['data'].keys():
                        ret_data['data'][key] = page_data[key]
                    else:
                        ret_data['data'][key].update(page_data[key])
            else:
                raise Exception("Not implemented")
        return ret_data


def get_amberdata_api_key_from_local_file(file_path: str) -> str:
    try:
        with open(file_path, 'r') as file:
            keys = json.load(file)
            return keys.get('amberdata_api_key')
    except FileNotFoundError:
        full_path = os.path.abspath(file_path)
        raise FileNotFoundError(f"The file at {full_path} is missing.")
    except KeyError:
        raise KeyError("The 'amberdata_api_key' key is missing in the file.")
    except json.JSONDecodeError:
        raise ValueError("The file is not valid JSON.")


def get_amberdata_api_key_from_aws_secret_manager(secret_name: str, secret_key: str) -> str:
    sm = SecretManager()
    secret_string = sm.get_secret(secret_name)
    secret_dict = eval(secret_string)
    return secret_dict[secret_key]