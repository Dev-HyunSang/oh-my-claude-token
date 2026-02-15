# oh-my-claude-token

A simple token usage monitor for Claude Code CLI. Displays your daily token consumption after each response.

## Features

- Automatic token usage display after each Claude Code response (via hooks)
- Color-coded usage indicators (green/yellow/red)
- Detailed statistics with `main.py`
- Tracks usage across multiple models (Opus, Sonnet, Haiku)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/oh-my-claude-token.git
cd oh-my-claude-token
```

2. Add the hook to your Claude Code settings (`~/.claude/settings.json`):
```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 /path/to/oh-my-claude-token/token_display.py"
          }
        ]
      }
    ]
  }
}
```

3. Replace `/path/to/oh-my-claude-token` with your actual installation path.

## Usage

### Automatic Display (Hook)

Once installed, token usage is automatically displayed after each Claude Code response:

```
[Today: 25K | Msgs: 42 | Turns: 5]
```

Colors:
- Green: < 100K tokens
- Yellow: < 300K tokens
- Red: >= 300K tokens

### Detailed Statistics

Run `main.py` for comprehensive usage statistics:

```bash
python3 main.py
```

Output:
```
==================================================
  Claude Code Token Usage - 2026-02-15
==================================================

Today's Usage:
----------------------------------------
  opus-4-5:
    Used: 25.3K / 500K
    Remaining: ~474.7K
    [████░░░░░░░░░░░░░░░░░░░░░░░░░░] 5.1%

==================================================
  Total Usage (All Time)
==================================================

  opus-4-5:
    Input:  85.0K
    Output: 8.2K
    Cache Read:  162.40M
    Cache Write: 8.43M

==================================================
  Session Statistics
==================================================
  Total Sessions: 81
  Total Messages: 10959
  First Session:  2026-01-01

==================================================
  Recent Activity (Last 7 Days)
==================================================
  2026-02-14: 174 msgs, 32 tools, 920 tokens
  2026-02-13: 222 msgs, 67 tools, 1.6K tokens
  ...
```

## How It Works

Claude Code stores usage statistics in `~/.claude/stats-cache.json`. This tool reads that file to display:

- Daily token usage by model
- Message and tool call counts
- Session statistics
- Historical activity

## Requirements

- Python 3.6+
- Claude Code CLI

## Note

The `stats-cache.json` file is updated periodically, not in real-time. Current session usage will be reflected in subsequent sessions.

## License

MIT
