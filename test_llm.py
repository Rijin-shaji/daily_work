import os
import json
from groq import Groq
from test_tool import tools
from booking import check_availability

MODEL = "llama-3.3-70b-versatile"
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


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
                    "You are a KSRTC intelligent booking assistant. "
                    "You MUST use the check_availability tool whenever "
                    "a user asks about buses or routes. "
                    + lang_instruction
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
        arguments = json.loads(tool_call.function.arguments)

        # Execute dataset function
        tool_result = check_availability(**arguments)

        second_response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a KSRTC intelligent booking assistant. "
                        "Format the bus details clearly and neatly. "
                        + lang_instruction
                    )
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


if __name__ == "__main__":

    print("Kerala State RTC Intelligent Booking Assistant")
    print("Select Language:")
    print("1. English")
    print("2. Malayalam")

    choice = input("Enter 1 or 2: ")

    if choice == "2":
        language = "malayalam"
        print("\nഭാഷ തിരഞ്ഞെടുക്കപ്പെട്ടു: മലയാളം\n")
    else:
        language = "english"
        print("\nLanguage selected: English\n")

    print("Type '0' to stop.\n")

    while True:
        user_input = input("Ask your question: ")

        if user_input == "0":
            print("Goodbye")
            break

        result = run_agent(user_input, language)
        print("\nAssistant:", result)
        print("-" * 50)