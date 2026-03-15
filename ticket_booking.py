import uuid
import json
from datetime import datetime
from db import conn, cursor

FILE = "ticket_bookings.json"
def book_ticket(bus_no, source, destination, travel_date, passenger_name, phone_number, seat):
    cursor.execute("""
        SELECT * FROM ticket_bookings
        WHERE bus_no=%s AND travel_date=%s AND seats=%s
    """, (bus_no, travel_date, seat))

    if cursor.fetchone():
        return {"error": "Seat already booked. Please choose another seat."}

    booking_id = "TKT-" + str(uuid.uuid4())[:6]
    booking_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {
        "booking_id": booking_id,
        "bus_no": bus_no,
        "source": source,
        "destination": destination,
        "travel_date": travel_date,
        "passenger_name": passenger_name,
        "phone_number": phone_number,
        "seat": seat,
        "booking_time": booking_time,
        "status": "confirmed"
    }

    cursor.execute("""
        INSERT INTO ticket_bookings
        (booking_id, bus_no, source, destination, travel_date,
         passenger_name, phone_number, seats, booking_time, status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        booking_id,
        bus_no,
        source,
        destination,
        travel_date,
        passenger_name,
        phone_number,
        seat,
        booking_time,
        "confirmed"
    ))

    conn.commit()
    try:
        with open(FILE, "r") as f:
            bookings = json.load(f)
    except:
        bookings = []
    bookings.append(data)
    with open(FILE, "w") as f:
        json.dump(bookings, f, indent=4)
    return data