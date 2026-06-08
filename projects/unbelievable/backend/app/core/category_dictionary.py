# -*- coding: utf-8 -*-
import re
from app.core.category_loader import category_loader

CATEGORY_DICT_VERSION = "2.0-json-loader"

# Dynamically loaded configurations from JSON dictionaries
CATEGORY_DICT = category_loader.category_dict
STOP_WORDS = category_loader.stop_words
UNSTABLE_WORDS = category_loader.unstable_words
STIMULUS_WORDS = category_loader.stimulus_words
YOUTUBE_CATEGORY_MAP = category_loader.youtube_category_map

DATE_PATTERN = re.compile(r'^\d{1,4}[-./]\d{1,2}([-./]\d{1,4})?$')
ALLOWED_2LETTER_ENG = {"AI", "IT", "UI", "UX", "VR", "AR", "IP", "DB", "PC", "OS", "VS", "ML", "DL"}
