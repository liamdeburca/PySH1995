"""
Submodule containing utilities for retrieving data from databases.
"""
from typing import Optional, Union, Iterable

class Query:
    """
    Light-weight SQL query builder. 

    This query builder is specifically designed for SH1995 data, and therefore
    lacks the ability to build large, complex queries. For complex operations,
    manipulate the outputted Pandas Dataframe.

    Basic usage:

    with Query.START(name_of_database) as q:
        data = q.FROM(name_of_table)
                .SELECT('z', 'n_u', 'n_l', 'value')
                .WHERE('z == 1') 
                .WHERE('n_l == 1')
                .ORDER_BY('wave', descending=False)
                .LIMIT(100)
                .STOP()
    """
    def __init__(self):
        from sqlite3 import Connection, Cursor
        
        self.connection: Optional[Connection] = None
        self.cursor: Optional[Cursor] = None

        self.table: Optional[str] = None
        self.columns: list[str] = []

        self.where_logic: list[str] = []
        self.order_by_logic: list[tuple[str, str]] = []
        self.limit: Optional[int] = None

    def __enter__(self) -> 'Query':
        return self
    
    def __exit__(self, type, value, traceback) -> None:
        self.cursor.close()
        self.cursor = None

        self.connection.close()
        self.connection = None

    def _build_query(self) -> tuple[list[str], str]:
        """
        Builds the SQL query.
        """
        query_elems: list[str] = []

        assert len(self.columns) > 0
        query_elems.append("SELECT " + ", ".join(self.columns))

        assert self.table is not None
        query_elems.append(f"FROM {self.table}")

        if self.where_logic:
            # Apply WHERE
            query_elems.append(
                "WHERE " + " AND ".join(self.where_logic)
            )

        if self.order_by_logic:
            # Apply ORDER_BY
            f = lambda a: "{} {}".format(*a)
            query_elems.append(
                "ORDER BY " + ", ".join(map(f, self.order_by_logic))
            )
            pass

        if self.limit:
            # Apply LIMIT
            query_elems.append(f"LIMIT {self.limit}")

        query: str = ' '.join(query_elems) + ';'

        return query_elems, query
    
    @property
    def column_info(self):
        """
        Get basic table information.
        """
        return self.cursor.execute(
            "PRAGMA table_info({})".format(self.table)
        ).fetchall()


    @property
    def table_names(self) -> list[str]:
        assert self.connection is not None
        assert self.cursor is not None

        if getattr(self, '_table_names', None) is not None:
            return self._table_names

        query_result: list[tuple] = self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table';",
        ).fetchall()

        if not all([len(tnames) == 1 for tnames in query_result]):
            raise ValueError(
                "Connected database is not valid!"
            )
        
        self._table_names: list[str] = [
            tnames[0] for tnames in query_result
        ]
        
        return self._table_names
    
    @property
    def column_names(self) -> list[str]:
        assert self.connection is not None
        assert self.cursor is not None
        assert getattr(self, 'table') is not None

        if getattr(self, '_column_names', None) is not None:
            return self._column_names

        self._column_names: list[str] = [
            cinfo[1] for cinfo in self.column_info
        ]

        return self._column_names

    def connectToDatabase(
        self, 
        name: Optional[str] = None,
    ) -> 'Query':
        """
        Connects this instance to the designated (or default) database. 
        """
        from .writing import connect_to_db
        _, self.connection = connect_to_db(name=name, replace=False)
        self.cursor = self.connection.cursor()
        return self

    @staticmethod
    def START(
        name: Optional[str] = None,
    ) -> 'Query':
        """
        Creates a Query instance and connects it to a database.
        """
        q = Query()
        return q.connectToDatabase(name=name)
    
    def STOP(self) -> dict:
        """
        Builds the SQL query and retrieves the data.
        """
        from pandas import read_sql_query
        return read_sql_query(
            self._build_query()[1], 
            self.connection,
        ).to_dict(orient='list')
    
    def FROM(
        self,
        table: str,
    ) -> 'Query':
        """
        Specifies the table from which data is queried from. This table must 
        exist. 
        """
        if table not in (table_names := self.table_names):
            raise ValueError(
                f"Table {table} was not found among {table_names}"
            )

        self.table = table

        return self
    
    def SELECT(
        self,
        *column: str,
    ) -> 'Query':
        """
        Specifies which value(s) to retrieve from the database table.
        """
        if len(column) > 1:
            assert '*' not in column
            _ = list(map(self.SELECT, column))
            return self
        
        column = column[0]
        
        if column == '*':
            self.columns.clear()
            self.columns.extend(self.column_names)
        else:
            assert column in self.column_names
            self.columns.append(column)

        return self
    
    def WHERE(
        self,
        column: Union[str, Iterable[str]],
        logic: str,
    ) -> 'Query':
        """
        Applies the specified logic.
        """
        if isinstance(column, str):
            assert column in self.column_names
        else:
            assert all(c in self.column_names for c in column)

        self.where_logic.append(logic)

        return self
    
    def ORDER_BY(
        self,
        column: Union[str, Iterable[str]],
        descending: Union[bool, Iterable[bool]] = False,
    ) -> 'Query':
        """
        Sorts the returned data according to the specified column.
        """
        if isinstance(column, str):
            assert column in self.column_names
            assert isinstance(descending, bool)

            cols: list[str] = [column]
            desc: list[bool] = [descending]
        else:
            assert all(c in self.column_names for c in column)

            cols: list[str] = list(column)
            if isinstance(descending, bool):
                desc: list[bool] = len(column) * [descending]
            else:
                desc: list[bool] = list(descending)
                assert len(cols) == len(desc)

        self.order_by_logic.extend(
            (c, 'DESC' if d else 'ASC') \
            for c, d in zip(cols, desc)
        )

        return self
    
    def LIMIT(
        self,
        limit: int,
    ) -> 'Query':
        """
        Limits the size (no. of rows) of the result.
        """
        assert limit >= 1

        self.limit: int = limit

        return self