"""Server-side IP rate limiting and global quota protection for Streamlit."""

from datetime import date
from typing import Tuple, Dict, Any
import streamlit as st

MAX_QUERIES_PER_IP_PER_DAY = 3
MAX_GLOBAL_DAILY_QUERIES = 200


@st.cache_resource
def get_rate_limiter_store() -> Dict[str, Any]:
    """Server-side cache persisting across sessions, browser tabs, and page refreshes."""
    return {
        "current_date": str(date.today()),
        "global_count": 0,
        "ip_counts": {},
    }


def get_client_identifier() -> str:
    """Extract client IP address or forward header from Streamlit context."""
    try:
        if hasattr(st, "context"):
            # Streamlit 1.38+ native IP context
            ip = getattr(st.context, "ip_address", None)
            if ip:
                return str(ip)
            
            headers = getattr(st.context, "headers", {})
            if headers:
                forwarded = headers.get("x-forwarded-for") or headers.get("X-Forwarded-For")
                if forwarded:
                    return forwarded.split(",")[0].strip()
                remote = headers.get("remote-addr") or headers.get("Remote-Addr")
                if remote:
                    return str(remote)
    except Exception:
        pass
    return "session_guest"


def get_remaining_queries(has_custom_key: bool = False) -> int:
    """Get number of queries remaining for the current visitor today."""
    if has_custom_key:
        return 999

    store = get_rate_limiter_store()
    today_str = str(date.today())

    # Daily rollover
    if store.get("current_date") != today_str:
        store["current_date"] = today_str
        store["global_count"] = 0
        store["ip_counts"] = {}

    # Global circuit breaker tripped
    if store.get("global_count", 0) >= MAX_GLOBAL_DAILY_QUERIES:
        return 0

    client_id = get_client_identifier()
    used = store["ip_counts"].get(client_id, 0)
    return max(0, MAX_QUERIES_PER_IP_PER_DAY - used)


def check_rate_limit(has_custom_key: bool = False) -> Tuple[bool, str]:
    """Verify if the request is permitted by IP and global daily budget."""
    if has_custom_key:
        return True, "Personal API key active — Unlimited queries."

    store = get_rate_limiter_store()
    today_str = str(date.today())

    if store.get("current_date") != today_str:
        store["current_date"] = today_str
        store["global_count"] = 0
        store["ip_counts"] = {}

    if store.get("global_count", 0) >= MAX_GLOBAL_DAILY_QUERIES:
        return False, "Global daily demo quota has been reached to protect the host token budget. Please provide a free Gemini or Groq API key in the sidebar to run queries."

    client_id = get_client_identifier()
    current_ip_count = store["ip_counts"].get(client_id, 0)

    if current_ip_count >= MAX_QUERIES_PER_IP_PER_DAY:
        return False, f"You have reached your daily demo limit ({MAX_QUERIES_PER_IP_PER_DAY}/{MAX_QUERIES_PER_IP_PER_DAY} queries used from this network/device). This prevents token exhaustion so other recruiters can test the app."

    return True, "Allowed"


def record_query_usage(has_custom_key: bool = False):
    """Increment both the per-IP and global daily usage counters."""
    if has_custom_key:
        return

    store = get_rate_limiter_store()
    client_id = get_client_identifier()
    store["global_count"] = store.get("global_count", 0) + 1
    store["ip_counts"][client_id] = store["ip_counts"].get(client_id, 0) + 1
