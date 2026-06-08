# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__name__)

def get_summary_transcript(video_id: str, front_mins: float = 1.5, back_mins: float = 1.0) -> str:
    if not video_id:
        return ""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript(['ko']).fetch()
        if not transcript:
            return ""
        last_entry = transcript[-1]
        total_duration = last_entry['start'] + last_entry['duration']
        front_seconds = front_mins * 60
        back_start_time = total_duration - (back_mins * 60)
        extracted_text = []
        for entry in transcript:
            start_time = entry['start']
            if start_time <= front_seconds or start_time >= back_start_time:
                clean_text = entry['text'].replace('\n', ' ')
                extracted_text.append(clean_text)
        return " ".join(extracted_text)
    except Exception as e:
        logger.debug(f"Transcript extraction skipped or failed for video {video_id}: {e}")
        return ""
