"""
Text processing utilities for horoscope data
"""
import re
from datetime import datetime, date
from typing import Tuple, Optional


def clean_text(text: str) -> str:
    """
    Clean and normalize text
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    if not text or text.lower() == 'nan':
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters (keep basic punctuation)
    text = re.sub(r'[^\w\s.,!?;:\-\'\"()가-힣]', '', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def extract_lucky_info(horoscope_text: str) -> Tuple[str, Optional[str], Optional[int], Optional[str]]:
    """
    Extract lucky number and color from horoscope text
    
    Args:
        horoscope_text: Full horoscope text
        
    Returns:
        Tuple of (main_text, love_text, lucky_number, lucky_color)
    """
    lucky_number = None
    lucky_color = None
    love_text = None
    
    # Extract Love Focus
    love_match = re.search(r'Love Focus:\s*(.+?)(?:\n\n|\nLucky)', horoscope_text, re.IGNORECASE)
    if love_match:
        love_text = love_match.group(1).strip()
    
    # Extract Lucky Number
    number_match = re.search(r'Lucky Number:\s*(\d+)', horoscope_text, re.IGNORECASE)
    if number_match:
        lucky_number = int(number_match.group(1))
    
    # Extract Lucky Colour
    color_match = re.search(r'Lucky Colou?r:\s*(\w+)', horoscope_text, re.IGNORECASE)
    if color_match:
        lucky_color = color_match.group(1).strip()
    
    # Clean main horoscope text (remove Love Focus and Lucky info)
    main_text = re.sub(r'\n*Love Focus:.*', '', horoscope_text, flags=re.IGNORECASE | re.DOTALL)
    main_text = clean_text(main_text)
    
    return main_text, love_text, lucky_number, lucky_color


def parse_date_flexible(date_str: str) -> Optional[date]:
    """
    Parse date string with multiple format support
    
    Args:
        date_str: Date string in various formats
        
    Returns:
        datetime.date object or None if parsing fails
    """
    formats = [
        "%d-%b-%y",      # 01-Jan-24
        "%B %d, %Y",     # May 9, 2024
        "%b %d, %Y",     # Jan 1, 2025
        "%Y-%m-%d",      # 2024-01-15
        "%d/%m/%Y",      # 15/01/2024
        "%m/%d/%Y",      # 01/15/2024
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    return None


def normalize_zodiac_sign(sign: str) -> str:
    """
    Normalize zodiac sign name
    
    Args:
        sign: Zodiac sign name (may include date range)
        
    Returns:
        Normalized zodiac sign name
    """
    # Extract sign name from range (e.g., "Aries (March 21-April 20)" -> "Aries")
    sign = sign.split('(')[0].strip()
    
    # Capitalize first letter
    sign = sign.capitalize()
    
    return sign


def validate_horoscope_text(text: str) -> bool:
    """
    Validate if horoscope text is meaningful
    
    Args:
        text: Horoscope text to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not text:
        return False
    
    # Check for 'nan' or similar invalid values
    if text.lower() in ['nan', 'null', 'none', 'n/a']:
        return False
    
    # Check minimum length (at least 10 characters)
    if len(text.strip()) < 10:
        return False
    
    return True


def truncate_text(text: str, max_length: int = 500) -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    # Truncate at word boundary
    truncated = text[:max_length].rsplit(' ', 1)[0]
    return truncated + "..."


def extract_keywords(text: str, top_n: int = 5) -> list:
    """
    Extract keywords from text (simple frequency-based)
    
    Args:
        text: Text to extract keywords from
        top_n: Number of top keywords to return
        
    Returns:
        List of keywords
    """
    # Remove common words (simple stopwords)
    stopwords = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
        'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'should', 'could', 'may', 'might', 'must', 'can', 'your',
        'you', 'it', 'this', 'that', 'these', 'those'
    }
    
    # Tokenize and count
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())
    word_freq = {}
    
    for word in words:
        if word not in stopwords:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    
    return [word for word, freq in sorted_words[:top_n]]
