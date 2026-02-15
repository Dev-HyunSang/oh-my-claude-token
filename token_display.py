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

def format_tokens(tokens: int) -> str:
    if tokens >= 1_000_000:
        return f"{tokens / 1_000_000:.1f}M"
    elif tokens >= 1_000:
        return f"{tokens / 1_000:.0f}K"
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

    # Get today's tokens
    tokens_today = {}
    for entry in daily_tokens:
        if entry.get("date") == today:
            tokens_today = entry.get("tokensByModel", {})
            break

    # Get today's message count
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
    # Try to get real-time data from hook
    hook_data = get_hook_data()

    # Get accumulated usage from stats file
    usage = get_today_usage()

    # Extract session info from hook if available
    session_tokens = 0
    stop_reason = hook_data.get("stop_reason", "")
    num_turns = hook_data.get("num_turns", 0)

    # Build output
    reset = "\033[0m"
    dim = "\033[90m"
    green = "\033[32m"
    yellow = "\033[33m"
    red = "\033[31m"

    parts = []

    # Show accumulated today usage from stats
    if usage:
        tokens = usage["tokens"]
        msgs = usage["messages"]
        total = sum(tokens.values()) if tokens else 0

        if total > 0 or msgs > 0:
            if total < 100_000:
                color = green
            elif total < 300_000:
                color = yellow
            else:
                color = red

            parts.append(f"{color}Today: {format_tokens(total)}{reset}")
            parts.append(f"Msgs: {msgs}")

    # Show current session turns if available
    if num_turns > 0:
        parts.append(f"Turns: {num_turns}")

    if parts:
        output = " | ".join(parts)
        print(f"{dim}[{reset}{output}{dim}]{reset}")
    else:
        print(f"{dim}[No usage data]{reset}")

if __name__ == "__main__":
    main()
