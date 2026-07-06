from datetime import datetime

from groq_travel import recommend
from travel import get_flights
from hotel import get_hotels


def prompt_non_empty(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Error: input cannot be empty. Please try again.")


def parse_date(value):
    for fmt in ("%b %d", "%B %d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise ValueError("invalid date")


def prompt_future_date(prompt, message):
    while True:
        value = prompt_non_empty(prompt)
        try:
            entered_date = parse_date(value).replace(year=datetime.now().year)
            if entered_date<=datetime.now().date():
                entered_date=entered_date.replace(year=datetime.now().year+1)
        except ValueError:
            print("Error: please enter a valid date like 'aug 1' or 'August 1'.")
            continue

        today = datetime.now().date()
        if entered_date <= today:
            print(f"Error: {message}. Please try again.")
            continue

        return value


def prompt_return_date(prompt, departure_date):
    while True:
        value = prompt_non_empty(prompt)
        try:
            return_date = parse_date(value).replace(year=datetime.now().year)
        except ValueError:
            print("Error: please enter a valid date like 'aug 1' or 'August 1'.")
            continue

        if return_date <= departure_date:
            print("Error: return date must be greater than departure date. Please try again.")
            continue

        return value


def prompt_date_range(checkin_prompt, checkout_prompt):
    while True:
        checkin = prompt_future_date(checkin_prompt, "check-in date must be greater than today")
        checkout = prompt_future_date(checkout_prompt, "check-out date must be greater than today")

        try:
            checkin_date = parse_date(checkin).replace(year=datetime.now().year)
            checkout_date = parse_date(checkout).replace(year=datetime.now().year)
        except ValueError:
            continue

        if checkout_date <= checkin_date:
            print("Error: check-out date must be after check-in date. Please try again.")
            continue

        return checkin, checkout


location = prompt_non_empty("From where are you departing: ")
to = prompt_non_empty("To where are you going: ")
date = prompt_future_date("When are you departing(month day): ", "departure date must be greater than today")

return_date = None
while True:
    trip = input("What type is your trip(one way/round trip): ").strip().lower()
    if trip in {"one way", "one-way", "oneway"}:
        trip = "one way"
        break
    if trip in {"round trip", "round-trip", "roundtrip"}:
        trip = "round trip"
        departure_date_obj = parse_date(date).replace(year=datetime.now().year)
        return_date = prompt_return_date("When are you returning(month day): ", departure_date_obj)
        break
    print("Error: please enter 'one way' or 'round trip'.")

flight = get_flights(location, to, date, trip, return_date)

print("=" * 60)
print("FOR HOTEL")
print("=" * 60)

destination = prompt_non_empty("Destination: ")
checkin, checkout = prompt_date_range(
    "Check-in  (e.g. aug 1):  ",
    "Check-out (e.g. aug 5):  ",
)

while True:
    persons = input("Persons:  ").strip()
    if persons.isdigit() and int(persons) > 0:
        break
    print("Error: please enter a positive number of persons.")

hotels = get_hotels(destination, checkin, checkout, persons)
print("=" * 60)
print("AI Travel recommendation")
print("=" * 60)
answer = recommend(flight, hotels)

print(answer)