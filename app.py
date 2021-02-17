import os
import pandas as pd
from slack_bolt import App
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slacktastic.template import PieChart, Message
from slacktastic.client import SlackClient
from channel_history import on_home_opened
from flag_toxic_message import flag_toxic_message
from googleapiclient import discovery

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

#Add event listeners here
@app.event("app_home_opened")
def history(say):
    on_home_opened(say)

@app.event("message")
def flag(event, say):
    flag_toxic_message(event, say)

if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
