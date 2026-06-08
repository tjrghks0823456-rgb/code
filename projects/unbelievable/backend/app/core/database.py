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
        
        url = self.supabase_url or ""
        key = self.supabase_key or ""
        
        is_placeholder_url = (
            not url or
            "your-supabase-url" in url or
            "your-project-ref" in url
        )
        is_placeholder_key = (
            not key or
            "your-supabase-anon-key" in key or
            "your-supabase-secret-key" in key
        )
        
        self.is_mock = is_placeholder_url or is_placeholder_key
        self.client = None
        
        if not self.is_mock:
            try:
                from supabase import create_client
                self.client = create_client(url, key)
                logger.info("Supabase client initialized successfully.")
            except Exception as e:
                # Log without printing settings.SUPABASE_KEY or settings.SUPABASE_URL to prevent leaks
                logger.error("Failed to connect to Supabase: connection error. Falling back to Mock DB.")
                self.is_mock = True

    def save_data(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Saves a row of data into Supabase (upsert) or falls back to local MockDB."""
        # Auto-pruning extra keys not in database schema to prevent PostgREST columns-not-found errors
        TABLE_COLUMNS = {
            "profiles": ["id", "email", "nickname", "birth_year", "survey_scores", "survey_result", "raw_survey", "created_at"],
            "raw_file": ["id", "user_id", "storage_path", "upload_status", "excluded_ad_count", "skipped_sources_with_reason", "ad_skip_summary", "data_coverage", "created_at"],
            "norm_event": ["id", "file_id", "event_time", "time_delta_sec", "video_duration_sec", "text_base", "platform", "action_type", "source_surface", "source_type", "content_format", "intent_level", "raw_time", "video_id", "channel_name", "channel_url", "title_url", "source_confidence", "is_duration_estimated", "estimated_duration_sec", "raw_item"],
            "session_text": ["id", "file_id", "aggregated_text", "token_count", "event_count", "start_time", "end_time"],
            "nlp_result": ["id", "session_id", "categories_json", "sentiment_score", "sentiment_magnitude", "language_code", "nlp_provider", "local_category", "category_confidence", "category_candidates", "category_source", "keywords_json", "created_at"],
            "score_run": ["run_id", "user_id", "file_id", "bias_risk_score", "weighted_health", "mbti_type", "exception_codes", "sampling_metadata", "data_quality_flags", "information_bias_risk", "shorts_stimulation_risk", "final_detox_risk", "shorts_analysis", "analyzed_at"],
            "score_axis": ["axis_id", "run_id", "axis_code", "axis_value", "axis_grade", "created_at"],
            "detox_plan": ["plan_id", "run_id", "user_id", "reverse_queries", "mission_json", "created_at"],
            "mission_log": ["log_id", "plan_id", "mission_item_id", "completed_yn", "completed_at"],
            "audit_log": ["id", "event_type", "target_id", "status_code", "latency_ms", "provider", "error_code", "created_at"],
            "content_classification_feedback": ["id", "user_id", "event_id", "content_text", "predicted_category_l1", "predicted_category_l2", "corrected_category_l1", "corrected_category_l2", "confidence", "feedback_reason", "created_at"]
        }
        
        pruned_data = data
        if table in TABLE_COLUMNS:
            valid_cols = set(TABLE_COLUMNS[table])
            pruned_data = {k: v for k, v in data.items() if k in valid_cols}

        if self.is_mock or not self.client:
            logger.info(f"[Storage] Saved {table} to MockDB (In-memory).")
            result = mock_db.insert(table, data)
            result["__storage"] = "MockDB"
            return result
        try:
            res = self.client.table(table).upsert(pruned_data).execute()
            if hasattr(res, "data") and res.data:
                logger.info(f"[Storage] Successfully saved {table} to Supabase Cloud.")
                result = res.data[0]
                result["__storage"] = "Supabase"
                return result
            logger.info(f"[Storage] Saved {table} to Supabase Cloud (no returned data).")
            data["__storage"] = "Supabase"
            return data
        except Exception as e:
            logger.error(f"[Storage] SUPABASE WRITE FAILED on {table}: {e}. Falling back to local MockDB!")
            result = mock_db.insert(table, data)
            result["__storage"] = "MockDB-Fallback"
            return result

    def fetch_data(self, table: str, query_filter: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Fetches rows of data from Supabase or falls back to local MockDB."""
        if self.is_mock or not self.client:
            results = mock_db.select(table, query_filter)
            for r in results:
                if isinstance(r, dict):
                    r["__storage"] = "MockDB"
            return results
        try:
            q = self.client.table(table).select("*")
            if query_filter:
                for k, v in query_filter.items():
                    q = q.eq(k, v)
            res = q.execute()
            if hasattr(res, "data"):
                results = res.data
                for r in results:
                    if isinstance(r, dict):
                        r["__storage"] = "Supabase"
                return results
            return []
        except Exception as e:
            logger.warning(f"Supabase select failed on {table}: {e}. Reading from local memory instead.")
            results = mock_db.select(table, query_filter)
            for r in results:
                if isinstance(r, dict):
                    r["__storage"] = "MockDB-Fallback"
            return results

db_client = DatabaseClient()
