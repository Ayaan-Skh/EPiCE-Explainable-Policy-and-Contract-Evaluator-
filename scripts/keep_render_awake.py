"""
Keep a Render free-tier service awake by pinging it on an interval.

Render free web services sleep after ~15 minutes of inactivity, so the first
request after that stalls for 30-60s. Pinging every 10 minutes keeps it warm.

Usage:
    # Pass the URL directly (base URL or full health URL both work)
    python scripts/keep_render_awake.py --url https://epice-api.onrender.com

    # Or set RENDER_PING_URL in your .env / environment and just run it
    python scripts/keep_render_awake.py

    # Custom interval (seconds)
    python scripts/keep_render_awake.py --interval 300

Notes:
    - This must keep running to have any effect, so the machine it runs on has
      to stay on. For an always-on solution that doesn't depend on your laptop,
      use the GitHub Actions cron workflow instead (ask Claude to add one).
    - Uses only the standard library (no extra dependencies).
"""

import argparse
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime
from urllib.parse import urlparse, urlunparse

# Load RENDER_PING_URL from a local .env if python-dotenv is available (optional)
try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


def normalize_url(url: str) -> str:
    """Accept a base URL or a full URL; default the path to /api/health."""
    url = url.strip().rstrip("/")
    parsed = urlparse(url)
    if not parsed.scheme:
        parsed = urlparse("https://" + url)
    if parsed.path in ("", "/"):
        parsed = parsed._replace(path="/api/health")
    return urlunparse(parsed)


def ping(url: str, timeout: float) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "epice-keep-alive"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            print(f"[{ts}] {resp.status} {resp.reason} <- {url}", flush=True)
    except urllib.error.HTTPError as e:
        # A response (even 4xx/5xx) still wakes the service
        print(f"[{ts}] HTTP {e.code} <- {url}", flush=True)
    except Exception as e:
        print(f"[{ts}] FAILED ({e.__class__.__name__}: {e}) <- {url}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ping a Render service to keep it awake.")
    parser.add_argument(
        "--url",
        default=os.getenv("RENDER_PING_URL"),
        help="Service URL to ping (default: RENDER_PING_URL env var).",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=600,
        help="Seconds between pings (default: 600 = 10 minutes).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Per-request timeout in seconds (default: 30).",
    )
    args = parser.parse_args()

    if not args.url:
        parser.error(
            "No URL provided. Pass --url https://your-app.onrender.com "
            "or set RENDER_PING_URL in your environment/.env."
        )

    url = normalize_url(args.url)
    print(
        f"Keeping {url} awake: pinging every {args.interval}s. Press Ctrl+C to stop.",
        flush=True,
    )

    try:
        while True:
            ping(url, args.timeout)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nStopped.", flush=True)
        sys.exit(0)


if __name__ == "__main__":
    main()
