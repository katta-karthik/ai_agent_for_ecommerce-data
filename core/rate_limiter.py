"""Server-side IP rate limiting and global quota protection for Streamlit."""

import uuid
from datetime import date
from typing import Tuple, Dict, Any
import streamlit as st

MAX_QUERIES_PER_USER_PER_DAY = 3
MAX_GLOBAL_DAILY_QUERIES = 200


@st.cache_resource(ttl=86400)
def get_rate_limiter_store(cache_version: str = "v4_session_based_quota") -> Dict[str, Any]:
    """Server-side cache persisting across sessions, browser tabs, and page refreshes."""
    return {
        "current_date": str(date.today()),
        "global_count": 0,
        "user_counts": {},
    }


def get_client_identifier() -> str:
    """Extract a unique per-user client identifier.

    ALWAYS uses a per-session unique visitor ID so each browser tab/session
    gets its own independent quota.  IP-based identification is NOT used
    because on Streamlit Cloud (and most cloud deployments) all users share
    the same reverse-proxy IP, which causes one user's exhausted quota to
    block every other user.

    The visitor ID is persisted in:
      1. st.session_state  (survives reruns within the same browser tab)
      2. URL query param ?vid=…  (survives full page refreshes / F5)
    """

    # 1. Already assigned in this session? Reuse it.
    try:
        if "visitor_id" in st.session_state and st.session_state.visitor_id:
            return st.session_state.visitor_id
    except Exception:
        pass

    # 2. Restored from URL query param after a page refresh.
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

    # 3. Brand-new visitor — mint a fresh unique ID.
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

    # Global circuit breaker tripped
    if store.get("global_count", 0) >= MAX_GLOBAL_DAILY_QUERIES:
        return 0

    client_id = get_client_identifier()
    user_counts = store.get("user_counts", {})
    used = user_counts.get(client_id, 0)
    return max(0, MAX_QUERIES_PER_USER_PER_DAY - used)


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

    if store.get("global_count", 0) >= MAX_GLOBAL_DAILY_QUERIES:
        return False, "Global daily demo quota has been reached to protect the host token budget. Please provide a free Gemini or Groq API key in the sidebar to run queries."

    client_id = get_client_identifier()
    user_counts = store.get("user_counts", {})
    current_count = user_counts.get(client_id, 0)

    if current_count >= MAX_QUERIES_PER_USER_PER_DAY:
        return False, f"You have reached your daily demo limit ({MAX_QUERIES_PER_USER_PER_DAY}/{MAX_QUERIES_PER_USER_PER_DAY} queries used). To prevent quota abuse, live queries are paused for your session today. You can still test demo questions or provide a free API key."

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
    store["user_counts"][client_id] = store["user_counts"].get(client_id, 0) + 1
