"""
NPI Registry Enrichment — TFA Analytics / Naeto Services Corp
==============================================================
Queries the CMS NPPES NPI Registry to enrich market datasets with
active-provider counts per ZIP code.

Uses concurrent HTTP requests to handle state-level batch lookups
(hundreds of ZIPs) efficiently.

Author : Dr. Roi Castrellon (Naeto Services Corp)
Version: 2.0 — Concurrent refactor for SOW M1 compliance
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import requests

logger = logging.getLogger(__name__)

NPI_API_URL = "https://npiregistry.cms.hhs.gov/api/?version=2.1"
DEFAULT_TAXONOMY = "Dentist"
MAX_WORKERS = 5
REQUEST_TIMEOUT_S = 10


def _fetch_single_zip(
    zip_code: str,
    taxonomy: str = DEFAULT_TAXONOMY,
    limit: int = 200,
) -> tuple:
    """Query NPPES for a single ZIP code (thread-safe).

    Args:
        zip_code:  5-digit postal code string.
        taxonomy:  Provider taxonomy description to filter on.
        limit:     Maximum results per query.

    Returns:
        Tuple of (zip_code, provider_count).
    """
    params = {
        "taxonomy_description": taxonomy,
        "postal_code": zip_code,
        "limit": limit,
    }
    try:
        resp = requests.get(NPI_API_URL, params=params, timeout=REQUEST_TIMEOUT_S)
        resp.raise_for_status()
        count = resp.json().get("result_count", 0)
        logger.debug("ZIP %s → %d providers", zip_code, count)
        return zip_code, count
    except requests.RequestException as exc:
        logger.warning("NPI lookup failed for ZIP %s: %s", zip_code, exc)
        return zip_code, 0


def fetch_npi_dentist_counts(
    zips: List[str],
    taxonomy: str = DEFAULT_TAXONOMY,
    max_workers: int = MAX_WORKERS,
) -> Dict[str, int]:
    """Concurrently fetch provider counts for a batch of ZIP codes.

    Uses ``ThreadPoolExecutor`` to parallelize HTTP requests,
    reducing wall-clock time by up to ``max_workers``×.

    Args:
        zips:        List of 5-digit ZIP code strings.
        taxonomy:    Provider taxonomy filter.
        max_workers: Thread pool size (default 5).

    Returns:
        Dict mapping each ZIP code to its provider count.
    """
    results: Dict[str, int] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(_fetch_single_zip, z, taxonomy): z for z in zips
        }
        for future in as_completed(futures):
            zip_code, count = future.result()
            results[zip_code] = count

    logger.info("NPI batch complete — %d ZIPs queried.", len(results))
    return results


def enrich_market_data(
    data_path: str = "data/raw/real_market_data.csv",
    zips: Optional[List[str]] = None,
) -> pd.DataFrame:
    """Enrich a market CSV with live NPI provider counts.

    Args:
        data_path: Path to the market data CSV.
        zips:      ZIP codes to query. If ``None``, uses the unique
                   ZIP codes present in the CSV's ``zip_code`` column.

    Returns:
        Updated DataFrame (also persisted back to ``data_path``).
    """
    path = Path(data_path)
    if not path.exists():
        logger.error("Market data file not found: %s", path)
        return pd.DataFrame()

    df = pd.read_csv(path)
    target_zips = zips or df["zip_code"].astype(str).unique().tolist()

    counts = fetch_npi_dentist_counts(target_zips)

    # Merge new counts, preserving existing values where API returned 0
    df["active_dentists"] = (
        df["zip_code"]
        .astype(str)
        .map(counts)
        .fillna(df.get("active_dentists", 0))
    )

    df.to_csv(path, index=False)
    logger.info("Updated %s with NPI counts: %s", path, counts)
    return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Default Doral ZIPs for local testing
    enrich_market_data(zips=["33178", "33122", "33166"])

