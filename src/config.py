import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    base_url: str = os.getenv("BASE_URL", "https://mse.co.mw/")
    listings_path: str = os.getenv("LISTINGS_PATH", "/market/mainboard")
    user_agent: str = os.getenv("USER_AGENT", "MSEAgent/0.0.1")
    timeout: int = int(os.getenv("REQUEST_TIMEOUT", "20"))
    retries: int = int(os.getenv("REQUEST_RETRIES", "3"))
    backoff: float = float(os.getenv("REQUEST_BACKOFF", "1.5"))
    data_dir: str = os.getenv("DATA_DIR", "./data")
    financials_dir: str = os.getenv("FINANCIALS_DIR", "./data/financials")
    http_state_path: str = os.getenv("HTTP_STATE_PATH", "./data/http_state.json")
    http_cache_path: str = os.getenv("HTTP_CACHE_PATH", "./data/http_cache")
    http_cache_expire: int = int(os.getenv("HTTP_CACHE_EXPIRE_SECONDS", str(3 * 3600)))
    retry_after_max_attempts: int = int(os.getenv("RETRY_AFTER_MAX_ATTEMPTS", "3"))
    retry_after_floor: float = float(os.getenv("RETRY_AFTER_FLOOR", "1"))

settings = Settings()
