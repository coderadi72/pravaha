"""Explainable confidence weights and Phase 7 threshold semantics."""

from math import floor


def confidence_level(score):
    return "high" if score >= 80 else "medium" if score >= 60 else "low"


def calculate_confidence(signals):
    weights = {"activity": 40, "identifier": 30, "discipline": 15, "location": 10, "keywords": 5}
    available = sum(weight for key, weight in weights.items() if signals[key]["available"])
    earned = sum(weight * signals[key]["similarity"] for key, weight in weights.items())
    penalties = sum(weight for key, weight in {"identifier": 25, "discipline": 20, "location": 15}.items() if signals[key].get("conflict"))
    # JS Math.round rounds half toward +infinity; Python round uses ties-to-even.
    score = max(0, min(100, floor(100 * (earned - penalties) / (available or 1) + 0.5)))
    if signals["identifier"].get("conflict"):
        score = min(score, 49)
    if signals["discipline"].get("conflict"):
        score = min(score, 59)
    if signals["identifier"].get("partial"):
        score = min(score, 79)
    return {"score": score, "confidenceLevel": confidence_level(score)}
