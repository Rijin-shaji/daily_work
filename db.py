import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Rijin@1234",
    database="ksrtc"
)

cursor = conn.cursor()