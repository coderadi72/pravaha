"""Argon2id and opaque, SHA-256 hashed server-side sessions."""
import base64
import hashlib
import hmac
import re
import secrets
import threading
import time

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from argon2.low_level import Type, hash_secret_raw

PASSWORD_HASHER = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=1, hash_len=32, salt_len=16, type=Type.ID)
COOKIE_NAME = "pravaha_session"


def hash_password(password: str) -> str:
    return PASSWORD_HASHER.hash(password)


def _base64url(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def verify_password(password: str, encoded: str | None) -> bool:
    try:
        if not encoded:
            return False
        if encoded.startswith("$argon2id$"):
            return PASSWORD_HASHER.verify(encoded, password)
        # Phase 6/7 native Node hashes use this fixed Argon2id parameter set.
        scheme, salt_text, digest_text = encoded.split("$")
        if scheme != "argon2id":
            return False
        salt, expected = _base64url(salt_text), _base64url(digest_text)
        if len(salt) != 16 or len(expected) != 32:
            return False
        actual = hash_secret_raw(password.encode("utf-8"), salt, time_cost=3, memory_cost=65536, parallelism=1, hash_len=32, type=Type.ID, version=19)
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError, InvalidHashError, VerificationError):
        return False


def is_valid_password(password) -> bool:
    return isinstance(password, str) and 12 <= len(password) <= 128 and all(re.search(pattern, password) for pattern in (r"[A-Z]", r"[a-z]", r"[0-9]", r"[^A-Za-z0-9]"))


def digest_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def new_session_token() -> str:
    return secrets.token_urlsafe(32)


class LoginRateLimiter:
    """Bounded per-process limiter keyed by direct peer IP and normalized email."""
    def __init__(self, max_attempts=5, window_seconds=15 * 60, max_buckets=10_000):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.max_buckets = max_buckets
        self.buckets = {}
        self._lock = threading.Lock()

    def _cleanup(self, now):
        stale = [key for key, bucket in self.buckets.items() if bucket[1] <= now]
        for key in stale:
            del self.buckets[key]
        return len(stale)

    def cleanup(self, now=None):
        with self._lock:
            return self._cleanup(time.monotonic() if now is None else now)

    def is_limited(self, key, now=None):
        with self._lock:
            self._cleanup(time.monotonic() if now is None else now)
            return self.buckets[key][0] >= self.max_attempts if key in self.buckets else len(self.buckets) >= self.max_buckets

    def record_failure(self, key, now=None):
        with self._lock:
            now = time.monotonic() if now is None else now
            self._cleanup(now)
            if key in self.buckets:
                self.buckets[key][0] += 1
            elif len(self.buckets) < self.max_buckets:
                self.buckets[key] = [1, now + self.window_seconds]

    def clear(self, key):
        with self._lock:
            self.buckets.pop(key, None)


class PostgresLoginRateLimiter:
    """Atomic attempt reservation, shared across workers/restarts; failures survive request rollback."""
    def __init__(self,session_factory,max_attempts=5,window_seconds=900):
        self.session_factory=session_factory
        self.max_attempts=max_attempts
        self.window_seconds=window_seconds

    def is_limited(self,key):
        from datetime import UTC,datetime,timedelta
        from sqlalchemy import case,delete
        from sqlalchemy.dialects.postgresql import insert
        from backend.app.models import LoginRateBucket
        now=datetime.now(UTC)
        with self.session_factory.begin() as session:
            session.execute(delete(LoginRateBucket).where(LoginRateBucket.expires_at<=now))
            statement=insert(LoginRateBucket).values(key_hash=digest_token(key),attempts=1,expires_at=now+timedelta(seconds=self.window_seconds))
            statement=statement.on_conflict_do_update(index_elements=[LoginRateBucket.key_hash],set_={"attempts":LoginRateBucket.attempts+1}).returning(LoginRateBucket.attempts)
            return session.scalar(statement)>self.max_attempts

    def record_failure(self,key):
        pass  # Reserved atomically before password verification.

    def clear(self,key):
        from sqlalchemy import delete
        from backend.app.models import LoginRateBucket
        with self.session_factory.begin() as session:
            session.execute(delete(LoginRateBucket).where(LoginRateBucket.key_hash==digest_token(key)))
