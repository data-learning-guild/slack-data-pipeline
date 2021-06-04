import base64
import json
import os

from google.cloud import bigquery

FN_CONVS_HISTORY = "conversations_history.json"
FN_CONVS_LIST = "conversations_list.json"
FN_USERS_LIST = "users_list.json"
LOADING_FILE_NAMES = [
    FN_CONVS_HISTORY,
    FN_CONVS_LIST,
    FN_USERS_LIST
]
PROJECT_ID = os.getenv('PROJECT_ID', default='salck-visualization')
GCS_BUCKET = os.getenv('GCS_BUCKET')
BQ_LAKE_DATASET = os.getenv('BQ_LAKE_DATASET')
BQ_WAREHOUSE_DATASET = os.getenv('BQ_WAREHOUSE_DATASET')
KEY_TARGET_DATE = 'target_date'


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
    
    # Transform datalake to datawarehouse on BQ Engine
    """
    datalake to datawarehouse with SQL on BQ
    SQLファイルは別ファイルにしたほうがいいかも、できるならね
    """
