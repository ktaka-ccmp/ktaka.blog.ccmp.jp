# Issue: Qiita クロスポスト検討

## Table of Contents

- [Description](#description)
- [Related Issues](#related-issues)
- [Approach](#approach)
- [Related Files](#related-files)
- [Implementation Tasks](#implementation-tasks)
- [Decision Log](#decision-log)
- [Resolution](#resolution)

## ID: 20260328-0300

## Created: 2026-03-28-03-00

## Closed:

## Status: deferred

## Priority: low

## Difficulty: medium

## Description

日本語記事を Qiita にもクロスポストするかの検討。

## Related Issues

- `20260328-0100` Zenn クロスポスト — ECDSA 記事 2 本 (open)
- `20260328-0200` dev.to クロスポスト — ECDSA 英語記事 2 本 (open)

## Approach

未定。以下の課題がある。

## Related Files

なし

## Implementation Tasks

- [ ] 課題の解決策を決める
- [ ] 実装

## Decision Log

<!-- APPEND-ONLY: Do not edit or delete existing entries. Add new entries at the bottom. -->

### 2026-03-28: 調査の結果、課題が多いため deferred

- Context: Zenn + dev.to で JP/EN をカバーしており、Qiita を追加するメリットと課題を検討
- Decision: 保留
- Reason: 以下の課題がある
  1. **canonical_url 非対応** — Qiita の frontmatter に canonical_url がなく、SEO 的に元ブログが正であることを宣言できない。Qiita のドメインパワーが強いため、元ブログより上位に表示される可能性がある
  2. **ディレクトリ衝突** — Qiita CLI のデフォルト出力先 `public/` が Zola の `zola build` 出力先と衝突。`--root` で変更可能だがワークフローが複雑化する
  3. **CLI 追加** — Qiita CLI（Node.js）のインストールが必要

## Resolution
