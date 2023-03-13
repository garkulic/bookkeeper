import pytest
from datetime import datetime, timedelta

from bookkeeper.models.budget import Budget
from bookkeeper.models.expense import Expense

from bookkeeper.repository.memory_repository import MemoryRepository


@pytest.fixture
def repo():
    return MemoryRepository()

def test_create_object():
    b = Budget("Day", 100)
    assert b.pk == 0
    assert b.period == "Day"
    assert b.limit == 100
    assert b.spent == 0

    b = Budget(limit=1000, period="Week", spent=999)
    assert b.pk == 0
    assert b.period == "Week"
    assert b.limit == 1000
    assert b.spent == 999

    with pytest.raises(ValueError):
        b = Budget(limit=100500, period="Year")

def test_can_add_to_repo(repo):
    b = Budget("Day", 100)
    pk = repo.add(b)
    assert b.pk == pk

def test_update_spent_day(repo):
    b = Budget("Day", 100)
    for i in range(5):
        e = Expense(100, 1)
        repo.add(e)
    b.update_spent(repo)
    assert b.spent == 500


