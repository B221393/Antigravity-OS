---
description: 24時間稼働のオート・パイロット（GitHub/Slack統合）
---

// turbo-all
1. 現在の未完了タスクを確認する
   `grep_search --SearchPath "c:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES\CAREER\SCHEDULE.md" --Query "📋"`
2. タスクを一つ選択し、自動的に実装または更新を開始する
3. 実装完了後、GitHubへ自動プッシュする
   `git add . ; git commit -m "Auto-Pilot: Task completed" ; git push origin main`
4. 完了したことをSlackへ報告する
   - Rube MCPの `SLACK_SEND_MESSAGE` を用いて報告
5. `STRATEGIC_INTEL_LOG.md` に進捗を記録する
