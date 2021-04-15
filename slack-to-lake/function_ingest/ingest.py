import datetime
import json
import logging
import os
import tempfile
from slack_bolt import App
from typing import List

logfilename = 'ingest_log_{}.log'.format(datetime.datetime.now().isoformat())
logging.basicConfig(
    filename=logfilename,
    format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p',
    encoding='utf-8', level=logging.INFO)


def download_conversations_list(client, page_limit: int) -> List[dict]:
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


def download_users_list(client, page_limit: int) -> List[dict]:
    """download Slack Web API users.list response.
    """
    users = []
    next_obj_exists = True
    next_cursor = None
    while next_obj_exists is True:
        slack_response = client.users_list(
                            cursor = next_cursor,
                            limit = page_limit)
        
        users.extend(slack_response.get('members'))
        next_cursor = slack_response.get('response_metadata').get('next_cursor')
        if next_cursor == "":
            next_obj_exists = False
    
    return users



# ==  BEGIN - Main Cloud Function  ==
def ingest_slack_data():
    # ボットトークンと署名シークレットを使ってアプリを初期化します
    app = App(
        # process_before_response must be True when running on FaaS
        process_before_response=True,
        token=os.environ.get("SLACK_BOT_TOKEN"),
        signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
    )
    client = app.client
    
    channels = download_conversations_list(client=client, page_limit=100)
    save_as_json(channels, 'conversations_list.json')
    
    users = download_users_list(client=client, page_limit=100)
    save_as_json(users, 'users_list.json')
    
    #conversations = download_conversations_history(
    #    client=client, page_limit=100, latest_unix_time=None, oldest_unix_time=None)
    #save_as_json(conversations, 'conversations_history.json')

    return 'Successfully ingested slack data.'
# ==  END - Main Cloud Function  ==


# ==  BEGIN - Sub Cloud Function  ==
def save_as_json(data: List[dict], fname: str=None):
    """save response data as json
    """
    with open(fname, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        logging.info('save {}'.format(fname))
# ==  END - Sub Cloud Function  ==


# run app
if __name__ == "__main__":
    return_str = ingest_slack_data()
    logging.info(return_str)
