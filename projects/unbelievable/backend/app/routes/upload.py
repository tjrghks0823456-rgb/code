import logging
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.core.config import settings, DEFAULT_MVP_USER_ID
from app.services.upload_service import UploadService
from app.parsers.takeout_parser import classify_takeout_file, is_supported_takeout_file, scan_youtube_files_from_zip

logger = logging.getLogger(__name__)
router = APIRouter()
upload_service = UploadService()


@router.post("/upload")
async def upload_file(
    user_id: str = DEFAULT_MVP_USER_ID,
    platform: str = "youtube",
    action_type: str = "view",
    file: UploadFile = File(...),
    mock_estimation: bool = False
):
    """
    Standard single history file upload route. Delegates orchestration to UploadService.
    """
    try:
        content = await file.read()
        text_content = content.decode("utf-8", errors="ignore")
        return upload_service.upload_single_file(
            user_id=user_id,
            platform=platform,
            action_type=action_type,
            filename=file.filename,
            text_content=text_content,
            mock_estimation=mock_estimation
        )
    except Exception as e:
        logger.error(f"Upload processing crash: {e}")
        raise HTTPException(status_code=500, detail=f"File upload and parsing failed: {str(e)}")


@router.post("/upload/takeout")
async def upload_takeout(
    user_id: str = DEFAULT_MVP_USER_ID,
    files: List[UploadFile] = File(default=None),
    paths: List[str] = Form(default=None),
    zip_file: UploadFile = File(default=None),
    survey_scores: Optional[str] = Form(default=None),
    mock_estimation: bool = Form(default=False)
):
    """
    Refined Takeout ZIP/folder upload route. delegates scanning to parsers and pipeline to UploadService.
    """
    try:
        logger.info("[upload/takeout] started")
        # 1. Merge-update survey scores via Service
        if survey_scores:
            upload_service.process_survey_scores(user_id, survey_scores)

        files_to_parse = []
        ignored_sources = []
        skipped_sources_with_reason = {}

        # 2. Gather candidates
        logger.info("[upload/takeout] file_scan_started")
        if zip_file:
            zip_content = await zip_file.read()
            zip_files, ignored_sources, skipped_sources_with_reason = scan_youtube_files_from_zip(zip_content)
            for zf in zip_files:
                files_to_parse.append({
                    "name": zf["filename"],
                    "content": zf["content"].decode("utf-8", errors="ignore"),
                    "kind": zf["kind"]
                })
        elif files:
            for idx, file in enumerate(files):
                rel_path = paths[idx] if (paths and idx < len(paths)) else file.filename
                kind = classify_takeout_file(rel_path)

                if kind == "music":
                    ignored_sources.append(rel_path)
                    skipped_sources_with_reason[rel_path] = "Excluded in MVP configuration (Music library/uploads)"
                    continue

                if not is_supported_takeout_file(rel_path):
                    continue

                content = await file.read()
                files_to_parse.append({
                    "name": rel_path,
                    "content": content.decode("utf-8", errors="ignore"),
                    "kind": kind
                })

        detected_files_str = ", ".join([f["name"] for f in files_to_parse])
        logger.info(f"[upload/takeout] file_scan_done detected_files={detected_files_str}")

        if not files_to_parse:
            raise HTTPException(
                status_code=400,
                detail="YouTube 시청/검색 기록 파일(watch-history.json/html, search-history.json/html)을 발견하지 못했습니다."
            )

        # 3. Delegate to service for limiting, parsing, filtering, and bulk saving
        logger.info("[upload/takeout] parse_started")
        res = upload_service.upload_takeout_flow(
            user_id=user_id,
            files_to_parse=files_to_parse,
            ignored_sources=ignored_sources,
            skipped_sources_with_reason=skipped_sources_with_reason,
            mock_estimation=mock_estimation
        )
        return res
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Takeout upload processing crash: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"File upload and parsing failed: {str(e)}")


@router.post("/upload/youtube-takeout")
async def upload_youtube_takeout(
    user_id: str = DEFAULT_MVP_USER_ID,
    files: List[UploadFile] = File(default=None),
    paths: List[str] = Form(default=None),
    zip_file: UploadFile = File(default=None),
    survey_scores: Optional[str] = Form(default=None),
    mock_estimation: bool = Form(default=False)
):
    """
    Deprecated endpoint forwarder for backward compatibility with testing scripts.
    """
    res = await upload_takeout(
        user_id=user_id,
        files=files,
        paths=paths,
        zip_file=zip_file,
        survey_scores=survey_scores,
        mock_estimation=mock_estimation
    )
    return res


@router.get("/youtube-test")
async def test_youtube_api(video_id: str = "dQw4w9WgXcQ"):
    """
    Diagnostics endpoint to test connection and parse responses from YouTube Data API.
    """
    from app.core.config import settings
    from app.core.youtube import parse_iso8601_duration
    import httpx

    api_key = settings.YOUTUBE_API_KEY
    if not api_key or api_key == "mock-youtube-api-key":
        logger.error("YouTube API key is missing or not configured.")
        raise HTTPException(
            status_code=400,
            detail="YouTube API Key가 설정되지 않았거나 유효하지 않습니다."
        )

    try:
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            "part": "snippet,contentDetails",
            "id": video_id,
            "key": api_key
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=5.0)

        if response.status_code != 200:
            logger.error(f"YouTube Data API test failed with HTTP {response.status_code}: {response.text}")
            raise HTTPException(
                status_code=response.status_code,
                detail=f"YouTube API 호출 실패 (HTTP {response.status_code})"
            )

        data = response.json()
        items = data.get("items", [])
        if not items:
            logger.warning(f"YouTube video {video_id} not found in test API call.")
            return {
                "success": False,
                "message": f"YouTube video ID '{video_id}' not found",
                "data": None
            }

        snippet = items[0].get("snippet", {})
        content_details = items[0].get("contentDetails", {})
        thumbnails = snippet.get("thumbnails", {})
        thumbnail_url = thumbnails.get("high", {}).get("url", "") or thumbnails.get("default", {}).get("url", "")

        return {
            "success": True,
            "message": "YouTube API connection successful",
            "data": {
                "video_id": video_id,
                "title": snippet.get("title", ""),
                "channel_title": snippet.get("channelTitle", ""),
                "category_id": snippet.get("categoryId", ""),
                "published_at": snippet.get("publishedAt", ""),
                "thumbnail_url": thumbnail_url,
                "duration_iso8601": content_details.get("duration", ""),
                "duration_sec": parse_iso8601_duration(content_details.get("duration", ""))
            }
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"YouTube Data API connection test crashed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="YouTube API 연결 테스트 중 서버 내부 에러가 발생했습니다."
        )
