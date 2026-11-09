"""
Live API Clients for Real-Time Job Market Ingestion.
Fetches active job listings from public tech job feeds (Arbeitnow & Remotive).
"""

import urllib.request
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class ArbeitnowClient:
    """Client for Arbeitnow Job Board API."""
    BASE_URL = "https://www.arbeitnow.com/api/job-board-api"

    def fetch_jobs(self, max_pages: int = 3, timeout: int = 6) -> List[Dict[str, Any]]:
        jobs: List[Dict[str, Any]] = []
        headers = {"User-Agent": "JobMarketIntelligence/1.0 (Mozilla/5.0)"}
        next_url = self.BASE_URL

        for page in range(max_pages):
            if not next_url:
                break
            try:
                req = urllib.request.Request(next_url, headers=headers)
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    if response.status == 200:
                        data = json.loads(response.read().decode("utf-8"))
                        page_jobs = data.get("data", [])
                        for item in page_jobs:
                            item["source"] = "Arbeitnow API"
                        jobs.extend(page_jobs)
                        next_url = data.get("links", {}).get("next")
                    else:
                        break
            except Exception as e:
                logger.warning(f"Arbeitnow API fetch failed on page {page + 1}: {e}")
                break
        return jobs

class RemotiveClient:
    """Client for Remotive Remote Jobs API."""
    BASE_URL = "https://remotive.com/api/remote-jobs?category=software-dev&limit=50"

    def fetch_jobs(self, timeout: int = 6) -> List[Dict[str, Any]]:
        jobs: List[Dict[str, Any]] = []
        headers = {"User-Agent": "JobMarketIntelligence/1.0 (Mozilla/5.0)"}
        try:
            req = urllib.request.Request(self.BASE_URL, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    raw_list = data.get("jobs", [])
                    for item in raw_list:
                        # Normalize key schema
                        item["source"] = "Remotive API"
                        item["company_name"] = item.get("company_name", "")
                        jobs.append(item)
        except Exception as e:
            logger.warning(f"Remotive API fetch failed: {e}")
        return jobs

