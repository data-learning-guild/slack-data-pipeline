# slack-to-lake

This directory includes scripts of ETL for ingesting to data lake.

## structure

- `function_ingest/ingest.py`
- `function_ingest/exec_ingestion.py`
- `deploy_function.sh`
- `deploy_cloudstrage.sh`
- `deploy_cloudschedler.sh`
- `automatic_ingest.sh`
- `manual_ingest.sh`

## execute locally

1. Set environs
    - Slack 署名シークレット: `export SLACK_SIGNING_SECRET=<>`
    - Slack ボットトークン: `export SLACK_BOT_TOKEN=<xoxb->`
2. Execute scripts
    - create virutal env : `python -m venv venv` (just once)
    - activate virtual env: `source venv/bin/activate` (just once)
    - install dependencies: `pip install -r requirements.txt` (just once)
    - `python xxx.py [args]`
