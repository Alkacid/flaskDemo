import mysql.connector
import pytest
from flask import Flask

config = {
    'user': 'root',
    'password': '+654',
    'host': 'localhost',
    'database': 'lab1',
    'raise_on_warnings': True
}

app = Flask(__name__)


@pytest.mark.p2
def test_1(self):
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()

    q = 'describe book'
    cursor.execute(q)
    print(cursor.fetchall())
