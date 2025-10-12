"""
Load existing horoscope data into MongoDB
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import re
import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from app.models.mongo import HoroscopeDocument
from app.database_mongo import connect_to_mongo, init_db


def parse_date(date_str: str) -> datetime:
    """Parse date string to datetime object"""
    # Try multiple formats
    formats = [
        "%d-%b-%y",  # 01-Jan-24
        "%B %d, %Y",  # May 9, 2024
        "%b %d, %Y",  # Jan 1, 2025
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    raise ValueError(f"Could not parse date: {date_str}")


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
    
    # Clean main horoscope text
    main_text = re.sub(r'\n*Love Focus:.*', '', horoscope_text, flags=re.IGNORECASE | re.DOTALL)
    main_text = main_text.strip()
    
    # Handle 'nan' values
    if main_text.lower() == 'nan' or not main_text:
        main_text = None
    
    return main_text, love_text, lucky_number, lucky_color


async def load_jsonl_data(file_path: str) -> int:
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
                existing = await HoroscopeDocument.find_one(
                    HoroscopeDocument.date == date,
                    HoroscopeDocument.zodiac_sign == zodiac_sign
                )
                
                if existing:
                    skipped += 1
                    continue
                
                # Extract information
                main_text, love_text, lucky_number, lucky_color = extract_lucky_info(data['horoscope'])
                
                if not main_text:
                    print(f"Skipping empty horoscope for {zodiac_sign} on {date}")
                    skipped += 1
                    continue
                
                # Create horoscope document
                horoscope = HoroscopeDocument(
                    date=date,
                    zodiac_sign=zodiac_sign,
                    horoscope_text=main_text,
                    love_text=love_text,
                    lucky_number=lucky_number,
                    lucky_color=lucky_color,
                    source=data.get('source', 'Unknown')
                )
                
                await horoscope.insert()
                count += 1
                
                if count % 100 == 0:
                    print(f"Loaded {count} records...")
                    
            except Exception as e:
                print(f"Error processing record: {e}")
                print(f"Data: {data}")
                continue
    
    return count, skipped


async def load_json_data(file_path: str) -> int:
    """Load data from JSON file (data_stars.json format)"""
    count = 0
    skipped = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for date_str, signs_data in data.items():
        try:
            date = parse_date(date_str)
            
            for sign_range, sign_data in signs_data.items():
                # Extract sign name
                zodiac_sign = sign_range.split('(')[0].strip()
                
                # Check if already exists
                existing = await HoroscopeDocument.find_one(
                    HoroscopeDocument.date == date,
                    HoroscopeDocument.zodiac_sign == zodiac_sign
                )
                
                if existing:
                    skipped += 1
                    continue
                
                horoscope_text = sign_data.get('horoscope', '')
                
                # Skip 'nan' or empty values
                if not horoscope_text or str(horoscope_text).lower() == 'nan':
                    skipped += 1
                    continue
                
                horoscope = HoroscopeDocument(
                    date=date,
                    zodiac_sign=zodiac_sign,
                    horoscope_text=horoscope_text,
                    love_text=sign_data.get('love', ''),
                    lucky_number=sign_data.get('lucky_num') or None,
                    lucky_color=sign_data.get('lucky_color', ''),
                    source='data_stars.json'
                )
                
                await horoscope.insert()
                count += 1
                
                if count % 100 == 0:
                    print(f"Loaded {count} records...")
                    
        except Exception as e:
            print(f"Error processing date {date_str}: {e}")
            continue
    
    return count, skipped


async def main():
    """Main function to load all horoscope data"""
    print("🚀 Starting horoscope data loading to MongoDB...")
    
    # Connect to MongoDB
    await connect_to_mongo()
    await init_db()
    
    total_loaded = 0
    total_skipped = 0
    
    try:
        # Load from horoscopes.jsonl
        jsonl_path = Path("horoscopes.jsonl")
        if jsonl_path.exists():
            print(f"\n📄 Loading from {jsonl_path}...")
            loaded, skipped = await load_jsonl_data(str(jsonl_path))
            total_loaded += loaded
            total_skipped += skipped
            print(f"✅ Loaded {loaded} records, skipped {skipped} duplicates/empty")
        
        # Load from data_stars.json
        json_path = Path("data_stars.json")
        if json_path.exists():
            print(f"\n📄 Loading from {json_path}...")
            loaded, skipped = await load_json_data(str(json_path))
            total_loaded += loaded
            total_skipped += skipped
            print(f"✅ Loaded {loaded} records, skipped {skipped} duplicates/empty")
        
        # Summary
        print(f"\n{'='*50}")
        print(f"✅ Data loading complete!")
        print(f"Total records loaded: {total_loaded}")
        print(f"Total skipped: {total_skipped}")
        print(f"{'='*50}")
        
        # Show statistics
        total_count = await HoroscopeDocument.count()
        print(f"\n📊 Database statistics:")
        print(f"Total horoscope records: {total_count}")
        
        # Count by zodiac sign using Motor directly
        from app.database_mongo import get_database
        db = get_database()
        collection = db['horoscopes']
        
        pipeline = [
            {"$group": {"_id": "$zodiac_sign", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]
        
        print(f"\nRecords by zodiac sign:")
        async for item in collection.aggregate(pipeline):
            print(f"  {item['_id']}: {item['count']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
