import os
from sqlalchemy import text
from backend.database import SessionLocal

def show_db():
    db = SessionLocal()
    try:
        tables = ["recipes", "ingredients", "recipe_ingredients", "doc_chunks"]
        for table in tables:
            print(f"\n--- Table: {table} ---")
            try:
                result = db.execute(text(f"SELECT * FROM {table} LIMIT 20"))
                columns = result.keys()
                print(" | ".join(columns))
                print("-" * 50)
                for row in result:
                    print(" | ".join(str(val) for val in row))
            except Exception as e:
                print(f"Error querying {table}: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    show_db()
