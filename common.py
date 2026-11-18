"""Shared helpers: HTTP with rate limit, NCBI key from Keychain, RWTHgpt call, tolerant JSON parsing.
Standard library only."""
import json
import re
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request

UA = "hack-meccog-apoe4/0.1 (literature pipeline; urllib)"
_last = {}


def ncbi_key():
    """NCBI API key from the macOS Keychain. Never printed or logged. None if unavailable."""
    try:
        r = subprocess.run(["security", "find-generic-password", "-s", "NCBI_API_KEY", "-w"],
                           capture_output=True, text=True, timeout=10)
        k = r.stdout.strip()
        return k or None
    except Exception:
        return None


def throttle(host, min_interval):
    now = time.monotonic()
    wait = _last.get(host, 0) + min_interval - now
    if wait > 0:
        time.sleep(wait)
    _last[host] = time.monotonic()


def http_get(url, params=None, min_interval=0.12, retries=3, secret_params=("api_key",)):
    """GET with throttle and retry on 429/5xx. Errors never include the query string (it may hold the key)."""
    q = urllib.parse.urlencode(params or {})
    full = url + ("?" + q if q else "")
    host = urllib.parse.urlparse(url).netloc
    for attempt in range(retries):
        throttle(host, min_interval)
        req = urllib.request.Request(full, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(1.5 * (attempt + 1))
                continue
            raise RuntimeError(f"HTTP {e.code} from {url}") from None
        except urllib.error.URLError as e:
            if attempt < retries - 1:
                time.sleep(1.5 * (attempt + 1))
                continue
            raise RuntimeError(f"network error from {url}: {e.reason}") from None


def extract_json(text):
    """Pull the first JSON value (object or array) out of a model reply, tolerating code fences and prose.
    Raises ValueError if none parses."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.I)
    try:
        return json.loads(text)
    except ValueError:
        pass
    dec = json.JSONDecoder()
    for i, ch in enumerate(text):
        if ch in "[{":
            try:
                val, _ = dec.raw_decode(text[i:])
                return val
            except ValueError:
                continue
    raise ValueError("no JSON found in model reply")


def rwth_ask(instruction, data, model=None, timeout=600):
    """One call to the free RWTHgpt CLI. Instruction goes on argv (short, no private data); the
    abstracts go on stdin. Returns the reply text."""
    cmd = ["rwth-ask"] + (["-m", model] if model else []) + [instruction]
    r = subprocess.run(cmd, input=data, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError("rwth-ask failed: " + (r.stderr or "")[:200])
    return r.stdout


def rwth_json(instruction, data, retries=2):
    last = None
    for _ in range(retries):
        try:
            return extract_json(rwth_ask(instruction, data))
        except ValueError as e:
            last = e
    raise last


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(obj, path):
    import os
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
