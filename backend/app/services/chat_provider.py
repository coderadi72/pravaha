"""Groq / hosted NVIDIA transport; server-controlled retrieval, no native tools."""
import asyncio
from dataclasses import dataclass, field
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
import json
import logging
import math
import time
from typing import Protocol
import httpx

logger = logging.getLogger("pravaha.ai")


@dataclass
class ProviderFailure(Exception):
    code: str
    retry_after: float | None = None


@dataclass
class Completion:
    content: str
    provider: str
    model: str
    usage: dict = field(default_factory=dict)
    rate_limits: dict = field(default_factory=dict)


class ChatProvider(Protocol):
    async def complete(self, messages: list[dict]) -> Completion: ...


def configured_providers(settings):
    if settings.ai_provider == "none":
        return []
    order = settings.ai_provider_order if settings.ai_provider == "auto" else [settings.ai_provider] + [p for p in settings.ai_provider_order if p != settings.ai_provider]
    if settings.ai_provider not in {"auto", "groq", "nvidia"}:
        return []
    result = []
    for name in order:
        if name not in {"groq", "nvidia"}:
            continue
        explicit = settings.ai_provider == name
        key = getattr(settings, name + "_api_key") or (settings.ai_api_key if explicit else "")
        model = getattr(settings, name + "_model")
        # Generic overrides apply only when provider-specific values retain defaults.
        if explicit and settings.ai_model and name + "_model" not in settings.model_fields_set:
            model = settings.ai_model
        base = getattr(settings, name + "_base_url")
        if explicit and settings.ai_base_url and name + "_base_url" not in settings.model_fields_set:
            base = settings.ai_base_url
        if key and model:
            result.append((name, key, model, base.rstrip("/")))
    return result


def provider_status(settings):
    if settings.ai_provider == "none":
        return "DISABLED"
    return "CONFIGURED" if configured_providers(settings) else "NOT_CONFIGURED"


def retry_after(value):
    try:
        seconds = float(value)
        return max(0.0, seconds) if math.isfinite(seconds) else None
    except (ValueError, TypeError):
        try:
            return max(0.0, (parsedate_to_datetime(value) - datetime.now(UTC)).total_seconds())
        except (ValueError, TypeError, OverflowError):
            return None


def normalize_failure(status, data, headers):
    error = data.get("error", {}) if isinstance(data, dict) else {}
    text = str(error).lower()
    if status == 429:
        return ProviderFailure("PROVIDER_RATE_LIMITED", retry_after(headers.get("retry-after")))
    if any(x in text for x in ("insufficient_quota", "quota_exceeded", "billing", "credit balance", "payment required")) or status == 402:
        return ProviderFailure("PROVIDER_QUOTA", retry_after(headers.get("retry-after")))
    if status in {404, 410} or any(x in text for x in ("model_not_found", "model_decommissioned", "unknown model", "model does not exist", "model is not available")):
        return ProviderFailure("MODEL_UNAVAILABLE")
    if status in {401, 403}:
        return ProviderFailure("PROVIDER_AUTHENTICATION")
    if status == 422:
        return ProviderFailure("PROVIDER_CONFIGURATION")
    if status == 413 or (status == 400 and any(x in text for x in ("context", "maximum tokens", "too many tokens", "reduce", "too large"))):
        return ProviderFailure("CONTEXT_OVERFLOW")
    if status == 400:
        return ProviderFailure("PROVIDER_CONFIGURATION")
    return ProviderFailure("PROVIDER_UNAVAILABLE")


class CompatibleChatProvider:
    name = ""
    def __init__(self, settings, key, model, base_url):
        self.settings, self.key, self.model, self.base_url = settings, key, model, base_url

    async def complete(self, messages):
        s = self.settings
        if 64 + sum(len(m["content"].encode("utf-8")) + 16 for m in messages) > s.ai_max_input_tokens:
            raise ProviderFailure("CONTEXT_OVERFLOW")
        payload = {"model": self.model, "messages": messages, "stream": False,
                   "max_completion_tokens" if self.name == "groq" else "max_tokens": s.ai_max_output_tokens if self.name == "groq" else min(s.ai_max_output_tokens, s.nvidia_max_output_tokens)}
        if self.name == "groq" and self.model.startswith("openai/gpt-oss-") and s.groq_reasoning_effort:
            payload["reasoning_effort"] = s.groq_reasoning_effort
            payload["include_reasoning"] = False
        if self.name == "nvidia" and s.nvidia_reasoning_effort is not None:
            if self.model.startswith("z-ai/glm-5.3"):
                if s.nvidia_reasoning_effort != "none":
                    payload["reasoning_effort"] = s.nvidia_reasoning_effort
                payload["chat_template_kwargs"] = {"clear_thinking": True}
            elif self.model.startswith("nvidia/nemotron-"):
                payload["chat_template_kwargs"] = {"enable_thinking": s.nvidia_reasoning_effort != "none"}
                if s.nvidia_reasoning_effort != "none":
                    payload["chat_template_kwargs"]["low_effort"] = s.nvidia_reasoning_effort == "low"
        if s.ai_response_format == "json_object" and not (self.name == "nvidia" and self.model.startswith("z-ai/glm-5.3")):
            payload["response_format"] = {"type": "json_object"}
        try:
            async with httpx.AsyncClient(timeout=s.ai_request_timeout_seconds, follow_redirects=False) as client:
                async with client.stream("POST", self.base_url + "/chat/completions", headers={"Authorization": "Bearer " + self.key}, json=payload) as response:
                    raw = bytearray()
                    async for part in response.aiter_bytes():
                        raw.extend(part)
                        if len(raw) > s.ai_max_response_bytes:
                            raise ProviderFailure("RESPONSE_LIMIT")
                    try:
                        data = json.loads(raw)
                    except ValueError:
                        data = {}
                    if response.status_code != 200:
                        logger.warning("AI provider: %s; HTTP status: %s", self.name, response.status_code)
                        raise normalize_failure(response.status_code, data, response.headers)
                    rate_limits = {}
                    for kind in ("requests", "tokens"):
                        for field_name in ("limit", "remaining", "reset"):
                            value = response.headers.get(f"x-ratelimit-{field_name}-{kind}")
                            if value and len(value) <= 40 and all(c.isdigit() or c in ".smhd" for c in value):
                                rate_limits[f"{field_name}_{kind}"] = value
            choice = data["choices"][0]
            if choice.get("finish_reason") == "length":
                raise ProviderFailure("OUTPUT_TRUNCATED")
            if choice.get("finish_reason") != "stop" or choice["message"].get("tool_calls"):
                raise ProviderFailure("INVALID_PROVIDER_RESPONSE")
            text = choice["message"]["content"]
            if not isinstance(text, str) or not text.strip():
                raise ProviderFailure("INVALID_PROVIDER_RESPONSE")
            usage = {k: v for k, v in (data.get("usage") or {}).items() if k in {"prompt_tokens", "completion_tokens", "total_tokens"} and type(v) is int and v >= 0}
            return Completion(text, self.name, self.model, usage, rate_limits)
        except httpx.TimeoutException as exc:
            raise ProviderFailure("PROVIDER_TIMEOUT") from exc
        except httpx.RequestError as exc:
            logger.warning("AI provider: %s; Network failure type: %s", self.name, type(exc).__name__)
            raise ProviderFailure("PROVIDER_UNAVAILABLE") from exc
        except (ValueError, KeyError, IndexError, TypeError, AttributeError) as exc:
            raise ProviderFailure("INVALID_PROVIDER_RESPONSE") from exc


class GroqProvider(CompatibleChatProvider):
    name = "groq"


class NvidiaProvider(CompatibleChatProvider):
    name = "nvidia"


class ProviderPool:
    """Per-worker cooldown and explicit daily request reservation, not billing estimates."""
    def __init__(self, settings):
        self.settings = settings
        self.providers = [({"groq": GroqProvider, "nvidia": NvidiaProvider}[name])(settings, key, model, base) for name, key, model, base in configured_providers(settings)]
        self.cooldowns = {}
        self.health = {name: {"status": "configured" if any(p.name == name for p in self.providers) else "not_configured", "lastFailure": None, "lastSuccess": None, "rateLimits": {}} for name in ("groq", "nvidia")}
        self.day, self.requests = None, 0
        self._lock = asyncio.Lock()
        logger.info("AI configuration: %s; configured providers: %s", provider_status(settings), ",".join(p.name for p in self.providers) or "none")
        for name in settings.ai_provider_order:
            if settings.ai_provider != "none" and not getattr(settings, name + "_api_key") and not (settings.ai_provider == name and settings.ai_api_key):
                logger.info("AI provider: %s; Status: API key missing", name)

    async def reserve(self):
        async with self._lock:
            day = datetime.now(UTC).date()
            if day != self.day:
                self.day, self.requests = day, 0
            if self.settings.ai_daily_request_budget and self.requests >= self.settings.ai_daily_request_budget:
                raise ProviderFailure("APPLICATION_BUDGET")
            self.requests += 1

    async def complete(self, messages, validate, reduce_context):
        if not self.providers:
            raise ProviderFailure(provider_status(self.settings))
        last = ProviderFailure("PROVIDER_COOLDOWN")
        for provider in self.providers:
            if self.cooldowns.get(provider.name, 0) > time.monotonic():
                logger.info("AI provider: %s; Status: cooldown; trying next configured provider", provider.name)
                continue
            current = messages
            for attempt in range(self.settings.ai_max_retries + 1):
                if 64 + sum(len(m["content"].encode("utf-8")) + 16 for m in current if isinstance(m, dict)) > self.settings.ai_max_input_tokens:
                    raise ProviderFailure("CONTEXT_OVERFLOW")
                await self.reserve()
                try:
                    logger.info("AI provider: %s; Status: request started", provider.name)
                    result = await provider.complete(current)
                    validated = validate(result, current)
                    self.health[provider.name] = {"status": "available", "lastFailure": self.health.get(provider.name, {}).get("lastFailure"), "lastSuccess": datetime.now(UTC).isoformat(), "rateLimits": result.rate_limits}
                    logger.info("AI provider: %s; Status: successful response", provider.name)
                    return validated
                except ProviderFailure as exc:
                    last = exc
                    if exc.code == "UNSAFE_ASSISTANT_RESPONSE":
                        logger.warning("AI provider: %s; Status: unsafe response rejected", provider.name)
                        raise  # A policy rejection is not a provider outage and must not trigger another paid call.
                    status = "rate_limited" if exc.code in {"PROVIDER_RATE_LIMITED", "PROVIDER_RATE_LIMIT", "PROVIDER_QUOTA"} else "timeout" if exc.code == "PROVIDER_TIMEOUT" else "invalid_configuration" if exc.code in {"PROVIDER_CONFIGURATION", "PROVIDER_AUTHENTICATION", "MODEL_UNAVAILABLE"} else "temporarily_unavailable"
                    self.health.setdefault(provider.name, {}).update({"status": status, "lastFailure": {"code": exc.code, "at": datetime.now(UTC).isoformat()}})
                    logger.warning("AI provider: %s; Status: request failed (%s)", provider.name, exc.code)
                    if exc.code == "APPLICATION_BUDGET":
                        raise
                    if exc.code == "CONTEXT_OVERFLOW" and attempt < self.settings.ai_max_retries:
                        current = reduce_context(current)
                        continue
                    if exc.code in {"PROVIDER_UNAVAILABLE", "PROVIDER_TIMEOUT"} and attempt < self.settings.ai_max_retries:
                        await asyncio.sleep(0.2)
                        continue
                    if exc.code == "INVALID_EVIDENCE_RESPONSE" and attempt < self.settings.ai_max_retries:
                        current = [{**m, "content": m["content"] + "\nReturn one valid JSON object matching the required schema. Copy evidenceId values exactly from the supplied records; do not shorten or invent IDs."} if m["role"] == "system" else m for m in current]
                        continue
                    duration = exc.retry_after if exc.retry_after is not None else self.settings.ai_cooldown_seconds
                    self.cooldowns[provider.name] = time.monotonic() + min(duration, 86400)
                    break
        raise last
