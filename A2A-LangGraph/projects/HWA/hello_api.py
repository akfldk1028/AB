from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Create FastAPI instance
app = FastAPI(title="Hello World API", version="1.0.0")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint that returns a welcome message"""
    return {"message": "Welcome to Hello World API"}

# Hello World endpoint
@app.get("/hello")
async def hello_world():
    """Returns a simple Hello World message"""
    return {"message": "Hello, World!"}

# Hello with name parameter
@app.get("/hello/{name}")
async def hello_name(name: str):
    """Returns a personalized hello message"""
    return {"message": f"Hello, {name}!"}

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "service": "Hello World API"}

if __name__ == "__main__":
    import uvicorn
    # Run the application
    uvicorn.run(app, host="0.0.0.0", port=8000)