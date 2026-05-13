from datetime import datetime, timezone

try:
    from datetime import UTC
except ImportError:  # pragma: no cover - compatibility for local Python 3.10 tooling
    UTC = timezone.utc


def utcnow() -> datetime:
    return datetime.now(UTC)

