from __future__ import annotations

import argparse
import errno
import gzip
import hashlib
import json
import html
import math
import os
import re
import socket
import sqlite3
import statistics
import subprocess
import sys
import time
import threading
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# Short-horizon directional model — additive, evaluated offline against the
# existing build_forecast (see scripts/compare_models.py + the report at
# vault/market-map/short_horizon_compare.json).
sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))
import short_horizon_model as _shm  # noqa: E402


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "financial_board.db"
CONFIG_PATH = BASE_DIR / "config.json"
KB_DIR = BASE_DIR / "kb"
DATA_DIR = BASE_DIR / "data"
UNIVERSE_DIR = DATA_DIR / "universes"
RELATIONS_DIR = DATA_DIR / "relations"
FACTOR_DIR = DATA_DIR / "factors"
PAPER_DIR = DATA_DIR / "papers"
MACRO_DATA_DIR = DATA_DIR / "macro"
VAULT_DIR = BASE_DIR / "vault" / "market-map"
COMPANY_PROJECTS_PATH = DATA_DIR / "company_projects.json"
DEFAULT_PORT = 8000
PORT_SCAN_LIMIT = 20

DEFAULT_CONFIG = {
  "provider": "yahoo",
  "alphaVantageApiKey": "",
  "fredApiKey": "",
  "localLlmBaseUrl": "http://127.0.0.1:11434",
  "localLlmModel": "Bonsai-8B-1bit",
}

DEFAULT_WATCHLIST = ["BHARTIARTL.NS", "ICICIBANK.NS", "GLENMARK.NS"]

FALLBACK_TICKERS = {
  "AAPL": {"name": "Apple", "basePrice": 212.4, "currency": "USD", "exchange": "NASDAQ", "beta": 1.08, "pe": 31.4, "sector": "technology", "tags": ["tech", "consumer electronics", "software"]},
  "MSFT": {"name": "Microsoft", "basePrice": 428.8, "currency": "USD", "exchange": "NASDAQ", "beta": 0.92, "pe": 36.2, "sector": "technology", "tags": ["tech", "software", "cloud", "ai"]},
  "NVDA": {"name": "NVIDIA", "basePrice": 928.1, "currency": "USD", "exchange": "NASDAQ", "beta": 1.74, "pe": 63.1, "sector": "technology", "tags": ["tech", "semiconductor", "chips", "ai", "gpu"]},
  "AMZN": {"name": "Amazon", "basePrice": 183.1, "currency": "USD", "exchange": "NASDAQ", "beta": 1.18, "pe": 44.5, "sector": "consumer discretionary", "tags": ["ecommerce", "cloud", "retail", "tech"]},
  "META": {"name": "Meta Platforms", "basePrice": 498.7, "currency": "USD", "exchange": "NASDAQ", "beta": 1.22, "pe": 27.4, "sector": "communication services", "tags": ["social media", "tech", "advertising", "ai"]},
  "GOOGL": {"name": "Alphabet", "basePrice": 161.5, "currency": "USD", "exchange": "NASDAQ", "beta": 1.04, "pe": 25.7, "sector": "communication services", "tags": ["tech", "search", "cloud", "advertising", "ai"]},
  "TSLA": {"name": "Tesla", "basePrice": 184.2, "currency": "USD", "exchange": "NASDAQ", "beta": 2.03, "pe": 58.9, "sector": "consumer discretionary", "tags": ["ev", "electric vehicle", "auto", "energy", "tech"]},
  "AMD": {"name": "AMD", "basePrice": 178.9, "currency": "USD", "exchange": "NASDAQ", "beta": 1.62, "pe": 49.8, "sector": "technology", "tags": ["semiconductor", "chips", "cpu", "gpu", "tech"]},
  "RELIANCE.NS": {"name": "Reliance Industries", "basePrice": 2940.0, "currency": "INR", "exchange": "NSE", "beta": 0.96, "pe": 28.3, "sector": "energy", "tags": ["oil", "gas", "petrochemical", "telecom", "retail", "conglomerate"]},
  "BHARTIARTL.NS": {"name": "Bharti Airtel", "basePrice": 1228.0, "currency": "INR", "exchange": "NSE", "beta": 0.84, "pe": 54.0, "sector": "communication services", "tags": ["telecom", "wireless", "broadband", "africa"]},
  "ICICIBANK.NS": {"name": "ICICI Bank", "basePrice": 1094.0, "currency": "INR", "exchange": "NSE", "beta": 0.89, "pe": 18.8, "sector": "financials", "tags": ["bank", "banking", "finance", "private bank", "nbfc"]},
  "GLENMARK.NS": {"name": "Glenmark Pharma", "basePrice": 1168.0, "currency": "INR", "exchange": "NSE", "beta": 0.93, "pe": 21.7, "sector": "healthcare", "tags": ["pharma", "pharmaceutical", "drug", "medicine", "healthcare"]},
  "TCS.NS": {"name": "TCS", "basePrice": 4125.0, "currency": "INR", "exchange": "NSE", "beta": 0.81, "pe": 31.2, "sector": "technology", "tags": ["it", "tech", "software", "consulting", "outsourcing"]},
  "INFY.NS": {"name": "Infosys", "basePrice": 1518.0, "currency": "INR", "exchange": "NSE", "beta": 0.88, "pe": 24.6, "sector": "technology", "tags": ["it", "tech", "software", "consulting", "outsourcing"]},
  "HDFCBANK.NS": {"name": "HDFC Bank", "basePrice": 1528.0, "currency": "INR", "exchange": "NSE", "beta": 0.77, "pe": 19.4, "sector": "financials", "tags": ["bank", "banking", "finance", "private bank"]},
  "SBIN.NS": {"name": "State Bank of India", "basePrice": 818.0, "currency": "INR", "exchange": "NSE", "beta": 0.92, "pe": 10.9, "aliases": ["SBI", "STATE BANK OF INDIA"], "sector": "financials", "tags": ["bank", "banking", "psu", "public sector", "finance"]},
  # Additional India sector stocks
  "SUNPHARMA.NS": {"name": "Sun Pharmaceutical", "basePrice": 1680.0, "currency": "INR", "exchange": "NSE", "beta": 0.72, "pe": 34.2, "sector": "healthcare", "tags": ["pharma", "pharmaceutical", "drug", "medicine", "healthcare"]},
  "DRREDDY.NS": {"name": "Dr Reddy's Laboratories", "basePrice": 5980.0, "currency": "INR", "exchange": "NSE", "beta": 0.68, "pe": 22.8, "sector": "healthcare", "tags": ["pharma", "pharmaceutical", "drug", "generic", "healthcare"], "aliases": ["DR REDDY"]},
  "CIPLA.NS": {"name": "Cipla", "basePrice": 1520.0, "currency": "INR", "exchange": "NSE", "beta": 0.71, "pe": 26.5, "sector": "healthcare", "tags": ["pharma", "pharmaceutical", "drug", "medicine", "healthcare"]},
  "DIVISLAB.NS": {"name": "Divi's Laboratories", "basePrice": 5320.0, "currency": "INR", "exchange": "NSE", "beta": 0.65, "pe": 42.1, "sector": "healthcare", "tags": ["pharma", "api", "pharmaceutical", "drug", "healthcare"], "aliases": ["DIVI"]},
  "WIPRO.NS": {"name": "Wipro", "basePrice": 478.0, "currency": "INR", "exchange": "NSE", "beta": 0.82, "pe": 22.4, "sector": "technology", "tags": ["it", "tech", "software", "consulting"]},
  "HCLTECH.NS": {"name": "HCL Technologies", "basePrice": 1690.0, "currency": "INR", "exchange": "NSE", "beta": 0.85, "pe": 24.8, "sector": "technology", "tags": ["it", "tech", "software", "consulting"], "aliases": ["HCL"]},
  "AXISBANK.NS": {"name": "Axis Bank", "basePrice": 1040.0, "currency": "INR", "exchange": "NSE", "beta": 0.94, "pe": 15.2, "sector": "financials", "tags": ["bank", "banking", "finance", "private bank"]},
  "KOTAKBANK.NS": {"name": "Kotak Mahindra Bank", "basePrice": 1780.0, "currency": "INR", "exchange": "NSE", "beta": 0.88, "pe": 23.5, "sector": "financials", "tags": ["bank", "banking", "finance", "private bank"], "aliases": ["KOTAK"]},
  "TATAMOTORS.NS": {"name": "Tata Motors", "basePrice": 780.0, "currency": "INR", "exchange": "NSE", "beta": 1.18, "pe": 8.9, "sector": "consumer discretionary", "tags": ["auto", "automobile", "ev", "car", "jlr", "tata"], "aliases": ["TATA MOTORS"]},
  "MARUTI.NS": {"name": "Maruti Suzuki", "basePrice": 11900.0, "currency": "INR", "exchange": "NSE", "beta": 0.88, "pe": 27.4, "sector": "consumer discretionary", "tags": ["auto", "automobile", "car", "suzuki"]},
  "ONGC.NS": {"name": "ONGC", "basePrice": 274.0, "currency": "INR", "exchange": "NSE", "beta": 0.94, "pe": 7.8, "sector": "energy", "tags": ["oil", "gas", "energy", "psu"], "aliases": ["OIL AND NATURAL GAS"]},
  "NTPC.NS": {"name": "NTPC", "basePrice": 382.0, "currency": "INR", "exchange": "NSE", "beta": 0.82, "pe": 16.4, "sector": "utilities", "tags": ["power", "energy", "electricity", "psu", "utility"]},
  "POWERGRID.NS": {"name": "Power Grid Corp", "basePrice": 332.0, "currency": "INR", "exchange": "NSE", "beta": 0.76, "pe": 19.2, "sector": "utilities", "tags": ["power", "energy", "electricity", "grid", "psu", "utility"]},
  "ITC.NS": {"name": "ITC", "basePrice": 445.0, "currency": "INR", "exchange": "NSE", "beta": 0.71, "pe": 27.8, "sector": "consumer staples", "tags": ["fmcg", "cigarette", "tobacco", "consumer", "hotel", "agri"]},
  "HINDUNILVR.NS": {"name": "Hindustan Unilever", "basePrice": 2290.0, "currency": "INR", "exchange": "NSE", "beta": 0.64, "pe": 55.2, "sector": "consumer staples", "tags": ["fmcg", "consumer goods", "personal care", "hul"], "aliases": ["HUL"]},
  "LT.NS": {"name": "Larsen & Toubro", "basePrice": 3580.0, "currency": "INR", "exchange": "NSE", "beta": 0.97, "pe": 32.6, "sector": "industrials", "tags": ["infra", "infrastructure", "construction", "engineering", "defence"], "aliases": ["L&T"]},
  "ADANIENT.NS": {"name": "Adani Enterprises", "basePrice": 2450.0, "currency": "INR", "exchange": "NSE", "beta": 1.22, "pe": 68.4, "sector": "industrials", "tags": ["conglomerate", "infra", "energy", "ports", "adani"]},
  # US additional
  "JPM": {"name": "JPMorgan Chase", "basePrice": 196.4, "currency": "USD", "exchange": "NYSE", "beta": 1.12, "pe": 11.8, "sector": "financials", "tags": ["bank", "banking", "finance", "investment bank"]},
  "JNJ": {"name": "Johnson & Johnson", "basePrice": 152.8, "currency": "USD", "exchange": "NYSE", "beta": 0.56, "pe": 15.4, "sector": "healthcare", "tags": ["pharma", "pharmaceutical", "medical devices", "consumer health"]},
  "PFE": {"name": "Pfizer", "basePrice": 26.8, "currency": "USD", "exchange": "NYSE", "beta": 0.62, "pe": 14.2, "sector": "healthcare", "tags": ["pharma", "pharmaceutical", "drug", "vaccine", "biotech"]},
  "ABBV": {"name": "AbbVie", "basePrice": 168.5, "currency": "USD", "exchange": "NYSE", "beta": 0.58, "pe": 16.8, "sector": "healthcare", "tags": ["pharma", "pharmaceutical", "drug", "biotech"]},
  "XOM": {"name": "ExxonMobil", "basePrice": 118.4, "currency": "USD", "exchange": "NYSE", "beta": 0.92, "pe": 14.2, "sector": "energy", "tags": ["oil", "gas", "energy", "petroleum"]},
  "^NSEI": {"name": "NIFTY 50", "basePrice": 22431.65, "currency": "INR", "exchange": "NSE", "beta": 1.0, "pe": 0.0},
  "^BSESN": {"name": "SENSEX", "basePrice": 73895.54, "currency": "INR", "exchange": "BSE", "beta": 1.0, "pe": 0.0},
  "^N225": {"name": "Nikkei 225", "basePrice": 38405.12, "currency": "JPY", "exchange": "JPX", "beta": 1.0, "pe": 0.0},
  "^TOPX": {"name": "TOPIX", "basePrice": 2721.45, "currency": "JPY", "exchange": "JPX", "beta": 1.0, "pe": 0.0},
  "^AXJO": {"name": "S&P/ASX 200", "basePrice": 7774.80, "currency": "AUD", "exchange": "ASX", "beta": 1.0, "pe": 0.0},
  "^AORD": {"name": "All Ordinaries", "basePrice": 8014.37, "currency": "AUD", "exchange": "ASX", "beta": 1.0, "pe": 0.0},
  "^HSI": {"name": "Hang Seng", "basePrice": 17763.18, "currency": "HKD", "exchange": "HKEX", "beta": 1.0, "pe": 0.0},
  "^HSTECH": {"name": "Hang Seng Tech", "basePrice": 3651.72, "currency": "HKD", "exchange": "HKEX", "beta": 1.0, "pe": 0.0},
  "^FTSE": {"name": "FTSE 100", "basePrice": 8144.13, "currency": "GBP", "exchange": "LSE", "beta": 1.0, "pe": 0.0},
  "^FTMC": {"name": "FTSE 250", "basePrice": 19986.41, "currency": "GBP", "exchange": "LSE", "beta": 1.0, "pe": 0.0},
  "^GSPC": {"name": "S&P 500", "basePrice": 5148.22, "currency": "USD", "exchange": "NYSE", "beta": 1.0, "pe": 0.0},
  "^IXIC": {"name": "NASDAQ Composite", "basePrice": 16162.37, "currency": "USD", "exchange": "NASDAQ", "beta": 1.0, "pe": 0.0},
}

MARKET_SUFFIXES = {
  "us": "",
  "nasdaq": "",
  "sp500": "",
  "nse": ".NS",
  "bse": ".BO",
  "asx": ".AX",
  "lse": ".L",
  "jpx": ".T",
  "xetra": ".DE",
}

# Sector keyword → sector tag mapping for fuzzy search
SECTOR_KEYWORDS: dict[str, list[str]] = {
  "pharma": ["healthcare"],
  "pharmaceutical": ["healthcare"],
  "drug": ["healthcare"],
  "medicine": ["healthcare"],
  "biotech": ["healthcare"],
  "healthcare": ["healthcare"],
  "health": ["healthcare"],
  "hospital": ["healthcare"],
  "medic": ["healthcare"],
  "bank": ["financials"],
  "banking": ["financials"],
  "finance": ["financials"],
  "financial": ["financials"],
  "nbfc": ["financials"],
  "insurance": ["financials"],
  "tech": ["technology", "communication services"],
  "technology": ["technology"],
  "software": ["technology"],
  "it ": ["technology"],
  "semiconductor": ["technology"],
  "chip": ["technology"],
  "cloud": ["technology"],
  "ai": ["technology"],
  "telecom": ["communication services"],
  "wireless": ["communication services"],
  "media": ["communication services"],
  "social": ["communication services"],
  "oil": ["energy"],
  "gas": ["energy"],
  "energy": ["energy"],
  "petroleum": ["energy"],
  "power": ["utilities", "energy"],
  "utility": ["utilities"],
  "electricity": ["utilities"],
  "electric": ["utilities", "consumer discretionary"],
  "auto": ["consumer discretionary"],
  "automobile": ["consumer discretionary"],
  "car": ["consumer discretionary"],
  "ev": ["consumer discretionary"],
  "fmcg": ["consumer staples"],
  "consumer": ["consumer staples", "consumer discretionary"],
  "food": ["consumer staples"],
  "retail": ["consumer discretionary"],
  "ecommerce": ["consumer discretionary"],
  "infra": ["industrials"],
  "infrastructure": ["industrials"],
  "construction": ["industrials"],
  "engineering": ["industrials"],
  "defence": ["industrials"],
  "psu": ["industrials", "energy", "utilities", "financials"],
  "conglomerate": ["industrials"],
  "metal": ["materials"],
  "steel": ["materials"],
  "mining": ["materials"],
  "cement": ["materials"],
  "chemical": ["materials"],
  "realty": ["real estate"],
  "real estate": ["real estate"],
  "property": ["real estate"],
  "reit": ["real estate"],
}

MACRO_SYMBOLS = [
  {"label": "S&P 500", "symbol": "^GSPC"},
  {"label": "NASDAQ 100", "symbol": "^NDX"},
  {"label": "NIFTY 50", "symbol": "^NSEI"},
  {"label": "US 10Y Yield", "symbol": "^TNX"},
  {"label": "WTI Crude", "symbol": "CL=F"},
  {"label": "Gold", "symbol": "GC=F"},
]

# Sector indices per market — used by /api/sectors
SECTOR_INDICES: dict[str, list[dict]] = {
  "india": [
    {"label": "Bank", "symbol": "^NSEBANK", "sector": "financials"},
    {"label": "IT", "symbol": "^CNXIT", "sector": "technology"},
    {"label": "Pharma", "symbol": "^CNXPHARMA", "sector": "healthcare"},
    {"label": "Auto", "symbol": "^CNXAUTO", "sector": "consumer discretionary"},
    {"label": "FMCG", "symbol": "^CNXFMCG", "sector": "consumer staples"},
    {"label": "Metal", "symbol": "^CNXMETAL", "sector": "materials"},
    {"label": "Energy", "symbol": "^CNXENERGY", "sector": "energy"},
    {"label": "Infra", "symbol": "^CNXINFRA", "sector": "industrials"},
    {"label": "Realty", "symbol": "^CNXREALTY", "sector": "real estate"},
    {"label": "Media", "symbol": "^CNXMEDIA", "sector": "communication services"},
    {"label": "PSU Bank", "symbol": "^NIFPSUBNK", "sector": "financials"},
    {"label": "Midcap", "symbol": "^NIFMDCP100", "sector": "broad"},
  ],
  "us": [
    {"label": "Technology", "symbol": "XLK", "sector": "technology"},
    {"label": "Financials", "symbol": "XLF", "sector": "financials"},
    {"label": "Healthcare", "symbol": "XLV", "sector": "healthcare"},
    {"label": "Energy", "symbol": "XLE", "sector": "energy"},
    {"label": "Industrials", "symbol": "XLI", "sector": "industrials"},
    {"label": "Cons. Disc.", "symbol": "XLY", "sector": "consumer discretionary"},
    {"label": "Cons. Staples", "symbol": "XLP", "sector": "consumer staples"},
    {"label": "Utilities", "symbol": "XLU", "sector": "utilities"},
    {"label": "Materials", "symbol": "XLB", "sector": "materials"},
    {"label": "Real Estate", "symbol": "XLRE", "sector": "real estate"},
    {"label": "Comm. Svcs", "symbol": "XLC", "sector": "communication services"},
  ],
  "global": [
    {"label": "NIFTY 50", "symbol": "^NSEI", "sector": "india broad"},
    {"label": "S&P 500", "symbol": "^GSPC", "sector": "us broad"},
    {"label": "NASDAQ 100", "symbol": "^NDX", "sector": "us tech"},
    {"label": "Nikkei 225", "symbol": "^N225", "sector": "japan broad"},
    {"label": "Hang Seng", "symbol": "^HSI", "sector": "hk broad"},
    {"label": "FTSE 100", "symbol": "^FTSE", "sector": "uk broad"},
    {"label": "Gold", "symbol": "GC=F", "sector": "commodities"},
    {"label": "Crude Oil", "symbol": "CL=F", "sector": "commodities"},
    {"label": "US 10Y", "symbol": "^TNX", "sector": "rates"},
    {"label": "USD Index", "symbol": "DX-Y.NYB", "sector": "fx"},
  ],
}

# In-memory cache: {market_key: {period: {updated_at, sectors}}}
_sector_cache: dict = {}
_SECTOR_CACHE_TTL = 900  # 15 minutes for closed-market and longer-period sector views
_SECTOR_LIVE_CACHE_TTL = 20
_quote_cache: dict[str, dict] = {}
_memory_payload_cache: dict[str, dict] = {}
_QUOTE_CACHE_LOCK = threading.Lock()
_QUOTE_FETCH_LOCK = threading.Lock()
_QUOTE_PROVIDER_HEALTH_LOCK = threading.Lock()
_QUOTE_PROVIDER_HEALTH: dict[str, dict] = {}
_MEMORY_PAYLOAD_CACHE_LOCK = threading.Lock()
_SERVER_STOPPING = threading.Event()
QUOTE_CACHE_TTL = 2
QUOTE_STALE_TTL = 600
QUOTE_PROVIDER_FAILURE_COOLDOWN = 45
QUOTE_PROVIDER_TIMEOUT_SECONDS = 5
QUOTE_PROVIDER_PARALLEL_TIMEOUT_SECONDS = 8
LIVE_QUOTE_EDGE_SECONDS = 90
QUOTE_STREAM_INTERVAL_SECONDS = 1.5
SECTOR_PERIOD_LABELS = {
  "1D": "1 day",
  "5D": "5 days",
  "1W": "1 week",
  "1M": "1 month",
  "3M": "3 months",
  "6M": "6 months",
  "1Y": "1 year",
}
SECTOR_BENCHMARKS: dict[str, list[dict]] = {
  "india": [
    {"label": "NIFTY 50", "symbol": "^NSEI"},
    {"label": "SENSEX", "symbol": "^BSESN"},
    {"label": "NIFTY Bank", "symbol": "^NSEBANK"},
  ],
  "us": [
    {"label": "S&P 500", "symbol": "^GSPC"},
    {"label": "NASDAQ 100", "symbol": "^NDX"},
    {"label": "Dow Jones", "symbol": "^DJI"},
  ],
  "global": [
    {"label": "NIFTY 50", "symbol": "^NSEI"},
    {"label": "S&P 500", "symbol": "^GSPC"},
    {"label": "Nikkei 225", "symbol": "^N225"},
  ],
}
MARKET_MAP_UNIVERSES = {
  "india": "nse_all",
  "us": "sp500",
}
MARKET_MAP_FALLBACK_UNIVERSES = {
  "nse_all": "sensex30",
}
MARKET_MAP_SCOPE_LIMITS = {
  "top100": 100,
  "top250": 250,
  "top750": 750,
  "all": 0,
}

GOOGLE_FINANCE_INDEX_ALIASES: dict[str, list[str]] = {
  "^NSEI": ["NIFTY_50:INDEXNSE"],
  "^BSESN": ["SENSEX:INDEXBOM"],
  "^NSEBANK": ["NIFTY_BANK:INDEXNSE"],
  "^CNXIT": ["NIFTY_IT:INDEXNSE"],
  "^CNXPHARMA": ["NIFTY_PHARMA:INDEXNSE"],
  "^CNXAUTO": ["NIFTY_AUTO:INDEXNSE"],
  "^CNXFMCG": ["NIFTY_FMCG:INDEXNSE"],
  "^CNXMETAL": ["NIFTY_METAL:INDEXNSE"],
  "^CNXENERGY": ["NIFTY_ENERGY:INDEXNSE"],
  "^CNXINFRA": ["NIFTY_INFRA:INDEXNSE"],
  "^CNXREALTY": ["NIFTY_REALTY:INDEXNSE"],
  "^CNXMEDIA": ["NIFTY_MEDIA:INDEXNSE"],
  "^NIFPSUBNK": ["NIFTY_PSU_BANK:INDEXNSE"],
  # Google Finance does not expose the NIFTY Midcap 100 page consistently;
  # use the closest NSE midcap index so the dashboard does not show a fake zero.
  "^NIFMDCP100": ["NIFTY_MIDCAP_50:INDEXNSE"],
}

MARKET_PRESETS = [
  {
    "name": "nasdaq_core",
    "label": "NASDAQ Core",
    "symbols": ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "AMD"],
  },
  {
    "name": "sp500_leaders",
    "label": "S&P 500 Leaders",
    "symbols": ["AAPL", "MSFT", "NVDA", "JPM", "XOM", "LLY", "BRK-B", "V"],
  },
  {
    "name": "nse_leaders",
    "label": "NSE Leaders",
    "symbols": ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "LT.NS", "ITC.NS"],
  },
  {
    "name": "global_macro",
    "label": "Global Macro",
    "symbols": ["^GSPC", "^IXIC", "^NSEI", "CL=F", "GC=F", "DX-Y.NYB"],
  },
]

REGION_CONFIGS = {
  "us": {
    "key": "us",
    "label": "United States",
    "currency": "USD",
    "timezone": "America/New_York",
    "equityBenchmarks": ["S&P 500", "NASDAQ 100"],
    "bondLabel": "UST",
    "centralBank": "Federal Reserve",
    "policyRateLabel": "Fed funds",
    "inflationLabel": "CPI",
    "eventKeywords": ["fed", "treasury", "cpi", "payrolls", "tariff", "consumer", "growth"],
    "symbols": {
      "equity": ["^GSPC", "^NDX"],
      "rates": ["^TNX"],
    },
  },
  "india": {
    "key": "india",
    "label": "India",
    "currency": "INR",
    "timezone": "Asia/Kolkata",
    "equityBenchmarks": ["NIFTY 50", "SENSEX"],
    "bondLabel": "G-Sec",
    "centralBank": "Reserve Bank of India",
    "policyRateLabel": "Repo rate",
    "inflationLabel": "CPI",
    "eventKeywords": ["rbi", "inflation", "food", "crude", "rupee", "fiscal", "credit"],
    "symbols": {
      "equity": ["^NSEI"],
      "rates": [],
    },
  },
}

GLOBAL_MARKET_CLOCKS = [
  {
    "key": "india",
    "label": "India",
    "timezone": "Asia/Kolkata",
    "sessionExchange": "NSE",
    "indices": [
      {"symbol": "^NSEI", "label": "NIFTY 50"},
      {"symbol": "^BSESN", "label": "SENSEX"},
    ],
  },
  {
    "key": "japan",
    "label": "Japan",
    "timezone": "Asia/Tokyo",
    "sessionExchange": "JPX",
    "indices": [
      {"symbol": "^N225", "label": "Nikkei 225"},
      {"symbol": "^TOPX", "label": "TOPIX"},
    ],
  },
  {
    "key": "australia",
    "label": "Australia",
    "timezone": "Australia/Sydney",
    "sessionExchange": "ASX",
    "indices": [
      {"symbol": "^AXJO", "label": "ASX 200"},
      {"symbol": "^AORD", "label": "All Ordinaries"},
    ],
  },
  {
    "key": "hong_kong",
    "label": "Hong Kong",
    "timezone": "Asia/Hong_Kong",
    "sessionExchange": "HKEX",
    "indices": [
      {"symbol": "^HSI", "label": "Hang Seng"},
      {"symbol": "^HSTECH", "label": "Hang Seng Tech"},
    ],
  },
  {
    "key": "london",
    "label": "London",
    "timezone": "Europe/London",
    "sessionExchange": "LSE",
    "indices": [
      {"symbol": "^FTSE", "label": "FTSE 100"},
      {"symbol": "^FTMC", "label": "FTSE 250"},
    ],
  },
  {
    "key": "us",
    "label": "United States",
    "timezone": "America/New_York",
    "sessionExchange": "NYSE",
    "indices": [
      {"symbol": "^GSPC", "label": "S&P 500"},
      {"symbol": "^IXIC", "label": "NASDAQ"},
    ],
  },
]

REGION_BOND_FALLBACKS = {
  "us": {
    "tenors": [
      {"tenor": "2Y", "yield": 4.62, "change1D": 4.0},
      {"tenor": "5Y", "yield": 4.23, "change1D": 3.0},
      {"tenor": "10Y", "yield": 4.31, "change1D": 2.0},
      {"tenor": "30Y", "yield": 4.48, "change1D": 1.0},
    ],
    "policyRate": 5.25,
    "breakeven": 2.34,
    "realYield": 1.97,
    "curveNarrative": "Front-end is anchored by policy, while the long end is absorbing growth and term-premium repricing.",
    "source": "Curated fallback",
  },
  "india": {
    "tenors": [
      {"tenor": "2Y", "yield": 6.92, "change1D": -1.0},
      {"tenor": "5Y", "yield": 7.01, "change1D": 1.0},
      {"tenor": "10Y", "yield": 7.09, "change1D": 2.0},
      {"tenor": "30Y", "yield": 7.23, "change1D": 2.0},
    ],
    "policyRate": 6.50,
    "breakeven": 5.10,
    "realYield": 1.99,
    "curveNarrative": "India rates remain sensitive to RBI liquidity stance, food inflation, and imported energy pressure.",
    "source": "Curated fallback",
  },
}

REGION_INFLATION_FALLBACKS = {
  "us": {
    "headline": 3.1,
    "core": 3.4,
    "trend": "Sticky services inflation keeps the front-end cautious.",
    "source": "Curated fallback",
  },
  "india": {
    "headline": 5.1,
    "core": 3.4,
    "trend": "Food-led inflation remains the key swing factor for RBI expectations.",
    "source": "Curated fallback",
  },
}

MARKET_SESSION_RULES = [
  {
    "matches": {"NSE", "BSE", "INDIA"},
    "timezone": "Asia/Kolkata",
    "open": (9, 15),
    "close": (15, 30),
    "hoursLabel": "09:15-15:30 IST",
  },
  {
    "matches": {"NASDAQ", "NYSE", "US"},
    "timezone": "America/New_York",
    "open": (9, 30),
    "close": (16, 0),
    "hoursLabel": "09:30-16:00 ET",
  },
  {
    "matches": {"LSE", "LONDON"},
    "timezone": "Europe/London",
    "open": (8, 0),
    "close": (16, 30),
    "hoursLabel": "08:00-16:30 UK",
  },
  {
    "matches": {"ASX", "AUSTRALIA"},
    "timezone": "Australia/Sydney",
    "open": (10, 0),
    "close": (16, 0),
    "hoursLabel": "10:00-16:00 AEST/AEDT",
  },
  {
    "matches": {"HKEX", "HONG KONG", "HONGKONG"},
    "timezone": "Asia/Hong_Kong",
    "open": (9, 30),
    "close": (16, 0),
    "hoursLabel": "09:30-16:00 HKT",
  },
  {
    "matches": {"JPX", "TSE", "TOKYO"},
    "timezone": "Asia/Tokyo",
    "open": (9, 0),
    "close": (15, 0),
    "hoursLabel": "09:00-15:00 JST",
  },
]

RESEARCH_REFERENCES = [
  {
    "title": "Chronos: Learning the Language of Time Series",
    "year": 2024,
    "url": "https://arxiv.org/abs/2403.07815",
  },
  {
    "title": "TimesFM",
    "year": 2024,
    "url": "https://arxiv.org/abs/2310.10688",
  },
  {
    "title": "A Time Series is Worth 64 Words",
    "year": 2023,
    "url": "https://arxiv.org/abs/2211.14730",
  },
  {
    "title": "Moirai 2.0",
    "year": 2025,
    "url": "https://arxiv.org/abs/2511.11698",
  },
]

CLASSIC_QUANT_REFERENCES = [
  {
    "title": "Foundations of Technical Analysis: Computational Algorithms, Statistical Inference, and Empirical Implementation",
    "year": 2000,
    "url": "https://doi.org/10.1111/0022-1082.00265",
  },
  {
    "title": "Value Investing: The Use of Historical Financial Statement Information to Separate Winners from Losers",
    "year": 2000,
    "url": "https://doi.org/10.1111/1475-679X.00009",
  },
  {
    "title": "Asset Pricing with Liquidity Risk",
    "year": 2003,
    "url": "https://doi.org/10.1016/j.jfineco.2004.06.001",
  },
  {
    "title": "Pairs Trading: Performance of a Relative-Value Arbitrage Rule",
    "year": 2006,
    "url": "https://doi.org/10.1093/rfs/hhj020",
  },
]

FALLBACK_HEADLINES = [
  "Rates repricing is spilling into equity leadership and compressing long-duration valuations.",
  "AI infrastructure names remain crowded as earnings revisions separate real beneficiaries from thematic passengers.",
  "Energy and shipping sensitivity is back in focus as growth and inflation signals diverge across regions.",
  "Currency volatility is lifting event risk for exporters and globally diversified earnings baskets.",
  "Crowded winners face higher reaction risk when macro data collides with elevated expectations.",
]

FALLBACK_MACRO_PULSE = [
  {"label": "S&P 500", "value": "5148.22", "trend": "+0.34%", "positive": True},
  {"label": "NASDAQ 100", "value": "18042.11", "trend": "+0.58%", "positive": True},
  {"label": "NIFTY 50", "value": "22431.65", "trend": "-0.21%", "positive": False},
  {"label": "US 10Y Yield", "value": "4.19%", "trend": "+0.08%", "positive": False},
  {"label": "WTI Crude", "value": "82.40 USD", "trend": "+1.12%", "positive": False},
  {"label": "Gold", "value": "2238.10 USD", "trend": "+0.46%", "positive": True},
]

EVENT_CATEGORY_QUERIES = {
  "all": "latest market moving events world business war deals partnerships layoffs brands today",
  "markets": "latest stock market events India US equities rates earnings market pulse today",
  "business": "latest global business news markets earnings deals",
  "world": "latest world news geopolitics economy today",
  "war": "latest war news global conflict defense markets today",
  "layoffs": "latest layoffs news companies technology finance today",
  "partnerships": "latest company partnerships business strategic alliance today",
  "deals": "latest mergers acquisitions deals companies today",
  "brands": "latest brand launches campaigns retail consumer brands today",
}

MARKET_INSIGHT_RSS_FEEDS = [
  {
    "url": "https://www.paytmmoney.com/blog/category/market-pulse/feed/",
    "source": "Paytm Money Market Pulse",
    "category": "markets",
  },
  {
    "url": "https://www.paytmmoney.com/blog/category/stocks/feed/",
    "source": "Paytm Money Stocks",
    "category": "markets",
  },
  {
    "url": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "source": "Economic Times Markets",
    "category": "markets",
  },
  {
    "url": "https://feeds.content.dowjones.io/public/rss/mw_marketpulse",
    "source": "MarketWatch MarketPulse",
    "category": "markets",
  },
  {
    "url": "https://feeds.content.dowjones.io/public/rss/mw_topstories",
    "source": "MarketWatch Top Stories",
    "category": "markets",
  },
]

POPULAR_RSS_FEEDS = {
  "markets": MARKET_INSIGHT_RSS_FEEDS,
  "business": [
    {"url": "https://feeds.bbci.co.uk/news/business/rss.xml", "source": "BBC Business"},
    {"url": "https://www.npr.org/rss/rss.php?id=1006", "source": "NPR Business"},
    {"url": "https://feeds.npr.org/1006/rss.xml", "source": "NPR Business"},
    {"url": "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml", "source": "NYT Business"},
    {"url": "https://feeds.content.dowjones.io/public/rss/mw_topstories", "source": "MarketWatch Top Stories"},
    {"url": "https://feeds.content.dowjones.io/public/rss/mw_marketpulse", "source": "MarketWatch MarketPulse"},
    {"url": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms", "source": "Economic Times Markets"},
    {"url": "https://timesofindia.indiatimes.com/rssfeeds/1898055.cms", "source": "Times of India Business"},
    {"url": "https://www.smh.com.au/rss/business.xml", "source": "Sydney Morning Herald Business"},
    {"url": "https://www.abc.net.au/news/feed/51892/rss.xml", "source": "ABC Australia Business"},
    {"url": "https://www.theguardian.com/business/rss", "source": "Guardian Business"},
  ],
  "world": [
    {"url": "https://feeds.bbci.co.uk/news/world/rss.xml", "source": "BBC World"},
    {"url": "https://www.npr.org/rss/rss.php?id=1004", "source": "NPR World"},
    {"url": "https://feeds.npr.org/1004/rss.xml", "source": "NPR World"},
    {"url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml", "source": "NYT World"},
    {"url": "https://feeds.content.dowjones.io/public/rss/mw_topstories", "source": "MarketWatch Top Stories"},
    {"url": "https://economictimes.indiatimes.com/news/rssfeedsdefault.cms", "source": "Economic Times News"},
    {"url": "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms", "source": "Times of India World"},
    {"url": "https://www.smh.com.au/rss/world.xml", "source": "Sydney Morning Herald World"},
    {"url": "https://www.abc.net.au/news/feed/51120/rss.xml", "source": "ABC Australia World"},
    {"url": "https://www.theguardian.com/world/rss", "source": "Guardian World"},
    {"url": "https://www.theguardian.com/us-news/rss", "source": "Guardian US"},
  ],
  "war": [
    {"url": "https://feeds.bbci.co.uk/news/world/rss.xml", "source": "BBC World"},
    {"url": "https://www.npr.org/rss/rss.php?id=1004", "source": "NPR World"},
    {"url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml", "source": "NYT World"},
    {"url": "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms", "source": "Times of India World"},
    {"url": "https://www.smh.com.au/rss/world.xml", "source": "Sydney Morning Herald World"},
    {"url": "https://www.abc.net.au/news/feed/51120/rss.xml", "source": "ABC Australia World"},
    {"url": "https://www.theguardian.com/world/rss", "source": "Guardian World"},
  ],
  "layoffs": [
    {"url": "https://feeds.bbci.co.uk/news/business/rss.xml", "source": "BBC Business"},
    {"url": "https://www.npr.org/rss/rss.php?id=1006", "source": "NPR Business"},
    {"url": "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml", "source": "NYT Business"},
    {"url": "https://feeds.content.dowjones.io/public/rss/mw_marketpulse", "source": "MarketWatch MarketPulse"},
    {"url": "https://economictimes.indiatimes.com/news/rssfeedsdefault.cms", "source": "Economic Times News"},
    {"url": "https://www.theguardian.com/business/rss", "source": "Guardian Business"},
  ],
  "partnerships": [
    {"url": "https://feeds.bbci.co.uk/news/business/rss.xml", "source": "BBC Business"},
    {"url": "https://www.npr.org/rss/rss.php?id=1006", "source": "NPR Business"},
    {"url": "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml", "source": "NYT Business"},
    {"url": "https://feeds.content.dowjones.io/public/rss/mw_marketpulse", "source": "MarketWatch MarketPulse"},
    {"url": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms", "source": "Economic Times Markets"},
    {"url": "https://www.theguardian.com/business/rss", "source": "Guardian Business"},
  ],
  "deals": [
    {"url": "https://feeds.bbci.co.uk/news/business/rss.xml", "source": "BBC Business"},
    {"url": "https://www.npr.org/rss/rss.php?id=1006", "source": "NPR Business"},
    {"url": "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml", "source": "NYT Business"},
    {"url": "https://feeds.content.dowjones.io/public/rss/mw_marketpulse", "source": "MarketWatch MarketPulse"},
    {"url": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms", "source": "Economic Times Markets"},
    {"url": "https://www.theguardian.com/business/rss", "source": "Guardian Business"},
  ],
  "brands": [
    {"url": "https://feeds.bbci.co.uk/news/business/rss.xml", "source": "BBC Business"},
    {"url": "https://www.npr.org/rss/rss.php?id=1006", "source": "NPR Business"},
    {"url": "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml", "source": "NYT Business"},
    {"url": "https://feeds.content.dowjones.io/public/rss/mw_marketpulse", "source": "MarketWatch MarketPulse"},
    {"url": "https://timesofindia.indiatimes.com/rssfeeds/1898055.cms", "source": "Times of India Business"},
    {"url": "https://www.theguardian.com/business/rss", "source": "Guardian Business"},
  ],
}

RADAR_REGION_KEYWORDS = {
  "north_america": {"us", "usa", "united states", "canada", "washington", "new york", "california", "mexico"},
  "south_america": {"brazil", "argentina", "chile", "colombia", "peru", "venezuela"},
  "europe": {"europe", "eu", "uk", "britain", "germany", "france", "italy", "spain", "nato", "brussels", "london", "ukraine", "russia"},
  "africa": {"africa", "egypt", "south africa", "nigeria", "ethiopia", "sudan"},
  "middle_east": {"iran", "israel", "gaza", "saudi", "uae", "qatar", "yemen", "lebanon", "syria", "iraq", "middle east"},
  "south_asia": {"india", "pakistan", "bangladesh", "sri lanka", "nse", "mumbai", "delhi"},
  "east_asia": {"china", "taiwan", "japan", "korea", "south korea", "north korea", "hong kong", "beijing", "tokyo"},
}

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123 Safari/537.36"
DB_LOCK = threading.Lock()
_DB_INITIALIZED = False
_DB_INITIALIZED_PATH: Path | None = None
_DB_INIT_LOCK = threading.Lock()
OUTBOUND_LOCK = threading.Lock()
OUTBOUND_LAST_REQUEST_AT: dict[str, float] = {}
OUTBOUND_RESPONSE_CACHE: dict[str, tuple[float, object]] = {}
HISTORY_WARMUP_LOCK = threading.Lock()
HISTORY_WARMUP_JOBS: dict[str, dict] = {}
HISTORY_INFLIGHT_LOCK = threading.Lock()
HISTORY_INFLIGHT: dict[str, threading.Event] = {}
BACKEND_SCRIPT_LOCK = threading.Lock()
BACKEND_SCRIPT_JOBS: dict[str, dict] = {}
BACKEND_SCRIPT_LAST_RUN: dict[str, str] = {}
BACKEND_SCRIPT_TIMEOUT_SECONDS = 120
BACKEND_REFRESH_SCRIPTS = [
  {
    "id": "macro-factor-store",
    "label": "Macro factor store",
    "script": "sync_macro_factor_store.py",
    "cadenceSeconds": 1800,
    "freshnessPaths": [MACRO_DATA_DIR / "manifest.json"],
  },
  {
    "id": "universe-manifests",
    "label": "Universe manifests",
    "script": "sync_universes.py",
    "cadenceSeconds": 86400,
    "freshnessPaths": [UNIVERSE_DIR / "manifest.json"],
  },
]
OPERATOR_JOB_SPECS = {
  "refresh-foundations": {
    "label": "Refresh data foundations",
    "description": "Refresh macro factors and universe manifests now.",
    "steps": [
      {"id": "macro-factor-store", "label": "Macro factor store", "script": "sync_macro_factor_store.py", "timeoutSeconds": 180},
      {"id": "universe-manifests", "label": "Universe manifests", "script": "sync_universes.py", "timeoutSeconds": 180},
    ],
  },
  "refresh-events": {
    "label": "Refresh market events",
    "description": "Refresh source-labelled market events into the local database.",
    "steps": [
      {"id": "market-events", "label": "Market events", "script": "refresh_market_events.py", "args": ["--category", "markets"], "timeoutSeconds": 180},
    ],
  },
  "prepare-market-graph": {
    "label": "Prepare market graph",
    "description": "Run the bounded universe, history, relations, company-network, and market-map pipeline.",
    "steps": [
      {
        "id": "market-graph",
        "label": "Market graph pipeline",
        "script": "prepare_market_graph.py",
        "args": ["--nasdaq-limit", "250", "--workers", "6"],
        "timeoutSeconds": 900,
      },
    ],
  },
  "rebuild-knowledge": {
    "label": "Rebuild local knowledge",
    "description": "Refresh research, agent-memory, and generated market-map notes.",
    "steps": [
      {
        "id": "knowledge-base",
        "label": "Knowledge base",
        "script": "update_knowledge_base.py",
        "args": ["--full-market-map"],
        "timeoutSeconds": 300,
      },
    ],
  },
}
TRUSTED_DATA_SOURCE_REGISTRY = [
  {
    "id": "sec-edgar",
    "label": "SEC EDGAR APIs",
    "url": "https://www.sec.gov/search-filings/edgar-application-programming-interfaces",
    "useFor": "US company filings, XBRL company facts, and filing timestamps.",
    "integration": "candidate",
    "note": "Use for factual fundamentals, not analyst opinions.",
  },
  {
    "id": "fred",
    "label": "FRED API",
    "url": "https://fred.stlouisfed.org/docs/api/fred/overview.html",
    "useFor": "US rates, inflation, policy, labor, and macro series.",
    "integration": "scripted",
    "note": "Macro scripts materialize this into data/macro for local reuse.",
  },
  {
    "id": "alpha-vantage",
    "label": "Alpha Vantage",
    "url": "https://www.alphavantage.co/documentation/",
    "useFor": "Quote, adjusted history, earnings calendar, estimates, and listing status where API keys permit.",
    "integration": "configured",
    "note": "Respect key limits and freshness labels.",
  },
  {
    "id": "google-finance",
    "label": "Google Finance",
    "url": "https://www.google.com/finance/",
    "useFor": "Live quote edge when regional exchange suffixes make generic quote APIs unreliable.",
    "integration": "configured",
    "note": "Use as a labelled public quote source with fallback handling.",
  },
  {
    "id": "yahoo-finance",
    "label": "Yahoo Finance",
    "url": "https://finance.yahoo.com/",
    "useFor": "Quote summary, chart live edge, fundamentals, and public consensus fields.",
    "integration": "configured",
    "note": "Normalize provider-specific fields server-side and label stale data.",
  },
  {
    "id": "stooq",
    "label": "Stooq",
    "url": "https://stooq.com/db/h/",
    "useFor": "Daily CSV fallback for history-derived quote context.",
    "integration": "configured",
    "note": "Use as historical fallback, not as an intraday live claim.",
  },
  {
    "id": "finnhub",
    "label": "Finnhub",
    "url": "https://finnhubio.github.io/",
    "useFor": "Analyst price targets, recommendation trends, estimates, ownership, and company profile data.",
    "integration": "candidate",
    "note": "Show as consensus/reference context, never as direct advice.",
  },
  {
    "id": "financial-modeling-prep",
    "label": "Financial Modeling Prep",
    "url": "https://site.financialmodelingprep.com/developer/docs/stable/financial-estimates",
    "useFor": "Analyst financial estimates such as revenue and EPS projections.",
    "integration": "candidate",
    "note": "Use with API-key gating and source confidence labels.",
  },
  {
    "id": "nasdaq-trader",
    "label": "Nasdaq Trader Symbol Directory",
    "url": "https://nasdaqtrader.com/Trader.aspx?id=symbollookup",
    "useFor": "Current-day US symbol directory and listed-security metadata.",
    "integration": "scripted",
    "note": "Universe sync uses the public directory text feed when available.",
  },
  {
    "id": "rbi",
    "label": "Reserve Bank of India",
    "url": "https://www.rbi.org.in/",
    "useFor": "India policy, rates, circulars, and official macro context.",
    "integration": "reference",
    "note": "Treat as the policy anchor for India macro interpretation.",
  },
  {
    "id": "federal-reserve",
    "label": "Federal Reserve",
    "url": "https://www.federalreserve.gov/",
    "useFor": "US policy statements, rate decisions, speeches, and calendars.",
    "integration": "reference",
    "note": "Use for policy facts before equity implications.",
  },
  {
    "id": "nse-official",
    "label": "NSE India data products",
    "url": "https://www.nseindia.com/static/market-data/eod-historical-data-subscription",
    "useFor": "Official India EOD/historical data products and market-data provenance.",
    "integration": "reference",
    "note": "Prefer official/subscribed channels over fragile scraping for India live data.",
  },
]
OUTBOUND_ALLOWED_HOSTS = {
  "query1.finance.yahoo.com",
  "query2.finance.yahoo.com",
  "finance.yahoo.com",
  "feeds.finance.yahoo.com",
  "www.google.com",
  "news.google.com",
  "duckduckgo.com",
  "feeds.bbci.co.uk",
  "www.npr.org",
  "feeds.npr.org",
  "rss.nytimes.com",
  "feeds.content.dowjones.io",
  "economictimes.indiatimes.com",
  "www.paytmmoney.com",
  "timesofindia.indiatimes.com",
  "www.smh.com.au",
  "www.abc.net.au",
  "www.theguardian.com",
  "api.bls.gov",
  "api.stlouisfed.org",
  "www.federalreserve.gov",
  "www.rbi.org.in",
  "www.nseindia.com",
  "archives.nseindia.com",
  "nsearchives.nseindia.com",
  "www.alphavantage.co",
  "stooq.com",
}
OUTBOUND_MIN_INTERVAL = {
  "query1.finance.yahoo.com": 0.8,
  "query2.finance.yahoo.com": 0.8,
  "finance.yahoo.com": 0.8,
  "feeds.finance.yahoo.com": 1.2,
  "www.google.com": 1.4,
  "news.google.com": 1.4,
  "duckduckgo.com": 2.0,
  "feeds.bbci.co.uk": 3.0,
  "www.npr.org": 3.0,
  "feeds.npr.org": 3.0,
  "rss.nytimes.com": 4.0,
  "feeds.content.dowjones.io": 4.0,
  "economictimes.indiatimes.com": 4.0,
  "www.paytmmoney.com": 4.0,
  "timesofindia.indiatimes.com": 4.0,
  "www.smh.com.au": 4.0,
  "www.abc.net.au": 4.0,
  "www.theguardian.com": 4.0,
  "api.bls.gov": 2.5,
  "api.stlouisfed.org": 2.5,
  "www.federalreserve.gov": 5.0,
  "www.rbi.org.in": 5.0,
  "www.alphavantage.co": 12.0,
  "stooq.com": 4.0,
}
OUTBOUND_CACHE_TTL = {
  "query1.finance.yahoo.com": 5,
  "query2.finance.yahoo.com": 5,
  "finance.yahoo.com": 10,
  "feeds.finance.yahoo.com": 90,
  "www.google.com": 5,
  "news.google.com": 120,
  "duckduckgo.com": 300,
  "feeds.bbci.co.uk": 900,
  "www.npr.org": 900,
  "feeds.npr.org": 900,
  "rss.nytimes.com": 900,
  "feeds.content.dowjones.io": 900,
  "economictimes.indiatimes.com": 900,
  "www.paytmmoney.com": 900,
  "timesofindia.indiatimes.com": 900,
  "www.smh.com.au": 900,
  "www.abc.net.au": 900,
  "www.theguardian.com": 900,
  "api.bls.gov": 21600,
  "api.stlouisfed.org": 21600,
  "www.federalreserve.gov": 21600,
  "www.rbi.org.in": 21600,
  "www.alphavantage.co": 1800,
  "stooq.com": 1800,
}


def resolve_local_llm_model(config: dict | None = None) -> str:
  return DEFAULT_CONFIG["localLlmModel"]


def ensure_private_file_permissions(path: Path) -> None:
  try:
    if path.exists() and path.is_file():
      os.chmod(path, 0o600)
  except OSError:
    pass


def load_config() -> dict:
  if CONFIG_PATH.exists():
    ensure_private_file_permissions(CONFIG_PATH)
    try:
      payload = {**DEFAULT_CONFIG, **json.loads(CONFIG_PATH.read_text())}
      payload["localLlmModel"] = resolve_local_llm_model(payload)
      return payload
    except json.JSONDecodeError:
      return DEFAULT_CONFIG.copy()
  return DEFAULT_CONFIG.copy()


def public_config(config: dict | None = None) -> dict:
  payload = config or load_config()
  return {
    "provider": payload.get("provider", "yahoo"),
    "alphaVantageConfigured": bool(payload.get("alphaVantageApiKey")),
    "fredConfigured": bool(payload.get("fredApiKey") or os.environ.get("FRED_API_KEY", "").strip()),
    "localLlmBaseUrl": payload.get("localLlmBaseUrl", DEFAULT_CONFIG["localLlmBaseUrl"]),
    "localLlmModel": resolve_local_llm_model(payload),
  }


def write_private_json(path: Path, payload: dict) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
  temporary.write_text(json.dumps(payload, indent=2))
  try:
    ensure_private_file_permissions(temporary)
    temporary.replace(path)
    ensure_private_file_permissions(path)
  finally:
    if temporary.exists():
      temporary.unlink()


def save_config(config: dict) -> dict:
  current = load_config()
  provider = str(config.get("provider", current.get("provider", "yahoo"))).strip().lower()
  if provider not in {"yahoo", "alpha_vantage"}:
    raise ValueError("Unsupported provider")
  local_llm_base_url = str(
    config.get("localLlmBaseUrl", current.get("localLlmBaseUrl", DEFAULT_CONFIG["localLlmBaseUrl"]))
  ).strip() or DEFAULT_CONFIG["localLlmBaseUrl"]
  if not is_allowed_local_llm_base_url(local_llm_base_url):
    raise ValueError("Local LLM URL must use http(s) on localhost or a loopback IP")

  payload = {
    "provider": provider,
    "alphaVantageApiKey": current.get("alphaVantageApiKey", ""),
    "fredApiKey": current.get("fredApiKey", ""),
    "localLlmBaseUrl": local_llm_base_url.rstrip("/"),
    "localLlmModel": resolve_local_llm_model(config),
  }
  if "alphaVantageApiKey" in config:
    payload["alphaVantageApiKey"] = str(config.get("alphaVantageApiKey") or "").strip()
  if "fredApiKey" in config:
    payload["fredApiKey"] = str(config.get("fredApiKey") or "").strip()
  write_private_json(CONFIG_PATH, payload)
  return public_config(payload)


def _configure_connection(conn: sqlite3.Connection) -> None:
  """Apply performance PRAGMAs to a SQLite connection."""
  conn.execute("PRAGMA journal_mode=WAL")
  conn.execute("PRAGMA synchronous=NORMAL")
  conn.execute("PRAGMA cache_size=-8192")    # 8 MB page cache
  conn.execute("PRAGMA temp_store=MEMORY")
  conn.execute("PRAGMA mmap_size=134217728") # 128 MB memory-mapped I/O


def init_db() -> None:
  global _DB_INITIALIZED, _DB_INITIALIZED_PATH
  current_path = Path(DB_PATH)
  # Fast path — already initialised (no lock needed for read)
  if _DB_INITIALIZED and _DB_INITIALIZED_PATH == current_path:
    return
  # Slow path — one-time setup with double-checked locking
  with _DB_INIT_LOCK:
    if _DB_INITIALIZED and _DB_INITIALIZED_PATH == current_path:
      return
    with DB_LOCK:
      connection = sqlite3.connect(DB_PATH)
      try:
        _configure_connection(connection)
        connection.execute(
          """
          CREATE TABLE IF NOT EXISTS watchlists (
            name TEXT PRIMARY KEY,
            symbols_json TEXT NOT NULL,
            updated_at TEXT NOT NULL
          )
          """
        )
        connection.execute(
          """
          CREATE TABLE IF NOT EXISTS history_cache (
            symbol TEXT NOT NULL,
            chart_range TEXT NOT NULL,
            closes_json TEXT NOT NULL,
            meta_json TEXT NOT NULL,
            source TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            PRIMARY KEY(symbol, chart_range)
          )
          """
        )
        connection.execute(
          """
          CREATE TABLE IF NOT EXISTS payload_cache (
            cache_key TEXT PRIMARY KEY,
            payload_json TEXT NOT NULL,
            source TEXT NOT NULL,
            updated_at TEXT NOT NULL
          )
          """
        )
        connection.execute(
          """
          CREATE TABLE IF NOT EXISTS historical_records (
            symbol TEXT NOT NULL,
            interval TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            close REAL NOT NULL,
            volume REAL,
            source TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            PRIMARY KEY(symbol, interval, timestamp)
          )
          """
        )
        connection.execute(
          """
          CREATE TABLE IF NOT EXISTS derived_insights (
            symbol TEXT NOT NULL,
            interval TEXT NOT NULL,
            insight_key TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            source TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            PRIMARY KEY(symbol, interval, insight_key)
          )
          """
        )
        connection.execute(
          """
          CREATE TABLE IF NOT EXISTS market_events (
            event_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            url TEXT,
            source TEXT NOT NULL,
            category TEXT NOT NULL,
            symbols_json TEXT NOT NULL,
            published_at TEXT,
            fetched_at TEXT NOT NULL,
            relevance_score REAL NOT NULL,
            significance_score REAL NOT NULL,
            payload_json TEXT NOT NULL
          )
          """
        )
        connection.execute(
          "CREATE INDEX IF NOT EXISTS idx_market_events_category_time ON market_events(category, published_at, fetched_at)"
        )
        connection.execute(
          "CREATE INDEX IF NOT EXISTS idx_market_events_source ON market_events(source)"
        )
        connection.commit()
      finally:
        connection.close()
      for private_path in (
        current_path,
        Path(f"{current_path}-shm"),
        Path(f"{current_path}-wal"),
      ):
        ensure_private_file_permissions(private_path)
    _DB_INITIALIZED = True
    _DB_INITIALIZED_PATH = current_path


def save_watchlist(name: str, symbols: list[str]) -> None:
  payload = json.dumps(symbols)
  updated_at = datetime.now(timezone.utc).isoformat()
  with DB_LOCK:
    connection = sqlite3.connect(DB_PATH)
    try:
      connection.execute(
        """
        INSERT INTO watchlists(name, symbols_json, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
          symbols_json = excluded.symbols_json,
          updated_at = excluded.updated_at
        """,
        (name, payload, updated_at),
      )
      connection.commit()
    finally:
      connection.close()


def list_watchlists() -> list[dict]:
  with DB_LOCK:
    connection = sqlite3.connect(DB_PATH)
    try:
      rows = connection.execute(
        "SELECT name, symbols_json, updated_at FROM watchlists ORDER BY updated_at DESC"
      ).fetchall()
    finally:
      connection.close()

  items = []
  for name, symbols_json, updated_at in rows:
    symbols = json.loads(symbols_json)
    items.append(
      {
        "name": name,
        "symbols": symbols,
        "count": len(symbols),
        "updatedAt": updated_at,
      }
    )
  return items


HISTORY_CACHE_MAX_AGE = {
  "1D": 90,
  "3D": 300,
  "5D": 600,
  "1M": 3600,
  "1Y": 21600,
  "2Y": 43200,
  "3Y": 86400,
  "5Y": 86400,
  "MAX": 86400,
}

PAYLOAD_CACHE_MAX_AGE = {
  "region_bonds": 1800,
  "region_inflation": 21600,
  "region_events": 1800,
  "region_calendar": 21600,
  "market_heat_map": 300,
}


def history_cache_ttl(chart_range: str) -> int:
  return HISTORY_CACHE_MAX_AGE.get((chart_range or "1M").upper(), HISTORY_CACHE_MAX_AGE["1M"])


def payload_cache_ttl(cache_kind: str) -> int:
  return PAYLOAD_CACHE_MAX_AGE.get(cache_kind, 1800)


def memory_cached_value(cache_key: str, ttl_seconds: int, builder):
  now = time.time()
  with _MEMORY_PAYLOAD_CACHE_LOCK:
    cached = _memory_payload_cache.get(cache_key)
    if cached and now - float(cached.get("ts", 0)) <= ttl_seconds:
      return cached.get("value")
  value = builder()
  with _MEMORY_PAYLOAD_CACHE_LOCK:
    _memory_payload_cache[cache_key] = {"value": value, "ts": now}
  return value


def load_cached_history(symbol: str, chart_range: str) -> tuple[list[float], dict, str, str] | None:
  init_db()
  with DB_LOCK:
    connection = sqlite3.connect(DB_PATH)
    try:
      row = connection.execute(
        """
        SELECT closes_json, meta_json, source, updated_at
        FROM history_cache
        WHERE symbol = ? AND chart_range = ?
        """,
        (symbol.upper(), chart_range.upper()),
      ).fetchone()
    finally:
      connection.close()
  if not row:
    return None
  closes_json, meta_json, source, updated_at = row
  try:
    closes = [float(value) for value in json.loads(closes_json)]
    meta = json.loads(meta_json)
  except (TypeError, ValueError, json.JSONDecodeError):
    return None
  return closes, meta if isinstance(meta, dict) else {}, source, updated_at


def load_cached_payload(cache_key: str) -> tuple[dict, str, str] | None:
  init_db()
  with DB_LOCK:
    connection = sqlite3.connect(DB_PATH)
    try:
      row = connection.execute(
        """
        SELECT payload_json, source, updated_at
        FROM payload_cache
        WHERE cache_key = ?
        """,
        (cache_key,),
      ).fetchone()
    finally:
      connection.close()
  if not row:
    return None
  payload_json, source, updated_at = row
  try:
    payload = json.loads(payload_json)
  except json.JSONDecodeError:
    return None
  if not isinstance(payload, dict):
    return None
  return payload, source, updated_at


def save_history_cache(symbol: str, chart_range: str, closes: list[float], meta: dict, source: str) -> None:
  init_db()
  payload = json.dumps([round(float(value), 6) for value in closes])
  meta_payload = json.dumps(meta or {})
  updated_at = datetime.now(timezone.utc).isoformat()
  with DB_LOCK:
    connection = sqlite3.connect(DB_PATH)
    try:
      connection.execute(
        """
        INSERT INTO history_cache(symbol, chart_range, closes_json, meta_json, source, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(symbol, chart_range) DO UPDATE SET
          closes_json = excluded.closes_json,
          meta_json = excluded.meta_json,
          source = excluded.source,
          updated_at = excluded.updated_at
        """,
        (symbol.upper(), chart_range.upper(), payload, meta_payload, source, updated_at),
      )
      connection.commit()
    finally:
      connection.close()


def save_historical_records(symbol: str, interval: str, points: list[dict], source: str) -> None:
  init_db()
  cleaned_rows = []
  updated_at = datetime.now(timezone.utc).isoformat()
  for point in points or []:
    timestamp = point.get("timestamp")
    close = point.get("value")
    if not timestamp or not isinstance(close, (int, float)):
      continue
    volume = point.get("volume")
    cleaned_rows.append(
      (
        symbol.upper(),
        interval,
        timestamp,
        float(close),
        float(volume) if isinstance(volume, (int, float)) else None,
        source,
        updated_at,
      )
    )
  if not cleaned_rows:
    return
  with DB_LOCK:
    connection = sqlite3.connect(DB_PATH)
    try:
      connection.executemany(
        """
        INSERT INTO historical_records(symbol, interval, timestamp, close, volume, source, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(symbol, interval, timestamp) DO UPDATE SET
          close = excluded.close,
          volume = excluded.volume,
          source = excluded.source,
          updated_at = excluded.updated_at
        """,
        cleaned_rows,
      )
      connection.commit()
    finally:
      connection.close()


def load_historical_records(symbol: str, interval: str, limit: int = 0) -> list[dict]:
  init_db()
  query = """
    SELECT timestamp, close, volume
    FROM historical_records
    WHERE symbol = ? AND interval = ?
    ORDER BY timestamp DESC
  """
  params: list[object] = [symbol.upper(), interval]
  if limit > 0:
    query += " LIMIT ?"
    params.append(limit)
  with DB_LOCK:
    connection = sqlite3.connect(DB_PATH)
    try:
      rows = connection.execute(query, params).fetchall()
    finally:
      connection.close()
  points = []
  for timestamp, close, volume in reversed(rows):
    if timestamp_age_seconds(timestamp) is None:
      continue
    points.append(
      {
        "timestamp": timestamp,
        "value": float(close),
        **({"volume": float(volume)} if volume is not None else {}),
      }
    )
  return points


def save_derived_insight(symbol: str, interval: str, insight_key: str, payload: dict, source: str) -> None:
  init_db()
  updated_at = datetime.now(timezone.utc).isoformat()
  with DB_LOCK:
    connection = sqlite3.connect(DB_PATH)
    try:
      connection.execute(
        """
        INSERT INTO derived_insights(symbol, interval, insight_key, payload_json, source, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(symbol, interval, insight_key) DO UPDATE SET
          payload_json = excluded.payload_json,
          source = excluded.source,
          updated_at = excluded.updated_at
        """,
        (
          normalize_symbol(symbol),
          interval.lower(),
          insight_key,
          json.dumps(payload or {}),
          source,
          updated_at,
        ),
      )
      connection.commit()
    finally:
      connection.close()


def load_derived_insight(symbol: str, interval: str, insight_key: str) -> dict | None:
  init_db()
  with DB_LOCK:
    connection = sqlite3.connect(DB_PATH)
    try:
      row = connection.execute(
        """
        SELECT payload_json, source, updated_at
        FROM derived_insights
        WHERE symbol = ? AND interval = ? AND insight_key = ?
        """,
        (normalize_symbol(symbol), interval.lower(), insight_key),
      ).fetchone()
    finally:
      connection.close()
  if not row:
    return None
  try:
    payload = json.loads(row[0])
  except json.JSONDecodeError:
    return None
  payload["source"] = row[1]
  payload["updatedAt"] = row[2]
  return payload


def stable_market_event_id(item: dict) -> str:
  seed = "|".join(
    [
      str(item.get("url") or "").strip(),
      str(item.get("title") or "").strip().lower(),
      str(item.get("source") or "").strip().lower(),
      str(item.get("publishedAt") or item.get("published_at") or "").strip(),
    ]
  )
  return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:24]


def normalize_event_symbols(symbol: str | None = None, extra_symbols: list[str] | None = None) -> list[str]:
  symbols = []
  for value in [symbol, *(extra_symbols or [])]:
    if not value:
      continue
    cleaned = normalize_symbol(str(value).strip().upper())
    if cleaned and cleaned not in symbols:
      symbols.append(cleaned)
  return symbols


def save_market_events(items: list[dict], category: str, symbol: str | None = None) -> int:
  init_db()
  cleaned_rows = []
  fetched_at = datetime.now(timezone.utc).isoformat()
  normalized_category = (category or "markets").strip().lower() or "markets"
  for item in items or []:
    title = str(item.get("title") or "").strip()
    if not title:
      continue
    item_category = (item.get("category") or normalized_category or "markets").strip().lower()
    url = str(item.get("url") or "").strip()
    source = str(item.get("source") or (urllib.parse.urlparse(url).netloc.replace("www.", "") if url else "Unknown")).strip() or "Unknown"
    symbols = normalize_event_symbols(symbol, item.get("symbols") if isinstance(item.get("symbols"), list) else [])
    relevance = float(market_relevance_score(item, item_category, symbol))
    significance = float(event_significance_score(item, item_category, symbol))
    payload = {
      **item,
      "title": title,
      "url": url,
      "source": source,
      "category": item_category,
      "symbols": symbols,
      "publishedAt": item.get("publishedAt"),
      "fetchedAt": fetched_at,
      "relevance": relevance,
      "significance": significance,
      "localDb": True,
    }
    cleaned_rows.append(
      (
        item.get("eventId") or stable_market_event_id(payload),
        title,
        url,
        source,
        item_category,
        json.dumps(symbols),
        item.get("publishedAt"),
        fetched_at,
        relevance,
        significance,
        json.dumps(payload),
      )
    )
  if not cleaned_rows:
    return 0
  with DB_LOCK:
    connection = sqlite3.connect(DB_PATH)
    try:
      connection.executemany(
        """
        INSERT INTO market_events(
          event_id, title, url, source, category, symbols_json, published_at,
          fetched_at, relevance_score, significance_score, payload_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(event_id) DO UPDATE SET
          title = excluded.title,
          url = excluded.url,
          source = excluded.source,
          category = excluded.category,
          symbols_json = excluded.symbols_json,
          published_at = COALESCE(excluded.published_at, market_events.published_at),
          fetched_at = excluded.fetched_at,
          relevance_score = excluded.relevance_score,
          significance_score = excluded.significance_score,
          payload_json = excluded.payload_json
        """,
        cleaned_rows,
      )
      connection.commit()
    finally:
      connection.close()
  return len(cleaned_rows)


def load_market_events(category: str = "all", symbol: str | None = None, limit: int = 20, max_age_hours: int = 168) -> list[dict]:
  init_db()
  normalized_category = (category or "all").strip().lower()
  cutoff = (datetime.now(timezone.utc) - timedelta(hours=max_age_hours)).isoformat()
  with DB_LOCK:
    connection = sqlite3.connect(DB_PATH)
    try:
      rows = connection.execute(
        """
        SELECT event_id, payload_json, category, symbols_json, published_at, fetched_at
        FROM market_events
        WHERE fetched_at >= ?
        ORDER BY COALESCE(published_at, fetched_at) DESC, significance_score DESC
        LIMIT ?
        """,
        (cutoff, max(limit * 4, limit)),
      ).fetchall()
    finally:
      connection.close()
  wanted_symbol = normalize_symbol(symbol) if symbol else ""
  items = []
  for event_id, payload_json, row_category, symbols_json, published_at, fetched_at in rows:
    if normalized_category not in {"all", ""} and row_category != normalized_category:
      continue
    try:
      payload = json.loads(payload_json)
      symbols = json.loads(symbols_json)
    except json.JSONDecodeError:
      continue
    if wanted_symbol and wanted_symbol not in symbols:
      continue
    payload["eventId"] = event_id
    payload["category"] = payload.get("category") or row_category
    payload["symbols"] = symbols
    payload["publishedAt"] = payload.get("publishedAt") or published_at
    payload["storedAt"] = fetched_at
    payload["localDb"] = True
    items.append(payload)
    if len(items) >= limit:
      break
  return items


def build_moving_average_insight(symbol: str, history: list[float], interval: str = "1d", persist: bool = True) -> dict:
  values = [float(value) for value in history if isinstance(value, (int, float)) and value > 0]
  if len(values) < 5:
    return {
      "label": "MA signal",
      "state": "Insufficient history",
      "sma5": None,
      "sma25": None,
      "spreadPercent": 0.0,
      "nextRunBias": "Wait",
      "confidence": 18.0,
      "why": "At least 5 valid closes are required.",
    }
  sma5 = average(values[-5:])
  sma25 = average(values[-25:]) if len(values) >= 25 else average(values)
  latest = values[-1]
  previous_sma5 = average(values[-6:-1]) if len(values) >= 6 else sma5
  previous_sma25 = average(values[-26:-1]) if len(values) >= 26 else sma25
  spread_percent = pct_change(sma5, sma25) if sma25 else 0.0
  slope5 = pct_change(sma5, previous_sma5) if previous_sma5 else 0.0
  slope25 = pct_change(sma25, previous_sma25) if previous_sma25 else 0.0
  price_vs_sma5 = pct_change(latest, sma5) if sma5 else 0.0
  price_vs_sma25 = pct_change(latest, sma25) if sma25 else 0.0
  if spread_percent > 1.2 and slope5 > 0:
    bias = "Continuation"
    state = "5D above 25D"
  elif spread_percent < -1.2 and slope5 < 0:
    bias = "Pressure"
    state = "5D below 25D"
  elif abs(spread_percent) <= 1.2:
    bias = "Compression"
    state = "Moving averages compressed"
  else:
    bias = "Mixed"
    state = "Moving averages diverging"
  confidence = clamp(42 + min(abs(spread_percent) * 5, 24) + min(abs(slope5) * 4, 12), 18, 86)
  payload = {
    "label": "5D / 25D moving-average signal",
    "state": state,
    "sma5": round(sma5, 4),
    "sma25": round(sma25, 4),
    "spreadPercent": round(spread_percent, 3),
    "slope5": round(slope5, 3),
    "slope25": round(slope25, 3),
    "priceVsSma5": round(price_vs_sma5, 3),
    "priceVsSma25": round(price_vs_sma25, 3),
    "nextRunBias": bias,
    "confidence": round(confidence, 1),
    "why": f"Latest price is {price_vs_sma5:+.2f}% vs 5D average and {price_vs_sma25:+.2f}% vs 25D average.",
  }
  if persist:
    save_derived_insight(symbol, interval, "sma_5_25", payload, "Local historical records")
  return payload


def save_payload_cache(cache_key: str, payload: dict, source: str) -> None:
  init_db()
  updated_at = datetime.now(timezone.utc).isoformat()
  payload_json = json.dumps(payload or {})
  with DB_LOCK:
    connection = sqlite3.connect(DB_PATH)
    try:
      connection.execute(
        """
        INSERT INTO payload_cache(cache_key, payload_json, source, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(cache_key) DO UPDATE SET
          payload_json = excluded.payload_json,
          source = excluded.source,
          updated_at = excluded.updated_at
        """,
        (cache_key, payload_json, source, updated_at),
      )
      connection.commit()
    finally:
      connection.close()


def build_cached_meta(meta: dict, source: str, updated_at: str, stale: bool = False) -> dict:
  payload = dict(meta or {})
  payload["historySource"] = source
  payload["historyCachedAt"] = updated_at
  payload["historyCacheState"] = "stale" if stale else "fresh"
  return payload


def payload_cache_state(updated_at: str, ttl_seconds: int) -> tuple[bool, bool]:
  try:
    age_seconds = max(0, (datetime.now(timezone.utc) - datetime.fromisoformat(updated_at)).total_seconds())
  except ValueError:
    return False, True
  return age_seconds <= ttl_seconds, age_seconds > ttl_seconds


def get_or_refresh_cached_payload(cache_kind: str, cache_key: str, builder) -> dict:
  ttl_seconds = payload_cache_ttl(cache_kind)
  cached = load_cached_payload(cache_key)
  if cached:
    payload, source, updated_at = cached
    fresh, _ = payload_cache_state(updated_at, ttl_seconds)
    if fresh:
      cached_payload = dict(payload)
      cached_payload["cacheSource"] = source
      cached_payload["cacheUpdatedAt"] = updated_at
      cached_payload["cacheState"] = "fresh"
      return cached_payload

  try:
    payload = builder()
  except Exception:
    payload = None

  if payload:
    source = payload.get("source", "Computed")
    now_iso = datetime.now(timezone.utc).isoformat()
    save_payload_cache(cache_key, payload, source)
    # Return in-memory copy directly — no read-back round-trip needed
    cached_payload = dict(payload)
    cached_payload["cacheSource"] = source
    cached_payload["cacheUpdatedAt"] = now_iso
    cached_payload["cacheState"] = "fresh"
    return cached_payload

  if cached:
    payload, source, updated_at = cached
    stale_payload = dict(payload)
    stale_payload["cacheSource"] = source
    stale_payload["cacheUpdatedAt"] = updated_at
    stale_payload["cacheState"] = "stale"
    return stale_payload

  return {"source": "Unavailable", "cacheSource": "Unavailable", "cacheState": "miss", "cacheUpdatedAt": datetime.now(timezone.utc).isoformat()}


def resolve_market_session_rule(exchange: str, region: str = "") -> dict | None:
  exchange_upper = (exchange or "").upper()
  region_upper = (region or "").upper()
  haystack_tokens = [token for token in re.split(r"[^A-Z0-9]+", f"{exchange_upper} {region_upper}") if token]
  for rule in MARKET_SESSION_RULES:
    if any(
      (
        candidate in haystack_tokens
        if len(candidate) <= 3
        else candidate in exchange_upper or candidate in region_upper or candidate in haystack_tokens
      )
      for candidate in rule["matches"]
    ):
      return rule
  return None


def next_weekday_open(current_time: datetime, open_hour: int, open_minute: int) -> datetime:
  candidate = current_time
  while True:
    candidate = candidate.replace(hour=open_hour, minute=open_minute, second=0, microsecond=0)
    if candidate.weekday() < 5 and candidate > current_time:
      return candidate
    candidate = (candidate + timedelta(days=1)).replace(hour=open_hour, minute=open_minute, second=0, microsecond=0)


def build_market_session(exchange: str, region: str, market_state: str, as_of: str | None = None) -> dict:
  rule = resolve_market_session_rule(exchange or "", region or "")
  market_state_upper = (market_state or "").upper()
  if not rule:
    return {
      "status": "Open" if market_state_upper == "REGULAR" else "Closed",
      "isOpen": market_state_upper == "REGULAR",
      "hoursLabel": "Market hours unavailable",
      "timezone": "UTC",
      "nextTransitionAt": None,
      "transitionLabel": "update",
    }

  market_tz = ZoneInfo(rule["timezone"])
  now = datetime.now(timezone.utc).astimezone(market_tz)
  open_hour, open_minute = rule["open"]
  close_hour, close_minute = rule["close"]
  today_open = now.replace(hour=open_hour, minute=open_minute, second=0, microsecond=0)
  today_close = now.replace(hour=close_hour, minute=close_minute, second=0, microsecond=0)
  within_hours = now.weekday() < 5 and today_open <= now < today_close

  if market_state_upper in {"REGULAR", "OPEN"}:
    is_open = within_hours
  elif market_state_upper in {"CLOSED", "PRE", "POST", "PREPRE", "POSTPOST"}:
    is_open = False
  else:
    is_open = within_hours

  if is_open and now.weekday() < 5 and now < today_close:
    next_transition = today_close
    transition_label = "close"
  else:
    if now.weekday() < 5 and now < today_open:
      next_transition = today_open
    else:
      next_transition = next_weekday_open(now + timedelta(seconds=1), open_hour, open_minute)
    transition_label = "open"

  return {
    "status": "Open" if is_open else "Closed",
    "isOpen": is_open,
    "hoursLabel": rule["hoursLabel"],
    "timezone": rule["timezone"],
    "nextTransitionAt": next_transition.astimezone(timezone.utc).isoformat(),
    "transitionLabel": transition_label,
    "sessionOpenAt": today_open.astimezone(timezone.utc).isoformat(),
    "sessionCloseAt": today_close.astimezone(timezone.utc).isoformat(),
    "providerState": market_state_upper or "UNKNOWN",
    "asOf": as_of,
  }


def quote_freshness(as_of: str | None, session: dict | None = None, source: str = "") -> dict:
  source_lower = (source or "").lower()
  is_reference_source = any(label in source_lower for label in {"fallback", "curated", "reference"})
  is_history_source = any(label in source_lower for label in {"history", "historical", "cache", "derived"})
  if not as_of:
    if source and is_reference_source:
      return {
        "label": "Reference level",
        "state": "reference",
        "isStale": False,
        "ageMinutes": None,
        "note": f"{source} is a documented fallback level while live benchmark providers are unavailable.",
      }
    return {
      "label": "No live timestamp",
      "state": "stale",
      "isStale": True,
      "ageMinutes": None,
      "note": f"{source or 'Provider'} did not return a quote timestamp; treat price as delayed/fallback.",
    }
  try:
    timestamp = datetime.fromisoformat(str(as_of).replace("Z", "+00:00"))
  except ValueError:
    return {
      "label": "Timestamp unreadable",
      "state": "stale",
      "isStale": True,
      "ageMinutes": None,
      "note": "Quote timestamp could not be parsed; verify before relying on this price.",
    }
  if timestamp.tzinfo is None:
    timestamp = timestamp.replace(tzinfo=timezone.utc)
  age_minutes = max(0.0, (datetime.now(timezone.utc) - timestamp.astimezone(timezone.utc)).total_seconds() / 60)
  is_open = bool((session or {}).get("isOpen"))
  stale_after = 20 if is_open else 24 * 60
  is_stale = age_minutes > stale_after
  if is_history_source:
    if is_open:
      label = "Historical fallback" if age_minutes <= stale_after else f"Stale history {age_minutes / 60:.1f}h"
      return {
        "label": label,
        "state": "stale",
        "isStale": True,
        "ageMinutes": round(age_minutes, 1),
        "staleAfterMinutes": 0,
        "note": f"{source or 'History'} is not a confirmed live quote while the market is open; refresh or verify with the source before treating this as current.",
      }
    return {
      "label": "Last history close" if age_minutes <= stale_after else f"Stale history {age_minutes / 1440:.1f}d",
      "state": "reference" if age_minutes <= stale_after else "stale",
      "isStale": age_minutes > stale_after,
      "ageMinutes": round(age_minutes, 1),
      "staleAfterMinutes": stale_after,
      "note": f"{source or 'History'} is a historical/cache-derived level, not a confirmed live quote.",
    }
  if age_minutes < 2:
    label = "Live edge"
  elif age_minutes < 20:
    label = f"Updated {age_minutes:.0f}m ago"
  elif age_minutes < 24 * 60:
    label = f"Delayed {age_minutes / 60:.1f}h"
  else:
    label = f"Stale {age_minutes / 1440:.1f}d"
  return {
    "label": label,
    "state": "stale" if is_stale else "fresh",
    "isStale": is_stale,
    "ageMinutes": round(age_minutes, 1),
    "staleAfterMinutes": stale_after,
    "note": "Market is open; stale quotes are flagged after 20 minutes." if is_open else "Market is closed; last session quote is acceptable but labeled by age.",
  }


def source_label_is_history(source: str | None) -> bool:
  source_lower = (source or "").lower()
  return any(label in source_lower for label in {"history", "historical", "cache", "derived", "daily csv"})


def quote_checked_at_iso(quote: dict | None) -> str | None:
  value = (quote or {}).get("quoteSourceCheckedAt")
  if not value:
    return None
  try:
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
  except ValueError:
    return None
  if parsed.tzinfo is None:
    parsed = parsed.replace(tzinfo=timezone.utc)
  return parsed.astimezone(timezone.utc).isoformat()


def quote_effective_as_of(quote: dict | None, data_source: str, history_as_of: str | None = None) -> str | None:
  market_time = (quote or {}).get("regularMarketTime")
  if market_time:
    return timestamp_from_epoch(market_time) or history_as_of
  if not source_label_is_history(data_source):
    return quote_checked_at_iso(quote) or history_as_of
  return history_as_of


def quote_session_state(quote: dict | None, data_source: str) -> str:
  state = str((quote or {}).get("marketState") or "REGULAR").upper()
  if source_label_is_history(data_source) and state == "CLOSED":
    return "REGULAR"
  return state


def json_get(url: str, timeout: int = 16) -> dict | list | None:
  candidates = [url]
  if "query1.finance.yahoo.com" in url:
    candidates.append(url.replace("query1.finance.yahoo.com", "query2.finance.yahoo.com"))
  elif "query2.finance.yahoo.com" in url:
    candidates.append(url.replace("query2.finance.yahoo.com", "query1.finance.yahoo.com"))

  header_sets = [
    {"User-Agent": USER_AGENT},
    {"User-Agent": USER_AGENT, "Referer": "https://finance.yahoo.com/"},
  ]

  for candidate in dict.fromkeys(candidates):
    for headers in header_sets:
      cache_key = outbound_cache_key("GET", candidate)
      hostname = (urllib.parse.urlparse(candidate).hostname or "").lower()
      ttl_seconds = outbound_ttl_for_host(hostname)
      with OUTBOUND_LOCK:
        cached = OUTBOUND_RESPONSE_CACHE.get(cache_key)
        if cached and (time.time() - cached[0]) <= ttl_seconds:
          return cached[1]
      body = secure_open_url(candidate, timeout=timeout, headers=headers)
      if body is None:
        continue
      try:
        payload = json.loads(body.decode("utf-8"))
      except json.JSONDecodeError:
        continue
      with OUTBOUND_LOCK:
        OUTBOUND_RESPONSE_CACHE[cache_key] = (time.time(), payload)
      return payload
  return None


def is_allowed_outbound_url(url: str) -> bool:
  parsed = urllib.parse.urlparse(url)
  if parsed.scheme != "https":
    return False
  hostname = (parsed.hostname or "").lower()
  return hostname in OUTBOUND_ALLOWED_HOSTS


def is_allowed_local_llm_base_url(url: str) -> bool:
  try:
    parsed = urllib.parse.urlparse(url)
    hostname = (parsed.hostname or "").lower()
    port = parsed.port
  except ValueError:
    return False
  if parsed.scheme not in {"http", "https"} or parsed.username or parsed.password:
    return False
  if hostname not in {"localhost", "127.0.0.1", "::1"}:
    return False
  if port is not None and not 1 <= port <= 65535:
    return False
  return parsed.path in {"", "/"} and not parsed.query and not parsed.fragment


def is_allowed_local_llm_url(url: str) -> bool:
  try:
    parsed = urllib.parse.urlparse(url)
    hostname = (parsed.hostname or "").lower()
    port = parsed.port
  except ValueError:
    return False
  if parsed.scheme not in {"http", "https"} or parsed.username or parsed.password:
    return False
  if hostname not in {"localhost", "127.0.0.1", "::1"}:
    return False
  if port is not None and not 1 <= port <= 65535:
    return False
  return parsed.path == "/api/generate" and not parsed.fragment


def outbound_cache_key(method: str, url: str, payload: dict | None = None) -> str:
  if payload is None:
    return f"{method}:{url}"
  return f"{method}:{url}:{json.dumps(payload, sort_keys=True, separators=(',', ':'))}"


def outbound_ttl_for_host(hostname: str) -> int:
  return OUTBOUND_CACHE_TTL.get(hostname, 120)


def outbound_min_interval_for_host(hostname: str) -> float:
  return OUTBOUND_MIN_INTERVAL.get(hostname, 1.5)


def secure_open_url(url: str, timeout: int = 12, headers: dict | None = None, data: bytes | None = None) -> bytes | None:
  if not is_allowed_outbound_url(url):
    return None
  parsed = urllib.parse.urlparse(url)
  hostname = (parsed.hostname or "").lower()
  min_interval = outbound_min_interval_for_host(hostname)
  with OUTBOUND_LOCK:
    last_seen = OUTBOUND_LAST_REQUEST_AT.get(hostname, 0.0)
    wait_time = max(0.0, min_interval - (time.time() - last_seen))
  if wait_time > 0:
    time.sleep(wait_time)
  request = urllib.request.Request(url, headers=headers or {"User-Agent": USER_AGENT}, data=data)
  try:
    with urllib.request.urlopen(request, timeout=timeout) as response:
      final_url = response.geturl()
      if not is_allowed_outbound_url(final_url):
        return None
      body = response.read()
  except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, socket.timeout, ValueError):
    return None
  finally:
    with OUTBOUND_LOCK:
      OUTBOUND_LAST_REQUEST_AT[hostname] = time.time()
  return body


def cached_get_text(url: str, timeout: int = 12, headers: dict | None = None) -> str | None:
  if not is_allowed_outbound_url(url):
    return None
  hostname = (urllib.parse.urlparse(url).hostname or "").lower()
  cache_key = outbound_cache_key("GET", url)
  ttl_seconds = outbound_ttl_for_host(hostname)
  with OUTBOUND_LOCK:
    cached = OUTBOUND_RESPONSE_CACHE.get(cache_key)
    if cached and (time.time() - cached[0]) <= ttl_seconds:
      return cached[1]
  body = secure_open_url(url, timeout=timeout, headers=headers)
  if body is None:
    return None
  text = body.decode("utf-8", errors="replace")
  with OUTBOUND_LOCK:
    OUTBOUND_RESPONSE_CACHE[cache_key] = (time.time(), text)
  return text


def text_get(url: str) -> str | None:
  return cached_get_text(
    url,
    timeout=12,
    headers={
      "User-Agent": USER_AGENT,
      "Accept": "application/rss+xml,application/xml,text/xml,text/plain,*/*",
    },
  )


def first_kb_paragraph(path: Path) -> str:
  if not path.exists():
    return ""
  text = path.read_text(encoding="utf-8").strip()
  if not text:
    return ""
  paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
  for paragraph in paragraphs:
    if not paragraph.startswith("#"):
      return re.sub(r"\s+", " ", paragraph).strip()
  return re.sub(r"\s+", " ", paragraphs[0].lstrip("# ").strip()) if paragraphs else ""


def kb_notes_bundle(region_key: str) -> dict:
  return {
    "bond": first_kb_paragraph(KB_DIR / "macro" / "bond-regimes.md"),
    "inflation": first_kb_paragraph(KB_DIR / "macro" / "inflation-regimes.md"),
    "playbook": first_kb_paragraph(KB_DIR / "playbooks" / "event-interpretation.md"),
    "regionBonds": first_kb_paragraph(KB_DIR / "regions" / region_key / "bonds.md"),
    "regionCentralBank": first_kb_paragraph(KB_DIR / "regions" / region_key / "central-bank.md"),
    "sector": first_kb_paragraph(KB_DIR / "sectors" / "rate-sensitivity.md"),
    "company": first_kb_paragraph(KB_DIR / "companies" / "watchlist-sensitivity.md"),
  }


COMPANY_NOTE_MAP = {
  "AAPL": "apple.md",
  "MSFT": "microsoft.md",
  "NVDA": "nvidia.md",
  "BHARTIARTL.NS": "bharti-airtel.md",
  "ICICIBANK.NS": "icici-bank.md",
  "GLENMARK.NS": "glenmark.md",
}


def company_note_for_symbol(symbol: str) -> str:
  filename = COMPANY_NOTE_MAP.get((symbol or "").upper())
  if not filename:
    return ""
  return first_kb_paragraph(KB_DIR / "companies" / filename)


def visible_text_lines(html_text: str) -> list[str]:
  cleaned = re.sub(r"<script\b[^>]*>.*?</script>", " ", html_text, flags=re.IGNORECASE | re.DOTALL)
  cleaned = re.sub(r"<style\b[^>]*>.*?</style>", " ", cleaned, flags=re.IGNORECASE | re.DOTALL)
  cleaned = re.sub(r"<[^>]+>", "\n", cleaned)
  cleaned = html.unescape(cleaned)
  lines = []
  for raw in cleaned.splitlines():
    text = re.sub(r"\s+", " ", raw).strip()
    if text:
      lines.append(text)
  return lines


def parse_number(text: str) -> float | None:
  cleaned = re.sub(r"[^\d.\-]", "", text or "")
  if not cleaned or cleaned in {"-", ".", "-."}:
    return None
  try:
    return float(cleaned)
  except ValueError:
    return None


def parse_compact_number(text: str) -> float | None:
  match = re.search(r"(-?[\d,.]+)\s*([KMBT])?", text or "", re.IGNORECASE)
  if not match:
    return None
  number = parse_number(match.group(1))
  if number is None:
    return None
  multiplier = {"K": 1e3, "M": 1e6, "B": 1e9, "T": 1e12}.get((match.group(2) or "").upper(), 1)
  return number * multiplier


def google_exchange_candidates(symbol: str, exchange_hint: str) -> list[str]:
  upper = symbol.upper()
  candidates = []
  candidates.extend(GOOGLE_FINANCE_INDEX_ALIASES.get(upper, []))
  if ":" in upper:
    candidates.append(upper)
  elif upper.endswith(".NS"):
    candidates.append(f"{upper[:-3]}:NSE")
  elif upper.endswith(".BO"):
    candidates.append(f"{upper[:-3]}:BOM")
  elif upper.endswith(".AX"):
    candidates.append(f"{upper[:-3]}:ASX")
  elif upper.endswith(".L"):
    candidates.append(f"{upper[:-2]}:LON")
  elif upper.endswith(".T"):
    candidates.append(f"{upper[:-2]}:TYO")
  elif upper.endswith(".DE"):
    candidates.append(f"{upper[:-3]}:ETR")
  elif upper.startswith("^"):
    return list(dict.fromkeys(candidates))
  else:
    preferred = exchange_hint.upper()
    if preferred in {"INDEXNSE", "INDEXBOM", "NSE", "BOM", "ASX", "LON", "TYO", "ETR"}:
      candidates.append(f"{upper}:{preferred}")
    elif preferred in {"NASDAQ", "NASDAQGS", "NASDAQGM", "NASDAQCM"}:
      candidates.extend([f"{upper}:NASDAQ", f"{upper}:NYSE"])
    elif preferred in {"NYSE", "NYSEARCA", "NYSEAMERICAN"}:
      candidates.extend([f"{upper}:NYSE", f"{upper}:NASDAQ"])
    else:
      candidates.extend([f"{upper}:NASDAQ", f"{upper}:NYSE"])
  return list(dict.fromkeys(candidates))


def extract_stat_after(lines: list[str], label: str, window: int = 4) -> str | None:
  lowered = label.lower()
  strict_value_pattern = re.compile(
    r"^(?:[₹$€£¥]\s*)?-?[\d,]+(?:\.\d+)?(?:\s*-\s*(?:[₹$€£¥]\s*)?[\d,]+(?:\.\d+)?)?(?:\s*[KMBT%])?(?:\s+[A-Z]{3})?$"
  )
  for index, line in enumerate(lines):
    if line.lower() == lowered:
      loose_candidate = None
      for candidate in lines[index + 1:index + 1 + window]:
        normalized = candidate.lower()
        if not candidate or normalized == lowered:
          continue
        if strict_value_pattern.match(candidate):
          return candidate
        if loose_candidate is None and len(candidate) <= 32 and re.search(r"[\d₹$€£¥%KMBT]", candidate):
          loose_candidate = candidate
      if loose_candidate:
        return loose_candidate
  return None


def extract_first_stat_after(lines: list[str], labels: list[str], window: int = 4) -> str | None:
  for label in labels:
    value = extract_stat_after(lines, label, window=window)
    if value not in (None, ""):
      return value
  return None


def parse_google_market_time(text: str | None) -> int | None:
  if not text:
    return None
  timestamp_text = str(text).split("·", 1)[0].strip()
  match = re.search(
    r"([A-Za-z]{3,9})\s+(\d{1,2}),\s+(\d{1,2}:\d{2}(?::\d{2})?\s+[AP]M)\s+GMT([+-]\d{1,2})(?::?(\d{2}))?",
    timestamp_text,
    flags=re.IGNORECASE,
  )
  if not match:
    return None
  month_text, day_text, time_text, hour_offset_text, minute_offset_text = match.groups()
  month = None
  for fmt in ("%b", "%B"):
    try:
      month = datetime.strptime(month_text[:3] if fmt == "%b" else month_text, fmt).month
      break
    except ValueError:
      continue
  if month is None:
    return None
  for fmt in ("%I:%M:%S %p", "%I:%M %p"):
    try:
      parsed_time = datetime.strptime(time_text.upper(), fmt).time()
      break
    except ValueError:
      parsed_time = None
  if parsed_time is None:
    return None
  offset_hours = int(hour_offset_text)
  offset_minutes = int(minute_offset_text or 0)
  offset_delta = timedelta(hours=offset_hours, minutes=offset_minutes if offset_hours >= 0 else -offset_minutes)
  tz = timezone(offset_delta)
  now = datetime.now(timezone.utc)
  timestamp = datetime(now.year, month, int(day_text), parsed_time.hour, parsed_time.minute, parsed_time.second, tzinfo=tz)
  if timestamp.astimezone(timezone.utc) > now + timedelta(days=2):
    timestamp = timestamp.replace(year=now.year - 1)
  return int(timestamp.timestamp())


def fetch_google_finance_quote(symbol: str, exchange_hint: str = "") -> dict:
  for google_symbol in google_exchange_candidates(symbol, exchange_hint):
    html_text = text_get(f"https://www.google.com/finance/quote/{urllib.parse.quote(google_symbol)}")
    if not html_text:
      continue
    lines = visible_text_lines(html_text)
    if not lines:
      continue

    symbol_anchor = google_symbol.replace(":", " • ")
    search_window = lines[:520]
    anchor_index = next((index for index, line in enumerate(search_window) if symbol_anchor in line or line == google_symbol), -1)
    if anchor_index < 0:
      symbol_base = google_symbol.split(":")[0]
      exchange_base = google_symbol.split(":")[1]
      anchor_index = next(
        (
          index
          for index, line in enumerate(search_window)
          if (line == symbol_base and any(candidate == google_symbol for candidate in lines[index:index + 6]))
          or (symbol_base in line and exchange_base in line)
        ),
        -1,
      )
    if anchor_index < 0:
      continue

    window = lines[anchor_index:anchor_index + 42]
    skip_name_labels = {
      "Research", "Add to list", "Area", "Line", "Candle", "Bar", "Compare", "All symbols",
      "No data", "Symbol", "Price", "Change", "% Change", "Prev Close", "Overview",
      "Earnings", "Financials", "Today", "close",
    }
    name = next(
      (
        line for line in window[1:]
        if not re.search(r"[₹$€£¥]|^[\d,]+(?:\.\d+)?$", line)
        and "·" not in line
        and line not in skip_name_labels
        and line != google_symbol
        and line != google_symbol.split(":")[0]
        and not line.startswith(("arrow_", "check_", "area_chart", "show_chart", "candlestick_", "bar_chart", "stacked_", "search"))
        and line not in {"1D", "5D", "1M", "6M", "YTD", "1Y", "5Y", "MAX"}
      ),
      fallback_meta(symbol)["name"],
    )

    price_text = next((line for line in window if re.search(r"[₹$€£¥]\s*[\d,]+(?:\.\d+)?", line)), "")
    if not price_text:
      numeric_price_pattern = re.compile(r"^\d{1,3}(?:,\d{2,3})*(?:\.\d+)?$|^\d+(?:\.\d+)?$")
      price_text = next(
        (
          line for line in window[1:14]
          if numeric_price_pattern.match(line)
          and not line.endswith("%")
        ),
        "",
      )
    if not price_text:
      continue
    price = parse_number(price_text)
    if price is None:
      continue

    timestamp_line = next((line for line in window if "·" in line and re.search(r"\b[A-Z]{3}\b", line)), "")
    currency_match = re.search(r"·\s*([A-Z]{3})\s*·", timestamp_line)
    if not currency_match:
      currency_match = re.search(r"·\s*([A-Z]{3})\s*$", timestamp_line)
    exchange_match = re.search(r"·\s*[A-Z]{3}\s*·\s*([A-Z]+)", timestamp_line)
    currency = currency_match.group(1) if currency_match else fallback_meta(symbol)["currency"]
    exchange = exchange_match.group(1) if exchange_match else exchange_hint or fallback_meta(symbol)["exchange"]
    detail_lines = lines[anchor_index:]
    change_percent = parse_number(next((line for line in window if "%" in line and re.search(r"[-+]?\d", line)), "") or "")
    change_amount = None
    for index, line in enumerate(window):
      if line == "(" and index + 2 < len(window) and window[index + 2] == ") Today":
        change_amount = parse_number(window[index + 1])
        break
    previous_close = parse_number(extract_first_stat_after(detail_lines, ["Previous close", "Prev close", "Prev Close"]) or "")
    implied_previous_close = price - change_amount if change_amount is not None else None
    if implied_previous_close is not None and implied_previous_close > 0:
      if previous_close is None or (
        change_percent is not None
        and abs(pct_change(price, previous_close) - change_percent) > 0.05
      ):
        previous_close = implied_previous_close
    avg_volume = parse_compact_number(extract_first_stat_after(detail_lines, ["Avg Volume", "Avg. vol.", "Avg vol"]) or "")
    market_volume = parse_compact_number(extract_first_stat_after(detail_lines, ["Volume"], window=2) or "")
    trailing_pe = parse_number(extract_first_stat_after(detail_lines, ["P/E ratio", "P/E Ratio"]) or "")
    market_cap = parse_compact_number(extract_first_stat_after(detail_lines, ["Market cap", "Mkt. cap", "Mkt cap"]) or "")
    day_low = parse_number(extract_first_stat_after(detail_lines, ["Low", "Day low"]) or "")
    day_high = parse_number(extract_first_stat_after(detail_lines, ["High", "Day high"]) or "")
    fifty_two_week_low = parse_number(extract_first_stat_after(detail_lines, ["52-wk low", "Year low"]) or "")
    fifty_two_week_high = parse_number(extract_first_stat_after(detail_lines, ["52-wk high", "Year high"]) or "")
    market_time = parse_google_market_time(timestamp_line)

    return {
      "symbol": symbol,
      "googleSymbol": google_symbol,
      "shortName": name,
      "longName": name,
      "regularMarketPrice": price,
      "regularMarketPreviousClose": previous_close,
      "regularMarketChangePercent": change_percent if change_percent is not None else (pct_change(price, previous_close) if previous_close else 0.0),
      "averageDailyVolume3Month": int(avg_volume or 0),
      "regularMarketVolume": int(market_volume or 0),
      "trailingPE": trailing_pe,
      "marketCap": market_cap,
      "currency": currency,
      "exchange": exchange,
      "fullExchangeName": exchange,
      "marketState": "REGULAR",
      "regularMarketTime": market_time,
      "fiftyTwoWeekLow": fifty_two_week_low,
      "fiftyTwoWeekHigh": fifty_two_week_high,
      "dayLow": day_low,
      "dayHigh": day_high,
      "quoteSource": "Google Finance",
    }
  return {}


def extract_balanced_array(text: str, start: int) -> str | None:
  depth = 0
  in_string = False
  escape = False
  for index in range(start, len(text)):
    char = text[index]
    if in_string:
      if escape:
        escape = False
      elif char == "\\":
        escape = True
      elif char == '"':
        in_string = False
      continue
    if char == '"':
      in_string = True
    elif char == "[":
      depth += 1
    elif char == "]":
      depth -= 1
      if depth == 0:
        return text[start:index + 1]
  return None


def extract_google_finance_series(html_text: str) -> list[list]:
  series = []
  for match in re.finditer(r"\[\[\[\d{4},\d{1,2},\d{1,2}", html_text):
    payload = extract_balanced_array(html_text, match.start())
    if not payload:
      continue
    try:
      data = json.loads(payload)
    except json.JSONDecodeError:
      continue
    if not isinstance(data, list) or len(data) < 2:
      continue
    if not all(isinstance(item, list) and len(item) >= 2 for item in data[:2]):
      continue
    series.append(data)
  return series


def normalize_google_finance_history(series: list, chart_range: str, time_zone: str = "UTC") -> tuple[list[float], list[str]]:
  normalized_range = chart_range.upper()
  intraday = []
  multi_day = []
  for candidate in series:
    closes = []
    timestamps = []
    dates = set()
    for item in candidate:
      if not isinstance(item, list) or len(item) < 2:
        continue
      timestamp_block = item[0]
      price_block = item[1]
      if not isinstance(timestamp_block, list) or len(timestamp_block) < 3:
        continue
      if not isinstance(price_block, list) or not price_block:
        continue
      price = price_block[0]
      if not isinstance(price, (int, float)):
        continue
      closes.append(float(price))
      timestamps.append(timestamp_from_google_block(timestamp_block, time_zone))
      dates.add(tuple(timestamp_block[:3]))
    if len(closes) < 2:
      continue
    if len(dates) <= 2:
      intraday.append((closes, timestamps))
    else:
      multi_day.append((closes, timestamps))

  def select_best(candidates: list[tuple[list[float], list[str]]]) -> tuple[list[float], list[str]]:
    if not candidates:
      return [], []
    return max(candidates, key=lambda item: len(item[0]))

  if normalized_range == "1D":
    intraday_closes, intraday_timestamps = select_best(intraday)
    if intraday_closes:
      return intraday_closes, intraday_timestamps
    return select_best(multi_day)
  if normalized_range in {"3D", "5D"}:
    base_closes, base_timestamps = select_best(multi_day)
    keep = 3 if normalized_range == "3D" else 5
    if len(base_closes) >= 2:
      return base_closes[-keep:], base_timestamps[-keep:]
    return select_best(intraday)
  if normalized_range in {"1M", "1Y"}:
    base_closes, base_timestamps = select_best(multi_day)
    if base_closes:
      return base_closes, base_timestamps
    return select_best(intraday)
  base_closes, base_timestamps = select_best(multi_day)
  if base_closes:
    return base_closes, base_timestamps
  return select_best(intraday)


def fetch_google_finance_history(symbol: str, exchange_hint: str = "", chart_range: str = "1M") -> tuple[list[float], dict]:
  for google_symbol in google_exchange_candidates(symbol, exchange_hint):
    html_text = text_get(f"https://www.google.com/finance/quote/{urllib.parse.quote(google_symbol)}")
    if not html_text:
      continue
    series = extract_google_finance_series(html_text)
    time_zone = google_finance_timezone(google_symbol, exchange_hint)
    closes, timestamps = normalize_google_finance_history(series, chart_range, time_zone)
    if len(closes) >= 2:
      payload = {
        "historySource": "Google Finance Page",
        "googleSymbol": google_symbol,
        "timezone": time_zone,
      }
      if timestamps and len(timestamps) == len(closes):
        payload["timestamps"] = timestamps
      return closes, payload
  return [], {}


def stooq_symbol_candidates(symbol: str, exchange_hint: str = "") -> list[str]:
  upper = (symbol or "").upper()
  if upper.startswith("^") or upper.endswith("=F") or upper.endswith("-USD"):
    return []
  if upper.endswith(".NS") or upper.endswith(".BO"):
    return []
  base = upper.split(".")[0].lower()
  candidates = []
  preferred = (exchange_hint or fallback_meta(upper).get("exchange", "")).upper()
  if preferred in {"NASDAQ", "NASDAQGS", "NASDAQGM", "NASDAQCM"}:
    candidates.extend([f"{base}.us", f"{base}.u"])
  elif preferred in {"NYSE", "NYSEARCA", "NYSEAMERICAN", "US"}:
    candidates.extend([f"{base}.us"])
  else:
    candidates.extend([f"{base}.us"])
  return list(dict.fromkeys(candidates))


def fetch_stooq_history(symbol: str, exchange_hint: str = "", chart_range: str = "1M") -> tuple[list[float], dict]:
  keep_map = {"1D": 2, "3D": 3, "5D": 5, "1M": 31, "1Y": 370}
  keep = keep_map.get(chart_range.upper(), 31)
  for stooq_symbol in stooq_symbol_candidates(symbol, exchange_hint):
    url = f"https://stooq.com/q/d/l/?s={urllib.parse.quote(stooq_symbol)}&i=d"
    csv_text = text_get(url)
    if not csv_text:
      continue
    rows = csv_text.splitlines()
    if len(rows) < 3:
      continue
    closes = []
    timestamps = []
    volumes = []
    for row in rows[1:]:
      parts = row.split(",")
      if len(parts) < 5:
        continue
      date_text = parts[0].strip()
      close_text = parts[4].strip()
      volume_text = parts[5].strip() if len(parts) > 5 else ""
      try:
        close_value = float(close_text)
      except ValueError:
        continue
      closes.append(close_value)
      timestamps.append(f"{date_text}T00:00:00+00:00")
      try:
        volumes.append(float(volume_text))
      except ValueError:
        pass
    if len(closes) >= 2:
      payload = {
        "historySource": "Stooq CSV",
        "stooqSymbol": stooq_symbol,
        "timestamps": timestamps[-keep:],
      }
      if len(volumes) == len(closes):
        payload["volumes"] = volumes[-keep:]
      return closes[-keep:], payload
  return [], {}


def fetch_alpha_vantage_history(symbol: str, api_key: str, chart_range: str = "1M") -> tuple[list[float], dict]:
  normalized = chart_range.upper()
  query = urllib.parse.urlencode(
    {
      "function": "TIME_SERIES_DAILY_ADJUSTED",
      "symbol": symbol,
      "outputsize": "compact" if normalized != "1Y" else "full",
      "apikey": api_key,
    }
  )
  payload = json_get(f"https://www.alphavantage.co/query?{query}")
  series = (payload or {}).get("Time Series (Daily)") or {}
  if not isinstance(series, dict) or not series:
    return [], {}
  keep_map = {"1D": 2, "3D": 3, "5D": 5, "1M": 31, "1Y": 370}
  keep = keep_map.get(normalized, 31)
  rows = sorted(series.items())[-keep:]
  closes = []
  timestamps = []
  volumes = []
  for date_key, fields in rows:
    try:
      closes.append(float(fields.get("4. close")))
      timestamps.append(f"{date_key}T00:00:00+00:00")
      volumes.append(float(fields.get("6. volume")))
    except (TypeError, ValueError):
      continue
  if len(closes) >= 2:
    return closes, {
      "historySource": "Alpha Vantage Daily Adjusted",
      "timestamps": timestamps,
      "volumes": volumes if len(volumes) == len(closes) else [],
    }
  return [], {}


def cached_live_quotes(symbols: list[str], max_age: int = QUOTE_CACHE_TTL) -> tuple[dict[str, dict], dict[str, dict]]:
  now = time.time()
  fresh = {}
  stale = {}
  with _QUOTE_CACHE_LOCK:
    for symbol in symbols:
      entry = _quote_cache.get(symbol.upper())
      if not entry:
        continue
      age = now - float(entry.get("ts", 0))
      quote = entry.get("quote") or {}
      if not quote:
        continue
      if age <= max_age:
        fresh[symbol.upper()] = quote
      elif age <= QUOTE_STALE_TTL:
        stale[symbol.upper()] = quote
  return fresh, stale


def save_live_quote_cache(quotes: dict[str, dict]) -> None:
  if not quotes:
    return
  now = time.time()
  with _QUOTE_CACHE_LOCK:
    for symbol, quote in quotes.items():
      if quote:
        _quote_cache[symbol.upper()] = {"quote": quote, "ts": now}


def fetch_live_quotes_from_providers(symbols: list[str]) -> dict[str, dict]:
  if _SERVER_STOPPING.is_set():
    return {}
  unresolved = [symbol.upper() for symbol in symbols if symbol]
  if not unresolved:
    return {}
  resolved: dict[str, dict] = {}
  provisional: dict[str, dict] = {}
  chain = build_live_quote_provider_chain(unresolved)
  source_count = len(chain)
  provider_ranks = {provider["id"]: rank for rank, provider in enumerate(chain, start=1)}

  def merge_provider_quotes(provider: dict, provider_quotes: dict[str, dict]) -> None:
    usable = {}
    for symbol, quote in (provider_quotes or {}).items():
      normalized_symbol = symbol.upper()
      if not quote_is_usable(quote):
        continue
      annotated = annotate_quote_source(
        quote,
        provider,
        rank=provider_ranks.get(provider["id"], source_count),
        source_count=source_count,
      )
      if normalized_symbol in resolved:
        if quote_candidate_score(normalized_symbol, annotated) > quote_candidate_score(normalized_symbol, resolved[normalized_symbol]):
          resolved[normalized_symbol] = annotated
          mark_quote_provider_success(provider["id"])
        continue
      if quote_is_live_edge(normalized_symbol, annotated):
        usable[normalized_symbol] = annotated
      elif quote_is_better_provisional(normalized_symbol, annotated, provisional.get(normalized_symbol)):
        provisional[normalized_symbol] = annotated
    if usable:
      resolved.update(usable)
      mark_quote_provider_success(provider["id"])

  def fetch_provider_bounded(provider: dict, pending_symbols: list[str]) -> dict[str, dict]:
    if not pending_symbols or not quote_provider_available(provider["id"]):
      return {}
    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(provider["fetch"], pending_symbols)
    try:
      return future.result(timeout=float(provider.get("timeoutSeconds") or QUOTE_PROVIDER_TIMEOUT_SECONDS)) or {}
    except Exception:
      future.cancel()
      mark_quote_provider_failure(provider["id"])
      return {}
    finally:
      executor.shutdown(wait=False, cancel_futures=True)

  sequential = [provider for provider in chain if not provider.get("parallel")]
  for provider in sequential:
    pending_symbols = [symbol for symbol in unresolved if symbol not in resolved]
    if not pending_symbols:
      break
    merge_provider_quotes(provider, fetch_provider_bounded(provider, pending_symbols))
    if all(symbol in resolved for symbol in unresolved):
      return {**provisional, **resolved}

  # Vendor-rotated subset first (1 provider per vendor), then expand to the
  # full chain only for symbols still unresolved. This caps per-request load
  # on any single vendor while keeping the long tail of fallbacks available.
  parallel_pool = [provider for provider in chain if provider.get("parallel")]
  rotated_subset = select_rotated_quote_chain(parallel_pool)
  used_provider_ids: set[str] = set()

  def run_parallel_wave(wave_providers: list[dict]) -> None:
    """Dispatch one parallel wave; mutates outer `resolved` / `provisional`."""
    healthy = [provider for provider in wave_providers if quote_provider_available(provider["id"]) and provider["id"] not in used_provider_ids]
    if not healthy or _SERVER_STOPPING.is_set():
      return
    remaining_symbols = [symbol for symbol in unresolved if symbol not in resolved]
    if not remaining_symbols:
      return
    for provider in healthy:
      used_provider_ids.add(provider["id"])
    executor = ThreadPoolExecutor(max_workers=min(8, len(healthy)))
    try:
      futures = {executor.submit(provider["fetch"], remaining_symbols): provider for provider in healthy}
    except RuntimeError:
      executor.shutdown(wait=False, cancel_futures=True)
      return
    pending_futures = set(futures)
    deadline = time.time() + QUOTE_PROVIDER_PARALLEL_TIMEOUT_SECONDS

    def process_done_futures(done_futures) -> None:
      for future in done_futures:
        provider = futures[future]
        try:
          provider_quotes = future.result() or {}
        except Exception:
          mark_quote_provider_failure(provider["id"])
          continue
        merge_provider_quotes(provider, provider_quotes)

    try:
      while pending_futures and time.time() < deadline:
        done, pending_futures = wait(pending_futures, timeout=max(0.1, deadline - time.time()), return_when=FIRST_COMPLETED)
        if not done:
          break
        process_done_futures(done)
        if all(symbol in resolved or symbol in provisional for symbol in unresolved):
          extra_done, pending_futures = wait(pending_futures, timeout=0.35)
          process_done_futures(extra_done)
          break
      for future in pending_futures:
        provider = futures[future]
        future.cancel()
        mark_quote_provider_failure(provider["id"])
    finally:
      executor.shutdown(wait=False, cancel_futures=True)

  run_parallel_wave(rotated_subset)
  if not all(symbol in resolved for symbol in unresolved) and not _SERVER_STOPPING.is_set():
    run_parallel_wave(parallel_pool)

  return {**provisional, **resolved}


def refresh_live_quote_cache_async(symbols: list[str]) -> None:
  cleaned = [symbol.upper() for symbol in symbols if symbol]
  if not cleaned or not _QUOTE_FETCH_LOCK.acquire(blocking=False):
    return

  def worker() -> None:
    try:
      if _SERVER_STOPPING.is_set():
        return
      fresh, _ = cached_live_quotes(cleaned)
      missing = [symbol for symbol in cleaned if symbol not in fresh]
      if missing and not _SERVER_STOPPING.is_set():
        save_live_quote_cache(fetch_live_quotes_from_providers(missing))
    except RuntimeError:
      if not _SERVER_STOPPING.is_set():
        raise
    finally:
      _QUOTE_FETCH_LOCK.release()

  threading.Thread(target=worker, name="quote-cache-refresh", daemon=True).start()


def fetch_live_quotes(symbols: list[str], fast: bool = False) -> dict[str, dict]:
  cleaned = [symbol.upper() for symbol in symbols if symbol]
  if not cleaned:
    return {}
  fresh, stale = cached_live_quotes(cleaned)
  missing = [symbol for symbol in cleaned if symbol not in fresh]
  if not missing:
    return fresh
  if fast:
    refresh_live_quote_cache_async(missing)
    return {**stale, **fresh}

  acquired = _QUOTE_FETCH_LOCK.acquire(blocking=not stale)
  if not acquired:
    return {**stale, **fresh}
  try:
    # Another request may have refreshed the cache while this request waited.
    fresh, stale = cached_live_quotes(cleaned)
    missing = [symbol for symbol in cleaned if symbol not in fresh]
    if not missing:
      return fresh

    primary = fetch_live_quotes_from_providers(missing)
    save_live_quote_cache(primary)
    return {**stale, **primary, **fresh}
  finally:
    _QUOTE_FETCH_LOCK.release()


def epoch_from_iso(value: str | None) -> int | None:
  if not value:
    return None
  try:
    timestamp = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
  except ValueError:
    return None
  if timestamp.tzinfo is None:
    timestamp = timestamp.replace(tzinfo=timezone.utc)
  return int(timestamp.timestamp())


def fetch_history_derived_quote(symbol: str, allow_live_refresh: bool = False) -> dict:
  history, meta = build_history(symbol, "1M", allow_live_refresh=allow_live_refresh)
  if len(history) < 2:
    return {}
  fallback = fallback_meta(symbol)
  timestamps = meta.get("timestamps") or []
  market_time = epoch_from_iso(timestamps[-1] if timestamps else None)
  source = meta.get("historySource") or "History-derived"
  return {
    "symbol": symbol,
    "shortName": fallback["name"],
    "longName": fallback["name"],
    "regularMarketPrice": float(history[-1]),
    "regularMarketPreviousClose": float(history[-2]),
    "regularMarketChangePercent": pct_change(float(history[-1]), float(history[-2])),
    "regularMarketVolume": int((meta.get("volumes") or [0])[-1] if meta.get("volumes") else 0),
    "averageDailyVolume3Month": 0,
    "currency": meta.get("currency") or fallback["currency"],
    "exchange": meta.get("exchangeName") or fallback["exchange"],
    "fullExchangeName": meta.get("fullExchangeName") or meta.get("exchangeName") or fallback["exchange"],
    "marketState": "CLOSED",
    "regularMarketTime": market_time,
    "quoteSource": source if "history" in source.lower() else f"{source} history",
    "historyCacheState": meta.get("historyCacheState"),
  }


def fetch_yahoo_chart_quote(symbol: str) -> dict:
  for range_value, interval in (("1d", "1m"), ("5d", "1d")):
    chart = fetch_yahoo_chart(symbol, range_value=range_value, interval=interval)
    meta = (chart or {}).get("meta") or {}
    price = meta.get("regularMarketPrice")
    previous_close = meta.get("previousClose") or meta.get("chartPreviousClose")
    if price is None:
      continue
    return {
      "symbol": symbol,
      "shortName": meta.get("shortName") or meta.get("longName") or fallback_meta(symbol)["name"],
      "longName": meta.get("longName") or meta.get("shortName") or fallback_meta(symbol)["name"],
      "regularMarketPrice": price,
      "regularMarketPreviousClose": previous_close,
      "regularMarketChangePercent": pct_change(float(price), float(previous_close)) if previous_close else 0.0,
      "regularMarketVolume": meta.get("regularMarketVolume") or 0,
      "averageDailyVolume3Month": 0,
      "currency": meta.get("currency") or fallback_meta(symbol)["currency"],
      "exchange": meta.get("exchangeName") or fallback_meta(symbol)["exchange"],
      "fullExchangeName": meta.get("fullExchangeName") or meta.get("exchangeName") or fallback_meta(symbol)["exchange"],
      "marketState": meta.get("marketState") or "REGULAR",
      "regularMarketTime": meta.get("regularMarketTime"),
      "fiftyTwoWeekLow": meta.get("fiftyTwoWeekLow"),
      "fiftyTwoWeekHigh": meta.get("fiftyTwoWeekHigh"),
      "dayLow": meta.get("regularMarketDayLow"),
      "dayHigh": meta.get("regularMarketDayHigh"),
      "quoteSource": "Yahoo Chart",
    }
  return {}


def quote_is_usable(quote: dict | None) -> bool:
  if not quote:
    return False
  try:
    price = float(quote.get("regularMarketPrice"))
  except (TypeError, ValueError):
    return False
  return math.isfinite(price) and price > 0


def quote_market_time_iso(quote: dict | None) -> str | None:
  if not quote:
    return None
  market_time = quote.get("regularMarketTime")
  if market_time:
    try:
      return datetime.fromtimestamp(float(market_time), tz=timezone.utc).isoformat()
    except (TypeError, ValueError, OSError):
      return None
  return None


def timestamp_from_epoch(value) -> str:
  try:
    return datetime.fromtimestamp(float(value), tz=timezone.utc).isoformat()
  except (TypeError, ValueError, OSError):
    return ""


def quote_age_seconds(quote: dict | None) -> float | None:
  as_of = quote_market_time_iso(quote)
  if not as_of:
    return None
  try:
    timestamp = datetime.fromisoformat(str(as_of).replace("Z", "+00:00"))
  except ValueError:
    return None
  if timestamp.tzinfo is None:
    timestamp = timestamp.replace(tzinfo=timezone.utc)
  return max(0.0, (datetime.now(timezone.utc) - timestamp.astimezone(timezone.utc)).total_seconds())


def quote_source_is_history(quote: dict | None) -> bool:
  if not quote:
    return False
  source_type = str(quote.get("quoteSourceType") or "").lower()
  source = str(quote.get("quoteSource") or "").lower()
  return source_type == "history" or any(label in source for label in {"history", "historical", "cache", "derived", "daily csv"})


def quote_price_differs_from_cache(symbol: str, quote: dict) -> bool:
  try:
    next_price = float(quote.get("regularMarketPrice"))
  except (TypeError, ValueError):
    return False
  with _QUOTE_CACHE_LOCK:
    entry = _quote_cache.get(symbol.upper()) or {}
    cached_quote = entry.get("quote") or {}
  if not cached_quote:
    return False
  try:
    cached_price = float(cached_quote.get("regularMarketPrice"))
  except (TypeError, ValueError):
    return True
  if not math.isfinite(cached_price):
    return True
  return abs(next_price - cached_price) > max(abs(cached_price) * 0.00001, 0.0001)


def quote_is_live_edge(symbol: str, quote: dict) -> bool:
  if quote_source_is_history(quote):
    return False
  if quote_price_differs_from_cache(symbol, quote):
    return True
  age = quote_age_seconds(quote)
  return age is not None and age <= LIVE_QUOTE_EDGE_SECONDS


def quote_candidate_score(symbol: str, quote: dict) -> tuple:
  age = quote_age_seconds(quote)
  live_type = 0 if quote_source_is_history(quote) else 1
  changed = 1 if quote_price_differs_from_cache(symbol, quote) else 0
  timestamp_score = -age if age is not None else -10**9
  rank_score = -int(quote.get("quoteSourceRank") or 999)
  return (live_type, changed, timestamp_score, rank_score)


def quote_is_better_provisional(symbol: str, quote: dict, current: dict | None) -> bool:
  if not current:
    return True
  return quote_candidate_score(symbol, quote) > quote_candidate_score(symbol, current)


def annotate_quote_source(quote: dict, provider: dict, rank: int, source_count: int) -> dict:
  annotated = dict(quote)
  label = provider.get("label") or provider.get("id") or "Quote provider"
  annotated["quoteSource"] = label
  annotated["quoteProviderId"] = provider.get("id")
  annotated["quoteSourceRank"] = rank
  annotated["quoteSourceCount"] = source_count
  annotated["quoteSourceType"] = provider.get("type", "live")
  annotated["quoteSourceCheckedAt"] = datetime.now(timezone.utc).isoformat()
  return annotated


def quote_provider_available(provider_id: str) -> bool:
  with _QUOTE_PROVIDER_HEALTH_LOCK:
    state = _QUOTE_PROVIDER_HEALTH.get(provider_id) or {}
    return time.time() >= float(state.get("nextRetryAt", 0.0))


def mark_quote_provider_success(provider_id: str) -> None:
  with _QUOTE_PROVIDER_HEALTH_LOCK:
    prior = _QUOTE_PROVIDER_HEALTH.get(provider_id) or {}
    _QUOTE_PROVIDER_HEALTH[provider_id] = {
      "failures": 0,
      "nextRetryAt": 0.0,
      "lastSuccessAt": time.time(),
      "lastFailureAt": prior.get("lastFailureAt"),
    }


def mark_quote_provider_failure(provider_id: str) -> None:
  with _QUOTE_PROVIDER_HEALTH_LOCK:
    prior = _QUOTE_PROVIDER_HEALTH.get(provider_id) or {}
    failures = int(prior.get("failures") or 0) + 1
    cooldown = min(QUOTE_PROVIDER_FAILURE_COOLDOWN * failures, 5 * 60)
    _QUOTE_PROVIDER_HEALTH[provider_id] = {
      "failures": failures,
      "nextRetryAt": time.time() + cooldown,
      "lastSuccessAt": prior.get("lastSuccessAt"),
      "lastFailureAt": time.time(),
    }


def quote_provider_status() -> list[dict]:
  providers = build_live_quote_provider_chain([])
  with _QUOTE_PROVIDER_HEALTH_LOCK:
    health = dict(_QUOTE_PROVIDER_HEALTH)
  now = time.time()
  status = []
  for provider in providers:
    state = health.get(provider["id"]) or {}
    next_retry_at = float(state.get("nextRetryAt") or 0.0)
    status.append(
      {
        "id": provider["id"],
        "label": provider.get("label") or provider["id"],
        "type": provider.get("type", "live"),
        "mode": "parallel" if provider.get("parallel") else "sequential",
        "status": "cooldown" if next_retry_at > now else "available",
        "failures": int(state.get("failures") or 0),
        "lastSuccessAt": timestamp_from_epoch(state.get("lastSuccessAt")) if state.get("lastSuccessAt") else "",
        "lastFailureAt": timestamp_from_epoch(state.get("lastFailureAt")) if state.get("lastFailureAt") else "",
        "nextRetryAt": timestamp_from_epoch(next_retry_at) if next_retry_at > now else "",
      }
    )
  return status


def fetch_yahoo_quotes_from_host(symbols: list[str], hostname: str, label: str) -> dict[str, dict]:
  cleaned = [symbol for symbol in symbols if symbol]
  if not cleaned:
    return {}
  quoted = urllib.parse.quote(",".join(cleaned))
  payload = json_get(f"https://{hostname}/v7/finance/quote?symbols={quoted}", timeout=6)
  results = {}
  quote_response = (payload or {}).get("quoteResponse", {})
  for item in quote_response.get("result", []):
    symbol = item.get("symbol")
    if symbol:
      quote = dict(item)
      quote["quoteSource"] = label
      results[symbol.upper()] = quote
  return results


def fetch_yahoo_chart_from_host(symbol: str, hostname: str, range_value: str = "1d", interval: str = "1m") -> dict | None:
  quoted = urllib.parse.quote(symbol)
  payload = json_get(
    f"https://{hostname}/v8/finance/chart/{quoted}?range={range_value}&interval={interval}&includePrePost=false&events=div%2Csplits",
    timeout=8,
  )
  chart = (payload or {}).get("chart", {})
  results = chart.get("result", [])
  return results[0] if results else None


def quote_from_yahoo_chart_payload(symbol: str, chart: dict | None, label: str) -> dict:
  meta = (chart or {}).get("meta") or {}
  price = meta.get("regularMarketPrice")
  previous_close = meta.get("previousClose") or meta.get("chartPreviousClose")
  if price is None:
    return {}
  fallback = fallback_meta(symbol)
  return {
    "symbol": symbol,
    "shortName": meta.get("shortName") or meta.get("longName") or fallback["name"],
    "longName": meta.get("longName") or meta.get("shortName") or fallback["name"],
    "regularMarketPrice": price,
    "regularMarketPreviousClose": previous_close,
    "regularMarketChangePercent": pct_change(float(price), float(previous_close)) if previous_close else 0.0,
    "regularMarketVolume": meta.get("regularMarketVolume") or 0,
    "averageDailyVolume3Month": 0,
    "currency": meta.get("currency") or fallback["currency"],
    "exchange": meta.get("exchangeName") or fallback["exchange"],
    "fullExchangeName": meta.get("fullExchangeName") or meta.get("exchangeName") or fallback["exchange"],
    "marketState": meta.get("marketState") or "REGULAR",
    "regularMarketTime": meta.get("regularMarketTime"),
    "fiftyTwoWeekLow": meta.get("fiftyTwoWeekLow"),
    "fiftyTwoWeekHigh": meta.get("fiftyTwoWeekHigh"),
    "dayLow": meta.get("regularMarketDayLow"),
    "dayHigh": meta.get("regularMarketDayHigh"),
    "quoteSource": label,
  }


def fetch_yahoo_chart_quotes_from_host(symbols: list[str], hostname: str, label: str) -> dict[str, dict]:
  results = {}
  for symbol in symbols:
    for range_value, interval in (("1d", "1m"), ("5d", "1d")):
      quote = quote_from_yahoo_chart_payload(
        symbol,
        fetch_yahoo_chart_from_host(symbol, hostname, range_value=range_value, interval=interval),
        label,
      )
      if quote:
        results[symbol.upper()] = quote
        break
  return results


def fetch_google_finance_quotes_provider(symbols: list[str]) -> dict[str, dict]:
  results = {}
  with ThreadPoolExecutor(max_workers=min(8, max(1, len(symbols)))) as executor:
    futures = {
      executor.submit(fetch_google_finance_quote, symbol, fallback_meta(symbol).get("exchange", "")): symbol
      for symbol in symbols
    }
    for future, symbol in futures.items():
      try:
        quote = future.result()
      except Exception:
        quote = {}
      if quote:
        results[symbol.upper()] = quote
  return results


def fetch_yahoo_search_quote_provider(symbols: list[str]) -> dict[str, dict]:
  results = {}
  for symbol in symbols:
    quoted = urllib.parse.quote(symbol)
    payload = json_get(f"https://query1.finance.yahoo.com/v1/finance/search?q={quoted}&quotesCount=8&newsCount=0", timeout=6)
    for item in (payload or {}).get("quotes", []):
      if (item.get("symbol") or "").upper() != symbol.upper():
        continue
      quote = {
        "symbol": symbol,
        "shortName": item.get("shortname") or item.get("longname") or fallback_meta(symbol)["name"],
        "longName": item.get("longname") or item.get("shortname") or fallback_meta(symbol)["name"],
        "regularMarketPrice": item.get("regularMarketPrice"),
        "regularMarketPreviousClose": item.get("regularMarketPreviousClose"),
        "regularMarketChangePercent": item.get("regularMarketChangePercent") or item.get("regularMarketPercentChange"),
        "regularMarketVolume": item.get("regularMarketVolume") or 0,
        "averageDailyVolume3Month": 0,
        "currency": item.get("currency") or fallback_meta(symbol)["currency"],
        "exchange": item.get("exchange") or item.get("exchDisp") or fallback_meta(symbol)["exchange"],
        "fullExchangeName": item.get("exchDisp") or item.get("exchange") or fallback_meta(symbol)["exchange"],
        "marketState": item.get("marketState") or "REGULAR",
        "regularMarketTime": item.get("regularMarketTime"),
        "quoteSource": "Yahoo Finance Search",
      }
      if quote_is_usable(quote):
        results[symbol.upper()] = quote
        break
  return results


def fetch_yahoo_summary_quote_provider(symbols: list[str]) -> dict[str, dict]:
  results = {}
  for symbol in symbols:
    quoted = urllib.parse.quote(symbol)
    payload = json_get(
      f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{quoted}?modules=price,summaryDetail",
      timeout=8,
    )
    result = (((payload or {}).get("quoteSummary") or {}).get("result") or [{}])[0]
    price = result.get("price") or {}
    detail = result.get("summaryDetail") or {}
    raw_price = (price.get("regularMarketPrice") or {}).get("raw")
    previous_close = (price.get("regularMarketPreviousClose") or detail.get("previousClose") or {}).get("raw")
    quote = {
      "symbol": symbol,
      "shortName": price.get("shortName") or price.get("longName") or fallback_meta(symbol)["name"],
      "longName": price.get("longName") or price.get("shortName") or fallback_meta(symbol)["name"],
      "regularMarketPrice": raw_price,
      "regularMarketPreviousClose": previous_close,
      "regularMarketChangePercent": (price.get("regularMarketChangePercent") or {}).get("raw"),
      "regularMarketVolume": (price.get("regularMarketVolume") or {}).get("raw") or 0,
      "averageDailyVolume3Month": (detail.get("averageVolume") or {}).get("raw") or 0,
      "currency": price.get("currency") or fallback_meta(symbol)["currency"],
      "exchange": price.get("exchangeName") or fallback_meta(symbol)["exchange"],
      "fullExchangeName": price.get("exchangeName") or fallback_meta(symbol)["exchange"],
      "marketState": price.get("marketState") or "REGULAR",
      "regularMarketTime": (price.get("regularMarketTime") or {}).get("raw"),
      "quoteSource": "Yahoo Finance Summary",
    }
    if quote_is_usable(quote):
      results[symbol.upper()] = quote
  return results


def fetch_yahoo_web_quote_provider(symbols: list[str]) -> dict[str, dict]:
  results = {}
  for symbol in symbols:
    html_text = text_get(f"https://finance.yahoo.com/quote/{urllib.parse.quote(symbol)}")
    if not html_text:
      continue
    def raw_number(field: str) -> float | None:
      match = re.search(rf'"{re.escape(field)}"\s*:\s*\{{\s*"raw"\s*:\s*(-?\d+(?:\.\d+)?)', html_text)
      return float(match.group(1)) if match else None
    price = raw_number("regularMarketPrice") or raw_number("postMarketPrice")
    previous_close = raw_number("regularMarketPreviousClose")
    quote = {
      "symbol": symbol,
      "shortName": fallback_meta(symbol)["name"],
      "longName": fallback_meta(symbol)["name"],
      "regularMarketPrice": price,
      "regularMarketPreviousClose": previous_close,
      "regularMarketChangePercent": raw_number("regularMarketChangePercent") or (pct_change(price, previous_close) if price and previous_close else 0.0),
      "regularMarketVolume": int(raw_number("regularMarketVolume") or 0),
      "averageDailyVolume3Month": int(raw_number("averageDailyVolume3Month") or 0),
      "currency": fallback_meta(symbol)["currency"],
      "exchange": fallback_meta(symbol)["exchange"],
      "fullExchangeName": fallback_meta(symbol)["exchange"],
      "marketState": "REGULAR",
      "regularMarketTime": int(raw_number("regularMarketTime") or 0) or None,
      "quoteSource": "Yahoo Finance Web",
    }
    if quote_is_usable(quote):
      results[symbol.upper()] = quote
  return results


def fetch_stooq_quote_provider(symbols: list[str]) -> dict[str, dict]:
  results = {}
  for symbol in symbols:
    closes, meta = fetch_stooq_history(symbol, fallback_meta(symbol).get("exchange", ""), "5D")
    if len(closes) < 2:
      continue
    fallback = fallback_meta(symbol)
    timestamps = meta.get("timestamps") or []
    quote = {
      "symbol": symbol,
      "shortName": fallback["name"],
      "longName": fallback["name"],
      "regularMarketPrice": float(closes[-1]),
      "regularMarketPreviousClose": float(closes[-2]),
      "regularMarketChangePercent": pct_change(float(closes[-1]), float(closes[-2])),
      "regularMarketVolume": int((meta.get("volumes") or [0])[-1] if meta.get("volumes") else 0),
      "averageDailyVolume3Month": 0,
      "currency": fallback["currency"],
      "exchange": fallback["exchange"],
      "fullExchangeName": fallback["exchange"],
      "marketState": "CLOSED",
      "regularMarketTime": epoch_from_iso(timestamps[-1] if timestamps else None),
      "quoteSource": "Stooq Daily CSV",
    }
    results[symbol.upper()] = quote
  return results


def fetch_alpha_vantage_global_quote_provider(symbols: list[str]) -> dict[str, dict]:
  api_key = load_config().get("alphaVantageApiKey", "").strip()
  if not api_key:
    return {}
  results = {}
  for symbol in symbols:
    query = urllib.parse.urlencode({"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": api_key})
    payload = json_get(f"https://www.alphavantage.co/query?{query}", timeout=12)
    fields = (payload or {}).get("Global Quote") or {}
    price = parse_number(fields.get("05. price") or "")
    previous_close = parse_number(fields.get("08. previous close") or "")
    change_percent = parse_number(fields.get("10. change percent") or "")
    volume = parse_number(fields.get("06. volume") or "")
    fallback = fallback_meta(symbol)
    quote = {
      "symbol": symbol,
      "shortName": fallback["name"],
      "longName": fallback["name"],
      "regularMarketPrice": price,
      "regularMarketPreviousClose": previous_close,
      "regularMarketChangePercent": change_percent if change_percent is not None else (pct_change(price, previous_close) if price and previous_close else 0.0),
      "regularMarketVolume": int(volume or 0),
      "averageDailyVolume3Month": 0,
      "currency": fallback["currency"],
      "exchange": fallback["exchange"],
      "fullExchangeName": fallback["exchange"],
      "marketState": "REGULAR",
      "regularMarketTime": epoch_from_iso(f"{fields.get('07. latest trading day')}T00:00:00+00:00") if fields.get("07. latest trading day") else None,
      "quoteSource": "Alpha Vantage Global Quote",
    }
    if quote_is_usable(quote):
      results[symbol.upper()] = quote
  return results


def fetch_alpha_vantage_daily_quote_provider(symbols: list[str]) -> dict[str, dict]:
  api_key = load_config().get("alphaVantageApiKey", "").strip()
  if not api_key:
    return {}
  results = {}
  for symbol in symbols:
    closes, meta = fetch_alpha_vantage_history(symbol, api_key, "5D")
    if len(closes) < 2:
      continue
    fallback = fallback_meta(symbol)
    timestamps = meta.get("timestamps") or []
    volumes = meta.get("volumes") or []
    quote = {
      "symbol": symbol,
      "shortName": fallback["name"],
      "longName": fallback["name"],
      "regularMarketPrice": float(closes[-1]),
      "regularMarketPreviousClose": float(closes[-2]),
      "regularMarketChangePercent": pct_change(float(closes[-1]), float(closes[-2])),
      "regularMarketVolume": int(volumes[-1] if len(volumes) == len(closes) else 0),
      "averageDailyVolume3Month": 0,
      "currency": fallback["currency"],
      "exchange": fallback["exchange"],
      "fullExchangeName": fallback["exchange"],
      "marketState": "CLOSED",
      "regularMarketTime": epoch_from_iso(timestamps[-1] if timestamps else None),
      "quoteSource": "Alpha Vantage Daily Adjusted",
    }
    results[symbol.upper()] = quote
  return results


def fetch_history_cache_quote_provider(symbols: list[str]) -> dict[str, dict]:
  results = {}
  for symbol in symbols:
    quote = fetch_history_derived_quote(symbol, allow_live_refresh=False)
    if quote:
      results[symbol.upper()] = quote
  return results


def quote_chain_prefers_google(symbols: list[str] | None = None) -> bool:
  if not symbols:
    return False
  india_like = 0
  for symbol in symbols:
    upper = (symbol or "").upper()
    if upper.endswith((".NS", ".BO")) or upper.startswith(("^NSE", "^BSE", "^CNX", "^NIF")):
      india_like += 1
  return india_like > 0 and india_like == len([symbol for symbol in symbols if symbol])


def build_live_quote_provider_chain(symbols: list[str] | None = None) -> list[dict]:
  providers = [
    {"id": "yahoo_quote_primary", "label": "Yahoo Finance Quote", "type": "live", "parallel": True, "timeoutSeconds": 4, "fetch": fetch_yahoo_quotes},
    {"id": "google_finance_page", "label": "Google Finance", "type": "live", "parallel": True, "timeoutSeconds": 5, "fetch": fetch_google_finance_quotes_provider},
    {"id": "yahoo_quote_secondary", "label": "Yahoo Finance Quote (secondary)", "type": "live", "parallel": True, "timeoutSeconds": 4, "fetch": lambda symbols: fetch_yahoo_quotes_from_host(symbols, "query2.finance.yahoo.com", "Yahoo Finance Quote (secondary)")},
    {"id": "yahoo_chart_primary", "label": "Yahoo Chart Live Edge", "type": "live", "parallel": True, "timeoutSeconds": 5, "fetch": lambda symbols: fetch_yahoo_chart_quotes_from_host(symbols, "query1.finance.yahoo.com", "Yahoo Chart Live Edge")},
    {"id": "yahoo_chart_secondary", "label": "Yahoo Chart Live Edge (secondary)", "type": "live", "parallel": True, "timeoutSeconds": 5, "fetch": lambda symbols: fetch_yahoo_chart_quotes_from_host(symbols, "query2.finance.yahoo.com", "Yahoo Chart Live Edge (secondary)")},
    {"id": "yahoo_search", "label": "Yahoo Finance Search", "type": "live", "parallel": True, "timeoutSeconds": 5, "fetch": fetch_yahoo_search_quote_provider},
    {"id": "yahoo_summary", "label": "Yahoo Finance Summary", "type": "live", "parallel": True, "timeoutSeconds": 6, "fetch": fetch_yahoo_summary_quote_provider},
    {"id": "yahoo_web", "label": "Yahoo Finance Web", "type": "live", "parallel": True, "timeoutSeconds": 6, "fetch": fetch_yahoo_web_quote_provider},
    {"id": "stooq_daily", "label": "Stooq Daily CSV", "type": "history", "parallel": True, "timeoutSeconds": 6, "fetch": fetch_stooq_quote_provider},
    {"id": "alpha_vantage_global", "label": "Alpha Vantage Global Quote", "type": "live", "parallel": True, "timeoutSeconds": 7, "fetch": fetch_alpha_vantage_global_quote_provider},
    {"id": "alpha_vantage_daily", "label": "Alpha Vantage Daily Adjusted", "type": "history", "parallel": True, "timeoutSeconds": 7, "fetch": fetch_alpha_vantage_daily_quote_provider},
    {"id": "local_history_cache", "label": "Local history cache", "type": "history", "parallel": True, "timeoutSeconds": 2, "fetch": fetch_history_cache_quote_provider},
  ]
  if quote_chain_prefers_google(symbols):
    providers.sort(key=lambda provider: 0 if provider["id"] == "google_finance_page" else 1)
  return providers


# ── Vendor-aware rotation ────────────────────────────────────────────────────
# Maps each provider id to its upstream vendor. We rotate WITHIN each vendor's
# pool so a single vendor isn't hit on every request, while still keeping at
# least one representative from every vendor in the live fetch.
QUOTE_PROVIDER_VENDOR = {
  "yahoo_quote_primary": "yahoo",
  "yahoo_quote_secondary": "yahoo",
  "yahoo_chart_primary": "yahoo",
  "yahoo_chart_secondary": "yahoo",
  "yahoo_search": "yahoo",
  "yahoo_summary": "yahoo",
  "yahoo_web": "yahoo",
  "google_finance_page": "google",
  "stooq_daily": "stooq",
  "alpha_vantage_global": "alpha_vantage",
  "alpha_vantage_daily": "alpha_vantage",
  "local_history_cache": "cache",
}

_QUOTE_VENDOR_ROTATION_LOCK = threading.Lock()
_QUOTE_VENDOR_ROTATION: dict[str, int] = {}


def select_rotated_quote_chain(chain: list[dict]) -> list[dict]:
  """
  Pick one provider per known vendor (rotated within that vendor's pool) and
  pass through any provider whose id isn't in the vendor map untouched. This
  lets each `/api/quotes` request hit ~4–5 sources instead of 12, spreading
  load and reducing rate-limit risk against any single upstream.

  The dispatch layer (`fetch_live_quotes_from_providers`) falls back to the
  full chain for any symbol the rotated subset can't satisfy, so resilience
  is preserved.

  When the input chain contains no recognised vendor ids (the case in unit
  tests that mock the chain), this returns the chain unchanged so the test
  expectations don't shift.
  """
  if not chain:
    return chain
  has_known_vendor = any(QUOTE_PROVIDER_VENDOR.get(provider.get("id")) for provider in chain)
  if not has_known_vendor:
    return chain
  by_vendor: dict[str, list[dict]] = {}
  unknown: list[dict] = []
  for provider in chain:
    vendor = QUOTE_PROVIDER_VENDOR.get(provider.get("id"))
    if vendor:
      by_vendor.setdefault(vendor, []).append(provider)
    else:
      unknown.append(provider)
  selected: list[dict] = []
  with _QUOTE_VENDOR_ROTATION_LOCK:
    for vendor, pool in by_vendor.items():
      healthy = [provider for provider in pool if quote_provider_available(provider["id"])]
      if not healthy:
        # Whole vendor is cooling down — still queue the next one so dispatch
        # can mark it failed again or recover when cooldown elapses.
        healthy = pool
      idx = _QUOTE_VENDOR_ROTATION.get(vendor, 0) % len(healthy)
      selected.append(healthy[idx])
      _QUOTE_VENDOR_ROTATION[vendor] = (idx + 1) % len(healthy)
  # Preserve the original chain's vendor ordering (yahoo > google > stooq > av)
  # so provider_ranks downstream still favour faster sources.
  vendor_order = {provider["id"]: index for index, provider in enumerate(chain)}
  selected.sort(key=lambda provider: vendor_order.get(provider["id"], 999))
  selected.extend(unknown)
  return selected


def get_quote_rotation_snapshot() -> dict[str, int]:
  """Read-only view of the current vendor rotation indices. Used by the
  data-flow / notification UI to show which provider will be tried first
  per vendor on the next request."""
  with _QUOTE_VENDOR_ROTATION_LOCK:
    return dict(_QUOTE_VENDOR_ROTATION)


def post_json(url: str, payload: dict, timeout: int = 40) -> dict | None:
  if not is_allowed_outbound_url(url):
    return None
  cache_key = outbound_cache_key("POST", url, payload)
  hostname = (urllib.parse.urlparse(url).hostname or "").lower()
  ttl_seconds = outbound_ttl_for_host(hostname)
  with OUTBOUND_LOCK:
    cached = OUTBOUND_RESPONSE_CACHE.get(cache_key)
    if cached and (time.time() - cached[0]) <= ttl_seconds:
      return cached[1]
  data = json.dumps(payload).encode("utf-8")
  body = secure_open_url(
    url,
    timeout=timeout,
    headers={
      "User-Agent": USER_AGENT,
      "Content-Type": "application/json",
      "Accept": "application/json",
    },
    data=data,
  )
  if body is None:
    return None
  try:
    parsed = json.loads(body.decode("utf-8"))
  except json.JSONDecodeError:
    return None
  with OUTBOUND_LOCK:
    OUTBOUND_RESPONSE_CACHE[cache_key] = (time.time(), parsed)
  return parsed


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
  def redirect_request(self, req, fp, code, msg, headers, newurl):
    return None


def post_local_json(url: str, payload: dict, timeout: int = 12, max_bytes: int = 2_000_000) -> dict | None:
  if not is_allowed_local_llm_url(url):
    return None
  data = json.dumps(payload).encode("utf-8")
  request = urllib.request.Request(
    url,
    headers={
      "User-Agent": USER_AGENT,
      "Content-Type": "application/json",
      "Accept": "application/json",
    },
    data=data,
    method="POST",
  )
  opener = urllib.request.build_opener(NoRedirectHandler())
  try:
    with opener.open(request, timeout=timeout) as response:
      content_length = int(response.headers.get("Content-Length", "0") or "0")
      if content_length > max_bytes:
        return None
      body = response.read(max_bytes + 1)
      if len(body) > max_bytes:
        return None
  except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, socket.timeout, ValueError):
    return None
  try:
    parsed = json.loads(body.decode("utf-8"))
  except (UnicodeDecodeError, json.JSONDecodeError):
    return None
  return parsed if isinstance(parsed, dict) else None


def normalize_symbol(symbol: str, market: str | None = None) -> str:
  cleaned = (symbol or "").strip().upper()
  if not cleaned:
    return ""
  if cleaned.startswith("^") or cleaned.endswith("=F") or cleaned.endswith("-USD"):
    return cleaned
  if "." in cleaned:
    return cleaned
  suffix = MARKET_SUFFIXES.get((market or "").lower(), "")
  return f"{cleaned}{suffix}"


def deterministic_noise(seed: int, index: int) -> float:
  value = math.sin(seed * 0.017 + index * 0.83) * 10000
  return value - math.floor(value)


def symbol_seed(symbol: str) -> int:
  return sum(ord(char) * (index + 11) for index, char in enumerate(symbol))


def fallback_meta(symbol: str) -> dict:
  if symbol in FALLBACK_TICKERS:
    return FALLBACK_TICKERS[symbol]
  if symbol.endswith(".NS"):
    return {"name": symbol.replace(".NS", ""), "basePrice": 1200.0, "currency": "INR", "exchange": "NSE", "beta": 0.92, "pe": 24.0}
  if symbol.endswith(".BO"):
    return {"name": symbol.replace(".BO", ""), "basePrice": 1200.0, "currency": "INR", "exchange": "BSE", "beta": 0.92, "pe": 24.0}
  if symbol.endswith(".AX"):
    return {"name": symbol.replace(".AX", ""), "basePrice": 38.0, "currency": "AUD", "exchange": "ASX", "beta": 0.86, "pe": 17.0}
  if symbol.endswith(".T"):
    return {"name": symbol.replace(".T", ""), "basePrice": 3150.0, "currency": "JPY", "exchange": "JPX", "beta": 0.78, "pe": 15.0}
  if symbol.startswith("^"):
    return {"name": symbol, "basePrice": 100.0, "currency": "USD", "exchange": "Index", "beta": 1.0, "pe": 20.0}
  return {"name": symbol, "basePrice": 120.0 + (symbol_seed(symbol) % 180), "currency": "USD", "exchange": "US", "beta": 1.0, "pe": 22.0}


def infer_region_key(symbol: str | None = None, exchange: str | None = None, currency: str | None = None) -> str:
  symbol = (symbol or "").upper()
  exchange_label = (exchange or "").upper()
  currency_label = (currency or "").upper()
  if symbol.endswith(".NS") or symbol.endswith(".BO") or exchange_label in {"NSE", "BSE", "INDIA"} or currency_label == "INR":
    return "india"
  return "us"


def region_config(region_key: str | None) -> dict:
  return REGION_CONFIGS.get((region_key or "us").lower(), REGION_CONFIGS["us"])


def fallback_series(symbol: str, points: int = 180) -> list[float]:
  meta = fallback_meta(symbol)
  base_price = meta["basePrice"]
  drift = ((symbol_seed(symbol) % 13) - 6) / 2800
  cycle = ((symbol_seed(symbol) % 7) + 3) / 40
  beta = meta["beta"]
  price = float(base_price)
  series = []
  for index in range(points):
    seasonal = math.sin(index / cycle) * price * 0.008
    shock = (deterministic_noise(symbol_seed(symbol), index) - 0.48) * price * 0.012 * beta
    price = max(price + price * drift + seasonal + shock, 1)
    series.append(round(price, 2))
  return series


def average(values: list[float]) -> float:
  if not values:
    return 0.0
  return sum(values) / len(values)


def std_dev(values: list[float]) -> float:
  if len(values) < 2:
    return 0.0
  return statistics.pstdev(values)


def pct_change(current: float, previous: float) -> float:
  if not previous:
    return 0.0
  return ((current - previous) / previous) * 100


def calc_rsi(prices: list[float], period: int = 14) -> float:
  """Calculate Wilder RSI(period). Returns 50.0 (neutral) if insufficient data."""
  if len(prices) < period + 1:
    return 50.0
  deltas = [prices[index] - prices[index - 1] for index in range(1, len(prices))]
  gains = [max(delta, 0.0) for delta in deltas]
  losses = [max(-delta, 0.0) for delta in deltas]
  avg_gain = sum(gains[:period]) / period
  avg_loss = sum(losses[:period]) / period
  for index in range(period, len(gains)):
    avg_gain = ((avg_gain * (period - 1)) + gains[index]) / period
    avg_loss = ((avg_loss * (period - 1)) + losses[index]) / period
  if avg_loss == 0:
    return 100.0 if avg_gain > 0 else 50.0
  rs = avg_gain / avg_loss
  return round(100.0 - (100.0 / (1.0 + rs)), 2)


def calc_volume_trend(volumes: list[float], short: int = 5, long: int = 20) -> float:
  """Returns ratio of recent avg volume to longer-term avg. >1 = rising volume."""
  if len(volumes) < long:
    return 1.0
  short_avg = average(volumes[-short:])
  long_avg = average(volumes[-long:])
  return short_avg / long_avg if long_avg else 1.0


def calc_ema(prices: list[float], period: int) -> list[float]:
  """Exponential moving average."""
  if not prices:
    return []
  k = 2.0 / (period + 1)
  ema = [prices[0]]
  for price in prices[1:]:
    ema.append(price * k + ema[-1] * (1 - k))
  return ema


def calc_macd(prices: list[float], fast: int = 12, slow: int = 26, signal: int = 9) -> dict:
  """MACD line, signal line, histogram, and crossover direction."""
  if len(prices) < slow + signal:
    return {"line": 0.0, "signal": 0.0, "histogram": 0.0, "crossover": 0.0}
  fast_ema = calc_ema(prices, fast)
  slow_ema = calc_ema(prices, slow)
  aligned_line = [fast_value - slow_value for fast_value, slow_value in zip(fast_ema, slow_ema)]
  macd_line = aligned_line[slow - 1:]
  if len(macd_line) < signal:
    return {"line": 0.0, "signal": 0.0, "histogram": 0.0, "crossover": 0.0}
  signal_line = calc_ema(macd_line, signal)
  histogram = macd_line[-1] - signal_line[-1]
  # Crossover: positive = MACD crossed above signal recently, negative = below
  crossover = 0.0
  if len(macd_line) >= 2 and len(signal_line) >= 2:
    prev_diff = macd_line[-2] - signal_line[-2]
    curr_diff = macd_line[-1] - signal_line[-1]
    if prev_diff < 0 and curr_diff > 0:
      crossover = 1.0   # bullish crossover
    elif prev_diff > 0 and curr_diff < 0:
      crossover = -1.0  # bearish crossover
    else:
      crossover = clamp(curr_diff / (abs(prices[-1]) * 0.01 + 1e-9), -1.0, 1.0)
  return {
    "line": round(macd_line[-1], 6),
    "signal": round(signal_line[-1], 6),
    "histogram": round(histogram, 6),
    "crossover": round(crossover, 4),
  }


def calc_bollinger(prices: list[float], period: int = 20, num_std: float = 2.0) -> dict:
  """Bollinger Band position: 0 = lower band, 0.5 = midline, 1 = upper band."""
  if len(prices) < period:
    return {"position": 0.5, "bandwidth": 0.0, "squeeze": False}
  window = prices[-period:]
  mid = average(window)
  sd = std_dev(window)
  upper = mid + num_std * sd
  lower = mid - num_std * sd
  band_range = upper - lower
  latest = prices[-1]
  position = clamp((latest - lower) / band_range, 0.0, 1.0) if band_range > 0 else 0.5
  bandwidth = band_range / mid if mid else 0.0
  # Squeeze: bandwidth below 2% suggests volatility contraction → breakout imminent
  squeeze = bandwidth < 0.02
  return {
    "position": round(position, 4),
    "bandwidth": round(bandwidth, 4),
    "squeeze": squeeze,
  }


def calc_atr(prices: list[float], period: int = 14) -> float:
  """Average True Range as % of latest price (simplified: using close-to-close)."""
  if len(prices) < period + 1:
    return 0.0
  true_ranges = [abs(prices[i] - prices[i - 1]) for i in range(1, len(prices))]
  atr = average(true_ranges[-period:])
  return atr / prices[-1] if prices[-1] else 0.0


def raw_value(block: dict, key: str, default=None):
  value = (block or {}).get(key)
  if isinstance(value, dict):
    return value.get("raw", value.get("fmt", default))
  return value if value is not None else default


def format_large_number(value: float | int | None) -> str:
  if value in (None, ""):
    return "n/a"
  number = float(value)
  for threshold, suffix in ((1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "K")):
    if abs(number) >= threshold:
      return f"{number / threshold:.2f}{suffix}"
  return f"{number:.0f}"


def parse_compact_number(value) -> float:
  if value in (None, ""):
    return 0.0
  if isinstance(value, (int, float)):
    return float(value)
  text = str(value).strip().replace(",", "")
  match = re.match(r"^([-+]?\d+(?:\.\d+)?)\s*([KMBT])?$", text, flags=re.IGNORECASE)
  if not match:
    numeric = re.sub(r"[^0-9.+-]", "", text)
    try:
      return float(numeric) if numeric else 0.0
    except ValueError:
      return 0.0
  number = float(match.group(1))
  suffix = (match.group(2) or "").upper()
  multiplier = {"K": 1e3, "M": 1e6, "B": 1e9, "T": 1e12}.get(suffix, 1.0)
  return number * multiplier


def centered_volume_participation(volume_ratio: float) -> float:
  """Log participation centered at 1.0x volume so normal volume adds no directional edge."""
  return clamp(math.log(max(float(volume_ratio or 0.0), 0.05)), -1.5, 1.5)


def fetch_yahoo_quotes(symbols: list[str]) -> dict[str, dict]:
  cleaned = [symbol for symbol in symbols if symbol]
  if not cleaned:
    return {}
  quoted = urllib.parse.quote(",".join(cleaned))
  payload = json_get(f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={quoted}", timeout=6)
  results = {}
  quote_response = (payload or {}).get("quoteResponse", {})
  for item in quote_response.get("result", []):
    symbol = item.get("symbol")
    if symbol:
      results[symbol.upper()] = item
  return results


def fetch_yahoo_chart(symbol: str, range_value: str = "6mo", interval: str = "1d") -> dict | None:
  quoted = urllib.parse.quote(symbol)
  payload = json_get(
    f"https://query1.finance.yahoo.com/v8/finance/chart/{quoted}?range={range_value}&interval={interval}&includePrePost=false&events=div%2Csplits",
    timeout=8,
  )
  chart = (payload or {}).get("chart", {})
  results = chart.get("result", [])
  return results[0] if results else None


def fetch_yahoo_quote_summary_uncached(symbol: str) -> dict:
  quoted = urllib.parse.quote(symbol)
  payload = json_get(
    f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{quoted}?modules=summaryDetail,defaultKeyStatistics,financialData,assetProfile,recommendationTrend,earningsTrend,majorHoldersBreakdown"
  )
  result = ((payload or {}).get("quoteSummary") or {}).get("result") or []
  return result[0] if result else {}


def fetch_yahoo_quote_summary(symbol: str) -> dict:
  return memory_cached_value(
    f"quote-summary:{symbol.upper()}",
    6 * 60 * 60,
    lambda: fetch_yahoo_quote_summary_uncached(symbol),
  ) or {}


def search_terms(value: str) -> set[str]:
  return {term for term in re.split(r"[^a-z0-9]+", (value or "").lower()) if len(term) >= 2}


def _sector_matches_query(query_lower: str, meta: dict) -> bool:
  """Return True if the query matches sector or tag metadata of a ticker."""
  sector = meta.get("sector", "").lower()
  tags = [t.lower() for t in meta.get("tags", [])]
  terms = search_terms(query_lower)
  if not terms:
    return False
  sector_terms = search_terms(sector)
  tag_terms = set().union(*(search_terms(tag) for tag in tags)) if tags else set()
  # Direct sector/tag matches should be based on words, not tiny substrings inside company names.
  if terms & sector_terms:
    return True
  if terms & tag_terms:
    return True
  # Sector keyword → sector lookup
  for kw, matched_sectors in SECTOR_KEYWORDS.items():
    keyword_terms = search_terms(kw)
    if terms & keyword_terms:
      if any(ms in sector for ms in matched_sectors):
        return True
      if any(ms in tag for ms in matched_sectors for tag in tags):
        return True
  return False


def search_match_metadata(query: str, symbol: str, meta: dict) -> dict:
  cleaned = query.strip().upper()
  query_lower = query.strip().lower()
  normalized_query = re.sub(r"[^A-Z0-9]+", " ", cleaned).strip()
  normalized_name = re.sub(r"[^A-Z0-9]+", " ", meta.get("name", "").upper()).strip()
  aliases = [alias.upper() for alias in meta.get("aliases", [])]
  alias_compact = [re.sub(r"[^A-Z0-9]+", " ", alias).strip() for alias in aliases]
  sector = meta.get("sector", "")
  tags = [tag.lower() for tag in meta.get("tags", [])]
  terms = search_terms(query_lower)
  if cleaned == symbol or cleaned == symbol.replace(".NS", "") or cleaned == symbol.replace(".BO", ""):
    return {"matchType": "Symbol match", "matchReason": "Exact ticker symbol", "score": 100}
  if symbol.startswith(cleaned):
    return {"matchType": "Symbol match", "matchReason": "Ticker prefix match", "score": 92}
  if normalized_name.startswith(normalized_query):
    return {"matchType": "Company match", "matchReason": f"Company starts with {query.strip()}", "score": 88}
  if cleaned in meta.get("name", "").upper() or normalized_query in normalized_name:
    return {"matchType": "Company match", "matchReason": "Company name contains search text", "score": 82}
  if cleaned in aliases or any(normalized_query in alias for alias in alias_compact):
    return {"matchType": "Alias match", "matchReason": "Known company alias", "score": 78}
  for keyword, matched_sectors in SECTOR_KEYWORDS.items():
    if terms & search_terms(keyword):
      if any(matched in sector.lower() for matched in matched_sectors):
        return {"matchType": "Sector match", "matchReason": f"{keyword.title()} maps to {sector}", "score": 72}
  sector_terms = search_terms(sector)
  tag_terms = set().union(*(search_terms(tag) for tag in tags)) if tags else set()
  if terms & sector_terms or terms & tag_terms:
    return {"matchType": "Sector match", "matchReason": sector or "Tag match", "score": 68}
  return {"matchType": "Local match", "matchReason": "Local universe match", "score": 50}


def local_search_results(query: str) -> list[dict]:
  cleaned = query.strip().upper()
  query_lower = query.strip().lower()
  if not cleaned:
    return []
  normalized_query = re.sub(r"[^A-Z0-9]+", " ", cleaned).strip()
  results = []
  for symbol, meta in FALLBACK_TICKERS.items():
    normalized_name = meta["name"].upper()
    normalized_name_compact = re.sub(r"[^A-Z0-9]+", " ", normalized_name).strip()
    aliases = [alias.upper() for alias in meta.get("aliases", [])]
    alias_compact = [re.sub(r"[^A-Z0-9]+", " ", alias).strip() for alias in aliases]
    if (
      cleaned in symbol
      or cleaned in normalized_name
      or normalized_query in normalized_name_compact
      or cleaned in aliases
      or cleaned == symbol.replace(".NS", "")
      or cleaned == symbol.replace(".BO", "")
      or any(cleaned in alias for alias in aliases)
      or any(normalized_query in alias for alias in alias_compact)
      or normalized_name_compact.startswith(normalized_query)
      or _sector_matches_query(query_lower, meta)
    ):
      results.append(
        {
          "symbol": symbol,
          "name": meta["name"],
          "exchange": meta["exchange"],
          "region": meta["exchange"],
          "sector": meta.get("sector", ""),
          **search_match_metadata(query, symbol, meta),
        }
      )
  return results


def ranked_results(query: str, remote_results: list[dict]) -> list[dict]:
  local_results = local_search_results(query)
  seen = set()
  ordered = []

  def push(item: dict) -> None:
    symbol = item.get("symbol", "").upper()
    if not symbol or symbol in seen:
      return
    seen.add(symbol)
    if "score" not in item:
      item["score"] = 45
    if "matchType" not in item:
      item["matchType"] = "Remote match"
    if "matchReason" not in item:
      item["matchReason"] = "Provider search result"
    ordered.append(item)

  cleaned = query.strip().upper()
  for item in local_results:
    push(item)
  for item in remote_results:
    push(item)

  def rank_tuple(item: dict) -> tuple:
    symbol = item["symbol"].upper()
    name = (item.get("name") or "").upper()
    exchange = (item.get("exchange") or "")
    normalized_name = re.sub(r"[^A-Z0-9]+", " ", name).strip()
    return (
      0 if symbol == cleaned else 1,
      0 if symbol == f"{cleaned}.NS" else 1,
      0 if symbol.startswith(cleaned) else 1,
      0 if normalized_name.startswith(cleaned) else 1,
      0 if cleaned in normalized_name else 1,
      0 if exchange == "NSE" else 1,
      -float(item.get("score") or 0),
      symbol,
    )

  ordered.sort(
    key=rank_tuple
  )
  return ordered[:16]


def fetch_yahoo_search(query: str) -> list[dict]:
  local_results = local_search_results(query)
  if local_results and max(float(item.get("score") or 0) for item in local_results) >= 78:
    return ranked_results(query, [])
  quoted = urllib.parse.quote(query)
  payload = json_get(
    f"https://query1.finance.yahoo.com/v1/finance/search?q={quoted}&quotesCount=20&newsCount=0"
  )
  results = []
  for item in (payload or {}).get("quotes", []):
    symbol = item.get("symbol")
    if not symbol:
      continue
    results.append(
      {
        "symbol": symbol.upper(),
        "name": item.get("shortname") or item.get("longname") or symbol,
        "exchange": item.get("exchange") or item.get("exchDisp") or "",
        "region": item.get("exchange") or "",
        "matchType": "Remote match",
        "matchReason": "Yahoo Finance search result",
        "score": 45,
      }
    )
  return ranked_results(query, results)


def duckduckgo_search(query: str) -> list[dict]:
  quoted = urllib.parse.quote(query)
  html_text = text_get(f"https://duckduckgo.com/html/?q={quoted}")
  if not html_text:
    return []

  matches = re.findall(
    r'<a[^>]*class="result__a"[^>]*href="(?P<href>[^"]+)"[^>]*>(?P<title>.*?)</a>',
    html_text,
    flags=re.IGNORECASE | re.DOTALL,
  )

  results = []
  for href, title_html in matches[:6]:
    title = html.unescape(re.sub(r"<.*?>", "", title_html)).strip()
    url = html.unescape(href)
    if "uddg=" in url:
      parsed = urllib.parse.urlparse(url)
      nested = urllib.parse.parse_qs(parsed.query).get("uddg")
      if nested:
        url = urllib.parse.unquote(nested[0])
    results.append({"title": title or "Result", "url": url})
  return results


def parse_publish_time(raw_value: str | None) -> str | None:
  if not raw_value:
    return None
  try:
    parsed = parsedate_to_datetime(raw_value)
  except (TypeError, ValueError, IndexError):
    return None
  if parsed.tzinfo is None:
    parsed = parsed.replace(tzinfo=timezone.utc)
  return parsed.astimezone(timezone.utc).isoformat()


def fetch_google_news_rss(query: str) -> list[dict]:
  quoted = urllib.parse.quote(query)
  xml_text = text_get(f"https://news.google.com/rss/search?q={quoted}&hl=en-US&gl=US&ceid=US:en")
  if not xml_text:
    return []
  try:
    root = ET.fromstring(xml_text)
  except ET.ParseError:
    return []

  items = []
  for item in root.findall(".//item"):
    title = (item.findtext("title") or "").strip()
    link = (item.findtext("link") or "").strip()
    published = parse_publish_time((item.findtext("pubDate") or "").strip())
    source = ""
    source_node = item.find("{http://search.yahoo.com/mrss/}source")
    if source_node is not None and source_node.text:
      source = source_node.text.strip()
    if not source:
      source = urllib.parse.urlparse(link).netloc.replace("www.", "") if link else ""
    if title and link:
      items.append(
        {
          "title": title,
          "url": link,
          "source": source,
          "publishedAt": published,
        }
      )
    if len(items) >= 12:
      break
  return items


def fetch_rss_feed(url: str, source_hint: str = "", limit: int = 8) -> list[dict]:
  xml_text = text_get(url)
  if not xml_text:
    return []
  try:
    root = ET.fromstring(xml_text)
  except ET.ParseError:
    return []

  items = []
  channel_title = ""
  channel = root.find("channel")
  if channel is not None:
    channel_title = (channel.findtext("title") or "").strip()
  for item in root.findall(".//item"):
    title = (item.findtext("title") or "").strip()
    link = (item.findtext("link") or "").strip()
    published = parse_publish_time((item.findtext("pubDate") or "").strip())
    source = source_hint or channel_title or (urllib.parse.urlparse(link).netloc.replace("www.", "") if link else "")
    if title and link:
      items.append(
        {
          "title": title,
          "url": link,
          "source": source,
          "publishedAt": published,
        }
      )
    if len(items) >= limit:
      break
  return items


def fetch_popular_rss_items(category: str) -> list[dict]:
  feeds = POPULAR_RSS_FEEDS.get(category, [])
  if not feeds:
    return []

  with ThreadPoolExecutor(max_workers=min(6, len(feeds))) as executor:
    futures = [executor.submit(fetch_rss_feed, feed["url"], feed.get("source", ""), 4) for feed in feeds]

  results: list[dict] = []
  for future in futures:
    try:
      results.extend(future.result())
    except Exception:
      continue
  return results


def fetch_market_insight_items(limit_per_feed: int = 5) -> list[dict]:
  """Pull source-labeled market insight feeds, led by Paytm Money Market Pulse."""
  feeds = MARKET_INSIGHT_RSS_FEEDS
  with ThreadPoolExecutor(max_workers=min(5, len(feeds))) as executor:
    futures = [
      executor.submit(fetch_rss_feed, feed["url"], feed.get("source", ""), limit_per_feed)
      for feed in feeds
    ]

  results: list[dict] = []
  for feed, future in zip(feeds, futures):
    try:
      fetched = future.result()
    except Exception:
      fetched = []
    for item in fetched:
      results.append(
        {
          **item,
          "category": feed.get("category") or "markets",
          "sourceType": "market_insight_rss",
        }
      )
  return results


def fetch_bls_cpi_snapshot() -> dict | None:
  payload = post_json(
    "https://api.bls.gov/publicAPI/v2/timeseries/data/",
    {
      "seriesid": ["CUUR0000SA0", "CUSR0000SA0"],
      "latest": "true",
    },
    timeout=12,
  )
  series = ((payload or {}).get("Results") or {}).get("series") or []
  if not series:
    return None
  values = {}
  for item in series:
    data = (item.get("data") or [{}])[0] or {}
    raw_value = data.get("value")
    if raw_value is None:
      continue
    try:
      values[item.get("seriesID")] = {
        "value": float(raw_value),
        "periodName": data.get("periodName", ""),
        "year": data.get("year", ""),
      }
    except (TypeError, ValueError):
      continue
  headline = values.get("CUUR0000SA0")
  core = values.get("CUSR0000SA0")
  if not headline:
    return None
  return {
    "headlineIndex": headline["value"],
    "coreIndex": core["value"] if core else None,
    "label": f"{headline.get('periodName', '')} {headline.get('year', '')}".strip(),
    "source": "BLS Public API",
  }


def fetch_fred_series_latest(series_id: str, api_key: str | None = None) -> dict | None:
  key = api_key or os.environ.get("FRED_API_KEY", "").strip()
  if not key:
    return None
  query = urllib.parse.urlencode(
    {
      "series_id": series_id,
      "api_key": key,
      "file_type": "json",
      "sort_order": "desc",
      "limit": "1",
    }
  )
  payload = json_get(f"https://api.stlouisfed.org/fred/series/observations?{query}")
  observations = (payload or {}).get("observations") or []
  if not observations:
    return None
  latest = observations[0]
  try:
    value = float(latest.get("value"))
  except (TypeError, ValueError):
    return None
  return {
    "value": value,
    "date": latest.get("date", ""),
    "source": "FRED",
  }


def fetch_us_fred_curve() -> dict | None:
  config = load_config()
  api_key = config.get("fredApiKey") or os.environ.get("FRED_API_KEY", "").strip()
  if not api_key:
    return None
  series_map = {
    "2Y": "DGS2",
    "5Y": "DGS5",
    "10Y": "DGS10",
    "30Y": "DGS30",
    "breakeven": "T10YIE",
  }
  results = {}
  with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {label: executor.submit(fetch_fred_series_latest, series_id, api_key) for label, series_id in series_map.items()}
    for label, future in futures.items():
      try:
        results[label] = future.result()
      except Exception:
        results[label] = None
  if not all(results.get(label) for label in ["2Y", "5Y", "10Y", "30Y"]):
    return None
  return results


def fetch_fed_calendar_items(limit: int = 6) -> list[dict]:
  html_text = text_get("https://www.federalreserve.gov/newsevents/calendar.htm")
  if not html_text:
    return []
  matches = re.findall(
    r'<a href="(?P<url>/newsevents/[^"]+)".*?>(?P<title>.*?)</a>.*?<p class="date">(?P<date>.*?)</p>',
    html_text,
    flags=re.IGNORECASE | re.DOTALL,
  )
  items = []
  for url, title, date_text in matches[:limit]:
    clean_title = html.unescape(re.sub(r"<.*?>", "", title)).strip()
    clean_date = html.unescape(re.sub(r"<.*?>", "", date_text)).strip()
    if clean_title:
      items.append(
        {
          "title": clean_title,
          "date": clean_date,
          "url": urllib.parse.urljoin("https://www.federalreserve.gov", url),
          "source": "Federal Reserve",
          "category": "calendar",
        }
      )
  return items


def fetch_rbi_calendar_items(limit: int = 6) -> list[dict]:
  html_text = text_get("https://www.rbi.org.in/Scripts/NotificationUser.aspx")
  if not html_text:
    return []
  matches = re.findall(
    r'href="(?P<url>[^"]*NotificationUser\.aspx[^"]*)".*?>(?P<title>.*?)</a>',
    html_text,
    flags=re.IGNORECASE | re.DOTALL,
  )
  items = []
  for url, title in matches:
    clean_title = html.unescape(re.sub(r"<.*?>", "", title)).strip()
    if not clean_title:
      continue
    items.append(
      {
        "title": clean_title,
        "date": "",
        "url": urllib.parse.urljoin("https://www.rbi.org.in/", url),
        "source": "RBI",
        "category": "calendar",
      }
    )
    if len(items) >= limit:
      break
  return items


MARKET_RELEVANT_TERMS = {
  "market", "markets", "stock", "stocks", "share", "shares", "equity", "equities", "index", "indexes",
  "earnings", "revenue", "profit", "margin", "guidance", "forecast", "inflation", "rates", "yield", "bond",
  "oil", "gold", "currency", "forex", "trade", "tariff", "sanction", "war", "ceasefire", "attack", "conflict",
  "deal", "deals", "partnership", "merger", "acquisition", "layoff", "restructuring", "policy", "regulation",
  "central bank", "fed", "rbi", "ecb", "boj", "economy", "economic", "gdp", "exports", "imports", "demand",
  "supply", "bank", "banking", "credit", "pharma", "energy", "telecom", "technology", "semiconductor",
  "automaker", "manufacturing", "shipping", "consumer", "retail", "brand", "ipo", "valuation", "risk",
}

MARKET_IRRELEVANT_TERMS = {
  "murder", "homicide", "shooting", "stab", "stabbing", "robbery", "burglary", "police", "arrest",
  "crime", "criminal", "court", "trial", "missing person", "firefighter", "weather alert", "storm warning",
  "traffic", "road closure", "lottery", "celebrity", "movie review", "sports score", "festival", "concert",
  "school board", "obituary", "wedding", "entertainment gossip", "sexual assault", "mosquito", "bite risk",
}

RADAR_SOURCE_BOOSTS = {
  "bbc business": 4,
  "bbc world": 4,
  "npr business": 4,
  "npr world": 4,
  "nyt business": 5,
  "nyt world": 5,
  "paytm money market pulse": 6,
  "paytm money stocks": 5,
  "marketwatch top stories": 5,
  "marketwatch marketpulse": 5,
  "economic times markets": 4,
  "economic times news": 3,
  "times of india business": 3,
  "times of india world": 3,
  "guardian business": 4,
  "guardian world": 4,
  "guardian us": 3,
  "cnbc": 4,
  "reuters": 6,
  "bloomberg": 6,
}


def market_relevance_score(item: dict, category: str, symbol: str | None = None) -> int:
  text = f"{item.get('title', '')} {item.get('source', '')}".lower()
  score = 0
  for term in MARKET_RELEVANT_TERMS:
    if term in text:
      score += 2
  for term in MARKET_IRRELEVANT_TERMS:
    if term in text:
      score -= 5
  if category in {"markets", "business", "deals", "partnerships", "layoffs", "brands"}:
    score += 2
  if category in {"world", "war"}:
    score += sum(term in text for term in {"oil", "shipping", "sanction", "tariff", "rates", "inflation", "energy"})
  if symbol:
    meta = fallback_meta(symbol)
    company_terms = {
      meta.get("name", "").lower(),
      symbol.lower(),
      meta.get("exchange", "").lower(),
      meta.get("sector", "").lower(),
      meta.get("industry", "").lower(),
    }
    score += sum(bool(term and term in text) for term in company_terms) * 2
  return score


def filter_market_relevant_items(items: list[dict], category: str, symbol: str | None = None) -> list[dict]:
  threshold = 2 if category == "all" else 1
  filtered = [item for item in items if market_relevance_score(item, item.get("category") or category, symbol) >= threshold]
  return filtered or items


def item_age_hours(item: dict) -> float:
  published_at = item.get("publishedAt")
  if not published_at:
    return 9999.0
  try:
    published = datetime.fromisoformat(published_at)
  except ValueError:
    return 9999.0
  if published.tzinfo is None:
    published = published.replace(tzinfo=timezone.utc)
  return max(0.0, (datetime.now(timezone.utc) - published.astimezone(timezone.utc)).total_seconds() / 3600)


def radar_priority_score(item: dict, symbol: str | None = None) -> float:
  source = (item.get("source") or "").lower()
  relevance = market_relevance_score(item, item.get("category") or "world", symbol)
  significance = event_significance_score(item, item.get("category") or "world", symbol)
  age_hours = item_age_hours(item)
  freshness = 6 if age_hours <= 6 else 4 if age_hours <= 24 else 2 if age_hours <= 72 else -4
  source_boost = sum(boost for key, boost in RADAR_SOURCE_BOOSTS.items() if key in source)
  return (relevance * 2.2) + (significance * 1.8) + freshness + source_boost


def event_significance_score(item: dict, category: str, symbol: str | None = None) -> int:
  text = f"{item.get('title', '')} {item.get('source', '')}".lower()
  score = 0
  for keyword in {"attack", "war", "ceasefire", "bomb", "tariff", "sanction", "deal", "partnership", "merger", "acquisition", "layoff", "earnings", "profit", "guidance", "regulator", "approval", "probe"}:
    if keyword in text:
      score += 2
  if category in {"war", "world"}:
    score += sum(keyword in text for keyword in {"iran", "israel", "russia", "ukraine", "china", "taiwan", "fed", "rbi"})
  if category in {"deals", "partnerships"}:
    score += sum(keyword in text for keyword in {"deal", "agreement", "alliance", "order", "stake"})
  if category == "layoffs":
    score += sum(keyword in text for keyword in {"layoff", "cut", "restructuring", "headcount"})
  if category in {"markets", "business"}:
    score += sum(keyword in text for keyword in {"earnings", "guidance", "margin", "revenue", "profit"})
  if symbol:
    meta = fallback_meta(symbol)
    if meta["name"].lower().split()[0] in text or symbol.replace(".NS", "").replace(".BO", "").lower() in text:
      score += 3
  published_at = item.get("publishedAt")
  if published_at:
    try:
      age_hours = max(0, (datetime.now(timezone.utc) - datetime.fromisoformat(published_at)).total_seconds() / 3600)
      if age_hours <= 12:
        score += 4
      elif age_hours <= 48:
        score += 2
    except ValueError:
      pass
  return score


def merge_event_items(*groups: list[dict]) -> list[dict]:
  seen_urls = set()
  merged = []
  for group in groups:
    for item in group:
      url = item.get("url", "")
      title = item.get("title", "")
      key = url or title.lower()
      if not key or key in seen_urls:
        continue
      seen_urls.add(key)
      merged.append(item)
  return merged


def generate_local_llm_answer(prompt: str, config: dict, timeout: int = 12) -> str | None:
  base = (config.get("localLlmBaseUrl") or DEFAULT_CONFIG["localLlmBaseUrl"]).rstrip("/")
  if not is_allowed_local_llm_base_url(base):
    return None
  model = resolve_local_llm_model(config)
  payload = {
    "model": model,
    "stream": False,
    "prompt": prompt,
    "options": {"temperature": 0.2},
  }
  response = post_local_json(f"{base}/api/generate", payload, timeout=timeout)
  if not response:
    return None
  return (response.get("response") or "").strip() or None


def build_research_context(symbol: str | None) -> dict:
  if not symbol:
    return {"symbol": "", "summary": "No active ticker selected."}
  snapshot = build_ticker_snapshot(symbol)
  return {
    "symbol": snapshot["symbol"],
    "name": snapshot["name"],
    "currency": snapshot["currency"],
    "price": snapshot["price"],
    "changePercent": snapshot["changePercent"],
    "regime": snapshot["regime"],
    "forecast": snapshot["forecast"]["direction"],
    "confidence": round(snapshot["forecast"]["confidence"], 1),
    "fairValueGap": round(snapshot["forecast"]["fairValueGap"], 2),
    "modelAgreement": snapshot["forecast"].get("models", {}).get("agreement", {}),
    "volume": snapshot["volume"],
    "stats": snapshot["stats"],
    "triggers": snapshot["forecast"]["triggers"],
  }


def synthesize_without_llm(query: str, context: dict, web_results: list[dict]) -> str:
  pieces = []
  if context.get("symbol"):
    pieces.append(
      f"{context['symbol']} is trading in {context.get('currency', 'local currency')} with a {context.get('forecast', 'neutral')} forecast, {context.get('confidence', 0)}% confidence, and fair-value gap of {context.get('fairValueGap', 0)}%."
    )
  if web_results:
    pieces.append("Web search found recent external references that may help ground the answer.")
  pieces.append(f"Question: {query}")
  pieces.append("Use the forecast, volume, catalysts, and any search results together before acting.")
  return " ".join(pieces)


def run_research_agent(query: str, symbol: str | None, use_web: bool, use_llm: bool) -> dict:
  config = load_config()
  context = {}
  web_results: list[dict] = []

  with ThreadPoolExecutor(max_workers=2) as executor:
    context_future = executor.submit(build_research_context, symbol)
    web_future = executor.submit(duckduckgo_search, query) if use_web else None
    context = context_future.result()
    if web_future is not None:
      web_results = web_future.result()

  prompt = "\n".join(
    [
      "You are a concise market research assistant embedded in a financial dashboard.",
      "Answer using the dashboard context first, then use the web results only as supporting evidence.",
      "Do not fabricate citations. If web results are weak, say so.",
      f"User question: {query}",
      f"Dashboard context: {json.dumps(context, ensure_ascii=True)}",
      f"Web results: {json.dumps(web_results, ensure_ascii=True)}",
      "Return a short answer, then 3-5 bullets of key takeaways.",
    ]
  )

  answer = generate_local_llm_answer(prompt, config, timeout=10) if use_llm else None
  if not answer:
    answer = synthesize_without_llm(query, context, web_results)

  takeaways = []
  for trigger in (context.get("triggers") or [])[:4]:
    takeaways.append(trigger.get("body"))

  return {
    "answer": answer,
    "webResults": web_results,
    "context": context,
    "takeaways": [item for item in takeaways if item][:4],
    "llmUsed": bool(use_llm and answer and "Question:" not in answer),
  }


def build_event_feed(category: str, symbol: str | None = None, keyword: str | None = None) -> dict:
  normalized = (category or "business").strip().lower()
  if normalized not in EVENT_CATEGORY_QUERIES:
    normalized = "business"
  event_categories = [key for key in EVENT_CATEGORY_QUERIES.keys() if key != "all"]
  symbol_query = ""
  if symbol:
    symbol_meta = fallback_meta(symbol)
    symbol_query = f" {symbol_meta['name']} {symbol_meta['exchange']}"
  query = (keyword or "").strip() or f"{EVENT_CATEGORY_QUERIES[normalized]}{symbol_query}"
  results = []
  market_insight_results: list[dict] = []

  if normalized == "all":
    with ThreadPoolExecutor(max_workers=8) as executor:
      future_map = {
        ("search", "all"): executor.submit(duckduckgo_search, query),
        ("market_insights", "markets"): executor.submit(fetch_market_insight_items, 5),
      }
      for category_key in event_categories:
        category_query = f"{EVENT_CATEGORY_QUERIES[category_key]}{symbol_query}"
        future_map[("google", category_key)] = executor.submit(fetch_google_news_rss, category_query)
        future_map[("popular", category_key)] = executor.submit(fetch_popular_rss_items, category_key)

      for (source_type, category_key), future in future_map.items():
        try:
          fetched = future.result()
        except Exception:
          continue
        if source_type == "search":
          enriched = [{**item, "category": item.get("category") or "all"} for item in fetched]
        elif source_type == "market_insights":
          enriched = [{**item, "category": item.get("category") or "markets"} for item in fetched]
          market_insight_results = merge_event_items(market_insight_results, enriched)
        else:
          enriched = [{**item, "category": category_key} for item in fetched]
        results = merge_event_items(results, enriched)
  else:
    with ThreadPoolExecutor(max_workers=4) as executor:
      google_future = executor.submit(fetch_google_news_rss, query)
      popular_future = executor.submit(fetch_popular_rss_items, normalized)
      search_future = executor.submit(duckduckgo_search, query)
      insight_future = executor.submit(fetch_market_insight_items, 5) if normalized in {"markets", "business"} else None
      rss_results = [{**item, "category": normalized} for item in google_future.result()]
      popular_results = [{**item, "category": normalized} for item in popular_future.result()]
      search_results = [{**item, "category": normalized} for item in search_future.result()]
      market_insight_results = [{**item, "category": item.get("category") or "markets"} for item in insight_future.result()] if insight_future is not None else []
    results = merge_event_items(rss_results, popular_results, search_results, market_insight_results)

  titles = [item.get("title", "") for item in results if item.get("title")]
  if symbol and normalized in {"partnerships", "deals", "brands", "layoffs"}:
    company_meta = fallback_meta(symbol)
    company_query = f"{company_meta['name']} {normalized} latest news"
    with ThreadPoolExecutor(max_workers=2) as executor:
      company_google = executor.submit(fetch_google_news_rss, company_query)
      company_search = executor.submit(duckduckgo_search, company_query)
      company_results = merge_event_items(company_google.result(), company_search.result())
    results = merge_event_items(results, company_results)
    titles = [item.get("title", "") for item in results if item.get("title")]

  live_result_count = len(results)
  results = filter_market_relevant_items(results, normalized, symbol)
  if not results:
    results = load_market_events(normalized, symbol, limit=12, max_age_hours=168)

  results = sorted(
    results,
    key=lambda item: (
      market_relevance_score(item, item.get("category") or normalized, symbol),
      item.get("publishedAt") or "",
      event_significance_score(item, item.get("category") or normalized, symbol),
    ),
    reverse=True,
  )[:10]
  titles = [item.get("title", "") for item in results if item.get("title")]

  config = load_config()
  brief = ""
  if titles:
    prompt = "\n".join(
      [
        "You are a concise event-briefing assistant inside a market dashboard.",
        f"Category: {normalized}",
        f"Symbol: {symbol or 'none'}",
        f"Headlines: {json.dumps(titles[:6], ensure_ascii=True)}",
        "Write one compact sentence summarizing the event flow and what kind of market risk it signals.",
      ]
    )
    brief = generate_local_llm_answer(prompt, config) or ""

  if not brief:
    brief = (
      f"{normalized.title()} flow is quiet right now."
      if not titles
      else f"{normalized.title()} headlines are active, with the latest results skewing toward market-relevant updates."
    )

  structured_items = []
  for item in results[:8]:
    url = item.get("url", "")
    item_category = item.get("category") or normalized
    structured_items.append(
      {
        "eventId": item.get("eventId") or stable_market_event_id(item),
        "title": item.get("title", "Update"),
        "url": url,
        "source": item.get("source") or (urllib.parse.urlparse(url).netloc.replace("www.", "") if url else ""),
        "category": item_category,
        "publishedAt": item.get("publishedAt"),
        "significance": event_significance_score(item, item_category, symbol),
        "relevance": market_relevance_score(item, item_category, symbol),
        "sourceType": item.get("sourceType") or ("local_db" if item.get("localDb") else "rss_search"),
        "storedAt": item.get("storedAt"),
      }
    )
  stored_count = save_market_events(structured_items, normalized, symbol)

  return {
    "category": normalized,
    "query": query,
    "brief": brief,
    "asOf": datetime.now(timezone.utc).isoformat(),
    "items": structured_items,
    "localStore": {
      "db": DB_PATH.name,
      "table": "market_events",
      "storedCount": stored_count,
      "liveResultCount": live_result_count,
      "marketInsightSources": [feed["source"] for feed in MARKET_INSIGHT_RSS_FEEDS],
    },
  }


def summarize_web_focus(symbol: str, snapshot: dict, web_results: list[dict]) -> str:
  if web_results:
    titles = [item.get("title", "") for item in web_results[:3] if item.get("title")]
    titles_text = " | ".join(titles)
    return f"Current web coverage for {snapshot['name']} is clustering around: {titles_text}."
  return f"External coverage is light right now, so the explainers lean more heavily on live market structure for {symbol}."


def build_academy_payload(symbol: str | None, use_web: bool = True, use_llm: bool = True) -> dict:
  payload = {
    "research": RESEARCH_REFERENCES,
    "classicResearch": CLASSIC_QUANT_REFERENCES,
  }
  if not symbol:
    return payload

  with ThreadPoolExecutor(max_workers=2) as executor:
    snapshot_future = executor.submit(build_ticker_snapshot, symbol)
    snapshot = snapshot_future.result()
    web_future = None
    if use_web:
      company_query = f"{snapshot['name']} {snapshot['exchange']} latest news outlook risk"
      web_future = executor.submit(duckduckgo_search, company_query)
    web_results: list[dict] = web_future.result() if web_future is not None else []

  config = load_config()
  titles = [item.get("title", "") for item in web_results[:5] if item.get("title")]
  prompt = "\n".join(
    [
      "You are an academy explainer inside a professional market dashboard.",
      "Write one concise paragraph that explains the active ticker using classic signals first, then mention whether modern overlays agree or disagree, then note the main live catalyst focus.",
      f"Ticker snapshot: {json.dumps({'symbol': snapshot['symbol'], 'name': snapshot['name'], 'direction': snapshot['forecast']['direction'], 'agreement': snapshot['forecast'].get('models', {}).get('agreement', {}), 'classicSummary': snapshot.get('classicQuant', {}).get('summary', ''), 'headlines': snapshot.get('headlines', [])[:4]}, ensure_ascii=True)}",
      f"Web result titles: {json.dumps(titles, ensure_ascii=True)}",
    ]
  )
  summary = generate_local_llm_answer(prompt, config, timeout=8) if use_llm else None
  if not summary:
    summary = (
      f"{snapshot['name']} is currently in a {snapshot['forecast']['direction'].lower()} setup. "
      f"{snapshot.get('classicQuant', {}).get('summary', '')} "
      f"{snapshot['forecast'].get('models', {}).get('agreement', {}).get('summary', '')} "
      f"{summarize_web_focus(symbol, snapshot, web_results)}"
    ).strip()

  agreement = snapshot["forecast"].get("models", {}).get("agreement", {})
  cards = [
    {
      "title": "Classic stack read",
      "body": snapshot.get("classicQuant", {}).get("summary", "Classic signals are still loading."),
    },
    {
      "title": "Modern overlay read",
      "body": snapshot["forecast"].get("models", {}).get("modern", {}).get("summary", "Modern overlay data is unavailable."),
    },
    {
      "title": "Agreement check",
      "body": f"{agreement.get('summary', 'Agreement data unavailable.')} Confidence score: {agreement.get('score', 0):.0f}/100.",
    },
    {
      "title": "Live catalyst focus",
      "body": summarize_web_focus(symbol, snapshot, web_results),
    },
  ]

  payload.update(
    {
      "symbol": snapshot["symbol"],
      "summary": summary,
      "cards": cards,
      "sources": web_results[:5],
      "updatedAt": datetime.now(timezone.utc).isoformat(),
    }
  )
  return payload


def infer_radar_hotspots(items: list[dict]) -> list[dict]:
  scores: dict[str, dict] = {}
  for item in items:
    title = (item.get("title") or "").lower()
    if not title:
      continue
    for region, keywords in RADAR_REGION_KEYWORDS.items():
      matches = sum(1 for keyword in keywords if keyword in title)
      if not matches:
        continue
      current = scores.setdefault(region, {"region": region, "score": 0, "headline": item.get("title", "")})
      current["score"] += matches
      if not current.get("headline"):
        current["headline"] = item.get("title", "")
  ordered = sorted(scores.values(), key=lambda item: item["score"], reverse=True)
  return ordered[:4]


def build_market_radar(symbol: str | None = None) -> dict:
  return memory_cached_value(
    f"market-radar:{(symbol or 'global').upper()}",
    5 * 60,
    lambda: build_market_radar_uncached(symbol),
  ) or {}


def build_market_radar_uncached(symbol: str | None = None) -> dict:
  queries = [EVENT_CATEGORY_QUERIES["world"], EVENT_CATEGORY_QUERIES["war"], EVENT_CATEGORY_QUERIES["business"]]
  with ThreadPoolExecutor(max_workers=5) as executor:
    future_map = {
      "world_google": executor.submit(fetch_google_news_rss, EVENT_CATEGORY_QUERIES["world"]),
      "war_google": executor.submit(fetch_google_news_rss, EVENT_CATEGORY_QUERIES["war"]),
      "business_google": executor.submit(fetch_google_news_rss, EVENT_CATEGORY_QUERIES["business"]),
      "world_popular": executor.submit(fetch_popular_rss_items, "world"),
      "business_popular": executor.submit(fetch_popular_rss_items, "business"),
    }
    if symbol:
      company = fallback_meta(symbol)
      queries.append(f"{company['name']} latest news {company['exchange']}")
      future_map["company_google"] = executor.submit(fetch_google_news_rss, queries[-1])

    items: list[dict] = []
    for future in future_map.values():
      try:
        items.extend(future.result())
      except Exception:
        continue

  unique_items = filter_market_relevant_items(merge_event_items(items), "world", symbol)
  unique_items = [
    item
    for item in unique_items
    if item_age_hours(item) <= 96 or radar_priority_score(item, symbol) >= 20
  ]
  unique_items = sorted(unique_items, key=lambda item: radar_priority_score(item, symbol), reverse=True)[:8]

  hotspots = infer_radar_hotspots(unique_items)
  titles = [item.get("title", "") for item in unique_items[:6] if item.get("title")]
  config = load_config()
  summary = ""
  if titles:
    prompt = "\n".join(
      [
        "You are a concise global market radar assistant.",
        f"Headlines: {json.dumps(titles, ensure_ascii=True)}",
        f"Hotspots: {json.dumps(hotspots, ensure_ascii=True)}",
        "Write one compact market-risk summary sentence, focused on what geographies are driving sentiment and why markets care.",
      ]
    )
    summary = generate_local_llm_answer(prompt, config) or ""
  if not summary:
    summary = "Global event radar is scanning live developments across geopolitics, business, and company-specific catalysts."

  return {
    "summary": summary,
    "headlines": titles[:6],
    "hotspots": hotspots,
    "items": unique_items[:6],
  }


def enrich_market_radar(radar: dict, macro_pulse: list[dict] | None = None, active_snapshot: dict | None = None) -> dict:
  enriched = dict(radar or {})
  macro_pulse = macro_pulse or []
  active_snapshot = active_snapshot or {}
  radar_items = enriched.get("items") or []
  sentiment = radar_sentiment(radar_items, active_snapshot, macro_pulse)
  macro_items = []
  for item in macro_pulse[:3]:
    macro_items.append(
      {
        "label": item.get("label", "Macro"),
        "value": item.get("value", ""),
        "trend": item.get("trend", ""),
      }
    )

  micro_items = []
  focus = active_snapshot.get("eventFocus") or {}
  if focus.get("label"):
    micro_items.append(
      {
        "label": "Catalyst focus",
        "value": focus.get("label", ""),
        "trend": focus.get("reason", ""),
      }
    )
  forecast = active_snapshot.get("forecast") or {}
  if forecast.get("direction"):
    micro_items.append(
      {
        "label": "Model bias",
        "value": f"{forecast.get('direction', 'Neutral')} {forecast.get('confidence', 0):.0f}%",
        "trend": f"{forecast.get('eventPressureLabel', 'Low')} event pressure",
      }
    )
  if active_snapshot.get("volume") is not None:
    volume_value = float(active_snapshot.get("volume", 0) or 0)
    if volume_value >= 1_000_000_000:
      volume_text = f"{volume_value / 1_000_000_000:.1f}B"
    elif volume_value >= 1_000_000:
      volume_text = f"{volume_value / 1_000_000:.1f}M"
    elif volume_value >= 1_000:
      volume_text = f"{volume_value / 1_000:.0f}K"
    else:
      volume_text = f"{volume_value:.0f}"
    micro_items.append(
      {
        "label": "Liquidity",
        "value": volume_text,
        "trend": f"{active_snapshot.get('exchange', 'Market')} traded volume",
      }
    )

  enriched["macroFactors"] = macro_items
  enriched["microFactors"] = micro_items
  enriched["sentiment"] = sentiment
  return enriched


def fetch_yahoo_rss_uncached(symbol: str) -> list[str]:
  quoted = urllib.parse.quote(symbol)
  xml_text = text_get(f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={quoted}&region=US&lang=en-US")
  if not xml_text:
    return []
  try:
    root = ET.fromstring(xml_text)
  except ET.ParseError:
    return []
  items = []
  for item in root.findall(".//item/title"):
    if item.text:
      items.append(item.text.strip())
    if len(items) >= 6:
      break
  return items


def fetch_yahoo_rss(symbol: str) -> list[str]:
  return memory_cached_value(
    f"yahoo-rss:{symbol.upper()}",
    15 * 60,
    lambda: fetch_yahoo_rss_uncached(symbol),
  ) or []


def fetch_alpha_vantage_news(symbol: str, api_key: str) -> list[str]:
  if not api_key:
    return []
  query = urllib.parse.urlencode(
    {
      "function": "NEWS_SENTIMENT",
      "tickers": symbol,
      "limit": "8",
      "apikey": api_key,
    }
  )
  payload = json_get(f"https://www.alphavantage.co/query?{query}")
  items = []
  for story in (payload or {}).get("feed", []):
    title = story.get("title")
    if title:
      items.append(title)
  return items[:6]


def headline_texts_from_search_uncached(query: str) -> list[str]:
  return [item.get("title", "") for item in duckduckgo_search(query)[:6] if item.get("title")]


def headline_texts_from_search(query: str) -> list[str]:
  normalized = re.sub(r"\s+", " ", query.strip().lower())
  return memory_cached_value(
    f"headline-search:{normalized}",
    15 * 60,
    lambda: headline_texts_from_search_uncached(query),
  ) or []


def dedupe_list(items: list[str]) -> list[str]:
  seen = set()
  ordered = []
  for item in items:
    cleaned = item.strip()
    if not cleaned:
      continue
    key = cleaned.lower()
    if key in seen:
      continue
    seen.add(key)
    ordered.append(cleaned)
  return ordered


def headline_sentiment(headlines: list[str]) -> dict:
  positive_words = {
    "beats", "beat", "growth", "surge", "rally", "approval", "wins", "win", "partnership",
    "contract", "upgrade", "record", "strong", "expansion", "launch", "profit", "optimism",
  }
  negative_words = {
    "cuts", "cut", "probe", "lawsuit", "downgrade", "fall", "drop", "warning", "miss", "delay",
    "ban", "fine", "weak", "slump", "decline", "recall", "antitrust", "risk",
  }
  text = " ".join(headlines).lower()
  pos = sum(word in text for word in positive_words)
  neg = sum(word in text for word in negative_words)
  score = clamp((pos - neg) / max(len(headlines), 1), -1.0, 1.0)
  label = "Positive" if score > 0.22 else "Negative" if score < -0.22 else "Mixed"
  return {"score": score, "label": label, "positiveHits": pos, "negativeHits": neg}


def radar_sentiment(items: list[dict], active_snapshot: dict | None = None, macro_pulse: list[dict] | None = None) -> dict:
  active_snapshot = active_snapshot or {}
  macro_pulse = macro_pulse or []
  if not items:
    return {"score": 0.0, "label": "Balanced", "tone": "neutral", "driver": "No live radar items", "positiveHits": 0, "negativeHits": 0}
  positive_terms = {
    "deal", "partnership", "approval", "beat", "beats", "cut rates", "stimulus", "ceasefire", "recovery", "eases", "expansion", "wins",
  }
  negative_terms = {
    "war", "attack", "bomb", "missile", "tariff", "sanction", "downgrade", "probe", "lawsuit", "recall", "inflation", "surge in yields",
    "selloff", "cut guidance", "miss", "slump", "ban", "fine", "escalation",
  }
  positive_score = 0.0
  negative_score = 0.0
  strongest_reason = "Mixed headline stack"
  strongest_abs = 0.0
  for item in items[:8]:
    title = str(item.get("title", "")).lower()
    significance = float(item.get("significance") or 1.0)
    freshness = max(0.3, 1.0 - (item_age_hours(item) / 72))
    weight = significance * freshness
    item_score = 0.0
    for term in positive_terms:
      if term in title:
        item_score += 1.0
    for term in negative_terms:
      if term in title:
        item_score -= 1.15
    category = str(item.get("category") or "").lower()
    if category in {"war", "world"}:
      item_score -= 0.5
    if category in {"deals", "partnerships"}:
      item_score += 0.35
    if category in {"layoffs"}:
      item_score -= 0.45
    weighted = item_score * weight
    if weighted > 0:
      positive_score += weighted
    elif weighted < 0:
      negative_score += abs(weighted)
    if abs(weighted) > strongest_abs:
      strongest_abs = abs(weighted)
      strongest_reason = item.get("title") or strongest_reason

  macro_bias = 0.0
  macro_text = " ".join(f"{item.get('label', '')} {item.get('trend', '')} {item.get('value', '')}".lower() for item in macro_pulse[:3])
  if "risk off" in macro_text or "yield" in macro_text and "higher" in macro_text:
    macro_bias -= 0.2
  if "risk on" in macro_text or "cooling" in macro_text or "easing" in macro_text:
    macro_bias += 0.15
  if str((active_snapshot.get("eventFocus") or {}).get("category") or "") == "war":
    macro_bias -= 0.2

  raw_score = clamp((positive_score - negative_score) / max(1.0, positive_score + negative_score), -1.0, 1.0)
  score = clamp(raw_score + macro_bias, -1.0, 1.0)
  if score >= 0.25:
    label = "Risk-on"
    tone = "positive"
  elif score <= -0.25:
    label = "Risk-off"
    tone = "negative"
  else:
    label = "Balanced"
    tone = "neutral"
  return {
    "score": score,
    "label": label,
    "tone": tone,
    "driver": strongest_reason,
    "positiveHits": round(positive_score, 2),
    "negativeHits": round(negative_score, 2),
  }


def categorized_signal(headlines: list[str], keywords: set[str], fallback_label: str) -> dict:
  for headline in headlines:
    lowered = headline.lower()
    if any(keyword in lowered for keyword in keywords):
      return {"label": fallback_label, "headline": headline}
  return {"label": fallback_label, "headline": "No strong current signal detected."}


def extract_signal_map(headlines: list[str], symbol: str, sector: str, industry: str) -> dict:
  policy = categorized_signal(
    headlines,
    {
      "government", "policy", "rbi", "fed", "budget", "tariff", "tax", "regulator", "regulatory",
      "parliament", "ministry", "sec", "fda", "approval", "probe", "ban",
    },
    "Policy & regulation",
  )
  deals = categorized_signal(
    headlines,
    {
      "deal", "partnership", "contract", "agreement", "collaboration", "alliance", "order",
      "acquire", "acquisition", "merger", "stake", "joint venture",
    },
    "Deals & partnerships",
  )
  industry_signal = categorized_signal(
    headlines,
    {
      "sector", "industry", "demand", "supply", "pricing", "competitor", "telecom", "bank", "pharma",
      "credit", "subscriber", "tower", "generic", "energy", "chip", "semiconductor",
    },
    "Adjacent industry",
  )
  earnings = categorized_signal(
    headlines,
    {"earnings", "revenue", "profit", "margin", "guidance", "results", "ebitda", "quarter"},
    "Financial results",
  )
  sentiment = headline_sentiment(headlines)
  return {
    "sentiment": sentiment,
    "signals": [policy, deals, industry_signal, earnings],
    "sector": sector or "n/a",
    "industry": industry or "n/a",
    "symbol": symbol,
  }


def infer_event_focus(headlines: list[str], signal_map: dict) -> dict:
  text = " ".join(headlines).lower()
  categories = {
    "war": {
      "score": sum(keyword in text for keyword in {"war", "missile", "bomb", "ceasefire", "attack", "conflict", "iran", "israel", "russia", "ukraine", "tariff", "sanction"}),
      "reason": "Geopolitical escalation or policy shocks are dominating the ticker risk map.",
      "label": "Geopolitics",
    },
    "layoffs": {
      "score": sum(keyword in text for keyword in {"layoff", "job cut", "workforce", "restructure", "restructuring", "cost cut", "headcount"}),
      "reason": "Workforce actions and restructuring headlines are the clearest stock-moving catalysts.",
      "label": "Restructuring",
    },
    "partnerships": {
      "score": 2 if signal_map["signals"][1]["headline"] != "No strong current signal detected." and any(keyword in signal_map["signals"][1]["headline"].lower() for keyword in {"partnership", "collaboration", "alliance", "joint venture"}) else 0,
      "reason": "Partnership and alliance headlines appear to be the strongest current stock driver.",
      "label": "Partnerships",
    },
    "deals": {
      "score": 2 if signal_map["signals"][1]["headline"] != "No strong current signal detected." else 0,
      "reason": "Deal flow and transaction headlines are shaping the current move.",
      "label": "Deal flow",
    },
    "brands": {
      "score": sum(keyword in text for keyword in {"brand", "launch", "product", "campaign", "consumer", "retail"}),
      "reason": "Brand and product headlines are carrying the clearest demand signal.",
      "label": "Brands",
    },
    "business": {
      "score": 2 if signal_map["signals"][3]["headline"] != "No strong current signal detected." else 1,
      "reason": "Business and earnings updates are the main drivers behind the current move.",
      "label": "Business",
    },
    "world": {
      "score": 2 if signal_map["signals"][0]["headline"] != "No strong current signal detected." else 0,
      "reason": "Macro and policy headlines are outweighing company-only narratives right now.",
      "label": "Macro policy",
    },
  }
  best_category, best_payload = max(categories.items(), key=lambda item: item[1]["score"])
  if best_payload["score"] <= 0:
    best_category = "business"
    best_payload = categories["business"]
  return {
    "category": best_category,
    "label": best_payload["label"],
    "reason": best_payload["reason"],
  }


CHART_RANGE_CONFIG = {
  "1D": ("1d", "5m"),
  "3D": ("5d", "15m"),
  "5D": ("5d", "30m"),
  "1M": ("1mo", "1d"),
  "1Y": ("1y", "1wk"),
  "2Y": ("2y", "1wk"),
  "3Y": ("5y", "1mo"),
  "5Y": ("5y", "1mo"),
  "MAX": ("max", "1mo"),
}

HISTORY_PREFETCH_RANGES = ["1D", "3D", "5D", "1M", "1Y"]


def history_points_from_meta(closes: list[float], meta: dict) -> list[dict]:
  timestamps = meta.get("timestamps") or []
  if not isinstance(timestamps, list) or len(timestamps) != len(closes):
    return [{"value": round(float(value), 4)} for value in closes]
  return [
    {
      "value": round(float(value), 4),
      "timestamp": timestamp,
    }
    for value, timestamp in zip(closes, timestamps)
  ]


def history_cache_is_fresh(symbol: str, chart_range: str) -> bool:
  cached = load_cached_history(symbol, chart_range)
  if not cached:
    normalized_range = chart_range.upper()
    interval = CHART_RANGE_CONFIG.get(normalized_range, CHART_RANGE_CONFIG["1M"])[1]
    historical_points = load_historical_records(symbol, interval, limit=2)
    if not historical_points:
      return False
    latest_age = timestamp_age_seconds(historical_points[-1].get("timestamp"))
    return latest_age is not None and latest_age <= history_cache_ttl(normalized_range)
  closes, _, _, updated_at = cached
  if len(closes) < 2:
    return False
  try:
    age_seconds = max(0.0, (datetime.now(timezone.utc) - datetime.fromisoformat(updated_at)).total_seconds())
  except ValueError:
    return False
  return age_seconds <= history_cache_ttl(chart_range)


def timestamp_age_seconds(value: str | None) -> float | None:
  if not value:
    return None
  try:
    timestamp = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
  except ValueError:
    return None
  if timestamp.tzinfo is None:
    timestamp = timestamp.replace(tzinfo=timezone.utc)
  delta_seconds = (datetime.now(timezone.utc) - timestamp.astimezone(timezone.utc)).total_seconds()
  if delta_seconds < -300:
    return None
  return max(0.0, delta_seconds)


def extract_yahoo_history_payload(chart: dict) -> tuple[list[float], dict]:
  quote_indicator = (((chart.get("indicators") or {}).get("quote") or [{}])[0] or {})
  raw_closes = quote_indicator.get("close") or []
  raw_volumes = quote_indicator.get("volume") or []
  raw_timestamps = chart.get("timestamp") or []
  closes = []
  timestamps = []
  volumes = []
  for index, raw_close in enumerate(raw_closes):
    if not isinstance(raw_close, (int, float)):
      continue
    closes.append(float(raw_close))
    if index < len(raw_timestamps) and isinstance(raw_timestamps[index], (int, float)):
      timestamps.append(datetime.fromtimestamp(raw_timestamps[index], tz=timezone.utc).isoformat())
    if index < len(raw_volumes) and isinstance(raw_volumes[index], (int, float)):
      volumes.append(float(raw_volumes[index]))
  meta = dict(chart.get("meta") or {})
  if timestamps:
    meta["timestamps"] = timestamps
  if volumes and len(volumes) == len(closes):
    meta["volumes"] = volumes
  return closes, meta


def google_finance_timezone(google_symbol: str, exchange_hint: str = "") -> str:
  exchange = ((google_symbol or "").split(":")[-1] if ":" in (google_symbol or "") else exchange_hint or "").upper()
  return {
    "NSE": "Asia/Kolkata",
    "BOM": "Asia/Kolkata",
    "INDEXNSE": "Asia/Kolkata",
    "INDEXBOM": "Asia/Kolkata",
    "NASDAQ": "America/New_York",
    "NYSE": "America/New_York",
    "ASX": "Australia/Sydney",
    "LON": "Europe/London",
    "TYO": "Asia/Tokyo",
    "ETR": "Europe/Berlin",
  }.get(exchange, "UTC")


def timestamp_from_google_block(block: list, time_zone: str = "UTC") -> str | None:
  if not isinstance(block, list) or len(block) < 3:
    return None
  try:
    year = int(block[0])
    month = int(block[1])
    day = int(block[2])
    if month == 0:
      month = 1
    if month < 1 or month > 12:
      month = max(1, min(12, month + 1))
    hour = int(block[3]) if len(block) > 3 else 0
    minute = int(block[4]) if len(block) > 4 else 0
    tz = ZoneInfo(time_zone)
    return datetime(year, month, day, hour, minute, tzinfo=tz).astimezone(timezone.utc).isoformat()
  except (TypeError, ValueError, ZoneInfoNotFoundError):
    return None


def history_symbol_candidates(symbol: str) -> list[str]:
  symbol = (symbol or "").upper()
  candidates = [symbol]
  if symbol.endswith(".BO"):
    root = symbol[:-3]
    candidates.append(f"{root}.NS")
  elif symbol.endswith(".NS"):
    root = symbol[:-3]
    candidates.append(f"{root}.BO")
  return dedupe_list([candidate for candidate in candidates if candidate])


def build_history(symbol: str, chart_range: str = "1M", allow_live_refresh: bool = True) -> tuple[list[float], dict]:
  normalized_range = chart_range.upper()
  inflight_key = f"{normalize_symbol(symbol)}::{normalized_range}"
  if allow_live_refresh:
    with HISTORY_INFLIGHT_LOCK:
      existing_event = HISTORY_INFLIGHT.get(inflight_key)
      if existing_event:
        should_fetch = False
      else:
        existing_event = threading.Event()
        HISTORY_INFLIGHT[inflight_key] = existing_event
        should_fetch = True
    if not should_fetch:
      existing_event.wait(timeout=12)
      return build_history(symbol, normalized_range, allow_live_refresh=False)
  else:
    existing_event = None
    should_fetch = False

  interval = CHART_RANGE_CONFIG.get(normalized_range, CHART_RANGE_CONFIG["1M"])[1]
  try:
    historical_points = load_historical_records(symbol, interval, limit=380 if normalized_range == "1Y" else 40)
    if len(historical_points) >= 2:
      values = [point["value"] for point in historical_points]
      timestamps = [point["timestamp"] for point in historical_points if point.get("timestamp")]
      latest_age = timestamp_age_seconds(timestamps[-1] if timestamps else None)
      historical_meta = {
        "timestamps": timestamps if len(timestamps) == len(values) else [],
        "historySource": historical_points[-1].get("source", "Historical records"),
        "historyCacheState": "fresh" if latest_age is not None and latest_age <= history_cache_ttl(normalized_range) else "stale",
        "historyCachedAt": timestamps[-1] if timestamps else datetime.now(timezone.utc).isoformat(),
      }
      if latest_age is not None and latest_age <= history_cache_ttl(normalized_range):
        return values, historical_meta
      if not allow_live_refresh:
        return values, historical_meta
    cached = load_cached_history(symbol, normalized_range)
    if cached:
      closes, meta, source, updated_at = cached
      try:
        age_seconds = max(
          0,
          (datetime.now(timezone.utc) - datetime.fromisoformat(updated_at)).total_seconds(),
        )
      except ValueError:
        age_seconds = history_cache_ttl(normalized_range) + 1
      cached_timestamps = meta.get("timestamps") or []
      cached_latest_age = timestamp_age_seconds(cached_timestamps[-1]) if cached_timestamps else age_seconds
      cache_timestamp_valid = cached_latest_age is not None
      if len(closes) >= 2 and age_seconds <= history_cache_ttl(normalized_range) and cache_timestamp_valid:
        return closes, build_cached_meta(meta, source or "Local cache", updated_at)
      if len(closes) >= 2 and not allow_live_refresh:
        return closes, build_cached_meta(meta, source or "Local cache", updated_at, stale=True)

    if not allow_live_refresh:
      return [], {}

    range_value, interval = CHART_RANGE_CONFIG.get(normalized_range, CHART_RANGE_CONFIG["1M"])
    config = load_config()
    alpha_key = config.get("alphaVantageApiKey", "").strip()
    for candidate_symbol in history_symbol_candidates(symbol):
      chart = fetch_yahoo_chart(candidate_symbol, range_value=range_value, interval=interval)
      if chart:
        closes, meta = extract_yahoo_history_payload(chart)
        if len(closes) >= 2:
          if candidate_symbol != symbol:
            meta["historyMappedSymbol"] = candidate_symbol
          save_historical_records(symbol, interval, history_points_from_meta(closes, meta), "Yahoo Chart")
          save_history_cache(symbol, normalized_range, closes, meta, "Yahoo Chart")
          return closes, build_cached_meta(meta, "Yahoo Chart", datetime.now(timezone.utc).isoformat())

      google_closes, google_meta = fetch_google_finance_history(candidate_symbol, fallback_meta(candidate_symbol).get("exchange", ""), normalized_range)
      if len(google_closes) >= 2:
        if candidate_symbol != symbol:
          google_meta["historyMappedSymbol"] = candidate_symbol
        google_interval = interval
        save_historical_records(symbol, google_interval, history_points_from_meta(google_closes, google_meta), google_meta.get("historySource", "Google Finance Page"))
        save_history_cache(symbol, normalized_range, google_closes, google_meta, google_meta.get("historySource", "Google Finance Page"))
        return google_closes, build_cached_meta(
          google_meta,
          google_meta.get("historySource", "Google Finance Page"),
          datetime.now(timezone.utc).isoformat(),
        )

      if alpha_key:
        alpha_closes, alpha_meta = fetch_alpha_vantage_history(candidate_symbol, alpha_key, normalized_range)
        if len(alpha_closes) >= 2:
          if candidate_symbol != symbol:
            alpha_meta["historyMappedSymbol"] = candidate_symbol
          save_historical_records(symbol, interval, history_points_from_meta(alpha_closes, alpha_meta), alpha_meta.get("historySource", "Alpha Vantage Daily Adjusted"))
          save_history_cache(symbol, normalized_range, alpha_closes, alpha_meta, alpha_meta.get("historySource", "Alpha Vantage Daily Adjusted"))
          return alpha_closes, build_cached_meta(
            alpha_meta,
            alpha_meta.get("historySource", "Alpha Vantage Daily Adjusted"),
            datetime.now(timezone.utc).isoformat(),
          )

      stooq_closes, stooq_meta = fetch_stooq_history(candidate_symbol, fallback_meta(candidate_symbol).get("exchange", ""), normalized_range)
      if len(stooq_closes) >= 2:
        if candidate_symbol != symbol:
          stooq_meta["historyMappedSymbol"] = candidate_symbol
        save_historical_records(symbol, interval, history_points_from_meta(stooq_closes, stooq_meta), stooq_meta.get("historySource", "Stooq CSV"))
        save_history_cache(symbol, normalized_range, stooq_closes, stooq_meta, stooq_meta.get("historySource", "Stooq CSV"))
        return stooq_closes, build_cached_meta(
          stooq_meta,
          stooq_meta.get("historySource", "Stooq CSV"),
          datetime.now(timezone.utc).isoformat(),
        )

    if cached:
      closes, meta, source, updated_at = cached
      if len(closes) >= 2:
        return closes, build_cached_meta(meta, source or "Local cache", updated_at, stale=True)
    return [], {}
  finally:
    if allow_live_refresh and should_fetch and existing_event:
      with HISTORY_INFLIGHT_LOCK:
        HISTORY_INFLIGHT.pop(inflight_key, None)
        existing_event.set()


def history_warmup_key(symbols: list[str], ranges: list[str]) -> str:
  cleaned_symbols = ",".join(sorted({normalize_symbol(symbol) for symbol in symbols if symbol}))
  cleaned_ranges = ",".join(sorted({(item or "").upper() for item in ranges if item}))
  return f"{cleaned_symbols}::{cleaned_ranges}"


def run_history_warmup(job_key: str, symbols: list[str], ranges: list[str]) -> None:
  with HISTORY_WARMUP_LOCK:
    job = HISTORY_WARMUP_JOBS.get(job_key, {})
    job.update({"status": "running", "startedAt": datetime.now(timezone.utc).isoformat(), "completed": 0, "errors": []})
    HISTORY_WARMUP_JOBS[job_key] = job
  total = max(1, len(symbols) * len(ranges))
  for symbol in symbols:
    for chart_range in ranges:
      if _SERVER_STOPPING.is_set():
        with HISTORY_WARMUP_LOCK:
          if job_key in HISTORY_WARMUP_JOBS:
            HISTORY_WARMUP_JOBS[job_key]["status"] = "cancelled"
            HISTORY_WARMUP_JOBS[job_key]["finishedAt"] = datetime.now(timezone.utc).isoformat()
        return
      try:
        if not history_cache_is_fresh(symbol, chart_range):
          build_history(symbol, chart_range, allow_live_refresh=True)
      except Exception as error:
        with HISTORY_WARMUP_LOCK:
          if job_key in HISTORY_WARMUP_JOBS:
            HISTORY_WARMUP_JOBS[job_key].setdefault("errors", []).append(f"{symbol}:{chart_range}:{error}")
      finally:
        with HISTORY_WARMUP_LOCK:
          if job_key not in HISTORY_WARMUP_JOBS:
            return
          HISTORY_WARMUP_JOBS[job_key]["completed"] = min(total, int(HISTORY_WARMUP_JOBS[job_key].get("completed", 0)) + 1)
          HISTORY_WARMUP_JOBS[job_key]["total"] = total
  with HISTORY_WARMUP_LOCK:
    if job_key in HISTORY_WARMUP_JOBS:
      HISTORY_WARMUP_JOBS[job_key]["status"] = "done"
      HISTORY_WARMUP_JOBS[job_key]["finishedAt"] = datetime.now(timezone.utc).isoformat()


def start_history_warmup(symbols: list[str], ranges: list[str] | None = None, reason: str = "dashboard") -> dict:
  cleaned_symbols = list(dict.fromkeys([normalize_symbol(symbol) for symbol in symbols if symbol]))
  cleaned_ranges = [item.upper() for item in (ranges or HISTORY_PREFETCH_RANGES) if item.upper() in CHART_RANGE_CONFIG]
  if not cleaned_symbols or not cleaned_ranges:
    return {"status": "skipped", "reason": "No symbols or ranges to warm."}
  job_key = history_warmup_key(cleaned_symbols, cleaned_ranges)
  with HISTORY_WARMUP_LOCK:
    existing = HISTORY_WARMUP_JOBS.get(job_key)
    if existing and existing.get("status") in {"queued", "running"}:
      return {"status": existing.get("status"), "jobKey": job_key, "total": existing.get("total", 0), "completed": existing.get("completed", 0)}
    HISTORY_WARMUP_JOBS[job_key] = {
      "status": "queued",
      "jobKey": job_key,
      "symbols": cleaned_symbols,
      "ranges": cleaned_ranges,
      "reason": reason,
      "total": len(cleaned_symbols) * len(cleaned_ranges),
      "completed": 0,
      "queuedAt": datetime.now(timezone.utc).isoformat(),
    }
  thread = threading.Thread(target=run_history_warmup, args=(job_key, cleaned_symbols, cleaned_ranges), daemon=True)
  thread.start()
  return {"status": "queued", "jobKey": job_key, "total": len(cleaned_symbols) * len(cleaned_ranges), "completed": 0}


def history_warmup_status() -> dict:
  with HISTORY_WARMUP_LOCK:
    jobs = list(HISTORY_WARMUP_JOBS.values())[-12:]
  script_status = backend_script_status()
  quote_providers = quote_provider_status()
  return {
    "jobs": jobs,
    "active": [job for job in jobs if job.get("status") in {"queued", "running"}],
    "scripts": script_status["jobs"],
    "scriptActive": script_status["active"],
    "quoteProviders": quote_providers,
    "quoteProviderActive": [provider for provider in quote_providers if provider.get("status") == "available"],
  }


def newest_mtime(paths: list[Path]) -> float:
  stamps = []
  for path in paths:
    try:
      if path.exists():
        stamps.append(path.stat().st_mtime)
    except OSError:
      continue
  return max(stamps) if stamps else 0.0


def backend_script_due(spec: dict, now: float | None = None) -> tuple[bool, str]:
  now = now or time.time()
  cadence = int(spec.get("cadenceSeconds") or 0)
  newest = newest_mtime(spec.get("freshnessPaths") or [])
  if newest and cadence and now - newest < cadence:
    age_minutes = max(0, int((now - newest) / 60))
    return False, f"local manifest fresh ({age_minutes}m old)"
  last_run = BACKEND_SCRIPT_LAST_RUN.get(spec["id"])
  if last_run:
    try:
      last_ts = datetime.fromisoformat(last_run).timestamp()
    except ValueError:
      last_ts = 0
    if cadence and now - last_ts < cadence:
      age_minutes = max(0, int((now - last_ts) / 60))
      return False, f"last refresh {age_minutes}m ago"
  return True, "stale or missing local manifest"


def run_backend_refresh_job(job_key: str) -> None:
  with BACKEND_SCRIPT_LOCK:
    job = BACKEND_SCRIPT_JOBS.get(job_key, {})
    job.update({"status": "running", "startedAt": datetime.now(timezone.utc).isoformat(), "completed": 0})
    BACKEND_SCRIPT_JOBS[job_key] = job
  for index, step in enumerate(job.get("steps") or []):
    if step.get("status") == "skipped":
      with BACKEND_SCRIPT_LOCK:
        BACKEND_SCRIPT_JOBS[job_key]["completed"] = index + 1
      continue
    script_name = str(step.get("script") or "")
    script_path = BASE_DIR / "scripts" / script_name
    allowed_scripts = {
      spec["script"] for spec in BACKEND_REFRESH_SCRIPTS
    } | {
      operator_step["script"]
      for job_spec in OPERATOR_JOB_SPECS.values()
      for operator_step in job_spec["steps"]
    }
    if script_name not in allowed_scripts or not script_path.is_file():
      error = f"Blocked unregistered maintenance script: {script_name}"
      with BACKEND_SCRIPT_LOCK:
        BACKEND_SCRIPT_JOBS[job_key]["steps"][index].update({"status": "error", "error": error})
        BACKEND_SCRIPT_JOBS[job_key].setdefault("errors", []).append(error)
        BACKEND_SCRIPT_JOBS[job_key]["completed"] = index + 1
      continue
    script_args = [str(value) for value in (step.get("args") or [])]
    timeout_seconds = max(10, min(int(step.get("timeoutSeconds") or BACKEND_SCRIPT_TIMEOUT_SECONDS), 900))
    with BACKEND_SCRIPT_LOCK:
      BACKEND_SCRIPT_JOBS[job_key]["steps"][index].update({"status": "running", "startedAt": datetime.now(timezone.utc).isoformat()})
    try:
      result = subprocess.run(
        [sys.executable, str(script_path), *script_args],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
      )
      output = (result.stdout or result.stderr or "").strip()
      if result.returncode:
        raise RuntimeError((result.stderr or output or f"{script_name} exited {result.returncode}").strip())
      try:
        parsed_output = json.loads(output) if output else {}
      except json.JSONDecodeError:
        parsed_output = {"output": output[-1200:]}
      with BACKEND_SCRIPT_LOCK:
        BACKEND_SCRIPT_JOBS[job_key]["steps"][index].update(
          {
            "status": "done",
            "finishedAt": datetime.now(timezone.utc).isoformat(),
            "result": parsed_output,
          }
        )
        BACKEND_SCRIPT_LAST_RUN[step.get("id") or script_name] = datetime.now(timezone.utc).isoformat()
    except subprocess.TimeoutExpired:
      error = f"{script_name} exceeded {timeout_seconds}s timeout"
      with BACKEND_SCRIPT_LOCK:
        BACKEND_SCRIPT_JOBS[job_key]["steps"][index].update({"status": "error", "error": error})
        BACKEND_SCRIPT_JOBS[job_key].setdefault("errors", []).append(error)
    except Exception as error:
      with BACKEND_SCRIPT_LOCK:
        BACKEND_SCRIPT_JOBS[job_key]["steps"][index].update({"status": "error", "error": str(error)})
        BACKEND_SCRIPT_JOBS[job_key].setdefault("errors", []).append(str(error))
    finally:
      with BACKEND_SCRIPT_LOCK:
        BACKEND_SCRIPT_JOBS[job_key]["completed"] = index + 1
  with BACKEND_SCRIPT_LOCK:
    final_job = BACKEND_SCRIPT_JOBS.get(job_key, {})
    final_job["status"] = "error" if final_job.get("errors") else "done"
    final_job["finishedAt"] = datetime.now(timezone.utc).isoformat()
    BACKEND_SCRIPT_JOBS[job_key] = final_job


def start_dashboard_backend_refresh(symbols: list[str], region_key: str | None = None) -> dict:
  now = time.time()
  with BACKEND_SCRIPT_LOCK:
    active = next((job for job in reversed(list(BACKEND_SCRIPT_JOBS.values())) if job.get("status") in {"queued", "running"}), None)
    if active:
      return {"status": active.get("status"), "jobKey": active.get("jobKey"), "detail": "backend refresh already running"}
  steps = []
  for spec in BACKEND_REFRESH_SCRIPTS:
    due, reason = backend_script_due(spec, now)
    steps.append(
      {
        "id": spec["id"],
        "label": spec["label"],
        "script": spec["script"],
        "status": "queued" if due else "skipped",
        "reason": reason,
      }
    )
  job_key = f"backend-refresh-{int(now * 1000)}"
  job = {
    "status": "queued" if any(step["status"] == "queued" for step in steps) else "done",
    "jobKey": job_key,
    "reason": "dashboard-loaded",
    "region": region_key or "global",
    "symbols": list(dict.fromkeys(symbols))[:24],
    "total": len(steps),
    "completed": sum(1 for step in steps if step["status"] == "skipped"),
    "steps": steps,
    "queuedAt": datetime.now(timezone.utc).isoformat(),
  }
  if job["status"] == "done":
    job["finishedAt"] = job["queuedAt"]
  with BACKEND_SCRIPT_LOCK:
    BACKEND_SCRIPT_JOBS[job_key] = job
  if job["status"] == "queued":
    thread = threading.Thread(target=run_backend_refresh_job, args=(job_key,), daemon=True)
    thread.start()
  return {"status": job["status"], "jobKey": job_key, "total": job["total"], "completed": job["completed"]}


def backend_script_status() -> dict:
  with BACKEND_SCRIPT_LOCK:
    jobs = list(BACKEND_SCRIPT_JOBS.values())[-12:]
  return {"jobs": jobs, "active": [job for job in jobs if job.get("status") in {"queued", "running"}]}


def operator_jobs_payload() -> dict:
  status = backend_script_status()
  return {
    "jobs": [
      {
        "id": job_id,
        "label": spec["label"],
        "description": spec["description"],
      }
      for job_id, spec in OPERATOR_JOB_SPECS.items()
    ],
    "runs": status["jobs"],
    "active": status["active"],
    "updatedAt": datetime.now(timezone.utc).isoformat(),
  }


def start_operator_job(job_id: str) -> dict:
  spec = OPERATOR_JOB_SPECS.get(job_id)
  if not spec:
    raise ValueError("Unknown maintenance job")
  with BACKEND_SCRIPT_LOCK:
    active = next(
      (job for job in reversed(list(BACKEND_SCRIPT_JOBS.values())) if job.get("status") in {"queued", "running"}),
      None,
    )
    if active:
      return {"status": active.get("status"), "jobKey": active.get("jobKey"), "detail": "another maintenance job is already running"}
    now = time.time()
    job_key = f"operator-{job_id}-{int(now * 1000)}"
    steps = [
      {
        **step,
        "status": "queued",
        "reason": "operator-requested",
      }
      for step in spec["steps"]
    ]
    BACKEND_SCRIPT_JOBS[job_key] = {
      "status": "queued",
      "jobKey": job_key,
      "jobId": job_id,
      "label": spec["label"],
      "reason": "operator-requested",
      "total": len(steps),
      "completed": 0,
      "steps": steps,
      "queuedAt": datetime.now(timezone.utc).isoformat(),
    }
  thread = threading.Thread(target=run_backend_refresh_job, args=(job_key,), daemon=True)
  thread.start()
  return {"status": "queued", "jobKey": job_key, "total": len(steps), "completed": 0}


def load_universe_manifest() -> dict:
  path = UNIVERSE_DIR / "manifest.json"
  if not path.exists():
    return {}
  try:
    payload = json.loads(path.read_text())
  except json.JSONDecodeError:
    return {}
  return payload if isinstance(payload, dict) else {}


def load_universe_members(universe_name: str) -> list[dict]:
  path = UNIVERSE_DIR / f"{universe_name}.json"
  if not path.exists():
    return []
  try:
    payload = json.loads(path.read_text())
  except json.JSONDecodeError:
    return []
  return payload if isinstance(payload, list) else []


def load_market_map_members(universe_name: str) -> tuple[list[dict], str, bool]:
  members = load_universe_members(universe_name)
  if members:
    return members, universe_name, False
  fallback_name = MARKET_MAP_FALLBACK_UNIVERSES.get(universe_name)
  fallback_members = load_universe_members(fallback_name) if fallback_name else []
  return fallback_members, fallback_name or universe_name, True


def load_relation_graph(universe_name: str) -> dict:
  path = RELATIONS_DIR / f"{universe_name}.json"
  if not path.exists():
    return {}
  try:
    payload = json.loads(path.read_text())
  except json.JSONDecodeError:
    return {}
  return payload if isinstance(payload, dict) else {}


def load_json_file(path: Path, fallback):
  if not path.exists():
    return fallback
  try:
    payload = json.loads(path.read_text())
  except json.JSONDecodeError:
    return fallback
  return payload


def load_company_networks() -> dict:
  manual = load_json_file(DATA_DIR / "company_networks.json", {})
  generated = load_json_file(DATA_DIR / "company_networks.generated.json", {})
  if not isinstance(manual, dict):
    manual = {}
  if not isinstance(generated, dict):
    generated = {}
  merged = {}
  for symbol in set(generated) | set(manual):
    base = generated.get(symbol, {}) if isinstance(generated.get(symbol), dict) else {}
    overlay = manual.get(symbol, {}) if isinstance(manual.get(symbol), dict) else {}
    merged[symbol] = {
      "entities": (base.get("entities") or []) + (overlay.get("entities") or []),
      "links": (base.get("links") or []) + (overlay.get("links") or []),
      "profile": {**(base.get("profile") or {}), **(overlay.get("profile") or {})},
    }
  return merged


def load_company_projects() -> dict:
  payload = load_json_file(COMPANY_PROJECTS_PATH, {})
  return payload if isinstance(payload, dict) else {}


def load_factor_schedule() -> list[dict]:
  payload = load_json_file(FACTOR_DIR / "factor_update_schedule.json", [])
  return payload if isinstance(payload, list) else []


def load_factor_registry() -> list[dict]:
  payload = load_json_file(FACTOR_DIR / "factor_registry.json", [])
  return payload if isinstance(payload, list) else []


def load_prediction_formulas() -> list[dict]:
  payload = load_json_file(FACTOR_DIR / "prediction_formulas.json", [])
  return payload if isinstance(payload, list) else []


def load_market_decision_inputs() -> list[dict]:
  payload = load_json_file(FACTOR_DIR / "market_decision_inputs.json", [])
  return payload if isinstance(payload, list) else []


def load_trading_papers() -> list[dict]:
  payload = load_json_file(PAPER_DIR / "trading_papers.json", [])
  return payload if isinstance(payload, list) else []


def load_dashboard_practices() -> list[dict]:
  payload = load_json_file(PAPER_DIR / "dashboard_practices.json", [])
  return payload if isinstance(payload, list) else []


def load_quant_concepts() -> list[dict]:
  payload = load_json_file(PAPER_DIR / "quant_concepts.json", [])
  return payload if isinstance(payload, list) else []


def load_methodology_flow() -> list[dict]:
  payload = load_json_file(FACTOR_DIR / "methodology_flow.json", [])
  return payload if isinstance(payload, list) else []


def load_macro_dataset_manifest() -> dict:
  payload = load_json_file(MACRO_DATA_DIR / "manifest.json", {})
  return payload if isinstance(payload, dict) else {}


def slugify_note_name(value: str) -> str:
  cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", (value or "").strip().lower()).strip("-")
  return cleaned or "note"


def load_market_map_note(symbol: str) -> dict:
  symbol = (symbol or "").upper()
  company_dir = VAULT_DIR / "companies"
  candidates = [
    company_dir / f"{symbol}.md",
    company_dir / f"{slugify_note_name(symbol)}.md",
    company_dir / f"{slugify_note_name(fallback_meta(symbol).get('name', symbol))}.md",
  ]
  for path in candidates:
    if not path.exists():
      continue
    text = path.read_text()
    summary = ""
    for line in text.splitlines():
      stripped = line.strip()
      if stripped and not stripped.startswith("---") and not stripped.startswith("#") and not stripped.startswith("symbol:") and not stripped.startswith("region:") and not stripped.startswith("exchange:") and not stripped.startswith("sector:"):
        summary = stripped
        break
    return {
      "path": str(path.relative_to(BASE_DIR)) if str(path).startswith(str(BASE_DIR)) else str(path),
      "summary": summary,
      "title": path.stem,
    }
  return {}


def universe_name_for_region(region_key: str) -> str:
  return "sensex30" if region_key == "india" else "sp500"


def correlation_from_prices(left: list[float], right: list[float]) -> float:
  size = min(len(left), len(right))
  if size < 10:
    return 0.0
  left = left[-size:]
  right = right[-size:]
  left_returns = []
  right_returns = []
  for index in range(1, size):
    prev_left, prev_right = left[index - 1], right[index - 1]
    curr_left, curr_right = left[index], right[index]
    if prev_left and prev_right:
      left_returns.append((curr_left - prev_left) / prev_left)
      right_returns.append((curr_right - prev_right) / prev_right)
  size = min(len(left_returns), len(right_returns))
  if size < 10:
    return 0.0
  left_returns = left_returns[-size:]
  right_returns = right_returns[-size:]
  left_mean = sum(left_returns) / size
  right_mean = sum(right_returns) / size
  numerator = sum((a - left_mean) * (b - right_mean) for a, b in zip(left_returns, right_returns))
  left_var = sum((a - left_mean) ** 2 for a in left_returns)
  right_var = sum((b - right_mean) ** 2 for b in right_returns)
  denominator = math.sqrt(left_var * right_var)
  return numerator / denominator if denominator else 0.0


def relation_links_for_watchlist(region_key: str, watchlist: list[dict]) -> tuple[list[dict], dict]:
  universe_name = universe_name_for_region(region_key)
  relation_graph = load_relation_graph(universe_name)
  tracked = {item["symbol"] for item in watchlist if item.get("symbol")}
  if relation_graph:
    filtered_links = [
      {
        "source": link.get("source"),
        "target": link.get("target"),
        "value": clamp(float(link.get("value") or 0), 0.8, 4.0),
        "direction": link.get("direction") or "neutral",
      }
      for link in relation_graph.get("links", [])
      if link.get("source") in tracked and link.get("target") in tracked
    ][:16]
    if filtered_links:
      return filtered_links, {
        "source": relation_graph.get("source", "Precomputed relation graph"),
        "generatedAt": relation_graph.get("generatedAt"),
        "universe": relation_graph.get("universe", universe_name),
      }

  histories = {}
  for item in watchlist:
    cached = load_cached_history(item["symbol"], "1Y")
    if cached and len(cached[0]) >= 20:
      histories[item["symbol"]] = cached[0]
  links = []
  symbols = list(histories.keys())
  for index, left_symbol in enumerate(symbols):
    for right_symbol in symbols[index + 1 :]:
      corr = correlation_from_prices(histories[left_symbol], histories[right_symbol])
      if abs(corr) < 0.4:
        continue
      links.append(
        {
          "source": left_symbol,
          "target": right_symbol,
          "value": round(clamp(abs(corr) * 3.2, 0.8, 4.0), 4),
          "direction": "positive" if corr >= 0 else "negative",
        }
      )
  return links[:16], {
    "source": "Dynamic cached-history correlation",
    "generatedAt": datetime.now(timezone.utc).isoformat(),
    "universe": universe_name,
  }


def company_network_for_symbol(symbol: str) -> dict:
  networks = load_company_networks()
  network = networks.get((symbol or "").upper()) or {}
  return network if isinstance(network, dict) else {}


def company_projects_for_symbol(symbol: str) -> list[dict]:
  projects = load_company_projects().get((symbol or "").upper()) or {}
  project_list = projects.get("projects") if isinstance(projects, dict) else []
  return project_list if isinstance(project_list, list) else []


def dedupe_graph_nodes(nodes: list[dict]) -> list[dict]:
  seen = {}
  for node in nodes:
    node_id = node.get("id")
    if not node_id:
      continue
    seen[node_id] = {**seen.get(node_id, {}), **node}
  return list(seen.values())


def build_forecast_inputs(symbol: str, quote: dict, summary: dict, history: list[float], news_count: int) -> dict:
  previous_close = float(quote.get("regularMarketPreviousClose") or history[-2] or history[-1])
  latest_price = float(quote.get("regularMarketPrice") or history[-1])
  change_pct = float(quote.get("regularMarketChangePercent") or pct_change(latest_price, previous_close))

  summary_detail = summary.get("summaryDetail") or {}
  statistics_block = summary.get("defaultKeyStatistics") or {}
  financial_data = summary.get("financialData") or {}

  beta = (
    statistics_block.get("beta", {}).get("raw")
    or summary_detail.get("beta", {}).get("raw")
    or fallback_meta(symbol)["beta"]
  )
  pe_ratio = (
    quote.get("trailingPE")
    or summary_detail.get("trailingPE", {}).get("raw")
    or fallback_meta(symbol)["pe"]
  )
  market_cap = quote.get("marketCap") or financial_data.get("marketCap", {}).get("raw") or 0
  quality_score = clamp(
    0.35
    + min(math.log10(market_cap + 1) / 15, 0.22)
    + (0.08 if float(pe_ratio or 0) < 28 else 0.0),
    0.32,
    0.88,
  )
  event_score = clamp(abs(change_pct) / 8 + news_count * 0.05, 0.22, 0.96)

  return {
    "latestPrice": latest_price,
    "previousPrice": previous_close,
    "beta": float(beta),
    "pe": float(pe_ratio or 20.0),
    "qualityScore": quality_score,
    "eventScore": event_score,
    "marketCap": market_cap,
  }


def build_macro_score(region: str, beta: float, pe_ratio: float, stress: str) -> float:
  base = (beta - 1) * -0.06 + (-0.02 if pe_ratio > 30 else 0.04)
  if "India" in region:
    base += 0.01
  shock_map = {
    "base": 0.0,
    "riskoff": -0.18,
    "growth": 0.16,
    "inflation": -0.07 if "US" in region else -0.03,
  }
  return base + shock_map.get(stress, 0.0)


def infer_regime(macro_score: float, realized_vol: float, event_score: float) -> str:
  if realized_vol > 0.03 or event_score > 0.72:
    return "High-volatility event regime"
  if macro_score > 0.08:
    return "Growth acceleration regime"
  if macro_score < -0.08:
    return "Risk-off regime"
  return "Balanced regime"


def clamp(value: float, low: float, high: float) -> float:
  return max(low, min(high, value))


def build_factor_cards(inputs: dict) -> list[dict]:
  return [
    {
      "title": "Fast momentum",
      "score": clamp(inputs["fastMomentum"] * 1200, -100, 100),
      "description": "Short-horizon tape strength captures flow, positioning, and immediate momentum persistence.",
    },
    {
      "title": "Slow trend",
      "score": clamp(inputs["slowMomentum"] * 1600, -100, 100),
      "description": "The longer drift filter stops the model from overreacting to a single noisy session.",
    },
    {
      "title": "Mean reversion",
      "score": clamp(inputs["meanReversion"] * 700, -100, 100),
      "description": "If price stretches too far from its rolling center, continuation odds are discounted.",
    },
    {
      "title": "Macro carry-through",
      "score": clamp(inputs["macroScore"] * 420, -100, 100),
      "description": "Rates, growth, inflation, and index sensitivity are mapped into asset-specific headwinds or tailwinds.",
    },
    {
      "title": "Volatility tax",
      "score": clamp(-inputs["realizedVol"] * 2400, -100, 100),
      "description": "Higher realized volatility lowers confidence and increases expected forecast error.",
    },
    {
      "title": "Quality overlay",
      "score": clamp(inputs["qualityLift"] * 220, -100, 100),
      "description": "Steadier fundamentals keep the model from blindly chasing fragile momentum bursts.",
    },
    {
      "title": "RSI signal",
      "score": clamp(inputs.get("rsiSignal", 0.0) * 5500, -100, 100),
      "description": "RSI(14) mean-reversion overlay. Oversold (<30) adds bullish bias; overbought (>70) adds bearish dampening.",
    },
    {
      "title": "Volume trend",
      "score": clamp((inputs.get("volumeTrend", 1.0) - 1.0) * 150, -100, 100),
      "description": "Rising volume relative to 20-session average confirms signal strength; thin volume reduces confidence.",
    },
    {
      "title": "MACD",
      "score": clamp(inputs.get("macdSignal", 0.0) * 4500, -100, 100),
      "description": f"MACD(12,26,9) crossover: {'bullish crossover' if inputs.get('macdCrossover', 0) > 0.5 else 'bearish crossover' if inputs.get('macdCrossover', 0) < -0.5 else 'trend continuation'}. Histogram measures MACD-signal separation.",
    },
    {
      "title": "Bollinger position",
      "score": clamp((0.5 - inputs.get("bollPosition", 0.5)) * 200, -100, 100),
      "description": f"BB(20,2): price at {inputs.get('bollPosition', 0.5):.0%} of band range. {'Squeeze detected — breakout likely.' if inputs.get('bollSqueeze') else 'Normal bandwidth.'}",
    },
    {
      "title": "ATR volatility",
      "score": clamp(-inputs.get("atrPct", 0.0) * 2000, -100, 0),
      "description": "ATR(14) as % of price. Higher ATR = wider expected moves = lower signal precision. Acts as a confidence drag.",
    },
  ]


def build_classic_quant_cards(history: list[float], enriched: dict, volume_ratio: float, realized_vol: float, macro_score: float) -> list[dict]:
  latest_price = float(enriched["latestPrice"])
  lookback = min(len(history), 20)
  base_price = history[-lookback] if lookback else latest_price
  momentum_20 = pct_change(latest_price, base_price) if base_price else 0.0

  mean_window = history[-20:] if len(history) >= 20 else history
  center = average(mean_window) if mean_window else latest_price
  dispersion = std_dev(mean_window) if len(mean_window) >= 2 else 0.0
  z_score = ((latest_price - center) / dispersion) if dispersion else 0.0

  annualized_vol = realized_vol * math.sqrt(252) * 100
  peak_window = max(history[-20:] or [latest_price])
  drawdown = pct_change(latest_price, peak_window)
  beta = float(enriched["beta"])
  pe_ratio = float(enriched["pe"])

  def label_from_threshold(value: float, positive: float, negative: float, high: str, low: str, neutral: str) -> str:
    if value >= positive:
      return high
    if value <= negative:
      return low
    return neutral

  return [
    {
      "title": "20-session momentum",
      "formula": "MOM(20) = P_t / P_{t-20} - 1",
      "value": f"{momentum_20:+.2f}%",
      "interpretation": label_from_threshold(momentum_20, 3.0, -3.0, "Trend support is positive.", "Price momentum is deteriorating.", "Momentum is mixed."),
      "failureMode": "Momentum often fails during violent reversals, crowded positioning unwinds, or event-driven gap moves.",
      "tag": "Momentum",
    },
    {
      "title": "Price z-score",
      "formula": "Z_t = (P_t - MA_20) / SD_20",
      "value": f"{z_score:+.2f}",
      "interpretation": label_from_threshold(z_score, 1.2, -1.2, "Price is stretched above its local center.", "Price is stretched below its local center.", "Price is near its rolling center."),
      "failureMode": "Mean-reversion signals usually struggle in persistent trend regimes and during structural repricing.",
      "tag": "Mean reversion",
    },
    {
      "title": "Annualized volatility",
      "formula": "sigma = std(r_t) * sqrt(252)",
      "value": f"{annualized_vol:.2f}%",
      "interpretation": label_from_threshold(annualized_vol, 34.0, 18.0, "Volatility is elevated, so expected error rises.", "Volatility is compressed.", "Volatility is in a normal operating band."),
      "failureMode": "Volatility is backward-looking and can understate upcoming event risk right before a shock.",
      "tag": "Risk",
    },
    {
      "title": "Participation ratio",
      "formula": "VR = Volume_t / AvgVolume_n",
      "value": f"{volume_ratio:.2f}x",
      "interpretation": label_from_threshold(volume_ratio, 1.15, 0.85, "The move has above-normal participation.", "Participation is light.", "Participation is near average."),
      "failureMode": "Volume spikes can be noisy around earnings, index rebalances, and one-off news bursts.",
      "tag": "Liquidity",
    },
    {
      "title": "Beta exposure",
      "formula": "beta ≈ cov(r_i, r_m) / var(r_m)",
      "value": f"{beta:.2f}",
      "interpretation": label_from_threshold(beta, 1.1, 0.9, "The stock amplifies index moves.", "The stock is relatively defensive.", "The stock is close to market-like beta."),
      "failureMode": "Beta can shift quickly when regimes, sector leadership, or company-specific catalysts change.",
      "tag": "Market sensitivity",
    },
    {
      "title": "Trailing P/E anchor",
      "formula": "P/E = Price / Earnings per share",
      "value": f"{pe_ratio:.2f}x",
      "interpretation": label_from_threshold(pe_ratio, 30.0, 18.0, "The multiple is rich and needs growth support.", "The multiple is comparatively modest.", "The multiple is in a middle band."),
      "failureMode": "P/E is weak for cyclical earnings, turnarounds, loss-making firms, and fast-changing rate regimes.",
      "tag": "Valuation",
    },
    {
      "title": "Rolling drawdown",
      "formula": "DD = P_t / max(P_{1:t}) - 1",
      "value": f"{drawdown:.2f}%",
      "interpretation": label_from_threshold(drawdown, -2.0, -8.0, "The stock is near its recent peak.", "The stock is in a deeper drawdown state.", "The stock is below its recent peak but not washed out."),
      "failureMode": "Drawdown alone does not tell you whether weakness is temporary or fundamentally justified.",
      "tag": "Path risk",
    },
    {
      "title": "Macro carry",
      "formula": "Macro carry = f(beta, rates, region, valuation)",
      "value": f"{macro_score:+.2f}",
      "interpretation": label_from_threshold(macro_score, 0.08, -0.08, "Top-down conditions are supportive.", "Macro conditions are acting as a drag.", "Macro conditions are balanced."),
      "failureMode": "Macro composites compress many variables and can miss sudden policy or geopolitical step-changes.",
      "tag": "Macro",
    },
  ]


def summarize_classic_quant(cards: list[dict], forecast: dict) -> str:
  if not cards:
    return "Classic quant signals are unavailable for this ticker."
  strongest = cards[:3]
  summary_bits = ", ".join(f"{item['title']} ({item['value']})" for item in strongest)
  return f"Classic quant stack is anchored on {summary_bits}. Current model direction is {forecast['direction'].lower()} with {forecast['confidence']:.0f}% confidence."


def build_relationship_cards(snapshot_inputs: dict, signal_map: dict) -> list[dict]:
  volume_ratio = snapshot_inputs["volumeRatio"]
  return [
    {
      "title": "Valuation",
      "score": clamp((28 - snapshot_inputs["pe"]) * 3.5, -100, 100),
      "description": f"Trailing P/E at {snapshot_inputs['pe']:.2f}; used as a valuation pressure input rather than a standalone buy/sell rule.",
    },
    {
      "title": "Volume pulse",
      "score": clamp((volume_ratio - 1) * 75, -100, 100),
      "description": f"Current volume is {volume_ratio:.2f}x the reference average, which helps distinguish conviction from low-participation moves.",
    },
    {
      "title": "News sentiment",
      "score": clamp(signal_map["sentiment"]["score"] * 100, -100, 100),
      "description": f"Headline read is {signal_map['sentiment']['label'].lower()}, based on directional language in the latest catalyst set.",
    },
    {
      "title": "Policy risk",
      "score": 35 if signal_map["signals"][0]["headline"] != "No strong current signal detected." else 0,
      "description": signal_map["signals"][0]["headline"],
    },
    {
      "title": "Deal flow",
      "score": 32 if signal_map["signals"][1]["headline"] != "No strong current signal detected." else 0,
      "description": signal_map["signals"][1]["headline"],
    },
    {
      "title": "Adjacent industry",
      "score": 28 if signal_map["signals"][2]["headline"] != "No strong current signal detected." else 0,
      "description": signal_map["signals"][2]["headline"],
    },
  ]


def build_driver_cards(signal_map: dict, summary: dict, forecast: dict) -> list[dict]:
  sector = signal_map["sector"]
  industry = signal_map["industry"]
  agreement = forecast.get("models", {}).get("agreement", {})
  moving_average = forecast.get("movingAverageSignal") or {}
  cards = [
    {
      "title": "5D vs 25D trend",
      "body": f"{moving_average.get('state', 'MA signal')} with {str(moving_average.get('nextRunBias', 'mixed')).lower()} next-run bias. {moving_average.get('why', '')}",
      "tag": f"{float(moving_average.get('confidence') or 0):.0f}% MA",
    },
    {
      "title": "Sentiment pulse",
      "body": f"Current headline sentiment is {signal_map['sentiment']['label'].lower()}. This is used with volatility so sentiment alone does not dominate the forecast.",
      "tag": signal_map["sentiment"]["label"],
    },
    {
      "title": "Policy & regulation",
      "body": signal_map["signals"][0]["headline"],
      "tag": "Policy",
    },
    {
      "title": "Deals & partnerships",
      "body": signal_map["signals"][1]["headline"],
      "tag": "Deal flow",
    },
    {
      "title": "Adjacent industry",
      "body": f"{signal_map['signals'][2]['headline']} Sector context: {sector}. Industry context: {industry}.",
      "tag": "Industry",
    },
    {
      "title": "Forecast relationship",
      "body": f"The current forecast is {forecast['direction'].lower()} with {forecast['confidence']:.0f}% confidence and {forecast['eventPressureLabel'].lower()} event pressure.",
      "tag": "Model",
    },
    {
      "title": "Classic vs modern",
      "body": agreement.get("summary", "Model agreement is loading."),
      "tag": agreement.get("label", "Agreement"),
    },
  ]
  return cards


def build_triggers(inputs: dict, stress: str) -> list[dict]:
  triggers: list[dict] = []

  def add(title: str, body: str, tag: str, weight: float) -> None:
    triggers.append({"title": title, "body": body, "tag": tag, "weight": round(abs(weight), 4)})

  fast = float(inputs.get("fastMomentum") or 0)
  slow = float(inputs.get("slowMomentum") or 0)
  if fast * slow > 0 and abs(fast) + abs(slow) > 0.003:
    add(
      "Trend alignment",
      "Short and medium-term trends point the same way, so the model gives continuation more room.",
      "Trend",
      fast + slow,
    )
  elif abs(fast - slow) > 0.004:
    add(
      "Trend disagreement",
      "Short-term and medium-term trend disagree; scenario confidence is reduced until the tape resolves.",
      "Trend",
      fast - slow,
    )

  rsi = float(inputs.get("rsi") or 50)
  if rsi < 30:
    add(
      f"RSI oversold — {rsi:.0f}",
      f"Wilder RSI(14) at {rsi:.1f}. Deeply oversold — mean-reversion odds improve historically, though oversold can persist in structural downtrends. The model applies a positive carry from this signal.",
      "RSI",
      inputs.get("rsiSignal") or 0,
    )
  elif rsi > 70:
    add(
      f"RSI overbought — {rsi:.0f}",
      f"Wilder RSI(14) at {rsi:.1f}. Overbought territory — reward/risk deteriorates on the buy side. The model reduces momentum weighting and adds a negative lean to slow continuation odds.",
      "RSI",
      inputs.get("rsiSignal") or 0,
    )
  elif rsi <= 40 or rsi >= 60:
    add(
      f"RSI elevated — {rsi:.0f}",
      f"Wilder RSI(14) at {rsi:.1f}. Approaching {'oversold' if rsi <= 40 else 'overbought'} territory. The continuous signal is applying a partial {'bullish' if rsi <= 40 else 'bearish'} mean-reversion adjustment.",
      "RSI",
      inputs.get("rsiSignal") or 0,
    )

  macd_crossover = float(inputs.get("macdCrossover") or 0)
  macd_histogram = float(inputs.get("macdHistogram") or 0)
  macd_sig = float(inputs.get("macdSignal") or 0)
  if abs(macd_sig) > 0.003 or abs(macd_crossover) >= 0.8:
    if macd_crossover > 0.8:
      crossover_note = "Bullish crossover confirmed — MACD crossed above signal line. "
    elif macd_crossover < -0.8:
      crossover_note = "Bearish crossover confirmed — MACD crossed below signal line. "
    else:
      crossover_note = ""
    hist_dir = "building" if macd_histogram >= 0 else "fading"
    add(
      f"MACD {'bullish' if macd_crossover >= 0 else 'bearish'} — histogram {macd_histogram:+.4f}",
      f"{crossover_note}Histogram at {macd_histogram:+.4f} ({hist_dir} momentum). ATR-normalized signal blended into both classic and modern stacks with different weights.",
      "MACD",
      macd_sig,
    )

  if bool(inputs.get("bollSqueeze")) or abs(float(inputs.get("breakoutPressure") or 0)) > 0.01:
    squeeze_note = "Bollinger bandwidth contracted below 2% — volatility compression signals an impending directional breakout. " if bool(inputs.get("bollSqueeze")) else ""
    boll_pos = float(inputs.get("bollPosition") or 0.5)
    band_note = f"Price at {boll_pos:.0%} of the 20-day band range."
    add(
      "Bollinger squeeze / breakout pressure" if bool(inputs.get("bollSqueeze")) else "Range breakout pressure",
      f"{squeeze_note}{band_note} Volatility expansion can dominate slower trend factors when this signal is active.",
      "Volatility",
      (inputs.get("breakoutPressure") or 0) + (inputs.get("bollBandwidth") or 0),
    )

  if abs(float(inputs.get("macroScore") or 0)) > 0.02:
    add(
      "Macro linkage",
      "Top-down bond, policy, valuation, and beta context is materially changing the equity scenario.",
      "Macro",
      inputs.get("macroScore") or 0,
    )

  realized_vol = float(inputs.get("realizedVol") or 0)
  if realized_vol > 0.025:
    add(
      "Volatility impact",
      "Realized volatility is elevated, so model error and stop-out risk both rise.",
      "Risk",
      realized_vol,
    )

  if abs(float(inputs.get("meanReversion") or 0)) > 0.04:
    add(
      "Stretch check",
      "Price is materially stretched versus its recent center, increasing snap-back risk.",
      "Reversion",
      inputs.get("meanReversion") or 0,
    )

  add(
    "Stress lens",
    f"The {stress} scenario changes macro weights without changing the observed price path, separating regime risk from ticker-specific behavior.",
    "Scenario",
    0.01,
  )
  return sorted(triggers, key=lambda item: item["weight"], reverse=True)[:6]


def model_direction(expected_return: float, bullish: float = 2.0, bearish: float = -2.0) -> str:
  if expected_return > bullish:
    return "Bullish"
  if expected_return < bearish:
    return "Bearish"
  return "Neutral"


def build_model_agreement(classic_expected_return: float, modern_expected_return: float) -> dict:
  classic_direction = model_direction(classic_expected_return)
  modern_direction = model_direction(modern_expected_return)
  spread = abs(classic_expected_return - modern_expected_return)
  alignment = 1 - clamp(spread / 12, 0, 1)

  if classic_direction == modern_direction and classic_direction != "Neutral":
    label = "Aligned"
    summary = f"Classic and modern overlays both lean {classic_direction.lower()}."
  elif classic_direction == modern_direction == "Neutral":
    label = "Balanced"
    summary = "Both stacks are cautious and see limited directional edge."
  else:
    label = "Diverging"
    summary = f"Classic leans {classic_direction.lower()} while the modern overlay leans {modern_direction.lower()}."

  return {
    "label": label,
    "score": round(alignment * 100, 1),
    "classicDirection": classic_direction,
    "modernDirection": modern_direction,
    "summary": summary,
  }


def build_forecast(symbol: str, quote: dict, summary: dict, history: list[float], stress: str = "base", horizon: int = 10, news_count: int = 0) -> dict:
  if len(history) < 2:
    latest_price = float(quote.get("regularMarketPrice") or fallback_meta(symbol)["basePrice"])
    previous_close = float(quote.get("regularMarketPreviousClose") or latest_price)
    expected_return = pct_change(latest_price, previous_close) * 0.35
    projected = [round(latest_price, 2) for _ in range(horizon)]
    direction = model_direction(expected_return, bullish=1.0, bearish=-1.0)
    agreement = build_model_agreement(expected_return, expected_return)
    return {
      "direction": direction,
      "confidence": 22.0,
      "fairValue": latest_price,
      "fairValueGap": 0.0,
      "eventPressure": 0.25,
      "eventPressureLabel": "Low",
      "mae": 0.0,
      "regime": "Live quote only",
      "expectedReturn": expected_return,
      "projected": projected,
      "realizedVol": 0.0,
      "factors": [],
      "factorsRaw": {},
      "movingAverageSignal": build_moving_average_insight(symbol, [previous_close, latest_price], persist=False),
      "models": {
        "classic": {"direction": direction, "expectedReturn": round(expected_return, 2), "confidence": 22.0, "summary": "History is unavailable, so the classic stack is using live-quote drift only."},
        "modern": {"direction": direction, "expectedReturn": round(expected_return, 2), "confidence": 22.0, "summary": "The modern overlay is disabled until a fuller price path is available."},
        "agreement": agreement,
      },
      "triggers": [
        {
          "title": "History missing",
          "body": "A live quote is available, but the historical series could not be fetched from the current provider.",
        }
      ],
    }

  returns = [
    (history[index] - history[index - 1]) / history[index - 1]
    for index in range(1, len(history))
    if history[index - 1]
  ]
  recent_returns = returns[-20:] or returns or [0.0]
  enriched = build_forecast_inputs(symbol, quote, summary, history, news_count)

  fast_momentum = average((returns[-5:] or [0.0]))
  slow_momentum = average((returns[-20:] or [0.0]))
  moving_average = build_moving_average_insight(symbol, history, persist=True)
  ma_spread = float(moving_average.get("spreadPercent") or 0.0) / 100
  ma_slope = float(moving_average.get("slope5") or 0.0) / 100
  mean_reversion = (average(history[-10:]) - enriched["latestPrice"]) / enriched["latestPrice"]
  realized_vol = std_dev(recent_returns)
  volatility_penalty = realized_vol * 1.6
  event_pressure = enriched["eventScore"] * 0.6 + realized_vol * 9
  region = quote.get("fullExchangeName") or quote.get("exchange") or "Global"
  macro_score = build_macro_score(region, enriched["beta"], enriched["pe"], stress)
  quality_lift = (enriched["qualityScore"] - 0.5) * 0.4

  # ── RSI factor: continuous mean-reversion oscillator (Wilder RSI, period 14)
  # Research basis: Wilder (1978) — RSI as continuous signal, not binary threshold.
  # (50 - rsi)/50 * scale: RSI=20 → +0.0108, RSI=50 → 0, RSI=80 → -0.0108
  rsi = calc_rsi(history, period=14)
  rsi_signal = clamp((50.0 - rsi) / 50.0 * 0.018, -0.018, 0.018)
  # Momentum dampening strengthens at extremes: RSI=70 → 0.75×, RSI=80 → 0.625×
  # Prevents chasing overbought momentum or adding to oversold falls
  rsi_momentum_dampen = clamp(1.0 - abs(rsi - 50.0) / 80.0, 0.40, 1.0)

  # ── Volume trend: rising volume confirms signals; falling volume weakens them
  vol_list = [float(v) for v in (summary.get("_volumeHistory") or []) if v]
  volume_trend = calc_volume_trend(vol_list) if len(vol_list) >= 5 else 1.0
  # >1.3 = volume surge (confidence lift), <0.6 = thin volume (confidence drag)
  volume_confidence_lift = clamp((volume_trend - 1.0) * 0.06, -0.04, 0.06)

  # ── MACD: EMA crossover signal (12/26/9). Crossover direction + histogram momentum
  macd = calc_macd(history, fast=12, slow=26, signal=9)
  atr_pct = calc_atr(history, period=14)
  atr_value = max(abs(enriched["latestPrice"]) * max(atr_pct, 0.003), 1e-9)
  macd_hist_component = clamp(macd["histogram"] / atr_value, -1.0, 1.0)
  macd_signal = clamp((macd["crossover"] * 0.010) + (macd_hist_component * 0.010), -0.024, 0.024)

  # ── Bollinger Bands: position within bands, squeeze detection
  boll = calc_bollinger(history, period=20, num_std=2.0)
  # Near lower band (<0.2) = mean-reversion bullish; near upper band (>0.8) = caution
  boll_signal = clamp((0.5 - boll["position"]) * 0.016, -0.012, 0.012)
  # Squeeze = low bandwidth → impending breakout; boost confidence weight of directional signals
  boll_squeeze_boost = 0.008 if boll["squeeze"] else 0.0

  classic_score = (
    fast_momentum * 1.2 * rsi_momentum_dampen  # dampened when overbought
    + slow_momentum * 1.1
    + ma_spread * 1.0
    + ma_slope * 0.75
    + mean_reversion * 0.75
    + macro_score * 0.85
    + quality_lift
    + rsi_signal                                # RSI mean-reversion overlay
    + macd_signal * 0.7                         # MACD crossover contribution
    + boll_signal * 0.5                         # Bollinger mean-reversion
    + boll_squeeze_boost * slow_momentum        # amplify trend in squeeze
    - volatility_penalty
    - event_pressure * 0.04
  )

  trend_patch = ((average(history[-5:]) / average(history[-20:])) - 1) if len(history) >= 20 and average(history[-20:]) else 0.0
  upper_window = max(history[-20:-1] or history[:-1] or [enriched["latestPrice"]])
  lower_window = min(history[-20:-1] or history[:-1] or [enriched["latestPrice"]])
  breakout_pressure = (
    (enriched["latestPrice"] - upper_window) / upper_window
    if upper_window and enriched["latestPrice"] >= upper_window
    else (enriched["latestPrice"] - lower_window) / lower_window
    if lower_window and enriched["latestPrice"] <= lower_window
    else 0.0
  )
  long_vol = std_dev(returns[-60:] or recent_returns)
  volatility_regime = realized_vol - long_vol
  regime_alignment = slow_momentum * 1.15 + macro_score * 0.95 - realized_vol * 1.1
  modern_score = (
    trend_patch * 1.6
    + breakout_pressure * 1.2
    + regime_alignment
    + rsi_signal * 0.5                          # RSI feeds modern model too
    + macd_signal * 0.9                         # MACD has stronger modern weight
    + boll_signal * 0.4
    - volatility_regime * 0.7
    - event_pressure * 0.03
  )

  agreement = build_model_agreement(classic_score * math.sqrt(horizon) * 100, modern_score * math.sqrt(horizon) * 100)
  agreement_boost = 0.05 if agreement["label"] == "Aligned" else -0.03 if agreement["label"] == "Diverging" else 0.0
  factor_score = (classic_score * 0.60) + (modern_score * 0.40) + agreement_boost

  expected_return = factor_score * math.sqrt(horizon) * 100
  classic_expected_return = classic_score * math.sqrt(horizon) * 100
  modern_expected_return = modern_score * math.sqrt(horizon) * 100
  # Confidence: add volume lift, slightly relax the vol penalty floor
  classic_confidence = clamp(100 - realized_vol * 1600 - enriched["eventScore"] * 24 + volume_confidence_lift * 100, 20, 89)
  modern_confidence = clamp(100 - realized_vol * 1350 - abs(volatility_regime) * 1100 - enriched["eventScore"] * 20 + volume_confidence_lift * 100, 20, 92)
  confidence = clamp(((classic_confidence * 0.58) + (modern_confidence * 0.42)) + (agreement["score"] - 50) * 0.08, 20, 93)
  fair_value = enriched["latestPrice"] * (1 + factor_score * 1.65)
  mae = clamp(realized_vol * 100 * (1.7 + enriched["beta"] * 0.25), 1.6, 12.5)
  direction = model_direction(expected_return)
  regime = infer_regime(macro_score, realized_vol, enriched["eventScore"])

  projected = []
  cursor = enriched["latestPrice"]
  for step in range(1, horizon + 1):
    noise = (deterministic_noise(symbol_seed(symbol), step + 90) - 0.5) * realized_vol * 0.9
    cursor = cursor * (1 + factor_score / horizon + noise)
    projected.append(round(cursor, 2))

  factors = {
    "fastMomentum": fast_momentum,
    "slowMomentum": slow_momentum,
    "maSpread": ma_spread,
    "maSlope": ma_slope,
    "meanReversion": mean_reversion,
    "macroScore": macro_score,
    "realizedVol": realized_vol,
    "qualityLift": quality_lift,
    "trendPatch": trend_patch,
    "breakoutPressure": breakout_pressure,
    "volatilityRegime": volatility_regime,
    "regimeAlignment": regime_alignment,
    "rsiSignal": rsi_signal,
    "rsi": rsi,
    "volumeTrend": volume_trend,
    "macdSignal": macd_signal,
    "macdLine": macd["line"],
    "macdSignalLine": macd["signal"],
    "macdHistogram": macd["histogram"],
    "macdCrossover": macd["crossover"],
    "bollPosition": boll["position"],
    "bollBandwidth": boll["bandwidth"],
    "bollSqueeze": boll["squeeze"],
    "atrPct": atr_pct,
  }

  return {
    "direction": direction,
    "confidence": confidence,
    "fairValue": fair_value,
    "fairValueGap": pct_change(fair_value, enriched["latestPrice"]),
    "eventPressure": event_pressure,
    "eventPressureLabel": "High" if event_pressure > 0.8 else "Medium" if event_pressure > 0.55 else "Low",
    "mae": mae,
    "regime": regime,
    "expectedReturn": expected_return,
    "projected": projected,
    "realizedVol": realized_vol,
    "factors": build_factor_cards(factors),
    "factorsRaw": factors,
    "movingAverageSignal": moving_average,
    "models": {
      "classic": {
        "direction": model_direction(classic_expected_return),
        "expectedReturn": round(classic_expected_return, 2),
        "confidence": round(classic_confidence, 1),
        "summary": "Classic stack blends momentum, mean reversion, macro carry, valuation discipline, and volatility control.",
      },
      "modern": {
        "direction": model_direction(modern_expected_return),
        "expectedReturn": round(modern_expected_return, 2),
        "confidence": round(modern_confidence, 1),
        "summary": "Modern overlay tracks patch trend persistence, breakout pressure, and regime stability before blending into the final path.",
      },
      "agreement": agreement,
    },
    "triggers": build_triggers(factors, stress),
  }


def build_short_horizon_forecast(history: list[float], horizon: int = 5) -> dict:
  """JSON-safe wrapper around scripts/short_horizon_model.predict. Runs the
  hand-crafted short-horizon directional model (see CLAUDE.md + the methodology
  report) and computes a quick walk-forward skill score versus a flat baseline.

  Returns a dict suitable for direct inclusion in the forecast payload. All keys
  are namespaced under shortHorizon so this is purely additive — no existing
  keys are renamed or overwritten."""
  horizon = max(1, min(int(horizon), 10))
  if not history or len(history) < 25:
    return {
      "horizon": horizon,
      "available": False,
      "reason": "Need at least 25 historical bars to compute features.",
    }

  forecast = _shm.predict(history, horizon=horizon)
  # Rolling skill check: only meaningful with >=80 bars. Lower bound otherwise.
  skill = {"samples": 0, "mae_pp": 0.0, "hit_rate_pct": 0.0, "ic": 0.0,
           "skill_vs_flat": 0.0, "status": "warmup"}
  if len(history) >= 80:
    new_metrics = _shm.walk_forward_backtest(history, horizon=horizon, predict_fn=_shm.predict)
    flat_metrics = _shm.walk_forward_backtest(history, horizon=horizon, predict_fn=_shm.predict_flat)
    flat_mae = flat_metrics.get("mae_pp") or 0.0
    new_mae = new_metrics.get("mae_pp") or 0.0
    skill_vs_flat = (flat_mae - new_mae) / flat_mae if flat_mae > 0 else 0.0
    skill = {
      "samples": int(new_metrics.get("samples", 0)),
      "mae_pp": float(new_metrics.get("mae_pp", 0.0)),
      "hit_rate_pct": float(new_metrics.get("hit_rate_pct", 0.0)),
      "ic": float(new_metrics.get("ic", 0.0)),
      "skill_vs_flat": round(skill_vs_flat, 4),
      "status": "evaluated",
    }
  return {
    "available": True,
    "horizon": forecast.horizon,
    "expectedReturnPct": forecast.expected_return_pct,
    "perDayDriftPct": forecast.per_day_drift_pct,
    "realizedVolDailyPct": forecast.realized_vol_daily,
    "coneLowPct": forecast.cone_low_pct,
    "coneHighPct": forecast.cone_high_pct,
    "direction": forecast.direction,
    "confidence": forecast.confidence,
    "features": forecast.features,
    "notes": forecast.notes,
    "skill": skill,
    "weights": _shm.WEIGHTS,
  }


def build_backtest(symbol: str, history: list[float], quote: dict, summary: dict, horizon: int, stress: str, news_count: int) -> dict:
  minimum_history = max(12, horizon + 4)
  empty = {
    "mae": 0.0, "medianApe": 0.0, "hitRate": 0.0, "sampleCount": 0,
    "returnResiduals": [], "meanReturnBias": 0.0, "residualStd": 0.0,
  }
  if len(history) < minimum_history:
    return empty

  errors = []
  hits = []
  return_residuals = []
  start = max(6, min(24, len(history) // 3))
  end = len(history) - horizon
  minimum_window = max(6, horizon // 2 + 1)
  for index in range(start, end):
    window = history[:index]
    if len(window) < minimum_window:
      continue
    # Window-time quote: build_forecast_inputs anchors latestPrice on quote.regularMarketPrice,
    # so without this override every historical forecast would start from TODAY's price and
    # leak future information into the walk-forward (causing wildly inflated MAE).
    # Only price-path information that existed at this cutoff is allowed into
    # the validation window. Current quote metadata, fundamentals, headlines,
    # and user-selected stress lenses would otherwise leak present-day context.
    window_quote = {
      "symbol": symbol,
      "regularMarketPrice": window[-1],
      "regularMarketPreviousClose": window[-2] if len(window) > 1 else window[-1],
    }
    forecast = build_forecast(symbol, window_quote, {}, window, stress="base", horizon=horizon, news_count=0)
    predicted = forecast["projected"][-1]
    actual = history[index + horizon - 1]
    current = window[-1]
    if not actual or not current:
      continue
    ape = abs((predicted - actual) / actual) * 100
    errors.append(ape)
    predicted_direction = 1 if predicted >= current else -1
    actual_direction = 1 if actual >= current else -1
    hits.append(1 if predicted_direction == actual_direction else 0)
    # Signed forecast-return error: positive value = model over-predicted return.
    predicted_return_pct = (predicted - current) / current * 100
    actual_return_pct = (actual - current) / current * 100
    return_residuals.append(predicted_return_pct - actual_return_pct)

  if not errors:
    return empty

  return {
    "mae": average(errors),
    "medianApe": statistics.median(errors),
    "hitRate": average(hits) * 100,
    "sampleCount": len(errors),
    "returnResiduals": return_residuals,
    "meanReturnBias": average(return_residuals),
    "residualStd": std_dev(return_residuals) if len(return_residuals) >= 2 else 0.0,
  }


MODEL_STATE_INSIGHT_PREFIX = "model_residual_state"
MODEL_STATE_VERSION = "residual-v2-point-in-time"


def model_training_fingerprint(history: list[float], horizon: int) -> str:
  normalized = ",".join(f"{float(value):.8f}" for value in history)
  return hashlib.sha256(f"{MODEL_STATE_VERSION}|h{horizon}|{normalized}".encode("utf-8")).hexdigest()


def update_model_residual_state(symbol: str, horizon: int, backtest: dict, data_fingerprint: str = "") -> dict:
  """Incremental residual learning. EMA-blends the latest walk-forward bias /
  residual std into a persisted per-(symbol, horizon) state.

  Each call retrains: prior state is loaded from derived_insights, new backtest
  stats are blended (alpha=0.4 favors recent), and the result is persisted so
  future runs continue from this baseline rather than re-learning cold.
  """
  if backtest.get("sampleCount", 0) < 4:
    return {
      "learnedBias": 0.0,
      "residualStd": 0.0,
      "trainingRuns": 0,
      "trainedAt": None,
      "samples": int(backtest.get("sampleCount", 0)),
      "status": "warming-up",
    }

  insight_key = f"{MODEL_STATE_INSIGHT_PREFIX}_h{horizon}"
  prior = load_derived_insight(symbol, "1d", insight_key) or {}
  if (
    data_fingerprint
    and prior.get("dataFingerprint") == data_fingerprint
    and prior.get("modelVersion") == MODEL_STATE_VERSION
  ):
    return {
      **prior,
      "status": "current",
      "didUpdate": False,
    }
  alpha = 0.4
  prior_bias = float(prior.get("learnedBias") or 0.0)
  prior_std = float(prior.get("residualStd") or 0.0)
  prior_runs = int(prior.get("trainingRuns") or 0)

  new_bias = float(backtest.get("meanReturnBias") or 0.0)
  new_std = float(backtest.get("residualStd") or 0.0)

  if prior_runs == 0:
    blended_bias = new_bias
    blended_std = new_std
  else:
    blended_bias = (1 - alpha) * prior_bias + alpha * new_bias
    blended_std = (1 - alpha) * prior_std + alpha * new_std

  state = {
    "learnedBias": round(blended_bias, 4),
    "residualStd": round(blended_std, 4),
    "trainingRuns": prior_runs + 1,
    "trainedAt": datetime.now(timezone.utc).isoformat(),
    "samples": int(backtest["sampleCount"]),
    "lastBatchBias": round(new_bias, 4),
    "lastBatchStd": round(new_std, 4),
    "status": "trained",
    "modelVersion": MODEL_STATE_VERSION,
    "dataFingerprint": data_fingerprint,
    "didUpdate": True,
  }
  save_derived_insight(symbol, "1d", insight_key, state, "Walk-forward residual learning")
  return state


def apply_residual_correction(forecast: dict, model_state: dict) -> dict:
  """Subtract learned bias (in pp of horizon return) from expectedReturn,
  rescale projected path linearly across the horizon, and refresh direction +
  fairValueGap. No-op when learned bias is negligible."""
  bias = float(model_state.get("learnedBias") or 0.0)
  if abs(bias) < 0.05 or not forecast.get("projected"):
    forecast["learnedBiasApplied"] = 0.0
    return forecast
  projected = list(forecast["projected"])
  n = len(projected)
  for i in range(n):
    step_fraction = (i + 1) / n
    projected[i] = round(projected[i] * (1 - (bias * step_fraction) / 100.0), 4)
  forecast["projected"] = projected
  raw_expected = float(forecast.get("expectedReturn") or 0.0)
  corrected_expected = raw_expected - bias
  forecast["expectedReturnRaw"] = raw_expected
  forecast["expectedReturn"] = corrected_expected
  forecast["learnedBiasApplied"] = round(bias, 4)
  forecast["direction"] = model_direction(corrected_expected)
  # Note: fairValueGap is a fundamental estimate (fair price vs. spot) — not a directional
  # return forecast — so we do NOT subtract learned bias from it. Bias correction only
  # applies to the momentum-driven expectedReturn and projected path.
  return forecast


def build_recommendation(forecast: dict) -> dict:
  """
  Build upside/base/downside scenario weights from an unbiased 33/33/33 base.

  Research basis:
  - Starts at equal 1/3 distribution — no a-priori directional bias.
  - Directional edge (expected return + fair-value gap) shifts weight toward upside/downside
    proportional to signal strength × analyst conviction.
  - Low conviction (confidence < 35%) and weak signal → base expands.
  - Event pressure raises downside and base weight, reducing upside headroom.
  - Scale: edge_strength maxes at |directional_edge| = 8%; above that, conviction caps the shift.
  """
  confidence = float(forecast.get("confidence") or 0)
  expected_return = float(forecast.get("expectedReturn") or 0)
  fair_value_gap = float(forecast.get("fairValueGap") or 0)
  event_pressure = float(forecast.get("eventPressure") or 0)

  # ── Directional edge: primary from 10-day expected return, secondary from fair-value gap
  # fair_value_gap is a raw fraction (e.g. 0.06 = 6 pp gap); scale to same % units
  directional_edge = clamp(expected_return * 0.72 + fair_value_gap * 100 * 0.28, -15.0, 15.0)

  # ── Conviction: how much to trust the signal (0 when conf ≤ 35%, 1.0 at 90%)
  conviction = clamp((confidence - 35.0) / 55.0, 0.0, 1.0)

  # ── Edge strength: magnitude of directional signal (0 flat → 1 max at ±8%)
  edge_strength = clamp(abs(directional_edge) / 8.0, 0.0, 1.0)

  # ── Combined signal: both conviction AND edge must be present
  direction = 1.0 if directional_edge >= 0 else -1.0
  signal_strength = edge_strength * conviction  # 0–1

  # ── Start from equal distribution
  buy_raw = 33.3
  sell_raw = 33.3
  hold_raw = 33.4

  # ── Directional shift: signal_strength moves weight between upside/downside
  # At signal_strength=1.0: buy gains +42, sell loses -7, hold loses -35 (for bullish)
  buy_raw  += direction * signal_strength * 42.0
  sell_raw -= direction * signal_strength * 35.0
  hold_raw -= signal_strength * 7.0

  # ── Uncertainty expansion: low conviction + weak signal → base grows
  uncertainty = (1.0 - conviction) * (1.0 - edge_strength)
  hold_raw += uncertainty * 22.0
  buy_raw  -= uncertainty * 11.0
  sell_raw -= uncertainty * 11.0

  # ── Event risk: raises downside + base weight and cuts upside headroom
  hold_raw += event_pressure * 8.0
  sell_raw += event_pressure * 6.0
  buy_raw  -= event_pressure * 8.0

  # ── Floor + normalise
  buy_raw  = max(2.0, buy_raw)
  sell_raw = max(2.0, sell_raw)
  hold_raw = max(5.0, hold_raw)
  total = buy_raw + sell_raw + hold_raw
  buy  = round((buy_raw  / total) * 100)
  sell = round((sell_raw / total) * 100)
  hold = max(0, 100 - buy - sell)

  scenario_signal = "Upside-led" if buy >= max(sell, hold) else "Downside-led" if sell >= max(buy, hold) else "Base-led"
  return {
    "upside": buy,
    "base": hold,
    "downside": sell,
    "scenarioSignal": scenario_signal,
    # Deprecated aliases retained additively for older local clients.
    "buy": buy,
    "hold": hold,
    "sell": sell,
    "signal": scenario_signal,
    "edge": round(directional_edge, 2),
    "confidenceUsed": round(confidence, 1),
  }


def build_decision_cockpit(snapshot: dict, region_payload: dict, radar: dict | None = None) -> dict:
  forecast = snapshot.get("forecast") or {}
  recommendation = snapshot.get("recommendation") or {}
  moving_average = forecast.get("movingAverageSignal") or {}
  region_analysis = region_payload.get("analysis") or {}
  bonds = region_payload.get("bonds") or {}
  inflation = region_payload.get("inflation") or {}
  policy = region_payload.get("policy") or {}
  radar = radar or {}
  sentiment = radar.get("sentiment") or {}
  confidence = float(forecast.get("confidence") or 0)
  expected_return = float(forecast.get("expectedReturn") or 0)
  capped_expected_return = clamp(expected_return, -10, 10)
  event_pressure = float(forecast.get("eventPressure") or 0)
  model_error = float(forecast.get("mae") or 0)
  ma_spread = float(moving_average.get("spreadPercent") or 0)
  snapshot_sentiment = snapshot.get("sentiment") or 0
  if isinstance(snapshot_sentiment, dict):
    snapshot_sentiment = snapshot_sentiment.get("score") or 0
  sentiment_score = float(sentiment.get("score") or snapshot_sentiment or 0)
  upside = float(recommendation.get("upside", recommendation.get("buy", 0)) or 0)
  downside = float(recommendation.get("downside", recommendation.get("sell", 0)) or 0)
  base = float(recommendation.get("base", recommendation.get("hold", 0)) or 0)
  edge_score = clamp(
    50
    + ((confidence - 50) * 0.35)
    + (capped_expected_return * 1.9)
    + (ma_spread * 1.35)
    + (sentiment_score * 12)
    - (event_pressure * 14)
    - (model_error * 0.7),
    0,
    100,
  )
  if edge_score >= 68:
    stance = "Constructive setup"
  elif edge_score <= 38:
    stance = "Defensive setup"
  else:
    stance = "Selective setup"
  risk_level = "High" if event_pressure >= 0.65 or model_error >= 7 else "Medium" if event_pressure >= 0.35 or model_error >= 4 else "Contained"
  top_event = (radar.get("items") or [{}])[0]
  event_title = top_event.get("title") or (snapshot.get("headlines") or ["No dominant event yet"])[0]
  facts = [
    {"label": "Price move", "value": f"{float(snapshot.get('changePercent') or 0):+.2f}%", "why": "Live quote change for the selected ticker."},
    {"label": "Trend stack", "value": moving_average.get("state") or "Trend pending", "why": moving_average.get("why") or "5D/25D moving-average relationship."},
    {"label": "Macro driver", "value": region_analysis.get("driver", "mixed"), "why": region_analysis.get("whyChanged", "Bond, inflation, and policy context.")},
    {"label": "Event tone", "value": sentiment.get("label") or "Balanced", "why": event_title[:140]},
  ]
  interpretation = [
    f"{stance}: model edge {edge_score:.0f}/100 with {risk_level.lower()} event/model risk.",
    f"Scenario split is upside {upside:.0f}%, base {base:.0f}%, downside {downside:.0f}% and is not a trading instruction.",
    f"Bond anchor: {((bonds.get('curve') or {}).get('shape') or 'mixed').lower()} curve, {policy.get('centralBank', 'central bank')} stance {str(policy.get('stance', 'watching')).lower()}, inflation impulse {str(inflation.get('impulse', 'mixed')).lower()}.",
  ]
  monitor = [
    f"Confirm whether 5D/25D spread holds above {ma_spread:.2f}%.",
    f"Watch volume versus normal: {format_large_number(snapshot.get('volume') or 0)} traded.",
    *(region_analysis.get("monitorNext") or [])[:2],
  ]
  return {
    "title": "Decision cockpit",
    "stance": stance,
    "edgeScore": round(edge_score, 1),
    "riskLevel": risk_level,
    "confidence": round(confidence, 1),
    "asOf": snapshot.get("asOf") or datetime.now(timezone.utc).isoformat(),
    "facts": facts,
    "interpretation": interpretation,
    "monitor": monitor[:4],
    "unknowns": (region_analysis.get("unknowns") or [])[:2],
    "sourceNote": "Uses live quote, local history, moving averages, radar sentiment, bonds, inflation, and policy context.",
  }


def build_operator_feature_cards(snapshot: dict, region_payload: dict, radar: dict | None = None) -> list[dict]:
  forecast = snapshot.get("forecast") or {}
  session = snapshot.get("marketSession") or {}
  expert = snapshot.get("expertOutlook") or {}
  analysis = region_payload.get("analysis") or {}
  radar = radar or {}
  sentiment = radar.get("sentiment") or {}
  price = float(snapshot.get("price") or 0)
  previous = float(snapshot.get("previousClose") or price or 1)
  day_move = pct_change(price, previous) if previous else 0.0
  return [
    {"label": "Session", "value": session.get("status") or "Unknown", "note": session.get("hoursLabel") or "Market hours pending"},
    {"label": "Source", "value": snapshot.get("dataSource") or "Unknown", "note": snapshot.get("historySource") or "History source pending"},
    {"label": "Liquidity", "value": format_large_number(snapshot.get("volume") or 0), "note": "Current traded volume"},
    {"label": "Move", "value": f"{day_move:+.2f}%", "note": "Latest versus previous close"},
    {"label": "Projection", "value": f"{float(forecast.get('expectedReturn') or 0):+.2f}%", "note": f"{forecast.get('direction', 'Neutral')} scenario"},
    {"label": "Model agreement", "value": (forecast.get("models") or {}).get("agreement", {}).get("label", "Pending"), "note": (forecast.get("models") or {}).get("agreement", {}).get("summary", "Agreement pending")},
    {"label": "External experts", "value": expert.get("label") or "Unavailable", "note": expert.get("sourceLabel") or "Web outlook pending"},
    {"label": "Macro driver", "value": analysis.get("driver", "mixed"), "note": analysis.get("confidence", "Confidence pending")},
    {"label": "Event pressure", "value": forecast.get("eventPressureLabel") or "Pending", "note": sentiment.get("label") or "Radar sentiment pending"},
    {"label": "Cache", "value": snapshot.get("historyCacheState") or "live", "note": snapshot.get("historyCachedAt") or "Live edge / fallback series"},
  ]


def sma_value(history: list[float], period: int) -> float | None:
  values = [float(value) for value in (history or []) if value is not None]
  if len(values) < period:
    return None
  return average(values[-period:])


def format_metric_value(value, kind: str = "plain", currency: str = "") -> str:
  if value in (None, "", "n/a"):
    return "Unavailable"
  try:
    number = float(value)
  except (TypeError, ValueError):
    return str(value)
  if kind == "currency":
    return f"{currency} {number:,.2f}".strip()
  if kind == "large":
    return format_large_number(number)
  if kind == "percent":
    return f"{number:.2f}%"
  if kind == "ratio":
    return f"{number:.2f}x"
  return f"{number:,.2f}"


def benchmark_symbols_for_region(region_key: str) -> list[dict]:
  if region_key == "india":
    return [
      {"symbol": "^NSEI", "label": "NIFTY 50"},
      {"symbol": "^BSESN", "label": "SENSEX"},
    ]
  return [
    {"symbol": "^GSPC", "label": "S&P 500"},
    {"symbol": "^NDX", "label": "NASDAQ 100"},
  ]


def normalized_return_series(label: str, symbol: str, history: list[float]) -> dict:
  values = [float(item) for item in (history or []) if item is not None]
  if not values:
    return {"label": label, "symbol": symbol, "series": [], "returnPercent": 0.0}
  base = values[0] or 1
  series = [round(pct_change(value, base), 2) for value in values[-80:]]
  return {
    "label": label,
    "symbol": symbol,
    "series": series,
    "returnPercent": round(series[-1], 2) if series else 0.0,
  }


def peer_candidates_for_symbol(symbol: str, currency: str, exchange: str, sector: str) -> list[str]:
  upper = (symbol or "").upper()
  region_key = infer_region_key(upper, exchange, currency)
  preferred = []
  if region_key == "india":
    if "BANK" in upper or "BANK" in sector.upper():
      preferred = ["HDFCBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS", "BANKBARODA.NS"]
    elif "PHARMA" in upper or "HEALTH" in sector.upper():
      preferred = ["SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS", "DIVISLAB.NS", "LUPIN.NS"]
    elif "AIRTEL" in upper or "TELECOM" in sector.upper():
      preferred = ["RELIANCE.NS", "IDEA.NS", "TATACOMM.NS", "HFCL.NS", "TEJASNET.NS"]
    else:
      preferred = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "SBIN.NS"]
  else:
    if upper in {"AAPL", "MSFT", "GOOGL", "META", "AMZN"}:
      preferred = ["MSFT", "AAPL", "GOOGL", "META", "AMZN", "NVDA"]
    elif upper in {"NVDA", "AMD"}:
      preferred = ["NVDA", "AMD", "AVGO", "QCOM", "INTC", "TSM"]
    else:
      preferred = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META"]
  fallback_pool = [candidate for candidate, meta in FALLBACK_TICKERS.items() if meta.get("currency") == currency and candidate != upper]
  return [item for item in list(dict.fromkeys(preferred + fallback_pool)) if item != upper][:5]


def build_peer_comparison(symbol: str, currency: str, exchange: str, sector: str) -> list[dict]:
  peers = peer_candidates_for_symbol(symbol, currency, exchange, sector)
  rows = []
  for peer in peers[:5]:
    quote = {}
    fallback = fallback_meta(peer)
    cached = load_cached_history(peer, "1Y")
    history = cached[0] if cached else []
    latest = float(quote.get("regularMarketPrice") or (history[-1] if history else fallback["basePrice"]))
    first = float(history[0]) if history else latest
    pe = quote.get("trailingPE") or fallback.get("pe")
    market_cap = quote.get("marketCap")
    rows.append(
      {
        "symbol": peer,
        "name": quote.get("shortName") or quote.get("longName") or fallback["name"],
        "marketCap": format_metric_value(market_cap, "large"),
        "pe": format_metric_value(pe, "ratio"),
        "oneYearReturn": format_metric_value(pct_change(latest, first), "percent") if first else "Unavailable",
        "salesGrowth": "Unavailable",
        "roe": "Unavailable",
        "valuationGap": "Unavailable" if pe in (None, "") else format_metric_value(float(pe) - float(fallback.get("pe") or pe), "ratio"),
      }
    )
  return rows


def build_expert_consensus(summary: dict, recommendation: dict) -> dict:
  financial_data = summary.get("financialData") or {}
  trend = ((summary.get("recommendationTrend") or {}).get("trend") or [])
  current = trend[0] if trend else {}
  buy_count = int((current.get("strongBuy") or 0) + (current.get("buy") or 0))
  hold_count = int(current.get("hold") or 0)
  sell_count = int((current.get("sell") or 0) + (current.get("strongSell") or 0))
  total = buy_count + hold_count + sell_count
  mean = raw_value(financial_data, "recommendationMean")
  key = raw_value(financial_data, "recommendationKey")
  opinions = raw_value(financial_data, "numberOfAnalystOpinions")
  if not total and opinions:
    hold_count = int(opinions)
    total = hold_count
  return {
    "buy": round((buy_count / total) * 100) if total else 0,
    "hold": round((hold_count / total) * 100) if total else 0,
    "sell": max(0, 100 - round((buy_count / total) * 100) - round((hold_count / total) * 100)) if total else 0,
    "rawCounts": {"buy": buy_count, "hold": hold_count, "sell": sell_count, "total": total},
    "rating": str(key or "Unavailable").title(),
    "mean": mean,
    "sourceLabel": "Yahoo Finance quote summary",
    "note": "External analyst consensus only; not dashboard advice.",
    "fallbackScenario": recommendation,
  }


def infer_external_view(title: str) -> str:
  lowered = title.lower()
  if any(word in lowered for word in {"buy", "outperform", "overweight", "accumulate", "add"}):
    return "Constructive"
  if any(word in lowered for word in {"sell", "reduce", "underperform", "downgrade"}):
    return "Cautious"
  if any(word in lowered for word in {"hold", "neutral", "market perform"}):
    return "Neutral"
  if any(word in lowered for word in {"target", "price target", "upside", "downside"}):
    return "Target watch"
  return "Context"


def extract_domain_from_url(url: str) -> str:
  try:
    return urllib.parse.urlparse(url).hostname.replace("www.", "")
  except AttributeError:
    return ""


def extract_price_target_from_title(title: str, currency: str) -> str:
  patterns = [
    r"(?:target|price target|tp|fair value)[^\d]{0,24}([0-9][0-9,]*(?:\.[0-9]+)?)",
    r"([0-9][0-9,]*(?:\.[0-9]+)?)[^\d]{0,18}(?:target|price target|tp)",
  ]
  for pattern in patterns:
    match = re.search(pattern, title, flags=re.IGNORECASE)
    if match:
      return f"{currency} {match.group(1)}"
  return ""


def build_expert_outlook(symbol: str, snapshot: dict, fallback: dict) -> dict:
  name = snapshot.get("name") or fallback.get("name") or symbol
  exchange = snapshot.get("exchange") or fallback.get("exchange") or ""
  currency = snapshot.get("currency") or fallback.get("currency") or ""
  region_key = infer_region_key(symbol, exchange, currency)
  market_terms = "India NSE BSE brokerages analyst price target" if region_key == "india" else "analyst price target rating"
  query = f"{name} {symbol.replace('.NS', '').replace('.BO', '')} share price target analyst rating {market_terms}"
  results = duckduckgo_search(query)
  items = []
  seen = set()
  for result in results[:8]:
    title = result.get("title") or ""
    url = result.get("url") or ""
    if not title or url in seen:
      continue
    seen.add(url)
    items.append(
      {
        "title": title,
        "url": url,
        "source": extract_domain_from_url(url) or "Web result",
        "view": infer_external_view(title),
        "target": extract_price_target_from_title(title, currency),
      }
    )
  constructive = sum(1 for item in items if item["view"] == "Constructive")
  cautious = sum(1 for item in items if item["view"] == "Cautious")
  neutral = sum(1 for item in items if item["view"] in {"Neutral", "Target watch", "Context"})
  if constructive > cautious and constructive >= neutral:
    consensus_label = "Constructive external tone"
  elif cautious > constructive and cautious >= neutral:
    consensus_label = "Cautious external tone"
  elif items:
    consensus_label = "Mixed external tone"
  else:
    consensus_label = "External outlook unavailable"
  return {
    "label": consensus_label,
    "query": query,
    "items": items[:5],
    "sourceLabel": "Curated web results",
    "asOf": datetime.now(timezone.utc).isoformat(),
    "note": "External headlines and analyst-result snippets are context only; verify source pages before relying on targets.",
  }


def build_influence_graph(symbol: str, summary: dict) -> dict:
  nodes = [{"id": symbol, "label": symbol, "group": "company", "confidence": "High"}]
  edges = []
  ledger = []
  holders = summary.get("majorHoldersBreakdown") or {}
  for key, label in [
    ("insidersPercentHeld", "Insider ownership"),
    ("institutionsPercentHeld", "Institution ownership"),
  ]:
    value = raw_value(holders, key)
    if value is None:
      continue
    node_id = f"{symbol}:{key}"
    nodes.append({"id": node_id, "label": label, "group": "holder", "value": format_metric_value(float(value) * 100, "percent"), "confidence": "Medium"})
    edges.append({"source": symbol, "target": node_id, "relation": "reported holding", "confidence": "Medium", "sourceLabel": "Yahoo Finance quote summary"})
    ledger.append({"claim": f"{label}: {format_metric_value(float(value) * 100, 'percent')}", "sourceLabel": "Yahoo Finance quote summary", "confidence": "Medium", "status": "Public provider field; not independently verified here."})
  for project in company_projects_for_symbol(symbol)[:3]:
    if not project.get("sourceUrl") and not project.get("sourceLabel"):
      continue
    project_id = f"{symbol}:project:{slugify_note_name(project.get('title', 'project'))}"
    nodes.append({"id": project_id, "label": project.get("title", "Project"), "group": "project", "value": project.get("worthLabel", "Undisclosed"), "confidence": "Medium"})
    edges.append({"source": symbol, "target": project_id, "relation": "public project exposure", "confidence": "Medium", "sourceLabel": project.get("sourceLabel", "Curated public project map"), "sourceUrl": project.get("sourceUrl", "")})
    ledger.append({"claim": f"Project exposure: {project.get('title', 'Project')}", "sourceLabel": project.get("sourceLabel", "Curated public project map"), "sourceUrl": project.get("sourceUrl", ""), "confidence": "Medium", "status": "Shown as context only."})
  return {"nodes": nodes, "edges": edges, "ledger": ledger, "policy": "Public cited relationships only; no unsourced political or shell-company claims."}


def build_stock_dossier(symbol: str, snapshot: dict, quote: dict, summary: dict, history: list[float], model_history: list[float]) -> dict:
  def numeric_or_none(value) -> float | None:
    try:
      parsed = float(value)
    except (TypeError, ValueError):
      return None
    return parsed if math.isfinite(parsed) else None

  def activity_metric(value, label: str, source: str, *, unit: str = "percent", available: bool = True, reason: str = "") -> dict:
    if not available or value is None:
      return {"value": None, "label": "Unavailable", "unit": unit, "source": source, "status": reason or "Provider value unavailable"}
    return {"value": value, "label": label, "unit": unit, "source": source, "status": "Available"}

  currency = snapshot.get("currency") or fallback_meta(symbol)["currency"]
  region_key = infer_region_key(symbol, snapshot.get("exchange"), currency)
  financial_data = summary.get("financialData") or {}
  statistics_block = summary.get("defaultKeyStatistics") or {}
  summary_detail = summary.get("summaryDetail") or {}
  latest = numeric_or_none(snapshot.get("price")) or 0.0
  previous_close_raw = snapshot.get("previousClose") or quote.get("regularMarketPreviousClose")
  previous_close_value = numeric_or_none(previous_close_raw)
  previous_close = previous_close_value if previous_close_value is not None else latest
  avg_volume = quote.get("averageDailyVolume3Month") or quote.get("averageDailyVolume10Day") or None
  avg_volume_value = numeric_or_none(avg_volume)
  volume_value = numeric_or_none(snapshot.get("volume"))
  two_day_available = len(history) >= 3 and numeric_or_none(history[-1]) is not None and numeric_or_none(history[-3]) not in (None, 0)
  two_day_move = pct_change(float(history[-1]), float(history[-3])) if two_day_available else None
  gap_available = previous_close_value not in (None, 0) and latest > 0
  gap_percent = pct_change(latest, previous_close_value) if gap_available else None
  volume_available = volume_value is not None and avg_volume_value not in (None, 0)
  volume_ratio = round(volume_value / avg_volume_value, 2) if volume_available else None
  high_52w_value = numeric_or_none(quote.get("fiftyTwoWeekHigh"))
  breakout_label = "52W breakout" if high_52w_value and latest >= high_52w_value * 0.995 else "Range watch"
  moving_average_periods = [5, 20, 25, 50, 200]
  moving_averages = []
  for period in moving_average_periods:
    value = sma_value(model_history or history, period)
    moving_averages.append(
      {
        "period": period,
        "value": value,
        "label": f"SMA {period}",
        "distancePercent": pct_change(latest, value) if value else None,
        "state": "Above" if value and latest >= value else "Below" if value else "Unavailable",
      }
    )
  benchmark_items = [{"symbol": symbol, "label": symbol, "history": history}]
  for benchmark in benchmark_symbols_for_region(region_key):
    cached_benchmark = load_cached_history(benchmark["symbol"], "1Y")
    benchmark_history = cached_benchmark[0] if cached_benchmark else []
    if len(benchmark_history) < 2:
      benchmark_history, _ = build_history(benchmark["symbol"], "1Y", allow_live_refresh=False)
    benchmark_items.append({"symbol": benchmark["symbol"], "label": benchmark["label"], "history": benchmark_history})
  return {
    "daySnapshot": {
      "open": quote.get("regularMarketOpen"),
      "previousClose": previous_close,
      "dayLow": quote.get("regularMarketDayLow") or quote.get("dayLow"),
      "dayHigh": quote.get("regularMarketDayHigh") or quote.get("dayHigh"),
      "fiftyTwoWeekLow": quote.get("fiftyTwoWeekLow"),
      "fiftyTwoWeekHigh": quote.get("fiftyTwoWeekHigh"),
      "lowerCircuit": None,
      "upperCircuit": None,
      "volume": snapshot.get("volume"),
      "averageVolume": avg_volume,
      "source": snapshot.get("dataSource") or "Quote provider",
    },
    "fundamentals": {
      "eps": raw_value(statistics_block, "trailingEps"),
      "revenue": raw_value(financial_data, "totalRevenue"),
      "netIncome": raw_value(financial_data, "netIncomeToCommon"),
      "grossMargins": raw_value(financial_data, "grossMargins"),
      "profitMargins": raw_value(financial_data, "profitMargins"),
      "debtToEquity": raw_value(financial_data, "debtToEquity"),
      "roe": raw_value(financial_data, "returnOnEquity"),
      "roa": raw_value(financial_data, "returnOnAssets"),
      "freeCashflow": raw_value(financial_data, "freeCashflow"),
      "salesGrowth": raw_value(financial_data, "revenueGrowth"),
      "trailingPe": quote.get("trailingPE") or raw_value(summary_detail, "trailingPE"),
      "forwardPe": raw_value(summary_detail, "forwardPE"),
      "scores": {
        "quality": round(clamp((float(raw_value(financial_data, "returnOnEquity", 0) or 0) * 120) + 45, 0, 100), 1),
        "valuation": round(clamp(72 - float((quote.get("trailingPE") or raw_value(summary_detail, "trailingPE") or 28)) * 0.9, 0, 100), 1),
        "risk": round(clamp(100 - float((snapshot.get("forecast") or {}).get("mae") or 0) * 8, 0, 100), 1),
      },
      "source": "Yahoo Finance quote summary",
    },
    "movingAverages": moving_averages,
    "peerComparison": build_peer_comparison(symbol, currency, snapshot.get("exchange") or "", snapshot.get("sector") or ""),
    "benchmarkComparison": [normalized_return_series(item["label"], item["symbol"], item["history"]) for item in benchmark_items],
    "expertConsensus": build_expert_consensus(summary, snapshot.get("recommendation") or {}),
    "unusualActivity": {
      "volumeRatio": volume_ratio,
      "twoDayMove": two_day_move,
      "gapPercent": gap_percent,
      "breakout": breakout_label,
      "metrics": {
        "twoDayMove": activity_metric(two_day_move, f"{two_day_move:+.2f}%" if two_day_move is not None else "Unavailable", "Local historical cache", available=two_day_available, reason="Need at least 3 valid history points"),
        "gapPercent": activity_metric(gap_percent, f"{gap_percent:+.2f}%" if gap_percent is not None else "Unavailable", snapshot.get("dataSource") or "Quote provider", available=gap_available, reason="Previous close missing or zero"),
        "volumeRatio": activity_metric(volume_ratio, f"{volume_ratio:.2f}x" if volume_ratio is not None else "Unavailable", snapshot.get("dataSource") or "Quote provider", unit="ratio", available=volume_available, reason="Average volume missing or zero"),
        "breakout": {"value": breakout_label, "label": breakout_label, "unit": "state", "source": snapshot.get("dataSource") or "Quote provider", "status": "52W high available" if high_52w_value else "52W high unavailable; using range watch"},
      },
    },
    "metricDrawer": [
      {"section": "Day snapshot", "metrics": ["open", "previousClose", "dayLow", "dayHigh", "volume", "averageVolume"]},
      {"section": "Fundamentals", "metrics": ["eps", "revenue", "netIncome", "roe", "salesGrowth", "debtToEquity"]},
      {"section": "Moving averages", "metrics": [f"SMA {period}" for period in moving_average_periods]},
    ],
    "influenceGraph": build_influence_graph(symbol, summary),
    "sourceProvenance": [
      {"label": snapshot.get("dataSource") or "Quote provider", "usedFor": "price/day snapshot"},
      {"label": "Local historical cache", "usedFor": "moving averages and benchmark normalization"},
      {"label": "Yahoo Finance quote summary", "usedFor": "fundamentals, consensus, holder fields where available"},
    ],
  }


def build_market_discovery(watchlist: list[dict]) -> dict:
  items = []
  for item in watchlist[:10]:
    cached = load_cached_history(item["symbol"], "5D") or load_cached_history(item["symbol"], "1M")
    history = cached[0] if cached else []
    if len(history) < 3:
      continue
    two_day = pct_change(history[-1], history[-3])
    avg_volume = item.get("volume") or 0
    reason = "Two-day price acceleration" if abs(two_day) >= 2 else "Watchlist movement"
    if abs(two_day) >= 1 or item.get("changePercent"):
      items.append(
        {
          "symbol": item["symbol"],
          "name": item.get("name", item["symbol"]),
          "twoDayMove": round(two_day, 2),
          "latestMove": round(float(item.get("changePercent") or 0), 2),
          "volume": int(avg_volume or 0),
          "reason": reason,
          "confidence": "Medium" if abs(two_day) >= 2 else "Low",
          "source": "Local history + live quote",
        }
      )
  items.sort(key=lambda entry: abs(entry["twoDayMove"]) + abs(entry["latestMove"]), reverse=True)
  return {"items": items[:5], "updatedAt": datetime.now(timezone.utc).isoformat(), "source": "Local history cache and live quote feed"}


def build_ticker_snapshot(symbol: str, quote: dict | None = None, stress: str = "base", horizon: int = 10, chart_range: str = "1M") -> dict:
  quotes = fetch_live_quotes([symbol], fast=True) if quote is None else {symbol: quote}
  quote = quotes.get(symbol) or {}
  with ThreadPoolExecutor(max_workers=4) as executor:
    history_future = executor.submit(build_history, symbol, chart_range)
    summary_future = executor.submit(fetch_yahoo_quote_summary, symbol)
    rss_future = executor.submit(fetch_yahoo_rss, symbol)
    history, chart_meta = history_future.result()
    summary = summary_future.result()
  fallback = fallback_meta(symbol)
  config = load_config()
  headlines = []
  if config.get("provider") == "alpha_vantage" and config.get("alphaVantageApiKey"):
    headlines = fetch_alpha_vantage_news(symbol, config.get("alphaVantageApiKey", ""))
  if not headlines:
    headlines = rss_future.result()
  company_query = f"{fallback['name']} stock news {fallback['exchange']}"
  headlines = dedupe_list(headlines + headline_texts_from_search(company_query))
  news_count = len(headlines)

  model_history = history
  if len(model_history) < 70:
    longer_history, _ = build_history(symbol, "1Y")
    if len(longer_history) >= len(model_history):
      model_history = longer_history

  latest_price = float(quote.get("regularMarketPrice") or (history[-1] if history else fallback["basePrice"]))
  previous_close = float(quote.get("regularMarketPreviousClose") or (history[-2] if len(history) > 1 else latest_price))
  change_percent = float(quote.get("regularMarketChangePercent") or pct_change(latest_price, previous_close))
  forecast = build_forecast(symbol, quote, summary, model_history, stress=stress, horizon=horizon, news_count=news_count)
  # Additive: hand-crafted short-horizon model output rides on the same
  # forecast object under a namespaced key. Horizon is independent from the
  # existing forecast horizon (capped at 10 for the short-horizon model).
  forecast["shortHorizon"] = build_short_horizon_forecast(model_history, horizon=min(int(horizon), 10))
  backtest = build_backtest(symbol, model_history, quote, summary, horizon, stress, news_count)
  # Self-retraining: blend new walk-forward residuals into a persisted state and
  # apply the learned bias correction before downstream consumers see the forecast.
  training_fingerprint = model_training_fingerprint(model_history, horizon)
  model_state = update_model_residual_state(symbol, horizon, backtest, training_fingerprint)
  forecast = apply_residual_correction(forecast, model_state)
  # Empirical walk-forward MAE replaces the vol-scaled heuristic once we have a
  # meaningful sample. Below the threshold we keep the heuristic but flag it.
  if backtest.get("sampleCount", 0) >= 6:
    forecast["maeHeuristic"] = float(forecast.get("mae") or 0.0)
    forecast["mae"] = float(backtest.get("mae") or forecast.get("mae") or 0.0)
    forecast["maeSource"] = "walk-forward"
  else:
    forecast["maeSource"] = "vol-scaled heuristic"
  forecast["backtestSamples"] = int(backtest.get("sampleCount", 0))
  forecast["backtestHitRate"] = float(backtest.get("hitRate", 0.0))
  forecast["backtestMedianApe"] = float(backtest.get("medianApe", 0.0))
  forecast["learning"] = {
    "learnedBias": float(model_state.get("learnedBias") or 0.0),
    "residualStd": float(model_state.get("residualStd") or 0.0),
    "trainingRuns": int(model_state.get("trainingRuns") or 0),
    "trainedAt": model_state.get("trainedAt"),
    "samples": int(model_state.get("samples") or 0),
    "status": model_state.get("status") or "warming-up",
    "biasApplied": float(forecast.get("learnedBiasApplied") or 0.0),
    "modelVersion": model_state.get("modelVersion") or MODEL_STATE_VERSION,
    "dataFingerprint": model_state.get("dataFingerprint") or training_fingerprint,
    "didUpdate": bool(model_state.get("didUpdate")),
  }
  recommendation = build_recommendation(forecast)

  market_cap = quote.get("marketCap")
  trailing_pe = quote.get("trailingPE") or ((summary.get("summaryDetail") or {}).get("trailingPE") or {}).get("raw")
  fifty_two_week_low = quote.get("fiftyTwoWeekLow")
  fifty_two_week_high = quote.get("fiftyTwoWeekHigh")
  volume = quote.get("regularMarketVolume") or quote.get("averageDailyVolume3Month") or 0
  avg_volume = quote.get("averageDailyVolume3Month") or quote.get("averageDailyVolume10Day") or 0
  sector = ((summary.get("assetProfile") or {}).get("sector")) or fallback["exchange"]
  industry = ((summary.get("assetProfile") or {}).get("industry")) or fallback["name"]
  signal_map = extract_signal_map(headlines, symbol, sector, industry)
  event_focus = infer_event_focus(headlines, signal_map)
  volume_ratio = float(volume or 0) / float(avg_volume or volume or 1)
  data_source = quote.get("quoteSource") or ("Live source" if quote else (chart_meta.get("historySource") or "History-derived"))
  market_time = quote.get("regularMarketTime") or chart_meta.get("regularMarketTime")
  chart_timestamps = chart_meta.get("timestamps") or []
  chart_as_of = chart_timestamps[-1] if chart_timestamps else None
  as_of = timestamp_from_epoch(market_time) if market_time else quote_effective_as_of(quote, data_source, chart_as_of)
  exchange_name = quote.get("fullExchangeName") or quote.get("exchange") or chart_meta.get("exchangeName") or fallback["exchange"]
  region_name = quote.get("exchange") or fallback["exchange"]
  session_state = quote_session_state(quote, data_source)
  market_session = build_market_session(exchange_name, region_name, session_state, as_of)
  freshness = quote_freshness(as_of, market_session, data_source)
  classic_inputs = build_forecast_inputs(symbol, quote, summary, model_history, news_count) if model_history else {
    "latestPrice": latest_price,
    "previousPrice": previous_close,
    "beta": float(fallback["beta"]),
    "pe": float(fallback["pe"]),
    "qualityScore": 0.5,
    "eventScore": 0.25,
    "marketCap": market_cap or 0,
  }

  relationship_inputs = {
    "pe": float(trailing_pe or fallback["pe"]),
    "volumeRatio": volume_ratio,
  }
  relationship_cards = build_relationship_cards(relationship_inputs, signal_map)
  driver_cards = build_driver_cards(signal_map, summary, forecast)
  classic_quant_cards = build_classic_quant_cards(
    model_history or history or [latest_price, previous_close],
    classic_inputs,
    volume_ratio,
    forecast["realizedVol"],
    forecast.get("factorsRaw", {}).get("macroScore", 0.0),
  )
  classic_quant = {
    "summary": summarize_classic_quant(classic_quant_cards, forecast),
    "cards": classic_quant_cards,
  }
  snapshot_context = {
    "symbol": symbol,
    "name": quote.get("shortName") or quote.get("longName") or fallback["name"],
    "exchange": exchange_name,
    "region": region_name,
    "currency": quote.get("currency") or chart_meta.get("currency") or fallback["currency"],
    "dataSource": data_source,
    "dataProviderId": quote.get("quoteProviderId"),
    "dataSourceRank": quote.get("quoteSourceRank"),
    "dataSourceCount": quote.get("quoteSourceCount"),
    "dataSourceType": quote.get("quoteSourceType"),
    "dataSourceCheckedAt": quote.get("quoteSourceCheckedAt"),
    "quoteFreshness": freshness,
    "price": latest_price,
    "previousClose": previous_close,
    "changePercent": change_percent,
    "volume": int(volume or 0),
    "sector": sector,
    "industry": industry,
    "forecast": forecast,
    "recommendation": recommendation,
  }
  expert_outlook = build_expert_outlook(symbol, snapshot_context, fallback)

  return {
    "symbol": symbol,
    "name": quote.get("shortName") or quote.get("longName") or fallback["name"],
    "exchange": exchange_name,
    "region": region_name,
    "currency": quote.get("currency") or chart_meta.get("currency") or fallback["currency"],
    "marketState": session_state,
    "marketSession": market_session,
    "dataSource": data_source,
    "dataProviderId": quote.get("quoteProviderId"),
    "dataSourceRank": quote.get("quoteSourceRank"),
    "dataSourceCount": quote.get("quoteSourceCount"),
    "dataSourceType": quote.get("quoteSourceType"),
    "dataSourceCheckedAt": quote.get("quoteSourceCheckedAt"),
    "historySource": chart_meta.get("historySource") or "Unavailable",
    "historyCachedAt": chart_meta.get("historyCachedAt"),
    "historyCacheState": chart_meta.get("historyCacheState"),
    "asOf": as_of,
    "quoteFreshness": freshness,
    "price": latest_price,
    "previousClose": previous_close,
    "changePercent": change_percent,
    "volume": int(volume or 0),
    "history": history,
    "historySeries": history_points_from_meta(history, chart_meta),
    "sector": sector,
    "industry": industry,
    "regime": forecast["regime"],
    "forecast": forecast,
    "recommendation": recommendation,
    "expertOutlook": expert_outlook,
    "chartRange": chart_range,
    "relationshipCards": relationship_cards,
    "driverCards": driver_cards,
    "eventFocus": event_focus,
    "classicQuant": classic_quant,
    "stockDossier": build_stock_dossier(symbol, snapshot_context, quote, summary, history, model_history),
    "sentiment": signal_map["sentiment"],
    "stats": [
      {"label": "Market cap", "value": format_large_number(market_cap)},
      {"label": "Trailing P/E", "value": f"{float(trailing_pe):.2f}" if trailing_pe else "n/a"},
      {"label": "Trade volume", "value": format_large_number(volume)},
      {"label": "Avg volume", "value": format_large_number(avg_volume)},
      {
        "label": "52W range",
        "value": (
          f"{float(fifty_two_week_low):.2f} - {float(fifty_two_week_high):.2f}"
          if fifty_two_week_low and fifty_two_week_high
          else "n/a"
        ),
      },
      {"label": "Backtest hit rate", "value": f"{backtest['hitRate']:.1f}%"},
    ],
    "headlines": headlines or FALLBACK_HEADLINES[:4],
    "lab": {
      "symbol": symbol,
      "history": history[-40:],
      "historySeries": history_points_from_meta(history[-40:], {"timestamps": (chart_meta.get("timestamps") or [])[-40:]}),
      "projected": forecast["projected"],
      "expectedReturn": forecast["expectedReturn"],
      "direction": forecast["direction"],
      "confidence": forecast["confidence"],
      "triggers": forecast["triggers"],
      "backtest": backtest,
      "historySource": chart_meta.get("historySource") or "Unavailable",
      "historyCachedAt": chart_meta.get("historyCachedAt"),
      "historyCacheState": chart_meta.get("historyCacheState"),
      "classicQuant": classic_quant,
    },
  }


def build_macro_pulse() -> list[dict]:
  return memory_cached_value("macro-pulse", 60, build_macro_pulse_uncached) or FALLBACK_MACRO_PULSE


def build_macro_pulse_uncached() -> list[dict]:
  quotes = fetch_yahoo_quotes([item["symbol"] for item in MACRO_SYMBOLS])
  items = []
  for macro in MACRO_SYMBOLS:
    quote = quotes.get(macro["symbol"])
    if not quote:
      continue
    price = quote.get("regularMarketPrice")
    change = float(quote.get("regularMarketChangePercent") or 0)
    currency = quote.get("currency") or "USD"
    if price is None:
      continue
    value = f"{price:.2f}" if macro["symbol"] == "^TNX" else (
      f"{price:.2f}%" if macro["symbol"] == "^GSPC" and False else str(price)
    )
    if macro["symbol"] in {"CL=F", "GC=F"}:
      value = f"{price:.2f} {currency}"
    elif macro["symbol"] == "^TNX":
      value = f"{price/10:.2f}%"
    else:
      value = f"{price:.2f}"
    items.append(
      {
        "label": macro["label"],
        "value": value,
        "trend": f"{change:+.2f}%",
        "positive": change >= 0,
      }
    )
  return items or FALLBACK_MACRO_PULSE


def build_region_bond_snapshot(region_key: str) -> dict:
  config = region_config(region_key)

  def builder() -> dict:
    fallback = REGION_BOND_FALLBACKS[config["key"]]
    tenors = [dict(item) for item in fallback["tenors"]]
    source = fallback["source"]
    fred_curve = None
    if config["key"] == "us":
      fred_curve = fetch_us_fred_curve()
      if fred_curve:
        tenors = [
          {"tenor": "2Y", "yield": fred_curve["2Y"]["value"], "change1D": fallback["tenors"][0]["change1D"]},
          {"tenor": "5Y", "yield": fred_curve["5Y"]["value"], "change1D": fallback["tenors"][1]["change1D"]},
          {"tenor": "10Y", "yield": fred_curve["10Y"]["value"], "change1D": fallback["tenors"][2]["change1D"]},
          {"tenor": "30Y", "yield": fred_curve["30Y"]["value"], "change1D": fallback["tenors"][3]["change1D"]},
        ]
        source = "FRED"
    slope_2s10s = tenors[2]["yield"] - tenors[0]["yield"]
    slope_5s30s = tenors[3]["yield"] - tenors[1]["yield"]
    curve_shape = "Steepening" if slope_2s10s > 0.18 else "Flat" if abs(slope_2s10s) <= 0.18 else "Inverted"
    direction = "Higher yields" if sum(item["change1D"] for item in tenors) > 0 else "Lower yields"
    return {
      "region": config["key"],
      "label": f"{config['label']} bond market",
      "tenors": tenors,
      "curve": {
        "slope2s10s": round(slope_2s10s, 2),
        "slope5s30s": round(slope_5s30s, 2),
        "shape": curve_shape,
        "direction": direction,
      },
      "policyRate": fallback["policyRate"],
      "breakeven": fred_curve["breakeven"]["value"] if config["key"] == "us" and fred_curve and fred_curve.get("breakeven") else fallback["breakeven"],
      "realYield": fallback["realYield"],
      "narrative": fallback["curveNarrative"],
      "asOf": datetime.now(timezone.utc).isoformat(),
      "source": source,
    }

  return get_or_refresh_cached_payload("region_bonds", f"region_bonds::{config['key']}", builder)


def build_region_inflation_snapshot(region_key: str, bonds: dict) -> dict:
  config = region_config(region_key)

  def builder() -> dict:
    fallback = REGION_INFLATION_FALLBACKS[config["key"]]
    headline = fallback["headline"]
    core = fallback["core"]
    source = fallback["source"]
    official_label = ""
    if config["key"] == "us":
      bls = fetch_bls_cpi_snapshot()
      if bls:
        source = bls["source"]
        official_label = bls.get("label", "")
    policy_rate = float(bonds.get("policyRate") or 0)
    real_policy_gap = round(policy_rate - headline, 2)
    impulse = "Inflation-driven" if headline > core + 0.6 else "Sticky core" if core >= headline else "Cooling impulse"
    return {
      "region": config["key"],
      "headline": headline,
      "core": core,
      "breakeven": bonds.get("breakeven"),
      "realPolicyGap": real_policy_gap,
      "impulse": impulse,
      "narrative": fallback["trend"],
      "asOf": datetime.now(timezone.utc).isoformat(),
      "source": source,
      "officialLabel": official_label,
    }

  return get_or_refresh_cached_payload("region_inflation", f"region_inflation::{config['key']}", builder)


def build_region_policy_snapshot(region_key: str, bonds: dict, inflation: dict) -> dict:
  config = region_config(region_key)
  stance = "Restrictive" if bonds.get("realYield", 0) > 1.5 else "Neutral"
  bias = "Data dependent"
  if config["key"] == "us":
    bias = "Watching inflation persistence and labor-market resilience"
  elif config["key"] == "india":
    bias = "Watching food inflation, liquidity, and crude pass-through"
  return {
    "centralBank": config["centralBank"],
    "policyRateLabel": config["policyRateLabel"],
    "policyRate": bonds.get("policyRate"),
    "stance": stance,
    "bias": bias,
    "inflationAnchor": inflation.get("headline"),
  }


def build_region_event_context(region_key: str) -> dict:
  config = region_config(region_key)
  def builder() -> dict:
    query = f"{config['label']} inflation rates central bank bond market latest"
    feed = build_event_feed("all", None, query)
    items = list(feed.get("items") or [])[:6]
    return {
      "query": query,
      "items": items,
      "asOf": feed.get("asOf"),
      "source": "RSS + search aggregation",
    }
  return get_or_refresh_cached_payload("region_events", f"region_events::{config['key']}", builder)


def build_region_calendar(region_key: str) -> dict:
  config = region_config(region_key)
  def builder() -> dict:
    items = fetch_fed_calendar_items() if config["key"] == "us" else fetch_rbi_calendar_items()
    if not items:
      items = [
        {
          "title": f"Next {config['centralBank']} communication",
          "date": "Schedule pending",
          "url": "",
          "source": config["centralBank"],
          "category": "calendar",
        }
      ]
    return {
      "items": items,
      "source": items[0]["source"] if items else config["centralBank"],
    }
  return get_or_refresh_cached_payload("region_calendar", f"region_calendar::{config['key']}", builder)


def build_region_equity_context(region_key: str, active_snapshot: dict | None, bonds: dict, inflation: dict) -> dict:
  config = region_config(region_key)
  notes = kb_notes_bundle(config["key"])
  slope = float((bonds.get("curve") or {}).get("slope2s10s") or 0)
  real_yield = float(bonds.get("realYield") or 0)
  impulse = inflation.get("impulse") or "Mixed"
  style_bias = "Defensives and banks" if real_yield > 1.8 else "Duration and growth"
  if config["key"] == "india" and inflation.get("headline", 0) > 5:
    style_bias = "Banks, domestic cyclicals, and pricing-power names"
  sectors = [
    {
      "sector": "Banks",
      "effect": "Positive" if slope >= 0 else "Mixed",
      "why": "Steeper curves and stable credit conditions usually support bank earnings leverage.",
    },
    {
      "sector": "Technology",
      "effect": "Negative" if real_yield > 1.8 else "Positive",
      "why": "Higher discount rates pressure long-duration valuation multiples first.",
    },
    {
      "sector": "Consumer",
      "effect": "Mixed" if inflation.get("headline", 0) > 4 else "Positive",
      "why": "Inflation pressure shifts focus to pricing power and input-cost pass-through.",
    },
    {
      "sector": "Energy",
      "effect": "Positive" if "inflation" in impulse.lower() or config["key"] == "india" else "Mixed",
      "why": "Commodity and geopolitical shocks can hold up energy cash flows while pressuring the rest of the market.",
    },
  ]
  positive_count = sum(1 for item in sectors if item["effect"] == "Positive")
  mixed_count = sum(1 for item in sectors if item["effect"] == "Mixed")
  negative_count = sum(1 for item in sectors if item["effect"] == "Negative")
  return {
    "styleBias": style_bias,
    "summary": f"{config['label']} equities are currently reading through the bond market via {impulse.lower()}, {real_yield:.2f}% real yields, and a {((bonds.get('curve') or {}).get('shape') or 'mixed').lower()} curve.",
    "breadth": {
      "label": "Broadening" if positive_count >= 2 else "Selective",
      "detail": f"{positive_count} positive • {mixed_count} mixed • {negative_count} negative sector reads",
    },
    "sectors": sectors,
    "activeRelevance": active_snapshot.get("symbol") if active_snapshot and infer_region_key(active_snapshot.get('symbol'), active_snapshot.get('exchange'), active_snapshot.get('currency')) == config["key"] else "",
    "kbNote": notes["sector"],
  }


def build_region_research_protocol(region_key: str, bonds: dict, inflation: dict) -> dict:
  registry = load_factor_registry()
  practices = [annotate_practice_coverage(item) for item in load_dashboard_practices()]
  macro_manifest = load_macro_dataset_manifest()
  region_manifest = (macro_manifest.get("regions") or {}).get(region_key, {})
  curve_shape = ((bonds.get("curve") or {}).get("shape") or "Mixed").lower()
  impulse = (inflation.get("impulse") or "Mixed").lower()
  key_factors = []
  preferred_domains = {"rates", "inflation", "policy", "equities", "events", "network"}
  for item in registry:
    if item.get("domain") not in preferred_domains:
      continue
    key_factors.append(
      {
        "label": item.get("label", "Factor"),
        "cadence": item.get("cadence", ""),
        "significance": item.get("significance", ""),
        "why": item.get("why", ""),
        "factsFirst": item.get("factsFirst", ""),
        "watchFor": item.get("watchFor", ""),
        "sourceLabel": item.get("sourceLabel", ""),
        "sourceUrl": item.get("sourceUrl", ""),
      }
    )
  summary = (
    f"Research protocol currently anchors on a {curve_shape} curve, {impulse} inflation read, and explicit policy/event transmission. "
    f"Interpretation is layered only after facts, cadence, and provenance are established."
  )
  return {
    "summary": summary,
    "factors": key_factors[:6],
    "practices": practices[:4],
    "datasets": {
      "seriesCount": region_manifest.get("seriesCount", 0),
      "sources": region_manifest.get("sources", []),
      "series": (region_manifest.get("series") or [])[:6],
    },
  }


IMPLEMENTED_RESEARCH_FACTORS = {
  "price history",
  "time ordering",
  "clean historical series",
  "multi-horizon windows",
  "momentum",
  "trend",
  "reversal",
  "price path",
  "volume",
  "liquidity regime",
  "mean reversion",
  "sector context",
  "concept graph",
  "shared information",
  "company relations",
}


PARTIAL_RESEARCH_FACTORS = {
  "uncertainty estimates",
  "long-context history",
  "normalized scale",
  "stable cadence",
  "turnover",
  "spread history",
  "co-movement",
}


def annotate_practice_coverage(practice: dict) -> dict:
  required = [str(item).lower() for item in (practice.get("requiredFactors") or [])]
  implemented = [item for item in required if item in IMPLEMENTED_RESEARCH_FACTORS]
  partial = [item for item in required if item in PARTIAL_RESEARCH_FACTORS]
  missing = [item for item in required if item not in IMPLEMENTED_RESEARCH_FACTORS and item not in PARTIAL_RESEARCH_FACTORS]
  if missing:
    status = "Partial"
  elif partial:
    status = "Partial"
  else:
    status = "Implemented"
  note = (
    f"{len(implemented)}/{len(required) or 1} required factors fully wired"
    + (f"; {len(partial)} partial" if partial else "")
    + (f"; {len(missing)} missing" if missing else "")
  )
  return {
    **practice,
    "implementationStatus": status,
    "implementedFactors": implemented,
    "partialFactors": partial,
    "missingFactors": missing,
    "coverageNote": note,
  }


def bond_equity_duration_flag(symbol: str) -> float:
  upper = (symbol or "").upper()
  if any(token in upper for token in {"AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TCS", "INFY"}):
    return 1.0
  return 0.35


def compute_project_dependency_pressure(symbol: str) -> tuple[float, int, int]:
  projects = company_projects_for_symbol(symbol)
  total_suppliers = 0
  high_impact = 0
  worth_scale = 0.0
  for project in projects:
    suppliers = project.get("suppliers") or []
    total_suppliers += len(suppliers)
    high_impact += sum(1 for supplier in suppliers if str(supplier.get("impact", "")).lower() == "high")
    worth_value = project.get("worthValue")
    if isinstance(worth_value, (int, float)) and worth_value > 0:
      worth_scale += math.log10(worth_value + 1)
  if total_suppliers <= 0:
    return 0.0, 0, 0
  score = (high_impact / total_suppliers) * max(0.8, worth_scale / max(1, len(projects)))
  return round(score, 3), high_impact, total_suppliers


def build_active_research_overview(snapshot: dict, region_payload: dict) -> dict:
  formulas = load_prediction_formulas()
  papers = [annotate_practice_coverage(item) for item in load_dashboard_practices()]
  forecast = snapshot.get("forecast") or {}
  factors_raw = forecast.get("factorsRaw") or {}
  bonds = region_payload.get("bonds") or {}
  inflation = region_payload.get("inflation") or {}
  event_pressure = float(forecast.get("eventPressure") or 0.0)
  volume = float(snapshot.get("volume") or 0.0)
  avg_volume_value = 0.0
  for stat in snapshot.get("stats") or []:
    if stat.get("label") == "Avg volume":
      avg_volume_value = parse_compact_number(stat.get("value"))
  volume_ratio = (volume / avg_volume_value) if avg_volume_value else 1.0
  fast_momentum = float(factors_raw.get("fastMomentum") or 0.0)
  slow_momentum = float(factors_raw.get("slowMomentum") or 0.0)
  trend_participation = (0.45 * fast_momentum) + (0.35 * slow_momentum) + (0.20 * centered_volume_participation(volume_ratio))
  duration_pressure = max(float(bonds.get("realYield") or 0.0) - 1.5, 0.0) * float((snapshot.get("forecast") or {}).get("models", {}).get("classic", {}).get("confidence", 0.0) / 100 or 0.5) * bond_equity_duration_flag(snapshot.get("symbol"))
  curve_impulse = float((bonds.get("curve") or {}).get("slope2s10s") or 0.0) * (1.0 if "BANK" in (snapshot.get("symbol") or "").upper() or "BANK" in (snapshot.get("name") or "").upper() else 0.35)
  project_pressure, high_impact_count, supplier_count = compute_project_dependency_pressure(snapshot.get("symbol", ""))
  z_score = 0.0
  classic_cards = snapshot.get("classicQuant", {}).get("cards") or []
  for card in classic_cards:
    if card.get("title") == "Price z-score":
      try:
        z_score = float(str(card.get("value", "0")).replace("+", ""))
      except ValueError:
        z_score = 0.0
        break
  formula_values = {
    "trend_participation": {"value": trend_participation, "display": f"{trend_participation:+.2f}", "note": f"MOM5 {fast_momentum:+.3f} • MOM20 {slow_momentum:+.3f} • VR {volume_ratio:.2f}x"},
    "duration_pressure": {"value": duration_pressure, "display": f"{duration_pressure:.2f}", "note": f"Real yield {float(bonds.get('realYield') or 0):.2f}% • duration flag {bond_equity_duration_flag(snapshot.get('symbol')):.2f}"},
    "curve_impulse": {"value": curve_impulse, "display": f"{curve_impulse:+.2f}", "note": f"2s10s {float((bonds.get('curve') or {}).get('slope2s10s') or 0):.2f}%"},
    "event_override": {"value": event_pressure, "display": f"{event_pressure:.2f}", "note": f"{snapshot.get('eventFocus', 'event')} focus • {snapshot.get('sentiment', {}).get('label', 'Mixed')} sentiment"},
    "project_dependency": {"value": project_pressure, "display": f"{project_pressure:.2f}", "note": f"{high_impact_count}/{supplier_count or 1} high-impact supplier links"},
    "reversion_stretch": {"value": z_score, "display": f"{z_score:+.2f}", "note": "20-session z-score from classic quant stack"},
  }
  cards = []
  for formula in formulas:
    mapped = formula_values.get(formula.get("key"))
    if not mapped:
      continue
    cards.append(
      {
        "label": formula.get("label", "Formula"),
        "formula": formula.get("formula", ""),
        "value": mapped["display"],
        "note": mapped["note"],
        "why": formula.get("why", ""),
        "cadence": formula.get("cadence", ""),
        "paperLink": formula.get("paperLink", ""),
      }
    )
  next_watch = [
    f"{region_payload.get('policy', {}).get('centralBank', 'Central bank')} path versus {region_payload.get('inflation', {}).get('headline', 0):.2f}% inflation.",
    f"Curve shape is {((bonds.get('curve') or {}).get('shape') or 'mixed').lower()} and can reprice sector leadership quickly.",
    f"{snapshot.get('symbol')} currently carries {supplier_count} mapped supplier/project links.",
  ]
  return {
    "headline": "Research stack ties bond moves, inflation, policy, events, and supplier/project links into the active equity read.",
    "cards": cards,
    "nextWatch": next_watch,
    "papers": papers[:4],
  }


def build_market_decision_overview(snapshot: dict, region_payload: dict) -> dict:
  market_session = snapshot.get("marketSession") or {}
  mode = "intraday" if market_session.get("isOpen") else "preopen"
  bonds = region_payload.get("bonds") or {}
  analysis = region_payload.get("analysis") or {}
  inflation = region_payload.get("inflation") or {}
  forecast = snapshot.get("forecast") or {}
  factors_raw = forecast.get("factorsRaw") or {}
  projects = company_projects_for_symbol(snapshot.get("symbol", ""))
  project_pressure, high_impact_count, supplier_count = compute_project_dependency_pressure(snapshot.get("symbol", ""))
  volume_ratio = 1.0
  raw_volume = float(snapshot.get("volume") or 0.0)
  avg_volume = 0.0
  for stat in snapshot.get("stats") or []:
    if stat.get("label") == "Avg volume":
      avg_volume = parse_compact_number(stat.get("value"))
  if avg_volume:
    volume_ratio = raw_volume / avg_volume
  inputs = []
  for item in sorted(load_market_decision_inputs(), key=lambda entry: entry.get("displayOrder", 99)):
    if item.get("mode") != mode:
      continue
    key = item.get("key")
    value_display = "Monitoring"
    note = ""
    if key == "overnight_rates_gap":
      curve = bonds.get("tenors") or []
      ten_year = curve[2] if len(curve) > 2 else {"change1D": 0}
      value_display = f"{float(ten_year.get('change1D') or 0):+.1f} bp"
      note = f"{bonds.get('label', 'Bond market')} overnight repricing"
    elif key == "macro_event_stack":
      value_display = f"{snapshot.get('eventFocus', {}).get('label', 'Mixed')} focus"
      note = f"{analysis.get('driver', 'event risk').replace('_', ' ')} is currently dominant"
    elif key == "global_leadership":
      value_display = region_payload.get("equity", {}).get("styleBias", "Mixed")
      note = f"{region_payload.get('equity', {}).get('summary', '')}"
    elif key == "duration_pressure_live":
      real_yield = float(bonds.get("realYield") or 0.0)
      duration_flag = bond_equity_duration_flag(snapshot.get("symbol"))
      value_display = f"{max(real_yield - 1.5, 0) * duration_flag:.2f}"
      note = f"Real yield {real_yield:.2f}% • duration flag {duration_flag:.2f}"
    elif key == "trend_participation_live":
      fast_momentum = float(factors_raw.get("fastMomentum") or 0.0)
      slow_momentum = float(factors_raw.get("slowMomentum") or 0.0)
      signal = (0.45 * fast_momentum) + (0.35 * slow_momentum) + (0.20 * centered_volume_participation(volume_ratio))
      value_display = f"{signal:+.2f}"
      note = f"MOM5 {fast_momentum:+.3f} • MOM20 {slow_momentum:+.3f} • VR {volume_ratio:.2f}x"
    elif key == "supplier_project_pressure":
      value_display = f"{project_pressure:.2f}"
      note = f"{len(projects)} projects • {high_impact_count}/{supplier_count or 1} high-impact suppliers"
    elif key == "event_override_live":
      value_display = f"{float(forecast.get('eventPressure') or 0.0):.2f}"
      note = f"{snapshot.get('eventFocus', {}).get('label', 'Mixed')} • {snapshot.get('sentiment', {}).get('label', 'Mixed')}"
    inputs.append(
      {
        "label": item.get("label", "Input"),
        "mode": mode,
        "cadence": item.get("cadence", ""),
        "significance": item.get("significance", ""),
        "formula": item.get("formula", ""),
        "why": item.get("why", ""),
        "sourceLabel": item.get("sourceLabel", ""),
        "value": value_display,
        "note": note,
      }
    )
  return {
    "mode": "During market" if mode == "intraday" else "Before market open",
    "inputs": inputs,
  }


def build_methodology_payload(snapshot: dict, region_payload: dict) -> dict:
  concepts = load_quant_concepts()
  flow = load_methodology_flow()
  decision_inputs = build_market_decision_overview(snapshot, region_payload)
  research_overview = build_active_research_overview(snapshot, region_payload)
  research_protocol = region_payload.get("researchProtocol") or {}
  graph = (region_payload.get("watchlistImplications") or {}).get("graph") or {}
  forecast = snapshot.get("forecast") or {}
  moving_average = forecast.get("movingAverageSignal") or {}
  decision_cockpit = snapshot.get("decisionCockpit") or {}
  live_input_cards = []
  for item in decision_inputs.get("inputs", [])[:6]:
    live_input_cards.append(
      {
        "label": item.get("label", "Input"),
        "value": item.get("value", "Monitoring"),
        "cadence": item.get("cadence", ""),
        "significance": item.get("significance", ""),
        "useWhere": item.get("sourceLabel", ""),
        "impactPath": item.get("note", ""),
      }
    )
  concept_cards = []
  for concept in concepts:
    live_match = next((item for item in live_input_cards if item["label"].lower().startswith(concept.get("label", "").split(" ")[0].lower())), None)
    concept_cards.append(
      {
        "label": concept.get("label", "Concept"),
        "family": concept.get("family", ""),
        "phase": concept.get("phase", ""),
        "formula": concept.get("formula", ""),
        "useWhere": concept.get("useWhere", ""),
        "impactPath": concept.get("impactPath", ""),
        "cadence": concept.get("cadence", ""),
        "whyItMatters": concept.get("whyItMatters", ""),
        "sourceTitle": concept.get("sourceTitle", ""),
        "url": concept.get("url", ""),
        "liveValue": live_match.get("value") if live_match else "",
      }
    )
  flow_nodes = []
  flow_edges = []
  flow_positions = {
    "inputs": (110, 90),
    "factors": (330, 90),
    "regime": (550, 90),
    "implications": (770, 90),
    "actions": (550, 260),
  }
  for item in flow:
    x, y = flow_positions.get(item.get("id"), (100, 100))
    flow_nodes.append(
      {
        "id": item.get("id", slugify_note_name(item.get("label", "node"))),
        "label": item.get("label", "Stage"),
        "summary": item.get("summary", ""),
        "x": x,
        "y": y,
      }
    )
  flow_edges.extend(
    [
      {"source": "inputs", "target": "factors", "label": "clean + score"},
      {"source": "factors", "target": "regime", "label": "classify"},
      {"source": "regime", "target": "implications", "label": "map impact"},
      {"source": "implications", "target": "actions", "label": "frame scenario"},
      {"source": "regime", "target": "actions", "label": "monitor"},
    ]
  )
  return {
    "headline": "A fact-first pipeline: macro anchor -> market factors -> event override -> stock scenarios.",
    "principles": [
      "Facts are separated from interpretation.",
      "Bonds explain the macro backdrop before equities are judged.",
      "Fresh events can override slower factors.",
      "Company links trace second-order impact.",
    ],
    "cockpit": {
      "stance": decision_cockpit.get("stance") or "Scenario engine active",
      "edgeScore": decision_cockpit.get("edgeScore", 0),
      "riskLevel": decision_cockpit.get("riskLevel", "Monitoring"),
      "activeSignal": moving_average.get("state") or forecast.get("direction") or "Signal pending",
      "summary": "The methodology is intentionally not a black box: every score is tied back to live inputs, classic quant signals, macro context, events, and graph dependencies.",
      "rules": [
        {"label": "1. Anchor", "value": region_payload.get("analysis", {}).get("driver", "macro"), "note": "Start with bonds, inflation, and policy."},
        {"label": "2. Confirm", "value": moving_average.get("state") or "trend pending", "note": "Check trend, volume, and model agreement."},
        {"label": "3. Override", "value": snapshot.get("eventFocus", {}).get("label", "event scan"), "note": "Fresh catalysts can outrank slow factors."},
        {"label": "4. Monitor", "value": decision_cockpit.get("riskLevel", "risk"), "note": "Show unknowns and watch-next items."},
      ],
    },
    "signalLayers": [
      {
        "layer": "Layer 1",
        "signal": "Trend participation",
        "explanation": "A move is treated as more reliable when short momentum, slower momentum, and participation move together instead of relying on price alone.",
        "guardrail": "Educational pattern only; private thresholds stay in local ignored research notes.",
      },
      {
        "layer": "Layer 2",
        "signal": "Macro pressure",
        "explanation": "Bond yields, curve slope, inflation impulse, and policy expectations are read before equity signals so duration and bank sensitivity are not confused with stock-specific strength.",
        "guardrail": "Scenario context, not buy/sell advice.",
      },
      {
        "layer": "Layer 3",
        "signal": "Event override",
        "explanation": "Fresh company, sector, policy, or geopolitical events can override slower technical factors when significance and recency are high.",
        "guardrail": "Sources and timestamps must remain visible.",
      },
      {
        "layer": "Layer 4",
        "signal": "Graph transmission",
        "explanation": "Supplier, customer, sector, and project links help explain second-order impact instead of treating every ticker as isolated.",
        "guardrail": "Unknown links are labeled instead of inferred as facts.",
      },
    ],
    "explainers": [
      {
        "label": "Participation",
        "title": "Momentum with volume confirmation",
        "formula": "TP = 0.45 * MOM_5 + 0.35 * MOM_20 + 0.20 * ln(volume / avg_volume)",
        "interpretation": "Positive values suggest trend and participation are aligned; low or negative values warn that price movement may lack breadth.",
      },
      {
        "label": "Macro",
        "title": "Duration pressure",
        "formula": "DP = max(real_yield - neutral_real_yield, 0) * duration_flag * model_confidence",
        "interpretation": "Higher values indicate rate-sensitive shares may need a stronger earnings or event offset before a bullish scenario deserves confidence.",
      },
      {
        "label": "Event",
        "title": "Catalyst override",
        "formula": "EO = significance * freshness_decay * source_weight * sentiment_direction",
        "interpretation": "Recent, material, well-sourced catalysts are allowed to change the scenario faster than slow historical factors.",
      },
      {
        "label": "Risk",
        "title": "Signal agreement",
        "formula": "Agreement = 100 - dispersion(classic_model, modern_overlay, macro_event_read)",
        "interpretation": "The dashboard increases confidence when independent views agree and lowers it when models conflict.",
      },
    ],
    "safetyNote": {
      "title": "Private signal protection",
      "body": "This section teaches public research concepts and dashboard logic. Proprietary thresholds, expert secrets, and monetizable playbooks belong only in ignored local paths such as vault/market-map/private/ and are excluded from GitHub.",
    },
    "concepts": concept_cards,
    "flow": {
      "nodes": flow_nodes,
      "edges": flow_edges,
    },
    "liveInputs": live_input_cards,
    "protocol": {
      "summary": research_protocol.get("summary", ""),
      "factors": research_protocol.get("factors", [])[:5],
      "practices": research_protocol.get("practices", [])[:4],
    },
    "researchCards": research_overview.get("cards", [])[:4],
    "tradingPapers": load_trading_papers(),
    "graphCoverage": {
      "nodes": len(graph.get("nodes") or []),
      "links": len(graph.get("links") or []),
      "coverage": ((graph.get("projectMeta") or {}).get("coverage") or 0),
    },
    "vault": {
      "conceptsPath": "vault/market-map/concepts",
      "workflowPath": "vault/market-map/workflows",
      "mode": "Local markdown",
    },
  }


def build_region_analysis(region_key: str, bonds: dict, inflation: dict, policy: dict, events: dict, equity: dict) -> dict:
  notes = kb_notes_bundle(region_key)
  slope = float((bonds.get("curve") or {}).get("slope2s10s") or 0)
  headline = float(inflation.get("headline") or 0)
  real_yield = float(bonds.get("realYield") or 0)
  driver = "policy expectations"
  if headline > 4.0 and real_yield > 1.5:
    driver = "inflation expectations"
  elif slope < 0:
    driver = "growth concerns"
  elif events.get("items"):
    top_titles = " ".join(item.get("title", "").lower() for item in events["items"][:3])
    if any(word in top_titles for word in {"war", "attack", "tariff", "sanction"}):
      driver = "event risk"
  implications = [
    f"{equity['styleBias']} lead the equity read-through.",
    f"{policy['centralBank']} stance is {policy['stance'].lower()} with {policy['bias'].lower()}.",
    f"Curve is {((bonds.get('curve') or {}).get('shape') or 'mixed').lower()}, which matters most for banks and duration-heavy sectors.",
  ]
  monitor = [
    f"Next {policy['centralBank']} communication and rates pricing.",
    f"{region_config(region_key)['inflationLabel']} releases and breakeven direction.",
    "Whether the bond move spills into index leadership or stays sector-specific.",
  ]
  return {
    "whatChanged": f"{bonds['label']} is seeing {((bonds.get('curve') or {}).get('direction') or 'mixed moves').lower()} with {((bonds.get('curve') or {}).get('shape') or 'mixed').lower()} curve signals.",
    "whyChanged": f"The dominant read is {driver}, reinforced by {inflation['impulse'].lower()} and {policy['centralBank']} expectations.",
    "marketImplication": " ".join(implications),
    "monitorNext": monitor,
    "driver": driver,
    "confidence": "Medium" if events.get("items") else "Low to medium",
    "unknowns": [
      "How much of the move is data-driven versus position unwinds.",
      "Whether event headlines evolve into policy action or fade quickly.",
    ],
    "kbNotes": [note for note in [notes["bond"], notes["inflation"], notes["playbook"], notes["regionCentralBank"]] if note][:3],
  }


def build_watchlist_implications(region_key: str, watchlist: list[dict], bonds: dict, inflation: dict) -> dict:
  notes = kb_notes_bundle(region_key)
  relevant = [
    item for item in watchlist
    if infer_region_key(item.get("symbol"), item.get("exchange"), item.get("currency")) == region_key
  ][:6]
  slope = float((bonds.get("curve") or {}).get("slope2s10s") or 0)
  real_yield = float(bonds.get("realYield") or 0)
  cards = []
  graph_nodes = [
    {
      "id": "bonds",
      "label": "Bond yields",
      "group": "macro",
      "summary": f"{bonds.get('label', 'Bond market')} is the anchor for the region-level read.",
      "detail": f"Curve shape {((bonds.get('curve') or {}).get('shape') or 'mixed')} • real yield {float(bonds.get('realYield') or 0):.2f}%",
    }
  ]
  graph_links = []
  graph_nodes.append({"id": "inflation", "label": "Inflation", "group": "macro", "summary": f"Headline {float(inflation.get('headline') or 0):.2f}% • core {float(inflation.get('core') or 0):.2f}%"})
  graph_nodes.append({"id": "policy", "label": "Policy", "group": "macro", "summary": f"{notes['regionCentralBank'] or 'Central-bank context'}"})
  graph_nodes.append({"id": "equities", "label": "Equities", "group": "market", "summary": "Sector and style leadership receives the macro shock after bonds and inflation."})
  for item in relevant:
    meta = fallback_meta(item["symbol"])
    label = meta.get("name", item["symbol"])
    symbol_upper = item["symbol"].upper()
    is_bank = "BANK" in label.upper() or "BANK" in symbol_upper or symbol_upper.startswith("SBIN")
    is_duration = any(token in symbol_upper for token in {"AAPL", "MSFT", "NVDA", "TCS", "INFY"})
    direction_score = (-1 if real_yield > 1.8 and is_duration else 1 if slope > 0 and is_bank else 0)
    projects = company_projects_for_symbol(item["symbol"])
    supplier_count = sum(len(project.get("suppliers") or []) for project in projects)
    top_projects = []
    for project in projects[:3]:
      suppliers = project.get("suppliers") or []
      top_projects.append(
        {
          "title": project.get("title", "Project"),
          "theme": project.get("theme", ""),
          "worthLabel": project.get("worthLabel", "Undisclosed"),
          "status": project.get("status", ""),
          "summary": project.get("summary", ""),
          "asOf": project.get("asOf", ""),
          "sourceLabel": project.get("sourceLabel", ""),
          "sourceUrl": project.get("sourceUrl", ""),
          "suppliers": [
            {
              "label": supplier.get("label", "Supplier"),
              "role": supplier.get("role", ""),
              "impact": supplier.get("impact", "Medium"),
            }
            for supplier in suppliers[:4]
          ],
        }
      )
    cards.append(
      {
        "symbol": item["symbol"],
        "name": item.get("name") or item["symbol"],
        "scenario": "Rates-sensitive" if direction_score < 0 else "Curve beneficiary" if direction_score > 0 else "Wait for clearer macro confirmation",
        "impact": "Negative duration pressure" if direction_score < 0 else "Positive earnings sensitivity" if direction_score > 0 else "Mixed macro transmission",
        "confidence": "Medium",
        "why": company_note_for_symbol(item["symbol"]) or notes["company"] or notes["sector"],
        "marketMapNote": load_market_map_note(item["symbol"]),
        "projectCount": len(projects),
        "supplierCount": supplier_count,
        "projects": top_projects,
      }
    )
    graph_nodes.append(
      {
        "id": item["symbol"],
        "label": item["symbol"],
        "group": "stock",
        "entityType": "company",
        "subtitle": label,
        "summary": cards[-1]["scenario"],
        "detail": cards[-1]["why"],
        "confidence": cards[-1]["confidence"],
      }
    )
    graph_links.append(
      {
        "source": "bonds",
        "target": item["symbol"],
        "value": abs(direction_score) + 1,
        "direction": "negative" if direction_score < 0 else "positive" if direction_score > 0 else "neutral",
      }
    )
    for project in projects[:4]:
      suppliers = project.get("suppliers") or []
      project_id = f"{item['symbol']}::{project.get('id') or slugify_note_name(project.get('title', 'project'))}"
      worth_label = project.get("worthLabel") or "Undisclosed"
      graph_nodes.append(
        {
          "id": project_id,
          "label": project.get("title", "Project"),
          "group": "project",
          "entityType": project.get("theme", "project"),
          "subtitle": worth_label,
          "summary": project.get("summary", ""),
          "detail": f"{project.get('status', '')} • {project.get('theme', '')}".strip(" •"),
          "status": project.get("status", ""),
          "sourceUrl": project.get("sourceUrl", ""),
          "sourceLabel": project.get("sourceLabel", ""),
          "worthLabel": worth_label,
          "worthValue": project.get("worthValue"),
          "asOf": project.get("asOf", ""),
        }
      )
      graph_links.append(
        {
          "source": item["symbol"],
          "target": project_id,
          "value": clamp(1.4 + (len(suppliers) * 0.22), 1.4, 3.8),
          "direction": "positive" if direction_score >= 0 else "negative",
          "relation": "project",
          "worthLabel": worth_label,
        }
      )
      for supplier in suppliers[:5]:
        supplier_id = supplier.get("id") or f"{project_id}::{slugify_note_name(supplier.get('label', 'entity'))}"
        impact = (supplier.get("impact") or "Medium").capitalize()
        graph_nodes.append(
          {
            "id": supplier_id,
            "label": supplier.get("label", "Supplier"),
            "group": "entity",
            "entityType": supplier.get("type", "entity"),
            "subtitle": supplier.get("role", ""),
            "impact": impact,
            "summary": f"{supplier.get('type', 'entity').replace('-', ' ')} dependency",
            "detail": supplier.get("role", ""),
          }
        )
        graph_links.append(
          {
            "source": project_id,
            "target": supplier_id,
            "value": 3.6 if impact == "High" else 2.8 if impact == "Medium" else 2.1,
            "direction": "neutral",
            "relation": supplier.get("role") or supplier.get("type") or "supplier",
            "impact": impact,
          }
        )
    company_network = company_network_for_symbol(item["symbol"])
    for entity in company_network.get("entities", [])[:5]:
      graph_nodes.append(
        {
          "id": entity.get("id"),
          "label": entity.get("label", entity.get("id", "Entity")),
          "group": "entity",
          "entityType": entity.get("type", "entity"),
          "subtitle": entity.get("role", "") or entity.get("theme", ""),
          "summary": entity.get("theme", "") or entity.get("type", "entity"),
        }
      )
    for link in company_network.get("links", [])[:6]:
      graph_links.append(
        {
          "source": link.get("source"),
          "target": link.get("target"),
          "value": float(link.get("value") or 1.0),
          "direction": link.get("direction") or "neutral",
          "relation": link.get("relation") or "entity",
        }
      )
  graph_links.extend(
    [
      {"source": "inflation", "target": "bonds", "value": 3, "direction": "negative" if inflation.get("headline", 0) > 4 else "neutral"},
      {"source": "policy", "target": "bonds", "value": 2, "direction": "neutral"},
      {"source": "bonds", "target": "equities", "value": 3, "direction": "negative" if real_yield > 1.8 else "positive"},
    ]
  )
  relation_links, relation_meta = relation_links_for_watchlist(region_key, relevant)
  graph_links.extend(relation_links)
  factor_schedule = load_factor_schedule()[:5]
  paper_set = load_trading_papers()[:4]
  return {
    "cards": cards,
    "graph": {
      "nodes": dedupe_graph_nodes(graph_nodes),
      "links": graph_links,
      "relationMeta": relation_meta,
      "projectMeta": {
        "source": "Curated company project map",
        "coverage": sum(1 for item in relevant if company_projects_for_symbol(item["symbol"])),
      },
      "factorSchedule": factor_schedule,
      "papers": paper_set,
      "vault": {
        "path": "vault/market-map",
        "mode": "Local markdown",
      },
      "graphMeta": {
        "layout": "Hierarchical dependency graph",
        "maxNodes": len(dedupe_graph_nodes(graph_nodes)),
        "maxLinks": len(graph_links),
      },
    },
  }


def build_region_payload(region_key: str, watchlist: list[dict], active_snapshot: dict | None = None) -> dict:
  config = region_config(region_key)
  notes = kb_notes_bundle(config["key"])
  bonds = build_region_bond_snapshot(config["key"])
  inflation = build_region_inflation_snapshot(config["key"], bonds)
  policy = build_region_policy_snapshot(config["key"], bonds, inflation)
  with ThreadPoolExecutor(max_workers=2) as executor:
    events_future = executor.submit(build_region_event_context, config["key"])
    equity_future = executor.submit(build_region_equity_context, config["key"], active_snapshot or {}, bonds, inflation)
    events = events_future.result()
    equity = equity_future.result()
  calendar = build_region_calendar(config["key"])
  analysis = build_region_analysis(config["key"], bonds, inflation, policy, events, equity)
  research_protocol = build_region_research_protocol(config["key"], bonds, inflation)
  watchlist_implications = build_watchlist_implications(config["key"], watchlist, bonds, inflation)
  return {
    "region": config["key"],
    "label": config["label"],
    "currency": config["currency"],
    "bonds": bonds,
    "inflation": inflation,
    "policy": policy,
    "events": events,
    "calendar": calendar,
    "equity": equity,
    "analysis": analysis,
    "researchProtocol": research_protocol,
    "watchlistImplications": watchlist_implications,
    "notes": notes,
  }


def build_region_comparison(regions: dict[str, dict]) -> dict:
  us = regions.get("us") or build_region_payload("us", [])
  india = regions.get("india") or build_region_payload("india", [])
  return {
    "rows": [
      {
        "metric": "10Y yield",
        "us": f"{us['bonds']['tenors'][2]['yield']:.2f}%",
        "india": f"{india['bonds']['tenors'][2]['yield']:.2f}%",
      },
      {
        "metric": "2s10s slope",
        "us": f"{us['bonds']['curve']['slope2s10s']:.2f}%",
        "india": f"{india['bonds']['curve']['slope2s10s']:.2f}%",
      },
      {
        "metric": "Headline inflation",
        "us": f"{us['inflation']['headline']:.2f}%",
        "india": f"{india['inflation']['headline']:.2f}%",
      },
      {
        "metric": "Policy rate",
        "us": f"{us['policy']['policyRate']:.2f}%",
        "india": f"{india['policy']['policyRate']:.2f}%",
      },
    ],
    "summary": f"US is currently led by {us['analysis']['driver']}, while India is led by {india['analysis']['driver']}.",
  }


def build_global_market_overview() -> list[dict]:
  return memory_cached_value("global-market-overview", 20, build_global_market_overview_uncached) or []


def build_global_market_overview_uncached() -> list[dict]:
  symbols = [item["symbol"] for market in GLOBAL_MARKET_CLOCKS for item in market["indices"]]
  quotes = fetch_live_quotes(symbols, fast=True)
  cards = []
  for market in GLOBAL_MARKET_CLOCKS:
    indices = []
    # Country benchmark clocks are exchange-schedule driven. Quote providers can
    # report CLOSED for delayed index prints during an active local session.
    session_state = "REGULAR"
    for benchmark in market["indices"]:
      symbol = benchmark["symbol"]
      quote = quotes.get(symbol, {})
      fallback = fallback_meta(symbol)
      price = quote.get("regularMarketPrice")
      previous_close = quote.get("regularMarketPreviousClose")
      change_percent = float(
        quote.get("regularMarketChangePercent")
        or (pct_change(float(price), float(previous_close)) if price is not None and previous_close not in (None, 0) else 0.0)
      )
      exchange = quote.get("fullExchangeName") or quote.get("exchange") or fallback.get("exchange") or market["label"]
      data_source = quote.get("quoteSource") or ("Live source" if quote else "curated_fallback")
      as_of = quote_effective_as_of(quote, data_source) or ""
      session_preview = build_market_session(
        market.get("sessionExchange") or exchange,
        market["label"],
        session_state,
        as_of,
      )
      indices.append(
        {
          "symbol": symbol,
          "label": benchmark["label"],
          "price": float(price if price is not None else fallback.get("basePrice") or 0.0),
          "changePercent": change_percent,
          "currency": quote.get("currency") or fallback.get("currency") or "USD",
          "exchange": exchange,
          "marketState": session_state,
          "asOf": as_of,
          "dataSource": data_source,
          "dataProviderId": quote.get("quoteProviderId"),
          "dataSourceRank": quote.get("quoteSourceRank"),
          "dataSourceCount": quote.get("quoteSourceCount"),
          "quoteFreshness": quote_freshness(as_of, session_preview, data_source),
        }
      )
    session = build_market_session(
      market.get("sessionExchange") or (indices[0].get("exchange") if indices else market["label"]),
      market["label"],
      session_state,
      indices[0].get("asOf") if indices else "",
    )
    cards.append(
      {
        "key": market["key"],
        "label": market["label"],
        "timezone": market["timezone"],
        "session": session,
        "indices": indices,
      }
    )
  return cards


def build_dashboard(symbols: list[str], active: str | None, chart_range: str = "1M", region_key: str | None = None) -> dict:
  cleaned = [symbol.upper() for symbol in symbols if symbol]
  if not cleaned:
    cleaned = DEFAULT_WATCHLIST.copy()
  if active and active.upper() not in cleaned:
    cleaned.insert(0, active.upper())
  cleaned = list(dict.fromkeys(cleaned))

  quote_map = fetch_live_quotes(cleaned, fast=True)
  watchlist = []
  for symbol in cleaned:
    quote = quote_map.get(symbol, {})
    fallback = fallback_meta(symbol)
    history = None
    history_meta = {}
    price = quote.get("regularMarketPrice")
    previous_close = quote.get("regularMarketPreviousClose")
    data_source = quote.get("quoteSource") or ("Live source" if quote else "Fallback data")
    if price is None or previous_close is None:
      history, history_meta = build_history(symbol, chart_range, allow_live_refresh=False)
      if len(history) >= 2:
        price = history[-1]
        previous_close = history[-2]
        data_source = "History-derived"
      else:
        price = None
        previous_close = None
    history_as_of = (history_meta.get("timestamps") or [None])[-1] if history_meta.get("timestamps") else None
    as_of = history_as_of if source_label_is_history(data_source) else quote_effective_as_of(quote, data_source, history_as_of)
    session_state = quote_session_state(quote, data_source)
    market_session = build_market_session(
      quote.get("fullExchangeName") or quote.get("exchange") or fallback["exchange"],
      quote.get("exchange") or fallback["exchange"],
      session_state,
      as_of,
    )
    watchlist.append(
      {
        "symbol": symbol,
        "name": quote.get("shortName") or quote.get("longName") or fallback["name"],
        "price": float(price) if price is not None else None,
        "changePercent": float(quote.get("regularMarketChangePercent") or pct_change(float(price), float(previous_close)) if price is not None and previous_close is not None else 0.0),
        "volume": int(quote.get("regularMarketVolume") or quote.get("averageDailyVolume3Month") or 0),
        "currency": quote.get("currency") or fallback["currency"],
        "exchange": quote.get("fullExchangeName") or quote.get("exchange") or fallback["exchange"],
        "marketState": session_state,
        "marketSession": market_session,
        "dataSource": data_source,
        "dataProviderId": quote.get("quoteProviderId"),
        "dataSourceRank": quote.get("quoteSourceRank"),
        "dataSourceCount": quote.get("quoteSourceCount"),
        "dataSourceType": quote.get("quoteSourceType"),
        "dataSourceCheckedAt": quote.get("quoteSourceCheckedAt"),
        "asOf": as_of,
        "quoteFreshness": quote_freshness(
          as_of,
          market_session,
          data_source,
        ),
      }
    )

  active_symbol = (active or cleaned[0]).upper()
  if active_symbol not in cleaned:
    active_symbol = cleaned[0]
  with ThreadPoolExecutor(max_workers=3) as executor:
    active_future = executor.submit(build_ticker_snapshot, active_symbol, quote_map.get(active_symbol), "base", 10, chart_range)
    macro_future = executor.submit(build_macro_pulse)
    radar_future = executor.submit(build_market_radar, active_symbol)
    global_markets_future = executor.submit(build_global_market_overview)
    active_snapshot = active_future.result()
    macro_pulse = macro_future.result()
    radar = enrich_market_radar(radar_future.result(), macro_pulse, active_snapshot)
    global_markets = global_markets_future.result()

  banner = radar["headlines"] or active_snapshot["headlines"][:4]
  selected_region = region_config(region_key or infer_region_key(active_snapshot.get("symbol"), active_snapshot.get("exchange"), active_snapshot.get("currency")))
  with ThreadPoolExecutor(max_workers=2) as executor:
    us_future = executor.submit(build_region_payload, "us", watchlist, active_snapshot)
    india_future = executor.submit(build_region_payload, "india", watchlist, active_snapshot)
    regions = {
      "us": us_future.result(),
      "india": india_future.result(),
    }
  active_region_key = selected_region["key"]
  active_snapshot["researchOverview"] = build_active_research_overview(active_snapshot, regions[active_region_key])
  active_snapshot["decisionInputs"] = build_market_decision_overview(active_snapshot, regions[active_region_key])
  active_snapshot["decisionCockpit"] = build_decision_cockpit(active_snapshot, regions[active_region_key], radar)
  active_snapshot["featureCards"] = build_operator_feature_cards(active_snapshot, regions[active_region_key], radar)
  methodology = build_methodology_payload(active_snapshot, regions[active_region_key])
  warmup = start_history_warmup(cleaned, HISTORY_PREFETCH_RANGES, reason="dashboard-loaded")
  backend_refresh = start_dashboard_backend_refresh(cleaned, selected_region["key"])

  return {
    "provider": load_config().get("provider", "yahoo"),
    "updatedAt": datetime.now(timezone.utc).isoformat(),
    "selectedRegion": selected_region["key"],
    "regionOptions": [{"key": item["key"], "label": item["label"]} for item in REGION_CONFIGS.values()],
    "watchlist": watchlist,
    "active": active_snapshot,
    "macroPulse": macro_pulse,
    "globalMarkets": global_markets,
    "radar": radar,
    "headlines": list(dict.fromkeys(banner))[:6],
    "discovery": build_market_discovery(watchlist),
    "regions": regions,
    "comparison": build_region_comparison(regions),
    "methodology": methodology,
    "historyWarmup": warmup,
    "backendRefresh": backend_refresh,
    "trustedDataSources": TRUSTED_DATA_SOURCE_REGISTRY,
  }


def build_radar_payload(symbol: str | None = None) -> dict:
  with ThreadPoolExecutor(max_workers=3) as executor:
    radar_future = executor.submit(build_market_radar, symbol)
    macro_future = executor.submit(build_macro_pulse)
    snapshot_future = executor.submit(build_ticker_snapshot, symbol) if symbol else None
    radar = radar_future.result()
    macro_pulse = macro_future.result()
    active_snapshot = snapshot_future.result() if snapshot_future else None
  radar = enrich_market_radar(radar, macro_pulse, active_snapshot)
  return {
    "updatedAt": datetime.now(timezone.utc).isoformat(),
    "symbol": symbol or "",
    "radar": radar,
    "headlines": list(dict.fromkeys(radar.get("headlines") or []))[:6],
  }


QUOTES_PAYLOAD_CACHE_TTL = 3  # seconds — dedupes concurrent /api/quotes clients hitting the same shape


def build_quote_snapshot(symbols: list[str], active: str | None) -> dict:
  """Lean quote-only payload for the /api/quotes short-poll path.

  Returns the same {updatedAt, watchlist, active} shape as build_live_quotes so
  the client can reuse applyLiveQuoteUpdate, but skips history fallback, KB
  notes, region inference, and regime text. Server-side micro-cached for
  QUOTES_PAYLOAD_CACHE_TTL seconds keyed by (symbols, active)."""
  cleaned = [symbol.upper() for symbol in symbols if symbol]
  if not cleaned:
    cleaned = DEFAULT_WATCHLIST.copy()
  cache_key = "quotes:" + ",".join(cleaned) + "|" + (active or "").upper()

  def builder() -> dict:
    updated_at = datetime.now(timezone.utc).isoformat()
    quote_map = fetch_live_quotes(cleaned, fast=True)
    items: list[dict] = []
    active_item = None
    for symbol in cleaned:
      quote = quote_map.get(symbol, {})
      price = quote.get("regularMarketPrice")
      previous_close = quote.get("regularMarketPreviousClose")
      if price is None or previous_close is None:
        continue
      fallback = fallback_meta(symbol)
      data_source = quote.get("quoteSource") or "Live source"
      as_of = quote_effective_as_of(quote, data_source)
      item = {
        "symbol": symbol,
        "name": quote.get("shortName") or quote.get("longName") or fallback["name"],
        "price": float(price),
        "previousClose": float(previous_close),
        "changePercent": float(
          quote.get("regularMarketChangePercent")
          or pct_change(float(price), float(previous_close))
        ),
        "volume": int(quote.get("regularMarketVolume") or 0),
        "currency": quote.get("currency") or fallback["currency"],
        "exchange": quote.get("fullExchangeName") or quote.get("exchange") or fallback["exchange"],
        "marketState": quote_session_state(quote, data_source),
        "dataSource": data_source,
        "asOf": as_of,
        "receivedAt": updated_at,
      }
      items.append(item)
      if symbol == (active or cleaned[0]).upper():
        active_item = item
    return {
      "updatedAt": updated_at,
      "watchlist": items,
      "active": active_item or (items[0] if items else None),
      "mode": "quotes",
    }

  return memory_cached_value(cache_key, QUOTES_PAYLOAD_CACHE_TTL, builder)


def build_live_quotes(symbols: list[str], active: str | None, allow_history_fallback: bool = True) -> dict:
  cleaned = [symbol.upper() for symbol in symbols if symbol]
  if not cleaned:
    cleaned = DEFAULT_WATCHLIST.copy()
  updated_at = datetime.now(timezone.utc).isoformat()
  quote_map = fetch_live_quotes(cleaned, fast=True)
  items = []
  active_item = None

  for symbol in cleaned:
    quote = quote_map.get(symbol, {})
    fallback = fallback_meta(symbol)
    history = None
    history_meta = {}
    price = quote.get("regularMarketPrice")
    previous_close = quote.get("regularMarketPreviousClose")
    data_source = quote.get("quoteSource") or ("Live source" if quote else "Fallback data")
    if (price is None or previous_close is None) and allow_history_fallback:
      history, history_meta = build_history(symbol, allow_live_refresh=False)
      if len(history) >= 2:
        price = history[-1]
        previous_close = history[-2]
        data_source = "History-derived"
      else:
        price = None
        previous_close = None
    if (price is None or previous_close is None) and not allow_history_fallback:
      continue
    history_as_of = (history_meta.get("timestamps") or [None])[-1] if history_meta.get("timestamps") else None
    as_of = history_as_of if source_label_is_history(data_source) else quote_effective_as_of(quote, data_source, history_as_of)
    session = build_market_session(
      quote.get("fullExchangeName") or quote.get("exchange") or fallback["exchange"],
      quote.get("exchange") or fallback["exchange"],
      quote_session_state(quote, data_source),
      as_of,
    )
    item = {
      "symbol": symbol,
      "name": quote.get("shortName") or quote.get("longName") or fallback["name"],
      "price": float(price) if price is not None else None,
      "previousClose": float(previous_close) if previous_close is not None else None,
      "changePercent": float(quote.get("regularMarketChangePercent") or pct_change(float(price), float(previous_close)) if price is not None and previous_close is not None else 0.0),
      "volume": int(quote.get("regularMarketVolume") or quote.get("averageDailyVolume3Month") or 0),
      "currency": quote.get("currency") or fallback["currency"],
      "exchange": quote.get("fullExchangeName") or quote.get("exchange") or fallback["exchange"],
      "marketState": quote_session_state(quote, data_source),
      "marketSession": session,
      "dataSource": data_source,
      "dataProviderId": quote.get("quoteProviderId"),
      "dataSourceRank": quote.get("quoteSourceRank"),
      "dataSourceCount": quote.get("quoteSourceCount"),
      "dataSourceType": quote.get("quoteSourceType"),
      "dataSourceCheckedAt": quote.get("quoteSourceCheckedAt"),
      "asOf": as_of,
      "receivedAt": updated_at,
      "quoteFreshness": quote_freshness(as_of, session, data_source),
    }
    items.append(item)
    if symbol == (active or cleaned[0]).upper():
      active_item = item

  return {
    "updatedAt": updated_at,
    "watchlist": items,
    "active": active_item or (items[0] if items else None),
    "mode": "stream" if not allow_history_fallback else "full",
  }


def sector_period_yahoo_config(period: str) -> tuple[str, str]:
  normalized = (period or "1D").upper()
  period_map = {"1D": "2d", "5D": "5d", "1W": "7d", "1M": "1mo", "3M": "3mo", "6M": "6mo", "1Y": "1y"}
  interval_map = {"1D": "5m", "5D": "30m", "1W": "1d", "1M": "1d", "3M": "1wk", "6M": "1wk", "1Y": "1mo"}
  return period_map.get(normalized, "2d"), interval_map.get(normalized, "1d")


def sector_benchmark_for_market(market: str, benchmark_symbol: str | None = None) -> dict:
  choices = SECTOR_BENCHMARKS.get(market, SECTOR_BENCHMARKS["india"])
  if benchmark_symbol:
    wanted = benchmark_symbol.upper()
    for item in choices:
      if item["symbol"].upper() == wanted:
        return item
  return choices[0]


def quote_meta_timestamps(quote: dict) -> list[str]:
  market_time = quote.get("regularMarketTime")
  try:
    as_of = datetime.fromtimestamp(float(market_time), tz=timezone.utc) if market_time else datetime.now(timezone.utc)
  except (TypeError, ValueError, OSError):
    as_of = datetime.now(timezone.utc)
  previous = as_of - timedelta(days=1)
  return [previous.isoformat(), as_of.isoformat()]


def sector_exchange_for_symbol(symbol: str) -> str:
  upper = (symbol or "").upper()
  aliases = " ".join(GOOGLE_FINANCE_INDEX_ALIASES.get(upper, [])).upper()
  if "INDEXNSE" in aliases or upper.endswith(".NS"):
    return "NSE"
  if "INDEXBOM" in aliases or upper.endswith(".BO"):
    return "BSE"
  exchange = fallback_meta(upper).get("exchange", "")
  return "NYSE" if exchange in {"US", "Index"} and upper in {"^GSPC", "^DJI", "^RUT", "SPY", "DIA", "IWM"} else exchange


def sector_period_cache_ttl(symbol: str, period: str) -> int:
  normalized_period = (period or "1D").upper()
  if normalized_period != "1D":
    return _SECTOR_CACHE_TTL
  exchange = sector_exchange_for_symbol(symbol)
  session = build_market_session(exchange, exchange, "REGULAR")
  return _SECTOR_LIVE_CACHE_TTL if session.get("isOpen") else _SECTOR_CACHE_TTL


def fetch_google_period_quote_change(symbol: str, interval: str) -> tuple[float, float, str] | None:
  quote = fetch_google_finance_quote(symbol, sector_exchange_for_symbol(symbol))
  price = quote.get("regularMarketPrice")
  change_pct = quote.get("regularMarketChangePercent")
  previous_close = quote.get("regularMarketPreviousClose")
  if not isinstance(price, (int, float)) or price <= 0 or not isinstance(change_pct, (int, float)):
    return None
  if not isinstance(previous_close, (int, float)) or previous_close <= 0:
    previous_close = price / (1 + (change_pct / 100)) if change_pct != -100 else price
  closes = [float(previous_close), float(price)]
  meta = {
    "timestamps": quote_meta_timestamps(quote),
    "quoteSource": quote.get("quoteSource", "Google Finance Quote"),
    "quoteSymbol": quote.get("googleSymbol") or quote.get("symbol") or symbol,
    "quoteChangePercent": round(float(change_pct), 4),
  }
  save_historical_records(symbol, interval, history_points_from_meta(closes, meta), "Google Finance Quote")
  save_history_cache(symbol, "1D", closes, meta, "Google Finance Quote")
  return round(float(change_pct), 2), round(float(price), 2), "Google Finance Quote"


def fetch_period_change(symbol: str, period: str) -> tuple[float, float, str]:
  normalized_period = (period or "1D").upper()
  range_value, interval = sector_period_yahoo_config(period)
  cache_ttl = sector_period_cache_ttl(symbol, normalized_period)
  needs_live_edge = normalized_period == "1D" and cache_ttl == _SECTOR_LIVE_CACHE_TTL
  cached = load_cached_history(symbol, normalized_period)
  if cached:
    closes, meta, source, updated_at = cached
    try:
      age_seconds = max(0.0, (datetime.now(timezone.utc) - datetime.fromisoformat(updated_at)).total_seconds())
    except ValueError:
      age_seconds = _SECTOR_CACHE_TTL + 1
    if len(closes) >= 2 and age_seconds <= cache_ttl:
      cached_quote_change = meta.get("quoteChangePercent")
      if source == "Google Finance Quote" and normalized_period == "1D":
        if isinstance(cached_quote_change, (int, float)):
          return round(float(cached_quote_change), 2), round(float(closes[-1]), 2), source
      else:
        return round(pct_change(float(closes[-1]), float(closes[0])), 2), round(float(closes[-1]), 2), source or "Local history cache"

  if needs_live_edge:
    google_result = fetch_google_period_quote_change(symbol, interval)
    if google_result:
      return google_result

  chart = fetch_yahoo_chart(symbol, range_value=range_value, interval=interval)
  closes, meta = extract_yahoo_history_payload(chart or {})
  if len(closes) >= 2:
    save_historical_records(symbol, interval, history_points_from_meta(closes, meta), "Yahoo Chart")
    save_history_cache(symbol, normalized_period, closes, meta, "Yahoo Chart")
    return round(pct_change(float(closes[-1]), float(closes[0])), 2), round(float(closes[-1]), 2), "Yahoo Chart"
  if normalized_period == "1D":
    google_result = fetch_google_period_quote_change(symbol, interval)
    if google_result:
      return google_result
  if cached:
    closes, _, source, _ = cached
    if len(closes) >= 2:
      return round(pct_change(float(closes[-1]), float(closes[0])), 2), round(float(closes[-1]), 2), f"Stale {source or 'local cache'}"
  return 0.0, 0.0, "Unavailable"


def build_sector_matrix(market: str, period: str = "1D", benchmark_symbol: str | None = None) -> dict:
  """Fetch sector index performance for the given market and period."""
  normalized_market = market if market in SECTOR_INDICES else "india"
  normalized_period = period if period in SECTOR_PERIOD_LABELS else "1D"
  benchmark = sector_benchmark_for_market(normalized_market, benchmark_symbol)
  cache_key = f"{normalized_market}:{normalized_period}:{benchmark['symbol']}"
  cache_ttl = sector_period_cache_ttl(benchmark["symbol"], normalized_period)
  live_mode = normalized_period == "1D" and cache_ttl == _SECTOR_LIVE_CACHE_TTL
  now = time.time()
  cached = _sector_cache.get(cache_key)
  if cached and (now - cached.get("ts", 0)) < cache_ttl:
    return {**cached["data"], "cacheState": "live memory" if live_mode else "memory"}

  sectors = SECTOR_INDICES.get(normalized_market, SECTOR_INDICES["india"])
  with ThreadPoolExecutor(max_workers=min(8, len(sectors) + 1)) as executor:
    benchmark_future = executor.submit(fetch_period_change, benchmark["symbol"], normalized_period)
    sector_futures = [(entry, executor.submit(fetch_period_change, entry["symbol"], normalized_period)) for entry in sectors]
    benchmark_change, benchmark_price, benchmark_source = benchmark_future.result()

    results = []
    for entry, future in sector_futures:
      change_pct, price, source = future.result()
      results.append({
        "label": entry["label"],
        "symbol": entry["symbol"],
        "sector": entry["sector"],
        "changePct": change_pct,
        "relativePct": round(change_pct - benchmark_change, 2),
        "price": price,
        "source": source,
      })

  data = {
    "market": normalized_market,
    "period": normalized_period,
    "periodLabel": SECTOR_PERIOD_LABELS[normalized_period],
    "benchmark": {
      **benchmark,
      "changePct": benchmark_change,
      "price": benchmark_price,
      "source": benchmark_source,
    },
    "sectors": results,
    "cacheState": "live refreshed" if live_mode else "refreshed",
    "liveMode": live_mode,
    "cacheTtlSeconds": cache_ttl,
    "marketSession": build_market_session(sector_exchange_for_symbol(benchmark["symbol"]), normalized_market, "REGULAR"),
    "source": benchmark_source,
    "updatedAt": datetime.now(timezone.utc).isoformat(),
  }
  _sector_cache[cache_key] = {"ts": now, "data": data}
  return data


def canonical_sector_key(value: str | None) -> str:
  label = re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).strip()
  if not label:
    return "other"
  if "tech" in label or "software" in label or "semiconductor" in label or label == "it":
    return "technology"
  if "health" in label or "pharma" in label or "biotech" in label:
    return "healthcare"
  if "bank" in label or "financ" in label or "insurance" in label:
    return "financials"
  if "telecom" in label or "communication" in label or "media" in label:
    return "communication services"
  if "consumer discretionary" in label or "auto" in label or "retail" in label or "durable" in label:
    return "consumer discretionary"
  if "consumer staples" in label or "fmcg" in label or "food" in label:
    return "consumer staples"
  if "industrial" in label or "capital goods" in label or "construction" in label or "defence" in label or "ports" in label:
    return "industrials"
  if "material" in label or "metal" in label or "cement" in label or "chemical" in label:
    return "materials"
  if "real" in label or "realty" in label or "reit" in label:
    return "real estate"
  if "util" in label or "power" in label:
    return "utilities"
  if "energy" in label or "oil" in label or "gas" in label or "petroleum" in label:
    return "energy"
  return label


def proxy_change_for_symbol(symbol: str, sector_change: float) -> float:
  seed = symbol_seed(symbol)
  micro_variation = ((seed % 91) - 45) / 100.0
  return round(clamp(float(sector_change or 0.0) + micro_variation, -9.99, 9.99), 2)


def market_map_tile_span(index: int, quote: dict | None = None) -> int:
  volume = float((quote or {}).get("regularMarketVolume") or 0)
  if volume >= 50_000_000:
    return 3
  if volume >= 8_000_000:
    return 2
  if index < 6:
    return 3
  if index < 18:
    return 2
  return 1


def market_map_size_bucket(member: dict, index: int) -> str:
  raw_rank = member.get("rank") or member.get("marketCapRank") or member.get("displayRank")
  try:
    rank = int(raw_rank)
  except (TypeError, ValueError):
    rank = index + 1
  if rank <= 100:
    return "mega"
  if rank <= 250:
    return "large"
  if rank <= 750:
    return "mid"
  return "small"


def market_map_sector_options(members: list[dict]) -> list[dict]:
  counts: dict[str, int] = {}
  labels: dict[str, str] = {}
  for member in members:
    sector = str(member.get("sector") or fallback_meta(str(member.get("symbol") or "")).get("sector") or "Other")
    key = canonical_sector_key(sector)
    counts[key] = counts.get(key, 0) + 1
    labels.setdefault(key, sector.title() if sector else "Other")
  return [
    {"key": key, "label": labels.get(key, key.title()), "count": count}
    for key, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
  ]


def normalize_market_map_scope(scope: str = "top250") -> str:
  normalized = (scope or "top250").lower()
  return normalized if normalized in MARKET_MAP_SCOPE_LIMITS else "top250"


def apply_market_map_scope(members: list[dict], scope: str = "top250") -> tuple[list[dict], str, int]:
  normalized_scope = normalize_market_map_scope(scope)
  limit = MARKET_MAP_SCOPE_LIMITS[normalized_scope]
  if limit <= 0:
    return members, normalized_scope, len(members)
  return members[:limit], normalized_scope, limit


def filter_market_map_members(members: list[dict], sector: str = "all", size: str = "all") -> list[dict]:
  sector_key = canonical_sector_key(sector) if sector and sector != "all" else "all"
  size_key = (size or "all").lower()
  filtered = []
  for index, member in enumerate(members):
    member_sector = canonical_sector_key(str(member.get("sector") or fallback_meta(str(member.get("symbol") or "")).get("sector") or "Other"))
    member_size = market_map_size_bucket(member, index)
    if sector_key != "all" and member_sector != sector_key:
      continue
    if size_key != "all" and member_size != size_key:
      continue
    filtered.append({**member, "_marketMapRank": index + 1, "_marketMapSize": member_size, "_marketMapSectorKey": member_sector})
  return filtered


def market_map_company_payload(member: dict, quote: dict, sector_changes: dict, sector_source: str, period: str, index: int) -> tuple[dict, bool]:
  symbol = str(member.get("symbol") or "").upper()
  fallback = fallback_meta(symbol)
  sector = member.get("sector") or fallback.get("sector") or "Other"
  sector_key = canonical_sector_key(str(sector))
  sector_change = sector_changes.get(sector_key, 0.0)
  live_1d = period == "1D" and quote_is_usable(quote) and quote.get("regularMarketChangePercent") is not None
  price = quote.get("regularMarketPrice")
  if price is None:
    price = fallback.get("basePrice")
  if live_1d:
    change_pct = round(float(quote.get("regularMarketChangePercent") or 0.0), 2)
    source = quote.get("quoteSource") or "Live quote"
    quality = "live"
  else:
    change_pct = proxy_change_for_symbol(symbol, sector_change)
    source = f"Sector index proxy ({sector_source or 'market data'})"
    quality = "sector-proxy"
  payload = {
    "symbol": symbol,
    "name": quote.get("shortName") or quote.get("longName") or member.get("name") or fallback.get("name") or symbol,
    "sector": sector,
    "sectorKey": sector_key,
    "sizeBucket": member.get("_marketMapSize") or market_map_size_bucket(member, index),
    "price": round(float(price), 2) if price is not None else None,
    "changePct": change_pct,
    "source": source,
    "quality": quality,
    "rank": int(member.get("_marketMapRank") or index + 1),
    "span": market_map_tile_span(index, quote),
  }
  return payload, live_1d


def build_market_map_sector_groups(companies: list[dict]) -> list[dict]:
  groups: dict[str, dict] = {}
  for company in companies:
    key = company.get("sectorKey") or canonical_sector_key(company.get("sector") or "Other")
    group = groups.setdefault(
      key,
      {
        "key": key,
        "label": str(company.get("sector") or "Other").title(),
        "count": 0,
        "liveCount": 0,
        "proxyCount": 0,
        "avgChangePct": 0.0,
        "best": None,
        "worst": None,
        "companies": [],
      },
    )
    group["count"] += 1
    if company.get("quality") == "live":
      group["liveCount"] += 1
    else:
      group["proxyCount"] += 1
    group["companies"].append(company)
    if not group["best"] or float(company.get("changePct") or 0.0) > float(group["best"].get("changePct") or 0.0):
      group["best"] = company
    if not group["worst"] or float(company.get("changePct") or 0.0) < float(group["worst"].get("changePct") or 0.0):
      group["worst"] = company

  sector_groups = []
  for group in groups.values():
    changes = [float(item.get("changePct") or 0.0) for item in group["companies"]]
    group["avgChangePct"] = round(sum(changes) / len(changes), 2) if changes else 0.0
    group["companies"] = sorted(group["companies"], key=lambda item: int(item.get("rank") or 999999))
    sector_groups.append(group)
  return sorted(sector_groups, key=lambda item: (-int(item.get("count") or 0), item.get("label") or ""))


def market_heat_map_cache_key(market: str, period: str, limit: int, sector: str, size: str, sort: str, scope: str) -> str:
  return "::".join(["market_heat_map", market, period, str(limit), sector or "all", size or "all", sort or "rank", scope or "top250"])


def build_market_heat_map(market: str = "india", period: str = "1D", limit: int = 80, sector: str = "all", size: str = "all", sort: str = "rank", scope: str = "top250") -> dict:
  normalized_market = market if market in MARKET_MAP_UNIVERSES else "india"
  normalized_period = period if period in SECTOR_PERIOD_LABELS else "1D"
  requested_sector = sector or "all"
  requested_size = size or "all"
  requested_scope = normalize_market_map_scope(scope)
  requested_universe = MARKET_MAP_UNIVERSES[normalized_market]
  members, universe_name, using_fallback_universe = load_market_map_members(requested_universe)
  scoped_members, normalized_scope, scope_count = apply_market_map_scope(members, requested_scope)
  max_items = int(clamp(float(limit or 80), 12, 1000))
  filtered_members = filter_market_map_members(scoped_members, requested_sector, requested_size)
  selected = filtered_members[:max_items]
  symbols = [str(item.get("symbol") or "").upper() for item in selected if item.get("symbol")]
  quote_map = fetch_live_quotes(symbols, fast=True)
  sector_payload = build_sector_matrix(normalized_market, normalized_period, None)
  sector_source = sector_payload.get("source") or "market data"
  sector_changes = {
    canonical_sector_key(item.get("sector") or item.get("label")): float(item.get("changePct") or 0.0)
    for item in sector_payload.get("sectors", [])
  }

  tiles = []
  live_count = 0
  for index, member in enumerate(selected):
    symbol = str(member.get("symbol") or "").upper()
    quote = quote_map.get(symbol) or {}
    company, live_1d = market_map_company_payload(member, quote, sector_changes, sector_source, normalized_period, index)
    if live_1d:
      live_count += 1
    tiles.append(company)

  sort_key = (sort or "rank").lower()
  if sort_key == "sector":
    tiles.sort(key=lambda item: (item.get("sectorKey") or "other", item.get("rank") or 999999))
  elif sort_key == "change":
    tiles.sort(key=lambda item: float(item.get("changePct") or 0.0), reverse=True)
  elif sort_key == "name":
    tiles.sort(key=lambda item: str(item.get("name") or item.get("symbol") or ""))

  return {
    "market": normalized_market,
    "universe": universe_name,
    "requestedUniverse": requested_universe,
    "usingFallbackUniverse": using_fallback_universe,
    "universeCount": len(members),
    "scopeCount": scope_count,
    "filteredCount": len(filtered_members),
    "returnedCount": len(tiles),
    "filters": {"sector": requested_sector, "size": requested_size, "sort": sort_key, "limit": max_items, "scope": normalized_scope},
    "scopes": [
      {"key": key, "label": "All listed" if key == "all" else f"Top {value}", "count": len(members) if value <= 0 else min(value, len(members))}
      for key, value in MARKET_MAP_SCOPE_LIMITS.items()
    ],
    "sectors": market_map_sector_options(scoped_members),
    "period": normalized_period,
    "periodLabel": SECTOR_PERIOD_LABELS[normalized_period],
    "updatedAt": datetime.now(timezone.utc).isoformat(),
    "tiles": tiles,
    "tableRows": tiles,
    "sectorGroups": build_market_map_sector_groups(tiles),
    "warmupSymbols": symbols[:160],
    "source": f"{universe_name} local manifest; live quotes where available; sector index proxy otherwise",
    "sourceNote": f"Universe scope is {normalized_scope.replace('top', 'top ')} from the local manifest. Tile area follows local universe rank or available volume, not verified market capitalization. Daily history warmup is queued for the visible slice and table snapshots are cached locally.",
    "liveCount": live_count,
    "proxyCount": max(len(tiles) - live_count, 0),
  }


def build_market_heat_map_with_cache(market: str, period: str, limit: int, sector: str, size: str, sort: str, scope: str) -> dict:
  normalized_scope = normalize_market_map_scope(scope)
  cache_key = market_heat_map_cache_key(market, period, limit, sector, size, sort, normalized_scope)
  try:
    payload = build_market_heat_map(market, period, limit, sector, size, sort, normalized_scope)
    save_payload_cache(cache_key, payload, payload.get("source") or "Market heat map")
    payload["cacheState"] = "fresh"
    payload["cacheKey"] = cache_key
    return payload
  except Exception:
    cached = load_cached_payload(cache_key)
    if cached:
      payload, source, updated_at = cached
      fallback_payload = dict(payload)
      fallback_payload["cacheState"] = "stale"
      fallback_payload["cacheSource"] = source
      fallback_payload["cacheUpdatedAt"] = updated_at
      fallback_payload["cacheKey"] = cache_key
      return fallback_payload
    raise


def build_overview_payload(symbols: list[str], active: str | None, region_key: str | None = None) -> dict:
  payload = build_live_quotes(symbols, active)
  active_item = payload.get("active") or {}
  exchange = active_item.get("exchange") or active_item.get("symbol") or "GLOBAL"
  market_state = active_item.get("marketState") or "REGULAR"
  payload["active"] = {
    **active_item,
    "marketSession": active_item.get("marketSession") or build_market_session(exchange, exchange, market_state, active_item.get("asOf")),
    "regime": "Refreshing active view",
  }
  payload["selectedRegion"] = region_config(region_key or infer_region_key(active_item.get("symbol"), exchange, active_item.get("currency")))["key"]
  return payload


SYMBOL_INPUT_RE = re.compile(r"^[A-Z0-9^=.\-]{1,32}$")


class RequestBodyError(ValueError):
  def __init__(self, status: HTTPStatus, message: str):
    super().__init__(message)
    self.status = status


def validate_symbol_inputs(values, limit: int = 50) -> list[str]:
  if not isinstance(values, list):
    raise RequestBodyError(HTTPStatus.BAD_REQUEST, "symbols must be an array")
  if len(values) > limit:
    raise RequestBodyError(HTTPStatus.BAD_REQUEST, f"symbols must contain at most {limit} items")
  cleaned = []
  for value in values:
    symbol = str(value or "").strip().upper()
    if not symbol:
      continue
    if not SYMBOL_INPUT_RE.fullmatch(symbol):
      raise RequestBodyError(HTTPStatus.BAD_REQUEST, f"invalid symbol: {symbol[:32]}")
    cleaned.append(symbol)
  return list(dict.fromkeys(cleaned))


def loopback_hostname(value: str | None) -> str:
  if not value:
    return ""
  try:
    return (urllib.parse.urlparse(f"//{value}").hostname or "").lower()
  except ValueError:
    return ""


class FinancialBoardHandler(BaseHTTPRequestHandler):
  def request_is_local(self, require_origin_match: bool = False) -> bool:
    host_header = self.headers.get("Host", "")
    if loopback_hostname(host_header) not in {"localhost", "127.0.0.1", "::1"}:
      return False
    if str(self.headers.get("Sec-Fetch-Site", "")).lower() == "cross-site":
      return False
    origin = self.headers.get("Origin")
    if not origin:
      return not require_origin_match
    try:
      parsed_origin = urllib.parse.urlparse(origin)
      origin_host = (parsed_origin.hostname or "").lower()
      origin_port = parsed_origin.port
      parsed_host = urllib.parse.urlparse(f"//{host_header}")
      request_port = parsed_host.port
    except ValueError:
      return False
    return (
      parsed_origin.scheme in {"http", "https"}
      and origin_host in {"localhost", "127.0.0.1", "::1"}
      and origin_port == request_port
    )

  def write_security_headers(self) -> None:
    self.send_header("X-Content-Type-Options", "nosniff")
    self.send_header("X-Frame-Options", "DENY")
    self.send_header("Referrer-Policy", "same-origin")
    self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=()")
    self.send_header("Cross-Origin-Opener-Policy", "same-origin")
    self.send_header("Cross-Origin-Resource-Policy", "same-origin")
    self.send_header(
      "Content-Security-Policy",
      "default-src 'self'; "
      "script-src 'self'; "
      "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
      "font-src 'self' https://fonts.gstatic.com; "
      "img-src 'self' data: https:; "
      "connect-src 'self'; "
      "object-src 'none'; "
      "frame-ancestors 'none'; "
      "base-uri 'self'; "
      "form-action 'self'",
    )

  def do_HEAD(self) -> None:
    if not self.request_is_local():
      return self.send_error(HTTPStatus.FORBIDDEN, "Local requests only")
    parsed = urllib.parse.urlparse(self.path)
    if parsed.path in {"/", "/index.html", "/app.js", "/styles.css", "/vendor/cytoscape.min.js", "/api/health"}:
      self.send_response(HTTPStatus.OK)
      self.write_security_headers()
      self.end_headers()
      return
    self.send_error(HTTPStatus.NOT_FOUND, "Not found")

  def do_OPTIONS(self) -> None:
    if not self.request_is_local(require_origin_match=True):
      return self.send_error(HTTPStatus.FORBIDDEN, "Cross-origin requests are not allowed")
    self.send_response(HTTPStatus.NO_CONTENT)
    self.write_security_headers()
    self.end_headers()

  def do_GET(self) -> None:
    if not self.request_is_local():
      return self.send_error(HTTPStatus.FORBIDDEN, "Local requests only")
    parsed = urllib.parse.urlparse(self.path)
    if parsed.path in {"/", "/index.html"}:
      return self.serve_file("index.html", "text/html; charset=utf-8")
    if parsed.path == "/styles.css":
      return self.serve_file("styles.css", "text/css; charset=utf-8")
    if parsed.path == "/app.js":
      return self.serve_file("app.js", "application/javascript; charset=utf-8")
    if parsed.path == "/vendor/cytoscape.min.js":
      return self.serve_file("vendor/cytoscape.min.js", "application/javascript; charset=utf-8")
    if parsed.path == "/api/health":
      return self.send_json({"status": "ok"})
    if parsed.path == "/api/config":
      return self.send_json(public_config())
    if parsed.path == "/api/presets":
      return self.send_json({"presets": MARKET_PRESETS, "research": RESEARCH_REFERENCES, "classicResearch": CLASSIC_QUANT_REFERENCES})
    if parsed.path == "/api/watchlists":
      return self.send_json({"watchlists": list_watchlists()})
    if parsed.path == "/api/academy":
      params = urllib.parse.parse_qs(parsed.query)
      symbol = ((params.get("symbol") or [""])[0] or "").strip().upper() or None
      use_web = (params.get("web") or ["1"])[0] != "0"
      use_llm = (params.get("llm") or ["1"])[0] != "0"
      return self.send_json(build_academy_payload(symbol, use_web=use_web, use_llm=use_llm))
    if parsed.path == "/api/events":
      params = urllib.parse.parse_qs(parsed.query)
      category = (params.get("category") or ["business"])[0]
      symbol = ((params.get("symbol") or [""])[0] or "").upper() or None
      keyword = (params.get("q") or [""])[0]
      return self.send_json(build_event_feed(category, symbol, keyword))
    if parsed.path == "/api/market-events":
      params = urllib.parse.parse_qs(parsed.query)
      category = (params.get("category") or ["all"])[0]
      symbol = ((params.get("symbol") or [""])[0] or "").upper() or None
      try:
        limit = int((params.get("limit") or ["20"])[0] or 20)
      except ValueError:
        limit = 20
      return self.send_json(
        {
          "items": load_market_events(category, symbol, limit=max(1, min(limit, 100))),
          "asOf": datetime.now(timezone.utc).isoformat(),
          "localStore": {"db": DB_PATH.name, "table": "market_events"},
        }
      )
    if parsed.path == "/api/radar":
      params = urllib.parse.parse_qs(parsed.query)
      symbol = ((params.get("symbol") or [""])[0] or "").upper() or None
      return self.send_json(build_radar_payload(symbol))
    if parsed.path == "/api/search":
      params = urllib.parse.parse_qs(parsed.query)
      query = (params.get("q") or [""])[0].strip()[:160]
      results = fetch_yahoo_search(query) if query else []
      if not results and query:
        results = [
          {
            "symbol": normalize_symbol(query, "nse"),
            "name": f"{query.upper()} manual symbol",
            "exchange": "NSE",
            "region": "NSE",
            "matchType": "Manual symbol",
            "matchReason": "No provider/local match; treating text as NSE symbol",
            "score": 10,
          }
        ]
      return self.send_json({"results": results})
    if parsed.path == "/api/sectors":
      params = urllib.parse.parse_qs(parsed.query)
      market = (params.get("market") or ["india"])[0].strip().lower()
      period = (params.get("period") or ["1D"])[0].strip().upper()
      benchmark = ((params.get("benchmark") or [""])[0] or "").strip().upper() or None
      return self.send_json(build_sector_matrix(market, period, benchmark))
    if parsed.path == "/api/market-map":
      params = urllib.parse.parse_qs(parsed.query)
      market = (params.get("market") or ["india"])[0].strip().lower()
      period = (params.get("period") or ["1D"])[0].strip().upper()
      sector = (params.get("sector") or ["all"])[0].strip().lower() or "all"
      size = (params.get("size") or ["all"])[0].strip().lower() or "all"
      sort = (params.get("sort") or ["rank"])[0].strip().lower() or "rank"
      scope = (params.get("scope") or ["top250"])[0].strip().lower() or "top250"
      try:
        limit = int((params.get("limit") or ["80"])[0] or 80)
      except ValueError:
        limit = 80
      return self.send_json(build_market_heat_map_with_cache(market, period, limit, sector, size, sort, scope))
    if parsed.path == "/api/data-sources":
      return self.send_json({"updatedAt": datetime.now(timezone.utc).isoformat(), "sources": TRUSTED_DATA_SOURCE_REGISTRY})
    if parsed.path == "/api/global-markets":
      return self.send_json({"updatedAt": datetime.now(timezone.utc).isoformat(), "markets": build_global_market_overview()})
    if parsed.path == "/api/overview":
      params = urllib.parse.parse_qs(parsed.query)
      try:
        symbols = validate_symbol_inputs([item for item in ((params.get("symbols") or [""])[0].split(",")) if item])
      except RequestBodyError as error:
        return self.send_json({"error": str(error)}, status=error.status)
      active = ((params.get("active") or [""])[0] or "").upper() or None
      if active and not SYMBOL_INPUT_RE.fullmatch(active):
        return self.send_json({"error": "invalid active symbol"}, status=HTTPStatus.BAD_REQUEST)
      region = ((params.get("region") or [""])[0] or "").strip().lower() or None
      if region and region not in REGION_CONFIGS:
        return self.send_json({"error": "unsupported region"}, status=HTTPStatus.BAD_REQUEST)
      return self.send_json(build_overview_payload(symbols, active, region))
    if parsed.path == "/api/quotes":
      # Lean short-poll endpoint: returns only what is needed to tick prices
      # in place on the client. Server-side micro-cached so concurrent clients
      # share the same JSON for QUOTES_PAYLOAD_CACHE_TTL seconds.
      params = urllib.parse.parse_qs(parsed.query)
      try:
        symbols = validate_symbol_inputs([item for item in ((params.get("symbols") or [""])[0].split(",")) if item])
      except RequestBodyError as error:
        return self.send_json({"error": str(error)}, status=error.status)
      active = ((params.get("active") or [""])[0] or "").upper() or None
      if active and not SYMBOL_INPUT_RE.fullmatch(active):
        return self.send_json({"error": "invalid active symbol"}, status=HTTPStatus.BAD_REQUEST)
      return self.send_json(build_quote_snapshot(symbols, active))
    if parsed.path == "/api/history/status":
      return self.send_json(history_warmup_status())
    if parsed.path == "/api/operations":
      return self.send_json(operator_jobs_payload())
    if parsed.path == "/api/short-horizon":
      params = urllib.parse.parse_qs(parsed.query)
      symbol = ((params.get("symbol") or [""])[0]).upper()
      if not symbol or not SYMBOL_INPUT_RE.fullmatch(symbol):
        return self.send_json({"error": "valid symbol is required"}, status=HTTPStatus.BAD_REQUEST)
      try:
        horizon = int((params.get("horizon") or ["5"])[0])
      except ValueError:
        horizon = 5
      chart_range = ((params.get("range") or ["1Y"])[0]).upper()
      history, _ = build_history(symbol, chart_range)
      if not history or len(history) < 25:
        history, _ = build_history(symbol, "1Y")
      return self.send_json({
        "symbol": symbol,
        "horizon": horizon,
        "asOf": datetime.now(timezone.utc).isoformat(),
        "shortHorizon": build_short_horizon_forecast(history, horizon=horizon),
        "historyBars": len(history),
      })
    if parsed.path == "/api/stream":
      params = urllib.parse.parse_qs(parsed.query)
      try:
        symbols = validate_symbol_inputs([item for item in ((params.get("symbols") or [""])[0].split(",")) if item])
      except RequestBodyError as error:
        return self.send_json({"error": str(error)}, status=error.status)
      active = ((params.get("active") or [""])[0] or "").upper() or None
      if active and not SYMBOL_INPUT_RE.fullmatch(active):
        return self.send_json({"error": "invalid active symbol"}, status=HTTPStatus.BAD_REQUEST)
      return self.stream_quotes(symbols, active)
    self.send_error(HTTPStatus.NOT_FOUND, "Not found")

  def do_POST(self) -> None:
    if not self.request_is_local(require_origin_match=bool(self.headers.get("Origin"))):
      return self.send_json({"error": "Cross-origin requests are not allowed"}, status=HTTPStatus.FORBIDDEN)
    parsed = urllib.parse.urlparse(self.path)
    try:
      body = self.read_json()
    except RequestBodyError as error:
      return self.send_json({"error": str(error)}, status=error.status)

    if parsed.path == "/api/config":
      try:
        return self.send_json(save_config(body))
      except ValueError as error:
        return self.send_json({"error": str(error)}, status=HTTPStatus.BAD_REQUEST)

    if parsed.path == "/api/watchlists":
      name = str(body.get("name", "")).strip()
      try:
        symbols = validate_symbol_inputs(body.get("symbols", []))
      except RequestBodyError as error:
        return self.send_json({"error": str(error)}, status=error.status)
      if len(name) > 80:
        return self.send_json({"error": "name must contain at most 80 characters"}, status=HTTPStatus.BAD_REQUEST)
      if not name or not symbols:
        return self.send_json({"error": "name and symbols are required"}, status=HTTPStatus.BAD_REQUEST)
      save_watchlist(name, list(dict.fromkeys(symbols)))
      return self.send_json({"ok": True, "watchlists": list_watchlists()})

    if parsed.path == "/api/dashboard":
      try:
        symbols = validate_symbol_inputs(body.get("symbols", []))
      except RequestBodyError as error:
        return self.send_json({"error": str(error)}, status=error.status)
      active = str(body.get("active") or "").strip().upper() or None
      if active and not SYMBOL_INPUT_RE.fullmatch(active):
        return self.send_json({"error": "invalid active symbol"}, status=HTTPStatus.BAD_REQUEST)
      chart_range = str(body.get("chartRange") or "1M").upper()
      if chart_range not in CHART_RANGE_CONFIG:
        return self.send_json({"error": "unsupported chart range"}, status=HTTPStatus.BAD_REQUEST)
      region = str(body.get("region") or "").strip().lower() or None
      if region and region not in REGION_CONFIGS:
        return self.send_json({"error": "unsupported region"}, status=HTTPStatus.BAD_REQUEST)
      return self.send_json(build_dashboard(symbols, active, chart_range, region))

    if parsed.path == "/api/history/warm":
      try:
        symbols = validate_symbol_inputs(body.get("symbols", []), limit=200)
      except RequestBodyError as error:
        return self.send_json({"error": str(error)}, status=error.status)
      raw_ranges = body.get("ranges", [])
      if not isinstance(raw_ranges, list) or len(raw_ranges) > len(CHART_RANGE_CONFIG):
        return self.send_json({"error": "invalid history ranges"}, status=HTTPStatus.BAD_REQUEST)
      ranges = [str(item).upper() for item in raw_ranges if str(item).upper() in CHART_RANGE_CONFIG]
      return self.send_json(start_history_warmup(symbols, ranges or HISTORY_PREFETCH_RANGES, reason="client-idle"))

    if parsed.path == "/api/operations/run":
      job_id = str(body.get("jobId") or "").strip()
      try:
        return self.send_json(start_operator_job(job_id), status=HTTPStatus.ACCEPTED)
      except ValueError as error:
        return self.send_json({"error": str(error)}, status=HTTPStatus.BAD_REQUEST)

    if parsed.path == "/api/lab":
      symbol = str(body.get("symbol") or "").strip().upper()
      if not symbol or not SYMBOL_INPUT_RE.fullmatch(symbol):
        return self.send_json({"error": "valid symbol is required"}, status=HTTPStatus.BAD_REQUEST)
      try:
        horizon = int(body.get("horizon") or 10)
      except (TypeError, ValueError):
        return self.send_json({"error": "horizon must be a number"}, status=HTTPStatus.BAD_REQUEST)
      if horizon < 1 or horizon > 60:
        return self.send_json({"error": "horizon must be between 1 and 60"}, status=HTTPStatus.BAD_REQUEST)
      stress = str(body.get("stress") or "base")
      if stress not in {"base", "riskoff", "growth", "inflation"}:
        return self.send_json({"error": "unsupported stress scenario"}, status=HTTPStatus.BAD_REQUEST)
      chart_range = str(body.get("chartRange") or "1M").upper()
      if chart_range not in CHART_RANGE_CONFIG:
        return self.send_json({"error": "unsupported chart range"}, status=HTTPStatus.BAD_REQUEST)
      snapshot = build_ticker_snapshot(symbol, stress=stress, horizon=horizon, chart_range=chart_range)
      return self.send_json(
        {
          "symbol": symbol,
          "history": snapshot["history"][-40:],
          "historySeries": snapshot.get("historySeries", [])[-40:],
          "projected": snapshot["forecast"]["projected"],
          "expectedReturn": snapshot["forecast"]["expectedReturn"],
          "direction": snapshot["forecast"]["direction"],
          "confidence": snapshot["forecast"]["confidence"],
          "triggers": snapshot["forecast"]["triggers"],
          "backtest": snapshot["lab"]["backtest"],
          "historySource": snapshot.get("historySource"),
          "historyCachedAt": snapshot.get("historyCachedAt"),
          "historyCacheState": snapshot.get("historyCacheState"),
        }
      )

    if parsed.path == "/api/research":
      query = str(body.get("query") or "").strip()
      if not query:
        return self.send_json({"error": "query is required"}, status=HTTPStatus.BAD_REQUEST)
      if len(query) > 2000:
        return self.send_json({"error": "query must contain at most 2000 characters"}, status=HTTPStatus.BAD_REQUEST)
      symbol = str(body.get("symbol") or "").strip().upper() or None
      if symbol and not SYMBOL_INPUT_RE.fullmatch(symbol):
        return self.send_json({"error": "invalid symbol"}, status=HTTPStatus.BAD_REQUEST)
      use_web = bool(body.get("useWeb", True))
      use_llm = bool(body.get("useLlm", True))
      return self.send_json(run_research_agent(query, symbol, use_web, use_llm))

    self.send_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

  def read_json(self) -> dict:
    if "application/json" not in str(self.headers.get("Content-Type", "")).lower():
      raise RequestBodyError(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "Content-Type must be application/json")
    try:
      length = int(self.headers.get("Content-Length", "0") or "0")
    except ValueError as error:
      raise RequestBodyError(HTTPStatus.BAD_REQUEST, "Invalid Content-Length") from error
    if length > 262144:
      raise RequestBodyError(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "JSON body exceeds 256 KiB")
    if length <= 0:
      raise RequestBodyError(HTTPStatus.BAD_REQUEST, "JSON body is required")
    try:
      raw = self.rfile.read(length).decode("utf-8")
    except UnicodeDecodeError as error:
      raise RequestBodyError(HTTPStatus.BAD_REQUEST, "JSON body must be UTF-8") from error
    try:
      payload = json.loads(raw)
    except json.JSONDecodeError as error:
      raise RequestBodyError(HTTPStatus.BAD_REQUEST, "Malformed JSON body") from error
    if not isinstance(payload, dict):
      raise RequestBodyError(HTTPStatus.BAD_REQUEST, "JSON body must be an object")
    return payload

  def serve_file(self, filename: str, content_type: str) -> None:
    path = BASE_DIR / filename
    if not path.exists():
      self.send_error(HTTPStatus.NOT_FOUND, "File not found")
      return
    data = path.read_bytes()
    self.send_response(HTTPStatus.OK)
    self.write_security_headers()
    self.send_header("Content-Type", content_type)
    self.send_header("Content-Length", str(len(data)))
    self.send_header("Cache-Control", "no-store, max-age=0")
    self.end_headers()
    try:
      self.wfile.write(data)
    except (BrokenPipeError, ConnectionResetError):
      return

  def send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
    raw = json.dumps(payload).encode("utf-8")
    accept_encoding = self.headers.get("Accept-Encoding", "")
    # Gzip payloads larger than 860 bytes when the client supports it
    if "gzip" in accept_encoding and len(raw) > 860:
      data = gzip.compress(raw, compresslevel=6)
      self.send_response(status)
      self.write_security_headers()
      self.send_header("Content-Type", "application/json; charset=utf-8")
      self.send_header("Content-Encoding", "gzip")
      self.send_header("Vary", "Accept-Encoding")
      self.send_header("Cache-Control", "no-store, max-age=0")
      self.send_header("Content-Length", str(len(data)))
      self.end_headers()
      self.wfile.write(data)
    else:
      self.send_response(status)
      self.write_security_headers()
      self.send_header("Content-Type", "application/json; charset=utf-8")
      self.send_header("Cache-Control", "no-store, max-age=0")
      self.send_header("Content-Length", str(len(raw)))
      self.end_headers()
      self.wfile.write(raw)

  def stream_quotes(self, symbols: list[str], active: str | None) -> None:
    self.send_response(HTTPStatus.OK)
    self.write_security_headers()
    self.send_header("Content-Type", "text/event-stream")
    self.send_header("Cache-Control", "no-cache")
    self.send_header("Connection", "keep-alive")
    self.end_headers()

    try:
      for _ in range(240):
        if _SERVER_STOPPING.is_set():
          return
        payload = build_live_quotes(symbols, active, allow_history_fallback=False)
        message = f"event: quote\ndata: {json.dumps(payload)}\n\n".encode("utf-8")
        self.wfile.write(message)
        self.wfile.flush()
        time.sleep(QUOTE_STREAM_INTERVAL_SECONDS)
    except (BrokenPipeError, ConnectionResetError):
      return

  def log_message(self, format: str, *args) -> None:
    return


class QuietThreadingHTTPServer(ThreadingHTTPServer):
  daemon_threads = True
  block_on_close = False

  def handle_error(self, request, client_address) -> None:
    error_type, _, _ = sys.exc_info()
    if error_type in {BrokenPipeError, ConnectionResetError}:
      return
    super().handle_error(request, client_address)


def parse_port(value: str | int | None, default: int = DEFAULT_PORT) -> int:
  if value in (None, ""):
    return default
  try:
    port = int(value)
  except (TypeError, ValueError) as exc:
    raise ValueError(f"Port must be a number, got {value!r}") from exc
  if port < 1 or port > 65535:
    raise ValueError(f"Port must be between 1 and 65535, got {port}")
  return port


def build_server(host: str, port: int, allow_port_fallback: bool = True) -> tuple[QuietThreadingHTTPServer, int]:
  last_error = None
  max_port = min(65535, port + (PORT_SCAN_LIMIT if allow_port_fallback else 0))
  for candidate in range(port, max_port + 1):
    try:
      return QuietThreadingHTTPServer((host, candidate), FinancialBoardHandler), candidate
    except OSError as exc:
      if exc.errno != errno.EADDRINUSE:
        raise
      last_error = exc
  raise OSError(errno.EADDRINUSE, f"No available port found from {port} to {max_port}") from last_error


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
  parser = argparse.ArgumentParser(description="Run the Financial Board local server.")
  parser.add_argument(
    "-p",
    "--port",
    default=None,
    help="Port to bind. Defaults to FINANCIAL_BOARD_PORT, PORT, or 8000.",
  )
  parser.add_argument(
    "--strict-port",
    action="store_true",
    help="Fail instead of trying nearby ports when the requested port is already in use.",
  )
  return parser.parse_args(argv)


def run(port: int | str | None = None, allow_port_fallback: bool = True) -> None:
  _SERVER_STOPPING.clear()
  init_db()
  requested_port = parse_port(port or os.environ.get("FINANCIAL_BOARD_PORT") or os.environ.get("PORT"))
  server, bound_port = build_server("127.0.0.1", requested_port, allow_port_fallback=allow_port_fallback)
  if bound_port != requested_port:
    print(f"Port {requested_port} is already in use; using {bound_port} instead.")
  print(f"Financial Board running on http://127.0.0.1:{bound_port}")
  try:
    server.serve_forever()
  finally:
    _SERVER_STOPPING.set()
    server.server_close()


def main(argv: list[str] | None = None) -> int:
  args = parse_args(argv)
  try:
    run(args.port, allow_port_fallback=not args.strict_port)
  except KeyboardInterrupt:
    _SERVER_STOPPING.set()
    print("\nFinancial Board stopped.")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
