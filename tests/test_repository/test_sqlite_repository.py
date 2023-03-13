import pytest
import sqlite3

from dataclasses import dataclass
from datetime import datetime

from bookkeeper.repository.sqlite_repository import SqliteRepository

DB_FILE = "test4sql_repository.db"
TEST_INT_VALUE = 123
TEST_STR_VALUE = "test sring"

@pytest.fixture
def create_bd():
    with sqlite3.connect(DB_FILE) as con:
        cur = con.cursor()
        cur.execute(f"DROP TABLE IF EXISTS custom")
    with sqlite3.connect(DB_FILE) as con:
        cur = con.cursor()
        cur.execute(f"CREATE TABLE IF NOT EXISTS custom(f1 int, f2 srt)")
    con.close()

@pytest.fixture
def custom_class():
    @dataclass
    class Custom():
        f1: int = TEST_INT_VALUE
        f2: str = TEST_STR_VALUE
        pk: int = 0
    return Custom

@pytest.fixture
def repo(custom_class, create_bd):
    return SQLiteRepository(db_file=DB_FILE, cls=custom_class)

def test_row2obj(repo):
    row = (123, "test__string_row2obj")
    obj = repo._row2obj(10, row)
    assert obj.pk == 10
    assert obj.f1 == 123
    assert obj.f2 == "test_string_row2obj"


def test_crud(repo, custom_class):
    # add
    obj_add = custom_class()
    pk = repo.add(obj_add)
    assert pk == obj_add.pk
    # get
    obj_get = repo.get(pk)
    assert obj_get is not None
    assert obj_get.pk == obj_add.pk
    assert obj_get.f1 == obj_add.f1
    assert obj_get.f2 == obj_add.f2
    # update
    obj_upd = custom_class(f1=10, f2="test_string_crud", pk=pk)
    repo.update(obj_upd)
    obj_get = repo.get(pk)
    assert obj_get == obj_upd
    assert obj_get_upd.field_str == obj_upd.f1
    assert obj_get_upd.field_int == obj_upd.f2
    # delete
    repo.delete(pk)
    assert repo.get(pk) is None

def test_cannot_add_with_pk(repo, custom_class):
    obj = custom_class()
    obj.pk = 1
    with pytest.raises(ValueError):
        repo.add(obj)

def test_cannot_add_without_pk(repo):
    with pytest.raises(ValueError):
        repo.add(0)

def test_cannot_delete_unexistent(repo):
    with pytest.raises(KeyError):
        repo.delete(-1)

def test_cannot_update_unexistent(repo, custom_class):
    obj = custom_class(f1=1, pk=100)
    with pytest.raises(ValueError):
        repo.update(obj)

def test_cannot_update_without_pk(repo, custom_class):
    obj = custom_class(f1=1, pk=0)
    with pytest.raises(ValueError):
        repo.update(obj)

def test_get_unexistent(repo):
    assert repo.get(-1) is None

def test_get_all(repo, custom_class):
    objects = [custom_class() for i in range(5)]
    for o in objects:
        repo.add(o)
    assert repo.get_all() == objects

def test_get_all_with_condition(repo, custom_class):
    objects = []
    for i in range(5):
        o = custom_class(f1=1)
        o.f1 = 1
        o.f2 = 'test'
        repo.add(o)
        objects.append(o)
    assert [objects[0]] == repo.get_all({'f1': 0})
    assert objects == repo.get_all({'f2': 'test'})

def test_get_all_like(repo, custom_class):
    objects = []
    for i in range(5):
        o = custom_class(f1=1)
        o.f1 = "__" + str(i) + "__"
        o.f2 = 'test'
        repo.add(o)
        objects.append(o)
    assert [objects[0]] == repo.get_all_like({'f1': '0'})
    assert objects == repo.get_all_like({'f2': 'test'})
