import os
import json
from groq import Groq
from tool import tools
from booking import check_availability

MODEL = "llama-3.3-70b-versatile"
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def run_agent(user_query: str):

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a KSRTC intelligent booking assistant. "
                    "You MUST use the check_availability tool whenever a user asks about buses, routes, or availability. "
                    "Do NOT answer from general knowledge. Always call the tool."
                )
            },
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
                    {"role": "system", "content": "You are a KSRTC intelligent booking assistant."},
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
    return {"message": message.content}

if __name__ == "__main__":
    print(" Kerala State RTC Intelligent Booking Assistant")
    print("Type '0' to stop.\n")

    while True:
        user_input = input("Ask your question: ")

        if user_input.lower() in ["0"]:
            print("Goodbye")
            break

        result = run_agent(user_input)

        print("\nAssistant:", result)
        print("-" * 50)