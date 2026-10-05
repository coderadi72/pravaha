"""Phase 7 deterministic matching behind an independent service boundary."""

import re
from datetime import datetime, timezone

from .activity_extractor import extract_field_activity, extract_identifiers, extract_location, normalize_text
from .confidence import calculate_confidence
from .match_evidence import explain_recommendation, generate_match_evidence

MATCHER_VERSION = "matcher-v1"
STOP_WORDS = set("a an and at by completed complete finished for from in installation installed install of on started start the to was were with line no near progressing progress update".split())
CANONICAL_WORDS = {"erection": "erect", "erected": "erect", "alignment": "align", "aligned": "align", "pouring": "pour", "poured": "pour", "concreting": "concrete", "spools": "spool", "sections": "section", "joints": "joint", "fitted": "fit", "installation": "install"}


def _words(text):
    words = [CANONICAL_WORDS.get(word, word) for word in re.sub(r"[^a-z0-9 ]", " ", normalize_text(text)).split(" ")]
    return list(dict.fromkeys(word for word in words if word and word not in STOP_WORDS and not word.isdigit()))


def _edit_similarity(left, right):
    if left == right:
        return 1
    if len(left) < 4 or len(right) < 4 or abs(len(left) - len(right)) > 2:
        return 0
    row = list(range(len(right) + 1))
    for i in range(1, len(left) + 1):
        next_row = [i]
        for j in range(1, len(right) + 1):
            next_row.append(min(next_row[j - 1] + 1, row[j] + 1, row[j - 1] + int(left[i - 1] != right[j - 1])))
        row = next_row
    return .8 if row[-1] <= 1 else 0


def _word_similarity(left, right):
    return sum(max(_edit_similarity(word, other) for other in right) for word in left) / max(len(left), len(right)) if left and right else 0


def _discipline_compatible(left, right):
    if left == right:
        return 1
    equipment = {"Mechanical", "Static Equipment", "Rotating Equipment", "Static / Rotating Equipment"}
    generic = {"Mechanical", "Static / Rotating Equipment"}
    return .8 if left in equipment and right in equipment and (left in generic or right in generic) else 0


def _identifier_signal(field, candidate):
    exact = [identifier for identifier in field if identifier in candidate]
    partial = not exact and any(identifier.startswith("Line ") and any(other.startswith("Line ") and (identifier == other.split("-")[0] or other == identifier.split("-")[0]) for other in candidate) for identifier in field)
    conflict = bool(field and candidate and len(exact) < len(field) and not partial)
    return {"available": bool(field or candidate), "similarity": len(exact) / len(field) if exact else .35 if partial else 0, "exact": exact, "partial": bool(partial), "conflict": conflict, "candidate": candidate}


def find_candidate_activities(schedule_activities, project_id):
    return [activity for activity in schedule_activities if activity.get("projectId") == project_id and activity.get("level") in ("L5", "L6")]


def score_candidate(extracted, description, schedule):
    candidate_extracted = extract_field_activity(schedule["activityName"], {"discipline": schedule.get("discipline")})
    field_words, candidate_words = _words(description), _words(schedule["activityName"])
    semantic = (.55 if extracted["workType"] and extracted["workType"] == candidate_extracted["workType"] else 0) + (.45 if extracted["actionFamily"] and extracted["actionFamily"] == candidate_extracted["actionFamily"] else 0)
    activity_similarity = max(_word_similarity(field_words, candidate_words), semantic)
    identifiers = " ".join(schedule["identifiers"]) if isinstance(schedule.get("identifiers"), list) else ""
    identifier = _identifier_signal(extracted["identifiers"], extract_identifiers(f"{schedule['activityName']} {schedule.get('location') or ''} {identifiers}"))
    discipline_known = extracted["discipline"] != "Unclassified" and bool(schedule.get("discipline"))
    discipline_similarity = _discipline_compatible(extracted["discipline"], schedule.get("discipline")) if discipline_known else 0
    candidate_location = schedule.get("location") or extract_location(schedule["activityName"])
    field_location, normalized_location = normalize_text(extracted["location"] or ""), normalize_text(candidate_location or "")
    location_similarity = (1 if field_location == normalized_location else .5 if normalized_location in field_location or field_location in normalized_location else 0) if field_location and normalized_location else 0
    shared = [word for word in field_words if word in candidate_words]
    signals = {
        "activity": {"available": True, "similarity": activity_similarity}, "identifier": identifier,
        "discipline": {"available": discipline_known, "similarity": discipline_similarity, "conflict": discipline_known and not discipline_similarity},
        "location": {"available": bool(field_location or normalized_location), "similarity": location_similarity, "conflict": bool(field_location and normalized_location and not location_similarity), "candidate": candidate_location},
        "keywords": {"available": True, "similarity": min(1, len(shared) / 2), "shared": shared},
    }
    result = {"scheduleActivityId": schedule["id"], "activityName": schedule["activityName"], "location": candidate_location, **calculate_confidence(signals), "evidence": generate_match_evidence(extracted, schedule, signals), "relevant": activity_similarity >= .2 or identifier["similarity"] > 0}
    result.update({key: schedule[key] for key in ("activityId", "level", "discipline") if key in schedule})
    return result


def analyze_field_activity(description, schedule_activities, context=None):
    context = context or {}
    extracted = extract_field_activity(description, context)
    candidates = [score_candidate(extracted, description, schedule) for schedule in find_candidate_activities(schedule_activities, context.get("projectId"))]
    candidates = sorted((candidate for candidate in candidates if candidate.pop("relevant") and candidate["score"] > 0), key=lambda candidate: (-candidate["score"], candidate["scheduleActivityId"]))[:5]
    for index, candidate in enumerate(candidates, start=1):
        candidate["candidateRank"] = index
    best = candidates[0] if candidates else None
    ambiguous = bool(best and best["score"] >= 60 and len(candidates) > 1 and best["score"] - candidates[1]["score"] <= 6)
    recommended_id = best["scheduleActivityId"] if best and best["score"] >= 60 and not ambiguous else None
    return {"extractedActivity": extracted, "match": {
        "confidence": best["score"] if best else 0, "confidenceLevel": best["confidenceLevel"] if best else "low", "candidates": candidates,
        "recommendedMatchId": recommended_id, "recommendationStatus": "ambiguous" if ambiguous else "suggested" if recommended_id else "unmatched",
        "evidence": best["evidence"] if best else [], **explain_recommendation(candidates, ambiguous, recommended_id, extracted),
        "matcherVersion": MATCHER_VERSION, "generatedAt": context.get("generatedAt") or datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
    }}
