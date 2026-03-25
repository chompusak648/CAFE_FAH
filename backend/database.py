from sqlalchemy import create_engine, Column, String, Integer, Text, Numeric, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from pgvector.sqlalchemy import Vector
from backend.config import DATABASE_URL, EMBED_DIM
import uuid

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DocChunk(Base):
    __tablename__ = "doc_chunks"
    
    chunk_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doc_id = Column(String(255), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(EMBED_DIM))
    metadata_col = Column("metadata", JSONB, default=dict) # mapped to metadata in DB

class Recipe(Base):
    __tablename__ = "recipes"
    
    recipe_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    price = Column(Numeric(10, 2))
    
    ingredients = relationship("RecipeIngredient", back_populates="recipe")

class Ingredient(Base):
    __tablename__ = "ingredients"
    
    ingredient_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    unit = Column(String(50)) # e.g., 'g', 'ml'
    sugar_per_unit = Column(Numeric(10, 4), default=0.0)
    
    recipes = relationship("RecipeIngredient", back_populates="ingredient")

class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"
    
    recipe_id = Column(Integer, ForeignKey("recipes.recipe_id"), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.ingredient_id"), primary_key=True)
    amount = Column(Numeric(10, 2), nullable=False) # e.g., 30.0 (g)
    
    recipe = relationship("Recipe", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="recipes")

class Product(Base):
    __tablename__ = "products"
    
    product_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    category = Column(String(100))
    price = Column(Numeric(10, 2))
    sugar_g = Column(Numeric(10, 2))
    brew_count = Column(Integer, default=0)


def init_db():
    """Best-effort database bootstrap for hosted Postgres providers like Supabase."""
    with engine.begin() as conn:
        try:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        except Exception as exc:
            print(f"WARNING: Could not enable pgvector extension automatically: {exc}")
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
