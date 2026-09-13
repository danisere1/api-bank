import pytest
from pydantic import ValidationError

from app.schemas.transactions import TransactionCreate


def valid_transaction(**overrides):
    data = {
        "date": "2026-09-13T10:00:00",
        "description": "Compra supermercado",
        "amount": -50.00,
        "category": "Alimentación",
        "type": "expense",
    }

    data.update(overrides)
    return data


def test_expense_with_negative_amount():
    transaction = TransactionCreate(
        **valid_transaction()
    )

    assert transaction.type == "expense"
    assert transaction.amount == -50.00


def test_expense_with_positive_amount_fails():
    with pytest.raises(ValidationError):
        TransactionCreate(
            **valid_transaction(
                amount=50.00
            )
        )


def test_income_with_positive_amount():
    transaction = TransactionCreate(
        **valid_transaction(
            type="income",
            amount=100.00
        )
    )

    assert transaction.type == "income"
    assert transaction.amount == 100.00


def test_income_with_negative_amount_fails():
    with pytest.raises(ValidationError):
        TransactionCreate(
            **valid_transaction(
                type="income",
                amount=-100.00
            )
        )

def test_invalid_type_fails():
    with pytest.raises(ValidationError):
        TransactionCreate(
            **valid_transaction(
                type="invalid_type"
            )
        )