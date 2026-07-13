import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from typing import Iterator

import pandas as pd
import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

_local = threading.local()

BASE_URL = os.getenv("API_URL", "http://localhost:8000")
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "8"))
RETRIABLE_STATUS = {429, 500, 502, 503, 504}


def _session() -> requests.Session:

    if not hasattr(_local, "session"):
        _local.session = requests.Session()
    return _local.session


class RetriableError(Exception):
    """Erro padrão para chamar o retry"""


@retry(
    reraise=True,
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=30),
    retry=retry_if_exception_type((requests.RequestException, RetriableError)),
)
def fetch_page(path: str, offset: int, limit: int) -> dict:

    resp = _session().get(
        url=f"{BASE_URL}/{path}", params={"offset": offset, "limit": limit}, timeout=10
    )

    if resp.status_code in RETRIABLE_STATUS:
        raise RetriableError(f"{path} offset={offset} -> HTTP {resp.status_code}")

    resp.raise_for_status()

    return resp.json()


def discover_total(path: str) -> int:

    first = fetch_page(path, offset=0, limit=1)

    return int(first["total"])


def fetch_resource(cfg: dict) -> pd.DataFrame:

    path, page_size = cfg["path"], cfg["page_size"]
    total = discover_total(path)
    offsets = range(0, total, page_size)

    registros: list[dict] = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {
            pool.submit(fetch_page, path, off, page_size): off for off in offsets
        }

        for fut in as_completed(futures):
            payload = fut.result()
            registros.extend(payload["data"])

    return pd.DataFrame(registros)


def extract_all(endpoints: dict) -> Iterator[tuple[str, pd.DataFrame]]:

    data_hoje = date.today().isoformat()

    for name, cfg in endpoints.items():
        df = fetch_resource(cfg)

        df["data_extracao"] = data_hoje

        yield name, df
