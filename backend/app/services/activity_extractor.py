"""Deterministic Phase 7 extraction; no external models or persistence."""

import re
import unicodedata


def normalize_text(value=""):
    text = unicodedata.normalize("NFKC", str(value))
    return re.sub(r"\s+", " ", re.sub(r"[‐‑‒–—−]", "-", text).lower()).strip()


def extract_identifiers(value=""):
    text = normalize_text(value)
    identifiers = []
    for match in re.finditer(r"\b(?:line|pipeline)\s*(?:no\.?\s*)?(\d+(?:\s*-\s*[a-z0-9]+)*)\b", text):
        identifiers.append("Line " + re.sub(r"\s*-\s*", "-", match[1]).upper())
    for match in re.finditer(r"\b(pt|lt|ft|tt|jb|hv|[pvekfmtc])\s*-\s*(\d+[a-z]?(?:-[a-z0-9]+)*)\b", text):
        identifiers.append(f"{match[1].upper()}-{match[2].upper()}")
    return sorted(set(identifiers))


def extract_location(value=""):
    text = normalize_text(value)
    locations = []
    patterns = [
        (r"\bblock\s*([a-z0-9]+)(?:\s+(north|south|east|west))?\b", "Block"),
        (r"\bunit\s*([a-z0-9]+)\b", "Unit"),
        (r"\brack\s*([a-z0-9]+)\b", "Rack"),
        (r"\barea\s*([a-z0-9]+)\b", "Area"),
        (r"\bskid\s*-?\s*(\d+)\b", "Skid"),
        (r"\bsubstation(?:\s+([a-z]|\d+))?\b", "Substation"),
        (r"\bpackage\s*([a-z0-9]+)\b", "Package"),
    ]
    for pattern, label in patterns:
        for match in re.finditer(pattern, text):
            suffix = ("-" if label == "Skid" else " ") + match[1].upper() if match[1] else ""
            qualifier = " " + match[2].capitalize() if len(match.groups()) > 1 and match[2] else ""
            locations.append(label + suffix + qualifier)
    for phrase, label in [("compressor area", "Compressor area"), ("turbine hall", "Turbine hall"), ("pump house", "Pump house"), ("tank farm", "Tank farm")]:
        if phrase in text:
            locations.append(label)
    locations = [location for location in dict.fromkeys(locations) if not re.fullmatch(r"Area (AND|NEAR|AT|IN|FOR|THE|COMPLETED|STARTED)", location)]
    return " / ".join(locations) or None


ACTIVITY_RULES = [
    (r"cable\s*tray", "Cable Tray Installation", "Electrical", "install", "cable tray"),
    (r"pressure\s*transmitter", "Pressure Transmitter Installation", "Instrumentation", "install", "transmitter"),
    (r"transmitter|junction\s*box|instrument", "Instrument Installation", "Instrumentation", "install", "instrument"),
    (r"foundation|concrete\s*(?:pour|poured)|(?:pour|poured).*concrete", "Foundation Concreting", "Civil", "pour", "foundation"),
    (r"excavat|earthwork", "Excavation", "Civil", "excavate", "excavation"),
    (r"rebar|reinforcement", "Rebar Installation", "Civil", "install", "rebar"),
    (r"support\s*steel|steel\s*support|structural\s*steel", "Support Steel Installation", "Civil", "install", "steel"),
    (r"fit[ -]?up|joint\s*(?:fit|weld)", "Pipe Joint Fit-up", "Piping", "fit", "pipe"),
    (r"hydrotest|pressure\s*test", "Pressure Testing", "Piping", "test", "pipe"),
    (r"spool", "Spool Erection", "Piping", "erect", "pipe"),
    (r"valve", "Valve Installation", "Piping", "install", "valve"),
    (r"flange", "Flange Installation", "Piping", "install", "flange"),
    (r"align", "Equipment Alignment", None, "align", "equipment"),
    (r"\berect|erection", "Line Erection", "Piping", "erect", "pipe"),
    (r"cable|earthing|lighting|substation", "Electrical Installation", "Electrical", "install", "cable"),
    (r"insulat", "Equipment Insulation", "Mechanical", "insulate", "equipment"),
    (r"safety|permit|hse|scaffold", "Safety Inspection", "HSE", "inspect", "safety"),
    (r"vessel|tank|exchanger", "Static Equipment Installation", "Static Equipment", "install", "equipment"),
    (r"pump|compressor|turbine|motor", "Rotating Equipment Installation", "Rotating Equipment", "install", "equipment"),
    (r"mechanical|equipment", "Mechanical Work", "Mechanical", None, "equipment"),
]


def extract_field_activity(description, context=None):
    context = context or {}
    text = normalize_text(description)
    rule = next((rule for rule in ACTIVITY_RULES if re.search(rule[0], text)), None)
    discipline = rule[2] if rule else None
    if not discipline and re.search(r"pump|compressor|motor|turbine", text):
        discipline = "Rotating Equipment"
    discipline = discipline or context.get("discipline") or "Unclassified"
    action = re.search(r"\b(erected|erect|poured|pour|installed|install|aligned|align|completed|complete|finished|started|start|progressing|blocked|delayed|replaced|replace)\b", text)
    action = action[1] if action else rule[3] if rule else None
    completion = bool(re.search(r"\b(completed|complete|finished)\b", text) and not re.search(r"\b(not|never|incomplete)\b.{0,24}\b(completed|complete|finished)\b", text))
    reported_progress = re.search(r"\b(100|\d{1,2})\s*(?:%|percent\b)", text)
    detected_location = extract_location(text)
    replacement = bool(re.search(r"\breplac", text))
    activity_name = rule[1].replace("Installation", "Replacement", 1) if rule and replacement else rule[1] if rule else "Field activity"
    date_pattern = r"\b(?:\d{4}-\d{2}-\d{2}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*(?:\s+\d{4})?|today|yesterday|tomorrow)\b"
    return {
        "activityName": activity_name, "discipline": discipline,
        "location": detected_location or context.get("location") or None,
        "locationSource": "text" if detected_location else "reported" if context.get("location") else "not_reported",
        "identifiers": extract_identifiers(text), "action": action,
        "actionFamily": "replace" if replacement else rule[3] if rule else None,
        "workType": rule[4] if rule else None,
        "progress": int(reported_progress[1]) if reported_progress else 100 if completion else None,
        "completion": completion,
        "blocked": bool(re.search(r"\b(blocked|delayed|shortage|unavailable|not available)\b", text)),
        "dateReferences": list(dict.fromkeys(match[0] for match in re.finditer(date_pattern, text))),
    }
