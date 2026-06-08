# -*- coding: utf-8 -*-
import unicodedata
from app.core.category_dictionary import (
    CATEGORY_DICT,
    YOUTUBE_CATEGORY_MAP
)

def map_topic_category_url(url: str) -> str:
    if not url:
        return None
    url_lower = url.lower()
    if "gaming" in url_lower or "game" in url_lower:
        return "🎮 게임"
    elif "music" in url_lower or "singing" in url_lower or "song" in url_lower:
        return "🎵 음악"
    elif "sport" in url_lower or "football" in url_lower or "baseball" in url_lower or "basketball" in url_lower or "cricket" in url_lower:
        return "⚽ 스포츠"
    elif "politics" in url_lower or "society" in url_lower or "news" in url_lower or "social" in url_lower:
        return "⚖️ 뉴스/정치/사회"
    elif "technology" in url_lower or "computing" in url_lower or "software" in url_lower or "hardware" in url_lower:
        return "💻 IT/테크"
    elif "finance" in url_lower or "economics" in url_lower or "business" in url_lower:
        return "📈 경제/금융"
    elif "real_estate" in url_lower or "property" in url_lower:
        return "🏠 부동산"
    elif "automotive" in url_lower or "car" in url_lower or "vehicle" in url_lower:
        return "🚗 자동차"
    elif "fashion" in url_lower or "beauty" in url_lower or "cosmetics" in url_lower or "clothing" in url_lower:
        return "💄 뷰티/패션"
    elif "food" in url_lower or "cooking" in url_lower or "recipe" in url_lower or "cuisine" in url_lower:
        return "🍳 먹방/요리"
    elif "entertainment" in url_lower or "variety" in url_lower or "television" in url_lower or "comedy" in url_lower or "humor" in url_lower:
        return "🍿 엔터/예능"
    elif "science" in url_lower or "education" in url_lower or "history" in url_lower or "philosophy" in url_lower or "academic" in url_lower:
        return "🔬 과학/지식"
    elif "lifestyle" in url_lower or "hobby" in url_lower or "pet" in url_lower or "animal" in url_lower or "travel" in url_lower:
        return "🛠️ 취미/일상"
    return None

def classify_text_by_keywords(keywords) -> str:
    if not keywords:
        return "❓ 기타/미분류"
    scores = {category: 0.0 for category in CATEGORY_DICT.keys()}
    for item in keywords:
        # keywords can be a list of tuples (word, count) or a list of words
        if isinstance(item, tuple):
            word, count = item
        else:
            word, count = item, 1
        word_lower = word.lower()
        for category, dict_words in CATEGORY_DICT.items():
            for dw in dict_words:
                if dw.lower() in word_lower:
                    scores[category] += count
    best_category = max(scores, key=scores.get)
    if scores[best_category] < 0.1:
        return "❓ 기타/미분류"
    return best_category

def map_gcp_category_to_local(gcp_cat: str) -> str:
    if not gcp_cat:
        return "❓ 기타/미분류"
    gcp_cat = gcp_cat.lower()
    if "games" in gcp_cat:
        return "🎮 게임"
    elif "finance" in gcp_cat or "business" in gcp_cat:
        return "📈 경제/금융"
    elif "real estate" in gcp_cat:
        return "🏠 부동산"
    elif "computer" in gcp_cat or "internet" in gcp_cat or "technology" in gcp_cat:
        return "💻 IT/테크"
    elif "science" in gcp_cat:
        return "🔬 과학/지식"
    elif "education" in gcp_cat or "reference" in gcp_cat or "books" in gcp_cat:
        return "📖 공부/입시"
    elif "health" in gcp_cat or "fitness" in gcp_cat:
        return "🏋️ 건강/운동"
    elif "sports" in gcp_cat:
        return "⚽ 스포츠"
    elif "music" in gcp_cat or "singing" in gcp_cat:
        return "🎵 음악"
    elif "autos" in gcp_cat or "vehicle" in gcp_cat:
        return "🚗 자동차"
    elif "beauty" in gcp_cat or "fashion" in gcp_cat:
        return "💄 뷰티/패션"
    elif "food" in gcp_cat or "cooking" in gcp_cat:
        return "🍳 먹방/요리"
    elif "news" in gcp_cat or "politics" in gcp_cat or "society" in gcp_cat:
        return "⚖️ 뉴스/정치/사회"
    elif "movie" in gcp_cat or "television" in gcp_cat or "entertainment" in gcp_cat:
        return "🍿 엔터/예능"
    elif "lifestyle" in gcp_cat or "hobbies" in gcp_cat or "pets" in gcp_cat:
        return "🛠️ 취미/일상"
    elif "shopping" in gcp_cat:
        return "🛒 쇼핑/소비"
    return "❓ 기타/미분류"

def classify_session_advanced(events, session_text) -> dict:
    from app.core.nlp_enhanced import extract_keywords_fallback

    tags = []
    topic_categories = []
    category_ids = []
    channel_names = []
    titles = []
    
    for ev in events:
        if ev.get("action_type") == "view" or ev.get("event_type") == "watch":
            # standard Takeout normalizes topicCategories / tags as list
            ev_tags = ev.get("tags")
            if ev_tags:
                if isinstance(ev_tags, str):
                    tags.append(ev_tags)
                elif isinstance(ev_tags, list):
                    tags.extend(ev_tags)
            ev_topic_cats = ev.get("topicCategories")
            if ev_topic_cats:
                if isinstance(ev_topic_cats, str):
                    topic_categories.append(ev_topic_cats)
                elif isinstance(ev_topic_cats, list):
                    topic_categories.extend(ev_topic_cats)
            if ev.get("categoryId"):
                category_ids.append(str(ev["categoryId"]))
            # Support both channel_name and author_id (Takeout uses subtitles.name or channel_name)
            channel = ev.get("channel_name") or ev.get("author_id")
            if channel:
                channel_names.append(channel)
            title = ev.get("title") or ev.get("text_base")
            if title:
                titles.append(title)
                
    tags = [unicodedata.normalize('NFC', str(t)) for t in tags]
    topic_categories = [unicodedata.normalize('NFC', str(tc)) for tc in topic_categories]
    category_ids = [unicodedata.normalize('NFC', str(cid)) for cid in category_ids]
    channel_names = [unicodedata.normalize('NFC', str(cn)) for cn in channel_names]
    titles = [unicodedata.normalize('NFC', str(t)) for t in titles]
    session_text = unicodedata.normalize('NFC', session_text)
    
    candidates = {}
    
    def add_score(cat_name, amount):
        candidates[cat_name] = candidates.get(cat_name, 0.0) + amount

    # Step 1: YouTube categoryId
    for cid in category_ids:
        mapped = YOUTUBE_CATEGORY_MAP.get(cid)
        if mapped:
            add_score(mapped, 3.0)
            
    # Step 2: YouTube topicCategories
    for url in topic_categories:
        mapped = map_topic_category_url(url)
        if mapped:
            add_score(mapped, 2.5)
            
    # Step 3: YouTube tags matching against CATEGORY_DICT
    for tag in tags:
        tag_lower = tag.lower()
        for cat, dict_words in CATEGORY_DICT.items():
            for dw in dict_words:
                if dw.lower() in tag_lower:
                    add_score(cat, 0.8)
                    
    # Step 4: Video title keywords matching against CATEGORY_DICT
    keywords = extract_keywords_fallback(session_text, num_keywords=15)
    for word, count in keywords:
        word_lower = word.lower()
        for cat, dict_words in CATEGORY_DICT.items():
            for dw in dict_words:
                if dw.lower() in word_lower:
                    add_score(cat, 0.5 * count)
                    
    # Step 5: Channel names matching against CATEGORY_DICT
    for cn in channel_names:
        cn_lower = cn.lower()
        for cat, dict_words in CATEGORY_DICT.items():
            for dw in dict_words:
                if dw.lower() in cn_lower:
                    add_score(cat, 0.6)

    sorted_candidates = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
    
    if sorted_candidates and sorted_candidates[0][1] > 0.1:
        best_cat = sorted_candidates[0][0]
        total_score = sum(candidates.values())
        confidence = round(sorted_candidates[0][1] / total_score, 2) if total_score > 0 else 1.0
        candidate_list = [{"name": name, "score": round(score, 2)} for name, score in sorted_candidates[:3]]
        
        return {
            "category": best_cat,
            "category_confidence": confidence,
            "category_source": "rule_based_metadata",
            "category_candidates": candidate_list,
            "is_uncategorized": False,
            "fallback_reason": None,
            "category_version": "2.0"
        }
    
    return {
        "category": "❓ 기타/미분류",
        "category_confidence": 0.0,
        "category_source": "fallback_failed",
        "category_candidates": [],
        "is_uncategorized": True,
        "fallback_reason": "no_metadata_or_keyword_match",
        "category_version": "2.0"
    }
