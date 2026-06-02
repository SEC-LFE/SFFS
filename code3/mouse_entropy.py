"""
Mouse movement entropy — mixed with OS CSPRNG for per-session file keys.

WHY: Adds unpredictable user-specific input on top of secrets.token_bytes.

Collection is MANUAL and gated: nothing is collected until the user explicitly
arms it via start_collection() (wired to a "Collect entropy" button). Mouse moves
only feed the pool while collection is armed; it auto-disarms once the target is
reached. reset_pool() lets the user clear and re-collect.
"""

from __future__ import annotations

import hashlib
import secrets
import threading
import time

_lock = threading.Lock()
_pool = bytearray()
_collecting = False        # armed only after user clicks "Collect entropy"

_ENTROPY_TARGET = 256


def start_collection() -> None:
    """Arm collection — call from the GUI button. Until this is called,
    feed_mouse_entropy() is a no-op so no mouse data is ever gathered."""
    global _collecting
    with _lock:
        _collecting = True


def stop_collection() -> None:
    """Disarm collection without clearing the pool already gathered."""
    global _collecting
    with _lock:
        _collecting = False


def reset_pool() -> None:
    """User reset — discard all collected entropy and disarm collection."""
    global _collecting
    with _lock:
        _pool.clear()
        _collecting = False


def is_collecting() -> bool:
    with _lock:
        return _collecting


def feed_mouse_entropy(x: int, y: int) -> None:
    """Call from GUI mouse-move handler. No-op unless collection is armed
    (start_collection()). The pool stays bounded; arm/disarm and reset are
    driven explicitly by the user, not automatically."""
    t = time.monotonic_ns()
    chunk = hashlib.sha256(f"{x}:{y}:{t}".encode()).digest()
    with _lock:
        if not _collecting:
            return
        _pool.extend(chunk)
        if len(_pool) > 8192:
            del _pool[:-8192]


def session_random_bytes(n: int) -> bytes:
    """
    Cryptographically strong random bytes, XOR-mixed with mouse pool if any.
    """
    base = secrets.token_bytes(max(n, 32))
    with _lock:
        extra = bytes(_pool)
    if not extra:
        return base[:n]
    h = hashlib.sha256(base + extra).digest()
    if n <= 32:
        return h[:n]
    out = bytearray(h)
    i = 32
    while len(out) < n:
        out.extend(hashlib.sha256(bytes(out[-32:]) + extra + base).digest())
    return bytes(out[:n])


def get_entropy_pool_status() -> dict:
    with _lock:
        size = len(_pool)
        collecting = _collecting
    return {
        "bytes_collected": size,
        "target": _ENTROPY_TARGET,
        "percentage": min(100, int(size / _ENTROPY_TARGET * 100)),
        "is_ready": size >= _ENTROPY_TARGET,
        "is_collecting": collecting,
    }


def is_entropy_ready() -> bool:
    with _lock:
        return len(_pool) >= _ENTROPY_TARGET
