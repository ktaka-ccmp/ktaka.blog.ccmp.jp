# Session Snapshot: Issue System Initialization & GitHub Pages Investigation

## Current Task

- GitHub Pages でこのリポジトリのコンテンツを `kt.blog.ccmp.jp` として公開する方法の調査
- 簡易イシューシステムの導入とグローバルスキル化

## Files Modified

- `CLAUDE.md` — 新規作成（ブログリポジトリ用のプロジェクトガイダンス）
- `.claude/commands/issue.md` — 新規作成（/issue コマンド定義）
- `.claude/commands/backlog.md` — 新規作成（/backlog コマンド定義）
- `.claude/commands/snapshot.md` — 新規作成（/snapshot コマンド定義）
- `.claude/issues/README.md` — 新規作成（イシューテンプレート・ルール）
- `.claude/issues/{open,completed,deferred,wontfix}/.gitkeep` — ディレクトリ構造
- `.claude/sessions/.gitkeep` — セッションディレクトリ
- `~/.claude/skills/init-issues/SKILL.md` — 新規作成（グローバルスキル）

## Key Decisions

1. **GitHub Pages は可能**: カスタムドメイン `kt.blog.ccmp.jp` で GitHub Actions 経由のデプロイが可能。DNS に CNAME レコード (`ktaka-ccmp.github.io.`) を設定し、GitHub リポジトリ Settings で Custom domain を設定する。
2. **イシューシステム**: oauth2-passkey リポジトリのイシューシステムをそのまま移植。プロジェクト非依存なので変更不要だった。
3. **グローバルスキル化**: `~/.claude/skills/init-issues/SKILL.md` として登録。どのリポジトリでも `/init-issues` で初期化可能に。詳細は後述の「グローバルスキル: /init-issues の再現手順」セクション参照。
4. **~/.claude の Git 管理は見送り**: 機密情報・自動生成ファイルが多いため。必要時に `claude-config` リポジトリ + symlink 方式で対応可能。
5. **GitHub Pages のイシューは completed 済み**: `20260219-1820-github-pages-custom-domain.md`

## Next Steps

- GitHub Pages の具体的な設定作業:
  1. DNS に CNAME レコード追加 (`kt.blog.ccmp.jp` → `ktaka-ccmp.github.io.`)
  2. GitHub Actions ワークフロー (`.github/workflows/`) の作成
  3. リポジトリ Settings → Pages でソースを GitHub Actions に設定、カスタムドメイン設定
  4. コンテンツの変換方法（md → html）の整理

## グローバルスキル: /init-issues の再現手順

### 概要

`~/.claude/skills/init-issues/SKILL.md` を配置すると、任意のリポジトリで `/init-issues` コマンドが使えるようになる。実行すると以下を自動作成する:

- `.claude/commands/issue.md` — `/issue` コマンド
- `.claude/commands/backlog.md` — `/backlog` コマンド
- `.claude/commands/snapshot.md` — `/snapshot` コマンド
- `.claude/issues/README.md` — イシューテンプレート・ルール・自動更新テーブル
- `.claude/issues/{open,completed,deferred,wontfix}/.gitkeep`
- `.claude/sessions/.gitkeep`

### 他の PC での適用手順

#### 方法 A: このリポジトリからコピー

このリポジトリの `.claude/` ディレクトリにあるファイルは、スキルが生成するものと同一内容。以下で他の PC にスキルを配置できる:

```bash
# 1. スキル用ディレクトリ作成
mkdir -p ~/.claude/skills/init-issues/

# 2. スキル定義ファイルをコピー（このリポジトリをクローン済みの場合）
#    ソースは oauth2-passkey リポジトリまたは ktaka.blog.ccmp.jp リポジトリの
#    セッションファイル末尾の SKILL.md 全文を使用
```

#### 方法 B: Claude Code に作らせる

別の PC で Claude Code を起動し、以下のように依頼する:

```
~/.claude/skills/init-issues/SKILL.md を作成してほしい。
任意のリポジトリで /init-issues を実行すると、
.claude/commands/ (issue, backlog, snapshot) と
.claude/issues/ (README, open/completed/deferred/wontfix ディレクトリ) と
.claude/sessions/ を自動作成するグローバルスキルです。
このセッションスナップショットの「SKILL.md 全文」セクションの内容で作成してください。
```

### SKILL.md 全文

他の PC で `~/.claude/skills/init-issues/SKILL.md` として保存すればそのまま動作する。

<details>
<summary>SKILL.md 全文（クリックで展開）</summary>

~~~
---
name: init-issues
description: Initialize the issue tracking system (.claude/issues, commands, sessions) in the current project
---

Initialize the issue tracking system in the current project. Create the following directory structure and files. If any of these already exist, skip them and report what was skipped.

## Directory Structure to Create

```
.claude/commands/
.claude/issues/open/
.claude/issues/completed/
.claude/issues/deferred/
.claude/issues/wontfix/
.claude/sessions/
```

## Files to Create

### 1. `.claude/commands/issue.md`

```markdown
# Issue Management

Create, update, or close an issue for task/bug tracking.

## Directory Structure

\```
.claude/issues/
├── open/           # New issues go here
├── completed/      # Move here when resolved
├── wontfix/        # Move here when closed without implementation
├── deferred/       # Move here when postponed
└── README.md
\```

## Instructions

### Creating a New Issue

Create a markdown file in `.claude/issues/open/` with:
- Filename: `YYYYMMDD-HHMM-<short-slug>.md` (e.g., `20260210-1430-login-history-enhancement.md`)
- ID: `YYYYMMDD-HHMM` matching the filename timestamp
- Created: `YYYY-MM-DD-HH-MM` (same timestamp in readable format)
- Use the template from `.claude/issues/README.md`

### Updating an Issue

When updating an existing issue:
1. Read the current issue file
2. Update the relevant sections (Status, Notes, Resolution)
3. If status changes, move file to appropriate directory:
   - `completed` -> move to `completed/`
   - `wontfix` -> move to `wontfix/`
   - `deferred` -> move to `deferred/`
4. When closing an issue, set the `Closed:` field to `YYYY-MM-DD-HH-MM`

### Status Values

| Status | Directory | Description |
|--------|-----------|-------------|
| `open` | `open/` | New or in-progress |
| `completed` | `completed/` | Resolved and committed |
| `wontfix` | `wontfix/` | Closed without implementation |
| `deferred` | `deferred/` | Postponed for later |

### After Creating/Updating

1. **Update README.md**: Update the "Current Issues" section in `.claude/issues/README.md`
   - The section is between `<!-- AUTO-UPDATED -->` and `<!-- END AUTO-UPDATED -->` markers
   - Regenerate the tables for Open, Completed, and Deferred issues
   - Sort Open issues by priority (high > medium > low), then by ID

2. **Inform the user** of:
   - The file path
   - A brief summary of what was created/changed
   - If moved, the new location
```

### 2. `.claude/commands/backlog.md`

```markdown
# View Backlog

List all open issues in the project.

## Instructions

1. Read all markdown files in `.claude/issues/open/` directory
2. Parse each file to extract:
   - ID (from `## ID: <id>`)
   - Title (from `# Issue: <Title>`)
   - Priority (from `## Priority: <priority>`)
   - Description (first paragraph after `## Description`)

3. Display as a sorted list (by priority: high > medium > low, then by date)

## Output Format

\```
# Open Issues

## High Priority
- `ID` [Title](path)
  Related: path/to/files

## Medium Priority
- `ID` [Title](path)
  Related: path/to/files

## Low Priority
- `ID` [Title](path)
  Related: path/to/files

---
Total: N open issues
\```

If no open issues exist, report:
\```
# Open Issues

No open issues found.
\```

## Optional: Show Other Categories

If user requests, also show counts from other directories:
- `.claude/issues/completed/` - Completed issues
- `.claude/issues/deferred/` - Deferred issues
```

### 3. `.claude/commands/snapshot.md`

```markdown
# Session Snapshot

Create a session snapshot for transferring work context between machines.

## Instructions

Create a markdown file in `.claude/sessions/` with:
- Filename: `YYYY-MM-DD-<topic>.md` (e.g., `2025-01-23-csrf-docs.md`)
- Content should include:
  1. **Current Task**: What was being worked on
  2. **Files Modified**: List of files changed in this session
  3. **Key Decisions**: Important decisions made
  4. **Next Steps**: What to do next
  5. **Context**: Any important background info

After creating the snapshot, inform the user of the file path.
```

### 4. `.claude/issues/README.md`

```markdown
# Issue Tracking

This directory contains issue/task tracking files for the project.

## Current Issues

<!-- AUTO-UPDATED: Do not edit manually. Updated by /issue command. -->

### Open (0)

| ID | Priority | Difficulty | Title |
|----|----------|------------|-------|

### Completed (0)

| ID | Title |
|----|-------|

### Wontfix (0)

| ID | Title |
|----|-------|

### Deferred (0)

| ID | Title |
|----|-------|

<!-- END AUTO-UPDATED -->

## Directory Structure

\```
.claude/issues/
├── open/           # Active issues
├── completed/      # Resolved issues
├── wontfix/        # Closed without implementation
├── deferred/       # Postponed issues
└── README.md       # This file
\```

Issues are organized by status. When status changes, move the file to the appropriate directory.

## File Naming Convention

New issues use the timestamp-based format:

\```text
YYYYMMDD-HHMM-<short-slug>.md
\```

Example: `20260210-1430-login-history-enhancement.md`

## Issue ID Format

New issues use a timestamp-based ID:

\```text
YYYYMMDD-HHMM
\```

- `YYYYMMDD`: Creation date
- `HHMM`: Creation time (24h format)

Example: `20260210-1430`, `20260210-1545`

## Issue Template

\```markdown
# Issue: <Title>

## Table of Contents

- [Description](#description)
- [Related Issues](#related-issues)
- [Approach](#approach)
- [Related Files](#related-files)
- [Implementation Tasks](#implementation-tasks)
- [Decision Log](#decision-log)
- [Resolution](#resolution)

## ID: YYYYMMDD-HHMM

## Created: YYYY-MM-DD-HH-MM

## Closed:

## Status: open | completed | wontfix | deferred

## Priority: high | medium | low

## Difficulty: small | medium | large

## Description

<What needs to be done and why>

## Related Issues

- `YYYYMMDD-HHMM` <Title> (relationship: e.g., depends on, related to, supersedes)

## Approach

<Current plan for implementation>

## Related Files

- `path/to/file`

## Implementation Tasks

- [ ] <Task 1>
- [ ] <Task 2>

## Decision Log

<!-- APPEND-ONLY: Do not edit or delete existing entries. Add new entries at the bottom. -->

### YYYY-MM-DD: <Short summary of decision>

- Context: <What prompted this decision>
- Decision: <What was decided>
- Reason: <Why this was chosen over alternatives>

## Resolution

<What was done to resolve this issue>
\```

## Section Update Rules

| Section | Update Rule |
|---------|------------|
| Created | Written once at creation |
| Closed | Written once when issue is resolved or closed |
| Description | Freely updatable |
| Related Issues | Freely updatable |
| Approach | Freely updatable (always reflects current plan) |
| Related Files | Freely updatable |
| Implementation Tasks | Freely updatable |
| **Decision Log** | **Append-only -- never edit or delete existing entries** |
| Resolution | Written once when issue is resolved |

The **Decision Log** preserves the history of design decisions, approach changes, and
rejected alternatives. When updating other sections (especially Approach), always add
a corresponding Decision Log entry explaining what changed and why.

## Status Values

| Status | Directory | Description |
|--------|-----------|-------------|
| `open` | `open/` | New or in-progress |
| `completed` | `completed/` | Resolved and committed |
| `wontfix` | `wontfix/` | Closed without implementation |
| `deferred` | `deferred/` | Postponed for later |

## Commands

- `/issue` - Create or update an issue
- `/backlog` - View all open issues
- `/snapshot` - Create a session snapshot (different from issues)

## Workflow

1. Create new issue in `open/` directory
2. **Update this README's "Current Issues" table** (increment count, add row)
3. Work on the issue
4. When resolved, update Resolution section and move to `completed/`
5. If postponed, move to `deferred/`

**Important**: Always update the README table when creating, completing, or moving issues.

## Difference from Sessions

- **Sessions** (`.claude/sessions/`): Work context snapshots for transferring between machines
- **Issues** (`.claude/issues/`): Task/bug tracking that persists across sessions
```

### 5. `.gitkeep` files

Create empty `.gitkeep` files in:
- `.claude/issues/open/.gitkeep`
- `.claude/issues/completed/.gitkeep`
- `.claude/issues/deferred/.gitkeep`
- `.claude/issues/wontfix/.gitkeep`
- `.claude/sessions/.gitkeep`

## After Initialization

1. Report all created files and directories
2. Remind the user to add the Workflow Tools section to their `CLAUDE.md` if it exists (do NOT modify CLAUDE.md automatically):

```markdown
## Workflow Tools

### Available Commands

| Command | Description |
|---------|-------------|
| `/snapshot` | Create a session snapshot for context transfer between machines |
| `/issue` | Create or update an issue for task/bug tracking |
| `/backlog` | View all open issues |

### Issue Tracking (`.claude/issues/`)

- **Filename**: `YYYYMMDD-HHMM-<short-slug>.md`
- **Status**: `open`, `completed`, `wontfix`, `deferred`
- **Priority**: `high`, `medium`, `low`
- **Format & Rules**: See `.claude/issues/README.md`
```
~~~

</details>

### 将来的な改善案

- `~/.claude/{CLAUDE.md,commands/,skills/}` だけを管理する `claude-config` リポジトリを作り、symlink で配置する方法も検討済み（今回は見送り）
- スキル自体をプラグイン化して `claude plugins install` で配布することも技術的には可能

## Context

- リポジトリには年ごとのディレクトリ (2013/, 2023/, 2024/, 2025/, 2026/) に Markdown と HTML の技術記事がある
- 現在のワークフロー: Markdown → pandoc で HTML 変換 → Blogger にコピペ
- 目標: GitHub Pages で直接公開に移行
