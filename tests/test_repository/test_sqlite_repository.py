import pytest
import sqlite3

from dataclasses import dataclass
from datetime import datetime

from bookkeeper.repository.sqlite_repository import SqliteRepository

DB_FILE = "test4sql_repository.db"
TEST_INT_VALUE = 73
TEST_STR_VALUE = "test sring"

@pytest.fixture
def custom_class():
    @dataclass
    class Custom():
        int_value: int = TEST_INT_VALUE
        str_value: str = TEST_STR_VALUE
        date_value: str = str(datetime.datetime.now())
        pk: int = 0
    return Custom

@pytest.fixture
def drop_table():
    with sqlite3.connect(DB_FILE) as con:
        cur = con.cursor()
        cur.execute("DROP TABLE IF EXISTS custom")

@pytest.fixture
def create_bd():
    with sqlite3.connect(DB_FILE) as con:
        cur = con.cursor()
        cur.execute(f"CREATE TABLE IF NOT EXISTS custom(int_value int, str_value srt)")
    con.close()

@pytest.fixture
def repo(custom_class, create_bd):
    return SqliteRepository(db_file=DB_FILE, cls=custom_class)

def test_crud(repo, custom_class):
    # create object
    obj = custom_class()
    # add
    pk = repo.add(obj)
    assert pk == obj.pk
    # get
    assert repo.get(pk) is not None
    obj_get = repo.get(pk)
    assert repo.get(pk) == obj #проверяем, что по индексу pk верно получаем объект
    assert obj_get.int_value == obj.int_value
    assert obj_get.str_value == obj.str_value
    assert obj_get.date_value == obj.date_value
    
    # update
    obj2 = custom_class(int_value = 37, str_value = "test str2", date_value = "1999-10-04 07:37:00" )
    obj2.pk = pk
    repo.update(obj2)
    assert repo.get(pk) == obj2
    
    # delete
    repo.delete(pk)
    assert repo.get(pk) is None
    repo.delete_all()

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
    obj = custom_class()
    with pytest.raises(ValueError):
        repo.update(obj)

def test_cannot_update_without_pk(repo, custom_class):
    obj = custom_class()
    with pytest.raises(ValueError):
        repo.update(obj)

def test_get_unexistent(repo):
    assert repo.get(-1) is None

def test_get_all(repo, custom_class):
    repo.delete_all()
    objects = [custom_class() for i in range(5)]
    for o in objects:
        repo.add(o)
    assert repo.get_all() == objects

def test_get_all_with_condition(repo, custom_class):
    objects = []
    for i in range(5):
        o = custom_class()
        o.int_value = i
        o.str_value = 'test string'
        repo.add(o)
        objects.append(o)
    assert [objects[0]] == repo.get_all({'int_value': 0})
    assert objects == repo.get_all({'str_value': 'test string'})

def test_get_all_like(repo, custom_class):
    objects = []
    for i in range(5):
        o = custom_class()
        o.int_value = "__" + str(i) + "__"
        o.str_value = 'test string'
        repo.add(o)
        objects.append(o)
    assert [objects[0]] == repo.get_all_like({'int_value': '0'})
    assert objects == repo.get_all_like({'str_value': 'test srting'})

def test_delete_all(repo, custom_class):
    objects = []
    objects = [custom_class() for i in range(5)]
    for o in objects:
        repo.add(o)
    repo.delete_all()
    assert repo.get_all() == None

