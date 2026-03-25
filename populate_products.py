from backend.database import SessionLocal, Product, engine, Base

# Standard data from barista.py
BARISTA_DATA = [
    {"name": "โกโก้", "category": "Drink", "price": 45.0, "sugar_g": 30.0, "brew_count": 0},
    {"name": "ชาไทย", "category": "Drink", "price": 40.0, "sugar_g": 40.0, "brew_count": 0},
    {"name": "ชาเขียว", "category": "Drink", "price": 45.0, "sugar_g": 35.0, "brew_count": 0},
    {"name": "เอสเพรสโซ่", "category": "Drink", "price": 50.0, "sugar_g": 25.0, "brew_count": 0},
    {"name": "นมชมพู", "category": "Drink", "price": 35.0, "sugar_g": 45.0, "brew_count": 0},
    {"name": "กาแฟดำ", "category": "Drink", "price": 40.0, "sugar_g": 5.0, "brew_count": 0},
    {"name": "นมคาราเมล", "category": "Drink", "price": 55.0, "sugar_g": 35.0, "brew_count": 0},
]

def populate_products():
    Base.metadata.create_all(engine) # Ensure table exists with new columns
    db = SessionLocal()
    try:
        for data in BARISTA_DATA:
            existing = db.query(Product).filter(Product.name == data["name"]).first()
            if existing:
                existing.sugar_g = data["sugar_g"]
                if existing.brew_count is None: existing.brew_count = 0
            else:
                db.add(Product(**data))
        db.commit()
        print("Products table populated/updated with sugar data.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_products()
