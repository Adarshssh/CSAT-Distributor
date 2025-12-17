from playwright.sync_api import sync_playwright
import time
import random

EMAIL_FILE = "emails.txt"
PASSWORD = "123456Mohib"

CATEGORY_TEXT = "Smart Phones"

# GLOBAL FEEDBACK COUNTER
feedback_count = 0

POCO_LIST = [
    "Poco M2", "Poco M3", "Poco X2", "Poco X3", "Poco C3",
    "Poco F3", "Poco X4 Pro", "Poco M4 Pro", "Poco F4", "Poco X5 Pro"
]

SECOND_MESSAGES = ["Sure", "Okay", "Good", "Noted", "Alright", "Understood"]


def get_emails_from_file():
    try:
        with open(EMAIL_FILE, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except:
        print("[error] emails.txt not found!")
        return []


def send_message(input_box, send_btn, msg):
    input_box.first.fill(msg)
    send_btn.first.click()
    print("[sent]", msg)


def do_end_chat(tab):
    global feedback_count

    # --- END CHAT ---
    try:
        end_divs = tab.locator("div.tip")
        for div in end_divs.all():
            children = [c.inner_text().strip() for c in div.locator("div").all()]
            if "End Chat" in children:
                div.click()
                time.sleep(1)
                confirm = tab.locator("div.confirm-action-ok")
                if confirm.count() > 0:
                    confirm.first.click()
                print("[chat ended]")
                break
    except Exception as e:
        print("End chat error:", e)

    # --- FEEDBACK SECTION ---
    try:
        time.sleep(2)

        # Select "Resolved"
        resolved = tab.locator("div.issettle >> div.unselect").filter(has_text="Resolved")
        if resolved.count() > 0:
            resolved.first.click()
            print("[resolved selected]")

        time.sleep(1)

        # Select 3 stars
        tab.evaluate("""
            () => {
                let stars = document.querySelectorAll("div.starselect.img, div.unstarselect.img");
                if (stars.length >= 3) stars[2].click();
            }
        """)

        time.sleep(1)

        # Submit
        submit = tab.locator("div.submit").filter(has_text="Submit")
        if submit.count() > 0:
            submit.first.click()

            feedback_count += 1
            print(f"[feedback submitted] — Total feedbacks so far: {feedback_count}")

        # Wait 10 seconds after feedback
        time.sleep(10)

    except Exception as e:
        print("Feedback error:", e)


def run_poco_chat(email):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, channel="chrome")
        context = browser.new_context()
        page = context.new_page()

        # Login
        page.goto("https://www.mi.com/in", wait_until="load")
        time.sleep(5)

        for _ in range(17):
            page.keyboard.press("Tab")
            time.sleep(0.2)
        page.click(":focus")
        time.sleep(6)

        page.locator("input[name='account']").fill(email)
        page.locator("input[name='password']").fill(PASSWORD)
        page.keyboard.press("Enter")
        time.sleep(8)

        # Online service
        page.goto("https://www.mi.com/in/service/online/", wait_until="load")
        time.sleep(5)

        # Open Live Chat Window
        for _ in range(20):
            page.keyboard.press("Tab")
            time.sleep(0.2)

        with context.expect_page() as new_page_info:
            page.keyboard.press("Enter")

        new_tab = new_page_info.value
        new_tab.wait_for_load_state("load")
        time.sleep(2)

        # Click LIVE CHAT button
        found = False
        for el in new_tab.locator("div, a, button").all():
            if el.inner_text().strip() == "Live Chat":
                el.click()
                found = True
                break

        if not found:
            print("Live Chat not found")
            return

        time.sleep(3)

        # Select Smart Phones
        for c in new_tab.locator("div").all():
            if c.inner_text().strip() == CATEGORY_TEXT:
                c.click()
                break

        input_box = new_tab.locator("textarea#input")
        send_btn = new_tab.locator("div.send").filter(has_text="Send")

        # WAIT 40 seconds before sending first message
        time.sleep(40)

        # ----- SEND FIRST POCO MESSAGE -----
        poco = random.choice(POCO_LIST)
        msg = f"I am facing issue with my {poco}."
        send_message(input_box, send_btn, msg)

        # WAIT 35 seconds, then send 2nd message
        time.sleep(35)

        send_message(input_box, send_btn, random.choice(SECOND_MESSAGES))

        # End chat + feedback
        time.sleep(5)
        do_end_chat(new_tab)

        browser.close()


# ---------------- MAIN EXECUTION ----------------
if __name__ == "__main__":
    emails = get_emails_from_file()

    for email in emails:
        print(f"\n--- Starting chat cycles for {email} ---\n")

        # Each email will be used 4 TIMES
        for i in range(4):
            print(f"[run {i+1}/4] Using email: {email}")
            run_poco_chat(email)

    print("\n==============================")
    print(f" FINAL TOTAL FEEDBACKS: {feedback_count}")
    print("==============================")
