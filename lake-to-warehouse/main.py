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
PROJECT_ID = os.getenv('PROJECT_ID', default='salck-visualization')
GCS_BUCKET = os.getenv('GCS_BUCKET')
BQ_LAKE_DATASET = os.getenv('BQ_LAKE_DATASET')
BQ_WAREHOUSE_DATASET = os.getenv('BQ_WAREHOUSE_DATASET')

class DwhTbls(IntEnum):
    TBL_0 = 0
    TBL_1 = 1
    TBL_2 = 2
DWH_TABLE_NAMES = [
    "TBL_0",
    "TBL_1",
    "TBL_2"
]
DWH_SCHEMAS = [
    [("col_name", "type"), ("col_name", "type"), ("col_name", "type")],
    [("col_name", "type"), ("col_name", "type"), ("col_name", "type")],
    [("col_name", "type"), ("col_name", "type"), ("col_name", "type")]
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


def create_dwh_tables():
    """Create datawarehouse tables if not exist.
    """
    client = bigquery.Client(project=PROJECT_ID)
    dataset_ref = bigquery.DatasetReference(PROJECT_ID, BQ_WAREHOUSE_DATASET)
    
    for tbl_idx in DwhTbls:
        cur_tbl_name = DWH_TABLE_NAMES[tbl_idx]
        cur_tbl_schema = DWH_SCHEMAS[tbl_idx]
        table_ref = dataset_ref.table(cur_tbl_name)
        schema = [bigquery.SchemaField(x[0], x[1]) for x in cur_tbl_schema]
        table = bigquery.Table(table_ref, schema=schema)
        table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="target_date",  # name of column to use for partitioning
            expiration_ms=7776000000,
        )  # 90 days


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
    
    # Create datawarehouse tables if not exist.
    create_dwh_tables()
    
    # Transform datalake to datawarehouse on BQ Engine
    """
    datalake to datawarehouse with SQL on BQ
    """
    bq_client = bigquery.Client(project=PROJECT_ID)
    with open('./sample_query.sql', 'r', encoding='utf-8') as f:
        query_str = f.read()
    query_job = bq_client.query(query_str)  # Make an API request.
    print('The query data.')
    print(f"query_job type is ... {type(query_job)}")
    for row in query_job:
        print(row)
