# Poster Automation

## Install
```bash
pip install -r requirements.txt
playwright install chrome
```

## Usage

### Option 1 — Use default config (edit config.py)
```python
from poster_automation.main import run
run()
```

### Option 2 — Pass everything as parameters
```python
from poster_automation.main import run

run(
    profile_dir       = "D:\\poster-automation\\chrome-profile",
    output_dir        = "D:\\poster-automation\\output",
    drive_folder_id   = "1KxkGIgE2M69hubz7OtEG7UQPWcCwna8J",
    oauth_credentials = "D:\\poster-automation\\oauth-credentials.json",
    token_file        = "D:\\poster-automation\\token.json",
    prompt_files      = [
        "D:\\poster-automation\\prompt1.txt",
        "D:\\poster-automation\\prompt2.txt",
        "D:\\poster-automation\\prompt3.txt",
        "D:\\poster-automation\\prompt4.txt",
    ],
    schedule_hour   = 16,
    schedule_minute = 3,
)
```

## Schedule on Windows (Task Scheduler)
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger → Daily → your time
4. Action → Start a Program
5. Program: `python`
6. Arguments: `D:\poster-automation\run.py`
7. Save

## run.py (place in D:\poster-automation\)
```python
from poster_automation.main import run
run()
```
//chrome history

Start-Process "C:\Program Files\Google\Chrome\Application\chrome.exe" -ArgumentList '--user-data-dir=D:\posters-automation\chrome-profile', '--profile-directory=Default'


//TO clear cookies
python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); context = p.chromium.launch_persistent_context('D:\\posters-automation\\chrome-profile', channel='chrome', headless=False, args=['--profile-directory=Default']); context.clear_cookies(); context.close(); p.stop(); print('Cookies cleared!')"