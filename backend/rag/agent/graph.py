from backend.config import client, generate_with_fallback, CHAT_MODEL
from backend.rag.retriever_pgvector import search_documents
from backend.rag.sql.function_calling_sql import ask_sql
from google import genai

BARISTA_SYSTEM_PROMPT = """
คุณคือ "Barista AI" ผู้เชี่ยวชาญด้านเครื่องดื่มประจำร้าน ChatBot-Cafe
หน้าที่ของคุณคือแนะนำเมนู บอกสูตรชง และเปรียบเทียบข้อมูลโภชนาการ

กฎเหล็ก (Critical Rules):
1. ห้ามตอบเกี่ยวกับสินค้าไอที (Laptop/Mouse/Technology) เด็ดขาด หากถูกถามให้ตอบเลี่ยงอย่างสุภาพและข้ามไปเรื่องเครื่องดื่มทันที
2. หากระบบแจ้งว่าไม่พบตาราง SQL หรือเกิด Error ห้ามบอกลูกค้าว่าไม่พบตาราง ให้ใช้ความรู้บาริสต้าของคุณตอบแทนทันทีเพื่อไม่ให้ลูกค้าเสียความรู้สึก
3. หากลูกค้ากังวลเรื่องน้ำตาล ให้แนะนำเมนูเหล่านี้ก่อนแสดงกราฟ:
   - **อเมริกาโน่ (ไม่ใส่น้ำตาล)**: เป็นตัวเลือกที่ดีที่สุดสำหรับคนรักสุขภาพค่ะ ☕️
   - **ชาเขียวร้อน (ไม่ใส่น้ำตาล)**: สดชื่นและมีประโยชน์ค่ะ 🍵
   - **ลาเต้/คาปูชิโน่ (ลดหวาน/ไม่ใส่น้ำเชื่อม)**: สามารถปรับระดับความหวานได้ตามใจชอบเลยค่ะ

ข้อมูลปริมาณน้ำตาล (Sugar Stats):
- คาราเมล มัคคิอาโต้ (69.5g)
- ชาไทยเย็น (60.5g)
- มัทฉะลาเต้ (41.5g)
- ลาเต้ร้อน (14.5g)
- อเมริกาโน่ (0g)

ฟังก์ชันการตอบ:
- การแนะนำเมนู: มีชื่อเมนู, ราคา และคำอธิบายให้น่ากิน (เช่น ☕ Dirty Coffee 85.- นุ่มละมุน)
- ตารางเปรียบเทียบ: ASCII Bar Chart ใน Code Block (```) เท่านั้น (แกน Y 0-70)
- การบอกสูตรการชง: บอกวัตถุดิบและขั้นตอน (Step-by-Step) และเคล็ดลับบาริสต้า

Tone & Style: สุภาพ เป็นมิตร ใช้ Emoji ที่เกี่ยวกับคาเฟ่เสมอ
"""

def generate_ascii_bar_chart(data: list[dict], label: str) -> str:
    """Generates an ASCII bar chart for quantitative comparisons."""
    if not data: return ""
    
    max_val = 70.0 # Standard scale max
    chart = f"📊 **{label}**\n```\n"
    
    for item in data:
        name = item.get("name", "Unknown")
        val = float(item.get("val", 0))
        # Clamp value for scale
        clamped_val = max(0.0, min(val, max_val))
        # Scale to 20 chars
        bar_len = int((clamped_val / max_val) * 20)
        bar = "█" * bar_len
        chart += f"{name[:15]:<15} | {bar:<20} ({val}g)\n"
    
    chart += "```"
    return chart

def route_intent(question: str) -> str:
    """Classifies if a question is meant for DOCUMENTS, SQL_DB, GENERAL, or MIXED."""
    prompt = f"""
Classify the user's question into one of the following categories:
- DOCUMENTS: if the question refers to specific facts, manuals, PDF contents, or uploaded data.
- SQL_DB: if asking about database-style queries like sales, quantities, or specific business data (e.g. 'ขอน้ำตาลในเครื่องดื่ม', 'ยอดขายรายเดือน', 'สถิติการชง').
- BARISTA_RECIPE: if the user asks for drink recipes or how to brew (e.g. 'สูตรโกโก้', 'ชงชาไทยยังไง').
- GENERAL: if it's a greeting, a general knowledge question, or casual talk.
- MIXED: if it combines both.

User Question: {question}

Reply with ONLY ONE WORD (DOCUMENTS, SQL_DB, BARISTA_RECIPE, GENERAL, or MIXED).
"""
    response = generate_with_fallback(
        prompt=prompt,
        config=genai.types.GenerateContentConfig(temperature=0.0)
    )
    return response.text.strip().upper()

def evaluate_context(question: str, context: str) -> dict:
    """Evaluates the retrieved context against the question."""
    prompt = f"""
Evaluate the following context based on the user's question.
Assign a score from 0 to 2 for Relevance and Sufficiency.
Relevance:
- 0: Not relevant
- 1: Partially relevant
- 2: Highly relevant
Sufficiency:
- 0: Cannot answer the question
- 1: Partially answers the question
- 2: Fully answers the question

Question: {question}
Context: {context}

Return JSON strictly in this format: {{"relevance": int, "sufficiency": int}}
"""
    response = generate_with_fallback(
        prompt=prompt,
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.0
        )
    )
    import json
    try:
        return json.loads(response.text)
    except Exception:
        return {"relevance": 0, "sufficiency": 0}

def generate_answer_from_docs(question: str, context: str) -> str:
    """Answers using context primarily, but allows general knowledge fallback."""
    prompt = f"""
{BARISTA_SYSTEM_PROMPT}

Answer the user's Question using the provided Context.
Rules:
1. If the provided Context contains the answer, use it.
2. If not, use your knowledge as Barista AI.
3. Keep it friendly with Emoji.

Context: 
{context}

Question: {question}
"""
    response = generate_with_fallback(
        prompt=prompt,
        config=genai.types.GenerateContentConfig(temperature=0.3)
    )
    return response.text

def generate_general_answer(question: str) -> str:
    """Generates a high-quality general purpose answer."""
    prompt = f"{BARISTA_SYSTEM_PROMPT}\n\nUser Question: {question}"
    response = generate_with_fallback(
        prompt=prompt,
        config=genai.types.GenerateContentConfig(temperature=0.7)
    )
    return response.text

def process_chat(question: str, mode: str = "auto", max_iterations: int = 2):
    tool_trace: list[dict] = []
    citations = []
    
    if mode == "sql":
        tool_trace.append({"step": "Mode: SQL"})
        answer, sql_trace = ask_sql(question)
        tool_trace.extend(sql_trace)
        return answer, citations, tool_trace
        
    elif mode == "rag":
        tool_trace.append({"step": "Mode: Document RAG"})
        
        # Retrieval
        docs = search_documents(question)
        context = "\n\n".join([f"Source: {d['metadata'].get('filename', 'Unknown')} (Chunk {d['chunk_index']})\n{d['content']}" for d in docs])
        citations.extend([{"doc_id": d["doc_id"], "chunk": d["chunk_index"], "score": d["score"]} for d in docs])
        
        tool_trace.append({"step": "Retrieved Docs", "count": len(docs)})
        
        answer = generate_answer_from_docs(question, context)
        tool_trace.append({"step": "Generated Answer"})
        return answer, citations, tool_trace

    # Auto Agentic RAG Pipeline
    tool_trace.append({"step": "Mode: Auto Agentic RAG"})
    
    # 1. Route Intent
    intent = route_intent(question)
    tool_trace.append({"step": f"Intent Routing", "result": intent})
    
    if intent == "SQL_DB":
        answer, sql_trace = ask_sql(question)
        tool_trace.extend(sql_trace)
        
        # Check if the result looks like graphable data (list of results with numeric values)
        sql_exec_step = None
        for t in reversed(sql_trace):
            if t["step"] == "Executing SQL":
                sql_exec_step = t
                break
        
        if sql_exec_step is not None:
            data = sql_exec_step.get("result")
            # data should now be a list of dicts from run_sql_db
            if isinstance(data, list) and len(data) > 1: # Need at least 2 points for a graph
                first_row = data[0]
                # Identify numeric column and name column
                num_col = next((c for c in first_row if isinstance(first_row[c], (int, float))), None)
                name_col = next((c for c in first_row if isinstance(first_row[c], str)), None)
                
                if num_col and name_col:
                    try:
                        all_stats = [{"name": str(row[name_col]), "val": float(row[num_col])} for row in data]
                        
                        # Generate ASCII chart for the response
                        ascii_chart = generate_ascii_bar_chart(all_stats, f"เปรียบเทียบ {num_col}")
                        final_answer = f"{answer}\n\n{ascii_chart}"
                        
                        tool_trace.append({
                            "step": "Adding Sugar Stats",
                            "data": {
                                "current": None,
                                "val": 0,
                                "label": f"เปรียบเทียบ {num_col} แยกตาม {name_col}",
                                "all_stats": all_stats
                            }
                        })
                        return final_answer, citations, tool_trace
                    except (ValueError, TypeError):
                        pass
        return answer, citations, tool_trace
        
    elif intent == "BARISTA" or intent == "BARISTA_RECIPE":
        tool_trace.append({"step": "Barista AI Routing"})
        from backend.barista import get_barista_response
        answer, data = get_barista_response(question)
        if answer:
            return answer, citations, tool_trace
        else:
            # Fallback if recipe not found in database
            tool_trace.append({"step": "Recipe not found in local DB, using general AI knowledge"})
            answer = generate_general_answer(f"ทำหน้าที่เป็น Barista AI ตอบสูตรเครื่องดื่มนี้อย่างละเอียด พร้อมปริมาณเป็น ml: {question}")
            return answer, citations, tool_trace

    elif intent == "GENERAL":
        tool_trace.append({"step": "General Knowledge Routing"})
        answer = generate_general_answer(question)
        return answer, citations, tool_trace

    elif intent == "DOCUMENTS" or intent == "MIXED":
        tool_trace.append({"step": "Retrieving Documents"})
        docs = search_documents(question)
        context = "\n\n".join([f"{d['content']}" for d in docs])
        
        if docs:
            citations.extend([{"doc_id": d["doc_id"], "chunk": d["chunk_index"], "score": d["score"]} for d in docs])
            tool_trace.append({"step": f"Context Found ({len(docs)} chunks)"})
        else:
            tool_trace.append({"step": "No relevant documents found, using general knowledge fallback"})
            
        answer = generate_answer_from_docs(question, context)
        return answer, citations, tool_trace
        
    # Default fallback for any other cases
    answer = generate_general_answer(question)
    return answer, citations, tool_trace
