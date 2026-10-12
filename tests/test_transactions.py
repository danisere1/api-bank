import pytest
from fastapi.testclient import TestClient
from decimal import Decimal

from app.main import app
from app.routes import transactions


client = TestClient(app)


class MockResponse:
    def __init__(self, data):
        self.data = data


class MockQuery:
    def __init__(self, supabase, data):
        self.supabase = supabase
        self.data = data

    def select(self, *args):
        return self

    def eq(self, column, value):
        self.data = [
            transaction
            for transaction in self.data
            if transaction.get(column) == value
        ]
        return self

    def gte(self, column, value):
        self.data = [
            transaction
            for transaction in self.data
            if transaction.get(column) >= value
        ]
        return self

    def lte(self, column, value):
        self.data = [
            transaction
            for transaction in self.data
            if transaction.get(column) <= value
        ]
        return self

    def order(self, *args, **kwargs):
        return self

    def insert(self, data):
        transaction = data.copy()

        transaction["id"] = self.supabase.next_id
        transaction["created_at"] = "2026-09-13T12:00:00"

        if "amount" in transaction:
            amount = Decimal(str(transaction["amount"]))
            transaction["amount"] = format(amount, "f").rstrip("0").rstrip(".")

        self.supabase.next_id += 1
        self.supabase.data.append(transaction)
        self.data = [transaction]

        return self

    def upsert(self, data, on_conflict=None, ignore_duplicates=False):
        existing = [
            transaction
            for transaction in self.supabase.data
            if transaction.get(on_conflict) == data.get(on_conflict)
        ]

        if existing and ignore_duplicates:
            self.data = []
            return self

        return self.insert(data)

    def execute(self):
        return MockResponse(self.data)


class MockSupabase:
    def __init__(self, data):
        self.data = data
        self.next_id = 2

    def table(self, table_name):
        return MockQuery(self, self.data.copy())


@pytest.fixture
def mock_supabase(monkeypatch):
    data = [
        {
            "id": 1,
            "description": "Compra supermercado",
            "amount": -50.00,
            "category": "Alimentación",
            "type": "expense",
            "created_at": "2026-09-13T10:05:00"
        }
    ]

    mock = MockSupabase(data)

    monkeypatch.setattr(
        transactions,
        "supabase",
        mock
    )

    return mock


def test_get_transactions(mock_supabase):
    response = client.get("/transactions/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == 1
    assert data[0]["category"] == "Alimentación"


def test_get_transaction(mock_supabase):
    response = client.get("/transactions/1")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["description"] == "Compra supermercado"


def test_post_transaction(mock_supabase):
    transaction = {
        "external_id": "expense-gasolina-001",
        "description": "Gasolina",
        "amount": -60.00,
        "category": "Transporte",
        "type": "expense"
    }

    response = client.post(
        "/transactions/",
        json=transaction
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 2
    assert data["description"] == "Gasolina"
    assert data["amount"] == "-60"
    assert data["category"] == "Transporte"
    assert data["type"] == "expense"
    assert data["external_id"] == "expense-gasolina-001"


def test_post_transaction_with_existing_external_id_returns_existing(mock_supabase):
    transaction = {
        "external_id": "expense-gasolina-001",
        "description": "Gasolina",
        "amount": -60.00,
        "category": "Transporte",
        "type": "expense"
    }

    first_response = client.post("/transactions/", json=transaction)
    retry_transaction = {**transaction, "description": "Reintento"}
    retry_response = client.post("/transactions/", json=retry_transaction)

    assert first_response.status_code == 200
    assert retry_response.status_code == 200
    assert retry_response.json() == first_response.json()
    assert len(mock_supabase.data) == 2


def test_post_transaction_requires_external_id(mock_supabase):
    transaction = {
        "description": "Gasolina",
        "amount": -60.00,
        "category": "Transporte",
        "type": "expense"
    }

    response = client.post("/transactions/", json=transaction)

    assert response.status_code == 422


def test_get_transaction_not_found(mock_supabase):
    response = client.get("/transactions/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Transaction not found"
    }


def test_post_transaction_invalid(mock_supabase):
    transaction = {
        "description": "Gasolina",
        "amount": "esto-no-es-un-numero",
        "category": "Transporte",
        "type": "expense"
    }

    response = client.post(
        "/transactions/",
        json=transaction
    )

    assert response.status_code == 422

def test_get_transactions_by_date(mock_supabase):
    response = client.get(
        "/transactions/",
        params={
            "date_from": "2026-09-13T00:00:00",
            "date_to": "2026-09-13T23:59:59"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == 1