import base64
import json
import os

from enum import IntEnum

from google.cloud import bigquery

FN_CONVS_HISTORY = "conversations_history.json"
FN_CONVS_LIST = "conversations_list.json"
FN_USERS_LIST = "users_list.json"
LOADING_FILE_NAMES = [
    FN_CONVS_HISTORY,
    FN_CONVS_LIST,
    FN_USERS_LIST
]
MASTER_FILE_NAMES = [
    FN_CONVS_LIST,
    FN_USERS_LIST
]
COL_TARGET_DATE = "target_date"
PROJECT_ID = os.getenv('PROJECT_ID', default='salck-visualization')
GCS_BUCKET = os.getenv('GCS_BUCKET')
BQ_LAKE_DATASET = os.getenv('BQ_LAKE_DATASET')
BQ_WAREHOUSE_DATASET = os.getenv('BQ_WAREHOUSE_DATASET')
QUERY_DIR = "./queries"
FN_QUERY_CHANNELS = "TransformLakeToWarehouse__channels.sql"
FN_QUERY_USERS = "TransformLakeToWarehouse__users.sql"
FN_QUERY_MESSAGES = "TransformLakeToWarehouse__messages.sql"
FN_QUERY_REACTIONS = "TransformLakeToWarehouse__reactions.sql"
QUERY_FILE_NAMES = [
    FN_QUERY_CHANNELS,
    FN_QUERY_USERS,
    FN_QUERY_MESSAGES,
    FN_QUERY_REACTIONS
]


def subscribe_test(event, context):
    # Print out the data from Pub/Sub, to prove that it worked
    print(base64.b64decode(event['data']))


def load_gcs_json_to_bq_tbl(blob_dir: str=None):
    """Load JSON in GCS to Table in BQ
    """
    client = bigquery.Client()
    
    # load by tables
    for fn in LOADING_FILE_NAMES:
        table_name = 'work_' + fn[:-5]
        table_id = f"{PROJECT_ID}.{BQ_LAKE_DATASET}.{table_name}"
        
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            autodetect=True, write_disposition="WRITE_TRUNCATE"
        )
        uri = f"gs://{GCS_BUCKET}/{blob_dir}/{fn}"
        
        load_job = client.load_table_from_uri(
            uri,
            table_id,
            location="US",  # Must match the destination dataset location.
            job_config=job_config,
        )  # Make an API request.
        
        load_job.result()  # Waits for the job to complete.
        
        # logging
        destination_table = client.get_table(table_id)
        print(f"from {uri}")
        print(f"to {table_id}")
        print(f"Loaded {destination_table.num_rows} rows.")


def add_target_date_column_to_lake_tbl(target_date: str=None):
    """Add target_date column to datalake work table in BQ
        ref: https://cloud.google.com/bigquery/docs/writing-results
    """
    bq_client = bigquery.Client()
    # add column by tables
    for fn in MASTER_FILE_NAMES:
        table_name = 'work_' + fn[:-5]
        table_id = f"{PROJECT_ID}.{BQ_LAKE_DATASET}.{table_name}"
        
        job_config = bigquery.QueryJobConfig(
            destination=table_id,
            write_disposition="WRITE_TRUNCATE"
        )
        
        sql = f"""
            SELECT *, "{target_date}" AS {COL_TARGET_DATE}
            FROM `{table_id}`
        """
        
        query_job = bq_client.query(sql, job_config=job_config)  # Make an API request.
        query_job.result()  # Wait for the job to complete.
        
        # logging
        destination_table = bq_client.get_table(table_id)
        field_names = [x.name for x in destination_table.schema]
        if COL_TARGET_DATE in field_names:
            print(f"Successfully added {COL_TARGET_DATE} column. (tbl: {table_id})")
        else:
            print(f"Failed to add {COL_TARGET_DATE} column. (tbl: {table_id})")


def load_to_warehouse(event, context):
    """Background Cloud Function to be triggered by Pub/Sub.
    Args:
        event (dict):  The dictionary with data specific to this type of
                        event. The `@type` field maps to
                        `type.googleapis.com/google.pubsub.v1.PubsubMessage`.
                        The `data` field maps to the PubsubMessage data
                        in a base64-encoded string. The `attributes` field maps
                        to the PubsubMessage attributes if any is present.
        context (google.cloud.functions.Context): Metadata of triggering event
                        including `event_id` which maps to the PubsubMessage
                        messageId, `timestamp` which maps to the PubsubMessage
                        publishTime, `event_type` which maps to
                        `google.pubsub.topic.publish`, and `resource` which is
                        a dictionary that describes the service API endpoint
                        pubsub.googleapis.com, the triggering topic's name, and
                        the triggering event type
                        `type.googleapis.com/google.pubsub.v1.PubsubMessage`.
    Returns:
        None. The output is written to Cloud Logging.
    """
    # parse published message
    data_bytes = base64.b64decode(event['data'])
    data = json.loads(data_bytes.decode('utf-8'))
    print(f"Published message by previous workflow : \n{data['data']['message']}")
    # get blob dir from event(published msg)
    blob_dir = data['data']['blob-dir-path']
    
    # Load objects(in GCS) to BQ work tables for datalake
    load_gcs_json_to_bq_tbl(blob_dir)
    
    # Add target_date column to BQ work talbes for datalake
    target_date_str = blob_dir[-10:]
    add_target_date_column_to_lake_tbl(target_date_str)
    
    # Transform datalake to datawarehouse on BQ Engine
    """
    datalake to datawarehouse with SQL on BQ
    """
    bq_client = bigquery.Client(project=PROJECT_ID)
    
    
    
    query_from_file(".sql")
    
    with open('./sample_query.sql', 'r', encoding='utf-8') as f:
        query_str = f.read()
    query_job = bq_client.query(query_str)  # Make an API request.
    print('The query data.')
    print(f"query_job type is ... {type(query_job)}")
    for row in query_job:
        print(row)
