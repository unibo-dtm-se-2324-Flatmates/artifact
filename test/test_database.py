import sqlite3
from datetime import date, time

import pytest

from backend.db.database import Database
from backend.models import Event, ShoppingItem, Expense, HouseSettings, Reimbursement


@pytest.fixture
def db_instance(tmp_path):
    instance = Database()
    instance.conn.close()

    db_path = tmp_path / "db.sqlite"
    instance.db_path = db_path
    instance.conn = sqlite3.connect(db_path, check_same_thread=False)
    instance.conn.row_factory = sqlite3.Row
    instance._ensure_tables()

    yield instance

    instance.conn.close()


@pytest.fixture
def house_id(db_instance):
    house = db_instance.create_house("Test Home")
    return house.id


def test_house_settings_roundtrip(db_instance, house_id):
    settings = HouseSettings(name="Test Home", flatmates=["Alice", "Bob"])
    stored = db_instance.update_house_settings(house_id, settings)
    assert stored.name == "Test Home"

    retrieved = db_instance.get_house_settings(house_id)
    assert retrieved.name == "Test Home"


def test_event_crud(db_instance, house_id):
    event = Event(
        title="Study Session",
        date=date.today(),
        start_time=time(18, 0),
        end_time=time(20, 0),
        description="Group study",
        assigned_to=["Alice"],
    )
    created = db_instance.add_event(event, house_id)
    assert created.id is not None

    events = db_instance.get_events(house_id)
    assert len(events) == 1
    assert events[0].title == "Study Session"

    updated_payload = Event(
        title="Updated Session",
        date=event.date,
        start_time=None,
        end_time=None,
        description="Updated",
        assigned_to=["Bob"],
    )
    updated = db_instance.update_event(created.id, updated_payload, house_id)
    assert updated is not None
    assert updated.title == "Updated Session"


def test_event_ordering_by_time(db_instance, house_id):
    today = date.today()
    early = Event(title="Early", date=today, start_time=time(9, 0), end_time=None, description=None, assigned_to=[])
    mid = Event(title="Mid", date=today, start_time=time(12, 0), end_time=None, description=None, assigned_to=[])
    no_time = Event(title="NoTime", date=today, description=None, assigned_to=[])

    db_instance.add_event(mid, house_id)
    db_instance.add_event(no_time, house_id)
    db_instance.add_event(early, house_id)

    events = db_instance.get_events(house_id)
    titles_in_order = [e.title for e in events]
    assert titles_in_order[:3] == ["Early", "Mid", "NoTime"]


def test_shopping_list_flow(db_instance, house_id):
    item = ShoppingItem(name="Bread", quantity=2, added_by="Alice")
    created = db_instance.add_shopping_item(item, house_id)
    assert created.id is not None

    items = db_instance.get_shopping_list(house_id)
    assert len(items) == 1
    assert items[0].name == "Bread"
    assert items[0].purchased is False

    purchased_item = ShoppingItem(name="Milk", quantity=1, added_by="Bob", purchased=True)
    purchased_created = db_instance.add_shopping_item(purchased_item, house_id)
    fetched = db_instance.get_shopping_list(house_id)
    assert any(i.id == purchased_created.id and i.purchased for i in fetched)

    db_instance.remove_shopping_item(created.id, house_id)
    db_instance.remove_shopping_item(purchased_created.id, house_id)
    assert db_instance.get_shopping_list(house_id) == []


def test_expenses_and_reimbursements(db_instance, house_id):
    expense = Expense(title="Utilities", amount=120.0, payer="Alice", involved_people=["Alice", "Bob"])
    saved_expense = db_instance.add_expense(expense, house_id)
    assert saved_expense.id is not None

    expenses = db_instance.get_expenses(house_id)
    assert len(expenses) == 1
    assert expenses[0].title == "Utilities"

    reimbursement = Reimbursement(from_person="Bob", to_person="Alice", amount=60.0, note="Bank transfer")
    saved_reimb = db_instance.add_reimbursement(reimbursement, house_id)
    assert saved_reimb.id is not None

    reimbursements = db_instance.get_reimbursements(house_id)
    assert len(reimbursements) == 1
    assert reimbursements[0].amount == 60.0


def test_clear_all_data(db_instance, house_id):
    db_instance.update_house_settings(house_id, HouseSettings(name="Demo", flatmates=["A"]))
    db_instance.add_event(
        Event(title="Temp", date=date.today(), description="", assigned_to=["A"]),
        house_id,
    )
    db_instance.add_shopping_item(ShoppingItem(name="Bread", quantity=1, added_by="A"), house_id)
    db_instance.add_expense(
        Expense(title="Water", amount=10.0, payer="A", involved_people=["A"]),
        house_id,
    )
    db_instance.add_reimbursement(
        Reimbursement(from_person="A", to_person="A", amount=1.0),
        house_id,
    )

    db_instance.clear_house_data(house_id)

    assert db_instance.get_house_settings(house_id).name == "Demo"
    assert db_instance.get_events(house_id) == []
    assert db_instance.get_shopping_list(house_id) == []
    assert db_instance.get_expenses(house_id) == []
    assert db_instance.get_reimbursements(house_id) == []