import sqlite3
from datetime import date

import pytest
from fastapi.testclient import TestClient

from backend.db.database import Database
from backend.main import app


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    """Create a fresh in-memory-style database per test and patch routers to use it."""
    db_instance = Database()
    db_instance.conn.close()

    db_path = tmp_path / "test.db"
    db_instance.conn = sqlite3.connect(db_path, check_same_thread=False)
    db_instance.conn.row_factory = sqlite3.Row
    db_instance._ensure_tables()

    targets = [
        "backend.db.database",
        "backend.db",
        "backend.routers.calendar",
        "backend.routers.shopping",
        "backend.routers.expenses",
        "backend.routers.house",
        "backend.routers.auth",
    ]
    for target in targets:
        monkeypatch.setattr(f"{target}.db", db_instance)

    yield db_instance

    db_instance.conn.close()


@pytest.fixture
def client(test_db):
    return TestClient(app)


@pytest.fixture
def auth_header(test_db):
    house = test_db.create_house("Test House")
    user = test_db.create_user("alice", "secret", house.id)
    token = test_db.create_session_token(user.id)
    return {"Authorization": f"Bearer {token}"}


def test_root_returns_welcome(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Flatmate App API"}


def test_calendar_flow(client, auth_header):
    event_payload = {
        "title": "Test Event",
        "date": str(date.today()),
        "description": "Sample",
        "assigned_to": ["Alice"],
    }
    create_resp = client.post("/calendar/", json=event_payload, headers=auth_header)
    assert create_resp.status_code == 200
    created = create_resp.json()
    assert created["id"] is not None

    list_resp = client.get("/calendar/", headers=auth_header)
    events = list_resp.json()
    assert len(events) == 1
    assert events[0]["title"] == event_payload["title"]

    update_payload = {
        "title": "Updated Event",
        "date": event_payload["date"],
        "description": "Updated description",
        "assigned_to": ["Bob"],
    }
    update_resp = client.put(f"/calendar/{created['id']}", json=update_payload, headers=auth_header)
    assert update_resp.status_code == 200
    assert update_resp.json()["title"] == "Updated Event"


def test_shopping_flow(client, auth_header):
    item_payload = {"name": "Milk", "quantity": 2, "added_by": "Alice"}
    create_resp = client.post("/shopping/", json=item_payload, headers=auth_header)
    assert create_resp.status_code == 200
    item_id = create_resp.json()["id"]

    list_resp = client.get("/shopping/", headers=auth_header)
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) == 1
    assert items[0]["name"] == "Milk"

    delete_resp = client.delete(f"/shopping/{item_id}", headers=auth_header)
    assert delete_resp.status_code == 200
    assert client.get("/shopping/", headers=auth_header).json() == []


def test_house_settings(client, auth_header):
    payload = {"name": "My House"}
    save_resp = client.post("/house/", json=payload, headers=auth_header)
    assert save_resp.status_code == 200

    fetch_resp = client.get("/house/", headers=auth_header)
    assert fetch_resp.status_code == 200
    returned = fetch_resp.json()
    assert returned["name"] == "My House"
    assert returned["flatmates"] == ["alice"]
    assert returned["join_code"] is not None


def test_auth_register_and_login(client, test_db):
    register_resp = client.post(
        "/auth/register",
        json={"username": "newuser", "password": "pw", "house_name": "Auth House"},
    )
    assert register_resp.status_code == 200
    payload = register_resp.json()
    token = payload["token"]
    assert token
    assert payload["house"]["join_code"] == str(payload["house"]["id"])

    login_resp = client.post(
        "/auth/login",
        json={"username": "newuser", "password": "pw"},
    )
    assert login_resp.status_code == 200
    login_payload = login_resp.json()
    assert login_payload["token"]

    me_resp = client.get("/auth/me", headers={"Authorization": f"Bearer {login_payload['token']}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["user"]["username"] == "newuser"


def test_auth_join_existing_house(client, test_db):
    # Create first user + house
    first = client.post(
        "/auth/register",
        json={"username": "host", "password": "pw", "house_name": "Shared"},
    )
    assert first.status_code == 200
    join_code = first.json()["house"]["join_code"]

    # Join existing house via code
    second = client.post(
        "/auth/register",
        json={"username": "guest", "password": "pw", "house_code": join_code},
    )
    assert second.status_code == 200
    assert second.json()["house"]["id"] == first.json()["house"]["id"]
    assert "guest" in second.json()["house"]["flatmates"]


def test_expenses_and_debts_flow(client, auth_header):
    expense_payload = {
        "title": "Groceries",
        "amount": 100.0,
        "payer": "Alice",
        "involved_people": ["Alice", "Bob"],
    }
    create_expense = client.post("/expenses/", json=expense_payload, headers=auth_header)
    assert create_expense.status_code == 200
    expenses_list = client.get("/expenses/", headers=auth_header)
    assert expenses_list.status_code == 200
    expenses_payload = expenses_list.json()
    assert len(expenses_payload) == 1
    assert expenses_payload[0]["title"] == "Groceries"

    debts_resp = client.get("/expenses/debts", headers=auth_header)
    assert debts_resp.status_code == 200
    debts = debts_resp.json()
    assert len(debts) == 1
    assert debts[0]["debtor"] == "Bob"
    assert debts[0]["creditor"] == "Alice"
    assert debts[0]["amount"] == 50.0

    same_person = client.post(
        "/expenses/reimbursements",
        json={"from_person": "Alice", "to_person": "Alice", "amount": 10},
        headers=auth_header,
    )
    assert same_person.status_code == 400

    negative_amount = client.post(
        "/expenses/reimbursements",
        json={"from_person": "Bob", "to_person": "Alice", "amount": -5},
        headers=auth_header,
    )
    assert negative_amount.status_code == 400

    reimbursement_payload = {
        "from_person": "Bob",
        "to_person": "Alice",
        "amount": 20.0,
        "note": "Cash",
    }
    reimb_resp = client.post("/expenses/reimbursements", json=reimbursement_payload, headers=auth_header)
    assert reimb_resp.status_code == 200
    reimbursement = reimb_resp.json()
    assert reimbursement["id"] is not None
    assert reimbursement["note"] == "Cash"

    reimb_list = client.get("/expenses/reimbursements", headers=auth_header)
    assert reimb_list.status_code == 200
    assert len(reimb_list.json()) == 1

    debts_after = client.get("/expenses/debts", headers=auth_header)
    assert debts_after.status_code == 200
    updated = debts_after.json()
    assert len(updated) == 1
    assert updated[0]["amount"] == 30.0


def test_reset_house_data(client, auth_header):
    client.post("/house/", json={"name": "Resettable"}, headers=auth_header)

    event_payload = {
        "title": "To clear",
        "date": str(date.today()),
        "description": "temp",
        "assigned_to": [],
    }
    client.post("/calendar/", json=event_payload, headers=auth_header)
    client.post("/shopping/", json={"name": "Milk", "quantity": 1, "added_by": "A"}, headers=auth_header)
    client.post(
        "/expenses/",
        json={"title": "Bill", "amount": 20.0, "payer": "A", "involved_people": ["A", "B"]},
        headers=auth_header,
    )

    reset_resp = client.delete("/house/reset", headers=auth_header)
    assert reset_resp.status_code == 200
    assert reset_resp.json()["message"] == "House and data reset"

    assert client.get("/house/", headers=auth_header).json()["flatmates"] == ["alice"]
    assert client.get("/calendar/", headers=auth_header).json() == []
    assert client.get("/shopping/", headers=auth_header).json() == []
    assert client.get("/expenses/", headers=auth_header).json() == []