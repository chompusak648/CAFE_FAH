from backend.database import Base, Product, SessionLocal, engine


DEFAULT_PRODUCTS = [
    ("Americano", "Coffee", 60.0, 0.0),
    ("Hot Latte", "Coffee", 65.0, 14.5),
    ("Matcha Latte", "Tea", 65.0, 41.5),
    ("Thai Tea", "Tea", 65.0, 60.5),
    ("Caramel Macchiato", "Coffee", 80.0, 69.5),
]


def init_db():
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        for name, category, price, sugar_g in DEFAULT_PRODUCTS:
            existing = db.query(Product).filter(Product.name == name).first()
            if existing:
                existing.category = category
                existing.price = price
                existing.sugar_g = sugar_g
                if existing.brew_count is None:
                    existing.brew_count = 0
            else:
                db.add(
                    Product(
                        name=name,
                        category=category,
                        price=price,
                        sugar_g=sugar_g,
                        brew_count=0,
                    )
                )
        db.commit()
        print("Brewing stats and default products initialized.")
    except Exception as exc:
        db.rollback()
        print(f"Error initializing brewing stats: {exc}")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
