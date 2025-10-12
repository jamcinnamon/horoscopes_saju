"""
Date and time utilities
"""
from datetime import datetime, date, time, timedelta
from typing import Optional


def get_zodiac_sign(birth_date: date) -> str:
    """
    Calculate zodiac sign from birth date
    
    Args:
        birth_date: Date of birth
        
    Returns:
        Zodiac sign name
    """
    month = birth_date.month
    day = birth_date.day
    
    # Zodiac date ranges
    if (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "Aries"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "Taurus"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
        return "Gemini"
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
        return "Cancer"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "Leo"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "Virgo"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return "Libra"
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return "Scorpio"
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
        return "Sagittarius"
    elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
        return "Capricorn"
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "Aquarius"
    else:  # (month == 2 and day >= 19) or (month == 3 and day <= 20)
        return "Pisces"


def get_current_year() -> int:
    """Get current year"""
    return datetime.now().year


def get_today() -> date:
    """Get today's date"""
    return date.today()


def format_date_korean(dt: date) -> str:
    """
    Format date in Korean style
    
    Args:
        dt: Date to format
        
    Returns:
        Formatted date string (e.g., "2024년 1월 15일")
    """
    return f"{dt.year}년 {dt.month}월 {dt.day}일"


def get_date_range(start_date: date, days: int) -> list:
    """
    Get list of dates in range
    
    Args:
        start_date: Starting date
        days: Number of days
        
    Returns:
        List of dates
    """
    return [start_date + timedelta(days=i) for i in range(days)]


def is_valid_birth_date(birth_date: date) -> bool:
    """
    Validate birth date
    
    Args:
        birth_date: Date to validate
        
    Returns:
        True if valid, False otherwise
    """
    today = date.today()
    
    # Cannot be in the future
    if birth_date > today:
        return False
    
    # Should be after 1900
    if birth_date.year < 1900:
        return False
    
    # Should not be more than 150 years ago
    if (today.year - birth_date.year) > 150:
        return False
    
    return True


def parse_time_string(time_str: str) -> Optional[time]:
    """
    Parse time string
    
    Args:
        time_str: Time string (e.g., "14:30", "2:30 PM")
        
    Returns:
        time object or None
    """
    formats = [
        "%H:%M",        # 14:30
        "%H:%M:%S",     # 14:30:00
        "%I:%M %p",     # 2:30 PM
        "%I:%M:%S %p",  # 2:30:00 PM
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(time_str, fmt)
            return dt.time()
        except ValueError:
            continue
    
    return None
