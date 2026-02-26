tools = [
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": (
                "Check bus availability between two cities on a specific travel date. "
                "Use this function when the user asks about available buses."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "The departure city "
                    },
                    "destination": {
                        "type": "string",
                        "description": "The arrival city "
                    },
                    "travel_date": {
                        "type": "string",
                        "description": "Travel date in YYYY-MM-DD format "
                    }
                },
                "required": ["source", "destination"]
            }
        }
    }
]