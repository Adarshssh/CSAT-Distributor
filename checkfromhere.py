from playwright.sync_api import sync_playwright
import sys, traceback, random, time

# ==========================================
#                CONFIG
# ==========================================

FIRST_TARGET = 17
SUPPORT_TARGET = 14

CHATNOW_TEXT = "Chat Now"
LIVECHAT_TEXT = "Live Chat"
CATEGORY_TEXT = "Smart Phones"

EMAIL = "searcy@bittiry.com"
PASSWORD = "123456Mohib"

CANDIDATE_SELECTOR = (
    "a, button, [role='button'], input[type=button], input[type=submit], "
    "input[type=password], [onclick], label, div[role='button'], "
    "span[role='button'], [tabindex]"
)

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

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
    "Redmi 14C 5G": ["battery", "back cover", "finger module", "volume key"]
}

THIRD_MSG = ["Sure", "Okay"]
FOURTH_MSG = [
    "I prefer not to share my name or mobile number.",
    "Sorry, I cannot give my details.",
    "I won't share my personal info."
]
FIFTH_MSG = ["okay", "ok", "yes", "yep", "okkk"]
SIXTH_MSG = ["take your time", "okay", "oakay", "sure"]
SEVENTH_MSG = ["Thank you", "Thanku", "Thankxx"]


# ==========================================
#           HELPER FUNCTIONS
# ==========================================

def collect_clickable_candidates(page, selector):
    """Collect all potential clickable elements with visibility info."""
    return page.eval_on_selector_all(selector, """
        (els) => els.map((el, idx) => {
            try {
                const rect = el.getBoundingClientRect();
                const style = window.getComputedStyle(el);
                const visible = rect.width > 0 && rect.height > 0 &&
                                style.visibility !== 'hidden' &&
                                el.offsetParent !== null;

                const text = (el.innerText || el.value ||
                              el.getAttribute('aria-label') ||
                              el.getAttribute('title') || "")
                              .trim().slice(0,120);

                return { idx, tag: el.tagName, text, href: el.href || null, visible };

            } catch (e) {
                return { idx, error: '' + e };
            }
        })
    """)


def click_exact_text(target, selector, text):
    """Clicks an element whose inner text matches exactly."""
    matches = target.locator(selector).filter(has_text=text)

    for i in range(matches.count()):
        element = matches.nth(i)
        if element.inner_text().strip() == text:
            element.scroll_into_view_if_needed()
            element.click()
            return True

    return False


def send_message(frame, message):
    """Send message inside chat input box."""
    try:
        textarea = frame.locator("textarea#input")

        if textarea.count() > 0:
            textarea.first.fill(message)

            send_btn = frame.locator("div.send").filter(has_text="Send")
            if send_btn.count() > 0:
                send_btn.first.click()

        print(f"[success] Sent message: {message}")
        return True

    except Exception as e:
        print(f"[error] Could not send message: {message} ({e})")
        return False


# ==========================================
#                MAIN LOGIC
# ==========================================

def main():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome", headless=False)

            context = browser.new_context(
                viewport={"width": SCREEN_WIDTH, "height": SCREEN_HEIGHT},
                device_scale_factor=1,
                is_mobile=False,
                has_touch=False,
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/127.0.0.0 Safari/537.36"
                )
            )

            page = context.new_page()
            print("[info] Opening MI site ...")
            page.goto("https://www.mi.com/in", wait_until="domcontentloaded")
            page.wait_for_timeout(2500)

            # ----------------------------------------------
            # STEP 1: Click FIRST_TARGET (17th visible)
            # ----------------------------------------------
            candidates = collect_clickable_candidates(page, CANDIDATE_SELECTOR)
            visible = [c for c in candidates if c.get("visible")]

            target_idx = visible[FIRST_TARGET - 1]["idx"]
            page.locator(CANDIDATE_SELECTOR).nth(target_idx).click()
            page.wait_for_load_state("networkidle")

            # ----------------------------------------------
            # STEP 2: Login
            # ----------------------------------------------
            page.locator("input[name='account']").fill(EMAIL)
            page.locator("input[name='password']").fill(PASSWORD)
            page.locator("button[type='submit'], input[type='submit']").first.press("Enter")
            print("[success] Login submitted.")

            # ----------------------------------------------
            # STEP 3: Click SUPPORT_TARGET (14th visible)
            # ----------------------------------------------
            page.wait_for_timeout(4000)
            candidates2 = collect_clickable_candidates(page, CANDIDATE_SELECTOR)
            visible2 = [c for c in candidates2 if c.get("visible")]

            support_idx = visible2[SUPPORT_TARGET - 1]["idx"]
            page.locator(CANDIDATE_SELECTOR).nth(support_idx).click()
            print("[success] Support clicked.")

            # ----------------------------------------------
            # STEP 4: Click "Chat Now"
            # ----------------------------------------------
            page.wait_for_timeout(4000)

            if not click_exact_text(page, "a", CHATNOW_TEXT):
                # fallback index (29th visible)
                candidates3 = collect_clickable_candidates(page, CANDIDATE_SELECTOR)
                visible3 = [c for c in candidates3 if c.get("visible")]

                if len(visible3) >= 29:
                    chat_idx = visible3[28]["idx"]
                    page.locator(CANDIDATE_SELECTOR).nth(chat_idx).click()
                    print("[success] Chat Now clicked by index.")
                else:
                    print("[error] Chat Now not found!")

            page.wait_for_timeout(6000)

            # ----------------------------------------------
            # STEP 5: Click "Live Chat"
            # ----------------------------------------------
            clicked = click_exact_text(page, "div", LIVECHAT_TEXT)

            if not clicked:
                for frame in page.frames:
                    if click_exact_text(frame, "div", LIVECHAT_TEXT):
                        print(f"[success] Live Chat clicked in iframe {frame.url}")
                        clicked = True
                        break

            page.wait_for_timeout(3000)

            # ----------------------------------------------
            # STEP 6: Select "Smart Phones" Category
            # ----------------------------------------------
            category_clicked = False
            for frame in page.frames:
                try:
                    channels = frame.locator("div.chat_channel").all()

                    for div in channels:
                        label = div.locator("div").first.inner_text().strip()
                        if label == CATEGORY_TEXT:
                            div.click()
                            print(f"[success] Category '{CATEGORY_TEXT}' selected.")
                            category_clicked = True
                            break

                    if category_clicked:
                        break

                except:
                    pass

            page.wait_for_timeout(10000)

            # ----------------------------------------------
            # STEP 7: Random phone + part message
            # ----------------------------------------------
            phone = random.choice(list(PHONE_LIST.keys()))
            part = random.choice(PHONE_LIST[phone])
            first_message = f"I want to know the {part} price of {phone}"

            # ----------------------------------------------
            # STEP 8: Detect chat iframe
            # ----------------------------------------------
            chat_frame = None
            for frame in page.frames:
                if frame.locator("textarea#input").count() > 0:
                    chat_frame = frame
                    break

            if not chat_frame:
                chat_frame = page

            # ----------------------------------------------
            # STEP 9: Send message sequence
            # ----------------------------------------------
            sequence = [
                (first_message, 0),
                ("yes", 80),
                (random.choice(THIRD_MSG), 10),
                (random.choice(FOURTH_MSG), 10),
                (random.choice(FIFTH_MSG), 95),
                (random.choice(SIXTH_MSG), 10),
                (random.choice(SEVENTH_MSG), 10)
            ]

            for msg, delay in sequence:
                print(f"[info] Waiting {delay}s → Sending: {msg}")
                time.sleep(delay)
                send_message(chat_frame, msg)

            # ----------------------------------------------
            # STEP 10: End chat + feedback
            # ----------------------------------------------
            page.wait_for_timeout(5000)

            # End chat button
            try:
                end_btn = chat_frame.locator("div.tip >> div").filter(has_text="End Chat")
                if end_btn.count() > 0:
                    end_btn.first.click()
                    time.sleep(1)
                    confirm = chat_frame.locator("div.confirm-action-ok")
                    if confirm.count() > 0:
                        confirm.first.click()
                        print("[success] Chat ended.")
            except:
                pass

            # Feedback
            try:
                time.sleep(1)
                resolved = chat_frame.locator("div.issettle >> div.unselect").filter(has_text="Resolved")
                resolved.first.click()

                # Select 3rd star
                chat_frame.evaluate("""
                    () => {
                        let stars = document.querySelectorAll("div.starselect.img, div.unstarselect.img");
                        if (stars.length >= 3) {
                            stars[2].classList.add("starselect");
                            stars[2].dispatchEvent(new MouseEvent('click', { bubbles: true }));
                        }
                    }
                """)

                submit = chat_frame.locator("div.submit").filter(has_text="Submit")
                submit.first.click()

                print("[success] Feedback submitted.")

            except Exception as e:
                print("[error] Feedback error:", e)

            print("[info] Finished. Closing browser.")
            browser.close()

    except Exception as e:
        print("[fatal] Exception:", e)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
