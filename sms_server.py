import time
import os
import random
from datetime import datetime
from playwright.sync_api import sync_playwright

def log_yaz(mesaj):
    zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{zaman}] {mesaj}"
    print(log_line)
    with open("bot_log.txt", "a", encoding="utf-8") as f:
        f.write(log_line + "\n")

def rastgele_eposta_al():
    first_names = ["alex", "jordan", "taylor", "morgan", "casey", "skyler", "quinn"]
    last_names = ["walker", "harris", "lewis", "robinson", "clark", "young"]
    return f"{random.choice(first_names)}.{random.choice(last_names)}{random.randint(100,999)}@gmail.com"

def sms_islemi(numara):
    temiz_numara = numara.replace("+48", "").replace(" ", "").strip()
    if len(temiz_numara) > 9:
        temiz_numara = temiz_numara[-9:]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 720}
        )
        page = context.new_page()

        try:
            page.goto("https://lisek.app/rejestracja", wait_until="networkidle", timeout=60000)

            if page.is_visible("input[name='name']"):
                page.fill("input[name='phoneNumber']", temiz_numara)
                page.fill("input[name='name']", "John Walker")
                page.fill("input[name='email']", rastgele_eposta_al())

                checkboxes = page.query_selector_all("button[role='checkbox']")
                for i, box in enumerate(checkboxes):
                    if i < 3:
                        box.click()
                        time.sleep(0.2)

                page.click("button[type='submit']")
                page.wait_for_timeout(3000)

            submit_selector = "button[type='submit']"

            if not page.is_visible("input[name='code']"):
                try:
                    page.wait_for_selector(submit_selector, state="visible", timeout=5000)
                    if page.is_visible("input[name='phoneNumber']"):
                        val = page.input_value("input[name='phoneNumber']")
                        if not val:
                            page.fill("input[name='phoneNumber']", temiz_numara)
                    page.eval_on_selector(submit_selector, "btn => btn.click()")
                except:
                    pass

            try:
                page.wait_for_selector("input[name='code'], input[autocomplete='one-time-code']", timeout=20000)
                log_yaz(f"[OK] {temiz_numara}: SMS SENT.")
            except:
                log_yaz(f"[!] {temiz_numara}: FAILED.")

        except Exception as e:
            log_yaz(f"[HATA] {temiz_numara}: {str(e)}")

        finally:
            browser.close()

def main():
    log_yaz("=== BOT STARTED ===")

    if not os.path.exists("numaralar.txt"):
        log_yaz("ERROR: numaralar.txt missing!")
        return

    with open("numaralar.txt", "r") as f:
        numaralar = [n.strip() for n in f.readlines() if n.strip()]

    log_yaz(f"--- STARTING CYCLE ({len(numaralar)} numbers) ---")

    for numara in numaralar:
        log_yaz(f"Current: {numara}")
        sms_islemi(numara)
        time.sleep(random.randint(10, 20))

    log_yaz("--- CYCLE FINISHED. 24H SLEEP ---")

    # 24 saat bekle ama her dakika log at (Railway uyku yapmasın)
    for i in range(86400, 0, -60):
        saat = i // 3600
        dakika = (i % 3600) // 60
        log_yaz(f"Timer: {saat:02d}:{dakika:02d} remaining")
        time.sleep(60)

if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            log_yaz(f"[SYSTEM ERROR] {str(e)}")
            log_yaz("Restarting in 60 seconds...")
            time.sleep(60)
