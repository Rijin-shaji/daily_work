import uuid
import json
from datetime import datetime
from db import get_connection

FILE = "support_requests.json"
conn = get_connection()
cursor = conn.cursor()
def register_support_request(message, request_type):
    request_id = "KSRTC-" + str(uuid.uuid4())[:6]
    data = {
        "request_id": request_id,
        "type": request_type,
        "message": message,
        "status": "registered",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        with open(FILE, "r") as f:
            json_data = json.load(f)

            if isinstance(json_data, dict):
                json_data = [json_data]

    except:
        json_data = []
    json_data.append(data)
    with open(FILE, "w") as f:
        json.dump(json_data, f, indent=4)

    try:
        query = """
        INSERT INTO support_requests
        (request_id, type, message, status, created_at)
        VALUES (%s,%s,%s,%s,%s)
        """
        values = (
            data["request_id"],
            data["type"],
            data["message"],
            data["status"],
            datetime.now()
        )

        cursor.execute(query, values)
        conn.commit()

    except Exception as e:
        print("MySQL Error:", e)

    return data