import os
import re
import io
import contextlib
from datetime import datetime, timedelta
from groq import Groq
from deep_translator import GoogleTranslator
from new_user import register_user, login_user
from ticket_booking import book_ticket, filter_buses_by_time
from bus_finder import show_buses
from seat_manager import show_available_seats
from support import register_support_request
from bus_delay import check_bus_delay
from next_bus import get_next_bus

# ─────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────
MODEL  = "llama-3.3-70b-versatile"
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Single source of truth for time ranges
TIME_MAP = {
    "1": ("morning",   "05:00", "11:59"),
    "2": ("afternoon", "12:00", "16:59"),
    "3": ("evening",   "17:00", "20:59"),
    "4": ("night",     "21:00", "23:59"),
}

# Keyword → (start, end) for slot detection & filtering
TIME_KEYWORD_MAP = {
    "morning":   ("05:00", "11:59"),
    "afternoon": ("12:00", "16:59"),
    "evening":   ("17:00", "20:59"),
    "night":     ("21:00", "23:59"),
}

# ─────────────────────────────────────────────
#  LANGUAGE HELPERS
# ─────────────────────────────────────────────
def translate_text(text: str, language: str) -> str:
    if language == "malayalam":
        try:
            return GoogleTranslator(source="auto", target="ml").translate(text)
        except Exception:
            return text
    return text

def tprint(text: str, language: str) -> None:
    print(translate_text(str(text), language))

def tinput(prompt: str, language: str) -> str:
    return input(translate_text(prompt, language))


# ─────────────────────────────────────────────
#  GROQ AI FALLBACK
# ─────────────────────────────────────────────
def ask_groq(user_input: str, language: str) -> str:
    system_prompt = (
        "You are a helpful bus-travel assistant for Kerala, India. "
        "Answer questions about bus routes, travel tips, ticket rules, "
        "and general travel advice. Keep answers short and practical."
    )
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_input},
            ],
            max_tokens=512,
        )
        reply = response.choices[0].message.content.strip()
        return translate_text(reply, language)
    except Exception as e:
        return translate_text(f"AI service error: {e}", language)


# ─────────────────────────────────────────────
#  NLP – EXTRACT BOOKING DETAILS
# ─────────────────────────────────────────────
def extract_details(text: str):
    text = text.lower()

    # Source / destination
    match = re.search(r'from\s+(.+?)\s+to\s+(.+?)(?:\s+on\s+|\s+tomorrow|$)', text)
    source      = match.group(1).strip() if match else None
    destination = match.group(2).strip() if match else None

    # Travel date
    travel_date = None
    if "tomorrow" in text:
        travel_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        m1 = re.search(r'\d{4}-\d{2}-\d{2}', text)
        m2 = re.search(r'\d{2}-\d{2}-\d{4}', text)
        if m1:
            travel_date = m1.group()
        elif m2:
            travel_date = datetime.strptime(m2.group(), "%d-%m-%Y").strftime("%Y-%m-%d")

    # Time preference — return string label or None
    time_pref = None
    for keyword in TIME_KEYWORD_MAP:
        if keyword in text:
            time_pref = keyword
            break

    # Passenger name (e.g. "for Rahul")
    name_match     = re.search(r'\bfor\s+([A-Za-z]+)', text)
    passenger_name = name_match.group(1).capitalize() if name_match else None

    return source, destination, travel_date, time_pref, passenger_name


# ─────────────────────────────────────────────
#  PHONE VALIDATION
# ─────────────────────────────────────────────
def get_valid_phone(prompt: str, language: str) -> str:
    while True:
        phone = tinput(prompt, language).strip()
        if re.fullmatch(r'[6-9]\d{9}', phone):
            return phone
        tprint("Invalid phone number. Please enter a valid 10-digit Indian mobile number.", language)


# ─────────────────────────────────────────────
#  AVAILABLE SLOT DETECTOR
# ─────────────────────────────────────────────
def get_available_time_slots(buses) -> list:
    """Return only time-slot labels that actually have buses."""
    available = []
    for label, (start, end) in TIME_KEYWORD_MAP.items():
        slot_buses = buses[
            buses["departure"].astype(str).str[:5].between(start, end)
        ]
        if not slot_buses.empty:
            available.append(label)
    return available


# ─────────────────────────────────────────────
#  BOOKING HANDLER
# ─────────────────────────────────────────────
def handle_booking(user_input: str, user_data: dict, language: str) -> str:
    source, destination, date, time_pref, friend_name = extract_details(user_input)

    # ── Validate mandatory fields ──
    if not source:
        source = tinput("Which city are you travelling from? ", language).strip()
    if not destination:
        destination = tinput("Which city are you travelling to? ", language).strip()
    if not date:
        date = tinput("What date are you travelling? (YYYY-MM-DD): ", language).strip()

    # ── Fetch buses SILENTLY (suppress any prints inside show_buses) ──
    with contextlib.redirect_stdout(io.StringIO()):
        buses = show_buses(source, destination, date)

    if buses is None or buses.empty:
        return "Sorry, no buses found for this route and date."

    # ── Detect which time slots actually have buses ──
    available_slots = get_available_time_slots(buses)

    # ── Ask time preference only from real available slots ──
    if time_pref not in available_slots:
        if len(available_slots) == 1:
            # Only one slot — auto-select, no need to ask
            time_pref = available_slots[0]
            tprint(f"Buses are only available in the {time_pref}.", language)
        else:
            slots_display = " / ".join(available_slots) + " / any"
            pref_input = tinput(
                f"What time do you prefer? ({slots_display}): ",
                language
            ).strip().lower()

            if pref_input in available_slots:
                time_pref = pref_input
            elif pref_input == "any":
                time_pref = None
            else:
                return (
                    f"No buses available at that time. "
                    f"Try: {', '.join(available_slots)}"
                )

    # ── Filter by chosen time ──
    filtered = filter_buses_by_time(buses, time_pref) if time_pref else buses

    if filtered is None or filtered.empty:
        return "No buses available in the selected time slot."

    # ── Auto-select first available bus and seat ──
    selected_bus = filtered.iloc[0]

    seats = show_available_seats(selected_bus["bus_no"], date)
    if not seats:
        return "Sorry, no seats available on this bus."
    seat = seats[0]

    # ── Passenger details from stored user data ──
    if friend_name:
        phone          = get_valid_phone(f"Enter phone number for {friend_name}: ", language)
        friend         = {"name": friend_name, "phone": phone}
        passenger_name = None
        phone_number   = None
    else:
        passenger_name = user_data["name"]
        phone_number   = user_data["phone"]
        friend         = None

    # ── Book directly — no extra confirmation needed ──
    booking = book_ticket(
        selected_bus["bus_no"],
        source,
        destination,
        date,
        passenger_name,
        phone_number,
        seat,
        user_data["user_id"],
        friend_details=friend,
    )

    if "error" in booking:
        return f"Booking failed: {booking['error']}"

    return f"""
══════════════════════════════
       TICKET CONFIRMED ✓
══════════════════════════════
  Passenger  : {booking['passenger_name']}
  Seat       : {booking['seat']}
  Route      : {source.title()} → {destination.title()}
  Departure  : {selected_bus['departure']}
  Date       : {date}
  Booking ID : {booking['booking_id']}
══════════════════════════════
"""


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main():
    print("\n============================")
    print("  Kerala Bus Booking System ")
    print("============================")

    print("\n1. English\n2. Malayalam\n0. Exit")
    lang_choice = input("Select language: ").strip()

    if lang_choice == "2":
        language = "malayalam"
    elif lang_choice == "1":
        language = "english"
    else:
        print("Goodbye!")
        return

    tprint("\n1. New User  (Register)\n2. Existing User  (Login)", language)
    user_choice = tinput("Select: ", language).strip()

    if user_choice == "1":
        user_data = register_user()
    elif user_choice == "2":
        user_data = login_user()
    else:
        tprint("Invalid choice. Exiting.", language)
        return

    if not user_data:
        tprint("Authentication failed. Please try again.", language)
        return

    tprint(f"\nWelcome, {user_data['name']}!", language)
    tprint("You can ask me to:\n  • Book a bus ticket\n  • Check next bus\n  • Check bus delay\n  • File a complaint", language)

    while True:
        user_input = tinput("\nHow can I help you? (type 0 to exit): ", language).strip()

        if not user_input:
            continue

        if user_input == "0":
            tprint("Thank you for using Kerala Bus Booking. Have a safe journey!", language)
            break

        text = user_input.lower()

        if "book" in text:
            result = handle_booking(user_input, user_data, language)
            tprint(result, language)

        elif any(word in text for word in ("complaint", "complain", "issue", "problem", "feedback")):
            msg = tinput("Please describe your issue: ", language).strip()
            if msg:
                res = register_support_request(msg, "Complaint")
                tprint(str(res), language)
            else:
                tprint("No message entered. Support request cancelled.", language)

        elif "next bus" in text:
            src  = tinput("Source city: ", language).strip()
            dst  = tinput("Destination city: ", language).strip()
            date = tinput("Travel date (YYYY-MM-DD): ", language).strip()
            bus  = get_next_bus(src, dst, date)
            tprint(str(bus), language)

        elif "delay" in text:
            bus_no = tinput("Enter bus number: ", language).strip()
            delay  = check_bus_delay(bus_no)
            tprint(str(delay), language)

        else:
            reply = ask_groq(user_input, language)
            tprint(reply, language)


if __name__ == "__main__":
    main()