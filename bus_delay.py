import json
from datetime import datetime
from db import get_connection

FILE = "bus_delay_data.json"
conn = get_connection()
cursor = conn.cursor()

def update_bus_status(bus_number, status, reason=None, delay_minutes=0):

    data = {
        "bus_number": bus_number,
        "status": status,
        "reason": reason if status == "late" else "No delay reported",
        "delay_minutes": delay_minutes if status == "late" else 0,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        with open(FILE, "r") as f:
            json_data = json.load(f)
    except:
        json_data = {}

    json_data[bus_number] = data

    with open(FILE, "w") as f:
        json.dump(json_data, f, indent=4)

    query = """
    INSERT INTO bus_delay
    (bus_number, status, reason, delay_minutes, updated_at)
    VALUES (%s,%s,%s,%s,%s)
    """

    values = (
        bus_number,
        data["status"],
        data["reason"],
        data["delay_minutes"],
        datetime.now()
    )

    cursor.execute(query, values)
    conn.commit()

    print("\nBus status updated successfully!\n")


def check_bus_delay(bus_number):

    query = """
    SELECT status, reason, delay_minutes, updated_at
    FROM bus_delay
    WHERE bus_number = %s
    ORDER BY updated_at DESC
    LIMIT 1
    """

    cursor.execute(query, (bus_number,))
    result = cursor.fetchone()

    if result:
        return {
            "status": result[0],
            "reason": result[1],
            "delay_minutes": result[2],
            "updated_at": str(result[3])
        }

    return {"status": "unknown"}

if __name__ == "__main__":

    print("\nKSRTC Driver Status Update System\n")

    bus_number = input("Enter Bus Number: ")

    print("\nSelect Status:")
    print("1. On Time")
    print("2. Delayed")

    choice = input("Enter option: ")

    if choice == "1":

        update_bus_status(bus_number, "on_time")

    elif choice == "2":

        reason = input("Enter reason for delay: ")
        delay = int(input("Enter delay minutes: "))

        update_bus_status(bus_number, "late", reason, delay)

    else:
        print("Invalid option")