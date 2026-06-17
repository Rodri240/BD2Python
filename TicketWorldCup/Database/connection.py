import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="REDACTED_HOST",     
        port = 50006, 
        user="REDACTED_USER",
        password="REDACTED_PASSWORD",
        database="REDACTED_DATABASE"
    )