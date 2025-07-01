from datetime import datetime
from pymongo import MongoClient
import json

client = MongoClient('mongodb://localhost:27017/')
db = client['horoscope_db']
collection = db['daily_horoscope']

# 파일명 수정v
with open('cleaned_data_horoscope.json', 'r') as file:
    data = json.load(file)
    
for date, zodiac_data in data.items():
    for zodiac_name, details in zodiac_data.items():
        document = {
            'date': date,                    # "Jan 1, 2025"
            'zodiac': zodiac_name,          # "Aries (March 21-April 20)"
            'horoscope': details['horoscope'],
            'love': details['love'],
            'lucky_num': details['lucky_num'],
            'lucky_color': details['lucky_color'],
            'created_at': datetime.now()
        }
        collection.insert_one(document)

print("데이터 저장 완료!")