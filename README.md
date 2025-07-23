# Shop Products CRUD API

This is a basic CRUD API for managing products in a shop, built with FastAPI, SQLAlchemy, and SQLite. It includes automatic Swagger documentation and basic tests with pytest.

## Features
- CRUD operations for products (id, name, description, price, quantity)
- SQLite database
- Swagger UI documentation at `/docs`
- Basic tests with pytest

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the API server:**
   ```bash
   uvicorn main:app --reload
   ```
   The API will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000)

3. **Swagger Documentation:**
   Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for interactive API docs.

4. **Run tests:**
   ```bash
   pytest
   ``` 