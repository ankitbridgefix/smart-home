from datetime import datetime, timedelta, timezone
import re

# --- Time keywords ---
RELATIVE_KEYWORDS = {
    "yesterday": lambda now: (
        (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0),
        (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1),
    ),
    "today": lambda now: (
        now.replace(hour=0, minute=0, second=0, microsecond=0),
        now,
    ),
    "last week": lambda now: (now - timedelta(days=7), now),
    "past week": lambda now: (now - timedelta(days=7), now),
    "last 7 days": lambda now: (now - timedelta(days=7), now),
    "last 24 hours": lambda now: (now - timedelta(hours=24), now),
}

# --- Known device keywords ---
DEVICE_KEYWORDS = {
    "ac": ["ac", "a/c", "air conditioner"],
    "fridge": ["fridge", "refrigerator"],
    "tv": ["tv", "television"],
    "heater": ["heater"],
    "washing-machine": ["washing machine", "washer"],
    "router": ["router", "wifi router"],
    "pump": ["pump", "water pump"],
}

# Precompile regex for devices
DEVICE_PAT = re.compile(
    r"(?:my|the)?\s*(?P<device>[a-zA-Z0-9\s/-]+)(?:\s+device)?", re.IGNORECASE
)

def extract_device_slug(text: str):
    """Return standardized device slug if found in text."""
    t = text.lower()
    for slug, variants in DEVICE_KEYWORDS.items():
        for variant in variants:
            if variant in t:
                return slug
    return None

def extract_time_range(text: str, now: datetime):
    """Return (start, end) if relative time phrase is found."""
    t = text.lower()
    for key, fn in RELATIVE_KEYWORDS.items():
        if key in t:
            return fn(now)
    return None, None



TOP_DEVICES_PATTERNS = [
    r"\btop\s+(device|devices)\b",
    r"\btop\s+consum(ing|ption)?\s+(device|devices)\b",
    r"\bmost\s+(power|energy|consum(ing|ption)?|usage)\b",
    r"\bhighest\s+(power|energy|consum(ing|ption)?|usage)\b",
    r"which of my devices.*(use|using).*(power|energy)"
]

def detect_intent(text: str):
    t = text.lower()
    for pat in TOP_DEVICES_PATTERNS:
        if re.search(pat, t):
            return "top_devices"
    return "total_usage"


def parse_query(text: str):
    """
    Returns dict: { intent, device_slug?, start?, end? }
    Supported intents: total_usage, top_devices
    """
    now = datetime.now(timezone.utc)

    intent = detect_intent(text)
    start, end = extract_time_range(text, now)
    device_slug = extract_device_slug(text)

    return {
        "intent": intent,
        "device_slug": device_slug,
        "start": start,
        "end": end,
    }



import re
from datetime import datetime, timedelta

DEVICES = ["fridge", "ac", "tv", "heater", "fan", "washing machine", "lights"]

def extract_entities(question: str):
    """
    Extract entities such as devices and time range from the question.
    Returns a dictionary with keys: devices, start_date, end_date
    """
    entities = {
        "devices": [],
        "start_date": None,
        "end_date": None,
    }

    q_lower = question.lower()

    # --- Device extraction ---
    for device in DEVICES:
        if device in q_lower:
            entities["devices"].append(device)

    # --- Time extraction ---
    today = datetime.today().date()

    if "today" in q_lower:
        entities["start_date"] = today
        entities["end_date"] = today

    elif "yesterday" in q_lower:
        yesterday = today - timedelta(days=1)
        entities["start_date"] = yesterday
        entities["end_date"] = yesterday

    elif "last week" in q_lower:
        start = today - timedelta(days=7)
        entities["start_date"] = start
        entities["end_date"] = today

    elif "last month" in q_lower:
        start = today - timedelta(days=30)
        entities["start_date"] = start
        entities["end_date"] = today

    # default fallback → if no time range, assume "today"
    if not entities["start_date"]:
        entities["start_date"] = today
        entities["end_date"] = today

    return entities
