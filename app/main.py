from app.services.supabase import supabase
from fastapi import FastAPI
from datetime import datetime
from app.routes.transactions import router as transactions_router

app = FastAPI(
title="API de Gastos",
description="API para gestionar gastos personales",
version="1.0.0"
)

app.include_router(transactions_router)

@app.get("/")
def home():
    return {
        "service": "bank-api",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }