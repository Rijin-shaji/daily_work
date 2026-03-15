from datetime import datetime
from searching import check_availability

def get_next_bus(source, destination, travel_date):
    """
    Returns the next bus for the given route and date.
    """
    result = check_availability(source, destination, travel_date)
    if "error" in result:
        return result

    buses = result.get("available_buses", [])
    if not buses:
        return {"message": "No buses available for this route."}

    current_time = datetime.now().time()

    for bus in buses:
        departure_time = datetime.strptime(bus["departure"], "%H:%M:%S").time()
        if departure_time > current_time:
            return bus
    return {"message": "No more buses available today."}