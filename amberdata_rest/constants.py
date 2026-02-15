from datetime import timedelta
from enum import Enum

# REST API Endpoints
# Spot End Points
AMBERDATA_SPOT_REST_OHLCV_ENDPOINT = "https://api.amberdata.com/markets/spot/ohlcv/"
AMBERDATA_SPOT_REST_LEGACY_OHLCV_ENDPOINT = "https://api.amberdata.com/market/spot/ohlcv/"
AMBERDATA_SPOT_REST_TRADES_ENDPOINT = "https://api.amberdata.com/markets/spot/trades/"
AMBERDATA_SPOT_REST_PRICES_ENDPOINT = "https://api.amberdata.com/market/spot/prices/"
AMBERDATA_SPOT_REST_EXCHANGES_ENDPOINT = "https://api.amberdata.com/markets/spot/exchanges/information/"
AMBERDATA_SPOT_REST_PAIRS_ENDPOINT = "https://api.amberdata.com/market/spot/prices/pairs/information/"
AMBERDATA_SPOT_REST_EXCHANGES_REFERENCE_ENDPOINT = "https://api.amberdata.com/markets/spot/exchanges/reference/"
AMBERDATA_SPOT_REST_REFERENCE_RATES_ENDPOINT = "https://api.amberdata.com/markets/spot/reference-rates/"
AMBERDATA_SPOT_REST_TICKERS_ENDPOINT = "https://api.amberdata.com/markets/spot/tickers/"
AMBERDATA_SPOT_REST_TWAP_ENDPOINT = "https://api.amberdata.com/market/spot/twap/"
AMBERDATA_SPOT_REST_ORDER_BOOK_EVENTS_ENDPOINT = "https://api.amberdata.com/markets/spot/order-book-events/"
AMBERDATA_SPOT_REST_ORDER_BOOK_SNAPSHOTS_ENDPOINT = "https://api.amberdata.com/markets/spot/order-book-snapshots/"
AMBERDATA_SPOT_REST_VWAP_ENDPOINT = "https://api.amberdata.com/market/spot/vwap/"

# Futures End Points
AMBERDATA_FUTURES_REST_EXCHANGES_REFERENCE_ENDPOINT = "https://api.amberdata.com/markets/futures/exchanges/reference"
AMBERDATA_FUTURES_REST_EXCHANGES_INFORMATION_ENDPOINT = "https://api.amberdata.com/markets/futures/exchanges/information"
AMBERDATA_FUTURES_REST_FUNDING_RATES_ENDPOINT = "https://api.amberdata.com/markets/futures/funding-rates/"
AMBERDATA_FUTURES_REST_BATCH_FUNDING_RATES_ENDPOINT = "https://api.amberdata.com/market/futures/funding-rates/"
AMBERDATA_FUTURES_REST_INSURANCE_FUNDS_ENDPOINT = "https://api.amberdata.com/markets/futures/insurance-fund/"
AMBERDATA_FUTURES_REST_LIQUIDATIONS_ENDPOINT = "https://api.amberdata.com/markets/futures/liquidations/"
AMBERDATA_FUTURES_REST_LONG_SHORT_RATIO_ENDPOINT = "https://api.amberdata.com/markets/futures/long-short-ratio/"
AMBERDATA_FUTURES_REST_OHLCV_ENDPOINT = "https://api.amberdata.com/markets/futures/ohlcv/"
AMBERDATA_FUTURES_REST_BATCH_OHLCV_ENDPOINT = "https://api.amberdata.com/market/futures/ohlcv/"
AMBERDATA_FUTURES_REST_OPEN_INTEREST_ENDPOINT = "https://api.amberdata.com/markets/futures/open-interest/"
AMBERDATA_FUTURES_REST_BATCH_OPEN_INTEREST_ENDPOINT = "https://api.amberdata.com/market/futures/open-interest/"
AMBERDATA_FUTURES_REST_ORDER_BOOK_SNAPSHOTS_ENDPOINT = "https://api.amberdata.com/markets/futures/order-book-snapshots/"
AMBERDATA_FUTURES_REST_ORDER_BOOK_EVENTS_ENDPOINT = "https://api.amberdata.com/markets/futures/order-book-events/"
AMBERDATA_FUTURES_REST_TICKERS_ENDPOINT = "https://api.amberdata.com/markets/futures/tickers/"
AMBERDATA_FUTURES_REST_TRADES_ENDPOINT = "https://api.amberdata.com/markets/futures/trades/"

# Swaps End Points
AMBERDATA_SWAPS_REST_BATCH_FUNDING_RATES_ENDPOINT = "https://api.amberdata.com/market/swaps/funding-rates/"
AMBERDATA_SWAPS_REST_BATCH_OHLCV_ENDPOINT = "https://api.amberdata.com/market/swaps/ohlcv/"
AMBERDATA_SWAPS_REST_BATCH_OPEN_INTEREST_ENDPOINT = "https://api.amberdata.com/market/swaps/open-interest/"



# 1 - DEX Trades Endpoints
AMBERDATA_DEFI_REST_DEX_TRADES_HISTORICAL_ENDPOINT = "https://api.amberdata.com/defi/dex/trades"
AMBERDATA_DEFI_REST_DEX_PROTOCOLS_INFORMATION_ENDPOINT = "https://api.amberdata.com/defi/dex/information"

# 2 - OHLCV Endpoints
AMBERDATA_DEFI_REST_OHLCV_INFORMATION_ENDPOINT = "https://api.amberdata.com/defi/dex/ohlcv/information"
AMBERDATA_DEFI_REST_OHLCV_LATEST_ENDPOINT = "https://api.amberdata.com/market/defi/ohlcv/{pool}/latest"
AMBERDATA_DEFI_REST_OHLCV_HISTORICAL_ENDPOINT = "https://api.amberdata.com/market/defi/ohlcv/{pool}/historical"

# 3 DEX LIQUIDITY ENDPOINTS
AMBERDATA_DEFI_REST_LIQUIDITY_INFORMATION_ENDPOINT = "https://api.amberdata.com/market/defi/liquidity/information"
AMBERDATA_DEFI_REST_LIQUIDITY_LATEST_ENDPOINT = "https://api.amberdata.com/market/defi/liquidity/{pool}/latest"
AMBERDATA_DEFI_REST_LIQUIDITY_HISTORICAL_ENDPOINT = "https://api.amberdata.com/market/defi/liquidity/{pool}/historical"
AMBERDATA_DEFI_REST_LIQUIDITY_SNAPSHOTS_ENDPOINT = "https://api.amberdata.com/market/defi/liquidity/{poolAddress}/snapshots"
AMBERDATA_DEFI_REST_UNISWAP_V3_LIQUIDITY_DISTRIBUTION_ENDPOINT = "https://api.amberdata.com/defi/dex/uniswapv3/pools/{poolAddress}/liquidity-distribution"

# 4 - LIQUIDITY PROVIDERS
AMBERDATA_DEFI_REST_DEX_LIQUIDITY_POSITIONS_PAIRS_LATEST_ENDPOINT = "https://api.amberdata.com/market/defi/liquidity-positions/pairs/{pair}/latest"
AMBERDATA_DEFI_REST_DEX_LIQUIDITY_POSITIONS_PROVIDERS_LATEST_ENDPOINT = "https://api.amberdata.com/market/defi/liquidity-positions/providers/{address}/latest"
AMBERDATA_DEFI_REST_DEX_LIQUIDITY_PROVIDER_EVENTS_ENDPOINT = "https://api.amberdata.com/market/defi/liquidity/providers/{providerAddress}/events"

# 5 - DEFI METRICS
AMBERDATA_DEFI_REST_METRICS_EXCHANGES_LATEST_ENDPOINT = "https://api.amberdata.com/market/defi/metrics/exchanges/{exchange}/latest"
AMBERDATA_DEFI_REST_METRICS_EXCHANGES_HISTORICAL_ENDPOINT = "https://api.amberdata.com/market/defi/metrics/exchanges/{exchange}/historical"
AMBERDATA_DEFI_REST_METRICS_ASSETS_LATEST_ENDPOINT = "https://api.amberdata.com/market/defi/metrics/exchanges/{exchange}/assets/{asset}/latest"
AMBERDATA_DEFI_REST_METRICS_ASSETS_HISTORICAL_ENDPOINT = "https://api.amberdata.com/market/defi/metrics/exchanges/{exchange}/assets/{asset}/historical"
AMBERDATA_DEFI_REST_METRICS_PAIRS_LATEST_ENDPOINT = "https://api.amberdata.com/market/defi/metrics/exchanges/{exchange}/pairs/{pair}/latest"
AMBERDATA_DEFI_REST_METRICS_PAIRS_HISTORICAL_ENDPOINT = "https://api.amberdata.com/market/defi/metrics/exchanges/{exchange}/pairs/{pair}/historical"

# 6 - Price/TWAP/VWAP Endpoints
AMBERDATA_DEFI_REST_ASSETS_INFORMATION_ENDPOINT = "https://api.amberdata.com/market/defi/prices/asset/information/"
AMBERDATA_DEFI_REST_ASSET_LATEST_ENDPOINT = "https://api.amberdata.com/market/defi/prices/asset/{asset}/latest"
AMBERDATA_DEFI_REST_ASSET_HISTORICAL_ENDPOINT = "https://api.amberdata.com/market/defi/prices/asset/{asset}/historical"
AMBERDATA_DEFI_REST_PAIRS_INFORMATION_ENDPOINT = "https://api.amberdata.com/defi/prices/pairs/information"
AMBERDATA_DEFI_REST_PAIRS_LATEST_ENDPOINT = "https://api.amberdata.com/market/defi/prices/pairs/bases/{base}/quotes/{quote}/latest"
AMBERDATA_DEFI_REST_PAIRS_HISTORICAL_ENDPOINT = "https://api.amberdata.com/market/defi/prices/pairs/bases/{base}/quotes/{quote}/historical"
AMBERDATA_DEFI_REST_TWAP_ASSETS_INFORMATION_ENDPOINT = "https://api.amberdata.com/market/defi/twap/asset/information"
AMBERDATA_DEFI_REST_TWAP_ASSET_LATEST_ENDPOINT = "https://api.amberdata.com/market/defi/twap/asset/{asset}/latest"
AMBERDATA_DEFI_REST_TWAP_ASSET_HISTORICAL_ENDPOINT = "https://api.amberdata.com/market/defi/twap/asset/{asset}/historical"
AMBERDATA_DEFI_REST_TWAP_PAIRS_INFORMATION_ENDPOINT = "https://api.amberdata.com/market/defi/twap/pairs/information"
AMBERDATA_DEFI_REST_TWAP_PAIRS_LATEST_ENDPOINT = "https://api.amberdata.com/market/defi/twap/pairs/bases/{base}/quotes/{quote}/latest"
AMBERDATA_DEFI_REST_TWAP_PAIRS_HISTORICAL_ENDPOINT = "https://api.amberdata.com/market/defi/twap/pairs/bases/{base}/quotes/{quote}/historical"
AMBERDATA_DEFI_REST_VWAP_ASSETS_INFORMATION_ENDPOINT = "https://api.amberdata.com/market/defi/vwap/asset/information"
AMBERDATA_DEFI_REST_VWAP_ASSET_LATEST_ENDPOINT = "https://api.amberdata.com/market/defi/vwap/asset/{asset}/latest"
AMBERDATA_DEFI_REST_VWAP_ASSET_HISTORICAL_ENDPOINT = "https://api.amberdata.com/market/defi/vwap/asset/{asset}/historical"
AMBERDATA_DEFI_REST_VWAP_PAIRS_INFORMATION_ENDPOINT = "https://api.amberdata.com/market/defi/vwap/pairs/information"
AMBERDATA_DEFI_REST_VWAP_PAIRS_LATEST_ENDPOINT = "https://api.amberdata.com/market/defi/vwap/pairs/bases/{base}/quotes/{quote}/latest"
AMBERDATA_DEFI_REST_VWAP_PAIRS_HISTORICAL_ENDPOINT = "https://api.amberdata.com/market/defi/vwap/pairs/bases/{base}/quotes/{quote}/historical"


### 7 - DEX ALL TRANSACTIONS ###
AMBERDATA_DEFI_REST_DEX_PROTOCOL_LENS_ENDPOINT = "https://api.amberdata.com/defi/dex/{protocolId}/protocol"
AMBERDATA_DEFI_REST_DEX_POOL_LENS_ENDPOINT = "https://api.amberdata.com/defi/dex/{protocolId}/pools/{poolAddress}"
AMBERDATA_DEFI_REST_DEX_WALLET_LENS_ENDPOINT = "https://api.amberdata.com/defi/dex/{protocolId}/wallets/{walletAddress}"

# 8 - PORTFOLIO & RETURNS #
AMBERDATA_DEFI_REST_PROVIDER_RETURN_SINCE_INCEPTION_ENDPOINT = "https://api.amberdata.com/market/defi/liquidity/providers/daily-return/{liquidityPoolAddress}"
AMBERDATA_DEFI_REST_PROVIDER_HISTORICAL_RETURN_ENDPOINT = "https://api.amberdata.com/market/defi/liquidity/providers/return/{liquidityPoolAddress}"
AMBERDATA_DEFI_REST_POOL_TOTAL_RETURN_ENDPOINT = "https://api.amberdata.com/market/defi/liquidity/pool/daily-return/{address}"
AMBERDATA_DEFI_REST_WALLET_POSITIONS_ENDPOINT = "https://api.amberdata.com/defi/lending/{protocolId}/wallets/{address}/portfolio"
AMBERDATA_DEFI_REST_PROFIT_LOSS_ENDPOINT = "https://api.amberdata.com/defi/lending/wallets/{walletAddress}/returns"
AMBERDATA_DEFI_REST_IMPERMANENT_LOSS_ENDPOINT = "https://api.amberdata.com/defi/dex/wallets/{walletAddress}/returns"


# 9 - Lending Endpoints
AMBERDATA_DEFI_REST_LENDING_PROTOCOL_METRICS_ENDPOINT = "https://api.amberdata.com/defi/lending/{protocolId}/metrics/summary"
AMBERDATA_DEFI_REST_LENDING_ASSET_METRICS_ENDPOINT = "https://api.amberdata.com/defi/lending/{protocolId}/assets/{assetId}/metrics/summary"

### 10 - LENDING ALL TRANSACTIONS ###
AMBERDATA_DEFI_REST_LENDING_PROTOCOL_LENS_ENDPOINT = "https://api.amberdata.com/defi/lending/{protocolId}/protocol"
AMBERDATA_DEFI_REST_LENDING_ASSET_LENS_ENDPOINT = "https://api.amberdata.com/defi/lending/{protocolId}/assets/{asset}"
AMBERDATA_DEFI_REST_LENDING_WALLET_LENS_ENDPOINT = "https://api.amberdata.com/defi/lending/{protocolId}/wallets/{walletAddress}"
AMBERDATA_DEFI_REST_LENDING_GOVERNANCE_LENS_ENDPOINT = "https://api.amberdata.com/defi/lending/{protocolId}/governance"

# 11 - LENDING STABLECOINS AGGREGATE INSIGHTS #
AMBERDATA_DEFI_REST_LENDING_STABLECOINS_AGGREGATE_INSIGHTS_ENDPOINT = "https://api.amberdata.com/defi/stablecoins/{assetSymbol}/lending/metrics/summary"

# 12 INFORMATION - LENDING PROTOCOLS #
AMBERDATA_DEFI_REST_LENDING_PROTOCOLS_INFORMATION_ENDPOINT = "https://api.amberdata.com/defi/lending/protocols/information"

# 13 - INFORMATION - ASSETS IN LENDING PROTOCOLS #
AMBERDATA_DEFI_REST_LENDING_ASSETS_INFORMATION_ENDPOINT = "https://api.amberdata.com/defi/lending/assets/information"

# 14 - INFORMATION - DEX PROTOCOLS #
AMBERDATA_DEFI_REST_DEX_EXCHANGES_ENDPOINT = "https://api.amberdata.com/market/defi/dex/exchanges"

# 15 - INFORMATION - PAIRS IN DEX PROTOCOLS #
AMBERDATA_DEFI_REST_DEX_PAIRS_ENDPOINT = "https://api.amberdata.com/market/defi/dex/pairs"


class MarketDataVenue(str, Enum):
    BINANCE = "binance"
    BINANCEUS = "binanceus"
    BITFINEX = "bitfinex"
    BITGET = "bitget"
    BITHUMB = "bithumb"
    BITMEX = "bitmex"
    BITSTAMP = "bitstamp"
    BYBIT = "bybit"
    CBOEDIGITAL = "cboedigital"
    COINBASE = "gdax"
    GDAX = "gdax"
    GEMINI = "gemini"
    HUOBI = "huobi"
    ITBIT = "itbit"
    KRAKEN = "kraken"
    LMAX = "lmax"
    MERCADOBITCOIN = "mercadobitcoin"
    MEXC = "mexc"
    OKEX = "okex"
    POLONIEX = "poloniex"
    DERIBIT = "deribit"
    HYPERLIQUID = "hyperliquid"

class TimeFormat(Enum):
    MILLISECONDS = "milliseconds"
    MS = "ms"
    ISO = "iso"
    ISO8601 = "iso8601"
    HR = "hr"
    HUMAN_READABLE = "human_readable"

class DexDataVenue(str, Enum):
    UNISWAP_V2 = "uniswapv2"
    UNISWAP_V3 = "uniswapv3"
    SUSHISWAP = "sushiswap"
    BALANCER_VAULT = "balancer vault"
    CURVE_V1 = "curvev1"
    PANCAKESWAP = "Pancake LPs"
    CRODEFISWAP = "CroDefiSwap"

class ProtocolId(str, Enum):
    UNISWAP_V2 = "uniswapv2"
    UNISWAP_V3 = "uniswapv3"
    SUSHISWAP = "sushiswap"
    CURVE_V1 = "curve"
    AAVE_V2 = "aavev2"
    AAVE_V3 = "aavev3"
    COMPOUND_V2 = "compoundv2"
    COMPOUND_V3 = "compoundv3"
    makerdao = "makerdao"


class ProtocolAction(str, Enum):
    PAIR_CREATED = "PairCreated"
    POOL_CREATED = "PoolCreated"
    DEPOSIT = "Deposit"
    WITHDRAW = "Withdraw"
    LIQUIDATION_CALL = "LiquidationCall"
    REPAY = "Repay"
    BORROW = "Borrow"
    FLASH_LOAN = "FlashLoan"

class StableCoin(str, Enum):
    USDC = "USDC"
    USDT = "USDT"
    DAI = "DAI"
    BUSD = "BUSD"
    TUSD = "TUSD"

class LendingProtocol(str, Enum):
    AAVE_V1 = "aave"
    AAVE_V2 = "aavev2"
    AAVE_V3 = "aavev3"
    COMPOUND_V1 = "compound"
    COMPOUND_V2 = "compoundv2"
    COMPOUND_V3 = "compoundv3"
    MAKERDAO = "makerdao"


class TimeInterval(Enum):
    MINUTE = 'minutes'
    HOUR = 'hours'
    DAY = 'days'
    TICKS = 'ticks'


class BatchPeriod(Enum):
    HOUR_1 = timedelta(hours=1)
    HOUR_2 = timedelta(hours=2)
    HOUR_4 = timedelta(hours=4)
    HOUR_8 = timedelta(hours=8)
    HOUR_12 = timedelta(hours=12)
    HOUR_16 = timedelta(hours=16)
    HOUR_20 = timedelta(hours=20)
    DAY_1 = timedelta(days=1)
    DAY_3 = timedelta(days=3)
    DAY_7 = timedelta(days=7)

class TimeBucket(Enum):
    MINUTES_5 = '5m'
    HOURS_1 = '1h'
    DAYS_1 = '1d'

class SortBy(Enum):
    NAME = 'name'
    NUMPAIRS = 'numPairs'

class SortDirection(Enum):
    ASCENDING = 'asc'
    DESCENDING = 'desc'

class DailyTime(Enum):
    T1600_M0500 = "T16:00-05:00"
    T1600_M0400 = "T16:00-04:00"
    T1600_P0000 = "T16:00+00:00"
    T1600_P0100 = "T16:00+01:00"
    T1600_P0400 = "T16:00+04:00"
    T1600_P0800 = "T16:00+08:00"
    T1600_P0900 = "T16:00+09:00"

class Blockchain(Enum):
    ETHEREUM_MAINNET = 'ethereum-mainnet'
    POLYGON_MAINNET = 'polygon-mainnet'
    AVALANCHE_MAINNET = 'avalanche-mainnet'
    ARBITRUM_ONE_MAINNET = 'arb-one-mainnet'
    BITCOIN_MAINNET = 'bitcoin-mainnet'
    BITCOIN_CASH_MAINNET = 'bitcoin-abc-mainnet'
    BINANCE_SMART_CHAIN_MAINNET = 'bnb-mainnet'
    LITECOIN_MAINNET = 'litecoin-mainnet'
    SOLANA_MAINNET = 'solana-mainnet'

class DEXSortBy(Enum):
    NUM_PAIRS = 'numPairs'
    VOLUME_USD = 'volumeUSD'
    # Add other sorting options as needed
