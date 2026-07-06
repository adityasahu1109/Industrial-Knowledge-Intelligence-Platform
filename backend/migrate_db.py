from core.database import engine, Base, init_db
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS drawings"))
    conn.execute(text("DROP TABLE IF EXISTS drawing_tags"))
    conn.commit()

init_db()
print("Migration complete!")
