import logging

logging.basicConfig(level=logging.DEBUG)

from slack_bolt import App

# process_before_response must be True when running on FaaS
app = App(process_before_response=True)
