# Text Router 知識蓄積機能追加パッチ

## 追加する場所

`analyze_and_route` メソッドの中、`self.log_routing(text, best_category)` の直後に以下を追加：

```python
        # 🌟 知識として蓄積（教養とエゴ）
        self.save_as_knowledge(text, best_category, scores)
        self.save_to_ego_memory(text, best_category)
```

## 変更するダイアログメッセージ

433-434行目を以下に変更：

```python
            f"「{best_category}」に振り分けられました。\n\n✅ 知識カードとエゴメモリに保存しました。\n\nこのアプリを起動しますか？"
```

## 手動適用手順

1. `text_router/app.py` を開く
2. 430行目（空行）の後に以下2行を追加：

   ```python
        # 🌟 知識として蓄積（教養とエゴ）
        self.save_as_knowledge(text, best_category, scores)
        self.save_to_ego_memory(text, best_category)
        
   ```

3. 434行目のメッセージを変更
4. 保存

## 確認方法

Text Routerを起動して、テキストを仕分けすると：

- `knowledge_cards/outputs/cards/` に `.kcard` ファイルが生成される
- `memory/data/` に `ego_thought_*.json` ファイルが生成される
