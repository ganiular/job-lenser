import sqlite3
from flask import g

def connect() -> sqlite3.Connection:
    # return connection stored in global variable holder if exist
    conn = g.get('conn', None)
    if conn is not None:
        print('already on connection')
        return conn
     
    conn = sqlite3.connect(
        database='appdata.db'
    )
    # This tells the connection to return rows that behave like dicts. 
    # This allows accessing the columns by name.
    # For example one can access a field with row_data['column name']
    conn.row_factory = sqlite3.Row

    # store the connection object in a gblobal variable holder
    # so that it can be access for closing
    g.conn = conn
    return conn

def close():
    # remove the connection object from global variable holder
    conn = g.pop('conn', None)
    if conn is not None:
        conn.close()
        print('database closed')

# Regsiter this function with the app response closure listener
# to help close the database connection regardless of error
def on_response_close(error=None):
    if error is not None:
        print('Error on_response_close:', error)
    close()