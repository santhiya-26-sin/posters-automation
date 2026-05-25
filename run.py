from poster_automation.main import run

run(
    profile_dir       = "D:\\posters-automation\\chrome-profile",
    output_dir        = "D:\\posters-automation\\output",
    drive_folder_id   = "1KxkGIgE2M69hubz7OtEG7UQPWcCwna8J",
    oauth_credentials = "D:\\posters-automation\\oauth-credentials.json",
    token_file        = "D:\\posters-automation\\token.json",  
    chatgpt_email     = "ramyagovi05@gmail.com",
    chatgpt_password  = "123sanVan",
    logo_path = "D:\\posters-automation\\logo.png",
    prompt_files      = [
        "D:\\posters-automation\\prompt1.txt",
        "D:\\posters-automation\\prompt2.txt",
        "D:\\posters-automation\\prompt3.txt",
        "D:\\posters-automation\\prompt4.txt",
    ],
    schedule_hour   = 6,
    schedule_minute = 48,
)