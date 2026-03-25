from backend.database import engine, Base, BrewingStats, SessionLocal

def init_db():
    Base.metadata.create_all(engine)
    print("Tables created.")
    
    db = SessionLocal()
    # Initialize with default drinks if they don't exist
    drinks = ["โกโก้", "ชาไทย", "ชาเขียว", "เอสเพรสโซ่", "นมชมพู", "กาแฟดำ", "นมคาราเมล"]
    for drink in drinks:
        existing = db.query(BrewingStats).filter(BrewingStats.drink_name == drink).first()
        if not existing:
            db.add(BrewingStats(drink_name=drink, brew_count=0))
    db.commit()
    db.close()
    print("Brewing stats initialized.")

if __name__ == "__main__":
    init_db()
