[English](README.md) | **中文**

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

### 3. 配置 xiaohongshu-mcp

下载 MCP Server、配置 Claude Code、登录小红书账号，请参考 [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) 项目说明。

## 使用方法

在 Claude Code 中使用 `/xhs-creator` skill：

```
/xhs-creator "话题关键词"    # 完整流程：研究 → 分析 → 撰写 → 审核 → 发布
/xhs-creator research "关键词"  # 仅竞品研究和分析
/xhs-creator write            # 跳过研究，直接撰写
```

## 项目结构

```
xhs-autopilot/
├── .claude/skills/
│   └── xhs-creator/
│       └── SKILL.md              # Claude Code Skill 定义（五阶段工作流）
├── scripts/
│   ├── generate_cover.py         # Pillow 封面生成（基础版）
│   └── screenshot_cover.py       # Playwright HTML→PNG 截图
├── workspace/                    # 运行产物（封面图 + 研究数据，按时间戳子文件夹隔离，git 忽略）
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

## 路线图

- [ ] **Remotion Skill** — 基于 [Remotion](https://remotion.dev/) 的程序化视频生成
- [ ] **自动化配音** — AI 语音合成，为视频内容自动生成旁白
- [ ] **AIGC 生图生视频** — 接入 AI 生成工具，自动产出图片和视频素材
- [ ] **自动化剪辑** — 智能视频剪辑与组装流水线

## 致谢

本项目依赖 [xpzouying/xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) 提供的 MCP Server 实现与小红书平台的交互。感谢作者的开源贡献。

## 许可证

[MIT License](LICENSE)

## 免责声明

本项目仅供学习和研究用途。使用者应遵守小红书平台的服务条款和社区规范。作者不对因使用本工具产生的任何后果承担责任。请合理使用，尊重平台规则和其他用户权益。
