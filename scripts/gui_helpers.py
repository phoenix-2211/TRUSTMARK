import sys
from pathlib import Path
import random
import string

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def generate_random_id(prefix: str, length: int = 12) -> str:
    chars = string.ascii_letters + string.digits
    return f"{prefix}_" + "".join(random.choices(chars, k=length))

def ensure_repo_root_on_path():
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
