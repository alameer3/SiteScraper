"""Validation utilities"""
import re
from urllib.parse import urlparse

class URLValidator:
    @staticmethod
    def is_valid(url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

class DataValidator:
    @staticmethod
    def validate(data) -> bool:
        return data is not None