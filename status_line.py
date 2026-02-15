#!/usr/bin/env python3
"""
Status line display for Claude Code
Shows token usage at the bottom of the input field
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
    """Format token count with K/M suffix"""
    if tokens >= 1_000_000:
        return f"{tokens / 1_000_000:.1f}M"
    elif tokens >= 1_000:
        return f"{tokens / 1_000:.1f}K"
    return str(tokens)

def get_status_data():
    """Read status line data from stdin"""
    try:
        data = sys.stdin.read()
        if data:
            return json.loads(data)
    except (json.JSONDecodeError, IOError):
        pass
    return {}

def get_today_usage():
    """Get today's accumulated token usage from stats file"""
    if not STATS_FILE.exists():
        return None

    try:
        with open(STATS_FILE, "r") as f:
            stats = json.load(f)
    except (json.JSONDecodeError, IOError):
        return None

    today = datetime.now().strftime("%Y-%m-%d")
    daily_tokens = stats.get("dailyModelTokens", [])

    for entry in daily_tokens:
        if entry.get("date") == today:
            return entry.get("tokensByModel", {})
    return {}

def main():
    data = get_status_data()

    parts = []

    # Model name
    model_name = data.get("model", {}).get("display_name", "")
    if model_name:
        parts.append(model_name)

    # Context usage from status data
    context = data.get("context_window", {})
    context_pct = context.get("used_percentage", 0) or 0
    if context_pct > 0:
        parts.append(f"Ctx: {context_pct:.0f}%")

    # Session tokens from status data
    input_tokens = context.get("total_input_tokens", 0) or 0
    output_tokens = context.get("total_output_tokens", 0) or 0
    session_total = input_tokens + output_tokens
    if session_total > 0:
        parts.append(f"Session: {format_tokens(session_total)}")

    # Today's accumulated usage and remaining
    today_tokens = get_today_usage()
    if today_tokens:
        total_today = sum(today_tokens.values())
        if total_today > 0:
            parts.append(f"Today: {format_tokens(total_today)}")

            # Calculate remaining
            primary_model = max(today_tokens.keys(), key=lambda m: today_tokens[m])
            limit = DAILY_LIMITS.get(primary_model, 500_000)
            remaining = max(0, limit - total_today)
            parts.append(f"Remain: ~{format_tokens(remaining)}")

    # Session cost
    cost = data.get("cost", {}).get("total_cost_usd", 0) or 0
    if cost > 0:
        parts.append(f"${cost:.2f}")

    if parts:
        print(" | ".join(parts))
    else:
        print("Claude Code")

if __name__ == "__main__":
    main()
