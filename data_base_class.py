import psycopg2
import urllib.parse as urlparse
from psycopg2 import Error
import os


class DataBase:

    def __init__(self, *args):

        url = urlparse.urlparse(os.environ['DATABASE_URL'])
        dbname = url.path[1:]
        user = url.username
        password = url.password
        host = url.hostname
        port = url.port
        self.connection = psycopg2.connect(user=user,
                                           # пароль, который указали при установке PostgreSQL
                                           password=password,
                                           host=host,
                                           port=port,
                                           database=dbname)
        self.cursor = self.connection.cursor()
        self.err = ""


    def read_all(self, table_name: str):
        sql_query = f"SELECT * FROM {table_name}"
        try:
            self.cursor.execute(sql_query)
            record = self.cursor.fetchall()
            self.close()
            return record

        except (Exception, Error) as error:
            self.err = error
            self.close()


    def read_one(self, table_name, target):
        sql_query = f"SELECT * FROM {table_name} WHERE userid={target}"
        try:
            self.cursor.execute(sql_query)
            record = self.cursor.fetchone()
            self.close()
            return record

        except (Exception, Error) as error:
            self.err = error
            self.close()


    def insert(self, user_id):
        try:
            sql_query = f"INSERT INTO subscribes (userid) VALUES ({user_id}) ON CONFLICT DO NOTHING"
            self.cursor.execute(sql_query)
            self.connection.commit()
            self.close()

        except (Exception, Error) as error:
            self.err = error
            self.close()

    def update(self, table, field, new_value, target):
        try:
            sql_query = f"UPDATE {table} SET {field} = '{new_value}' WHERE userid={target}"
            self.cursor.execute(sql_query)
            self.connection.commit()
            self.close()
            return 'Успешно обновлено'

        except (Exception, Error) as error:
            self.err = error
            self.close()


    def delete(self, table, target):
        try:
            sql_query = f"DELETE FROM {table} WHERE userid={target}"
            self.cursor.execute(sql_query)
            self.connection.commit()
            self.close()
        except (Exception, Error) as error:
            self.err = error
            self.close()

    def close(self):
        self.cursor.close()
        self.connection.close()
        if self.err:
            print('Ошибка при работе с PostgreSQL: \n')
            print(self.err)


if __name__ == '__main__':
    test = DataBase()
    print(test.delete('subscribes', 100))
