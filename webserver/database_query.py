from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response


class Database(object):

    def __init__(self, database_user, passwd, ip_addr, database_location):
        self.database_uri = "postgresql://{}:{}@{}/{}".format(database_user, passwd, ip_addr, database_location)
        self.engine = create_engine(self.database_uri)

        self.flask_g = None
    
    @app.context         
    def engine_connect(self, flask_g):
        self.flask_g = flask_g
        self.flask_g = self.engine.connect()

    def engine_close(self):
        self.flask_g.conn.close()


    def get_list_of_names(self):
        cursor = self.flask_g.conn.execute("SELECT name FROM test")
        names = []
        for result in cursor:
            names.append(result['name'])
        cursor.close()
        return names
    
    def add_name(self, name):
      cmd = 'INSERT INTO test(name) VALUES (:name1)';
      flask_g.conn.execute(text(cmd), name1 = name);



