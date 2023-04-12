from config import DEBUG

def DEBUG_PRINT(debug_msg: str) -> None:
    if not DEBUG:
        return
    print(debug_msg)
