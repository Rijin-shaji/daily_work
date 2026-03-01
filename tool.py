tools = [
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": (
                "Check bus availability between two cities on a specific travel date. "
                "ALWAYS use this tool when the user asks about buses, routes, schedules, or availability. "
                "Never answer from general knowledge."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "The departure city name, e.g. 'Ernakulam'"
                    },
                    "destination": {
                        "type": "string",
                        "description": "The arrival city name, e.g. 'Kottayam'"
                    },
                    "travel_date": {
                        "type": "string",
                        "description": "Travel date in YYYY-MM-DD format. Optional."
                    }
                },
                "required": ["source", "destination"]
            }
        }
    }
]