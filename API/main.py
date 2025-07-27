# Import necessary libraries from FastAPI, SQLAlchemy, and Pydantic
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List

# Database URL for SQLite
DATABASE_URL = "sqlite:///./products.db"

# Create the SQLAlchemy engine and session
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy Product model (table definition)
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    price = Column(Float)
    quantity = Column(Integer)

# Create the products table in the database (if it doesn't exist)
Base.metadata.create_all(bind=engine)

# Pydantic model for creating a product (request body)
class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    quantity: int

# Pydantic model for reading a product (response body)
class ProductRead(ProductCreate):
    id: int
    class Config:
        orm_mode = True  # Tells Pydantic to use ORM mode for SQLAlchemy models

# Dependency to get a database session
# Ensures each request gets its own session and closes it after
def get_db():
    """
    Yields a database session for use in request handlers, ensuring it is closed after the request is processed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create the FastAPI app instance
app = FastAPI(
    title="Product Management API",
    description="API for managing products with CRUD operations",
    version="1.0.0"
)

# Endpoint to create a new product
@app.post("/products/", response_model=ProductRead)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(**product.dict())  # Unpack product fields into Product model
    db.add(db_product)
    db.commit()
    db.refresh(db_product)  # Refresh to get the new ID
    return db_product

# Endpoint to get a list of products (with pagination)
@app.get("/products/", response_model=List[ProductRead])
def read_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Product).offset(skip).limit(limit).all()

# Endpoint to get a single product by ID
@app.get("/products/{product_id}", response_model=ProductRead)
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Endpoint to update an existing product by ID
@app.put("/products/{product_id}", response_model=ProductRead)
def update_product(product_id: int, product: ProductCreate, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in product.dict().items():
        setattr(db_product, key, value)  # Update each field
    db.commit()
    db.refresh(db_product)
    return db_product

# Endpoint to delete a product by ID
@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return {"ok": True} 