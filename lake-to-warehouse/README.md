# lake-to-warehouse

## usage

### environment values

1. Create `.env.yaml`
2. Set environment values
    - `TOPIC_NAME`: topic name that triggers this function
    - `PROJECT_ID`: target project id
    - `GCS_BUCKET`: source bucket name
    - `BQ_LAKE_DATASET`: datalake dataset name (temporary) on BQ
    - `BQ_WAREHOUSE_DATASET`: datawarehouse dataset name on BQ


## schema of datalake on bq

- conversations_history
- conversations_list
- users_list

### conversations_history

[conversations.history | Slack API Documentation](https://api.slack.com/methods/conversations.history)

```json
{"channel": "channel id STR", "message": {"key": "value"}}
{"channel": "channel id STR", "message": {"key": "value"}}
...
{"channel": "channel id STR", "message": {"key": "value"}}
```


### conversations_list

[conversations.list | Slack API Documentation](https://api.slack.com/methods/conversations.list)


### users_list

[users.list | Slack API Documentation](https://api.slack.com/methods/users.list)


## schema of datawarehouse on bq

Table architecture is based on [this schema](https://github.com/data-learning-guild/slack-archive-to-bq).

### channels

The master table for channels.



### users

The master table for users.

### channel_users

The cross reference table for mapping channels to users.

### messages

The transaction table for messages.

### reactions

The transaction table for reactions.
