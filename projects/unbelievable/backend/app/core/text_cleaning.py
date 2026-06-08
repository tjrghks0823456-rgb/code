# -*- coding: utf-8 -*-
import re
from app.core.category_dictionary import (
    DATE_PATTERN,
    ALLOWED_2LETTER_ENG,
    STOP_WORDS
)

def clean_and_filter_keyword(word: str) -> str:
    if not word:
        return ""
    word_clean = word.strip(" \t\n\r#?![](),. \"'_-|~*+:;/\\&@<>{}")
    if len(word_clean) <= 1:
        return ""
    if "=" in word_clean:
        return ""
    if re.match(r'^[a-zA-Z0-9_-]{11}$', word_clean):
        if not (word_clean.isalpha() and word_clean.islower()):
            return ""
    if any(char in word_clean for char in ["-", "|", ":", "/", "\\"]):
        return ""
    if len(word_clean.split()) >= 3:
        return ""
    if len(word_clean) > 20:
        return ""
    if len(word_clean) >= 3:
        particles = ['은', '는', '이', '가', '을', '를', '의', '에', '도', '만', '과', '와', '로', '으로']
        for p in particles:
            if word_clean.endswith(p):
                stem = word_clean[:-len(p)]
                if all(ord('가') <= ord(c) <= ord('힣') for c in stem):
                    word_clean = stem
                    break
    if len(word_clean) <= 1:
        return ""
    if DATE_PATTERN.match(word_clean):
        return ""
    if word_clean.isdigit():
        return ""
    try:
        float(word_clean)
        return ""
    except ValueError:
        pass
    word_lower = word_clean.lower()
    if any(domain in word_lower for domain in [".com", ".net", ".org", "http", "www", "youtube", "co.kr"]):
        return ""
    if len(word_clean) == 2 and word_clean.isalpha() and word_clean.isascii():
        if word_clean.upper() not in ALLOWED_2LETTER_ENG:
            return ""
    if word_clean in STOP_WORDS or word_lower in STOP_WORDS:
        return ""
    if re.match(r'^\d+[화회부편탄분초]$', word_clean):
        return ""
    return word_clean
