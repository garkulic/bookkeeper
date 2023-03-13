"""
Модуль содержит описание репозитория для SQLite
"""
import sqlite3

from inspect import get_annotations
from typing import Any, Optional

from bookkeeper.repository.abstract_repository import AbstractRepository, T

class SqliteRepository(AbstractRepository[T]):
    """
    Репозиторий для SQLite. Хранит данные в БД.
    """
    def __init__(self, db_file: str, cls: type) -> None:
        self.db_file = db_file
        self.table_name = cls.__name__.lower()
        self.fields = get_annotations(cls, eval_str=True)
        self.fields.pop('pk')
        self.obj_cls = cls

    def add(self, obj: T) -> int:
        if getattr(obj, 'pk', None) != 0:
            raise ValueError(f'trying to add object {obj} with filled `pk` attribute')
        names = ', '.join(self.fields.keys())
        p = ', '.join("?" * len(self.fields))
        values = [getattr(obj, f) for f in self.fields]
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute('PRAGMA foreign_keys = ON')
            cur.execute(
                f'INSERT INTO {self.table_name} ({names}) VALUES({p})',
                values
            )
            if (type(cur.lastrowid) is int): 
                obj.pk = cur.lastrowid
        con.close()
        return obj.pk
    
    """ Метод преобразует строку в объект типа Т """
    def _row2obj(self, rowid: int, row: tuple[Any]) -> T:
        kwargs = dict(zip(self.fields, row))
        obj = self.obj_cls(**kwargs)
        obj.pk = rowid
        return obj

    def get(self, pk: int) -> T | None:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            row = cur.execute(
                f'SELECT * FROM {self.table_name} '
                + f'WHERE ROWID=={pk}'
            ).fetchone()
        con.close()
        if row is None:
            return None
        obj = self._row2obj(pk, row)
        return obj
    
    def get_all(self, where: dict[str, Any] | None = None) -> list[T]:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            if where is None: #если условие не задано (по умолчанию), вернуть все записи
                rows = cur.execute(
                    f'SELECT ROWID, * FROM {self.table_name} '
                ).fetchall()
            else:
                fields = " AND ".join([f"{f}=?" for f in where.keys()])
                rows = cur.execute(
                    f'SELECT ROWID, * FROM {self.table_name} '
                    + f'WHERE {fields}',
                    list(where.values())
                ).fetchall()
        con.close()
        return [self._row2obj(r[0], r[1:-1]) for r in rows]
    
    def get_all_like(self, like: dict[str, str]) -> list[T]:
        values = [f"%{v}%" for v in like.values()]
        where = dict(zip(like.keys(), values))
        return self.get_all(where=where)

    def update(self, obj: T) -> None:
        fields = ", ".join([f"{f}=?" for f in self.fields.keys()])
        values = [getattr(obj, f) for f in self.fields]
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(
                f'UPDATE {self.table_name} SET {fields} '
                + f'WHERE ROWID=={obj.pk}',
                values
            )
            if cur.rowcount == 0:
                raise ValueError('No object with such primary key in DB to update.')
        con.close()

    """ Удалить запись """
    def delete(self, pk: int) -> None:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(
                f'DELETE FROM  {self.table_name} '
                + f'WHERE ROWID=={pk}'
            )
            if cur.rowcount == 0:
                raise ValueError('No object with such primary key in DB to delete.')
        con.close()

    """ Удалить все записи """
    def delete_all(self) -> None:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute('PRAGMA foreign_keys = ON')
            cur.execute(f'DELETE FROM {self.table_name}')
            con.close()
