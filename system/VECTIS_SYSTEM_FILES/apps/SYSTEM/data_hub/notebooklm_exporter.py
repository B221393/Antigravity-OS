#!/usr/bin/env python3
"""
NotebookLM Exporter
===================
NotebookLMの会話履歴・ノート・アーティファクトをエクスポートするスクリプト。

使い方:
  1. 初回認証:  python notebooklm_exporter.py login
  2. ノートブック一覧:  python notebooklm_exporter.py list
  3. 会話エクスポート:  python notebooklm_exporter.py export <notebook_id>
  4. 全ノートブック一括: python notebooklm_exporter.py export-all
"""

import asyncio
import json
import sys
import os
import io
from datetime import datetime
from pathlib import Path

# Windows cp932 対策: 標準出力をUTF-8に
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# エクスポート先ディレクトリ
EXPORT_DIR = Path(__file__).parent / "notebooklm_exports"


def ensure_export_dir():
    """エクスポートディレクトリを作成"""
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    return EXPORT_DIR


async def do_login():
    """ブラウザを開いてGoogle認証を行う"""
    print("=" * 60)
    print("  NotebookLM 認証")
    print("=" * 60)
    print()
    print("ブラウザが開きます。Googleアカウントでログインしてください。")
    print("ログイン後、自動的にトークンが保存されます。")
    print()

    # CLIコマンドで認証を実行
    os.system("notebooklm login")
    print()
    print("✅ 認証完了！")


async def list_notebooks():
    """全ノートブックを一覧表示"""
    from notebooklm import NotebookLMClient

    print("=" * 60)
    print("  NotebookLM ノートブック一覧")
    print("=" * 60)
    print()

    async with await NotebookLMClient.from_storage() as client:
        notebooks = await client.notebooks.list()

        if not notebooks:
            print("⚠️  ノートブックが見つかりません。")
            return

        print(f"📚 {len(notebooks)} 件のノートブック:\n")
        for i, nb in enumerate(notebooks, 1):
            title = getattr(nb, 'title', getattr(nb, 'name', 'Untitled'))
            nb_id = getattr(nb, 'id', 'N/A')
            print(f"  [{i}] {title}")
            print(f"      ID: {nb_id}")
            print()

        return notebooks


async def export_notebook(notebook_id: str):
    """特定のノートブックの全データをエクスポート"""
    from notebooklm import NotebookLMClient

    export_dir = ensure_export_dir()

    async with await NotebookLMClient.from_storage() as client:
        # ノートブック情報を取得
        notebooks = await client.notebooks.list()
        target_nb = None
        for nb in notebooks:
            if getattr(nb, 'id', '') == notebook_id:
                target_nb = nb
                break

        if not target_nb:
            print(f"❌ ノートブック ID '{notebook_id}' が見つかりません。")
            return

        title = getattr(target_nb, 'title', getattr(target_nb, 'name', 'Untitled'))
        safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in title)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nb_export_dir = export_dir / f"{safe_title}_{timestamp}"
        nb_export_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n📕 ノートブック: {title}")
        print(f"📂 エクスポート先: {nb_export_dir}")
        print("-" * 50)

        # --- 会話履歴のエクスポート ---
        print("\n💬 会話履歴を取得中...")
        try:
            chat_history = await client.chat.history(notebook_id)
            if chat_history:
                # Markdownで保存
                md_content = f"# {title} - 会話履歴\n\n"
                md_content += f"エクスポート日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                md_content += "---\n\n"

                for entry in chat_history:
                    question = getattr(entry, 'question', getattr(entry, 'query', ''))
                    answer = getattr(entry, 'answer', getattr(entry, 'response', ''))
                    md_content += f"## Q: {question}\n\n"
                    md_content += f"{answer}\n\n"
                    md_content += "---\n\n"

                chat_md_path = nb_export_dir / "chat_history.md"
                chat_md_path.write_text(md_content, encoding="utf-8")
                print(f"  ✅ 会話履歴 → {chat_md_path.name} ({len(chat_history)} 件)")

                # JSONでも保存
                chat_json_path = nb_export_dir / "chat_history.json"
                chat_data = []
                for entry in chat_history:
                    chat_data.append({
                        "question": getattr(entry, 'question', getattr(entry, 'query', '')),
                        "answer": getattr(entry, 'answer', getattr(entry, 'response', '')),
                    })
                chat_json_path.write_text(
                    json.dumps(chat_data, ensure_ascii=False, indent=2),
                    encoding="utf-8"
                )
                print(f"  ✅ 会話履歴(JSON) → {chat_json_path.name}")
            else:
                print("  ⚠️ 会話履歴なし（ページリロード済みの可能性）")
        except Exception as e:
            print(f"  ⚠️ 会話履歴の取得に失敗: {e}")

        # --- ソース一覧のエクスポート ---
        print("\n📄 ソース情報を取得中...")
        try:
            sources = await client.sources.list(notebook_id)
            if sources:
                sources_md = f"# {title} - ソース一覧\n\n"
                sources_data = []
                for src in sources:
                    src_title = getattr(src, 'title', getattr(src, 'name', 'Unknown'))
                    src_type = getattr(src, 'type', 'Unknown')
                    sources_md += f"- **{src_title}** ({src_type})\n"
                    sources_data.append({
                        "title": src_title,
                        "type": str(src_type),
                        "id": getattr(src, 'id', ''),
                    })

                (nb_export_dir / "sources.md").write_text(sources_md, encoding="utf-8")
                (nb_export_dir / "sources.json").write_text(
                    json.dumps(sources_data, ensure_ascii=False, indent=2),
                    encoding="utf-8"
                )
                print(f"  ✅ ソース一覧 → sources.md ({len(sources)} 件)")
            else:
                print("  ⚠️ ソースなし")
        except Exception as e:
            print(f"  ⚠️ ソース情報の取得に失敗: {e}")

        # --- ノートのエクスポート ---
        print("\n📝 ノートを取得中...")
        try:
            notes = await client.notes.list(notebook_id)
            if notes:
                notes_md = f"# {title} - ノート\n\n"
                for note in notes:
                    note_title = getattr(note, 'title', getattr(note, 'name', 'Untitled Note'))
                    note_content = getattr(note, 'content', getattr(note, 'text', ''))
                    notes_md += f"## {note_title}\n\n{note_content}\n\n---\n\n"

                (nb_export_dir / "notes.md").write_text(notes_md, encoding="utf-8")
                print(f"  ✅ ノート → notes.md ({len(notes)} 件)")
            else:
                print("  ⚠️ ノートなし")
        except Exception as e:
            print(f"  ⚠️ ノートの取得に失敗: {e}")

        print(f"\n{'=' * 50}")
        print(f"✅ エクスポート完了: {nb_export_dir}")
        print(f"{'=' * 50}")
        return nb_export_dir


async def export_all():
    """全ノートブックを一括エクスポート"""
    from notebooklm import NotebookLMClient

    print("=" * 60)
    print("  NotebookLM 全ノートブック一括エクスポート")
    print("=" * 60)

    async with await NotebookLMClient.from_storage() as client:
        notebooks = await client.notebooks.list()

        if not notebooks:
            print("⚠️  ノートブックが見つかりません。")
            return

        print(f"\n📚 {len(notebooks)} 件のノートブックをエクスポートします...\n")

        results = []
        for nb in notebooks:
            nb_id = getattr(nb, 'id', '')
            title = getattr(nb, 'title', getattr(nb, 'name', 'Untitled'))
            try:
                export_path = await export_notebook(nb_id)
                results.append({"title": title, "status": "success", "path": str(export_path)})
            except Exception as e:
                print(f"  ❌ '{title}' のエクスポートに失敗: {e}")
                results.append({"title": title, "status": "error", "error": str(e)})

        # サマリー出力
        print(f"\n{'=' * 60}")
        print("  エクスポート結果サマリー")
        print(f"{'=' * 60}")
        success = sum(1 for r in results if r["status"] == "success")
        failed = sum(1 for r in results if r["status"] == "error")
        print(f"  ✅ 成功: {success}")
        print(f"  ❌ 失敗: {failed}")
        print(f"  📂 出力先: {EXPORT_DIR}")


def print_usage():
    """使い方を表示"""
    print("""
╔══════════════════════════════════════════════════╗
║         NotebookLM Exporter  v1.0               ║
╠══════════════════════════════════════════════════╣
║                                                  ║
║  使い方:                                         ║
║                                                  ║
║  python notebooklm_exporter.py login             ║
║    → Google認証（初回のみ）                       ║
║                                                  ║
║  python notebooklm_exporter.py list              ║
║    → ノートブック一覧を表示                       ║
║                                                  ║
║  python notebooklm_exporter.py export <ID>       ║
║    → 特定ノートブックの会話をエクスポート          ║
║                                                  ║
║  python notebooklm_exporter.py export-all        ║
║    → 全ノートブックを一括エクスポート              ║
║                                                  ║
╚══════════════════════════════════════════════════╝
""")


def main():
    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1].lower()

    if command == "login":
        asyncio.run(do_login())
    elif command == "list":
        asyncio.run(list_notebooks())
    elif command == "export":
        if len(sys.argv) < 3:
            print("❌ ノートブックIDを指定してください。")
            print("   まず 'list' コマンドでIDを確認してください。")
            return
        asyncio.run(export_notebook(sys.argv[2]))
    elif command == "export-all":
        asyncio.run(export_all())
    else:
        print(f"❌ 不明なコマンド: {command}")
        print_usage()


if __name__ == "__main__":
    main()
