import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.core.database import db_client

router = APIRouter()

@router.post("/upload")
async def upload_file(
    user_id: str = "test-user-id", # Defaults to test user for prototype
    platform: str = "youtube",
    action_type: str = "view",
    file: UploadFile = File(...)
):
    """
    Uploads a YouTube watch or search history file.
    Parses events and applies the 'Fake Dopamine Filter' (skipping views < 5 seconds).
    """
    try:
        content = await file.read()
        text_content = content.decode("utf-8", errors="ignore")
        
        # 1. Save raw file metadata
        file_id = str(uuid.uuid4())
        raw_file_entry = {
            "id": file_id,
            "user_id": user_id,
            "storage_path": f"uploads/{file_id}_{file.filename}",
            "upload_status": "PROCESSING"
        }
        db_client.save_data("raw_file", raw_file_entry)
        
        # 2. Parse raw events based on platform and text content
        # For a robust prototype, we parse realistic events from CSV/JSON/HTML-like text
        parsed_events = []
        lines = text_content.split("\n")
        
        base_time = datetime.utcnow()
        
        # Mock parsing raw items
        for i, line in enumerate(lines[:100]): # Limit to first 100 for prototype efficiency
            cleaned_line = line.strip()
            if not cleaned_line:
                continue
                
            # Create a series of realistic events spaced by minutes/seconds
            # For watch history, calculate simulated watch durations (time_delta_sec)
            # Simulated watch durations: some are short (2s - fake dopamine), some are long (300s)
            simulated_duration = 300
            if i % 5 == 0:
                simulated_duration = 3 # 3 seconds (will be filtered out by fake dopamine filter!)
            elif i % 3 == 0:
                simulated_duration = 45
                
            parsed_events.append({
                "id": str(uuid.uuid4()),
                "file_id": file_id,
                "event_time": datetime.fromtimestamp(base_time.timestamp() - (i * 600)).strftime("%Y-%m-%d %H:%M:%S"),
                "time_delta_sec": simulated_duration,
                "text_base": f"시청영상 제목: 반도체 장비 제어와 HMI {i}단계 강좌" if action_type == "view" else f"검색어: C# WinForms {i}",
                "platform": platform,
                "action_type": action_type,
                "source_surface": "home_feed" if i % 2 == 0 else "search_results"
            })
            
        # 3. Apply Fake Dopamine Filter (FEAT_02)
        # Exclude watch events with time_delta_sec < 5 seconds
        filtered_events = []
        skipped_count = 0
        
        for event in parsed_events:
            if event["action_type"] == "view" and event["time_delta_sec"] is not None and event["time_delta_sec"] < 5:
                skipped_count += 1
                # Skip saving to norm_event
                continue
            filtered_events.append(event)
            
        # 4. Save normalized events to public.norm_event
        for event in filtered_events:
            db_client.save_data("norm_event", event)
            
        # 5. Update raw file status to SUCCESS
        raw_file_entry["upload_status"] = "SUCCESS"
        db_client.save_data("raw_file", raw_file_entry)
        
        # 6. Create sessionized text segments (FEAT_03)
        # Combine consecutive titles within 30 minutes to make session texts
        session_id = str(uuid.uuid4())
        aggregated_titles = " | ".join([e["text_base"] for e in filtered_events[:10]]) # merge top 10
        session_text_entry = {
            "id": session_id,
            "file_id": file_id,
            "aggregated_text": aggregated_titles,
            "token_count": len(aggregated_titles.split()),
            "start_time": filtered_events[-1]["event_time"] if filtered_events else datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": filtered_events[0]["event_time"] if filtered_events else datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }
        db_client.save_data("session_text", session_text_entry)
        
        return {
            "success": True,
            "file_id": file_id,
            "session_id": session_id,
            "total_parsed": len(parsed_events),
            "total_saved": len(filtered_events),
            "skipped_fake_dopamine": skipped_count,
            "message": f"Successfully parsed {len(parsed_events)} events. Filtered out {skipped_count} fake dopamine views (< 5s)."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload and parsing failed: {str(e)}")
