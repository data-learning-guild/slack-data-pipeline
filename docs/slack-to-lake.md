# Slack to Data Lake

## What data to ingest and save

- 原則として、全てのデータを取得
- ただし、admin系APIで取得したメールアドレスなどの個人情報は、保持しない

## Frequency

- daily
  - users.list
  - conversations.list
  - conversations.history
- monthly
  - admin.analytics.getFile


## How to ingest

Via Slack API methods below. ([document and tester](https://api.slack.com/methods))

### Daily ingest

> **Input: バッチ処理実行時の日付**
**※最初の一回は、2020/01~現在日までを繰り返し実行。二回目以降は、現在日のみ。**

- users.list
  - `limit=100` として、最後のページまで繰り返し処理（`cursor={"response_metadata": "next_cursor"}` によって次ページ取得）
  - user ID（=レスポンス内の `"members": [{"id"}, ...]`） を保持し、次の `users.getPresence` で利用する 
- ~~users.getPresence~~ <font color=blue>バッチ実行時（夜中）のpresenceを取得しても意味がない。この当たりの情報はanalyticsから取得するのが妥当。</font>
  - ~~`users.list` から取得しておいた、user ID リストをAPIのパラメータに設定~~
- conversations.list
  - `limit=20` として、最後のページまで繰り返し処理（`cursor={"response_metadata": "next_cursor"}` によって次ページ取得）
  - channel ID（=レスポンス内の `"channels": [{"id"}, ...]`） を保持し、次の `conversations.history` で利用する 
- conversations.history
  - `conversations.list` から取得しておいた、channel ID リストをAPIのパラメータに設定
  - `latest`: バッチ処理実行時が属する日付の00:00を指定（Unixエポックタイム）
  - `oldest`: バッチ処理実行時が属する日付の前日の00:00を指定（Unixエポックタイム）


### Monthly ingest

> 毎月初日の00:00に実行
> 前月の1日〜末日までを指定して、1月分のデータを取得
> Input: 実行日の日付

- ~~admin.analytics.getFile~~ ※ only Slack Enterprise
  - ~~チャンネルアナリティクス~~
    - `type=public_channel`
    - `date=YYYY-MM-DD` in UTC (from 2020/01)：バッチ処理実行日
  - ~~メンバーアナリティクス~~
    - `type=member`
    - `date=YYYY-MM-DD` in UTC (from 2020/01)：バッチ処理実行日


## How to transform

- ~~admin.analytics.getFile~~
  - メールアドレスは保存対象から除外する
- Others within pagenation
  - `limit` パラメータを明示的に設定し、ページごとに細かく区切って取得する
  - ページごとにtemplateファイルとして一時的に出力しておいて、全ページのロードが終わったら、統合して、ファイル出力する


## How to handle errors

- System Error
  - トリガーのエラー：Cloud Scheduler に任せる
  - 処理中のエラー：Cloud Functions のモニタリング, Errは中断＋アラート、Warnは実行継続
- App Error
  - Error：中断、次回再実行のためのファイル出力
  - Warning：処理継続
- Logging
  - Cloud Functions内でログ出力処理を実行
  - Lakeのターゲット日付のフォルダの中に保存


## How to save

- Cloud Storage に保存
- オブジェクトのライフサイクルは、初めの365日がNearline, その後Archiveとする。


## Structure of directories

- `bucket_root`
  - `daily-ingest_target-date_YYYY-MM-DD/`
    - `conversations_list.json`
    - `conversations_history.json`
    - `users_list.json`
    - ~~`users_presence.json`~~
    - `ingest_log_at_YYYY-MM-DD.txt`（target-dateと必ずしも一致しない）
  - `monthly-ingest_target-date_YYYY-MM-DD/`
    - `analytics_channel.json`
    - `analytics_member.json`
    - `ingest_log_at_YYYY-MM-DD.txt`（target-dateと必ずしも一致しない）
