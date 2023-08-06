import psycopg2 as pg

from typeguard import typechecked


class PgConnector:
    @typechecked
    def __init__(self, host: str, db_name: str, user: str, password: str):
        super().__init__()
        self._pg_host = host
        self._pg_db_name = db_name
        self._pg_user = user
        self._pg_password = password

    def connect(self):
        return pg.connect(dbname=self._pg_db_name,
                          host=self._pg_host,
                          user=self._pg_user,
                          password=self._pg_password)
