import json
import os
from db import get_connection

JSON_FILE = "users.json"
conn = get_connection()
cursor = conn.cursor()
def load_json():
    if not os.path.exists(JSON_FILE):
        return {}

    with open(JSON_FILE, "r") as f:
        return json.load(f)

def save_json(data):
    with open(JSON_FILE, "w") as f:
        json.dump(data, f, indent=4)

def register_user():
    print("\n--- New User Registration ---")
    user_id = input("Create User ID: ")
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    if cursor.fetchone():
        print(" User already exists!")
        conn.close()
        return None

    password = input("Create Password: ")
    name = input("Name: ")
    gender = input("Gender: ")
    phone = input("Mobile Number: ")
    address = input("Address: ")
    seat_pref = input("Preferred Seat (front/middle/back): ")
    window_seat = input("Window seat (yes/no): ")

    query = """
    INSERT INTO users 
    (user_id, password, name, gender, phone, address, seat_pref, window_seat)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (user_id, password, name, gender, phone, address, seat_pref, window_seat)
    cursor.execute(query, values)
    conn.commit()
    conn.close()

    users_json = load_json()
    users_json[user_id] = {
        "password": password,
        "name": name,
        "gender": gender,
        "phone": phone,
        "address": address,
        "seat_pref": seat_pref,
        "window_seat": window_seat
    }
    save_json(users_json)
    return {
        "user_id": user_id,
        "name": name,
        "phone": phone,
        "seat_pref": seat_pref,
        "window_seat": window_seat
    }

def login_user():
    print("\n--- Login ---")
    user_id = input("User ID: ")
    password = input("Password: ")
    query = """
    SELECT * FROM users 
    WHERE user_id = %s AND password = %s
    """

    cursor.execute(query, (user_id, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        print(" Login successful!")
        return {
            "user_id": user[0],
            "name": user[2],
            "phone": user[4],
            "seat_pref": user[6],
            "window_seat": user[7]
        }
    print(" Invalid credentials")
    return None