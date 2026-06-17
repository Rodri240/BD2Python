import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="mysql.reto-ucu.net",     
        port = 50006, 
        user=" xr_g6_admin",
        password="OBLBD2ST",
        database="XR_Grupo6"
    )