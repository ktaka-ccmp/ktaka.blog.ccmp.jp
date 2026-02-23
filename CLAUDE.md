# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

## Essential Guidelines

**CRITICAL**: Always observe these fundamental principles:
- **Never go beyond the scope of the request**
- **Never shortcut what was requested**
- Must read ~/.claude/CLAUDE.md

## Project Overview

This is a Zola-based blog containing technical articles in Markdown, organized by year. The blog is published at `ktaka.blog.ccmp.jp` via GitHub Pages. Zola (v0.22.1) is used as the static site generator.

## Repository Structure

```
├── config.toml            # Zola site configuration
├── content/               # Articles in Zola format (Markdown + TOML front matter)
│   ├── _index.md          # Root section (sort_by = "date")
│   ├── 2013/              # Articles by year
│   ├── 2023/
│   ├── 2024/
│   ├── 2025/
│   └── 2026/
├── templates/             # Tera templates (base, index, section, page)
├── static/                # Static assets (CSS, CNAME, .nojekyll)
└── .github/workflows/     # GitHub Actions (zola build + deploy)
```

## Content Workflow

1. Create article directory under `content/YYYY/ArticleName/`
2. Write `index.md` with TOML front matter:
   ```
   +++
   title = "Article Title"
   date = YYYY-MM-DD
   path = "YYYY/ArticleName"
   +++
   ```
3. For bilingual articles, add `index.en.md` alongside `index.md`
4. Place images in `image/` subdirectory, reference with relative paths
5. Preview locally: `zola serve`
6. Build: `zola build` (output to `public/`)

## Build Commands

- `zola serve` — Local dev server with live reload (http://127.0.0.1:1111)
- `zola build` — Build static site to `public/`
- `zola check` — Check for broken links and other issues

## Workflow Tools

This project uses Claude Code commands for workflow management.

### Available Commands

| Command | Description |
|---------|-------------|
| `/snapshot` | Create a session snapshot for context transfer between machines |
| `/issue` | Create or update an issue for task/bug tracking |
| `/backlog` | View all open issues |

### Session Snapshots (`.claude/sessions/`)

For transferring work context between machines or sessions:
- **Purpose**: Capture current work state for resumption
- **Filename**: `YYYY-MM-DD-<topic>.md`
- **Content**: Current task, files modified, key decisions, next steps, context

### Issue Tracking (`.claude/issues/`)

For persistent task and bug tracking across sessions:
- **Purpose**: Track tasks that span multiple sessions
- **Filename**: `YYYYMMDD-HHMM-<short-slug>.md`
- **ID Format**: `YYYYMMDD-HHMM`
- **Status**: `open`, `completed`, `wontfix`, `deferred`
- **Priority**: `high`, `medium`, `low`
- **Structure**: `open/`, `completed/`, `deferred/` subdirectories
- **Format & Rules**: See `.claude/issues/README.md` for issue template, workflow, and README update requirements

### When to Use Each

| Scenario | Use |
|----------|-----|
| Switching machines mid-task | `/snapshot` |
| End of day work capture | `/snapshot` |
| Feature request to implement later | `/issue` |
| Bug found but not fixing now | `/issue` |
| Check pending work | `/backlog` |
| Planning next session | `/backlog` then read relevant snapshots |
