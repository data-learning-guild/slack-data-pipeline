#gcloud functions deploy subscribe_test --env-vars-file=.env.yaml  --trigger-topic=ingested-slackdata-to-gcs --runtime=python37 --allow-unauthenticated --project=salck-visualization --region=asia-northeast1
gcloud functions deploy load_to_warehouse --env-vars-file=.env.yaml  --trigger-topic=ingested-slackdata-to-gcs --runtime=python37 --allow-unauthenticated --project=salck-visualization --region=asia-northeast1