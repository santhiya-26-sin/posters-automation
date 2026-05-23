import os
import base64
import time
from datetime import datetime
from playwright.sync_api import sync_playwright
from .logger import log
from .config import CONFIG

def save_image(page, src, output_path):
    if src.startswith("data:"):
        _, b64 = src.split(",", 1)
        with open(output_path, "wb") as f:
            f.write(base64.b64decode(b64))
        return

    b64 = page.evaluate("""async (url) => {
        const res = await fetch(url, { credentials: 'include' });
        if (!res.ok) throw new Error('Fetch failed: ' + res.status);
        const buf = await res.arrayBuffer();
        const u8  = new Uint8Array(buf);
        let b = '';
        u8.forEach(x => b += String.fromCharCode(x));
        return btoa(b);
    }""", src)

    with open(output_path, "wb") as f:
        f.write(base64.b64decode(b64))

def wait_for_generated_image(page, timeout_s):
    sel = ", ".join([
        'img[src*="oaiusercontent"]',
        'img[src*="estuary"]',
        'img[src*="file-service"]',
    ])
    start = time.time()

    while time.time() - start < timeout_s:
        candidates = page.locator(sel)
        count      = candidates.count()
        log(f"Scanning for image... {count} candidate(s)")

        for i in range(count):
            img    = candidates.nth(i)
            src    = img.get_attribute("src") or ""
            loaded = img.evaluate("el => el.naturalWidth > 0")
            if loaded and src and "avatar" not in src and "logo" not in src:
                log(f"Image found: {src[:70]}")
                img.scroll_into_view_if_needed()
                return img

        time.sleep(2)

    raise TimeoutError("Timed out waiting for generated image")

def send_message(page, text):
    page.evaluate("(t) => navigator.clipboard.writeText(t)", text)
    textarea = page.locator("div[contenteditable='true']").first
    textarea.click()
    time.sleep(0.4)
    page.keyboard.press("Control+v")
    time.sleep(1.2)

    send_btn = page.locator(
        '[data-testid="send-button"], button[aria-label="Send prompt"]'
    ).first

    for _ in range(15):
        disabled = send_btn.get_attribute("disabled")
        if not disabled:
            send_btn.click()
            log("Message sent.")
            return
        time.sleep(1)

    raise Exception("Send button never became enabled")

def run_browser(prompt, output_dir=None, profile_dir=None, login_timeout_s=None, prompt_timeout_s=None):
    output_dir      = output_dir      or CONFIG["output_dir"]
    profile_dir     = profile_dir     or CONFIG["profile_dir"]
    login_timeout_s = login_timeout_s or CONFIG["login_timeout_s"]
    prompt_timeout_s= prompt_timeout_s or CONFIG["prompt_timeout_s"]

    os.makedirs(output_dir, exist_ok=True)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            profile_dir,
            headless        = False,
            channel         = "chrome",
            accept_downloads= True,
            viewport        = {"width": 1400, "height": 900},
            user_agent      = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            args = [
                "--profile-directory=Default",
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars",
                "--disable-dev-shm-usage",
                "--start-maximized",
            ],
            ignore_default_args = ["--enable-automation"],
        )

        context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', { get: () => false })"
        )
        context.grant_permissions(["clipboard-read", "clipboard-write"])

        page = context.pages[0] if context.pages else context.new_page()
        time.sleep(3)

        log("Opening ChatGPT...")
        page.goto("https://chatgpt.com", wait_until="domcontentloaded", timeout=60_000)

        log("Waiting for chat input...")
        page.wait_for_selector(
            "div[contenteditable='true']",
            state   = "visible",
            timeout = login_timeout_s * 1000
        )
        time.sleep(2)

        log("Sending prompt...")
        send_message(page, prompt)

        log("Waiting for poster image...")
        img = wait_for_generated_image(page, prompt_timeout_s)
        src = img.get_attribute("src")
        if not src:
            raise Exception("Image has no src attribute")

        timestamp   = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        output_file = os.path.join(output_dir, f"poster-{timestamp}.png")
        save_image(page, src, output_file)
        log(f"Poster saved → {output_file}")

        context.close()
        return output_file
