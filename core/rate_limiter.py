"""Server-side IP rate limiting and global quota protection for Streamlit."""

import uuid
from datetime import date
from typing import Tuple, Dict, Any
import streamlit as st

MAX_QUERIES_PER_IP_PER_DAY = 3
MAX_QUERIES_PER_USER_PER_DAY = 3
MAX_GLOBAL_DAILY_QUERIES = 200


@st.cache_resource(ttl=86400)
def get_rate_limiter_store(cache_version: str = "v3_isolated_user_sessions") -> Dict[str, Any]:
    """Server-side cache persisting across sessions, browser tabs, and page refreshes."""
    return {
        "current_date": str(date.today()),
        "global_count": 0,
        "user_counts": {},
        "ip_counts": {},
    }


def _is_valid_public_ip(ip_str: str) -> bool:
    """Check if an IP string is a real, non-loopback, non-private public IP address."""
    if not ip_str:
        return False
    ip = ip_str.strip()
    if not ip or ip.lower() in ("127.0.0.1", "localhost", "0.0.0.0", "::1", "unknown", "none"):
        return False
    # Filter private / internal Docker subnets to prevent container sharing
    if ip.startswith((
        "10.", "192.168.", "127.",
        "172.16.", "172.17.", "172.18.", "172.19.", "172.20.",
        "172.21.", "172.22.", "172.23.", "172.24.", "172.25.",
        "172.26.", "172.27.", "172.28.", "172.29.", "172.30.", "172.31."
    )):
        return False
    return True


def get_client_identifier() -> str:
    """Extract a unique per-user client identifier.

    1. Checks for a real public client IP from Cloudflare or proxy headers.
    2. If on local network or behind a private proxy, uses a unique persistent visitor ID.
    CRITICAL: Never returns a static fallback string like 'session_guest' so users never collide.
    """
    try:
        if hasattr(st, "context"):
            headers = getattr(st.context, "headers", {})
            if headers:
                # Cloudflare real visitor IP
                cf_ip = headers.get("cf-connecting-ip")
                if cf_ip and _is_valid_public_ip(str(cf_ip)):
                    return f"ip_{str(cf_ip).strip()}"

                # Standard reverse proxy forwarded headers
                for header_key in ("x-forwarded-for", "x-real-ip", "true-client-ip", "x-client-ip"):
                    val = headers.get(header_key)
                    if val:
                        first_ip = str(val).split(",")[0].strip()
                        if _is_valid_public_ip(first_ip):
                            return f"ip_{first_ip}"

            # Streamlit 1.38+ native IP context attribute
            native_ip = getattr(st.context, "ip_address", None)
            if native_ip and _is_valid_public_ip(str(native_ip)):
                return f"ip_{str(native_ip).strip()}"
    except Exception:
        pass

    # If no public IP could be extracted (local dev, or proxy sanitization):
    # Use an isolated, persistent visitor ID per browser session so users NEVER share limits!
    try:
        if "visitor_id" in st.session_state and st.session_state.visitor_id:
            return st.session_state.visitor_id
    except Exception:
        pass

    # Check URL query param (?vid=...) to preserve quota across F5 page reloads
    try:
        query_params = getattr(st, "query_params", {})
        if "vid" in query_params and query_params["vid"]:
            vid = str(query_params["vid"]).strip()
            visitor_id = f"vis_{vid}"
            try:
                st.session_state.visitor_id = visitor_id
            except Exception:
                pass
            return visitor_id
    except Exception:
        pass

    # Brand new unique visitor
    new_vid = uuid.uuid4().hex[:12]
    assigned_id = f"vis_{new_vid}"
    try:
        st.session_state.visitor_id = assigned_id
        st.query_params["vid"] = new_vid
    except Exception:
        pass

    return assigned_id


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
        store["user_counts"] = {}
        store["ip_counts"] = {}

    # Global circuit breaker tripped
    if store.get("global_count", 0) >= MAX_GLOBAL_DAILY_QUERIES:
        return 0

    client_id = get_client_identifier()
    counts = store.get("user_counts", store.get("ip_counts", {}))
    used = counts.get(client_id, 0)
    return max(0, MAX_QUERIES_PER_IP_PER_DAY - used)


def check_rate_limit(has_custom_key: bool = False) -> Tuple[bool, str]:
    """Verify if the request is permitted by user quota and global daily budget."""
    if has_custom_key:
        return True, "Personal API key active — Unlimited queries."

    store = get_rate_limiter_store()
    today_str = str(date.today())

    if store.get("current_date") != today_str:
        store["current_date"] = today_str
        store["global_count"] = 0
        store["user_counts"] = {}
        store["ip_counts"] = {}

    if store.get("global_count", 0) >= MAX_GLOBAL_DAILY_QUERIES:
        return False, "Global daily demo quota has been reached to protect the host token budget. Please provide a free Gemini or Groq API key in the sidebar to run queries."

    client_id = get_client_identifier()
    counts = store.get("user_counts", store.get("ip_counts", {}))
    current_count = counts.get(client_id, 0)

    if current_count >= MAX_QUERIES_PER_IP_PER_DAY:
        return False, f"You have reached your daily demo limit ({MAX_QUERIES_PER_IP_PER_DAY}/{MAX_QUERIES_PER_IP_PER_DAY} queries used). To prevent quota abuse, live queries are paused for your session today. You can still test demo questions or provide a free API key."

    return True, "Allowed"


def record_query_usage(has_custom_key: bool = False):
    """Increment both the per-user and global daily usage counters."""
    if has_custom_key:
        return

    store = get_rate_limiter_store()
    client_id = get_client_identifier()
    store["global_count"] = store.get("global_count", 0) + 1
    if "user_counts" not in store:
        store["user_counts"] = {}
    if "ip_counts" not in store:
        store["ip_counts"] = {}
    store["user_counts"][client_id] = store["user_counts"].get(client_id, 0) + 1
    store["ip_counts"][client_id] = store["ip_counts"].get(client_id, 0) + 1
