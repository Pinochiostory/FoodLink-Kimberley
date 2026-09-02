import os
from urllib.parse import quote_plus

import mysql.connector
from dotenv import load_dotenv
from sqlalchemy import create_engine


load_dotenv()


def get_connection():
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    return connection


def get_sqlalchemy_engine():

    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    database = os.getenv("DB_NAME")

    encoded_password = quote_plus(password)

    connection_url = (
        f"mysql+mysqlconnector://"
        f"{user}:{encoded_password}@{host}/{database}"
    )

    return create_engine(connection_url)