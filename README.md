**English** | [中文](README_CN.md)

# xhs-autopilot

> Xiaohongshu content creation autopilot — AI Agent workflow powered by Claude Code Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/Python-3.13%2B-blue.svg)](https://www.python.org/downloads/)

From competitor research to one-click publishing, let an AI Agent handle every step of Xiaohongshu (Little Red Book) content creation.

## Features

- **Competitor Research** — Multi-dimensional search (most liked / most saved / latest) to quickly understand the competitive landscape
- **Pattern Analysis** — Automatically extract viral title patterns, content structure, tag strategies, and comment insights
- **Smart Writing** — Generate original content based on analysis results, matching platform tone and character limits
- **Cover Generation** — Two approaches: Pillow for batch generation / HTML+Playwright for high-quality screenshots
- **One-Click Publish** — Supports immediate and scheduled publishing with auto-filled title, body, tags, and cover image

## Prerequisites

| Dependency | Version | Description |
|------------|---------|-------------|
| [Python](https://www.python.org/) | 3.13+ | Runtime |
| [uv](https://docs.astral.sh/uv/) | latest | Python package manager |
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | latest | AI coding assistant (CLI) |
| [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) | latest | Xiaohongshu MCP Server (separate download) |

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Jinsong-Zhou/xhs-autopilot.git
cd xhs-autopilot
```

### 2. Install dependencies

```bash
uv sync
uv run playwright install chromium  # first time only: browser for cover screenshots
```

### 3. Set up xiaohongshu-mcp

Download the MCP Server, configure Claude Code, and log in to your Xiaohongshu account by following the [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) project instructions.

## Usage

Use the `/xhs-creator` skill in Claude Code:

```
/xhs-creator "topic keyword"          # full workflow: research → analyze → write → review → publish
/xhs-creator research "keyword"       # research and analysis only
/xhs-creator write                    # skip research, write directly
```

## Project Structure

```
xhs-autopilot/
├── .claude/skills/
│   └── xhs-creator/
│       └── SKILL.md              # Claude Code Skill definition (5-phase workflow)
├── scripts/
│   ├── generate_cover.py         # Pillow cover generation (basic)
│   └── screenshot_cover.py       # Playwright HTML→PNG screenshot
├── workspace/                    # Run artifacts (covers + research data, timestamped subfolders, git-ignored)
├── CLAUDE.md                     # Claude Code project guide
├── pyproject.toml                # Project config
└── LICENSE                       # MIT License
```

## Platform Limits

| Item | Limit |
|------|-------|
| Title | Max 20 Chinese characters |
| Body | ~1000 char limit (emoji may count as multiple chars; target 600-900) |
| Cover image | 1242×1660px (3:4), max 5MB |
| Tags | Passed via `tags` parameter as plain strings (no `#` prefix) |

## Roadmap

- [ ] **Remotion Skill** — Programmatic video generation with [Remotion](https://remotion.dev/)
- [ ] **Automated Voiceover** — AI-powered audio narration for video content
- [ ] **AIGC Image & Video** — Integrate AI generation tools for visual assets
- [ ] **Automated Editing** — Intelligent video editing and assembly pipeline

## Acknowledgments

This project relies on [xpzouying/xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) for MCP Server integration with the Xiaohongshu platform. Thanks to the author for the open-source contribution.

## License

[MIT License](LICENSE)

## Disclaimer

This project is for learning and research purposes only. Users should comply with Xiaohongshu's terms of service and community guidelines. The author assumes no responsibility for any consequences arising from the use of this tool. Please use responsibly and respect platform rules and other users' rights.
