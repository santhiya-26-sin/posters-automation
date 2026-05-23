# ─────────────────────────────────────────
#  CONFIG — edit these values
# ─────────────────────────────────────────

CONFIG = {
    # Chrome profile directory
    "profile_dir": "D:\\poster-automation\\chrome-profile",

    # Folder to save generated posters
    "output_dir": "D:\\poster-automation\\output",

    # Google Drive folder ID (from the URL of your Drive folder)
    "drive_folder_id": "1KxkGIgE2M69hubz7OtEG7UQPWcCwna8J",

    # OAuth credentials file (downloaded from Google Cloud Console)
    "oauth_credentials": "D:\\poster-automation\\oauth-credentials.json",

    # Token file (auto-created after first login)
    "token_file": "D:\\poster-automation\\token.json",

    # Prompt text files (paste your prompts inside these files)
    "prompt_files": [
        "D:\\poster-automation\\prompt1.txt",
        "D:\\poster-automation\\prompt2.txt",
        "D:\\poster-automation\\prompt3.txt",
        "D:\\poster-automation\\prompt4.txt",
    ],

    # Scheduled time (24hr format)
    "schedule_hour":   16,
    "schedule_minute": 3,

    # Timeouts (seconds)
    "prompt_timeout_s": 240,
    "login_timeout_s":  600,
}
