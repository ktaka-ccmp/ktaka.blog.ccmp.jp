# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

## Essential Guidelines

**CRITICAL**: Always observe these fundamental principles:
- **Never go beyond the scope of the request**
- **Never shortcut what was requested**
- Must read ~/.claude/CLAUDE.md

## Project Overview

This is a blog content repository containing technical articles in Markdown and HTML format, organized by year. The blog is published at `kt.blog.ccmp.jp` via GitHub Pages.

## Repository Structure

```
├── 2013/                  # Articles by year
├── 2023/
├── 2024/
├── 2025/
├── 2026/
├── gh-md-toc              # Table of contents generator
├── github-markdown.css    # CSS for GitHub-style markdown
└── Readme.md              # Blog workflow instructions
```

## Content Workflow

1. Write articles in Markdown format
2. Generate TOC: `./gh-md-toc Readme.md`
3. Convert to HTML: `pandoc Readme.md -o Readme.html`
4. Or with CSS: `pandoc -s -c ../../github-markdown.css Readme.md -o Readme.html --metadata title="..."`

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
