from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from database import engine, Base
from routes import auth, transactions, budgets

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sensible Finance API",
    description="Personal Finance Management Application",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
from flask import send_from_directory
from flask_cors import CORS
CORS(app)
@app.route('/')
def home():
    return send_from_directory(r'C:\Users\Admin\Sensible-Finance-Manager\expense-tracker', 'index.html')

