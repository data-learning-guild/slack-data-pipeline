-- Query URL
-- https://console.cloud.google.com/bigquery?sq=876898807484:1d090d3fc5034cc9943d7a5af9d34971

-- TransformLakeToWarehouse__channels

CREATE TABLE IF NOT EXISTS
    `salck-visualization`.`slack__datawarehouse`.`channels`
    (
        channel_id STRING OPTIONS(description="An channel id"),
        channel_name STRING,
        created_at INT64 OPTIONS(description="When this channel was created."),
        creator STRING OPTIONS(description="The user id who create this channel."),
        is_archived BOOL,
        is_general BOOL,
        topic_val STRING OPTIONS(description="A channel topic value."),
        purpose_val STRING OPTIONS(description="A channel purpose value."),
        num_members INT64 OPTIONS(description="The number of members those belong to this channel."),
        target_date DATE OPTIONS(description="ingested date")
    )
    PARTITION BY target_date;

INSERT INTO
    `salck-visualization`.`slack__datawarehouse`.`channels`

SELECT 
    id AS channel_id,
    name AS channel_name,
    created AS created_at,
    creator,
    is_archived,
    is_general,
    topic.value AS topic_val,
    purpose.value AS purpose_val,
    num_members,
    CAST(target_date AS DATE) AS target_date
FROM 
    `salck-visualization`.`slack__datalake`.`work_conversations_list`
ORDER BY channel_id

