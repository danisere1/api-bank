from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, model_validator


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


class TransactionCreate(BaseModel):
    type: TransactionType
    description: str
    amount: Decimal
    category: str

    @model_validator(mode="after")
    def validate_amount(self):
        if self.type == TransactionType.EXPENSE and self.amount > 0:
            raise ValueError("Amount must be negative for expenses.")
        if self.type == TransactionType.INCOME and self.amount < 0:
            raise ValueError("Amount must be positive for income.")

        return self

class TransactionResponse(TransactionCreate):
    id: int
    created_at: datetime