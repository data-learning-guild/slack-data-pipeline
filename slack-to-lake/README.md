# slack-to-lake

This directory includes scripts of ETL for ingesting to data lake.

## structure

- `function_ingest/main.py`
  - ingestion main script
- `deploy.sh`
  - deployment of `function_ingest/main/ingest_slack_data`
- `call_functions.sh`
  - call cloud function via Google Cloud SDK
- `gen_call_func_sh.py`
  - generate `call_functions_batch.sh` by from dt to dt
- `call_functions_batch.sh`
  - batch ingestion call via Google Cloud SDK

## execution

### Local Machine

1. Set environs
    - Slack 署名シークレット: `export SLACK_SIGNING_SECRET=<>`
    - Slack ボットトークン: `export SLACK_BOT_TOKEN=<xoxb->`
2. Execute scripts
    - create virutal env : `python -m venv venv` (just once)
    - activate virtual env: `source venv/bin/activate` (just once)
    - install dependencies: `pip install -r requirements.txt` (just once)
    - `python xxx.py [args]`


### Cloud Functions

1. Set environs
    - create `./.env.yaml` and set environs below
      - `SLACK_SIGNING_SECRET=<>`
      - `SLACK_BOT_TOKEN=<xoxb->`
2. Deploy the function
    - exec `./deploy.sh`
3. Call the function
   1. Just once
        - exec `./call_functions.sh`
   2. Custom
        - exec `./gen_call_func_sh.py`
        - then exec `./call_functions_batch.sh`
