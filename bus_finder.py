import pandas as pd
from seat_manager import get_available_seat_count

FILE_PATH = "D:/New folder (2)/Bus_dataset.xlsx"
def show_buses(source, destination, travel_date):
    df = pd.read_excel(FILE_PATH)
    df.columns = df.columns.str.strip()
    buses = df[
        (df["Source"].str.lower() == source.lower()) &
        (df["Destination"].str.lower() == destination.lower()) &
        (df["Travel_Date"] == travel_date)
    ]
    if buses.empty:
        print("No buses available for this route.")
        return None

    print("\nAvailable Buses:\n")

    for i, row in buses.iterrows():
        bus_no = row["Bus_No"]
        seat_left = get_available_seat_count(bus_no, travel_date)
        if seat_left == 0:
            print("Seats FULL")
        else:
            print("Seats Left  ")
        print(f"""
Departure : {row['Departure']}
Arrival   : {row['Arrival']}
Bus Type  : {row['Bus_Type']}
Fare      : {row['Fare']}
Seats Left  : {seat_left}
""")

    return buses


def find_bus(source, destination, travel_date, departure):
    df = pd.read_excel(FILE_PATH)
    df.columns = df.columns.str.strip()
    df["Source"] = df["Source"].astype(str).str.lower()
    df["Destination"] = df["Destination"].astype(str).str.lower()
    df["Departure"] = df["Departure"].astype(str)
    result = df[
        (df["Source"].str.lower() == source.lower()) &
        (df["Destination"].str.lower() == destination.lower()) &
        (df["Travel_Date"] == travel_date) &
        (df["Departure"] == departure)
    ]

    if result.empty:
        return None

    return result.iloc[0]["Bus_No"]