#!/usr/bin/env python3
"""
Claude Code Token Usage Monitor
Shows token usage statistics from Claude Code CLI
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# Claude Code stats file location
STATS_FILE = Path.home() / ".claude" / "stats-cache.json"

# Estimated daily token limits (approximate, not official)
DAILY_LIMITS = {
    "claude-opus-4-5-20251101": 500_000,
    "claude-opus-4-6": 500_000,
    "claude-sonnet-4-5-20250929": 1_000_000,
    "claude-haiku-4-5-20251001": 2_000_000,
}

def format_tokens(tokens: int) -> str:
    """Format token count with K/M suffix"""
    if tokens >= 1_000_000:
        return f"{tokens / 1_000_000:.2f}M"
    elif tokens >= 1_000:
        return f"{tokens / 1_000:.1f}K"
    return str(tokens)

def load_stats() -> dict:
    """Load Claude Code stats from cache file"""
    if not STATS_FILE.exists():
        print(f"Stats file not found: {STATS_FILE}")
        return {}

    with open(STATS_FILE, "r") as f:
        return json.load(f)

def get_today_tokens(stats: dict) -> dict:
    """Get today's token usage by model"""
    today = datetime.now().strftime("%Y-%m-%d")
    daily_tokens = stats.get("dailyModelTokens", [])

    for entry in daily_tokens:
        if entry.get("date") == today:
            return entry.get("tokensByModel", {})
    return {}

def get_total_usage(stats: dict) -> dict:
    """Get total token usage by model"""
    return stats.get("modelUsage", {})

def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{'=' * 50}")
    print(f"  {text}")
    print(f"{'=' * 50}")

def print_usage_bar(used: int, limit: int, width: int = 30) -> str:
    """Create a visual progress bar"""
    percentage = min(used / limit, 1.0) if limit > 0 else 0
    filled = int(width * percentage)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {percentage * 100:.1f}%"

def display_stats():
    """Display token usage statistics"""
    stats = load_stats()
    if not stats:
        return

    today = datetime.now().strftime("%Y-%m-%d")
    today_tokens = get_today_tokens(stats)
    total_usage = get_total_usage(stats)

    # Header
    print_header(f"Claude Code Token Usage - {today}")

    # Today's usage
    print("\n📊 Today's Usage:")
    print("-" * 40)

    if today_tokens:
        for model, tokens in today_tokens.items():
            limit = DAILY_LIMITS.get(model, 500_000)
            remaining = max(0, limit - tokens)
            bar = print_usage_bar(tokens, limit)

            model_short = model.replace("claude-", "").replace("-20250929", "").replace("-20251101", "")
            print(f"  {model_short}:")
            print(f"    Used: {format_tokens(tokens)} / {format_tokens(limit)}")
            print(f"    Remaining: ~{format_tokens(remaining)}")
            print(f"    {bar}")
    else:
        print("  No usage recorded today")

    # Total usage summary
    print_header("Total Usage (All Time)")

    for model, usage in total_usage.items():
        input_tokens = usage.get("inputTokens", 0)
        output_tokens = usage.get("outputTokens", 0)
        cache_read = usage.get("cacheReadInputTokens", 0)
        cache_write = usage.get("cacheCreationInputTokens", 0)

        total = input_tokens + output_tokens
        model_short = model.replace("claude-", "").replace("-20250929", "").replace("-20251101", "")

        print(f"\n  {model_short}:")
        print(f"    Input:  {format_tokens(input_tokens)}")
        print(f"    Output: {format_tokens(output_tokens)}")
        print(f"    Cache Read:  {format_tokens(cache_read)}")
        print(f"    Cache Write: {format_tokens(cache_write)}")

    # Session stats
    print_header("Session Statistics")
    print(f"  Total Sessions: {stats.get('totalSessions', 0)}")
    print(f"  Total Messages: {stats.get('totalMessages', 0)}")

    first_date = stats.get("firstSessionDate", "")
    if first_date:
        first = datetime.fromisoformat(first_date.replace("Z", "+00:00"))
        print(f"  First Session:  {first.strftime('%Y-%m-%d')}")

    # Recent activity (last 7 days)
    print_header("Recent Activity (Last 7 Days)")
    daily_activity = stats.get("dailyActivity", [])
    daily_tokens_list = stats.get("dailyModelTokens", [])

    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    recent = [d for d in daily_activity if d.get("date", "") >= week_ago]

    if recent:
        for day in sorted(recent, key=lambda x: x["date"], reverse=True):
            date = day["date"]
            msgs = day.get("messageCount", 0)
            tools = day.get("toolCallCount", 0)

            # Find tokens for this day
            tokens_for_day = next(
                (t.get("tokensByModel", {}) for t in daily_tokens_list if t.get("date") == date),
                {}
            )
            total_tokens = sum(tokens_for_day.values())

            print(f"  {date}: {msgs} msgs, {tools} tools, {format_tokens(total_tokens)} tokens")
    else:
        print("  No recent activity")

    print()

def main():
    display_stats()

if __name__ == "__main__":
    main()
