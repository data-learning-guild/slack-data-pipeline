-- Query URL
-- https://console.cloud.google.com/bigquery?sq=876898807484:a1f832bafc3448c6946d0d38ff65116a

-- TransformLakeToWarehouse__reactions

CREATE TABLE IF NOT EXISTS
    `salck-visualization`.`slack__datawarehouse`.`reactions`
    (
        msg_ts FLOAT64 OPTIONS(description="A message timestamp."),
        msg_user_id STRING OPTIONS(description="An user id who posted message."),
        reaction_name STRING OPTIONS(description="A reaction name."),
        react_user_id STRING OPTIONS(description="An user id who reacted.")
    );

INSERT INTO
    `salck-visualization`.`slack__datawarehouse`.`reactions`

WITH base_reactions AS (
    SELECT
        ts AS msg_ts,
        user AS msg_user_id,
        reaction.users AS react_user_ids,
        reaction.name AS reaction_name
    FROM 
        `salck-visualization`.`slack__datalake`.`work_conversations_history` AS t
    CROSS JOIN 
        UNNEST(t.reactions) AS reaction
)

SELECT
    msg_ts ,
    msg_user_id ,
    reaction_name ,
    react_user_id
FROM base_reactions
CROSS JOIN 
    UNNEST(react_user_ids) AS react_user_id

