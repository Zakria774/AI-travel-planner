

✈️ AI Travel Planner

Overview

AI Travel Planner is a Python application that automates travel planning by combining web scraping and AI recommendations.

The application searches for:

* ✈️ Flights using Google Flights (Playwright)
* 🏨 Hotels using Booking.com (Playwright)

It then sends the collected data to the Groq API, which analyzes all available options and recommends the best itinerary based on price, travel time, hotel quality, and location.

⸻

Features

* Automated Google Flights search
* Automated Booking.com hotel search
* AI-powered itinerary recommendation using Groq LLM
* Input validation and error handling
* Supports one-way and round-trip flights
* Hotel rating and location extraction
* Clean modular Python architecture

⸻

Technologies Used

* Python
* Playwright
* Groq API
* python-dotenv
* Git & GitHub

⸻

Project Structure

AI-travel-planner/
│
├── main.py              # Main application
├── travel.py            # Google Flights scraper
├── hotel.py             # Booking.com scraper
├── groq_travel.py       # AI recommendation module
├── .env                 # API key (ignored)
├── .gitignore
└── README.md

⸻

Installation

Clone the repository

git clone https://github.com/Zakria774/AI-travel-planner.git

Install dependencies

pip install playwright
pip install groq
pip install python-dotenv

Install Playwright browsers

playwright install

Create a .env file

groq_api_key=YOUR_API_KEY

Run the application

python main.py

⸻

How It Works

1. User enters travel information.
2. Google Flights is scraped automatically.
3. Booking.com hotels are scraped automatically.
4. Flight and hotel data are sent to Groq.
5. Groq recommends the best complete itinerary.

⸻

Future Improvements

* Weather integration
* Restaurant recommendations
* Attraction suggestions
* Interactive GUI
* PDF itinerary export
* Multiple hotel booking websites
* Multi-city trip planning

⸻

Example Output

Recommended Flight:
✓ Lowest price
✓ One stop
✓ Short travel duration
Recommended Hotel:
✓ Excellent rating
✓ Close to city centre
✓ Best value for money
Reason:
This itinerary offers the lowest overall cost while maintaining excellent hotel quality and minimizing travel time.

⸻

Author

Muhammad Zakria

GitHub: https://github.com/Zakria774

⸻
* Real-world problem solving

It covers several skills employers look for in Python and automation roles.
