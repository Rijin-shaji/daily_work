import pandas as pd
import os

FILE_PATH = "D:/New folder (2)/Bus_dataset.xlsx"

def check_availability(source: str, destination: str, travel_date: str = None):
    try:
        if not os.path.exists(FILE_PATH):
            return {"error": "Bus schedule data file not found."}

        df = pd.read_excel(FILE_PATH)
        df.columns = df.columns.str.strip()

        source = source.strip().lower()
        destination = destination.strip().lower()

        df["Source"] = df["Source"].astype(str).str.strip().str.lower()
        df["Destination"] = df["Destination"].astype(str).str.strip().str.lower()
        df["Travel_Date"] = pd.to_datetime(df["Travel_Date"]).dt.date

        filtered = df[
            (df["Source"] == source) &
            (df["Destination"] == destination) &
            (df["Available_Seats"] > 0)
        ]

        if travel_date and travel_date.strip() != "":
            travel_date_parsed = pd.to_datetime(travel_date).date()
            filtered = filtered[filtered["Travel_Date"] == travel_date_parsed]

        if filtered.empty:
            return {
                "status": "success",
                "available_buses": [],
                "message": f"No buses available from {source.title()} to {destination.title()}"
                           + (f" on {travel_date}." if travel_date else ".")
            }

        filtered = filtered.sort_values(by="Departure")
        filtered = filtered.head(4)

        buses = []
        for _, row in filtered.iterrows():
            buses.append({
                "ticket_id": row["Ticket_ID"],
                "bus_no": row["Bus_No"],
                "travel_date": str(row["Travel_Date"]),
                "departure": str(row["Departure"]),
                "arrival": str(row["Arrival"]),
                "bus_type": row["Bus_Type"],
                "fare": int(row["Fare"]),
                "available_seats": int(row["Available_Seats"])
            })

        return {
            "status": "success",
            "route": f"{source.title()} → {destination.title()}",
            "total_found": len(buses),
            "available_buses": buses
        }

    except Exception as e:
        return {"error": str(e)}