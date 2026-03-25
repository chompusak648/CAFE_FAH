import pypdf
from google import genai
from sqlalchemy.orm import Session
from backend.database import SessionLocal, DocChunk
from backend.config import GEMINI_API_KEY, EMBED_MODEL, CHAT_MODEL
import uuid
import os

client = genai.Client(api_key=GEMINI_API_KEY)

def extract_text_pypdf(file_path: str) -> str:
    try:
        reader = pypdf.PdfReader(file_path, strict=False)
        pages_text = []
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted and extracted.strip():
                pages_text.append(extracted.strip())
        text = "\n\n".join(pages_text)
        print(f"Extracted {len(text)} chars from {len(reader.pages)} pages.")
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def chunk_text(text: str, chunk_size: int = 600, overlap: int = 100):
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = start + chunk_size
        chunks.append(text[start:end])
        start += (chunk_size - overlap)
    return chunks

def embed_chunks(chunks: list[str]) -> list[list[float]]:
    """Embed text chunks using Gemini. Forces output_dimensionality=768 to match VECTOR(768) in DB."""
    from google import genai as _genai
    embeddings = []
    batch_size = 20  # smaller batches to avoid quota issues
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        print(f"Embedding batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1} ({len(batch)} chunks)...")
        response = client.models.embed_content(
            model=EMBED_MODEL,
            contents=batch,
            config=_genai.types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
                output_dimensionality=768
            )
        )
        for emb in response.embeddings:
            embeddings.append(list(emb.values))
    return embeddings

def extract_structured_data(text: str) -> dict:
    """Uses Gemini to extract recipes and ingredients from text."""
    prompt = f"""
Analyze the following text from a cafe/beverage document.
Identify any drink recipes and their ingredients.

Return a JSON object with this structure:
{{
  "recipes": [
    {{
      "name": "Recipe Name",
      "description": "Short description",
      "price": float (if available, else 0.0),
      "ingredients": [
        {{
          "name": "Ingredient Name",
          "unit": "Unit (e.g. ml, g, ช้อน)",
          "amount": float,
          "sugar_per_unit": float (if available, else 0.0)
        }}
      ]
    }}
  ]
}}

If no recipes are found, return {{"recipes": []}}.

Text:
{text[:5000]} # Limit text for API
"""
    try:
        response = client.models.generate_content(
            model=CHAT_MODEL,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.0
            )
        )
        import json
        return json.loads(response.text)
    except Exception as e:
        print(f"Extraction error: {e}")
        return {"recipes": []}

def save_structured_to_sql(db: Session, data: dict):
    """Saves extracted recipes and ingredients to the database."""
    from backend.database import Recipe, Ingredient, RecipeIngredient
    
    for r_data in data.get("recipes", []):
        # Create or Get Recipe
        recipe = db.query(Recipe).filter(Recipe.name == r_data["name"]).first()
        if not recipe:
            recipe = Recipe(
                name=r_data["name"],
                description=r_data.get("description", ""),
                price=r_data.get("price", 0.0)
            )
            db.add(recipe)
            db.flush() # Get recipe_id
            
        for i_data in r_data.get("ingredients", []):
            # Create or Get Ingredient
            ingredient = db.query(Ingredient).filter(Ingredient.name == i_data["name"]).first()
            if not ingredient:
                ingredient = Ingredient(
                    name=i_data["name"],
                    unit=i_data.get("unit", ""),
                    sugar_per_unit=i_data.get("sugar_per_unit", 0.0)
                )
                db.add(ingredient)
                db.flush()
            
            # Link via RecipeIngredient
            ri = db.query(RecipeIngredient).filter(
                RecipeIngredient.recipe_id == recipe.recipe_id,
                RecipeIngredient.ingredient_id == ingredient.ingredient_id
            ).first()
            if not ri:
                ri = RecipeIngredient(
                    recipe_id=recipe.recipe_id,
                    ingredient_id=ingredient.ingredient_id,
                    amount=i_data.get("amount", 0.0)
                )
                db.add(ri)
    db.commit()

def process_file(file_path: str, doc_id: str, chunk_size: int = 600, overlap: int = 100):
    print(f"Processing {file_path}")
    text = ""
    if file_path.lower().endswith('.pdf'):
        text = extract_text_pypdf(file_path)
    else:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
    
    if not text.strip():
        print("No text extracted.")
        return

    # 1. RAG Chunks and Embeddings
    chunks = chunk_text(text, chunk_size, overlap)
    embeddings = embed_chunks(chunks)
    
    # 2. Structured Extraction
    structured_data = extract_structured_data(text)
    
    filename = os.path.basename(file_path)
    db: Session = SessionLocal()
    try:
        # Save RAG Chunks
        for idx, (chunk_text_data, embedding) in enumerate(zip(chunks, embeddings)):
            doc_chunk = DocChunk(
                chunk_id=uuid.uuid4(),
                doc_id=doc_id,
                chunk_index=idx,
                content=chunk_text_data,
                embedding=embedding,
                metadata_col={"filename": filename}
            )
            db.add(doc_chunk)
        
        # Save Structured Data
        save_structured_to_sql(db, structured_data)
        
        db.commit()
        print(f"Successfully ingrained {len(chunks)} chunks and structured data into DB.")
    except Exception as e:
        db.rollback()
        print(f"DB insertion error: {e}")
    finally:
        db.close()
