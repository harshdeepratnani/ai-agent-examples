import requests
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

CALENDLY_API_KEY = os.getenv("CALENDLY_API_KEY")

headers = {
    "Authorization": f"Bearer {CALENDLY_API_KEY}",
    "Content-Type": "application/json"
}

def get_meeting_url():
    """ This function returns the SwiftLife Insurance Company's Calendly meeting URL """

    # Fetch the authenticated user information
    response = requests.get("https://api.calendly.com/users/me", headers=headers)

    if response.status_code == 200:
        user_uri = response.json()["resource"]["uri"]
        print("✅ User URI:", user_uri)
    else:
        print("❌ Error fetching user URI:", response.json())

    # Fetch event types for this user
    response = requests.get(f"https://api.calendly.com/event_types?user={user_uri}", headers=headers)

    print(response)

    if response.status_code == 200:
        event_types = response.json()["collection"]
        
        for event in event_types:
            print("📌 Event Name:", event["name"])
            print("🔗 Event Type URI:", event["uri"])
    else:
        print("❌ Error fetching event types:", response.json())

    return user_uri
