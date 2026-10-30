import json
import logging
import os
from typing import Dict, Any, List
import requests
from ..config import Config

logger = logging.getLogger(__name__)

class DatabaseService:
    """Manages cloud synchronization with PostgreSQL/Supabase and local offline ledger."""

    def __init__(self, local_ledger_path: str = None):
        self.local_ledger_path = local_ledger_path or os.path.join(Config.DATA_DIR, "local_ledger.json")

    def save_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save inspection record to local ledger and attempt cloud sync."""
        # 1. Local Persistence (Offline-First)
        records = self.get_all_reports()
        records.append(report_data)
        os.makedirs(os.path.dirname(self.local_ledger_path), exist_ok=True)
        with open(self.local_ledger_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)

        # 2. Cloud Synchronization (Supabase REST API)
        synced_cloud = False
        if Config.SUPABASE_URL and Config.SUPABASE_KEY and not Config.TESTING:
            try:
                headers = {
                    "apikey": Config.SUPABASE_KEY,
                    "Authorization": f"Bearer {Config.SUPABASE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal"
                }
                endpoint = f"{Config.SUPABASE_URL}/rest/v1/inspections"
                res = requests.post(endpoint, json=report_data, headers=headers, timeout=5)
                synced_cloud = (res.status_code in [200, 201])
            except Exception as e:
                logger.warning(f"Cloud sync deferred (offline mode): {e}")

        return {
            "status": "saved",
            "report_id": report_data.get("id"),
            "cloud_synced": synced_cloud,
            "offline_stored": True
        }

    def get_all_reports(self) -> List[Dict[str, Any]]:
        """Retrieve all recorded inspection reports from local ledger."""
        if not os.path.exists(self.local_ledger_path):
            return []
        try:
            with open(self.local_ledger_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
