# ChumToto イベント監視Bot

TicketDiveのChumTotoページを毎日自動チェックし、新しいイベントが追加されたらLINEに通知します。

## セットアップ手順

### 1. リポジトリを作成
GitHubで新しいリポジトリを作成し、このファイル一式をプッシュしてください。

```
リポジトリ構成:
├── .github/
│   └── workflows/
│       └── check_events.yml
├── check_events.py
├── events.json        ← 初回実行時に自動生成されます
└── README.md
```

初回は空の `events.json` を作成してコミットしてください：
```bash
echo "[]" > events.json
git add events.json
git commit -m "Initial events.json"
git push
```

---

### 2. LINE Messaging API の設定

1. [LINE Developers](https://developers.line.biz/ja/) にアクセス
2. 「Messaging API」チャンネルを新規作成
3. 以下の値をメモする：
   - **チャンネルアクセストークン**（長期）→ `LINE_CHANNEL_ACCESS_TOKEN`
   - **あなた自身のユーザーID** → `LINE_USER_ID`
     - LINE Developersコンソール → プロフィール画面で確認できます

4. 作成したBotと **友だちになる**（友だちでないとメッセージが届きません）

---

### 3. GitHub Secrets の設定

リポジトリの `Settings` → `Secrets and variables` → `Actions` で以下を追加：

| シークレット名 | 値 |
|---|---|
| `LINE_CHANNEL_ACCESS_TOKEN` | LINEのチャンネルアクセストークン |
| `LINE_USER_ID` | あなたのLINEユーザーID |

---

### 4. 動作確認

`Actions` タブ → `ChumToto イベント監視` → `Run workflow` で手動実行できます。

---

## 実行スケジュール

毎日 **JST 10:00** に自動実行されます。変更したい場合は `check_events.yml` の `cron` を編集してください。

```yaml
- cron: '0 1 * * *'   # UTC 01:00 = JST 10:00
- cron: '0 0 * * *'   # JST 09:00 に変更する場合
```
