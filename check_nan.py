import sqlite3

conn = sqlite3.connect('fortune.db')
cursor = conn.cursor()

# Count nan values
result = cursor.execute("SELECT COUNT(*) FROM horoscopes WHERE horoscope_text = 'nan'").fetchone()
print(f"'nan' 레코드: {result[0]}개")

# Count total
total = cursor.execute("SELECT COUNT(*) FROM horoscopes").fetchone()
print(f"전체 레코드: {total[0]}개")

# Count by zodiac
print("\n별자리별 'nan' 개수:")
nan_by_sign = cursor.execute("""
    SELECT zodiac_sign, COUNT(*) 
    FROM horoscopes 
    WHERE horoscope_text = 'nan' 
    GROUP BY zodiac_sign
""").fetchall()

for sign, count in nan_by_sign:
    print(f"  {sign}: {count}개")

conn.close()
