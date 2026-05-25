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

def wait_for_generated_image(page, timeout_s, images_before=0):
    sel = ", ".join([
        'img[src*="oaiusercontent"]',
        'img[src*="estuary/content"]',
    ])
    start = time.time()

    # Wait minimum 15 seconds for ChatGPT to start generating
    log("Waiting 15 seconds for ChatGPT to start generating...")
    time.sleep(15)

    while time.time() - start < timeout_s:
        candidates = page.locator(sel)
        count      = candidates.count()
        log(f"Scanning for image... {count} candidate(s)")

        # Need at least 2 images — uploaded logo + generated poster
        if count > images_before + 1:
            # Always take the LAST image — that's the generated one
            img    = candidates.last
            src    = img.get_attribute("src") or ""
            loaded = img.evaluate("el => el.naturalWidth > 0")

            if loaded and src:
                log(f"Image found: {src[:70]}")
                img.scroll_into_view_if_needed()
                return img

        time.sleep(2)

    raise TimeoutError("Timed out waiting for generated image")

def send_message(page, text, logo_path=None):
    textarea = page.locator("div[contenteditable='true']").first
    textarea.click()
    time.sleep(0.5)

    # Upload logo file if provided
    if logo_path and os.path.exists(logo_path):
        log("Uploading logo file...")

        # Resize logo before uploading
        from PIL import Image
        import tempfile
        logo_img = Image.open(logo_path)
        logo_img = logo_img.resize((800, 267), Image.LANCZOS)
        tmp_path = tempfile.mktemp(suffix=".png")
        logo_img.save(tmp_path)

        page.locator('input[type="file"]').first.set_input_files(tmp_path)
        time.sleep(3)

        # Clean up temp file
        os.remove(tmp_path)
        log("Logo uploaded ✅")

    # Type prompt
    page.evaluate("(t) => navigator.clipboard.writeText(t)", text)
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
# ─────────────────────────────────────────
#  CHECK IF ALREADY LOGGED IN
# ─────────────────────────────────────────
def is_logged_in(page):
    try:
        # Check if "Log in" button is visible at top right
        login_btn = page.locator('button:has-text("Log in")').first
        if login_btn.is_visible(timeout=5_000):
            log("ChatGPT is not logged in ❌")
            return False
        log("ChatGPT is already logged in ✅")
        return True
    except:
        log("ChatGPT is already logged in ✅")
        return True

# ─────────────────────────────────────────
#  AUTO LOGIN
# ─────────────────────────────────────────
def login_to_chatgpt(page, email, password):
    log("Logging in to ChatGPT...")

    # Click the Log in button inside the popup
    page.wait_for_selector('button:has-text("Log in")', timeout=15_000)
    page.locator('button:has-text("Log in")').last.click()
    time.sleep(3)

    # Enter email
    log("Entering email...")
    page.wait_for_selector('input[type="email"], input[name="email"]', timeout=15_000)
    page.locator('input[type="email"], input[name="email"]').first.fill(email)
    page.get_by_role("button", name="Continue", exact=True).click()
    time.sleep(3)

    # Check if password field exists — some accounts skip it
    try:
        page.wait_for_selector('input[type="password"]', timeout=8_000)
        log("Entering password...")
        page.locator('input[type="password"]').first.fill(password)
        page.get_by_role("button", name="Continue", exact=True).click()
        time.sleep(5)
    except:
        log("Password step skipped — checking if already logged in...")
        time.sleep(3)

    log("Waiting for login to complete...")
    page.wait_for_selector("div[contenteditable='true']", timeout=30_000)
    log("Login successful ✅")

# ─────────────────────────────────────────
#  MAIN BROWSER FUNCTION
# ─────────────────────────────────────────

def run_browser(prompt, output_dir=None, profile_dir=None, login_timeout_s=None,
                prompt_timeout_s=None, chatgpt_email=None, chatgpt_password=None,
                logo_path=None):

    output_dir       = output_dir       or CONFIG["output_dir"]
    profile_dir      = profile_dir      or CONFIG["profile_dir"]
    login_timeout_s  = login_timeout_s  or CONFIG["login_timeout_s"]
    prompt_timeout_s = prompt_timeout_s or CONFIG["prompt_timeout_s"]
    chatgpt_email    = chatgpt_email    or CONFIG.get("chatgpt_email")
    chatgpt_password = chatgpt_password or CONFIG.get("chatgpt_password")
    logo_path        = logo_path        or CONFIG.get("logo_path")

    os.makedirs(output_dir, exist_ok=True)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            profile_dir,
            headless         = False,
            channel          = "chrome",
            accept_downloads = True,
            viewport         = {"width": 1400, "height": 900},
            user_agent       = (
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

        # Open ChatGPT
        log("Opening ChatGPT...")
        page.goto("https://chatgpt.com", wait_until="domcontentloaded", timeout=60_000)
        time.sleep(3)

        # Check login BEFORE sending prompt
        if not is_logged_in(page):
            if chatgpt_email and chatgpt_password:
                login_to_chatgpt(page, chatgpt_email, chatgpt_password)
            else:
                log("No credentials provided — please log in manually in the browser...")
                page.wait_for_selector("div[contenteditable='true']",
                                       timeout=login_timeout_s * 1000)
        
        # Wait and confirm login before proceeding
        time.sleep(2)
        page.wait_for_selector("div[contenteditable='true']", timeout=30_000)
        log("Chat input ready — proceeding to send prompt...")
        time.sleep(2)

        # Count existing images BEFORE sending prompt
        sel = 'img[src*="oaiusercontent"], img[src*="estuary/content"]'
        images_before = page.locator(sel).count()
        log(f"Images before prompt: {images_before}")

        # Send prompt WITH logo
        log("Sending prompt...")
        send_message(page, prompt, logo_path=logo_path)

        # Wait for NEW image AFTER prompt
        log("Waiting for poster image...")
        img = wait_for_generated_image(page, prompt_timeout_s, images_before)
        src = img.get_attribute("src")
        if not src:
            raise Exception("Image has no src attribute")

        # Save image
        timestamp   = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        output_file = os.path.join(output_dir, f"poster-{timestamp}.png")
        save_image(page, src, output_file)
        log(f"Poster saved → {output_file}")

        context.close()
        return output_file

