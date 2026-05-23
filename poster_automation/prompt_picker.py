import os
import random
from .logger import log
from .config import CONFIG

def get_random_prompt(prompt_files=None):
    prompt_files = prompt_files or CONFIG["prompt_files"]

    # Check all files exist
    for file_path in prompt_files:
        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"Prompt file not found: {file_path}\n"
                f"Please create it and paste your prompt inside."
            )

    idx       = random.randint(0, len(prompt_files) - 1)
    file_path = prompt_files[idx]
    prompt    = open(file_path, encoding="utf-8").read().strip()
    log(f"Using prompt {idx + 1} of {len(prompt_files)} → {file_path}")
    return prompt
