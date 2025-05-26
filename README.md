# StakeAI Vector Database API

A high-performance vector database API built with FastAPI, following Domain-Driven Design principles.

## Features

- Vector similarity search with multiple algorithms (Brute Force, KD-Tree, VP-Tree)
- RESTful API with FastAPI
- Clean architecture with domain-driven design
- Thread-safe in-memory storage
- Comprehensive testing suite

## Installation

1. Install dependencies using Poetry:
```bash
poetry install
```

2. Run the development server:
```bash
poetry run uvicorn vector_db_api.interface.main:app --reload
```

## Project Structure

The project follows a four-ring Domain-Driven Design architecture:

- `domain/` - Pure business logic and entities
- `application/` - Use cases and services
- `infrastructure/` - Data access and external integrations
- `interface/` - API routes and delivery layer

## Development

Run tests:
```bash
poetry run pytest
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc 
