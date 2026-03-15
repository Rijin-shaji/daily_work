import os
import json
import pandas as pd
from groq import Groq
from test_tool import tools
from searching import check_availability
from support import register_support_request
from bus_delay import check_bus_delay
from next_bus import get_next_bus
from ticket_booking import book_ticket
from bus_finder import show_buses, find_bus
from seat_manager import show_available_seats
from deep_translator import GoogleTranslator

def translate_text(text, language):
    if language == "malayalam":
        return GoogleTranslator(source="auto", target="ml").translate(text)
    return text


def tprint(text, language):
    print(translate_text(text, language))


def tinput(text, language):
    return input(translate_text(text, language))

MODEL = "llama-3.3-70b-versatile"
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
DATASET_FILE = "D:/New folder (2)/Bus_dataset.xlsx"


def run_agent(user_query: str, language: str):
    if language == "malayalam":
        lang_instruction = "Respond ONLY in Malayalam."
    else:
        lang_instruction = "Respond ONLY in English."

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a KSRTC intelligent assistant.\n"
                    "If the user asks about buses or routes, "
                    "you must use the check_availability tool.\n"
                    "Never invent information yourself."
                )
            },
            {"role": "user", "content": user_query}
        ],
        tools=tools,
        tool_choice="auto"
    )

    message = response.choices[0].message

    if message.tool_calls:
        tool_call = message.tool_calls[0]
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        if function_name == "check_availability":
            tool_result = check_availability(**arguments)
        else:
            tool_result = {"error": "Unknown tool"}

        second_response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "Format the result clearly.\n" + lang_instruction
                },
                {"role": "user", "content": user_query},
                message,
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result)
                }
            ]
        )

        return second_response.choices[0].message.content

    return "Sorry, I couldn't process your request."


def format_support_response(data, language):
    if language == "malayalam":
        instruction = "Format the support request clearly in Malayalam."
    else:
        instruction = "Format the support request clearly in English."

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": instruction},
            {"role": "user", "content": json.dumps(data)}
        ]
    )

    return response.choices[0].message.content

def show_available_routes():
    if not os.path.exists(DATASET_FILE):
        return [], []

    df = pd.read_excel(DATASET_FILE)
    sources = sorted(df["Source"].dropna().unique())
    destinations = sorted(df["Destination"].dropna().unique())
    return sources, destinations


if __name__ == "__main__":

    while True:
        print("\nKerala State RTC Intelligent Assistant")
        print("\nSelect Language:")
        print("1. English")
        print("2. Malayalam")
        print("0. Exit / പുറത്തുപോവുക ")
        lang_choice = input("Enter 1, 2 or 0: ")

        if lang_choice == "2":
            language = "malayalam"
            print("\nഭാഷ തിരഞ്ഞെടുക്കപ്പെട്ടു: മലയാളം\n")
        elif lang_choice == "1":
            language = "english"
            print("\nLanguage selected: English\n")
        else:
            print("Goodbye")
            break

        tprint("Select Service:", language)
        tprint("1. Search Bus", language)
        tprint("2. Ask Us (Support)", language)
        tprint("3. Book Ticket", language)
        service_choice = tinput("Choose (1, 2, 3): ", language)

        if service_choice == "1":
            user_input = tinput("\nEnter route (example: Ernakulam to Kottayam): ", language)
            result = run_agent(user_input, language)
            tprint("\nAssistant: " + str(result), language)
            print("-" * 50)

        elif service_choice == "2":

            tprint("\nSupport Options:", language)
            tprint("1. Complaint", language)
            tprint("2. Query", language)
            tprint("3. Suggestion", language)

            support_choice = tinput("Enter 1, 2, or 3: ", language)
            message = tinput("\nDescribe your issue: ", language)

            if support_choice == "1":
                tool_result = register_support_request(message, "Complaint")
                result = format_support_response(tool_result, language)
                tprint("\nAssistant: " + str(result), language)

            elif support_choice == "2":
                if "next bus" in message.lower():
                    sources, destinations = show_available_routes()
                    print("\nAvailable Sources:", ", ".join(sources))
                    print("Available Destinations:", ", ".join(destinations))

                    while True:
                        source = tinput("Enter Source: ", language).strip()
                        destination = tinput("Enter Destination: ", language).strip()

                        if source and destination:
                            break
                        tprint("Please enter both Source and Destination.", language)
                    travel_date = tinput("Enter Travel Date (YYYY-MM-DD): ", language).strip()
                    bus = get_next_bus(source, destination, travel_date)

                    if "bus_no" in bus:
                        tprint(f"""
Next Bus Information

Route       : {source} → {destination}
Bus Number  : {bus['bus_no']}
Departure   : {bus['departure']}
Arrival     : {bus['arrival']}
Bus Type    : {bus['bus_type']}
Fare        : {bus['fare']}
Seats Left  : {bus['available_seats']}
Available Seats  : {bus['available_seats']}
""", language)

                    else:
                        tprint(bus.get("message", "No buses found."), language)
                elif "late" in message.lower() or "delay" in message.lower():
                    bus_number = tinput("\nEnter Bus Number: ", language)
                    delay_info = check_bus_delay(bus_number)
                    if delay_info["status"] == "late":
                        tprint(f"""
Bus Delay Information

Bus Number : {bus_number}
Status     : Late
Delay      : {delay_info['delay_minutes']} minutes
Reason     : {delay_info['reason']}
Updated At : {delay_info['updated_at']}
""", language)
                    else:
                        tprint("""
No delay has been officially reported for this bus.
We will contact the conductor and update the status soon.
Please check again later.
""", language)
                else:
                    tool_result = register_support_request(message, "Query")
                    result = format_support_response(tool_result, language)
                    tprint("\nAssistant: " + str(result), language)

            elif support_choice == "3":

                tool_result = register_support_request(message, "Suggestion")
                result = format_support_response(tool_result, language)
                tprint("\nAssistant: " + str(result), language)
            else:
                tprint("Sorry Wrong option", language)

            print("-" * 50)

        elif service_choice == "3":
          tprint("\nTicket Booking", language)
          passenger_name = tinput("Passenger Name : ", language)
          while True:
              phone_number = tinput("Phone Number : ", language)
              if phone_number.isdigit() and len(phone_number) == 10:
                  break
              else:
                  print("Phone number must be exactly 10 digits.")
          source = tinput("Source : ", language)
          destination = tinput("Destination : ", language)
          travel_date = tinput("Travel Date (YYYY-MM-DD) : ", language)

          while True:
            buses = show_buses(source, destination, travel_date)
            if buses is None:
                continue
            departure = tinput("\nChoose Departure Time : ", language)
            bus_no = find_bus(source, destination, travel_date, departure)
            if not bus_no:
                tprint("Invalid bus selection.", language)
                continue
            available = show_available_seats(bus_no, travel_date)
            if not available:
                print("Choose another bus")
                continue
            seat_number = int(tinput("\nChoose Seat Number : ", language))
            booking = book_ticket(
                bus_no,
                source,
                destination,
                travel_date,
                passenger_name,
                phone_number,
                seat_number
            )
            if "error" in booking:
                tprint(booking["error"], language)
            else:
                tprint(f"""
Ticket Booked Successfully

Booking ID : {booking['booking_id']}
Passenger  : {booking['passenger_name']}
Seat       : {booking['seat']}
Route      : {booking['source']} → {booking['destination']}
Date       : {booking['travel_date']}
""", language)
        else:
            tprint("Sorry wrong option", language)