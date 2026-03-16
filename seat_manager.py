import pandas as pd
from db import cursor

FILE_PATH = "D:/New folder (2)/Bus_dataset_200.xlsx"

def get_total_seats(bus_no):
    df = pd.read_excel(FILE_PATH)
    df.columns = df.columns.str.strip()
    result = df[df["Bus_No"] == bus_no]
    if result.empty:
        print("Showing some error...Please come after sometime.")
        return 0
    return int(result.iloc[0]["Available_Seats"])

def get_booked_seats(bus_no, travel_date):
    cursor.execute(
        "SELECT seats FROM ticket_bookings WHERE bus_no=%s AND travel_date=%s",
        (bus_no, travel_date)
    )
    rows = cursor.fetchall()
    return [row[0] for row in rows]

def show_available_seats(bus_no, travel_date):
    total_seats = get_total_seats(bus_no)
    booked = get_booked_seats(bus_no, travel_date)
    available = [seat for seat in range(1, total_seats + 1) if seat not in booked]
    if not available:
        print("No seats available")
        return 0
    else:
         print("\nAvailable Seat Numbers:")
         print(available)
         return available

def get_available_seat_count(bus_no, travel_date):
    total_seats = get_total_seats(bus_no)
    booked = get_booked_seats(bus_no, travel_date)
    return max(total_seats - len(booked), 0)