from datetime import datetime, timedelta
import pytest

from bookkeeper.models.budget import Budget
from bookkeeper.models.expense import Expense

from bookkeeper.repository.memory_repository import MemoryRepository


@pytest.fixture
def repo():
    return MemoryRepository()


def test_create_object():
    b = Budget(5000, "day")
    assert b.pk == 0
    assert b.period == "day"
    assert b.limit == 10000
    assert b.spent == 0

    b = Budget(limit=5000, period="week", spent=100)
    assert b.pk == 0
    assert b.period == "week"
    assert b.limit == 5000
    assert b.spent == 1000

    with pytest.raises(ValueError):
        b = Budget(limit=1000, period="year")


def test_can_add_to_repo(repo):
    b = Budget(1000, "day")
    pk = repo.add(b)
    assert b.pk == pk


def test_update_spent_day(repo):
    b = Budget(1000, "day")
    for i in range(5):
        e = Expense(1000, 1)
        repo.add(e)
    b.update_spent(repo)
    assert b.spent == 5000


def test_update_spent_month(repo):
    b = Budget(1000, "month")
    date = datetime.now().isoformat()[:8]
    for i in range(5):
        e = Expense(1000, 1, expense_date=date+f"{i*5+1}")
        repo.add(e)
    e = Expense(1000, 1, expense_date=date[:5]+"13-01")
    repo.add(e)
    b.update_spent(repo)
    assert b.spent == 5000


def test_update_spent_week(repo):
    b = Budget(100, "week")
    date = datetime.now().isoformat()[:10]
    weekday_now = datetime.now().weekday()
    day_now = datetime.fromisoformat(date)
    first_week_day = day_now - timedelta(days=weekday_now)
    for i in range(9):
        day = first_week_day + timedelta(days=i-1)
        e = Expense(100, 1, expense_date=day.isoformat(
            sep='\t', timespec='minutes'))
        repo.add(e)
    b.update_spent(repo)
    assert b.spent == 700
