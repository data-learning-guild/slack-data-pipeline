# lake-to-warehouse

## schema of datalake on bq

- conversations_history
- conversations_list
- users_list

### conversations_history

[conversations.history | Slack API Documentation](https://api.slack.com/methods/conversations.history)

```json
[
    {
        "channel": "channel id in STRING",
        "messages": ["the same as conversations.history"]
    }
]
```


### conversations_list

[conversations.list | Slack API Documentation](https://api.slack.com/methods/conversations.list)


### users_list

[users.list | Slack API Documentation](https://api.slack.com/methods/users.list)


## schema of datawarehouse on bq


