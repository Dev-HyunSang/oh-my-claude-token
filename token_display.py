#!/usr/bin/env python3
"""
Compact token usage display for Claude Code hooks
Shows current session token usage in a single line
"""

import json
import sys
from datetime import datetime
from pathlib import Path

STATS_FILE = Path.home() / ".claude" / "stats-cache.json"

# Estimated daily token limits (approximate)
DAILY_LIMITS = {
    "claude-opus-4-5-20251101": 500_000,
    "claude-opus-4-6": 500_000,
    "claude-sonnet-4-5-20250929": 1_000_000,
    "claude-haiku-4-5-20251001": 2_000_000,
}

def format_tokens(tokens: int) -> str:
    if tokens >= 1_000_000:
        return f"{tokens / 1_000_000:.1f}M"
    elif tokens >= 1_000:
        return f"{tokens / 1_000:.1f}K"
    return str(tokens)

def get_hook_data():
    """Read hook event data from stdin"""
    try:
        data = sys.stdin.read()
        if data:
            return json.loads(data)
    except (json.JSONDecodeError, IOError):
        pass
    return {}

def get_session_tokens(transcript_path: str) -> dict:
    """Read current session tokens from transcript file"""
    if not transcript_path:
        return {}

    path = Path(transcript_path)
    if not path.exists():
        return {}

    total_input = 0
    total_output = 0
    total_cache_read = 0
    total_cache_create = 0

    try:
        with open(path, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get("type") == "assistant":
                        usage = entry.get("message", {}).get("usage", {})
                        total_input += usage.get("input_tokens", 0)
                        total_output += usage.get("output_tokens", 0)
                        total_cache_read += usage.get("cache_read_input_tokens", 0)
                        total_cache_create += usage.get("cache_creation_input_tokens", 0)
                except json.JSONDecodeError:
                    continue
    except IOError:
        return {}

    return {
        "input": total_input,
        "output": total_output,
        "cache_read": total_cache_read,
        "cache_create": total_cache_create,
        "total": total_input + total_output,
    }

def get_today_usage():
    if not STATS_FILE.exists():
        return None

    try:
        with open(STATS_FILE, "r") as f:
            stats = json.load(f)
    except (json.JSONDecodeError, IOError):
        return None

    today = datetime.now().strftime("%Y-%m-%d")
    daily_tokens = stats.get("dailyModelTokens", [])
    daily_activity = stats.get("dailyActivity", [])

    tokens_today = {}
    for entry in daily_tokens:
        if entry.get("date") == today:
            tokens_today = entry.get("tokensByModel", {})
            break

    msgs_today = 0
    for entry in daily_activity:
        if entry.get("date") == today:
            msgs_today = entry.get("messageCount", 0)
            break

    return {
        "tokens": tokens_today,
        "messages": msgs_today,
    }

def main():
    hook_data = get_hook_data()

    if hook_data.get("stop_hook_active"):
        return

    # Get real-time session tokens from transcript
    transcript_path = hook_data.get("transcript_path", "")
    session = get_session_tokens(transcript_path)

    # Get accumulated daily usage
    usage = get_today_usage()

    parts = []

    # Show real-time session tokens
    if session and session.get("total", 0) > 0:
        parts.append(f"Session: {format_tokens(session['total'])}")
        parts.append(f"In: {format_tokens(session['input'])}")
        parts.append(f"Out: {format_tokens(session['output'])}")

    # Show daily accumulated and remaining tokens
    if usage:
        tokens = usage["tokens"]
        total = sum(tokens.values()) if tokens else 0
        if total > 0:
            parts.append(f"Today: {format_tokens(total)}")

        # Calculate remaining tokens based on primary model used
        if tokens:
            # Use the model with most usage as the primary model
            primary_model = max(tokens.keys(), key=lambda m: tokens[m])
            limit = DAILY_LIMITS.get(primary_model, 500_000)
            remaining = max(0, limit - total)
            parts.append(f"Remain: ~{format_tokens(remaining)}")

    if parts:
        output = " | ".join(parts)
        message = f"[{output}]"
    else:
        message = "[No usage data]"

    print(json.dumps({"systemMessage": message}))

if __name__ == "__main__":
    main()
