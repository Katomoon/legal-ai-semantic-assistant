import json
import logging
import os
import tempfile
from typing import Any, Dict, List, Optional

import requests

from ..config import Config

logger = logging.getLogger(__name__)


class DatabaseService:
    """Persist reports locally and optionally attempt one Supabase REST insert."""

    def __init__(self, local_ledger_path: Optional[str] = None):
        self.local_ledger_path = local_ledger_path or Config.LOCAL_LEDGER_PATH

    def save_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save locally first, then make one best-effort cloud sync attempt."""
        records = self.get_all_reports()
        records.append(report_data)

        directory = os.path.dirname(os.path.abspath(self.local_ledger_path))
        os.makedirs(directory, exist_ok=True)
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=directory,
                prefix=".ledger-",
                suffix=".tmp",
                delete=False
            ) as temp_file:
                json.dump(records, temp_file, indent=2, ensure_ascii=False)
                temp_path = temp_file.name
            os.replace(temp_path, self.local_ledger_path)
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

        cloud_synced = False
        if Config.SUPABASE_URL and Config.SUPABASE_KEY and not Config.TESTING:
            endpoint = f"{Config.SUPABASE_URL.rstrip('/')}/rest/v1/inspections"
            headers = {
                "apikey": Config.SUPABASE_KEY,
                "Authorization": f"Bearer {Config.SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            }
            try:
                response = requests.post(
                    endpoint,
                    json=report_data,
                    headers=headers,
                    timeout=5
                )
                cloud_synced = response.status_code in (200, 201, 204)
                if not cloud_synced:
                    logger.warning(
                        "Supabase sync failed with HTTP status %s",
                        response.status_code
                    )
            except requests.RequestException as exc:
                logger.warning("Supabase sync failed; report remains local: %s", exc)

        return {
            "status": "saved",
            "report_id": report_data.get("id"),
            "cloud_synced": cloud_synced,
            "offline_stored": True
        }

    def get_all_reports(self) -> List[Dict[str, Any]]:
        """Read the local ledger; return an empty list when it does not exist."""
        if not os.path.exists(self.local_ledger_path):
            return []
        try:
            with open(self.local_ledger_path, "r", encoding="utf-8") as ledger_file:
                records = json.load(ledger_file)
            if not isinstance(records, list):
                logger.error("Local ledger must contain a JSON list")
                return []
            return records
        except (OSError, json.JSONDecodeError) as exc:
            logger.error("Could not read local ledger: %s", exc)
            return []
