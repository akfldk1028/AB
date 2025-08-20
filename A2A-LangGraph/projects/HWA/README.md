# Hello World API

A simple REST API built with FastAPI that demonstrates basic endpoint creation.

## Features

- **GET /** - Welcome message
- **GET /hello** - Returns "Hello, World!"
- **GET /hello/{name}** - Personalized greeting
- **GET /health** - Health check endpoint

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the API

### Method 1: Direct Python
```bash
python hello_api.py
```

### Method 2: Uvicorn CLI
```bash
uvicorn hello_api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## Testing the Endpoints

```bash
# Test root endpoint
curl http://localhost:8000/

# Test hello endpoint
curl http://localhost:8000/hello

# Test personalized hello
curl http://localhost:8000/hello/John

# Test health check
curl http://localhost:8000/health
```

## API Documentation

FastAPI automatically generates interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`