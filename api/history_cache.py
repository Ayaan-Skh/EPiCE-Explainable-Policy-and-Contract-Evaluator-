"""
Query history and response cache.
Does not modify core pipeline logic; wraps around it for performance and analytics.
"""
import json
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

# In-memory response cache: key -> (response_dict, expiry_time)
_response_cache: Dict[str, tuple] = {}
CACHE_TTL_SECONDS = 300  # 5 minutes
CACHE_MAX_ENTRIES = 500

# History file path
HISTORY_DIR = Path("data/processed")
HISTORY_FILE = HISTORY_DIR / "query_history.json"


def _cache_key(query: str, top_k: int) -> str:
    raw = f"{query.strip().lower()}|{top_k}"
    return hashlib.sha256(raw.encode()).hexdigest()


def get_cached_response(query: str, top_k: int) -> Optional[Dict[str, Any]]:
    """Return cached response if present and not expired."""
    key = _cache_key(query, top_k)
    if key not in _response_cache:
        return None
    data, expiry = _response_cache[key]
    if time.time() > expiry:
        del _response_cache[key]
        return None
    return data


def set_cached_response(query: str, top_k: int, response: Dict[str, Any]) -> None:
    """Store response in cache with TTL."""
    key = _cache_key(query, top_k)
    # Simple eviction: if over limit, drop oldest half by clearing (no ordered dict needed)
    if len(_response_cache) >= CACHE_MAX_ENTRIES:
        expired = [k for k, (_, exp) in _response_cache.items() if time.time() > exp]
        for k in expired:
            del _response_cache[k]
        if len(_response_cache) >= CACHE_MAX_ENTRIES:
            _response_cache.clear()
    _response_cache[key] = (response, time.time() + CACHE_TTL_SECONDS)


def _load_history() -> List[Dict[str, Any]]:
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []


def _save_history(entries: List[Dict[str, Any]]) -> None:
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(entries[-5000:], f, indent=2)  # Keep last 5000 entries


def append_to_history(
    query: str,
    top_k: int,
    response: Dict[str, Any],
    from_cache: bool = False,
) -> None:
    """Append a successful query result to history."""
    entry = {
        "id": hashlib.sha256(f"{query}{time.time()}".encode()).hexdigest()[:16],
        "query": query,
        "top_k": top_k,
        "timestamp": response.get("timestamp", time.strftime("%Y-%m-%d %H:%M:%S")),
        "processing_time_seconds": response.get("processing_time_seconds"),
        "approved": response.get("decision", {}).get("approved"),
        "from_cache": from_cache,
    }
    history = _load_history()
    history.append(entry)
    _save_history(history)


def get_history(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """Return recent history entries (newest first)."""
    history = _load_history()
    history.reverse()
    return history[offset : offset + limit]


def get_analytics() -> Dict[str, Any]:
    """Compute analytics from history (and optionally cache stats)."""
    history = _load_history()
    total = len(history)
    approved = sum(1 for e in history if e.get("approved") is True)
    rejected = sum(1 for e in history if e.get("approved") is False)
    times = [e["processing_time_seconds"] for e in history if e.get("processing_time_seconds") is not None]
    avg_time = sum(times) / len(times) if times else 0
    from_cache_count = sum(1 for e in history if e.get("from_cache"))
    return {
        "total_queries": total,
        "approved_count": approved,
        "rejected_count": rejected,
        "approval_rate": round(100 * approved / total, 2) if total else 0,
        "avg_processing_time_seconds": round(avg_time, 3),
        "cache_hits": from_cache_count,
        "cache_size": len(_response_cache),
    }
