"""
Load existing horoscope data into database
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import re
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.models import Horoscope


def parse_date(date_str: str) -> datetime:
    """Parse date string to datetime object"""
    # Format: "01-Jan-24" -> 2024-01-01
    return datetime.strptime(date_str, "%d-%b-%y").date()


def extract_lucky_info(horoscope_text: str) -> tuple:
    """Extract lucky number and color from horoscope text"""
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
    main_text = main_text.strip()
    
    return main_text, love_text, lucky_number, lucky_color


def load_jsonl_data(file_path: str, db: Session) -> int:
    """Load data from JSONL file"""
    count = 0
    skipped = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
                
            data = json.loads(line)
            
            try:
                date = parse_date(data['date'])
                zodiac_sign = data['sign']
                
                # Check if already exists
                existing = db.query(Horoscope).filter(
                    Horoscope.date == date,
                    Horoscope.zodiac_sign == zodiac_sign
                ).first()
                
                if existing:
                    skipped += 1
                    continue
                
                # Extract information
                main_text, love_text, lucky_number, lucky_color = extract_lucky_info(data['horoscope'])
                
                # Create horoscope entry
                horoscope = Horoscope(
                    date=date,
                    zodiac_sign=zodiac_sign,
                    horoscope_text=main_text,
                    love_text=love_text,
                    lucky_number=lucky_number,
                    lucky_color=lucky_color,
                    source=data.get('source', 'Unknown')
                )
                
                db.add(horoscope)
                count += 1
                
                # Commit in batches
                if count % 100 == 0:
                    db.commit()
                    print(f"Loaded {count} records...")
                    
            except Exception as e:
                print(f"Error processing record: {e}")
                print(f"Data: {data}")
                continue
    
    db.commit()
    return count, skipped


def load_json_data(file_path: str, db: Session) -> int:
    """Load data from JSON file (data_stars.json format)"""
    count = 0
    skipped = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for date_str, signs_data in data.items():
        try:
            date = parse_date(date_str)
            
            for sign_range, sign_data in signs_data.items():
                # Extract sign name from range (e.g., "Aries (March 21-April 20)" -> "Aries")
                zodiac_sign = sign_range.split('(')[0].strip()
                
                # Check if already exists
                existing = db.query(Horoscope).filter(
                    Horoscope.date == date,
                    Horoscope.zodiac_sign == zodiac_sign
                ).first()
                
                if existing:
                    skipped += 1
                    continue
                
                horoscope = Horoscope(
                    date=date,
                    zodiac_sign=zodiac_sign,
                    horoscope_text=sign_data.get('horoscope', ''),
                    love_text=sign_data.get('love', ''),
                    lucky_number=sign_data.get('lucky_num') or None,
                    lucky_color=sign_data.get('lucky_color', ''),
                    source='data_stars.json'
                )
                
                db.add(horoscope)
                count += 1
                
                if count % 100 == 0:
                    db.commit()
                    print(f"Loaded {count} records...")
                    
        except Exception as e:
            print(f"Error processing date {date_str}: {e}")
            continue
    
    db.commit()
    return count, skipped


def main():
    """Main function to load all horoscope data"""
    print("🚀 Starting horoscope data loading...")
    
    # Initialize database
    print("Initializing database...")
    init_db()
    
    db = SessionLocal()
    total_loaded = 0
    total_skipped = 0
    
    try:
        # Load from horoscopes.jsonl
        jsonl_path = Path("horoscopes.jsonl")
        if jsonl_path.exists():
            print(f"\n📄 Loading from {jsonl_path}...")
            loaded, skipped = load_jsonl_data(str(jsonl_path), db)
            total_loaded += loaded
            total_skipped += skipped
            print(f"✅ Loaded {loaded} records, skipped {skipped} duplicates")
        
        # Load from data_stars.json
        json_path = Path("data_stars.json")
        if json_path.exists():
            print(f"\n📄 Loading from {json_path}...")
            loaded, skipped = load_json_data(str(json_path), db)
            total_loaded += loaded
            total_skipped += skipped
            print(f"✅ Loaded {loaded} records, skipped {skipped} duplicates")
        
        # Summary
        print(f"\n{'='*50}")
        print(f"✅ Data loading complete!")
        print(f"Total records loaded: {total_loaded}")
        print(f"Total duplicates skipped: {total_skipped}")
        print(f"{'='*50}")
        
        # Show statistics
        total_count = db.query(Horoscope).count()
        print(f"\n📊 Database statistics:")
        print(f"Total horoscope records: {total_count}")
        
        # Count by zodiac sign
        from sqlalchemy import func
        sign_counts = db.query(
            Horoscope.zodiac_sign,
            func.count(Horoscope.id)
        ).group_by(Horoscope.zodiac_sign).all()
        
        print(f"\nRecords by zodiac sign:")
        for sign, count in sorted(sign_counts):
            print(f"  {sign}: {count}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
