from backend.database import SessionLocal, Recipe, Ingredient, RecipeIngredient, engine, Base
from sqlalchemy import text

def populate_recipes():
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        # Clear existing data in correct order
        db.execute(text("TRUNCATE TABLE recipe_ingredients, recipes, ingredients RESTART IDENTITY CASCADE"))
        
        # 1. Ingredients
        ingredients_data = [
            ("Espresso Shot", "shot", 0.0),
            ("Fresh Coconut Water", "ml", 0.04),
            ("Coconut Meat", "g", 0.05),
            ("Concentrated Coffee", "ml", 0.0),
            ("Coconut Milk", "ml", 0.03),
            ("Condensed Milk", "ml", 0.7),
            ("Thai Tea Base", "ml", 0.0),
            ("Fresh Milk", "ml", 0.05),
            ("Sugar", "g", 1.0),
            ("Caramel Syrup", "ml", 0.8),
            ("Cocoa Powder", "g", 0.1),
            ("Matcha Powder", "g", 0.0),
            ("Orange Juice", "ml", 0.12),
            ("Tonic Water", "ml", 0.0),
            ("Lemon Juice", "ml", 0.02),
            ("Strawberry Syrup", "ml", 0.75),
            ("Blueberry Syrup", "ml", 0.75),
            ("Soda Water", "ml", 0.0),
            ("Vanilla Ice Cream", "scoop", 0.15),
            ("Water", "ml", 0.0),
            ("Milk Foam", "ml", 0.05)
        ]
        
        ing_objs = {}
        for name, unit, sugar in ingredients_data:
            ing = Ingredient(name=name, unit=unit, sugar_per_unit=sugar)
            db.add(ing)
            ing_objs[name] = ing
        
        db.flush()
        
        # 2. Recipes
        recipes_data = [
            ("Iced Coconut Americano", "อเมริกาโน่น้ำมะพร้าวสด", 85.0),
            ("Coconut Frozen Coffee", "กาแฟมะพร้าวปั่นสูตรพิเศษ", 95.0),
            ("Thai Tea Latte", "ชาไทยลัตเต้หอมกรุ่น", 65.0),
            ("Coconut Latte", "ลาเต้มะพร้าวหอมมัน", 90.0),
            ("Dirty Coconut Coffee", "เดอร์ตี้คอฟฟี่เลเยอร์น้ำมะพร้าว", 95.0),
            ("Espresso", "เอสเพรสโซ่ช็อตเข้มข้น", 50.0),
            ("Americano (Hot)", "อเมริกาโน่ร้อน", 55.0),
            ("Americano (Iced)", "อเมริกาโน่เย็น", 60.0),
            ("Latte", "ลาเต้นมสด", 65.0),
            ("Cappuccino", "คาปูชิโน่ฟองนมนุ่ม", 70.0),
            ("Mocha", "มอคค่าผสมโกโก้", 75.0),
            ("Caramel Macchiato", "คาราเมลมัคคิอาโต้หวานหอม", 80.0),
            ("Green Tea Latte", "ชาเขียวมัทฉะลาเต้", 65.0),
            ("Cocoa", "โกโก้เย็นเข้มข้น", 60.0),
            ("Lemon Tea", "ชามมะนาวสดชื่น", 50.0),
            ("Italian Soda Strawberry", "สตรอว์เบอร์รี่โซดา", 55.0),
            ("Italian Soda Blueberry", "บลูเบอร์รี่โซดา", 55.0),
            ("Dirty Coffee", "นมเย็นจัดราดเอสเพรสโซ่ช็อต", 85.0),
            ("Affogato", "ไอศกรีมวานิลลาราดเอสเพรสโซ่", 95.0),
            ("Cold Brew Orange", "กาแฟสกัดเย็นผสมน้ำส้มสด", 110.0),
            ("Espresso Tonic", "เอสเพรสโซ่ผสมโทนิคซ่าๆ", 90.0)
        ]
        
        recipe_objs = {}
        for name, desc, price in recipes_data:
            rec = Recipe(name=name, description=desc, price=price)
            db.add(rec)
            recipe_objs[name] = rec
            
        db.flush()
        
        # 3. Recipe Ingredients Mapping
        def add_ing(recipe_name, ing_name, amount):
            db.add(RecipeIngredient(
                recipe_id=recipe_objs[recipe_name].recipe_id, 
                ingredient_id=ing_objs[ing_name].ingredient_id, 
                amount=amount
            ))

        # Data from Image
        add_ing("Iced Coconut Americano", "Espresso Shot", 2)
        add_ing("Iced Coconut Americano", "Fresh Coconut Water", 120)
        add_ing("Iced Coconut Americano", "Coconut Meat", 20)
        
        add_ing("Coconut Frozen Coffee", "Concentrated Coffee", 60)
        add_ing("Coconut Frozen Coffee", "Coconut Milk", 60)
        add_ing("Coconut Frozen Coffee", "Condensed Milk", 30)
        
        add_ing("Thai Tea Latte", "Thai Tea Base", 100)
        add_ing("Thai Tea Latte", "Fresh Milk", 50)

        # Additional mappings to populate the list
        add_ing("Coconut Latte", "Espresso Shot", 1)
        add_ing("Coconut Latte", "Fresh Milk", 100)
        add_ing("Coconut Latte", "Fresh Coconut Water", 50)
        
        add_ing("Espresso", "Espresso Shot", 1)
        add_ing("Latte", "Espresso Shot", 1)
        add_ing("Latte", "Fresh Milk", 150)
        
        add_ing("Cocoa", "Cocoa Powder", 20)
        add_ing("Cocoa", "Fresh Milk", 150)
        add_ing("Cocoa", "Sugar", 20)
        
        add_ing("Green Tea Latte", "Matcha Powder", 10)
        add_ing("Green Tea Latte", "Fresh Milk", 150)
        
        add_ing("Caramel Macchiato", "Espresso Shot", 1)
        add_ing("Caramel Macchiato", "Fresh Milk", 120)
        add_ing("Caramel Macchiato", "Caramel Syrup", 25)

        add_ing("Americano (Hot)", "Espresso Shot", 1)
        add_ing("Americano (Hot)", "Water", 150)

        add_ing("Americano (Iced)", "Espresso Shot", 2)
        add_ing("Americano (Iced)", "Water", 120)

        add_ing("Cappuccino", "Espresso Shot", 1)
        add_ing("Cappuccino", "Fresh Milk", 100)
        add_ing("Cappuccino", "Milk Foam", 50)

        add_ing("Mocha", "Espresso Shot", 1)
        add_ing("Mocha", "Fresh Milk", 100)
        add_ing("Mocha", "Cocoa Powder", 15)

        add_ing("Lemon Tea", "Thai Tea Base", 100)
        add_ing("Lemon Tea", "Lemon Juice", 20)
        add_ing("Lemon Tea", "Sugar", 15)

        add_ing("Italian Soda Strawberry", "Strawberry Syrup", 30)
        add_ing("Italian Soda Strawberry", "Soda Water", 150)

        add_ing("Italian Soda Blueberry", "Blueberry Syrup", 30)
        add_ing("Italian Soda Blueberry", "Soda Water", 150)

        add_ing("Dirty Coffee", "Espresso Shot", 1)
        add_ing("Dirty Coffee", "Fresh Milk", 120)

        add_ing("Affogato", "Espresso Shot", 1)
        add_ing("Affogato", "Vanilla Ice Cream", 1)

        add_ing("Cold Brew Orange", "Concentrated Coffee", 60)
        add_ing("Cold Brew Orange", "Orange Juice", 120)

        add_ing("Espresso Tonic", "Espresso Shot", 2)
        add_ing("Espresso Tonic", "Tonic Water", 150)

        add_ing("Dirty Coconut Coffee", "Espresso Shot", 1)
        add_ing("Dirty Coconut Coffee", "Coconut Milk", 120)

        db.commit()
        print(f"Successfully populated {len(recipes_data)} recipes.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_recipes()
