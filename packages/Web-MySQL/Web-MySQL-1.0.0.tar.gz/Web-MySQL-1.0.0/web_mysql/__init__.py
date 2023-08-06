"""
Web-MySQL: A pure Python mysql connect tool which base on PyMysql
Copyright (c) 2020 Web-MySQL contributors
...略
"""
import pymysql


class Connector:

    def __init__(self):
        """
        MySQL connector parameters init.
        """
        self.host = "localhost"
        self.user = "root"
        self.password = None
        self.database = None

    def connect(self):
        """
        A connection creation function.
        :return: mysql connection
        """
        return pymysql.connect(self.host, self.user, self.password, self.database)

    def executor(self, sql, values=None):
        """
        Executor mysql sql command.
        :param sql: The mysql command
        :param values: Parameter values for the mysql command
        :return: Don't return anything
        """
        connection = self.connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, values)
        finally:
            connection.commit()
            connection.close()

    def fetchone(self, sql, value=None):
        """
        Execute mysql select command and return a cursor fetchone result.
        :param sql: The mysql command
        :param value: Parameter values for the mysql command
        :return: cursor.fetchone()
        """
        connection = self.connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, value)
                fetch_result = cursor.fetchone()
        finally:
            connection.close()
        return fetch_result

    def fetchall(self, sql, value=None):
        """
        Execute mysql select command and return cursor fetchall result.
        :param sql: The mysql command
        :param value: Parameter values for the mysql command
        :return: cursor.fetchall()
        """
        connection = self.connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, value)
                fetch_result = cursor.fetchall()
        finally:
            connection.close()
        return fetch_result
