"""Bounded live checks over only the isolated Greenfield Refinery demo copy."""
import argparse
import json
import logging
from pathlib import Path
from fastapi.testclient import TestClient
from backend.app.core.config import Settings
from backend.app.db.session import create_engine_and_factory
from backend.app.main import create_app
from backend.app.services.chat_provider import ProviderFailure
from scripts.phase12_runtime import state, digest

ROOT = Path(__file__).resolve().parents[1]


class Diagnostics(logging.Handler):
    def __init__(self):
        super().__init__()
        self.messages = []

    def emit(self, record):
        self.messages.append(record.getMessage())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("provider", choices=["groq", "nvidia", "auto", "fallback"])
    args = parser.parse_args()
    value = state()
    assert value.get("organization") == "ORG-OIL-DEMO" and value.get("project") == "PRJ-001" and not value.get("cleanedUp"), "Only the active isolated Greenfield demo fixture is permitted."
    canonical = Settings()
    selected = "auto" if args.provider in {"auto", "fallback"} else args.provider
    settings = canonical.model_copy(update={"db_schema": value["schema"], "app_env": "test", "ai_provider": selected,
        "ai_provider_order": ["groq", "nvidia"] if selected == "auto" else [selected], "ai_max_retries": canonical.ai_max_retries if args.provider == "nvidia" else 0})
    engine, factory = create_engine_and_factory(settings)
    before, canonical_before = digest(settings), digest(canonical)
    handler = Diagnostics()
    logger = logging.getLogger("pravaha.ai")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    try:
        app = create_app(settings, factory, engine)
        if args.provider == "fallback":
            class UnavailablePrimary:
                name = "groq"
                async def complete(self, messages):
                    raise ProviderFailure("PROVIDER_UNAVAILABLE")
            app.state.assistant_providers.providers[0] = UnavailablePrimary()
        with TestClient(app) as client:
            assert client.post("/api/auth/login", json={"email":"browser-pm", "password":"BrowserManagerPass123!"}).status_code == 200
            contexts = client.get("/api/assistant/contexts").json()
            assert contexts["projects"] == [{"id":"PRJ-001", "name":"Greenfield Refinery"}]
            report = {"providerSelection": args.provider, "syntheticOrganization":"ORG-OIL-DEMO", "project":"Greenfield Refinery", "checks":[]}
            questions = ["What are the main execution items I should review for Greenfield Refinery?"]
            if args.provider == "nvidia":
                questions.append("How do I submit a field update?")
            for question in questions:
                response = client.post("/api/assistant/ask", json={"question":question, "project_id":"PRJ-001"})
                assert response.status_code == 200, f"Assistant status {response.status_code}"
                data = response.json()
                assert data["context"]["organizationId"] == "ORG-OIL-DEMO" and data["context"]["role"] == "PROJECT_MANAGER"
                assert data["mode"] == "AI", f"Live response mode {data['mode']}; safe category {data['failure']}"
                assert "provider" not in data and "model" not in data
                for source in data["evidence"]:
                    assert client.get(source["source"]).status_code == 200
                report["checks"].append({"question":question,"mode":data["mode"],"answer":data["answer"],"evidence":[{k:v for k,v in r.items() if k!="source"} for r in data["evidence"]],"usage":data["usage"]})
            expected = next((name for name in ("groq", "nvidia") if f"AI provider: {name}; Status: successful response" in handler.messages), None) if args.provider == "auto" else "nvidia" if args.provider == "fallback" else args.provider
            assert any(f"AI provider: {expected}; Status: successful response" == line for line in handler.messages)
        assert before == digest(settings) and canonical_before == digest(canonical), "Domain records changed"
        report["diagnostics"] = handler.messages
        report["successfulProvider"] = expected
        report["fallbackCondition"] = "Controlled unavailable primary, genuine NVIDIA secondary" if args.provider == "fallback" else "Actual configured primary failure, genuine secondary" if args.provider == "auto" and expected == "nvidia" else None
        serialized = json.dumps(report, ensure_ascii=False, indent=2)
        assert all(secret not in serialized for secret in (canonical.groq_api_key, canonical.nvidia_api_key, canonical.ai_api_key) if secret)
        (ROOT/f".audit/assistant-live-{args.provider}.json").write_text(serialized, encoding="utf-8")
        print({"check":args.provider,"liveProviderSucceeded":expected,"answers":len(questions),"sources":"PASS","authorization":"PROJECT_MANAGER / ORG-OIL-DEMO","domainData":"UNCHANGED"})
    except AssertionError:
        diagnostics = json.dumps({"selection":args.provider, "diagnostics":handler.messages}, ensure_ascii=False)
        assert all(secret not in diagnostics for secret in (canonical.groq_api_key, canonical.nvidia_api_key, canonical.ai_api_key) if secret)
        (ROOT/f".audit/assistant-live-{args.provider}-failure.json").write_text(diagnostics, encoding="utf-8")
        print({"safeDiagnostics":handler.messages})
        raise
    finally:
        logger.removeHandler(handler)
        engine.dispose()


if __name__ == "__main__":
    main()
