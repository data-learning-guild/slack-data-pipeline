# Data Lake to Data Warehouse

## Data Warehouse model

- tables
  - channels
  - users
  - channel_users
  - messages
  - reactions
  - analytics_channel
  - analytics_member

<br>

### channels

チャンネルマスターテーブル

- 主な入力元
  - `conversations_list.json`

|No.|フィールド名|タイプ|モード|備考|対応するkey|
|:--|:--|:--|:--|:--|:--|
|0|id|INT64|Auto Increment|| - |
|1|channel_id|STRING|NOT NULL|PRIMARY|conversations_list.json > id|
|2|channel_name|STRING|NOT NULL|latest channel name|conversations_list.json > name|
|3|created_at|DATETIME_INT|NOT NULL||conversations_list.json > created|
|4|creator|STRING|NOT NULL|creator user's id|conversations_list.json > creator|
|5|is_archived|BOOL|NOT NULL||conversations_list.json > is_archived|
|6|is_general|BOOL|NOT NULL||conversations_list.json > is_general|
|7|topic_val|STRING|NULLABLE|latest topic|conversations_list.json > topic.value|
|8|purpose_val|STRING|NULLABLE|latest purpose|conversations_list.json > purpose.value|
|9|num_members|INTEGER|NULLABLE|num of members belong to the channel|conversations_list.json > num_members|
|10|target_date|DATE|NOT NULL|when master loaded to dwh in UTC<br>`2014-09-27`|partitioning with this column|

<br>

### users

ユーザーマスターテーブル

- 主な入力元
  - `users_list.json`

|No.|フィールド名|タイプ|モード|備考|対応するkey|
|:--|:--|:--|:--|:--|:--|
|0|id|INT64|Auto Increment|| - |
|1|user_id|STRING|NOT NULL|PRIMARY|users_list.json > id|
|2|display_name|STRING|NULLABLE|user display name|users_list.json > profile.display_name|
|3|real_name|STRING|NOT NULL|user real name|users_list.json > profile.real_name|
|4|deleted|BOOL|NOT NULL||users_list.json > deleted|
|5|profile_title|STRING|NULLABLE||users_list.json > profile.title|
|6|status_txt|STRING|NULLABLE||users_list.json > profile.status_text|
|7|status_emoji|STRING|NULLABLE||users_list.json > profile.status_emoji|
|8|image_48_path|STRING|NOT NULL|icon image 48x48|users_list.json > profile.image_48|
|9|is_admin|BOOL|NOT NULL||users_list.json > |
|10|is_owner|BOOL|NOT NULL||users_list.json > |
|11|is_app_user|BOOL|NOT NULL||users_list.json > |
|12|is_bot|BOOL|NOT NULL||users_list.json > |
|13|is_restricted|BOOL|NOT NULL||users_list.json > |
|14|target_date|DATE|NOT NULL|when master loaded to dwh in UTC<br>`2014-09-27`|partitioning with this column|

**※display_name_normalizedにすると半角カタカナになるので、DB的に好ましくないと判断**

<br>


### messages

メッセージログテーブル

- 主な入力元
  - `conversations_history.json`

|No.|フィールド名|タイプ|モード|備考|対応するkey|
|:--|:--|:--|:--|:--|:--|
|0|id|INT64|Auto Increment|PK| - |
|1|ts|FLOAT64|NOT NULL|PK|conversations_history.json > ts **partitioning with this column**|
|2|user_id|STRING|NOT NULL|FK|conversations_history.json > user|
|3|channel_id|STRING|NOT NULL|FK|conversations_history.json の<br>フォルダ名と channelsを利用して計算|
|4|client_msg_id|STRING|NULLABLE||conversations_history.json > |
|5|text|STRING|NULLABLE||conversations_history.json > |
|6|thread_ts|FLOAT64|NULLABLE||conversations_history.json > thread_ts|
|7|is_thread|BOOL|NOT NULL||True if <br> `conversations.history > thread_ts ` is NOT NULL|
|8|is_thread_parent|BOOL|NOT NULL||True if <br> `conversations.history > thread_ts` == `... > ts` |

<br>

### reactions

あるメッセージに対するリアクションのテーブル

- 主な入力元
  - `conversations_history.json`

> msg 1 : reaction N

- どのメッセージに対するリアクションか特定したい場合は、msg_tsをキーにしてmessagesを検索
- だれのリアクションか特定したい場合は、user_idをキーにしてusersを検索

|No.|フィールド名|タイプ|モード|備考|対応するkey|
|:--|:--|:--|:--|:--|:--|
|0|id|INT64|Auto Increment|PK| - |
|1|msg_ts|FLOAT64|NOT NULL|FK:リアクションしたメッセージのタイムスタンプ|conversations_history.json > ts|
|2|msg_user_id|STRING|NOT NULL||conversations_history.json > user|
|3|reaction_name|STRING|NOT NULL||conversations_history.json > reactions[ i ].name|
|4|react_user_id|STRING|NOT NULL|FK:リアクションしたユーザー|conversations_history.json > reactions[ i ].users[ j ]|


<br>

## References

- slack-archive-to-bq [![icon](https://img.shields.io/badge/-View%20on%20GitHub-181717?style=flat&logo=github&logoColor=white)](https://github.com/data-learning-guild/slack-archive-to-bq)
- [BigQueryにおけるスキーマの指定 | Google Cloud](https://cloud.google.com/bigquery/docs/schemas?hl=ja)
- [標準SQLのデータ型](https://cloud.google.com/bigquery/docs/reference/standard-sql/data-types?hl=ja)
- [データ ウェアハウス使用者のための BigQuery | Google Cloud](https://cloud.google.com/solutions/bigquery-data-warehouse?hl=ja)
- [やさしい図解で学ぶ　中間テーブル　多対多　概念編 | Qiita](https://qiita.com/ramuneru/items/db43589551dd0c00fef9)
