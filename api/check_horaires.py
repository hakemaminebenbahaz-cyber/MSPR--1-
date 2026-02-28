from core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
result = db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'horaires'"))
for row in result:
    print(row[0])
db.close()