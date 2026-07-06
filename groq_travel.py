
from groq import Groq
import os


from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)


def recommend(flight, hotels):

    prompt = f"""
    You are a travel advisor.

    Flights:
    {flight}

    Hotels:
    {hotels}

    produce a complete itinerary.

    Consider:
    - Lowest overall price
    - Fewest stops
    - Shortest travel time
    - Good hotel rating
    - Good hotel location

    Explain why you chose them.
    """

    response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert travel planner"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    },
                ],
            )

    recommended=response.choices[0].message.content
    return recommended