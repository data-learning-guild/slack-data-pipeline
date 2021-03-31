import json
import logging
import os

logging.basicConfig(level=logging.DEBUG)

from slack_bolt import App

def download_conversations_list(client, page_limit: int) -> dict:
    """download Slack Web API conversations.list response.
    """
    channels = []
    next_obj_exists = True
    next_cursor = None
    while next_obj_exists is True:
        slack_response = client.conversations_list(
                            cursor = next_cursor,
                            limit = page_limit, 
                            types = 'public_channel,private_channel')
        
        channels.extend(slack_response.get('channels'))

        next_cursor = slack_response.get('response_metadata').get('next_cursor')
        if next_cursor == "":
            next_obj_exists = False
    
    return channels
    

# ボットトークンと署名シークレットを使ってアプリを初期化します
app = App(
    # process_before_response must be True when running on FaaS
    process_before_response=True,
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)
client = app.client

# run app
if __name__ == "__main__":
    conversations_list = download_conversations_list(client, page_limit=100)
    with open('conversations_list.json', 'w', encoding='utf-8') as f:
        json.dump(conversations_list, f, ensure_ascii=False, indent=4)
