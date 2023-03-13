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
