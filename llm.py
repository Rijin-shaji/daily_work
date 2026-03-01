import os
import json
from groq import Groq
from test_tool import tools
from test_booking import check_availability

MODEL = "llama-3.3-70b-versatile"
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = (
    "You are a Kerala KSRTC intelligent bus booking assistant. "
    "You MUST call the check_availability tool for every query about buses, routes, schedules, or seat availability. "
    "NEVER answer from your own knowledge or training data. "
    "Only present information returned by the tool."
)

STRICT_RESPONSE_PROMPT = (
    "You are a Kerala KSRTC booking assistant. "
    "Present ONLY the data returned by the check_availability tool. "
    "Do NOT invent, assume, or add any bus timings, fares, or schedules from your own knowledge. "
    "If the tool returns no buses, clearly say: 'No buses found for this route.' "
    "Format the results in a clean, readable way for the user. "
    "Show ticket ID, bus number, departure, arrival, bus type, fare, and available seats for each bus."
"Always format each bus EXACTLY like this, no bold, no markdown, no asterisks:\n\n"
    "Bus 1\n"
    "  Ticket ID      : T001\n"
    "  Bus No         : KL15B1234\n"
    "  Route          : Ernakulam -> Kottayam\n"
    "  Date           : 2026-03-05\n"
    "  Departure      : 08:00:00\n"
    "  Arrival        : 10:00:00\n"
    "  Bus Type       : Express\n"
    "  Fare           : Rs.120\n"
    "  Available Seats: 10\n\n"
    "Repeat this exact format for every bus. No asterisks, no markdown, no bullet points."
)

def run_agent(user_query: str):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_query}
        ],
        tools=tools,
        tool_choice={
            "type": "function",
            "function": {"name": "check_availability"}
        }
    )

    message = response.choices[0].message

    if message.tool_calls:
        tool_call = message.tool_calls[0]
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        if function_name == "check_availability":
            tool_result = check_availability(**arguments)

            second_response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": STRICT_RESPONSE_PROMPT},
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

    return (
        "I was unable to fetch bus data at this time. "
        "Please try again or visit the KSRTC website."
    )


if __name__ == "__main__":
    print("Kerala State RTC Intelligent Booking Assistant")
    print("Type '0' to exit.\n")

    while True:
        user_input = input("Ask your question: ").strip()
        if user_input.lower() == "0":
            print("Goodbye!")
            break
        if not user_input:
            continue

        result = run_agent(user_input)
        print(f"\nAssistant: {result}")
        print("-" * 50)