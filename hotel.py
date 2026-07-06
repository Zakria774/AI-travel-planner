def get_hotels(destination, checkin_raw, checkout_raw, persons_raw):
    import logging
    import json
    from datetime import datetime
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
    
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    log = logging.getLogger(__name__)

    def parse_date(date_str):
        date_str = date_str.strip()
        current_year = datetime.now().year
        for fmt in ["%b %d", "%B %d"]:
            try:
                parsed = datetime.strptime(date_str, fmt)
                result = parsed.replace(year=current_year)
                if result < datetime.now():
                    result = parsed.replace(year=current_year + 1)
                return result.strftime("%Y-%m-%d")
            except ValueError:
                continue
        raise ValueError(f"Cannot parse '{date_str}'. Use format like 'jul 8' or 'august 10'")


    def advance_calendar_to(page, target_date_str):
        for _ in range(12):
            cell = page.locator(f'span[data-date="{target_date_str}"]')
            if cell.count() > 0 and cell.first.is_visible():
                return
            try:
                next_btn = page.locator('[aria-label="Next month"]')
                if not next_btn.is_visible():
                    next_btn = page.locator('button[data-testid="searchbox-datepicker-calendar-header-next-month"]')
                next_btn.click(timeout=3000)
                page.wait_for_timeout(600)
            except PlaywrightTimeoutError:
                log.warning("Could not advance calendar month")
                break


    try:
        checkin  = parse_date(checkin_raw)
        checkout = parse_date(checkout_raw)
        persons  = int(persons_raw)
    except (ValueError, TypeError) as e:
        log.error(e)
        raise SystemExit(1)

    log.info("Searching %s | %s → %s | %d person(s)", destination, checkin, checkout, persons)

    # ── Browser ───────────────────────────────────────────────────────────────────

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="/snap/bin/chromium",
            headless=False,
            slow_mo=50
        )
        page = browser.new_page()
        page.set_default_timeout(15000)

        # ── 1. Open Booking.com ───────────────────────────────────────────────────
        log.info("Opening Booking.com ...")
        page.goto("https://www.booking.com", wait_until="domcontentloaded")
        page.wait_for_timeout(5000)


        # ── 2. Dismiss cookie banner ──────────────────────────────────────────────
        try:
            page.get_by_role("button", name="Dismiss sign-in info.").click()
        except:
            pass
        # ── 3. Fill destination ───────────────────────────────────────────────────
        log.info("Filling destination: %s", destination)

        # click the destination input
        try:
            page.get_by_role("button", name="Dismiss sign-in info.").click()
        except:
            pass
        dest_input = page.locator('[data-testid="destination-container"] input').first
        dest_input.click(timeout=5000)
        page.wait_for_timeout(500)

        # clear whatever is in the box first
        dest_input.fill("")
        dest_input.fill(destination)
        log.info("Typed destination, waiting for autocomplete ...")

        # wait for autocomplete results immediately
        page.wait_for_selector('[data-testid="autocomplete-result"]', timeout=8000)
        page.wait_for_timeout(1000)  # small pause so dropdown stabilizes

        # click first result before Booking.com overwrites the field
        first_result = page.locator('[data-testid="autocomplete-result"]').first
        first_result.wait_for(state="visible", timeout=5000)
        first_result.click()
        log.info("Selected first autocomplete result")

        # wait until destination field is stable (no more dropdown)
        try:
            page.wait_for_selector('[data-testid="autocomplete-result"]', state="hidden", timeout=5000)
        except PlaywrightTimeoutError:
            pass
        page.wait_for_timeout(800)

        # ── 4. Open calendar ──────────────────────────────────────────────────────
        log.info("Opening date picker ...")
        page.locator('[data-testid="searchbox-datepicker-calendar"]').click()

        # wait until calendar cells are visible
        page.wait_for_selector('span[data-date]', timeout=8000)
        page.wait_for_timeout(500)

        # ── 5. Click check-in ─────────────────────────────────────────────────────
        log.info("Selecting check-in date: %s", checkin)
        advance_calendar_to(page, checkin)
        checkin_cell = page.locator(f'span[data-date="{checkin}"]').first
        checkin_cell.wait_for(state="visible", timeout=5000)
        checkin_cell.click()
        log.info("Check-in date clicked")
        page.wait_for_timeout(600)

        # ── 6. Click check-out ────────────────────────────────────────────────────
        log.info("Selecting check-out date: %s", checkout)
        advance_calendar_to(page, checkout)
        checkout_cell = page.locator(f'span[data-date="{checkout}"]').first
        checkout_cell.wait_for(state="visible", timeout=5000)
        checkout_cell.click()
        log.info("Check-out date clicked")
        page.wait_for_timeout(600)

        # close calendar - try footer button, then Escape
        try:
            footer_btn = page.locator('[data-testid="searchbox-datepicker-footer-button"]')
            if footer_btn.is_visible():
                footer_btn.click(timeout=3000)
                log.info("Calendar closed via footer button")
            else:
                page.keyboard.press("Escape")
        except PlaywrightTimeoutError:
            page.keyboard.press("Escape")

        # wait until calendar is gone
        try:
            page.wait_for_selector('span[data-date]', state="hidden", timeout=3000)
        except PlaywrightTimeoutError:
            pass  # calendar may stay open, that's ok
        page.wait_for_timeout(500)

        # ── 7. Occupancy ──────────────────────────────────────────────────────────
        log.info("Setting occupancy to %d adult(s) ...", persons)
        page.locator('[data-testid="occupancy-config"]').click()

        # wait for popup to be visible before interacting
        page.wait_for_selector('[data-testid="occupancy-popup"]', state="visible", timeout=5000)
        log.info("Occupancy popup is open")

        current_adults = 2
        diff = persons - current_adults

        if diff > 0:
            for _ in range(diff):
                page.locator('[data-testid="occupancy-popup"] [aria-label="Increase number of Adults"]').click()
                page.wait_for_timeout(300)
        elif diff < 0:
            for _ in range(abs(diff)):
                page.locator('[data-testid="occupancy-popup"] [aria-label="Decrease number of Adults"]').click()
                page.wait_for_timeout(300)

        # close popup - try done button first
        closed = False
        for done_selector in [
            '[data-testid="occupancy-config-done-button"]',
            'button:has-text("Done")',
            'button:has-text("Apply")'
        ]:
            try:
                btn = page.locator(done_selector)
                if btn.is_visible():
                    btn.click(timeout=3000)
                    closed = True
                    log.info("Occupancy popup closed via: %s", done_selector)
                    break
            except PlaywrightTimeoutError:
                continue

        if not closed:
            # click outside the popup
            page.mouse.click(400, 100)
            log.info("Occupancy popup closed by clicking outside")

        # wait for popup to actually disappear
        try:
            page.wait_for_selector('[data-testid="occupancy-popup"]', state="hidden", timeout=4000)
            log.info("Popup confirmed closed")
        except PlaywrightTimeoutError:
            log.warning("Popup may still be visible, proceeding anyway")
        page.wait_for_timeout(500)

        # ── 8. Submit search ──────────────────────────────────────────────────────
        log.info("Clicking search button ...")
        search_btn = page.locator("button[type='submit']")
        search_btn.wait_for(state="visible", timeout=5000)
        search_btn.click()

        # ── 9. Wait for results ───────────────────────────────────────────────────
        log.info("Waiting for results ...")
        try:
            page.wait_for_selector('[data-testid="property-card"]', timeout=20000)
            page.wait_for_timeout(2000)  # let prices settle
        except PlaywrightTimeoutError:
            log.error("Results did not load - may be CAPTCHA or layout change")
            browser.close()
            raise SystemExit(1)

        # ── 10. Extract hotels ────────────────────────────────────────────────────
        log.info("Extracting results ...")
        cards = page.locator('[data-testid="property-card"]')
        total = min(cards.count(), 10)
        log.info("Found %d hotel cards", total)

        hotels = []
        for i in range(total):
            card = cards.nth(i)

            try:
                name = card.locator('[data-testid="title"]').inner_text(timeout=2000).strip()
            except PlaywrightTimeoutError:
                name = "N/A"

            try:
                price = card.locator('[data-testid="price-and-discounted-price"]').inner_text(timeout=2000).strip()
            except PlaywrightTimeoutError:
                price = "Price not available"

            try:
                rating = card.locator('[data-testid="review-score"]').inner_text(timeout=2000)
                lines=rating.splitlines()
                if len(lines)>=3:
                    score=lines[1]
                    text=lines[2]
                    rating=f"{score}/10 ({text})"

            except PlaywrightTimeoutError:
                rating = "No rating"

            try:
                location = card.locator('[data-testid="address-link"]').inner_text(timeout=2000).strip()
            except PlaywrightTimeoutError:
                location = "Location not available"

            try:
                link = card.locator("a").first.get_attribute("href") or ""
                if link and not link.startswith("http"):
                    link = "https://www.booking.com" + link
                if ".html" in link:
                    link=link.split(".html")[0]+".html"
            except PlaywrightTimeoutError:
                link = "https://www.booking.com"

            hotels.append({
                "id":       i + 1,
                "name":     name,
                "price":    price,
                "rating":   rating,
                "location": location,
                "url":      link,
            })
            log.info("  [%d] %s — %s", i + 1, name, price)

        browser.close()

    # ── Print results ─────────────────────────────────────────────────────────────
    # print("\n" + "="*60)
    # print(f"  {destination}  |  {checkin_raw} → {checkout_raw}  |  {persons} person(s)")
    # print("="*60)

    if not hotels:
        hotels=[]
    # else:
    #     for h in hotels:
    #         print(f"\n{h['id']}. {h['name']}")
    #         print(f"   Price:    {h['price']}")
    #         print(f"   Rating:   {h['rating']}")
    #         print(f"   Location: {h['location']}")
    #         print(f"   URL:      {h['url']}")

    # print("\n" + "="*60)
    # print(json.dumps(hotels, indent=2, ensure_ascii=False))
    return hotels