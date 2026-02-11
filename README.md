# xhs-autopilot

> 小红书内容创作自动驾驶 — 基于 Claude Code Skill 的 AI Agent 全流程自动化

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/Python-3.13%2B-blue.svg)](https://www.python.org/downloads/)

从竞品调研到一键发布，让 AI Agent 帮你完成小红书内容创作的每一步。

## 功能特性

- **竞品研究** — 多维度搜索（最多点赞 / 最多收藏 / 最新），快速掌握竞争格局
- **模式分析** — 自动提取爆款标题模式、内容结构、标签策略和评论区洞察
- **智能撰写** — 基于分析结果生成原创内容，符合平台调性和字数限制
- **封面生成** — 两套方案：Pillow 批量生成 / HTML+Playwright 高质量截图
- **一键发布** — 支持立即发布和定时发布，自动填充标题、正文、标签和封面

## 前置条件

| 依赖 | 版本 | 说明 |
|------|------|------|
| [Python](https://www.python.org/) | 3.13+ | 运行环境 |
| [uv](https://docs.astral.sh/uv/) | latest | Python 包管理器 |
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | latest | AI 编程助手（CLI） |
| [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) | latest | 小红书 MCP Server（需单独下载） |

## 安装

### 1. 克隆仓库

```bash
git clone https://github.com/Jinsong-Zhou/xhs-autopilot.git
cd xhs-autopilot
```

### 2. 安装依赖

```bash
uv sync
uv run playwright install chromium  # 首次安装：用于封面截图
```

### 3. 下载 MCP Server

前往 [xiaohongshu-mcp Releases](https://github.com/xpzouying/xiaohongshu-mcp/releases) 下载对应平台的二进制文件，放置到项目根目录：

```
xiaohongshu-mcp-darwin-arm64    # macOS Apple Silicon
xiaohongshu-mcp-darwin-amd64    # macOS Intel
xiaohongshu-mcp-linux-amd64     # Linux
```

### 4. 配置 Claude Code MCP

在 Claude Code 的 MCP 配置中添加 xiaohongshu-mcp server。参考上游项目的 [配置说明](https://github.com/xpzouying/xiaohongshu-mcp#readme)。

### 5. 登录小红书

在 Claude Code 中调用 `check_login_status` 检查登录状态，如未登录则通过 `get_login_qrcode` 扫码登录。

## 使用方法

### 完整创作流程（推荐）

在 Claude Code 中使用 `/xhs-creator` skill：

```
/xhs-creator "话题关键词"    # 完整流程：研究 → 分析 → 撰写 → 审核 → 发布
/xhs-creator research "关键词"  # 仅竞品研究和分析
/xhs-creator write            # 跳过研究，直接撰写
```

### 单独生成封面

```bash
# Pillow 方案（快速批量）
uv run python scripts/generate_cover.py --title "标题" --template gradient --color warm

# HTML+Playwright 方案（高质量，推荐）
uv run python scripts/screenshot_cover.py --html scripts/cover_template.html --output images/generated/cover.png
```

#### 封面模板与配色

| 模板 | 适用场景 |
|------|---------|
| `gradient` | 通用型，适合大多数话题 |
| `minimal` | 生活方式、文艺类 |
| `list` | 清单 / 推荐 / 排行类 |
| `bold` | 观点输出、热点评论 |

| 配色 | 适用场景 |
|------|---------|
| `warm` | 美食、家居、穿搭 |
| `cool` | 科技、学习、职场 |
| `green` | 健康、户外、环保 |
| `neutral` | 通用、理性分析 |

## 项目结构

```
xhs-autopilot/
├── .claude/skills/
│   └── xhs-creator/
│       └── SKILL.md              # Claude Code Skill 定义（五阶段工作流）
├── scripts/
│   ├── generate_cover.py         # Pillow 封面生成（基础版）
│   └── screenshot_cover.py       # Playwright HTML→PNG 截图
├── images/generated/             # 生成的封面图（git 忽略）
├── data/research/                # 研究数据存档（git 忽略）
├── CLAUDE.md                     # Claude Code 项目指引
├── pyproject.toml                # 项目配置
└── LICENSE                       # MIT License
```

## 平台限制

| 项目 | 限制 |
|------|------|
| 标题 | 最多 20 个中文字符 |
| 正文 | 约 1000 字上限（emoji 按多字符计算，建议 600-900 字） |
| 封面图 | 1242×1660px（3:4），最大 5MB |
| 标签 | 通过 `tags` 参数传递，不含 `#` 前缀 |

## 致谢

本项目依赖 [xpzouying/xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) 提供的 MCP Server 实现与小红书平台的交互。感谢作者的开源贡献。

## 许可证

[MIT License](LICENSE)

## 免责声明

本项目仅供学习和研究用途。使用者应遵守小红书平台的服务条款和社区规范。作者不对因使用本工具产生的任何后果承担责任。请合理使用，尊重平台规则和其他用户权益。
