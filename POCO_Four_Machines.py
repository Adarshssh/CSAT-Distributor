from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
import multiprocessing
import time
import random
import traceback
from typing import List, Tuple, Optional

# ---------------- CONFIG ----------------
EMAIL_FILE = "emails.txt"
PASSWORD = "123456Mohib"
LIVECHAT_TEXT = "Live Chat"
CATEGORY_TEXT = "Smart Phones"

WORKER_COUNT = 4
CHATS_PER_EMAIL = 5

# TIMINGS (seconds)
PAGE_OPEN_WAIT = 8
AFTER_CLICK_17_WAIT = 6
AFTER_LOGIN_WAIT = 8
SERVICE_PAGE_WAIT = 6
WAIT_BEFORE_FIRST_MSG = 40
WAIT_BETWEEN_MSGS = 30
WAIT_BEFORE_END = 10
WAIT_AFTER_FEEDBACK = 10

POCO_LIST = [
    "Poco M2", "Poco M3", "Poco X2", "Poco X3", "Poco C3",
    "Poco F3", "Poco X4 Pro", "Poco M4 Pro", "Poco F4", "Poco X5 Pro"
]
SECOND_MESSAGES = ["Sure", "Okay", "Good", "Noted", "Alright", "Understood"]

# ---------------- Helpers ----------------

def read_emails() -> List[str]:
    try:
        with open(EMAIL_FILE, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception:
        print("[error] emails.txt not found or unreadable.")
        return []

def safe_inner_text(el):
    try:
        return el.inner_text().strip()
    except Exception:
        return ""

def find_and_click_livechat(new_tab, max_attempts=8):
    try:
        for attempt in range(max_attempts):
            elements = new_tab.locator("div, a, button").all()
            for el in elements:
                try:
                    if safe_inner_text(el) == LIVECHAT_TEXT:
                        el.scroll_into_view_if_needed()
                        try:
                            el.click()
                        except Exception:
                            # fallback evaluate
                            try:
                                new_tab.evaluate("(el) => el.click()", el)
                            except Exception:
                                pass
                        time.sleep(1.5)
                        print("[debug] Live Chat clicked")
                        return True
                except Exception:
                    continue
            time.sleep(1 + attempt * 0.5)
        return False
    except Exception as e:
        print("find_and_click_livechat error:", e)
        return False

def find_and_click_category(new_tab, category_text=CATEGORY_TEXT, max_attempts=6):
    try:
        for attempt in range(max_attempts):
            divs = new_tab.locator("div").all()
            for d in divs:
                try:
                    if safe_inner_text(d) == category_text:
                        d.scroll_into_view_if_needed()
                        try:
                            d.click()
                        except Exception:
                            try:
                                new_tab.evaluate("(el) => el.click()", d)
                            except Exception:
                                pass
                        time.sleep(1.0)
                        print(f"[debug] Category '{category_text}' clicked")
                        return True
                except Exception:
                    continue
            time.sleep(1 + attempt * 0.4)
        return False
    except Exception as e:
        print("find_and_click_category error:", e)
        return False

def find_chat_input_and_send(tab, timeout=25) -> Tuple[Optional[object], Optional[object], Optional[object]]:
    """
    Search main page and all frames for a chat input and a send button.
    Returns (frame_or_page, input_locator, send_btn_locator) or (None, None, None).
    Retries until timeout seconds.
    """
    start = time.time()
    tried = set()
    selectors_input = [
        "textarea#input",
        "textarea",
        "div[contenteditable='true']",
        "input[placeholder*='message']",
        "input[aria-label*='message']",
    ]
    selectors_send = [
        "div.send:has-text('Send')",
        "button:has-text('Send')",
        "a:has-text('Send')",
        "div:has-text('Send')",
    ]

    def try_search(frame_or_page):
        # returns (input_locator, send_locator) or (None, None)
        for sel in selectors_input:
            try:
                loc = frame_or_page.locator(sel)
                if loc.count() > 0:
                    # find send btn too
                    for s in selectors_send:
                        try:
                            send_loc = frame_or_page.locator(s)
                            if send_loc.count() > 0:
                                return (loc, send_loc)
                        except Exception:
                            continue
                    # no direct send btn in same frame; return input with None (caller may search send elsewhere)
                    return (loc, None)
            except Exception:
                continue
        return (None, None)

    while time.time() - start < timeout:
        # 1) try main page
        try:
            inp, snd = try_search(tab)
            if inp is not None:
                # If send not found in same frame, look for common send btn types across the frame
                if snd is None:
                    for s in selectors_send:
                        try:
                            send_loc = tab.locator(s)
                            if send_loc.count() > 0:
                                snd = send_loc
                                break
                        except Exception:
                            continue
                if snd is None:
                    # try to look inside divs for send word
                    try:
                        for el in tab.locator("div, button, a").all():
                            try:
                                if "send" == safe_inner_text(el).lower() or "send" in safe_inner_text(el).lower():
                                    snd = el
                                    break
                            except Exception:
                                continue
                    except Exception:
                        pass
                return (tab, inp, snd)

        except Exception:
            pass

        # 2) try frames
        try:
            for frame in tab.frames:
                fid = getattr(frame, "url", None) or str(frame)
                if fid in tried:
                    continue
                try:
                    inp, snd = try_search(frame)
                    if inp is not None:
                        # if send missing, attempt send in frame
                        if snd is None:
                            for s in selectors_send:
                                try:
                                    send_loc = frame.locator(s)
                                    if send_loc.count() > 0:
                                        snd = send_loc
                                        break
                                except Exception:
                                    continue
                        tried.add(fid)
                        return (frame, inp, snd)
                except Exception:
                    continue
        except Exception:
            pass

        time.sleep(0.8)

    # final attempt: try to find contenteditable + sibling send across frames
    print("[debug] Chat input not found within timeout")
    return (None, None, None)

def end_chat_submit_feedback(tab, shared_counter, counter_lock):
    try:
        # Click "End Chat"
        try:
            end_divs = tab.locator("div.tip")
            for div in end_divs.all():
                try:
                    child_texts = [c.inner_text().strip() for c in div.locator("div").all()]
                except Exception:
                    child_texts = []
                if "End Chat" in child_texts:
                    try:
                        div.scroll_into_view_if_needed()
                        div.click()
                    except Exception:
                        try:
                            tab.evaluate("(el) => el.click()", div)
                        except Exception:
                            pass
                    time.sleep(1.0)
                    confirm = tab.locator("div.confirm-action-ok")
                    if confirm.count() > 0:
                        try:
                            confirm.first.click()
                        except Exception:
                            pass
                    print("[chat ended]")
                    break
        except Exception as e:
            print("end chat locate/click error:", e)

        time.sleep(2)

        # Click Resolved
        try:
            resolved = tab.locator("div.issettle >> div.unselect").filter(has_text="Resolved")
            if resolved.count() > 0:
                try:
                    resolved.first.scroll_into_view_if_needed()
                    resolved.first.click()
                    print("[resolved selected]")
                except Exception:
                    try:
                        tab.evaluate("(el) => el.click()", resolved.first)
                        print("[resolved selected (eval)]")
                    except Exception:
                        pass
            else:
                print("[warning] 'Resolved' not found")
        except Exception as e:
            print("resolved click error:", e)

        time.sleep(1.0)

        # Click 3rd star
        try:
            tab.evaluate("""
                () => {
                    let stars = document.querySelectorAll("div.starselect.img, div.unstarselect.img");
                    if (stars.length >= 3) {
                        stars[2].scrollIntoView();
                        stars[2].click();
                    }
                }
            """)
            print("[3-star selected]")
        except Exception as e:
            print("star evaluate error:", e)

        time.sleep(1.0)

        # Submit
        try:
            submit = tab.locator("div.submit").filter(has_text="Submit")
            if submit.count() > 0:
                try:
                    submit.first.scroll_into_view_if_needed()
                    submit.first.click()
                    if shared_counter is not None and counter_lock is not None:
                        with counter_lock:
                            shared_counter.value += 1
                            total = shared_counter.value
                        print(f"[feedback submitted] — Total feedbacks so far: {total}")
                    else:
                        print("[feedback submitted]")
                except Exception as e:
                    print("submit click error:", e)
            else:
                print("[warning] Submit button not found")
        except Exception as e:
            print("submit locate error:", e)

        time.sleep(WAIT_AFTER_FEEDBACK)

    except Exception as e:
        print("end_chat_submit_feedback error:", e)
        traceback.print_exc()

# ---------------- Core worker logic ----------------

def run_email_cycles(email: str, shared_counter, counter_lock):
    print(f"[INSTANCE] Starting for: {email}")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, channel="chrome", args=["--window-size=1280,720"])
            context = browser.new_context(viewport={"width": 1280, "height": 720})
            page = context.new_page()

            # open mi.com and wait
            page.goto("https://www.mi.com/in", wait_until="load")
            time.sleep(PAGE_OPEN_WAIT)

            # tab 17 times, click
            for _ in range(17):
                try:
                    page.keyboard.press("Tab")
                except Exception:
                    pass
                time.sleep(0.2)
            try:
                page.click(":focus")
            except Exception:
                pass
            time.sleep(AFTER_CLICK_17_WAIT)

            # login
            try:
                page.wait_for_selector("input[name='account']", timeout=20000)
                page.locator("input[name='account']").fill(email)
                page.locator("input[name='password']").fill(PASSWORD)
                page.keyboard.press("Enter")
            except PWTimeoutError:
                print(f"[{email}] login fields not found in time")
            except Exception as e:
                print(f"[{email}] login fill error:", e)
            time.sleep(AFTER_LOGIN_WAIT)

            # service page
            try:
                page.goto("https://www.mi.com/in/service/online/", wait_until="load")
            except Exception:
                try:
                    page.goto("https://www.mi.com/in/service/online/")
                except Exception:
                    pass
            time.sleep(SERVICE_PAGE_WAIT)

            for cycle in range(1, CHATS_PER_EMAIL + 1):
                print(f"[{email}] cycle {cycle}/{CHATS_PER_EMAIL} start")
                try:
                    # press tab 20 times then Enter (open chat)
                    for _ in range(20):
                        try:
                            page.keyboard.press("Tab")
                        except Exception:
                            pass
                        time.sleep(0.12)

                    new_tab = None
                    try:
                        with context.expect_page() as new_page_info:
                            page.keyboard.press("Enter")
                        new_tab = new_page_info.value
                        try:
                            new_tab.wait_for_load_state("load", timeout=30000)
                        except Exception:
                            pass
                    except Exception:
                        new_tab = page

                    time.sleep(2.0)

                    # click live chat & category
                    lc_ok = find_and_click_livechat(new_tab, max_attempts=10)
                    if not lc_ok:
                        print(f"[{email}] Live Chat not found/clicked. Will still try to find input in frames.")

                    time.sleep(2.0)
                    cat_ok = find_and_click_category(new_tab, category_text=CATEGORY_TEXT, max_attempts=8)
                    if not cat_ok:
                        print(f"[{email}] Category '{CATEGORY_TEXT}' not found/clicked.")

                    # wait 40s
                    time.sleep(WAIT_BEFORE_FIRST_MSG)

                    # find input & send button (search frames)
                    frame_obj, input_loc, send_loc = find_chat_input_and_send(new_tab, timeout=25)
                    if frame_obj is None or input_loc is None:
                        print(f"[{email}][cycle {cycle}] ERROR: chat input not found (tried frames). Skipping this cycle.")
                        # still try to end gracefully then continue
                        try:
                            end_chat_submit_feedback(new_tab, shared_counter, counter_lock)
                        except Exception:
                            pass
                        # refresh for next cycle
                        try:
                            if new_tab is not None and new_tab is not page:
                                try:
                                    new_tab.close()
                                except Exception:
                                    pass
                                page.goto("https://www.mi.com/in/service/online/", wait_until="load")
                            else:
                                try:
                                    page.reload()
                                except Exception:
                                    page.goto("https://www.mi.com/in/service/online/", wait_until="load")
                        except Exception:
                            pass
                        time.sleep(2)
                        continue

                    # send first message (POCO)
                    poco = random.choice(POCO_LIST)
                    first_msg = f"I am facing issue with my {poco}."

                    try:
                        input_loc.first.fill(first_msg)
                        # use send_loc if available, else try to find "Send" in that frame/page again
                        if send_loc is not None and send_loc.count() > 0:
                            send_loc.first.click()
                        else:
                            # fallback: try a variety of send selectors in this frame
                            fallback = frame_obj.locator("div.send").filter(has_text="Send")
                            if fallback.count() > 0:
                                fallback.first.click()
                            else:
                                # try any element with text 'Send'
                                for el in frame_obj.locator("div, button, a").all():
                                    try:
                                        if safe_inner_text(el).lower().strip() == "send":
                                            el.click()
                                            break
                                    except Exception:
                                        continue
                        print(f"[{email}][cycle {cycle}] Sent first message: {first_msg}")
                    except Exception as e:
                        print(f"[{email}][cycle {cycle}] send first msg error:", e)

                    # wait 30s
                    time.sleep(WAIT_BETWEEN_MSGS)

                    # send second message
                    second_msg = random.choice(SECOND_MESSAGES)
                    try:
                        input_loc.first.fill(second_msg)
                        if send_loc is not None and send_loc.count() > 0:
                            send_loc.first.click()
                        else:
                            fallback = frame_obj.locator("div.send").filter(has_text="Send")
                            if fallback.count() > 0:
                                fallback.first.click()
                            else:
                                for el in frame_obj.locator("div, button, a").all():
                                    try:
                                        if safe_inner_text(el).lower().strip() == "send":
                                            el.click()
                                            break
                                    except Exception:
                                        continue
                        print(f"[{email}][cycle {cycle}] Sent second message: {second_msg}")
                    except Exception as e:
                        print(f"[{email}][cycle {cycle}] send second msg error:", e)

                    # wait 10s then end & feedback
                    time.sleep(WAIT_BEFORE_END)
                    end_chat_submit_feedback(new_tab, shared_counter, counter_lock)

                    # refresh/prep next cycle
                    try:
                        if new_tab is not None and new_tab is not page:
                            try:
                                new_tab.close()
                            except Exception:
                                pass
                            page.goto("https://www.mi.com/in/service/online/", wait_until="load")
                        else:
                            try:
                                page.reload()
                            except Exception:
                                page.goto("https://www.mi.com/in/service/online/", wait_until="load")
                    except Exception as e:
                        print(f"[{email}] refresh error after cycle {cycle}:", e)
                    time.sleep(2.0)

                except Exception as exc:
                    print(f"[{email}] Exception during cycle {cycle}:", exc)
                    traceback.print_exc()

            try:
                browser.close()
            except Exception:
                pass
            print(f"[INSTANCE] Completed {CHATS_PER_EMAIL} cycles for {email}")

    except Exception as e:
        print(f"[INSTANCE] fatal for {email}:", e)
        traceback.print_exc()

# ---------------- Multiprocessing workers ----------------

def worker_proc(emails_list, shared_counter, counter_lock, worker_id):
    print(f"[WORKER {worker_id}] started")
    while True:
        try:
            try:
                email = emails_list.pop(0)
            except IndexError:
                break
            print(f"[WORKER {worker_id}] picked {email}")
            run_email_cycles(email, shared_counter, counter_lock)
        except Exception as e:
            print(f"[WORKER {worker_id}] error:", e)
            traceback.print_exc()
    print(f"[WORKER {worker_id}] exiting")

def main():
    emails = read_emails()
    if not emails:
        print("No emails found. Put emails (one per line) in emails.txt")
        return

    manager = multiprocessing.Manager()
    emails_list = manager.list(emails.copy())
    shared_counter = manager.Value('i', 0)
    counter_lock = manager.Lock()

    procs = []
    for i in range(WORKER_COUNT):
        p = multiprocessing.Process(target=worker_proc, args=(emails_list, shared_counter, counter_lock, i+1))
        p.start()
        procs.append(p)

    for p in procs:
        p.join()

    print("All workers finished.")
    print("Total feedbacks submitted:", shared_counter.value)

if __name__ == "__main__":
    main()
