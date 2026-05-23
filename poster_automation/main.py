from .config import CONFIG
from .logger import log
from .scheduler import wait_until_scheduled_time
from .prompt_picker import get_random_prompt
from .browser import run_browser
from .drive_upload import upload_to_drive

def run(
    profile_dir       = None,
    output_dir        = None,
    drive_folder_id   = None,
    oauth_credentials = None,
    token_file        = None,
    prompt_files      = None,
    schedule_hour     = None,
    schedule_minute   = None,
    chatgpt_email     = None,   # ← NEW
    chatgpt_password  = None,   # ← NEW
):
    try:
        # Wait until scheduled time
        wait_until_scheduled_time(
            hour   = schedule_hour   or CONFIG["schedule_hour"],
            minute = schedule_minute or CONFIG["schedule_minute"],
        )

        # Pick random prompt
        prompt = get_random_prompt(prompt_files)

        # Run browser → generate image → save locally
        output_file = run_browser(
            prompt           = prompt,
            output_dir       = output_dir,
            profile_dir      = profile_dir,
            chatgpt_email    = chatgpt_email,     # ← NEW
            chatgpt_password = chatgpt_password,  # ← NEW
        )

        # Upload to Google Drive
        upload_to_drive(
            file_path         = output_file,
            drive_folder_id   = drive_folder_id,
            oauth_credentials = oauth_credentials,
            token_file        = token_file,
        )

        print("\n✅  Done.")

    except Exception as e:
        log(f"Workflow failed: {e}", is_error=True)
        raise
    