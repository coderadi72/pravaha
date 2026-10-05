"""Persistable explanations derived solely from the scored candidate signals."""


def generate_match_evidence(extracted, schedule, signals):
    evidence = []

    def add(signal, outcome, text):
        evidence.append({"signal": signal, "outcome": outcome, "text": text})

    similarity = signals["activity"]["similarity"]
    add("activity", "support" if similarity >= .75 else "partial" if similarity > 0 else "conflict", f"Activity wording is compatible: {extracted['activityName']} ↔ {schedule['activityName']}." if similarity >= .75 else f"Activity wording has {'limited' if similarity > 0 else 'no clear'} overlap with {schedule['activityName']}.")
    identifier = signals["identifier"]
    if identifier["exact"]:
        add("identifier", "support", f"Identifier matched: {', '.join(identifier['exact'])}.")
    elif identifier["conflict"]:
        add("identifier", "conflict", f"Identifiers differ: {', '.join(extracted['identifiers'])} ↔ {', '.join(identifier['candidate'])}.")
    elif identifier["partial"]:
        add("identifier", "partial", "Only part of the line identifier agrees; its suffix needs verification.")
    else:
        add("identifier", "missing", "The schedule activity does not contain the reported identifier." if extracted["identifiers"] else "No unique identifier was reported in the field text.")
    discipline = signals["discipline"]
    add("discipline", "conflict" if discipline["conflict"] else "support" if discipline["similarity"] else "missing", f"Discipline differs: {extracted['discipline']} ↔ {schedule['discipline']}." if discipline["conflict"] else f"Compatible discipline: {extracted['discipline']} ↔ {schedule['discipline']}." if discipline["similarity"] else "Discipline could not be compared.")
    location = signals["location"]
    add("location", "conflict" if location["conflict"] else "support" if location["similarity"] == 1 else "partial" if location["similarity"] else "missing", f"Location differs: {extracted['location']} ↔ {location['candidate']}." if location["conflict"] else f"Location matched: {extracted['location']}." if location["similarity"] == 1 else f"Location partly agrees: {extracted['location']} ↔ {location['candidate']}; verify the work area." if location["similarity"] else "Location evidence is incomplete; no location agreement is assumed.")
    if signals["keywords"]["similarity"]:
        add("keywords", "support", f"Shared work terms: {', '.join(signals['keywords']['shared'])}.")
    if not any(item["outcome"] == "conflict" for item in evidence):
        add("conflicts", "support", "No major conflicting signals were detected in the available information.")
    return evidence


def explain_recommendation(candidates, ambiguous, recommended_match_id, extracted):
    best = candidates[0] if candidates else None
    support = [item["text"] for item in best["evidence"] if item["outcome"] == "support" and item["signal"] != "conflicts"] if best else []
    conflicts = [item["text"] for item in best["evidence"] if item["outcome"] in ("conflict", "partial")] if best else []
    match_reason = " ".join(support) or "No supporting schedule match evidence was found."
    if not best:
        unmatch_reason = "No project schedule activity has enough activity or identifier overlap with this field text."
    elif ambiguous:
        scores = "; ".join(f"{item['activityName']}: {item['score']}%" for item in candidates[:2])
        identifier_reason = "The available identifiers do not distinguish them." if extracted["identifiers"] else "No unique identifier was reported."
        unmatch_reason = f"Multiple plausible activities have close scores ({scores}). {identifier_reason} Select the correct activity or mark this update unmatched."
    elif not recommended_match_id:
        reason = " ".join(conflicts) or "More activity, identifier, or location information is needed."
        unmatch_reason = f"The strongest candidate is below the 60% recommendation threshold. {reason} Select an activity or request more information."
    else:
        unmatch_reason = "A recommendation requires PM confirmation before it becomes a confirmed schedule link." + (" " + " ".join(conflicts) if conflicts else "")
    return {"matchReason": match_reason, "unmatchReason": unmatch_reason}
