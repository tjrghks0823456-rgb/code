"""Upload parser and duration inference settings.

These values keep the prototype predictable without hiding important limits
inside route code. Tune them here when the Takeout sample size grows.
"""

ZIP_LIMITS = {
    "max_file_count": 3000,
    "max_single_file_size": 30 * 1024 * 1024,
    "max_total_extract_size": 150 * 1024 * 1024,
}

PARSER_LIMITS = {
    "max_html_content_cells": 1000,
    "max_json_history_items": 1000,
    "max_html_links": 3000,
    "max_auxiliary_records": 1000,
    "max_csv_rows": 1000,
    "legacy_upload_json_items": 500,
    "legacy_upload_text_lines": 300,
}

DURATION_LIMITS = {
    "shorts_default_sec": 45,
    "standard_default_sec": 300,
    "default_estimated_watch_sec": 600,
    "search_default_sec": 15,
    "auxiliary_default_sec": 0,
    "min_watch_sec": 5,
    "max_timeline_gap_sec": 6 * 60 * 60,
    "idle_gap_threshold_sec": 30 * 60,
    "max_estimated_watch_sec_without_metadata": 30 * 60,
    "metadata_video_limit": 50,
}
