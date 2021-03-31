import logging
import os

logging.basicConfig(level=logging.DEBUG)

from slack_bolt import App

# ボットトークンと署名シークレットを使ってアプリを初期化します
app = App(
    # process_before_response must be True when running on FaaS
    process_before_response=True,
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# run app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))