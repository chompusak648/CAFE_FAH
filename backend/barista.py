from typing import Dict, Optional
from backend.database import SessionLocal

# Standard Thai Cafe Recipes (With Prices and Descriptions for Persona)
BARISTA_RECIPES = {
    "โกโก้": {
        "name": "Dirty Cocoa",
        "price": 65.0,
        "description": "โกโก้เข้มข้นเลเยอร์สวย ตัดกับนมเย็นจัดสูตรลับเฉพาะ",
        "ingredients": [
            "ผงโกโก้: 10 ml (ประมาณ 2 ช้อนโต๊ะ)",
            "น้ำร้อน: 60 ml",
            "นมข้นหวาน: 20 ml",
            "นมข้นจืด: 15 ml",
            "นมสด/น้ำเชื่อม: 15 ml"
        ],
        "steps": [
            "ละลายผงโกโก้ในน้ำร้อนจนเนียนละเอียด",
            "ผสมนมข้นหวานและนมข้นจืดลงไป คนให้เข้ากัน",
            "เทนมสดเย็นจัดลงในแก้ว แล้วค่อยๆ เทส่วนผสมโกโก้ทับด้านบน"
        ],
        "tip": "ใช้นมที่เย็นจัดจะช่วยให้เลเยอร์แยกชั้นสวยงามและรสชาติละมุนขึ้น"
    },
    "ชาไทย": {
        "name": "Thai Tea Latte",
        "price": 55.0,
        "description": "ชาไทยหอมกรุ่นต้นตำรับ ผสมนมนุ่มละมุนลิ้น",
        "ingredients": [
            "น้ำชาไทย (สกัดเข้มข้น): 90 ml",
            "นมข้นหวาน: 30 ml",
            "นมข้นจืด: 20 ml",
            "น้ำเชื่อม (ถ้าชอบหวาน): 10 ml"
        ],
        "steps": [
            "สกัดน้ำชาไทยให้ได้ความเข้มข้นตามสัดส่วน",
            "ผสมนมข้นหวานและน้ำเชื่อมลงในน้ำชาขณะร้อน",
            "เทลงในแก้วที่มีน้ำแข็ง แล้วราดนมข้นจืดปิดท้าย"
        ],
        "tip": "การกรองชาหลายๆ รอบจะช่วยให้กลิ่นชาหอมฟุ้งยิ่งขึ้น"
    },
    "เอสเพรสโซ่": {
        "name": "Signature Espresso",
        "price": 70.0,
        "description": "กาแฟเอสเพรสโซ่เข้มข้น หอมอโรม่า ปลุกความสดชื่น",
        "ingredients": [
            "กาแฟเอสเพรสโซ่ (2 ช็อต): 60 ml",
            "นมข้นหวาน: 20 ml",
            "นมข้นจืด: 20 ml",
            "นมสด: 30 ml"
        ],
        "steps": [
            "สกัดเอสเพรสโซ่ช็อตใหม่ๆ จากเครื่อง",
            "ผสมนมข้นหวานลงไปในกาแฟร้อน คนให้ละลาย",
            "ใส่น้ำแข็งแล้วราดนมสดและนมข้นจืดด้านบน"
        ],
        "tip": "ควรดื่มทันทีหลังจากชงเพื่อรสชาติที่ดีที่สุดของเมล็ดกาแฟ"
    },
    "นมคาราเมล": {
        "name": "Caramel Milk",
        "price": 60.0,
        "description": "นมสดรสหวานหอมจากซอสคาราเมลพรีเมียม",
        "ingredients": [
            "นมสด: 150 ml",
            "ซอสคาราเมล: 20 ml",
            "นมข้นหวาน: 10 ml",
            "วิปปิ้งครีม: ท็อปปิ้ง"
        ],
        "steps": [
            "ผสมซอสคาราเมลลงในนมสด",
            "เพิ่มความหวานด้วยนมข้นหวานเล็กน้อย",
            "เทใส่แก้วน้ำแข็ง และท็อปด้วยวิปปิ้งครีม"
        ],
        "tip": "ราดซอสคาราเมลรอบๆ ขอบแก้วก่อนเทนมจะช่วยให้ดูน่าทานยิ่งขึ้น"
    }
}

def record_brew(matched_drink: str):
    """Placeholder for recording brew count."""
    # Logic for old BrewingStats removed to match new schema
    pass

def get_barista_response(query: str) -> tuple[Optional[str], Optional[dict]]:
    """Provides a formatted response for barista-related queries."""
    query = query.lower()
    
    # 1. Recommended Menu Function
    if any(word in query for word in ["แนะนำ", "เมนู", "menu", "recommend"]):
        response = "☕ สวัสดีครับ! ผม Barista AI ยินดีให้บริการครับ วันนี้มีเมนูแนะนำดังนี้ครับ:\n\n"
        # Using the user's example format
        response += "☕ **Dirty Coffee (85.-)** - นุ่มละมุนด้วยนมสูตรลับเฉพาะ\n"
        response += "🥤 **Thai Tea Latte (55.-)** - ชาไทยหอมกรุ่นต้นตำรับ ผสมนมนุ่มละมุนลิ้น\n"
        response += "🍫 **Dirty Cocoa (65.-)** - โกโก้เข้มข้นเลเยอร์สวย ตัดกับนมเย็นจัด\n"
        response += "🍯 **Caramel Milk (60.-)** - นมสดรสหวานหอมจากซอสคาราเมลพรีเมียม\n"
        response += "\nสนใจเมนูไหนหรืออยากทราบสูตรการชง สอบถามได้เลยนะครับ! 😊"
        return response, None

    # 2. Brewing Recipe Function
    matched_drink = None
    for drink in BARISTA_RECIPES:
        if drink in query or drink.replace(" ", "") in query:
            matched_drink = drink
            break
            
    if not matched_drink:
        # Fallback keyword matching
        if any(word in query for word in ["โกโก้", "cocoa"]): matched_drink = "โกโก้"
        elif any(word in query for word in ["ชาไทย", "thai tea"]): matched_drink = "ชาไทย"
        elif any(word in query for word in ["เอสเพรสโซ่", "espresso"]): matched_drink = "เอสเพรสโซ่"
        elif any(word in query for word in ["คาราเมล", "caramel"]): matched_drink = "นมคาราเมล"

    if matched_drink:
        recipe = BARISTA_RECIPES[matched_drink]
        
        response = f"🥤 **สูตรชง{matched_drink} (Barista AI)**\n\n"
        response += "**📦 วัตถุดิบที่ต้องใช้:**\n"
        ingredients = recipe.get("ingredients", [])
        if isinstance(ingredients, list):
            for item in ingredients:
                response += f"- {item}\n"
        
        response += "\n**📝 ขั้นตอนการชง:**\n"
        steps = recipe.get("steps", [])
        if isinstance(steps, list):
            for i, step in enumerate(steps, 1):
                response += f"{i}. {step}\n"
            
        response += f"\n💡 **เคล็ดลับความอร่อย:** {recipe.get('tip', 'ชงด้วยใจให้อร่อยที่สุดครับ')}\n"
        
        # Record the brew event
        record_brew(matched_drink)
        
        return response, None
        
    return None, None
