def get_flights(where_from, to, date, trip, return_date=None):
    from playwright.sync_api import sync_playwright
    import re

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="/snap/bin/chromium",
            headless=False)
        
        page = browser.new_page()
        print("Page is opening...")
        page.goto("https://www.google.com/travel/flights", wait_until="load", timeout=60000)
        # page.pause()

        page.get_by_role("combobox",name="Where from").click()
        search_box=page.get_by_role("combobox",name="Where else?")
        search_box.fill(where_from)
        page.keyboard.press("ArrowDown")
        page.keyboard.press("Enter")
        print("Departure location filled.")
        page.get_by_placeholder("Where to?").fill(to)
        page.get_by_role("option").first.click()
        # page.keyboard.press("Enter")
        if trip=="one way":
            one=page.locator("div.VfPpkd-aPP78e").first.click()
            page.get_by_role("option", name="One way").click()
            page.wait_for_timeout(5000)
            depart=page.get_by_role("textbox", name="Departure").fill(date)
            page.keyboard.press("Enter")
            print("one way trip details filled.")

        elif trip=="round trip":
            one=page.locator("div.VfPpkd-aPP78e").first.click()
            page.get_by_role("option", name="Round trip").click() 
            depart=page.get_by_role("textbox", name="Departure").fill(date)
            if return_date is not None:
                page.get_by_role("textbox", name="return").fill(return_date)
            page.keyboard.press("Enter")
            print("round trip details filled.")

        page.wait_for_timeout(5000)
        
        page.get_by_role("button", name="Search").click()
        page.wait_for_load_state("load") 
        page.wait_for_timeout(6000)
        flights=page.locator("li.pIav2d")
        flight_info=[]
        print(f"Total flights found: {flights.count()}")
        for i in range(flights.count()):
            print(f"Fetching flight {i+1} details...")
            departure_time=flights.nth(i).locator("span[aria-label^='Departure time']").first.inner_text()
            arrival=flights.nth(i).locator("span[aria-label^='Arrival time']").first.inner_text()
            departure_time=departure_time.replace("\u202f"," ").replace("-"," ").strip()
            arrival=arrival.replace("\u202f"," ").strip()
            flight_time=f"{departure_time} - {arrival}"
            
            company=flights.nth(i).locator("div.sSHqwe span").first.inner_text()
            # print(company)
            duration=flights.nth(i).locator("div[aria-label^='Total duration']").first.inner_text()
            # print(duration)
            text=flights.nth(i).inner_text()
            lines=text.splitlines()
            stop_count=0
            for line in lines:
                line=line.strip()
                if re.fullmatch(r"(Nonstop|1 stop|\d+ stops)",line):
                    stop_count=line
                    break

            try:
                layover=flights.nth(i).locator("div[aria-label^='Layover']").first.inner_text()
                
            except:
                layover="0"
                
                
            ruppes=flights.nth(i).locator("span[role='text']").last.inner_text()
            flight_time=flight_time.replace("\u202f"," ").replace("\xa0"," ")
            ruppes=ruppes.replace("\u202f"," ").replace("\xa0"," ")

            flight_info.append({
                "Flight timing":flight_time,
                "Airline":company,
                "Duration":duration,
                "Stops":stop_count,
                "layover":layover,
                "Price":ruppes
                    })
    import json
    flight=json.dumps(flight_info,indent=4,ensure_ascii=False)
    print("Flights details fetched successfully.")
    return flight
    

