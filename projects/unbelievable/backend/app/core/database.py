import logging
from typing import Dict, Any, List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class MockDatabaseStore:
    """In-memory database store for running the prototype locally without Supabase setup."""
    def __init__(self):
        self.profiles = {}
        self.raw_files = {}
        self.norm_events = {}
        self.session_texts = {}
        self.nlp_results = {}
        self.score_runs = {}
        self.score_axes = {}
        self.detox_plans = {}
        self.mission_logs = {}
        self.audit_logs = []
        
        # Populate initial test user profile with standard UUID
        self.profiles["00000000-0000-0000-0000-000000000001"] = {
            "id": "00000000-0000-0000-0000-000000000001",
            "email": "seokhwan.son@gmail.com",
            "nickname": "손석환",
            "birth_year": 1999,
            "survey_scores": {
                "TDS": 70, "SBS": 60, "EBS": 50, "VOS": 65, "SMS": 80, "UAS": 55
            }
        }

    def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"[MockDB] Inserting/Upserting into {table}: {list(data.keys())}")
        if table == "profiles":
            self.profiles[data["id"]] = data
        elif table == "raw_file":
            self.raw_files[data["id"]] = data
        elif table == "norm_event":
            self.norm_events[data["id"]] = data
        elif table == "session_text":
            self.session_texts[data["id"]] = data
        elif table == "nlp_result":
            self.nlp_results[data["id"]] = data
        elif table == "score_run":
            self.score_runs[data["run_id"]] = data
        elif table == "score_axis":
            self.score_axes[f"{data['run_id']}_{data['axis_code']}"] = data
        elif table == "detox_plan":
            self.detox_plans[data["plan_id"]] = data
        elif table == "mission_log":
            self.mission_logs[data["log_id"]] = data
        elif table == "audit_log":
            self.audit_logs.append(data)
        return data

    def select(self, table: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        logger.info(f"[MockDB] Selecting from {table} with filters {filters}")
        
        # Exact table stores mapping to resolve plurals / name mismatches
        TABLE_STORES = {
            "profiles": "profiles",
            "raw_file": "raw_files",
            "norm_event": "norm_events",
            "session_text": "session_texts",
            "nlp_result": "nlp_results",
            "score_run": "score_runs",
            "score_axis": "score_axes",
            "detox_plan": "detox_plans",
            "mission_log": "mission_logs",
            "audit_log": "audit_logs",
        }
        
        mapped_store_name = TABLE_STORES.get(table)
        if mapped_store_name:
            store = getattr(self, mapped_store_name, None)
        else:
            store = getattr(self, f"{table}s" if not table.endswith("y") else f"{table[:-1]}ies", None)
            
        if store is None and table == "audit_log":
            store = self.audit_logs
            
        if isinstance(store, list):
            return store
            
        results = list(store.values()) if store else []
        if filters:
            for key, val in filters.items():
                results = [r for r in results if r.get(key) == val]
        return results

mock_db = MockDatabaseStore()

class DatabaseClient:
    def __init__(self):
        self.supabase_url = settings.SUPABASE_URL
        self.supabase_key = settings.SUPABASE_KEY
        self.is_mock = self.supabase_url == "https://your-supabase-url.supabase.co"
        self.client = None
        
        if not self.is_mock:
            try:
                from supabase import create_client
                self.client = create_client(self.supabase_url, self.supabase_key)
                logger.info("Supabase client initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to connect to Supabase: {e}. Falling back to Mock DB.")
                self.is_mock = True

    def save_data(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Saves a row of data into Supabase (upsert) or falls back to local MockDB."""
        if self.is_mock or not self.client:
            return mock_db.insert(table, data)
        try:
            res = self.client.table(table).upsert(data).execute()
            # Supabase response object has data field
            if hasattr(res, "data") and res.data:
                return res.data[0]
            return data
        except Exception as e:
            logger.warning(f"Supabase write (upsert) failed on {table}: {e}. Saving to local memory instead.")
            return mock_db.insert(table, data)

    def fetch_data(self, table: str, query_filter: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Fetches rows of data from Supabase or falls back to local MockDB."""
        if self.is_mock or not self.client:
            return mock_db.select(table, query_filter)
        try:
            q = self.client.table(table).select("*")
            if query_filter:
                for k, v in query_filter.items():
                    q = q.eq(k, v)
            res = q.execute()
            if hasattr(res, "data"):
                return res.data
            return []
        except Exception as e:
            logger.warning(f"Supabase select failed on {table}: {e}. Reading from local memory instead.")
            return mock_db.select(table, query_filter)

db_client = DatabaseClient()
