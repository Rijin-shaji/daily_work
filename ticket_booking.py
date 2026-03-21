import uuid
import json
from datetime import datetime
from db import get_connection

FILE = "ticket_bookings.json"
TIME_MAP = {
    "morning":   ("05:00", "11:59"),
    "afternoon": ("12:00", "16:59"),
    "evening":   ("17:00", "20:59"),
    "night":     ("21:00", "23:59"),
}

def filter_buses_by_time(buses, time_pref):
    """
    buses     : pandas DataFrame returned by show_buses()
    time_pref : string label e.g. "morning", "afternoon" or None
    returns   : filtered DataFrame
    """
    if not time_pref or time_pref not in TIME_MAP:
        return buses

    start, end = TIME_MAP[time_pref]
    filtered = buses[
        buses["Departure"].astype(str).str[:5].between(start, end)
    ]
    return filtered

def book_ticket(bus_no, source, destination, travel_date,
                passenger_name, phone_number, seat, user_id,
                time_pref=None, friend_details=None):
    conn   = get_connection()
    cursor = conn.cursor()

    if friend_details:
        passenger_name = friend_details.get("name")
        phone_number   = friend_details.get("phone")

    if not seat:
        conn.close()
        return {"error": "No seat available."}

    cursor.execute("""
        SELECT 1 FROM ticket_bookings
        WHERE bus_no=%s AND travel_date=%s AND seats=%s
    """, (bus_no, travel_date, seat))

    if cursor.fetchone():
        conn.close()
        return {"error": "Seat already booked. Please choose another seat."}

    booking_id   = "TKT-" + str(uuid.uuid4())[:6]
    booking_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data = {
        "booking_id":     booking_id,
        "user_id":        user_id,
        "bus_no":         bus_no,
        "source":         source,
        "destination":    destination,
        "travel_date":    travel_date,
        "passenger_name": passenger_name,
        "phone_number":   phone_number,
        "seat":           seat,
        "time_preference":time_pref,
        "booking_time":   booking_time,
        "status":         "confirmed",
    }

    cursor.execute("""
        INSERT INTO ticket_bookings
        (booking_id, user_id, bus_no, source, destination, travel_date,
         passenger_name, phone_number, seats, booking_time, status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        booking_id,
        user_id,
        bus_no,
        source,
        destination,
        travel_date,
        passenger_name,
        phone_number,
        seat,
        booking_time,
        "confirmed",
    ))
    conn.commit()
    conn.close()
    try:
        with open(FILE, "r") as f:
            bookings = json.load(f)
    except Exception:
        bookings = []
    bookings.append(data)
    with open(FILE, "w") as f:
        json.dump(bookings, f, indent=4)
    return data