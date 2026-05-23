from datetime import datetime

def log(msg, is_error=False):
    tag  = "[ERROR]" if is_error else "[INFO] "
    time = datetime.now().strftime("%H:%M:%S")
    print(f"[{time}] {tag} {msg}")