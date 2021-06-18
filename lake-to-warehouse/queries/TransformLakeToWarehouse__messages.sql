-- Query URL
-- https://console.cloud.google.com/bigquery?sq=876898807484:bca2281d05a6452c8f389e782811d91d

-- TransformLakeToWarehouse__messages

CREATE TABLE IF NOT EXISTS
    `salck-visualization`.`slack__datawarehouse`.`messages`
    (
        ts FLOAT64 OPTIONS(description="A message timestamp."),
        user_id STRING OPTIONS(description="An user id who posted message."),
        channel_id STRING OPTIONS(description="A channel id where the message posted."),
        client_msg_id STRING OPTIONS(description="A message id what is posted by not bot/app user."),
        text STRING OPTIONS(description="The posted message text."),
        thread_ts FLOAT64 OPTIONS(description="A thread timestamp (NULL if thread does not exist)."),
        is_thread BOOL OPTIONS(description="True if this message belong to a thread."),
        is_thread_parent BOOL OPTIONS(description="True if this message is thread parent.")
    );

INSERT INTO
    `salck-visualization`.`slack__datawarehouse`.`messages`

SELECT
    ts,
    user AS user_id,
    channel AS channel_id,
    client_msg_id,
    text,
    thread_ts,
    CASE
        WHEN thread_ts IS NULL THEN False
        ELSE True
    END AS is_thread,
    CASE
        WHEN thread_ts IS NULL THEN False
        WHEN (thread_ts IS NOT NULL AND thread_ts != ts) THEN False
        WHEN (thread_ts IS NOT NULL AND thread_ts = ts) THEN True
    END AS is_thread_parent
FROM 
    `salck-visualization`.`slack__datalake`.`work_conversations_history`

