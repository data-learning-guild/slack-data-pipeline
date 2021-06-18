-- Query URL
-- https://console.cloud.google.com/bigquery?sq=876898807484:ded679055e794edf9af772ee88f38e47

-- TransformLakeToWarehouse__users

CREATE TABLE IF NOT EXISTS
    `salck-visualization`.`slack__datawarehouse`.`users`
    (
        user_id STRING OPTIONS(description="An user id"),
        display_name STRING,
        real_name STRING,
        deleted BOOL,
        profile_title STRING,
        status_txt STRING,
        status_emoji STRING,
        image_48_path STRING OPTIONS(description="An user's icon image(48x48pix) path."),
        is_admin BOOL,
        is_owner BOOL,
        is_app_user BOOL,
        is_bot BOOL,
        is_restricted BOOL,
        target_date DATE OPTIONS(description="ingested date")
    )
    PARTITION BY target_date;

INSERT INTO
    `salck-visualization`.`slack__datawarehouse`.`users`

SELECT 
    id AS user_id,
    profile.display_name AS display_name,
    profile.real_name AS real_name,
    deleted,
    profile.title AS profile_title,
    profile.status_text AS status_txt,
    profile.status_emoji AS status_emoji,
    profile.image_48 AS image_48_path,
    is_admin,
    is_owner,
    is_app_user,
    is_bot,
    is_restricted,
    CAST(target_date AS DATE) AS target_date
FROM 
    `salck-visualization`.`slack__datalake`.`work_users_list`
ORDER BY user_id
