# -*- coding: utf-8 -*-
import os
import sys
import logging
from collections import Counter
from app.core.config import settings
from app.core.category_dictionary import (
    UNSTABLE_WORDS,
    STIMULUS_WORDS
)
from app.core.text_cleaning import clean_and_filter_keyword

logger = logging.getLogger(__name__)

_okt = None

def get_okt():
    global _okt
    if _okt is None:
        try:
            import platform
            is_windows = platform.system() == "Windows"
            
            if is_windows:
                import ctypes
                def get_short_path(long_path):
                    try:
                        buf = ctypes.create_unicode_buffer(1024)
                        ctypes.windll.kernel32.GetShortPathNameW(long_path, buf, 1024)
                        return buf.value if buf.value else long_path
                    except Exception:
                        return long_path
                new_paths = []
                for p in sys.path:
                    if " " in p:
                        new_paths.append(get_short_path(p))
                    else:
                        new_paths.append(p)
                sys.path = new_paths
                
                # Use environment variable JAVA_HOME first, fallback to default path
                java_home = os.environ.get("JAVA_HOME", r"C:\Program Files\Eclipse Adoptium\jdk-17.0.18.8-hotspot")
                if os.path.exists(java_home):
                    short_java = get_short_path(java_home)
                    os.environ["JAVA_HOME"] = short_java
                    os.environ["PATH"] = (
                        os.path.join(short_java, "bin") + os.pathsep +
                        os.path.join(short_java, "bin", "server") + os.pathsep +
                        os.environ.get("PATH", "")
                    )
                else:
                    logger.warning(f"Java not found at expected path: {java_home}. Please check JAVA_HOME configuration.")
                
                old_cwd = os.getcwd()
                win_temp = os.environ.get("USERPROFILE", os.environ.get("TEMP", "C:\\"))
                safe_cwd = get_short_path(win_temp)
                try:
                    if os.path.exists(safe_cwd):
                        os.chdir(safe_cwd)
                    from konlpy.tag import Okt
                    _okt = Okt()
                except (ImportError, RuntimeError) as e:
                    logger.warning(f"KoNLPy import or JVM initialization failed on Windows. Native fallbacks will be used. Error details: {str(e)}")
                    _okt = None
                finally:
                    os.chdir(old_cwd)
            else:
                try:
                    from konlpy.tag import Okt
                    _okt = Okt()
                except (ImportError, RuntimeError) as e:
                    logger.warning(f"KoNLPy import or JVM initialization failed on Linux/Mac. Native fallbacks will be used. Error details: {str(e)}")
                    _okt = None
        except Exception as e:
            logger.error(f"Uncaught exception during Okt tagger setup: {str(e)}", exc_info=True)
            _okt = None
    return _okt

def extract_keywords_fallback(text, num_keywords=10):
    if not text:
        return []
    try:
        okt = get_okt()
        if okt is None:
            raw_words = text.split()
            valid_words = []
            for w in raw_words:
                cleaned = clean_and_filter_keyword(w)
                if cleaned:
                    valid_words.append(cleaned)
            return Counter(valid_words).most_common(num_keywords)
        nouns = okt.nouns(text)
        valid_nouns = []
        for noun in nouns:
            cleaned = clean_and_filter_keyword(noun)
            if cleaned:
                valid_nouns.append(cleaned)
        count = Counter(valid_nouns)
        return count.most_common(num_keywords)
    except Exception as e:
        logger.warning(f"Fallback keyword extraction failed: {e}")
        # Simplest space split fallback
        raw_words = text.split()
        valid_words = []
        for w in raw_words:
            cleaned = clean_and_filter_keyword(w)
            if cleaned:
                valid_words.append(cleaned)
        return Counter(valid_words).most_common(num_keywords)

def analyze_sentiment_and_stimulus_fallback(text):
    if not text:
        return 1.0, 1.0
    unstable_count = sum(text.count(word) for word in UNSTABLE_WORDS)
    stimulus_count = sum(text.count(word) for word in STIMULUS_WORDS)
    stability_factor = max(0.1, 1.0 - (unstable_count * 0.10))
    safety_factor = max(0.1, 1.0 - (stimulus_count * 0.12))
    return stability_factor, safety_factor

def analyze_text_with_gcp(text, language_hint="ko"):
    if not text or not text.strip():
        return None
    try:
        # Use Google Cloud Language v2 API key if configured
        api_key = settings.GOOGLE_LANGUAGE_API_KEY
        if not api_key or api_key == "mock-nl-api-key":
            return None
        
        # Load google.cloud.language Client Option and Client
        from google.cloud import language_v2
        client = language_v2.LanguageServiceClient(client_options={"api_key": api_key})
        document = language_v2.Document(
            content=text,
            type_=language_v2.Document.Type.PLAIN_TEXT
        )
        word_count = len(text.split())
        features = {
            "extract_entities": True,
            "extract_document_sentiment": True,
            "moderate_text": True,
            "classify_text": word_count >= 20
        }
        response = client.annotate_text(
            request={
                "document": document,
                "features": features
            }
        )
        res_dict = type(response).to_dict(response)
        sentiment_data = res_dict.get("document_sentiment", {})
        sentiment_score = sentiment_data.get("score", 0.0)
        sentiment_magnitude = sentiment_data.get("magnitude", 0.0)
        entities = [
            {"name": e.get("name"), "type": e.get("type"), "salience": e.get("salience", 0.0)}
            for e in res_dict.get("entities", [])
        ]
        categories = [
            {"name": c.get("name"), "confidence": c.get("confidence", 0.0)}
            for c in res_dict.get("categories", [])
        ]
        moderation_categories = [
            {"name": m.get("name"), "confidence": m.get("confidence", 0.0)}
            for m in res_dict.get("moderation_categories", [])
        ]
        return {
            "documentSentiment": {
                "score": sentiment_score,
                "magnitude": sentiment_magnitude
            },
            "entities": entities,
            "categories": categories,
            "moderationCategories": moderation_categories,
            "language_code": res_dict.get("language_code", "ko")
        }
    except Exception as e:
        logger.warning(f"GCP NLP API call failed: {e}")
        return None

def analyze_session_text(text):
    from app.core.category_classifier import classify_text_by_keywords, map_gcp_category_to_local

    gcp_res = analyze_text_with_gcp(text)
    if gcp_res:
        entities = gcp_res["entities"]
        keywords = []
        for e in entities:
            name = e["name"]
            if e.get("type") in ["NUMBER", "PRICE", "DATE", "PHONE_NUMBER"]:
                continue
            cleaned = clean_and_filter_keyword(name)
            if not cleaned:
                continue
            keywords.append((cleaned, int(e["salience"] * 100)))
            if len(keywords) >= 10:
                break
        category = "❓ 기타/미분류"
        if gcp_res.get("categories"):
            sorted_cats = sorted(gcp_res["categories"], key=lambda x: x["confidence"], reverse=True)
            category = map_gcp_category_to_local(sorted_cats[0]["name"])
        else:
            category = classify_text_by_keywords(keywords)
        score = gcp_res["documentSentiment"]["score"]
        stability_factor = max(0.1, 1.0 - max(0.0, -score) * 0.8)
        max_mod_confidence = 0.0
        bad_categories = ["Toxic", "Insult", "Profanity", "Violence", "Hate Speech", "Harassment", "Derogatory", "Sexual"]
        for cat in gcp_res.get("moderationCategories", []):
            if cat["name"] in bad_categories:
                max_mod_confidence = max(max_mod_confidence, cat["confidence"])
        safety_factor = max(0.1, 1.0 - max_mod_confidence * 1.2)
        return keywords, category, stability_factor, safety_factor, gcp_res
    else:
        keywords = extract_keywords_fallback(text)
        category = classify_text_by_keywords(keywords)
        stability_factor, safety_factor = analyze_sentiment_and_stimulus_fallback(text)
        return keywords, category, stability_factor, safety_factor, None

def analyze_session_text_advanced(session: dict) -> tuple:
    from app.core.category_classifier import classify_session_advanced

    session_text = session.get("session_text", "")
    events = session.get("events", [])
    
    res = classify_session_advanced(events, session_text)
    
    gcp_res = analyze_text_with_gcp(session_text)
    if gcp_res:
        score = gcp_res["documentSentiment"]["score"]
        stability_factor = max(0.1, 1.0 - max(0.0, -score) * 0.8)
        max_mod_confidence = 0.0
        bad_categories = ["Toxic", "Insult", "Profanity", "Violence", "Hate Speech", "Harassment", "Derogatory", "Sexual"]
        for cat in gcp_res.get("moderationCategories", []):
            if cat["name"] in bad_categories:
                max_mod_confidence = max(max_mod_confidence, cat["confidence"])
        safety_factor = max(0.1, 1.0 - max_mod_confidence * 1.2)
    else:
        stability_factor, safety_factor = analyze_sentiment_and_stimulus_fallback(session_text)
        
    keywords = []
    if gcp_res:
        entities = gcp_res["entities"]
        for e in entities:
            name = e["name"]
            if e.get("type") in ["NUMBER", "PRICE", "DATE", "PHONE_NUMBER"]:
                continue
            cleaned = clean_and_filter_keyword(name)
            if not cleaned:
                continue
            keywords.append((cleaned, int(e["salience"] * 100)))
            if len(keywords) >= 10:
                break
    else:
        keywords = extract_keywords_fallback(session_text)
        
    return keywords, res, stability_factor, safety_factor, gcp_res
