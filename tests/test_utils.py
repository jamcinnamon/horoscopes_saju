"""
Test utility functions
"""
import pytest
from datetime import date, time
from app.utils import (
    clean_text,
    get_zodiac_sign,
    validate_horoscope_text,
    is_valid_birth_date,
    parse_time_string,
)


def test_clean_text():
    """Test text cleaning"""
    assert clean_text("  Hello   World  ") == "Hello World"
    assert clean_text("nan") == ""
    assert clean_text("Test\n\nText") == "Test Text"


def test_get_zodiac_sign():
    """Test zodiac sign calculation"""
    assert get_zodiac_sign(date(1990, 5, 15)) == "Taurus"
    assert get_zodiac_sign(date(1990, 3, 25)) == "Aries"
    assert get_zodiac_sign(date(1990, 12, 25)) == "Capricorn"
    assert get_zodiac_sign(date(1990, 1, 15)) == "Capricorn"
    assert get_zodiac_sign(date(1990, 7, 25)) == "Leo"


def test_validate_horoscope_text():
    """Test horoscope text validation"""
    assert validate_horoscope_text("This is a valid horoscope text") == True
    assert validate_horoscope_text("nan") == False
    assert validate_horoscope_text("") == False
    assert validate_horoscope_text("short") == False


def test_is_valid_birth_date():
    """Test birth date validation"""
    assert is_valid_birth_date(date(1990, 5, 15)) == True
    assert is_valid_birth_date(date(2050, 1, 1)) == False  # Future
    assert is_valid_birth_date(date(1850, 1, 1)) == False  # Too old
    assert is_valid_birth_date(date.today()) == True


def test_parse_time_string():
    """Test time string parsing"""
    assert parse_time_string("14:30") == time(14, 30)
    assert parse_time_string("2:30 PM") == time(14, 30)
    assert parse_time_string("invalid") is None
