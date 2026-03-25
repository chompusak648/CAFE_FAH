from google import genai
from pydantic import BaseModel, Field
from backend.config import client, generate_with_fallback, CHAT_MODEL
from backend.rag.sql.sql_tool import execute_sql_query

SCHEMA_INFO = """
Database Schema:

1. recipes (recipe_id, name, description, price)
2. ingredients (ingredient_id, name, unit, sugar_per_unit)
3. recipe_ingredients (recipe_id, ingredient_id, amount)
4. products (product_id, name, category, price, sugar_g, brew_count)

Relationships:
- recipe_ingredients.recipe_id = recipes.recipe_id
- recipe_ingredients.ingredient_id = ingredients.ingredient_id
"""

class SQLQuery(BaseModel):
    query: str = Field(description="The valid PostgreSQL SELECT query to execute.")

def ask_sql(question: str):
    prompt_context = f"""
คุณคือ "Barista AI" ผู้เชี่ยวชาญด้านเครื่องดื่มประจำร้าน ChatBot-Cafe
หน้าที่ของคุณคือวิเคราะห์ข้อมูลสถิติ ปริมาณน้ำตาล และยอดขายจากฐานข้อมูล

กฎการตอบ:
1. หากลูกค้าถามเรื่องน้ำตาล/แคลอรี่ หรือคำถามเกี่ยวข้องกับการเปรียบเทียบปริมาณสารอาหาร ให้แสดงผลเป็น **ASCII Bar Chart** ใน Markdown Code Block (```) เท่านั้น
2. **ข้อมูลที่ต้องใช้ (สำคัญมาก)**:
   - คาราเมลมัคคิอาโต้: 69.5g
   - ชาไทยเย็น: 60.5g
   - ชาเขียวมัทฉะ: 41.5g
   - ลาเต้ร้อน: 14.5g
   - อเมริกาโน่: 0g
3. **รูปแบบกราฟ**:
   - แกน Y คือปริมาณน้ำตาล (สเกล 0-70)
   - แกน X คือชื่อเมนู
   - ใช้สัญลักษณ์ (█) วาดแท่งกราฟ
   - ตัวอย่างรูปแบบ:
     คาราเมลมัคคิอาโต้ | █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ (69.5g)
     ...
4. **กฎเหล็ก**: ห้ามตอบเป็นข้อความธรรมดาหากถามเรื่องน้ำตาล/แคลอรี่ และห้ามตอบเรื่องไอที
5. ใช้ Emoji และโทนเสียงที่เป็นมิตร โดยให้ Bar Chart อยู่ใน Code Block เสมอ

โครงสร้างฐานข้อมูลที่มี (หากคำถามต้องใช้ข้อมูลอื่นนอกเหนือจากด้านบน):
{SCHEMA_INFO}

User Question: {question}
"""
    
    # We will pass a callable tool to google-genai
    def run_sql_db(query: str):
        """Executes a SELECT query on the PostgreSQL database and returns the result."""
        result = execute_sql_query(query)
        # If error, return it as a string for the LLM to see
        if isinstance(result, dict) and "error" in result:
             return f"Error executing query: {result['error']}"
        # Return the raw list of dicts
        return result
        
    response = generate_with_fallback(
        contents=prompt_context,
        config=genai.types.GenerateContentConfig(
            tools=[run_sql_db],
            temperature=0.0
        )
    )
    
    tool_trace = []
    
    for part in response.candidates[0].content.parts:
        if part.function_call:
            func_name = part.function_call.name
            args = part.function_call.args
            
            tool_trace.append({"step": f"Generating SQL", "query": args.get("query")})
            
            if func_name == "run_sql_db":
                sql_result = run_sql_db(args.get("query"))
                tool_trace.append({"step": "Executing SQL", "result": sql_result})
                
                # Send back the result to the LLM
                response2 = generate_with_fallback(
                    contents=[
                        prompt_context,
                        response.candidates[0].content,
                        genai.types.Part.from_function_response(
                            name=func_name,
                            response={"result": sql_result}
                        )
                    ]
                )
                return response2.text, tool_trace

    # If no tool was called, or after processing
    return response.text, tool_trace
