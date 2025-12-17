from playwright.sync_api import sync_playwright
import time
import random

EMAIL_FILE = "emails.txt"
PASSWORD = "123456Mohib"
LIVECHAT_TEXT = "Live Chat"
CATEGORY_TEXT = "Laptop"

# GLOBAL FEEDBACK COUNTER
feedback_count = 0

# ------------------------
# DEVICE + SPARE PART LIST
# ------------------------
PHONE_LIST = {
    "Redmi 10 Power": ["display", "battery", "speaker"],
    "Redmi 10 Prime": ["display", "battery", "sub Board", "speaker"],
    "Redmi 10 Prime 2022": ["display", "battery", "back cover"],
    "Redmi 10A": ["display", "speaker"],
    "Redmi 11 Prime": ["display", "battery", "back cover"],
    "Redmi 11 Prime 5G": ["display"],
    "Redmi 12": ["display", "battery", "back cover"],
    "Redmi 12 5G": ["battery", "sub board"],
    "Redmi 12C": ["display", "battery", "speaker", "suboard"],
    "Redmi 13 5G": ["back cover", "display"],
    "Redmi 13C": ["battery", "back cover", "finger module"],
    "Redmi 14C 5G": ["battery", "back cover", "finger module", "volume key"],
    "Redmi 15 5G": ["battery", "display"],
    "Redmi Note 10": ["display", "battery"],
    "Redmi Note 10 Pro": ["display", "battery"],
    "Redmi Note 11": ["display", "battery"],
    "Redmi Note 11 Pro": ["display", "battery"],
    "Redmi Note 12": ["display", "battery"],
    "Redmi Note 12 Pro": ["display", "battery"],
    "Redmi Note 12 Pro Plus": ["display", "battery"],
    "Xiaomi 15 Ultra": ["display", "battery"],
    "Xiaomi 12": ["display", "battery"],
    "Xiaomi 12 Pro": ["display", "battery"],
    "Xiaomi 12T": ["display", "battery"],
    "Xiaomi 12T Pro": ["display", "battery"],
    "Xiaomi 15": ["display", "battery"],
}

# GENERAL ISSUES
GENERAL_ISSUES = [
    "heating", "lagging", "battery draining", "slow performance",
    "network connectivity", "camera", "speaker", "display",
    "touchscreen", "charging"
]

# POCO DEVICES
POCO_LIST = [
    "Poco M2", "Poco M3", "Poco X2", "Poco X3", "Poco C3",
    "Poco F3", "Poco X4 Pro", "Poco M4 Pro", "Poco F4", "Poco X5 Pro",
    "Poco F5", "Poco X6 Pro", "Poco C40", "Poco C55", "Poco M5", "Poco M5s"
]

# MESSAGES
FOLLOW_UP_MESSAGES = [
    "Yes, you understood it correct",
    "Absolutely, please continue",
    "Yes",
    "Please share the details",
    "You are absolutely right",
    "Correct",
    "That's right",
]

THIRD_MSG = ["Sure", "Okay", "Good", "Thanks", "Understood", "Alright", "Fine", "Noted", "Got it", "Very well"]

FOURTH_MSG = [
    "I prefer not to share my name or mobile number.",
    "Sorry, I cannot give my details.",
    "I won't share my personal info.",
    "I don't feel comfortable sharing that.",
    "I'd rather keep that private.",
]

FIFTH_MSG = [
    "Still I can't share details",
    "So what, I don't want to share details",
    "I cannot provide that info",
    "I would prefer to keep it private",
    "I am not comfortable sharing that",
]

SIXTH_MSG = ["Take your time", "okay", "oakay", "sure", "no problem", "fine", "noted"]
SEVENTH_MSG = ["Thank you", "Thanku", "Thankxx", "Thanks a lot", "Thanks", "Thnxx", "Thankyou", "Thankx", "Thnx", "Thankq"]


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

        # 3-star rating
        tab.evaluate("""
            () => {
                let stars = document.querySelectorAll("div.starselect.img, div.unstarselect.img");
                if (stars.length >= 3) stars[2].click();
            }
        """)

        time.sleep(1)

        # Submit feedback
        submit = tab.locator("div.submit").filter(has_text="Submit")
        if submit.count() > 0:
            submit.first.click()

            # Increase feedback counter
            feedback_count += 1

            print(f"[feedback submitted] — Total feedbacks so far: {feedback_count}")

        # WAIT 10 SECONDS
        time.sleep(5)

    except Exception as e:
        print("Feedback error:", e)


def open_chat_for_email(email, query_type_index):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, channel="chrome")
        context = browser.new_context()
        page = context.new_page()

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

        page.goto("https://www.mi.com/in/service/online/", wait_until="load")
        time.sleep(5)

        for _ in range(20):
            page.keyboard.press("Tab")
            time.sleep(0.2)

        with context.expect_page() as new_page_info:
            page.keyboard.press("Enter")

        new_tab = new_page_info.value
        new_tab.wait_for_load_state("load")
        time.sleep(2)

        # OPEN LIVE CHAT
        found = False
        for el in new_tab.locator("div, a, button").all():
            if el.inner_text().strip() == "Live Chat":
                el.click()
                found = True
                break

        if not found:
            print("Live chat not found")
            return

        time.sleep(3)

        for c in new_tab.locator("div").all():
            if c.inner_text().strip() == CATEGORY_TEXT:
                c.click()
                break

        input_box = new_tab.locator("textarea#input")
        send_btn = new_tab.locator("div.send").filter(has_text="Send")

        time.sleep(15)

        # QUERY TYPES — 1 to 4
        if query_type_index == 1:
            device = random.choice(list(PHONE_LIST.keys()))
            part = random.choice(PHONE_LIST[device])
            msg = f"I want to know the price of {part} for {device}."
            send_message(input_box, send_btn, msg)

            time.sleep(35)
            send_message(input_box, send_btn, random.choice(FOLLOW_UP_MESSAGES))

            time.sleep(35)
            send_message(input_box, send_btn, random.choice(THIRD_MSG))

            time.sleep(35)
            send_message(input_box, send_btn, random.choice(FOURTH_MSG))

            time.sleep(30)
            send_message(input_box, send_btn, random.choice(FIFTH_MSG))

            time.sleep(30)
            send_message(input_box, send_btn, random.choice(SIXTH_MSG))

            time.sleep(50)
            send_message(input_box, send_btn, random.choice(SEVENTH_MSG))

            time.sleep(5)
            do_end_chat(new_tab)

        elif query_type_index == 2:
            issue = random.choice(GENERAL_ISSUES)
            device = random.choice(list(PHONE_LIST.keys()))
            msg = f"I am facing {issue} issue after update in my {device}."
            send_message(input_box, send_btn, msg)

            time.sleep(35)
            send_message(input_box, send_btn, random.choice(FOLLOW_UP_MESSAGES))

            time.sleep(25)
            send_message(input_box, send_btn, random.choice(THIRD_MSG))

            time.sleep(35)
            send_message(input_box, send_btn, random.choice(FOURTH_MSG))

            time.sleep(70)
            do_end_chat(new_tab)

        elif query_type_index == 3:
            poco = random.choice(POCO_LIST)
            msg = f"I am facing issue with my {poco}."
            send_message(input_box, send_btn, msg)

            time.sleep(40)
            send_message(input_box, send_btn, random.choice(THIRD_MSG))

            time.sleep(120)
            do_end_chat(new_tab)

        elif query_type_index == 4:
            device = random.choice(list(PHONE_LIST.keys()))
            msg = f"I want to add widgets on the screen of my device {device}."
            send_message(input_box, send_btn, msg)

            time.sleep(20)
            send_message(input_box, send_btn, random.choice(THIRD_MSG))

            time.sleep(120)
            do_end_chat(new_tab)

        browser.close()


if __name__ == "__main__":
    emails = get_emails_from_file()

    for idx, email in enumerate(emails):
        print(f"\n--- Starting session for {email} ---")

        query_type = (idx % 4) + 1
        open_chat_for_email(email, query_type)
