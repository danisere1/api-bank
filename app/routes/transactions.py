from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from app.services.supabase import supabase
from app.schemas.transactions import TransactionCreate, TransactionResponse

table = "transactions"

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"]
)


@router.get("/", response_model=list[TransactionResponse])
def get_transactions(
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None)
    ):

    query = (
            supabase
            .table(table)
            .select("*")
    )
    if date_from:
        query = query.gte("created_at", date_from.isoformat())
    if date_to:
        query = query.lte("created_at", date_to.isoformat())

    response = query.execute()

    return response.data



@router.get("/{id}", response_model=TransactionResponse)
def get_transaction(id: int):

    response = (
        supabase
        .table(table)
        .select("*")
        .eq("id", id)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    return response.data[0]

@router.put("/{id}", response_model=TransactionResponse)
def update_transaction(id: int, transaction: TransactionCreate):

    response = (
        supabase
        .table(table)
        .update(transaction.model_dump(mode="json"))
        .eq("id", id)
        .execute()
    )

    return response.data[0]