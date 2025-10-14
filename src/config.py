import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    base_url: str = os.getenv("BASE_URL", "https://mse.co.mw/")
    listings_path: str = os.getenv("LISTINGS_PATH", "/markets/")
    user_agent: str = os.getenv("USER_AGENT", "MSEAgent/0.0.1 (+https://example.com/contact)")
    timeout: int = int(os.getenv("REQUEST_TIMEOUT", "20"))
    retries: int = int(os.getenv("REQUEST_RETRIES", "3"))
    backoff: float = float(os.getenv("REQUEST_BACKOFF", "1.5"))
    data_dir: str = os.getenv("DATA_DIR", "./data")
    financials_dir: str = os.getenv("FINANCIALS_DIR", "./data/financials")

settings = Settings()
