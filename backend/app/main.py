from fastapi import FastAPI, Depends, Header, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import engine, Base
from .routes import auth, transactions, budgets
from .utils.auth import get_current_user
from .models.user import User

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sensible Finance API",
    description="Personal Finance Management",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Debug middleware to log all requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"\n=== REQUEST ===")
    print(f"Method: {request.method}")
    print(f"Path: {request.url.path}")
    print(f"Headers: {dict(request.headers)}")
    response = await call_next(request)
    print(f"Status: {response.status_code}")
    return response

# Include routers
app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(budgets.router)

@app.get("/")
async def root():
    return {
        "message": "Sensible Finance API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/test-auth")
async def test_auth(current_user: User = Depends(get_current_user)):
    return {"user": current_user.username, "authenticated": True}
