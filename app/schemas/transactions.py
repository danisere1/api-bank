from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, field_validator, model_validator


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


class TransactionBase(BaseModel):
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


class TransactionCreate(TransactionBase):
    external_id: str

    @field_validator("external_id")
    @classmethod
    def validate_external_id(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("external_id cannot be empty.")

        return value


class TransactionUpdate(TransactionBase):
    pass


class TransactionResponse(TransactionBase):
    id: int
    created_at: datetime
    external_id: str | None = None